from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate

router = APIRouter(prefix="/admin/users", tags=["admin"])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    users = db.query(User).order_by(User.id.desc()).all()
    return [UserOut(
        id=u.id, username=u.username, role=u.role, is_active=u.is_active, expires_at=u.expires_at
    ) for u in users]

@router.post("", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=409, detail="Username already exists")

    u = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
        expires_at=payload.expires_at,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return UserOut(id=u.id, username=u.username, role=u.role, is_active=u.is_active, expires_at=u.expires_at)

@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.password is not None:
        u.password_hash = hash_password(payload.password)
    if payload.role is not None:
        u.role = payload.role
    if payload.is_active is not None:
        u.is_active = payload.is_active
    if payload.expires_at is not None or payload.expires_at is None:
        u.expires_at = payload.expires_at

    db.commit()
    db.refresh(u)
    return UserOut(id=u.id, username=u.username, role=u.role, is_active=u.is_active, expires_at=u.expires_at)
