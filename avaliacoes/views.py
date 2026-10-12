from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from restaurantes.models import Restaurante
from .forms import AvaliacaoForm
from .services import registrar_avaliacao


@login_required
def criar_avaliacao(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante.objects.aprovados(), pk=restaurante_id)
    form = AvaliacaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            registrar_avaliacao(usuario=request.user, restaurante=restaurante, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("restaurantes:perfil", restaurante_id=restaurante.pk)
    return render(request, "avaliacoes/formulario.html", {"form": form, "restaurante": restaurante})


@login_required
def sucesso(request, restaurante_id):
    return redirect("restaurantes:perfil", restaurante_id=restaurante_id)


@login_required
def minhas_avaliacoes(request):
    # Histórico completo: não aplicar o filtro de avaliações mais recentes.
    avaliacoes = (
        request.user.avaliacoes
        .select_related("restaurante")
        .order_by("-data", "-pk")
    )
    return render(request, "avaliacoes/minhas_avaliacoes.html", {"avaliacoes": avaliacoes})
