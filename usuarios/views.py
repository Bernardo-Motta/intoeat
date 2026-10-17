from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def perfil(request):
    """Mostra o perfil do usuario autenticado."""
    return render(request, "usuarios/perfil.html", {"usuario": request.user})
