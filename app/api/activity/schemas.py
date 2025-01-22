from pydantic import Field
from app.api.organization.schemas import OrganizationBase, ResponseSchema


class OrgActivResponse(OrganizationBase, ResponseSchema):
    address: str = Field(description="Название здания", examples=["Блюхера, 32/1"])
    activities: str = Field(
        description="Название деятельности",
        examples=["Молочная продукция", "Мясная продукция"],
    )
