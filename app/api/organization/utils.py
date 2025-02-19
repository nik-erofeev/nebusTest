import random

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.activity.dao import ActivityDao
from app.api.building.dao import BuildingDao
from app.api.organization.dao import OrganizationDao, OrganizationActivityDao
from app.api.organization.schemas import BuildingCreate, ActivityCreate, OrganizationCreate, OrganizationActivityCreate
from app.models import Activity


CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Сочи",
    "Казань",
    "Новосибирск",
    "Екатеринбург",
    "Нижний Новгород",
    "Ростов-на-Дону",
]
STREETS = [
    "Ленина",
    "Пушкина",
    "Гагарина",
    "Мира",
    "Садовая",
    "Кирова",
    "Советская",
    "Тимирязева",
    "Набережная",
    "Центральная",
]
ORGANIZATION_NAMES = [
    "ООО “Рога и Копыта”",
    "ЗАО “Светлый путь”",
    "ИП “Надежда”",
    "ООО “ТехноСервис”",
    "ЗАО “ЭкоПродукт”",
    "ООО “СтройМир”",
    "ИП “Кулинария”",
    "ООО “АвтоМир”",
    "ЗАО “Электроника”",
    "ООО “Финансовые решения”",
]
ACTIVITY_HIERARCHY = {
    "Еда": {
        "Мясная продукция": ["Говядина", "Свинина"],
        "Молочная продукция": ["Молоко", "Йогурты"],
        "Овощи и фрукты": ["Свежие овощи", "Свежие фрукты"],
    },
    "Автомобили": {
        "Грузовые": ["Фургоны", "Самосвалы"],
        "Легковые": ["Седаны", "Хэтчбеки"],
    },
    "Электроника": {
        "Мобильные устройства": ["Смартфоны", "Планшеты"],
        "Компьютеры": ["Ноутбуки", "Настольные ПК"],
        "Аудио и видео": ["Телевизоры", "Колонки"],
    },
}


class DataGenerator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.buildings: list[BuildingCreate] = []
        self.activities: list[ActivityCreate] = []
        self.activity_map: dict = {}

    @staticmethod
    def generate_phone_number() -> str:
        """Генерирует номера в формате +X-XXX-XXXX или X-XXX-XXXX."""
        if random.choice([True, False]):
            return f"+{random.randint(1, 9)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        else:
            return f"{random.randint(1, 9)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

    async def create_buildings(self) -> None:
        for _ in range(random.randint(3, 5)):
            city = random.choice(CITIES)
            street = random.choice(STREETS)
            house_number = random.randint(1, 50)
            building = BuildingCreate(
                address=f"{city}, ул. {street} {house_number}",
                latitude=round(random.uniform(55.0, 56.0), 6),
                longitude=round(random.uniform(37.0, 38.0), 6),
            )
            building_response = await BuildingDao.add(self.session, building)
            self.buildings.append(building_response)

    async def create_activities(self) -> None:
        for root_name, children in ACTIVITY_HIERARCHY.items():
            root_activity = ActivityCreate(name=root_name)
            root_activity_response = await ActivityDao.add_activity(self.session, root_activity)
            self.activities.append(root_activity_response)
            self.activity_map[root_activity_response.id] = None

            for child_name, grandchildren in children.items():
                child_activity = ActivityCreate(name=child_name, parent_id=root_activity_response.id)
                child_activity_response = await ActivityDao.add_activity(self.session, child_activity)
                self.activities.append(child_activity_response)
                self.activity_map[child_activity_response.id] = root_activity_response.id

                for grandchild_name in grandchildren:
                    great_grandchild_activity = ActivityCreate(
                        name=grandchild_name,
                        parent_id=child_activity_response.id,
                    )
                    await ActivityDao.add_activity(self.session, great_grandchild_activity)

    async def create_organizations(self) -> None:
        for _ in range(random.randint(5, 10)):
            organization = OrganizationCreate(
                name=random.choice(ORGANIZATION_NAMES),
                phone_numbers=[self.generate_phone_number() for _ in range(random.randint(1, 3))],
                building_id=random.choice(self.buildings).id,
            )
            organization_response = await OrganizationDao.add(self.session, organization)

            selected_activities = random.sample(self.activities, k=random.randint(1, 3))
            for activity in selected_activities:
                if isinstance(activity, Activity) and activity.id:
                    organization_activity = OrganizationActivityCreate(
                        organization_id=organization_response.id,
                        activity_id=activity.id,
                    )
                    await OrganizationActivityDao.add(self.session, organization_activity)

    async def create_initial_data(self) -> None:
        try:
            await self.create_buildings()
            await self.create_activities()
            await self.create_organizations()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при наполнении {e=!r}.",
            )
