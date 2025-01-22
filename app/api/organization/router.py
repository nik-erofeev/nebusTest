from fastapi import APIRouter, status, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.organization.dao import OrganizationDao
from app.api.organization.schemas import OrganizationResponse

from app.dao.session_maker import TransactionSessionDep


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
    db: AsyncSession = TransactionSessionDep,
):
    return await OrganizationDao.get_org_by_name(db, name)


@router.get(
    "/{organization_id}",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=OrganizationResponse,
    summary="Получить организацию по id",
)
async def get_organization_by_id(organization_id: int, db: AsyncSession = TransactionSessionDep):
    return await OrganizationDao.get_orgs_by_id(db, organization_id)
