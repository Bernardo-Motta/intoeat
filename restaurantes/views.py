from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from avaliacoes.services import avaliacoes_mais_recentes
from .forms import RestauranteForm
from .models import Restaurante
from .services import solicitar_restaurante


def lista_restaurantes(request):
    restaurantes = Restaurante.objects.aprovados().order_by("nome")
    return render(request, "restaurantes/lista.html", {"restaurantes": restaurantes})


def perfil_restaurante(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante.objects.aprovados(), pk=restaurante_id)
    avaliacoes = avaliacoes_mais_recentes(restaurante).select_related("usuario").order_by("-data", "-pk")
    resumo = avaliacoes.aggregate(media=Avg("nota"), total=Count("id"))
    return render(request, "restaurantes/perfil.html", {"restaurante": restaurante, "avaliacoes": avaliacoes, "resumo": resumo})


@login_required
def cadastrar_restaurante(request):
    form = RestauranteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            solicitar_restaurante(usuario=request.user, **form.cleaned_data)
        except ValidationError as erro:
            form.add_error(None, erro)
        else:
            return redirect("restaurantes:meus")
    return render(request, "restaurantes/cadastro.html", {"form": form})


@login_required
def meus_restaurantes(request):
    restaurantes = Restaurante.objects.filter(solicitante=request.user).order_by("nome")
    return render(request, "restaurantes/meus.html", {"restaurantes": restaurantes})
