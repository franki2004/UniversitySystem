from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "faculty_number",
        "role",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "faculty_number",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Допълнителна информация",
            {
                "fields": (
                    "role",
                    "faculty_number",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Допълнителна информация",
            {
                "fields": (
                    "role",
                    "faculty_number",
                ),
            },
        ),
    )