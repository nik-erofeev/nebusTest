from fastapi import APIRouter, status, Query, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.organization.dao import OrganizationDao
from app.api.organization.schemas import OrganizationResponse
from app.dependencies.dao_dep import get_session_without_commit

router = APIRouter(
    prefix="/organizations",
    tags=["Организации"],
)


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    summary="Получить организацию по названию",
)
async def search_organization(
    name: str = Query(..., example="ЗАО “Электроника”"),
    db: AsyncSession = Depends(get_session_without_commit),
):
    return await OrganizationDao.get_org_by_name(db, name)


@router.get(
    "/{organization_id}",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=OrganizationResponse,
    summary="Получить организацию по id",
)
async def get_organization_by_id(organization_id: int, db: AsyncSession = Depends(get_session_without_commit)):
    return await OrganizationDao.get_orgs_by_id(db, organization_id)
