class CompanyScopedQuerysetMixin:
    """
    Querysetni avtomatik company bo‘yicha filter qiladi
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.role == "admin":
            return qs

        if user.company:
            return qs.filter(company=user.company)

        return qs.none()
