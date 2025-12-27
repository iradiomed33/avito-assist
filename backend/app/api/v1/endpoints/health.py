from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.get("/ready")
def ready():
    return {"ready": True}

@router.get("/version")
def version():
    return {"version": "0.0.1"}
