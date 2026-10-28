from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from assignments.models import Assignment, Submission
from courses.models import Discipline
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .forms import UserCreateForm, UserUpdateForm


User = get_user_model()


def home(request):
    return render(
        request,
        "home.html",
    )


@login_required
def dashboard(request):
    if request.user.is_superuser or request.user.role == "ADMIN":
        return admin_dashboard(request)

    if request.user.role == "TEACHER":
        return teacher_dashboard(request)

    return student_dashboard(request)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser and request.user.role != "ADMIN":
        return render(
            request,
            "403.html",
            status=403,
        )

    users_count = User.objects.count()

    teachers_count = User.objects.filter(
        role=User.Role.TEACHER
    ).count()

    students_count = User.objects.filter(
        role=User.Role.STUDENT
    ).count()

    admins_count = User.objects.filter(
            role=User.Role.ADMIN
        ).count()

    disciplines_count = Discipline.objects.count()

    assignments_count = Assignment.objects.count()

    submissions_count = Submission.objects.count()

    ungraded_submissions = Submission.objects.filter(
        grade__isnull=True
    ).count()

    recent_assignments = Assignment.objects.select_related(
        "discipline",
        "created_by",
    ).order_by("-created_at")[:5]

    recent_submissions = Submission.objects.select_related(
        "student",
        "assignment",
        "assignment__discipline",
    ).order_by("-submitted_at")[:5]

    context = {
        "users_count": users_count,
        "teachers_count": teachers_count,
        "students_count": students_count,
        "admins_count" : admins_count,
        "disciplines_count": disciplines_count,
        "assignments_count": assignments_count,
        "submissions_count": submissions_count,
        "ungraded_submissions": ungraded_submissions,
        "recent_assignments": recent_assignments,
        "recent_submissions": recent_submissions,
        
    }

    return render(
        request,
        "accounts/admin_dashboard.html",
        context,
    )
@login_required
def teacher_dashboard(request):
    if request.user.role != "TEACHER":
        return render(
            request,
            "403.html",
            status=403,
        )
    
    disciplines = request.user.teaching_disciplines.prefetch_related(
        "students",
        "assignments",
    )
    disciplines_count = disciplines.count()
    assignments = Assignment.objects.filter(
        discipline__teachers=request.user
    ).select_related(
        "discipline",
    ).order_by(
        "-created_at"
    )

    submissions = Submission.objects.filter(
        assignment__discipline__teachers=request.user,
        grade__isnull=True,
    ).select_related(
        "student",
        "assignment",
        "assignment__discipline",
    ).order_by(
        "-submitted_at"
    )

    students_count = User.objects.filter(
        role=User.Role.STUDENT,
        enrolled_disciplines__teachers=request.user,
    ).distinct().count()

    context = {
        "disciplines": disciplines,
        "assignments": assignments[:5],
        "pending_submissions": submissions[:5],
        "students_count": students_count,
        "assignments_count": assignments.count(),
        "pending_submissions_count": submissions.count(),
        "disciplines_count": disciplines_count,
    }

    return render(
        request,
        "accounts/teacher_dashboard.html",
        context,
    )
@login_required
def student_dashboard(request):
    if request.user.role != "STUDENT":
        return render(
            request,
            "403.html",
            status=403,
        )

    disciplines = request.user.enrolled_disciplines.prefetch_related(
        "teachers",
        "assignments",
    )

    assignments = Assignment.objects.filter(
        discipline__students=request.user
    ).select_related(
        "discipline",
    ).order_by(
        "-deadline"
    )

    submissions = Submission.objects.filter(
        student=request.user
    ).select_related(
        "assignment",
        "assignment__discipline",
    ).order_by(
        "-submitted_at"
    )

    submitted_assignment_ids = submissions.values_list(
        "assignment_id",
        flat=True,
    )

    pending_assignments = assignments.exclude(
        pk__in=submitted_assignment_ids
    )

    graded_submissions = submissions.filter(
        grade__isnull=False
    )

    context = {
        "disciplines": disciplines,
        "assignments": assignments[:5],
        "pending_assignments": pending_assignments[:5],
        "submissions": submissions[:5],
        "graded_submissions": graded_submissions[:5],
        "disciplines_count": disciplines.count(),
        "assignments_count": assignments.count(),
        "pending_count": pending_assignments.count(),
        "graded_count": graded_submissions.count(),
    }

    return render(
        request,
        "accounts/student_dashboard.html",
        context,
    )


@login_required
def user_list(request):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        return render(
            request,
            "403.html",
            status=403,
        )

    users = User.objects.all().order_by(
        "role",
        "first_name",
        "last_name",
        "username",
    )

    return render(
        request,
        "accounts/user_list.html",
        {
            "users": users,
        },
    )


@login_required
def user_create(request):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        return render(
            request,
            "403.html",
            status=403,
        )

    if request.method == "POST":
        form = UserCreateForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("user_list")

    else:
        form = UserCreateForm()

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": "Нов потребител",
        },
    )


@login_required
def user_update(request, pk):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        return render(
            request,
            "403.html",
            status=403,
        )

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if request.method == "POST":
        form = UserUpdateForm(
            request.POST,
            instance=user,
        )

        if form.is_valid():
            form.save()
            return redirect("user_list")

    else:
        form = UserUpdateForm(
            instance=user,
        )

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "user_object": user,
            "title": "Редактиране на потребител",
        },
    )


@login_required
def user_delete(request, pk):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        return render(
            request,
            "403.html",
            status=403,
        )

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if user == request.user:
        return render(
            request,
            "403.html",
            status=403,
        )

    if request.method == "POST":
        user.delete()
        return redirect("user_list")

    return render(
        request,
        "accounts/user_confirm_delete.html",
        {
            "user_object": user,
        },
    )