import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base

if typing.TYPE_CHECKING:
    from app.models import Organization


class Building(Base):
    __tablename__ = "buildings"

    address: Mapped[str] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)

    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        back_populates="building",
        # lazy='joined',  # если  не указаны lazy="joined" и lazy="selectin", то подгружаем
    )
