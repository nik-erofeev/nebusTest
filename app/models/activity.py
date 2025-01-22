import typing
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base

if typing.TYPE_CHECKING:
    from app.models import Organization


class Activity(Base):
    __tablename__ = "activities"

    # переопределим, так как ссылаемся в parent/remote_side
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("activities.id"), nullable=True)

    parent: Mapped[Optional["Activity"]] = relationship("Activity", remote_side=[id], back_populates="children")
    children: Mapped[list["Activity"]] = relationship("Activity", back_populates="parent")

    organizations: Mapped[list["Organization"]] = relationship(
        secondary="organization_activity",  # Указываем промежуточную таблицу
        back_populates="activities",
        # lazy='joined',  # если  не указаны lazy="joined" и lazy="selectin", то подгружаем
    )
