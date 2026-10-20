from django.urls import path
from . import views

app_name = "restaurantes"
urlpatterns = [
    path("", views.lista_restaurantes, name="lista"),
    path("novo/", views.cadastrar_restaurante, name="cadastrar"),
    path("meus/", views.meus_restaurantes, name="meus"),
    path("<int:restaurante_id>/", views.perfil_restaurante, name="perfil"),
]
