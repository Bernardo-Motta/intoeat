from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Avaliacao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="avaliacoes")
    restaurante = models.ForeignKey("restaurantes.Restaurante", on_delete=models.CASCADE, related_name="avaliacoes")
    nota = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    comentario = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    ocasioes = models.ManyToManyField("restaurantes.Ocasiao", blank=True, related_name="avaliacoes")
    caracteristicas = models.ManyToManyField("restaurantes.Caracteristica", blank=True, related_name="avaliacoes")

    class Meta:
        ordering = ["-data"]
        constraints = [models.CheckConstraint(condition=models.Q(nota__gte=0, nota__lte=5), name="avaliacao_nota_entre_0_e_5")]

    def __str__(self):
        return f"{self.restaurante} - {self.nota}/5"
