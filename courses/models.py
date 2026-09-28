from django.conf import settings
from django.db import models


class Discipline(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teaching_disciplines",
        limit_choices_to={"role": "TEACHER"},
        blank=True,
    )

    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_disciplines",
        limit_choices_to={"role": "STUDENT"},
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name