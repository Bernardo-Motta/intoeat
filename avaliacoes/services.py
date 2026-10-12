from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import OuterRef, Subquery
from restaurantes.models import Restaurante
from .models import Avaliacao


def restaurante_pode_receber_avaliacao(restaurante):
    return restaurante.status == Restaurante.Status.APROVADO


@transaction.atomic
def registrar_avaliacao(*, usuario, restaurante, nota, comentario):
    if not usuario.is_authenticated:
        raise ValidationError("Faça login para avaliar um restaurante.")
    if not Restaurante.objects.aprovados().filter(pk=restaurante.pk).exists():
        raise ValidationError("Somente restaurantes aprovados podem receber avaliações.")
    if isinstance(nota, bool) or not isinstance(nota, int) or not 0 <= nota <= 5:
        raise ValidationError("A nota deve ser um número inteiro entre 0 e 5.")
    if not isinstance(comentario, str) or not comentario.strip():
        raise ValidationError("O comentário é obrigatório.")
    avaliacao = Avaliacao(usuario=usuario, restaurante=restaurante, nota=nota, comentario=comentario.strip())
    avaliacao.full_clean()
    avaliacao.save()
    return avaliacao


def avaliacoes_mais_recentes(restaurante=None):
    """Uma avaliação por (restaurante, usuário), escolhida por data e ID.

    Retorna QuerySet para permitir agregações no banco (Avg, Count etc.).
    """
    mais_recente = (
        Avaliacao.objects.filter(
            restaurante_id=OuterRef("restaurante_id"),
            usuario_id=OuterRef("usuario_id"),
        )
        .order_by("-data", "-pk")
        .values("pk")[:1]
    )
    avaliacoes = Avaliacao.objects.filter(pk=Subquery(mais_recente))
    if restaurante is not None:
        avaliacoes = avaliacoes.filter(restaurante=restaurante)
    return avaliacoes
