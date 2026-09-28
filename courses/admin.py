from django.contrib import admin

from .models import Discipline


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("teachers", "students")