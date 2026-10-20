from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PerfilForm


@login_required
def perfil(request):
    """Mostra o perfil do usuario autenticado."""
    return render(request, "usuarios/perfil.html", {"usuario": request.user})


@login_required
def editar_perfil(request):
    """Exibe (GET) e processa (POST) o formulario de edicao do proprio perfil."""
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("usuarios:perfil")
        messages.error(request, "Não foi possível salvar. Corrija os erros abaixo.")
    else:
        form = PerfilForm(instance=request.user)
    return render(request, "usuarios/editar_perfil.html", {"form": form})
