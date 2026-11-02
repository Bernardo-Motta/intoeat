"""HU07/HU08/HU15: consultas e pontuação por compatibilidade.

Somente avaliações vigentes: uma por usuário/restaurante. A nota média funciona
como desempate; não substitui a pertinência à ocasião/características.
"""
from dataclasses import dataclass

from django.db.models import Avg, Count, Q

from avaliacoes.services import avaliacoes_mais_recentes
from restaurantes.models import Restaurante

# Pesos do MVP, documentados e sujeitos a avaliação na Sprint II.
PESO_OCASIAO = 0.60
PESO_CARACTERISTICAS = 0.40
# Equivale a 2 avaliações neutras fictícias: reduz o peso de 1 voto isolado.
FORCA_SUAVIZACAO = 2
PRIOR_NEUTRO = 0.50


@dataclass(frozen=True)
class ResultadoBusca:
    restaurante: Restaurante
    compatibilidade: float | None
    nota_media: float | None
    total_avaliacoes: int
    percentual_ocasioes: float | None
    percentual_caracteristicas: float | None


def _contagens_por_escolha(avaliacoes, campo, selecionadas):
    """Em uma consulta SQL, conta votos para cada ID selecionado/restaurante."""
    ids = [item.pk for item in selecionadas]
    if not ids:
        return {}
    linhas = (
        avaliacoes.filter(**{f"{campo}__in": ids})
        .order_by()
        .values("restaurante_id", campo)
        .annotate(quantidade=Count("pk", distinct=True))
    )
    return {(linha["restaurante_id"], linha[campo]): linha["quantidade"] for linha in linhas}


def _percentual_medio(restaurante_id, total, selecionadas, votos):
    if not selecionadas or total == 0:
        return None
    proporcoes = [votos.get((restaurante_id, item.pk), 0) / total for item in selecionadas]
    return sum(proporcoes) / len(proporcoes)


def _suavizar(percentual, total):
    """Suavização bayesiana de proporções (prior de 50%, força 2)."""
    return (percentual * total + PRIOR_NEUTRO * FORCA_SUAVIZACAO) / (total + FORCA_SUAVIZACAO)


def buscar_restaurantes(*, texto="", ocasioes=None, caracteristicas=None):
    """Lista aprovada, filtrada por texto e ordenada por compatibilidade.

    Usa agregações SQL para não materializar todo o histórico de avaliações,
    e nunca dá peso às avaliações antigas de um mesmo usuário.
    """
    ocasioes = list(ocasioes or [])
    caracteristicas = list(caracteristicas or [])
    texto = (texto or "").strip()[:120]
    queryset = Restaurante.objects.aprovados()
    if texto:
        queryset = queryset.filter(Q(nome__icontains=texto) | Q(tipo_cozinha__icontains=texto))
    restaurantes = list(queryset.order_by("nome", "pk"))
    if not restaurantes:
        return []

    ids_restaurantes = [r.pk for r in restaurantes]
    vigentes = avaliacoes_mais_recentes().filter(restaurante_id__in=ids_restaurantes)
    resumo = {
        item["restaurante_id"]: item
        for item in vigentes.order_by().values("restaurante_id").annotate(
            total=Count("pk", distinct=True), media=Avg("nota")
        )
    }
    votos_ocasioes = _contagens_por_escolha(vigentes, "ocasioes", ocasioes)
    votos_caracteristicas = _contagens_por_escolha(vigentes, "caracteristicas", caracteristicas)
    com_filtros = bool(ocasioes or caracteristicas)
    saida = []

    for restaurante in restaurantes:
        item = resumo.get(restaurante.pk, {})
        total = item.get("total", 0)
        media = item.get("media")
        percentual_oc = _percentual_medio(restaurante.pk, total, ocasioes, votos_ocasioes)
        percentual_ca = _percentual_medio(restaurante.pk, total, caracteristicas, votos_caracteristicas)

        compatibilidade = None
        if com_filtros:
            if not total:
                compatibilidade = 0.0  # sem dados: não afirmar 50% de recomendação
            elif percentual_oc is not None and percentual_ca is not None:
                compatibilidade = 100 * (
                    PESO_OCASIAO * _suavizar(percentual_oc, total)
                    + PESO_CARACTERISTICAS * _suavizar(percentual_ca, total)
                )
            elif percentual_oc is not None:
                compatibilidade = 100 * _suavizar(percentual_oc, total)
            else:
                compatibilidade = 100 * _suavizar(percentual_ca, total)

        saida.append(ResultadoBusca(
            restaurante=restaurante,
            compatibilidade=round(compatibilidade, 1) if compatibilidade is not None else None,
            nota_media=round(float(media), 1) if media is not None else None,
            total_avaliacoes=total,
            percentual_ocasioes=round(100 * percentual_oc, 1) if percentual_oc is not None else None,
            percentual_caracteristicas=round(100 * percentual_ca, 1) if percentual_ca is not None else None,
        ))

    # Sem filtros, usa nota geral; com filtros, compatibilidade é o critério principal.
    # Total de avaliações e nome garantem desempate reprodutível.
    saida.sort(key=lambda r: (
        -(r.compatibilidade if com_filtros else (r.nota_media if r.nota_media is not None else -1)),
        -(r.nota_media if r.nota_media is not None else -1),
        -r.total_avaliacoes,
        r.restaurante.nome.casefold(),
        r.restaurante.pk,
    ))
    return saida
