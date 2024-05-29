from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "books"

urlpatterns = [
    path("", views.index, name="index"),
    path("sign_up", views.sign_up, name="sign_up"),
    path("logout_user/", TemplateView.as_view(template_name='registration/logout_user.html'), name='logout_user'),
]