import typing

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base

if typing.TYPE_CHECKING:
    from app.models import Building, OrganizationActivity


class Organization(Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(nullable=False)
    phone_numbers: Mapped[list] = mapped_column(JSON)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))

    building: Mapped["Building"] = relationship("Building", back_populates="organizations")
    activities: Mapped[list["OrganizationActivity"]] = relationship(
        "OrganizationActivity",
        back_populates="organization",
    )
