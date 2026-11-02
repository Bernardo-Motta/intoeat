from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from restaurantes.models import Ocasiao
from .forms import BuscaForm
from .services import buscar_restaurantes


# HU08: intenções predefinidas, a partir das ocasiões do domínio.
INTENCOES = {
    "encontro": ("Encontro", "Um lugar para um encontro"),
    "familia": ("Família", "Um lugar para a família"),
    "amigos": ("Amigos", "Um lugar para reunir amigos"),
    "comemoracao": ("Comemoração", "Um lugar para comemorar"),
    "descobrir": (None, "Descobrir restaurantes"),
}
RESULTADOS_POR_PAGINA = 12


def _pagina(request, itens):
    return Paginator(itens, RESULTADOS_POR_PAGINA).get_page(request.GET.get("pagina"))


def busca_com_filtros(request):
    form = BuscaForm(request.GET or None)
    resultados = []
    if form.is_valid():
        dados = form.cleaned_data
        resultados = buscar_restaurantes(
            texto=dados["q"], ocasioes=dados["ocasioes"],
            caracteristicas=dados["caracteristicas"],
        )
    parametros = request.GET.copy()
    parametros.pop("pagina", None)
    return render(request, "busca/resultados.html", {
        "querystring": parametros.urlencode(),
        "form": form,
        "resultados": _pagina(request, resultados),
        "total": len(resultados),
        "titulo": "Encontrar restaurantes",
        "com_filtros": bool(form.is_valid() and (form.cleaned_data["ocasioes"] or form.cleaned_data["caracteristicas"])),
        "modo": "filtros",
    })


def intencoes(request):
    return render(request, "busca/intencoes.html", {
        "intencoes": [(slug, titulo) for slug, (_, titulo) in INTENCOES.items()],
    })


def resultados_intencao(request, slug):
    if slug not in INTENCOES:
        raise Http404("Intenção desconhecida")
    nome, titulo = INTENCOES[slug]
    selecionadas = list(Ocasiao.objects.filter(nome__iexact=nome)[:1]) if nome else []
    resultados = buscar_restaurantes(ocasioes=selecionadas)
    return render(request, "busca/resultados.html", {
        "resultados": _pagina(request, resultados),
        "total": len(resultados),
        "titulo": titulo,
        "com_filtros": bool(selecionadas),
        "modo": "intencao",
        "intencao": slug,
        "aviso": ("Esta intenção apresenta os restaurantes aprovados por nota geral; "
                  "a recomendação personalizada de lugares não visitados pertence à HU09.") if slug == "descobrir" else "",
    })


def categorias_ocasiao(request):
    return render(request, "busca/ocasioes.html", {
        "ocasioes": Ocasiao.objects.all().order_by("nome", "pk"),
    })


def resultados_ocasiao(request, ocasiao_id):
    ocasiao = get_object_or_404(Ocasiao, pk=ocasiao_id)
    resultados = buscar_restaurantes(ocasioes=[ocasiao])
    return render(request, "busca/resultados.html", {
        "resultados": _pagina(request, resultados),
        "total": len(resultados),
        "titulo": f"Restaurantes para {ocasiao.nome}",
        "com_filtros": True,
        "modo": "ocasiao",
        "ocasiao": ocasiao,
    })
