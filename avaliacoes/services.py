from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import OuterRef, Subquery
from restaurantes.models import Caracteristica, Restaurante
from .models import Avaliacao


def restaurante_pode_receber_avaliacao(restaurante):
    return restaurante.status == Restaurante.Status.APROVADO


@transaction.atomic
def registrar_avaliacao(*, usuario, restaurante, nota, comentario="", caracteristicas=None):
    if not getattr(usuario, "is_authenticated", False):
        raise ValidationError("Faça login para avaliar um restaurante.")
    if not Restaurante.objects.aprovados().filter(pk=restaurante.pk).exists():
        raise ValidationError("Somente restaurantes aprovados podem receber avaliações.")
    if isinstance(nota, bool) or not isinstance(nota, int) or not 0 <= nota <= 5:
        raise ValidationError("A nota deve ser um número inteiro entre 0 e 5.")
    if comentario is None:
        comentario = ""
    if not isinstance(comentario, str):
        raise ValidationError("O comentário deve ser um texto.")

    # ModelMultipleChoiceField retorna uma queryset de Caracteristica.
    # Validar também no serviço impede associar tags inexistentes por outras chamadas.
    tags = list(caracteristicas) if caracteristicas is not None else []
    if any(not isinstance(tag, Caracteristica) or tag.pk is None for tag in tags):
        raise ValidationError("Selecione apenas tags cadastradas.")
    ids = {tag.pk for tag in tags}
    if Caracteristica.objects.filter(pk__in=ids).count() != len(ids):
        raise ValidationError("Selecione apenas tags cadastradas.")

    avaliacao = Avaliacao(
        usuario=usuario,
        restaurante=restaurante,
        nota=nota,
        comentario=comentario.strip(),
    )
    avaliacao.full_clean()
    avaliacao.save()
    if tags:
        avaliacao.caracteristicas.set(tags)
    return avaliacao


def avaliacoes_mais_recentes(restaurante=None):
    """Uma avaliação por (restaurante, usuário), escolhida por data e ID."""
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
