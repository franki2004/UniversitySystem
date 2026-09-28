from django.conf import settings
from django.db import models

from courses.models import Discipline


class Assignment(models.Model):
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    attachment = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    deadline = models.DateTimeField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assignments",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    file = models.FileField(
        upload_to="submissions/",
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
    )

    grade = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
    )

    feedback = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_student_submission",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.assignment}"