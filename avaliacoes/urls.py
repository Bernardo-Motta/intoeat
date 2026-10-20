from django.urls import path
from . import views

app_name = "avaliacoes"
urlpatterns = [
    path("minhas-avaliacoes/", views.minhas_avaliacoes, name="minhas"),
    path("restaurantes/<int:restaurante_id>/avaliar/", views.criar_avaliacao, name="criar"),
    path("restaurantes/<int:restaurante_id>/avaliacao-enviada/", views.sucesso, name="sucesso"),
]
