from django.urls import path
from . import views

app_name = "busca"
urlpatterns = [
    path("", views.busca_com_filtros, name="filtros"),
    path("intencoes/", views.intencoes, name="intencoes"),
    path("intencoes/<slug:slug>/", views.resultados_intencao, name="resultado_intencao"),
    path("ocasioes/", views.categorias_ocasiao, name="ocasioes"),
    path("ocasioes/<int:ocasiao_id>/", views.resultados_ocasiao, name="resultado_ocasiao"),
]
