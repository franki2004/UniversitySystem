from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AddStudentsForm,
    DisciplineForm,
    TeacherDisciplineForm,
)
from .models import Discipline


User = get_user_model()


def is_admin_user(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def can_manage_discipline(user, discipline):
    if is_admin_user(user):
        return True

    return (
        user.role == User.Role.TEACHER
        and discipline.teachers.filter(pk=user.pk).exists()
    )


@login_required
def discipline_list(request):
    user = request.user

    if is_admin_user(user):
        disciplines = Discipline.objects.all()

    elif user.role == User.Role.TEACHER:
        disciplines = user.teaching_disciplines.all()

    elif user.role == User.Role.STUDENT:
        disciplines = user.enrolled_disciplines.all()

    else:
        return render(request, "403.html", status=403)

    return render(
        request,
        "courses/discipline_list.html",
        {"disciplines": disciplines},
    )


@login_required
def discipline_detail(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)

    user = request.user

    if not is_admin_user(user):
        if user.role == User.Role.TEACHER:
            if not discipline.teachers.filter(pk=user.pk).exists():
                return render(request, "403.html", status=403)

        elif user.role == User.Role.STUDENT:
            if not discipline.students.filter(pk=user.pk).exists():
                return render(request, "403.html", status=403)

        else:
            return render(request, "403.html", status=403)

    can_manage_students = can_manage_discipline(user, discipline)

    add_students_form = AddStudentsForm(discipline=discipline)

    if request.method == "POST":
        # Само администраторът или преподавателят на тази дисциплина
        # може да добавя и премахва студенти.
        if not can_manage_students:
            return render(request, "403.html", status=403)

        if "add_students" in request.POST:
            add_students_form = AddStudentsForm(
                request.POST,
                discipline=discipline,
            )

            if add_students_form.is_valid():
                selected_students = add_students_form.cleaned_data[
                    "students"
                ]

                discipline.students.add(*selected_students)

                messages.success(
                    request,
                    "Студентите бяха добавени към дисциплината.",
                )

                return redirect(
                    "discipline_detail",
                    pk=discipline.pk,
                )

        elif "remove_student" in request.POST:
            try:
                student_pk = int(request.POST["remove_student"])
            except (KeyError, TypeError, ValueError):
                messages.error(
                    request,
                    "Невалиден студент.",
                )
                return redirect(
                    "discipline_detail",
                    pk=discipline.pk,
                )

            student = get_object_or_404(
                User,
                pk=student_pk,
                role=User.Role.STUDENT,
            )

            if discipline.students.filter(pk=student.pk).exists():
                discipline.students.remove(student)

                messages.success(
                    request,
                    "Студентът беше премахнат от дисциплината.",
                )
            else:
                messages.error(
                    request,
                    "Студентът не е записан в тази дисциплина.",
                )

            return redirect(
                "discipline_detail",
                pk=discipline.pk,
            )

    available_students_count = (
        add_students_form.fields["students"].queryset.count()
    )

    context = {
        "discipline": discipline,
        "can_manage_students": can_manage_students,
        "add_students_form": add_students_form,
        "available_students_count": available_students_count,
    }

    return render(
        request,
        "courses/discipline_detail.html",
        context,
    )


@login_required
def discipline_create(request):
    if not is_admin_user(request.user):
        return render(request, "403.html", status=403)

    form = DisciplineForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        discipline = form.save()

        messages.success(
            request,
            "Дисциплината беше създадена успешно.",
        )

        return redirect(
            "discipline_detail",
            pk=discipline.pk,
        )

    return render(
        request,
        "courses/discipline_form.html",
        {
            "form": form,
            "page_title": "Създаване на дисциплина",
            "submit_label": "Създай дисциплината",
        },
    )


@login_required
def discipline_update(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)

    if is_admin_user(request.user):
        form_class = DisciplineForm

    elif (
        request.user.role == User.Role.TEACHER
        and discipline.teachers.filter(pk=request.user.pk).exists()
    ):
        form_class = TeacherDisciplineForm

    else:
        return render(request, "403.html", status=403)

    form = form_class(
        request.POST or None,
        instance=discipline,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Дисциплината беше редактирана успешно.",
        )

        return redirect(
            "discipline_detail",
            pk=discipline.pk,
        )

    return render(
        request,
        "courses/discipline_form.html",
        {
            "form": form,
            "page_title": "Редактиране на дисциплина",
            "submit_label": "Запази промените",
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