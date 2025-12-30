from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.admin_users import router as admin_users_router
from app.api.v1.endpoints.projects import router as projects_router
from app.api.v1.endpoints.avito_accounts import router as avito_router
from app.api.v1.endpoints import avito_webhooks

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(admin_users_router)
api_router.include_router(projects_router)
api_router.include_router(avito_router)
api_router.include_router(avito_webhooks.router)