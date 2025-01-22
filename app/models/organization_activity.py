import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.dao.database import Base


if typing.TYPE_CHECKING:
    pass


class OrganizationActivity(Base):
    __tablename__ = "organization_activity"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("organization_id", "activity_id", name="uq_organization_activity"),)
