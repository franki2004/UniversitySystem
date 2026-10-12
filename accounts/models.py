from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    faculty_number = models.CharField(
    max_length=30,
    unique=True,
    null=True,
    blank=True,
    verbose_name="Факултетен номер",
)

    def __str__(self):
        return self.username