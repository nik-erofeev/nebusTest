from fastapi import APIRouter, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.activity.dao import ActivityDao
from app.api.activity.schemas import OrgActivResponse
from app.dao.session_maker import TransactionSessionDep


router = APIRouter(
    prefix="/activities",
    tags=["Деятельности"],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[OrgActivResponse],
    response_class=ORJSONResponse,
    summary="Получить организации по виду деятельности",
)
async def get_organizations_by_activity(
    activity_name: str = Query(..., example="Еда"),
    db: AsyncSession = TransactionSessionDep,
):
    return await ActivityDao.get_orgs_by_activity_name(db, activity_name)
