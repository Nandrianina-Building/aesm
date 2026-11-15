from django.urls import path

from . import views

app_name = "publications"
urlpatterns = [
    path("", views.publication_list, name="list"),
    path("commentaires/<int:pk>/modifier/", views.comment_edit, name="comment_edit"),
    path("commentaires/<int:pk>/supprimer/", views.comment_delete, name="comment_delete"),
    path("commentaires/<int:pk>/signaler/", views.comment_report, name="comment_report"),
    path("<slug:slug>/", views.publication_detail, name="detail"),
    path("<slug:slug>/aimer/", views.like, name="like"),
    path("<slug:slug>/epingler/", views.toggle_pin, name="toggle_pin"),
    path("<slug:slug>/verrouiller/", views.toggle_lock, name="toggle_lock"),
    path("<slug:slug>/commenter/", views.comment_add, name="comment_add"),
]
