import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.api.organization.schemas import ActivityCreate
from app.api.activity.schemas import OrgActivResponse
from app.dao.base import BaseDAO
from app.models import Activity, Organization

logger = logging.getLogger(__name__)


class ActivityDao(BaseDAO):
    model = Activity

    @classmethod
    async def get_orgs_by_activity_name(cls, session: AsyncSession, activity_name: str) -> list[OrgActivResponse]:
        # можно new join
        # query = (
        #     select(
        #         Organization.id,
        #         Organization.created_at,
        #         Organization.name,
        #         Organization.phone_numbers,
        #         Building.address,
        #         Activity.name.label("activities"),  #  алиас для
        #     )
        #     .join(OrganizationActivity, OrganizationActivity.organization_id == Organization.id)
        #     .join(Activity, Activity.id == OrganizationActivity.activity_id)
        #     .join(Building, Building.id == Organization.building_id)
        #     .where(Activity.name == activity_name)
        # )
        #
        # result = await session.execute(query)
        # organizations = result.fetchall()
        #
        # if not organizations:
        #     logger.info(f"Организации для вида деятельности {activity_name}не найдены.")
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Организации не найдены.")
        #
        # results = [OrgActivResponse.model_validate(org) for org in organizations]
        # logger.info(f"Найдено организаций: {len(results)} для вида деятельности: {activity_name}")
        #
        # return results

        query = (
            select(Organization)
            .join(Organization.activities)
            .where(cls.model.name == activity_name)
            .options(selectinload(Organization.building))
        )
        result = await session.execute(query)
        organizations = result.scalars().all()

        if not organizations:
            logger.info(f"Организации для вида деятельности {activity_name}не найдены.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вид деятельности не найден.")

        results = [
            OrgActivResponse(
                id=org.id,
                created_at=org.created_at,
                name=org.name,
                phone_numbers=org.phone_numbers,
                address=org.building.address,
                activities=activity_name,
            )
            for org in organizations
        ]
        logger.info(f"Найдено организаций: {len(results)} для вида деятельности: {activity_name}")

        return results

    @classmethod
    async def _check_activity_depth(cls, session: AsyncSession, activity_id: int, current_depth: int = 1) -> None:
        logger.info(f"current_depth: {current_depth}")
        if current_depth > 2:
            logger.warning("Достигнут максимальный уровень вложенности (3 уровня).")
            raise ValueError("Достигнут максимальный уровень вложенности (3 уровня).")

        parent_activity = await session.get(cls.model, activity_id)
        if parent_activity and parent_activity.parent_id:
            await cls._check_activity_depth(session, parent_activity.parent_id, current_depth + 1)

    @classmethod
    async def add_activity(cls, session: AsyncSession, activity_data: ActivityCreate) -> Activity:
        new_activity = Activity(**activity_data.model_dump())

        if new_activity.parent_id:
            await cls._check_activity_depth(session, new_activity.parent_id)

        session.add(new_activity)
        await session.commit()
        return new_activity
