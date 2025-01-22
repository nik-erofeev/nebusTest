import logging

from fastapi import APIRouter, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.organization.shemas import GenerateDataResponse
from app.api.organization.utils import DataGenerator

from app.dao.session_maker import TransactionSessionDep

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/organizations",
    tags=["Организации"],
)


@router.post(
    "/initialize-data/",
    status_code=status.HTTP_201_CREATED,
    summary="Инициализация тестовых данных",
    response_class=ORJSONResponse,
)
async def initialize_data(session: AsyncSession = TransactionSessionDep):
    data_generator = DataGenerator(session)
    result = await data_generator.create_initial_data()
    return GenerateDataResponse(nesting_of_organizations=result)
