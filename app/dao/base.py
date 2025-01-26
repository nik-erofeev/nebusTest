import logging
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import Base

# Объявляем типовой параметр T с ограничением, что это наследник Base
T = TypeVar("T", bound=Base)


logger = logging.getLogger(__name__)


class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    async def find_one_or_none_by_id(
        cls,
        data_id: int,
        session: AsyncSession,
    ) -> T | None:
        # Найти запись по ID
        logger.info(f"Поиск {cls.model.__name__} с ID: {data_id}")
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {cls.model.__name__} с ID {data_id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    @classmethod
    async def find_one_or_none(
        cls,
        session: AsyncSession,
        filters: BaseModel,
    ) -> T | None:
        # Найти одну запись по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter_dict}",
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        filters: BaseModel | None = None,
    ) -> list[T]:
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f"Поиск всех записей {cls.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}",
            )
            raise

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel) -> T:
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Добавление записи {cls.model.__name__} с параметрами: {values_dict}",
        )
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        try:
            await session.flush()
            await session.refresh(new_instance)
            logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
            # todo при успешном коммитится так как TransactionSessionDep
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise e
        return new_instance

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: list[BaseModel]):
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.info(f"Добавление нескольких записей {cls.model.__name__}. Количество: {len(values_list)}")
        try:
            new_instances = [cls.model(**values) for values in values_list]
            session.add_all(new_instances)
            logger.info(f"Успешно добавлено {len(new_instances)} записей.")
            await session.flush()
            return new_instances
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении нескольких записей: {e}")
            raise

    @classmethod
    async def update(cls, session: AsyncSession, filters: BaseModel, values: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Обновление записей {cls.model.__name__} по фильтру: {filter_dict} с параметрами: {values_dict}")
        try:
            query = (
                sqlalchemy_update(cls.model)
                .where(*[getattr(cls.model, k) == v for k, v in filter_dict.items()])
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(query)
            logger.info(f"Обновлено {result.rowcount} записей.")
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise

    @classmethod
    async def delete(cls, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Удаление записей {cls.model.__name__} по фильтру: {filter_dict}")
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")
        try:
            query = sqlalchemy_delete(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            logger.info(f"Удалено {result.rowcount} записей.")
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записей: {e}")
            raise

    @classmethod
    async def count(cls, session: AsyncSession, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f"Подсчет количества записей {cls.model.__name__} по фильтру: {filter_dict}")
        try:
            query = select(func.count(cls.model.id)).filter_by(**filter_dict)
            result = await session.execute(query)
            count = result.scalar()
            logger.info(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей: {e}")
            raise

    @classmethod
    async def bulk_update(cls, session: AsyncSession, records: list[BaseModel]):
        logger.info(f"Массовое обновление записей {cls.model.__name__}")
        try:
            updated_count = 0
            for record in records:
                record_dict = record.model_dump(exclude_unset=True)
                if "id" not in record_dict:
                    continue

                update_data = {k: v for k, v in record_dict.items() if k != "id"}
                stmt = sqlalchemy_update(cls.model).filter_by(id=record_dict["id"]).values(**update_data)
                result = await session.execute(stmt)
                updated_count += result.rowcount

            logger.info(f"Обновлено {updated_count} записей")
            await session.flush()
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при массовом обновлении: {e}")
            raise

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        filters: BaseModel | None = None,
    ) -> list[T]:
        # Пагинация записей
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(
            f"Пагинация записей {cls.model.__name__} по фильтру: {filter_dict}, страница: {page}, размер страницы: {page_size}",
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(
                query.offset((page - 1) * page_size).limit(page_size),
            )
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей на странице {page}.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при пагинации записей: {e}")
            raise
