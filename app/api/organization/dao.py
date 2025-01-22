from app.dao.base import BaseDAO
from app.models import Organization, Building, Activity, OrganizationActivity


class BuildingDao(BaseDAO):
    model = Building


class OrganizationDao(BaseDAO):
    model = Organization


class ActivityDao(BaseDAO):
    model = Activity


class OrganizationActivityDao(BaseDAO):
    model = OrganizationActivity
