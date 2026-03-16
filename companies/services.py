from django.core.exceptions import PermissionDenied
from companies.models import CompanyMembership


class PermissionService:

    @staticmethod
    def get_membership(user, company):
        membership = CompanyMembership.objects.filter(
            user=user,
            company=company
        ).first()

        if not membership:
            raise PermissionDenied("User not part of this company")

        return membership

    @staticmethod
    def require_admin_or_owner(user, company):
        membership = PermissionService.get_membership(user, company)

        if membership.role not in [
            CompanyMembership.Role.ADMIN,
            CompanyMembership.Role.OWNER,
        ]:
            raise PermissionDenied("Admin or Owner role required")

    @staticmethod
    def require_engineer(user, company):
        membership = PermissionService.get_membership(user, company)

        if membership.role != CompanyMembership.Role.ENGINEER:
            raise PermissionDenied("Engineer role required")