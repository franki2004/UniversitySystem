from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.discipline_list,
        name="discipline_list",
    ),

    path(
        "create/",
        views.discipline_create,
        name="discipline_create",
    ),

    path(
        "<int:pk>/",
        views.discipline_detail,
        name="discipline_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.discipline_update,
        name="discipline_update",
    ),

    path(
        "<int:pk>/delete/",
        views.discipline_delete,
        name="discipline_delete",
    ),
]