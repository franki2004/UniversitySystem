from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Discipline
from courses.permissions import (
    is_student_of_discipline,
    is_teacher_of_discipline,
)

from .forms import (
    AssignmentForm,
    GradeForm,
    SubmissionForm,
)
from .models import Assignment, Submission


def is_admin(user):
    return user.is_superuser or user.role == "ADMIN"


@login_required
def assignment_create(request, discipline_pk):
    discipline = get_object_or_404(
        Discipline,
        pk=discipline_pk,
    )

    if not is_admin(request.user):
        if request.user.role != "TEACHER":
            return render(
                request,
                "403.html",
                status=403,
            )

        if not is_teacher_of_discipline(
            request.user,
            discipline,
        ):
            return render(
                request,
                "403.html",
                status=403,
            )

    if request.method == "POST":
        form = AssignmentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.discipline = discipline
            assignment.created_by = request.user
            assignment.save()

            return redirect(
                "assignment_detail",
                pk=assignment.pk,
            )

    else:
        form = AssignmentForm()

    return render(
        request,
        "assignments/assignment_form.html",
        {
            "form": form,
            "discipline": discipline,
            "title": "Ново задание",
        },
    )


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(
        Assignment.objects.select_related(
            "discipline",
            "created_by",
        ),
        pk=pk,
    )

    discipline = assignment.discipline

    if is_admin(request.user):
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

    submission = None

    if request.user.role == "STUDENT":
        submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user,
        ).first()

    return render(
        request,
        "assignments/assignment_detail.html",
        {
            "assignment": assignment,
            "submission": submission,
        },
    )


@login_required
def assignment_update(request, pk):
    assignment = get_object_or_404(
        Assignment,
        pk=pk,
    )

    if is_admin(request.user):
        pass

    elif request.user.role == "TEACHER":
        if not is_teacher_of_discipline(
            request.user,
            assignment.discipline,
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

    if request.method == "POST":
        form = AssignmentForm(
            request.POST,
            request.FILES,
            instance=assignment,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "assignment_detail",
                pk=assignment.pk,
            )

    else:
        form = AssignmentForm(
            instance=assignment,
        )

    return render(
        request,
        "assignments/assignment_form.html",
        {
            "form": form,
            "assignment": assignment,
            "discipline": assignment.discipline,
            "title": "Редактиране на задание",
        },
    )


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(
        Assignment,
        pk=pk,
    )

    if is_admin(request.user):
        pass

    elif request.user.role == "TEACHER":
        if not is_teacher_of_discipline(
            request.user,
            assignment.discipline,
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

    if request.method == "POST":
        assignment.delete()

        return redirect(
            "discipline_detail",
            pk=assignment.discipline.pk,
        )

    return render(
        request,
        "assignments/assignment_confirm_delete.html",
        {
            "assignment": assignment,
        },
    )

@login_required
def submit_assignment(request, assignment_pk):
    assignment = get_object_or_404(
        Assignment,
        pk=assignment_pk,
    )

    if request.user.role != "STUDENT":
        return render(
            request,
            "403.html",
            status=403,
        )

    if not is_student_of_discipline(
        request.user,
        assignment.discipline,
    ):
        return render(
            request,
            "403.html",
            status=403,
        )

    submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user,
    ).first()

    if request.method == "POST":
        form = SubmissionForm(
            request.POST,
            request.FILES,
            instance=submission,
        )

        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()

            return redirect(
                "assignment_detail",
                pk=assignment.pk,
            )

    else:
        form = SubmissionForm(
            instance=submission,
        )

    return render(
        request,
        "assignments/submission_form.html",
        {
            "form": form,
            "assignment": assignment,
            "submission": submission,
        },
    )

@login_required
def submission_list(request, assignment_pk):
    assignment = get_object_or_404(
        Assignment,
        pk=assignment_pk,
    )

    if is_admin(request.user):
        pass

    elif request.user.role == "TEACHER":
        if not is_teacher_of_discipline(
            request.user,
            assignment.discipline,
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

    submissions = assignment.submissions.select_related(
        "student"
    ).all()

    return render(
        request,
        "assignments/submission_list.html",
        {
            "assignment": assignment,
            "submissions": submissions,
        },
    )

@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(
        Submission.objects.select_related(
            "assignment",
            "student",
        ),
        pk=pk,
    )

    assignment = submission.assignment

    if is_admin(request.user):
        pass

    elif request.user.role == "TEACHER":
        if not is_teacher_of_discipline(
            request.user,
            assignment.discipline,
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

    if request.method == "POST":
        form = GradeForm(
            request.POST,
            instance=submission,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "submission_list",
                assignment_pk=assignment.pk,
            )

    else:
        form = GradeForm(
            instance=submission,
        )

    return render(
        request,
        "assignments/grade_form.html",
        {
            "form": form,
            "submission": submission,
        },
    )