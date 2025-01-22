import logging
import math

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.api.organization.schemas import ActivityBase
from app.api.building.schemas import OrgBuildResponse
from app.dao.base import BaseDAO
from app.models import Building, Organization


logger = logging.getLogger(__name__)


class BuildingDao(BaseDAO):
    model = Building

    @classmethod
    async def get_organizations_by_id(cls, session: AsyncSession, building_id: int) -> list[OrgBuildResponse]:
        query = (
            select(cls.model)
            .options(
                selectinload(cls.model.organizations),
                selectinload(
                    cls.model.organizations,
                    Organization.activities,
                ),  # если ну указано # lazy='selectin' в Organization
            )
            .where(cls.model.id == building_id)
        )

        result = await session.execute(query)
        building = result.scalar_one_or_none()

        if not building:
            logger.warning("Организации не найдены.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Организации не найдены.")

        results = [
            OrgBuildResponse(
                id=organizations.id,
                created_at=organizations.created_at,
                name=organizations.name,
                phone_numbers=organizations.phone_numbers,
                address=building.address,
                activities=organizations.activities,
            )
            for organizations in building.organizations
        ]

        logger.info(f"Найдено организаций: {len(results)}, в здании building_id: {building_id}")

        return results

    # по хорошему переписать
    # @classmethod
    # async def get_orgs_within_radius(
    #     cls, session: AsyncSession, latitude: float, longitude: float, radius: float
    # ) -> list[OrgBuildResponse]:
    #     radius_in_degrees = radius / 111000  # 1 градус ~ 111 км
    #
    #     lat_min = latitude - radius_in_degrees
    #     lat_max = latitude + radius_in_degrees
    #     lon_min = longitude - radius_in_degrees / math.cos(math.radians(latitude))
    #     lon_max = longitude + radius_in_degrees / math.cos(math.radians(latitude))
    #
    #     building_query = select(cls.model).where(
    #         cls.model.latitude.between(lat_min, lat_max), cls.model.longitude.between(lon_min, lon_max)
    #     )
    #
    #     building_result = await session.execute(building_query)
    #     buildings = building_result.scalars().all()
    #
    #     if not buildings:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Здания не найдены в заданном радиусе.")
    #
    #     building_ids = [building.id for building in buildings]
    #
    #     org_query = (
    #         select(Organization)
    #         .where(Organization.building_id.in_(building_ids))
    #         .options(
    #             selectinload(Organization.building),
    #             selectinload(Organization.activities),
    #         )
    #     )
    #
    #     org_result = await session.execute(org_query)
    #     organizations = org_result.scalars().all()
    #
    #     if not organizations:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Организации не найдены в заданном радиусе."
    #         )
    #
    #     results = [
    #         OrgBuildResponse(
    #             id=org.id,
    #             created_at=org.created_at,
    #             name=org.name,
    #             phone_numbers=org.phone_numbers,
    #             address=org.building.address,
    #             activities=org.activities,
    #         )
    #         for org in organizations
    #     ]
    #
    #     return results
    @classmethod
    async def get_orgs_within_radius(
        cls,
        session: AsyncSession,
        latitude: float,
        longitude: float,
        radius: float,
    ) -> list[OrgBuildResponse]:
        radius_in_degrees = radius / 111000  # 1 градус ~ 111 км

        lat_min = latitude - radius_in_degrees
        lat_max = latitude + radius_in_degrees
        lon_min = longitude - radius_in_degrees / math.cos(math.radians(latitude))
        lon_max = longitude + radius_in_degrees / math.cos(math.radians(latitude))

        org_query = (
            select(Organization)
            .join(Organization.building)
            .outerjoin(Organization.activities)
            .where(Building.latitude.between(lat_min, lat_max), Building.longitude.between(lon_min, lon_max))
            .options(
                selectinload(Organization.building),
                selectinload(Organization.activities),
            )
        )

        org_result = await session.execute(org_query)
        organizations = org_result.scalars().all()

        if not organizations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организации не найдены в заданном радиусе.",
            )

        results = [
            OrgBuildResponse(
                id=org.id,
                created_at=org.created_at,
                name=org.name,
                phone_numbers=org.phone_numbers,
                address=org.building.address,
                activities=[ActivityBase(name=activity.name) for activity in org.activities],
            )
            for org in organizations
        ]

        return results
