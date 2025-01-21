import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base


if typing.TYPE_CHECKING:
    from app.models import Organization, Activity


class OrganizationActivity(Base):
    __tablename__ = "organization_activity"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="activities")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="organizations")

    __table_args__ = (UniqueConstraint("organization_id", "activity_id", name="uq_organization_activity"),)
