from django.shortcuts import get_object_or_404

from .models import Discipline


def get_teacher_discipline(user, pk):
    discipline = get_object_or_404(
        Discipline,
        pk=pk,
        teachers=user,
    )

    return discipline


def is_teacher_of_discipline(user, discipline):
    return discipline.teachers.filter(
        pk=user.pk
    ).exists()


def is_student_of_discipline(user, discipline):
    return discipline.students.filter(
        pk=user.pk
    ).exists()