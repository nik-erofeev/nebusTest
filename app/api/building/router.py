from fastapi import APIRouter, Query, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.building.dao import BuildingDao
from app.api.building.schemas import OrgBuildResponse
from app.dependencies.dao_dep import get_session_without_commit

router = APIRouter(
    prefix="/buildings",
    tags=["Здания"],
)


@router.get(
    "/{building_id}",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=list[OrgBuildResponse],
    summary="Получить список организаций в здании",
)
async def get_organizations(building_id: int, session: AsyncSession = Depends(get_session_without_commit)):
    return await BuildingDao.get_organizations_by_id(session, building_id)


@router.get(
    "/organizations/within-radius",
    response_model=list[OrgBuildResponse],
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
    summary="список организаций, которые находятся в заданном радиусе/прямоугольной",
)
async def get_organizations_within_radius(
    latitude: float = Query(..., example="55.972044"),
    longitude: float = Query(..., example="37.297443"),
    radius: float = Query(..., example="9"),
    session: AsyncSession = Depends(get_session_without_commit),
):
    return await BuildingDao.get_orgs_within_radius(session, latitude, longitude, radius)
