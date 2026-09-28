from django.contrib import admin

from .models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "discipline",
        "created_by",
        "deadline",
    )

    list_filter = (
        "discipline",
    )

    search_fields = (
        "title",
        "description",
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "assignment",
        "student",
        "submitted_at",
        "grade",
    )

    list_filter = (
        "assignment",
        "grade",
    )

    search_fields = (
        "student__username",
        "assignment__title",
    )