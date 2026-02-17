class CompanyQuerysetMixin:
    """
    Admin  → barcha company ma'lumotlari
    Manager/User → faqat o‘z company ma'lumotlari
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Admin hammasini ko‘radi
        if user.role == "admin":
            return queryset

        # Company yo‘q bo‘lsa — bo‘sh
        if not user.company:
            return queryset.none()

        # Faqat o‘z company
        return queryset.filter(company=user.company)
