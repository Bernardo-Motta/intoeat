from django.db import models


class Ocasiao(models.Model):
    nome = models.CharField(max_length=80)

    def __str__(self):
        return self.nome


class Caracteristica(models.Model):
    nome = models.CharField(max_length=80)

    def __str__(self):
        return self.nome


class Restaurante(models.Model):
    nome = models.CharField(max_length=120)
    endereco = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(max_length=80)

    def __str__(self):
        return self.nome