from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DisciplineForm, TeacherDisciplineForm
from .models import Discipline
from .permissions import (
    get_teacher_discipline,
    is_teacher_of_discipline,
    is_student_of_discipline,
)


@login_required
def discipline_list(request):
    user = request.user

    if user.role == "ADMIN":
        disciplines = Discipline.objects.all()

    elif user.role == "TEACHER":
        disciplines = user.teaching_disciplines.all()

    elif user.role == "STUDENT":
        disciplines = user.enrolled_disciplines.all()

    else:
        disciplines = Discipline.objects.none()

    return render(
        request,
        "courses/discipline_list.html",
        {
            "disciplines": disciplines,
        },
    )


@login_required
def discipline_detail(request, pk):
    discipline = get_object_or_404(
        Discipline.objects.prefetch_related(
            "teachers",
            "students",
            "assignments",
        ),
        pk=pk,
    )

    if request.user.role == "ADMIN":
        pass

    elif request.user.role == "TEACHER":
        if not is_teacher_of_discipline(
            request.user,
            discipline,
        ):
            return render(
                request,
                "403.html",
                status=403,
            )

    elif request.user.role == "STUDENT":
        if not is_student_of_discipline(
            request.user,
            discipline,
        ):
            return render(
                request,
                "403.html",
                status=403,
            )

    else:
        return render(
            request,
            "403.html",
            status=403,
        )

    return render(
        request,
        "courses/discipline_detail.html",
        {
            "discipline": discipline,
            "can_edit": (
                request.user.is_superuser
                or request.user.role == "ADMIN"
                or (
                    request.user.role == "TEACHER"
                    and discipline.teachers.filter(
                        pk=request.user.pk
                    ).exists())),
        },
    )


@login_required
def discipline_create(request):
    if request.user.role != "ADMIN":
        return render(
            request,
            "403.html",
            status=403,
        )

    if request.method == "POST":
        form = DisciplineForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("discipline_list")

    else:
        form = DisciplineForm()

    return render(
        request,
        "courses/discipline_form.html",
        {
            "form": form,
            "title": "Нова дисциплина",
        },
    )


@login_required
def discipline_update(request, pk):
    discipline = get_object_or_404(
        Discipline,
        pk=pk,
    )

    if request.user.role == "ADMIN":
        form_class = DisciplineForm

    elif request.user.role == "TEACHER":
        if not is_teacher_of_discipline(
            request.user,
            discipline,
        ):
            return render(
                request,
                "403.html",
                status=403,
            )

        form_class = TeacherDisciplineForm

    else:
        return render(
            request,
            "403.html",
            status=403,
        )

    if request.method == "POST":
        form = form_class(
            request.POST,
            instance=discipline,
        )

        if form.is_valid():
            form.save()
            return redirect(
                "discipline_detail",
                pk=discipline.pk,
            )

    else:
        form = form_class(
            instance=discipline,
        )

    return render(
        request,
        "courses/discipline_form.html",
        {
            "form": form,
            "discipline": discipline,
            "title": "Редактиране на дисциплина",
        },
    )


@login_required
def discipline_delete(request, pk):
    discipline = get_object_or_404(
        Discipline,
        pk=pk,
    )

    if request.user.role != "ADMIN":
        return render(
            request,
            "403.html",
            status=403,
        )

    if request.method == "POST":
        discipline.delete()
        return redirect("discipline_list")

    return render(
        request,
        "courses/discipline_confirm_delete.html",
        {
            "discipline": discipline,
        },
    )