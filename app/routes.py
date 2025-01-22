"""Корневой роутер приложения"""

from fastapi import APIRouter

from app.api.organization.router import router as organization_router
from app.api.default.router import router as default_router
from app.core.settings import APP_CONFIG

router = APIRouter(
    prefix=f"{APP_CONFIG.api.v1}",
)


routers = (default_router, organization_router)
for resource_router in routers:
    router.include_router(resource_router)
