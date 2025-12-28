from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])

def _check_owner(project: Project, current: User):
    if project.owner_user_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    rows = db.query(Project).filter(Project.owner_user_id == current.id).order_by(Project.id.desc()).all()
    return [ProjectOut(
        id=p.id, name=p.name, niche=p.niche, description=p.description, status=p.status, created_at=p.created_at
    ) for p in rows]

@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    p = Project(
        owner_user_id=current.id,
        name=payload.name,
        niche=payload.niche,
        description=payload.description,
        status="active",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return ProjectOut(id=p.id, name=p.name, niche=p.niche, description=p.description, status=p.status, created_at=p.created_at)

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    _check_owner(p, current)
    return ProjectOut(id=p.id, name=p.name, niche=p.niche, description=p.description, status=p.status, created_at=p.created_at)

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    _check_owner(p, current)

    if payload.name is not None:
        p.name = payload.name
    if payload.niche is not None:
        p.niche = payload.niche
    if payload.description is not None:
        p.description = payload.description
    if payload.status is not None:
        p.status = payload.status

    db.commit()
    db.refresh(p)
    return ProjectOut(id=p.id, name=p.name, niche=p.niche, description=p.description, status=p.status, created_at=p.created_at)

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    _check_owner(p, current)

    db.delete(p)
    db.commit()
    return {"deleted": True}
