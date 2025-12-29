from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.avito_account import AvitoAccount
from app.schemas.avito_account import AvitoAccountOut, AvitoOAuthStartOut
from app.services.avito_oauth import create_oauth_state, build_authorize_url

# предполагаю, что у тебя уже есть эти зависимости (как в Sprint 0):
from app.core.security import get_current_user  # поправишь импорт под свой проект
from app.models.user import User  # поправишь импорт под свой проект

router = APIRouter(prefix="/avito", tags=["avito"])


def assert_project_access(db: Session, user: User, project_id: int) -> None:
    # Минимально: если у тебя уже есть project_members — проверь членство.
    # Подстрой под свою схему (мы это делали в Sprint 0).
    from app.models.project_member import ProjectMember  # если у тебя так называется

    m = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id)
        .first()
    )
    if not m:
        raise HTTPException(status_code=403, detail="No access to project")


@router.get("/oauth/start", response_model=AvitoOAuthStartOut)
def avito_oauth_start(
    project_id: int = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    assert_project_access(db, user, project_id)

    if not settings.AVITO_CLIENT_ID or not settings.AVITO_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Avito OAuth is not configured")

    state = create_oauth_state(settings, user_id=user.id, project_id=project_id)
    url = build_authorize_url(settings, state)

    return AvitoOAuthStartOut(auth_url=url)


@router.get("/accounts", response_model=list[AvitoAccountOut])
def list_avito_accounts(
    project_id: int = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    assert_project_access(db, user, project_id)

    rows = (
        db.query(AvitoAccount)
        .filter(AvitoAccount.project_id == project_id)
        .order_by(AvitoAccount.id.desc())
        .all()
    )
    return rows
