import pytest
from datetime import datetime
from pydantic import ValidationError

from app.api.organization.schemas import ResponseSchema, OrganizationCreate


@pytest.mark.parametrize(
    "id, created_at, expected",
    [
        (1, datetime(2023, 10, 1, 12, 30), "2023-10-01 12:30"),
        (2, "2023-10-02 14:45", "2023-10-02 14:45"),
    ],
)
def test_response_schema(id, created_at, expected):
    response = ResponseSchema(id=id, created_at=created_at)
    assert response.created_at == expected


@pytest.mark.parametrize(
    "id, created_at",
    [
        (1, None),  # Неверный формат
        (2, 12345),  # Неверный тип
    ],
)
def test_response_schema_invalid_data(id, created_at):
    with pytest.raises(ValidationError):
        ResponseSchema(id=id, created_at=created_at)


# Тесты для OrganizationCreate
@pytest.mark.parametrize(
    "name, phone_numbers, building_id, expected",
    [
        ("ООО “Рога и Копыта”", ["2-222-222", "3-333-333"], 1, "ООО “Рога и Копыта”"),
        ("Компания", ["8-923-666-13-13"], 2, "Компания"),
    ],
)
def test_organization_create(name, phone_numbers, building_id, expected):
    organization = OrganizationCreate(name=name, phone_numbers=phone_numbers, building_id=building_id)
    assert organization.name == expected


@pytest.mark.parametrize(
    "name, phone_numbers, building_id",
    [
        ("", ["2-222-222"], 1),  # Пустое имя
        ("Компания", ["123-456"], 2),  # Неверный формат телефона
    ],
)
def test_organization_create_invalid_data(name, phone_numbers, building_id):
    with pytest.raises(ValidationError):
        OrganizationCreate(name=name, phone_numbers=phone_numbers, building_id=building_id)
