from pydantic import Field, BaseModel, ConfigDict, field_validator
import re
from datetime import datetime


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ResponseSchema(BaseModelConfig):
    id: int
    created_at: str

    @field_validator("created_at", mode="before")
    def format_created_at(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M")
        return v


class OrganizationBase(BaseModelConfig):
    name: str = Field(
        min_length=1,
        description="имя организации",
        examples=["ООО “Рога и Копыта”"],
        max_length=50,
    )
    phone_numbers: list[str] = Field(
        description="номера телефонов",
        examples=["2-222-222", "3-333-333", "8-923-666-13-13", "+7-923-666-13-13"],
    )

    @field_validator("phone_numbers", mode="before")
    def validate_phone_numbers(cls, v):
        pattern = r"^\+?\d-\d{3}-\d{3,4}(-\d{2,4}){0,2}$"
        for number in v:
            if not re.match(pattern, number):
                raise ValueError(
                    'Номер телефона должен быть в формате "X-XXX-XXXX", "X-XXX-XXXX-XXXX" или "X-XXX-XXXX-XXXX-XXXX", где X - цифра',
                )
        return v


class ActivityBase(BaseModelConfig):
    name: str = Field(
        description="Название деятельности",
        examples=["Молочная продукция", "Мясная продукция"],
        max_length=50,
        min_length=1,
    )


class OrgBuildResponse(OrganizationBase, ResponseSchema):
    address: str = Field(description="Название здания", examples=["Блюхера, 32/1"])
    activities: list[ActivityBase]
