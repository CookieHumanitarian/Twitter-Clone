
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newPost", views.newPost, name="newPost"),
    path("profileView/<str:user>", views.profileView, name="profileView"),
    path("followView/<str:profileUsername>/<str:currentUsername>", views.followView, name="followView"),
    path("followPage", views.followPage, name="followPage"),
    path("editView", views.editView, name="editView"),
    path("like", views.like, name="like"),
]
