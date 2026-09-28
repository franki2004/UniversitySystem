from django.urls import path

from . import views


urlpatterns = [
    path(
        "discipline/<int:discipline_pk>/create/",
        views.assignment_create,
        name="assignment_create",
    ),

    path(
        "<int:pk>/",
        views.assignment_detail,
        name="assignment_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.assignment_update,
        name="assignment_update",
    ),

    path(
        "<int:pk>/delete/",
        views.assignment_delete,
        name="assignment_delete",
    ),

    path(
        "<int:assignment_pk>/submit/",
        views.submit_assignment,
        name="submit_assignment",
    ),

    path(
        "<int:assignment_pk>/submissions/",
        views.submission_list,
        name="submission_list",
    ),

    path(
        "submission/<int:pk>/grade/",
        views.grade_submission,
        name="grade_submission",
    ),
]