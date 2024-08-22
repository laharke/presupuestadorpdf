
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout_view"),
    path("abm_dispositivos", views.abm_dispositivos, name="abm_dispositivos"),
    path("borrar_dispositivo", views.borrar_dispositivo, name="borrar_dispositivo"),
    path("edit_dispositivos", views.edit_dispositivos, name="edit_dispositivos"),
    path("generar_pdf", views.generar_pdf, name="generar_pdf"),
]
