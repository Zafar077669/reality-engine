from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    NOTE:
    role and company fields are legacy.
    New RBAC system uses CompanyMembership.
    """

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("analyst", "Analyst"),
        ("company_user", "Company User"),
    )

    # 🔥 LEGACY (temporary, do not use in new logic)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username