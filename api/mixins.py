from rest_framework.permissions import BasePermission


class CompanyQuerySetMixin:
    """
    Querysetni avtomatik company bo‘yicha filter qiladi.
    Multi-tenant security uchun asosiy mixin.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Anonymous user bo‘lsa – hech narsa ko‘rmaydi
        if not user or not user.is_authenticated:
            return qs.none()

        # Admin hamma narsani ko‘ra oladi
        if getattr(user, "role", None) == "admin":
            return qs

        # Oddiy user faqat o‘z kompaniyasini
        if getattr(user, "company", None):
            return qs.filter(company=user.company)

        return qs.none()


class IsCompanyMember(BasePermission):
    """
    User faqat o‘z company obyektlari bilan ishlay oladi
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if getattr(user, "role", None) == "admin":
            return True

        return getattr(obj, "company", None) == getattr(user, "company", None)