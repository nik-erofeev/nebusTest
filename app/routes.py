"""Корневой роутер приложения"""

from fastapi import APIRouter

from app.api.organization.router import router as organization_router
from app.api.activity.router import router as activity_router
from app.api.building.router import router as building_router
from app.api.init_data_router import router as init_data_router
from app.core.settings import APP_CONFIG

router = APIRouter(
    prefix=f"{APP_CONFIG.api.v1}",
)


routers = (
    init_data_router,
    organization_router,
    activity_router,
    building_router,
)
for resource_router in routers:
    router.include_router(resource_router)
