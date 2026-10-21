from django.conf import settings
from django.db import models
from django.db.models import Q


class Ocasiao(models.Model):
    nome = models.CharField(max_length=80)
    def __str__(self):
        return self.nome


class Caracteristica(models.Model):
    nome = models.CharField(max_length=80)
    def __str__(self):
        return self.nome


class RestauranteQuerySet(models.QuerySet):
    def aprovados(self):
        return self.filter(status=Restaurante.Status.APROVADO)


class Restaurante(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADO = "aprovado", "Aprovado"
        REJEITADO = "rejeitado", "Rejeitado"

    nome = models.CharField(max_length=120, db_index=True)
    endereco = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100, blank=True)
    descricao = models.TextField(blank=True)
    tipo_cozinha = models.CharField(max_length=80)
    cnpj = models.CharField(max_length=14, blank=True, db_index=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="restaurantes_criados")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE, db_index=True)
    motivo_rejeicao = models.TextField(blank=True)
    objects = RestauranteQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cnpj"], condition=Q(status__in=["pendente", "aprovado"]) & ~Q(cnpj=""), name="cnpj_ativo_unico")
        ]

    def __str__(self):
        return self.nome
