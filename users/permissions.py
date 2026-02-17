from rest_framework.permissions import BasePermission


# =====================================================
# ROLE-BASED PERMISSIONS (ENDPOINT LEVEL)
# =====================================================

class IsAdmin(BasePermission):
    """
    Faqat admin role
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsManager(BasePermission):
    """
    Faqat manager role
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "manager"
        )


class IsUser(BasePermission):
    """
    Faqat user role
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "user"
        )


class IsAdminOrManager(BasePermission):
    """
    Admin yoki Manager
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("admin", "manager")
        )


# =====================================================
# OBJECT-LEVEL & MULTI-TENANT SECURITY
# =====================================================

class IsSameCompany(BasePermission):
    """
    OBJECT-LEVEL PERMISSION

    Admin  -> barcha company obyektlariga ruxsat
    Manager/User -> faqat o‘z company obyektlari
    """

    def has_permission(self, request, view):
        # Auth bo‘lmasa yo‘q
        if not request.user.is_authenticated:
            return False

        # Admin har doim ruxsatli
        if request.user.role == "admin":
            return True

        # Manager/User uchun company bo‘lishi shart
        return request.user.company is not None

    def has_object_permission(self, request, view, obj):
        # Admin hammasini ko‘ra oladi
        if request.user.role == "admin":
            return True

        # User company bo‘lmasa – yo‘q
        if not request.user.company:
            return False

        # Object company user company bilan mos bo‘lishi shart
        return getattr(obj, "company", None) == request.user.company
