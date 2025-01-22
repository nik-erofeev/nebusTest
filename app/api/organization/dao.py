import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.api.organization.schemas import OrganizationResponse
from app.dao.base import BaseDAO
from app.models import Organization, OrganizationActivity
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class OrganizationActivityDao(BaseDAO):
    model = OrganizationActivity


class OrganizationDao(BaseDAO):
    model = Organization

    # deprecated (для ознакомления)
    # @classmethod
    # async def get_orgs_by_build_id(cls, session: AsyncSession, building_id: int) -> list[OrgBuildResponse]:
    #     # если в орм указать lazy="joined" и lazy="selectin", то подгружаем автоматом
    #     # v1 через базовую
    #     # filters = FilterOrganization(building_id=building_id)
    #     # organizations = await cls.find_all(session, filters)
    #
    #     # v2
    #     # query = select(cls.model).where(cls.model.building_id == building_id)
    #     query = (
    #         select(cls.model)
    #         .options(joinedload(cls.model.building), selectinload(cls.model.activities))
    #         .where(cls.model.building_id == building_id)
    #     )
    #
    #     result = await session.execute(query)
    #     organizations = result.scalars().all()
    #
    #     if not organizations:
    #         logger.warning("Организации не найдены.")
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Организации не найдены.")
    #
    #     results = [
    #         OrgBuildResponse(
    #             id=organization.id,
    #             created_at=organization.created_at,
    #             name=organization.name,
    #             phone_numbers=organization.phone_numbers,
    #             address=organization.building.address,
    #             activities=organization.activities,
    #         )
    #         for organization in organizations
    #     ]
    #     logger.info(f"Найдено организаций: {len(results)}, в здании building_id: {building_id}")
    #
    #     return results

    @classmethod
    async def get_orgs_by_id(cls, session: AsyncSession, organization_id: int) -> OrganizationResponse:
        query = (
            select(cls.model)
            .options(joinedload(cls.model.building), selectinload(cls.model.activities))
            .where(cls.model.id == organization_id)
        )

        result = await session.execute(query)
        organization = result.scalar_one_or_none()

        if not organization:
            logger.info(f"Организация {organization_id} не найдена.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Организация {organization_id} не найдена.",
            )

        result = OrganizationResponse(
            id=organization.id,
            created_at=organization.created_at,
            name=organization.name,
            phone_numbers=organization.phone_numbers,
            address=organization.building.address,
            activities=organization.activities,
        )
        logger.info(f"Организация {organization_id} найдена. ")
        return result

    @classmethod
    async def get_org_by_name(cls, session: AsyncSession, organization_name: str):
        query = (
            select(cls.model)
            .options(joinedload(cls.model.building), selectinload(cls.model.activities))
            .where(cls.model.name == organization_name)
        )
        result = await session.execute(query)
        organization = result.scalars().first()  # по хорошему добавить уникальность/ из тестовых достаю 1й

        if not organization:
            logger.info(f"Организация {organization_name} не найдена.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вид деятельности не найден.")

        result = OrganizationResponse(
            id=organization.id,
            created_at=organization.created_at,
            name=organization.name,
            phone_numbers=organization.phone_numbers,
            address=organization.building.address,
            activities=organization.activities,
        )
        logger.info(f"Организация {organization_name} найдена. ")
        return result
