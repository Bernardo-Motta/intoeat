from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from restaurantes.models import Restaurante
from .forms import AvaliacaoForm
from .services import avaliacao_do_usuario, registrar_avaliacao


@login_required
def criar_avaliacao(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante.objects.aprovados(), pk=restaurante_id)
    anterior = avaliacao_do_usuario(request.user, restaurante)
    inicial = None
    if anterior is not None:
        # "Editar avaliação": abre o formulário com os valores da avaliação vigente.
        inicial = {
            "nota": anterior.nota,
            "comentario": anterior.comentario,
            "caracteristicas": [tag.pk for tag in anterior.caracteristicas.all()],
        }
    form = AvaliacaoForm(request.POST or None, initial=inicial)
    if request.method == "POST" and form.is_valid():
        try:
            registrar_avaliacao(usuario=request.user, restaurante=restaurante, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("restaurantes:perfil", restaurante_id=restaurante.pk)
    return render(request, "avaliacoes/formulario.html", {"form": form, "restaurante": restaurante, "editando": anterior is not None})


@login_required
def sucesso(request, restaurante_id):
    return redirect("restaurantes:perfil", restaurante_id=restaurante_id)


@login_required
def minhas_avaliacoes(request):
    # Histórico completo: não aplicar o filtro de avaliações mais recentes.
    avaliacoes = (
        request.user.avaliacoes
        .select_related("restaurante")
        .prefetch_related("caracteristicas")
        .order_by("-data", "-pk")
    )
    return render(request, "avaliacoes/minhas_avaliacoes.html", {
        "avaliacoes": avaliacoes,
        "identificador": request.user.email.partition("@")[0],
        "estrelas": range(1, 6),
    })
