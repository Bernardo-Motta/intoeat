from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CadastroForm


def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("home")
    else:
        form = CadastroForm()
    return render(request, "usuarios/cadastro.html", {"form": form})


@login_required
def perfil(request):
    """Mostra o perfil do usuario autenticado."""
    return render(request, "usuarios/perfil.html", {"usuario": request.user})