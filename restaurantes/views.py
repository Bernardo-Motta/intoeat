from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from avaliacoes.services import avaliacao_do_usuario, avaliacoes_mais_recentes
from .forms import RestauranteForm
from .models import Caracteristica, Ocasiao, Restaurante
from .services import solicitar_restaurante


def lista_restaurantes(request):
    restaurantes = Restaurante.objects.aprovados().order_by("nome")
    return render(request, "restaurantes/lista.html", {"restaurantes": restaurantes})


AVALIACOES_POR_PAGINA = 5
DESTAQUES_NO_PERFIL = 3


def _mais_citados(modelo, avaliacoes):
    """Itens (características/ocasiões) mais citados nas avaliações vigentes, contados no banco."""
    itens = (
        modelo.objects.filter(avaliacoes__in=avaliacoes.values("pk"))
        .annotate(total=Count("avaliacoes"))
        .order_by("-total", "nome")[:DESTAQUES_NO_PERFIL]
    )
    return [{"nome": item.nome, "total": item.total} for item in itens]


def perfil_restaurante(request, restaurante_id):
    restaurante = get_object_or_404(
        Restaurante.objects.aprovados().prefetch_related("fotos"), pk=restaurante_id
    )
    # O perfil coletivo considera apenas a avaliação mais recente de cada pessoa.
    vigentes = avaliacoes_mais_recentes(restaurante)
    resumo = vigentes.aggregate(media=Avg("nota"), total=Count("id"))

    lista = (
        vigentes.select_related("usuario")
        .prefetch_related("caracteristicas")
        .order_by("-data", "-pk")
    )
    pagina = Paginator(lista, AVALIACOES_POR_PAGINA).get_page(request.GET.get("pagina"))

    return render(request, "restaurantes/perfil.html", {
        "restaurante": restaurante,
        "avaliacoes": pagina,
        "resumo": resumo,
        "minha_avaliacao": avaliacao_do_usuario(request.user, restaurante),
        "caracteristicas_destaque": _mais_citados(Caracteristica, vigentes),
        "ocasioes_destaque": _mais_citados(Ocasiao, vigentes),
        "estrelas": range(1, 6),
    })


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
    restaurantes = Restaurante.objects.filter(criado_por=request.user).order_by("nome")
    return render(request, "restaurantes/meus.html", {"restaurantes": restaurantes})
