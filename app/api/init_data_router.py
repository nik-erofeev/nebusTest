from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.organization.utils import DataGenerator
from app.dao.session_maker import TransactionSessionDep


router = APIRouter(
    prefix="/initialize-data",
    tags=["Тестовые данные"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Инициализация тестовых данных",
    response_class=ORJSONResponse,
)
async def initialize_data(session: AsyncSession = TransactionSessionDep):
    data_generator = DataGenerator(session)
    for _ in range(5):
        await data_generator.create_initial_data()
    return {"тестовые данные вставлены": "successful"}
