# api/mixins.py

from rest_framework.permissions import BasePermission


class CompanyQuerySetMixin:
    """
    Multi-tenant queryset filter.
    User faqat o‘zi a'zo bo‘lgan kompaniyalar ma'lumotini ko‘radi.
    """

    company_field = "company"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Anonymous user
        if not user or not user.is_authenticated:
            return qs.none()

        # Superuser hamma narsani ko‘radi
        if user.is_superuser:
            return qs

        # User a'zo bo‘lgan kompaniyalar
        company_ids = user.company_memberships.values_list(
            "company_id",
            flat=True
        )

        filter_kwargs = {
            f"{self.company_field}__in": company_ids
        }

        return qs.filter(**filter_kwargs)


class IsCompanyMember(BasePermission):
    """
    Object-level multi-tenant permission
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        company_ids = user.company_memberships.values_list(
            "company_id",
            flat=True
        )

        return getattr(obj, "company_id", None) in company_ids