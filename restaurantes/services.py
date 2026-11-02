import re
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Restaurante


def validar_cnpj(valor):
    digitos = re.sub(r"\D", "", str(valor))
    if len(digitos) != 14 or len(set(digitos)) == 1:
        raise ValidationError("CNPJ inválido.")
    def verificador(parcial, pesos):
        resto = sum(int(a) * b for a, b in zip(parcial, pesos)) % 11
        return 0 if resto < 2 else 11 - resto
    primeiro = verificador(digitos[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    segundo = verificador(digitos[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    if digitos[-2:] != f"{primeiro}{segundo}":
        raise ValidationError("CNPJ inválido.")
    return digitos


def solicitar_restaurante(*, usuario, nome, tipo_cozinha, endereco, cidade, cnpj, descricao=""):
    if not usuario.is_authenticated:
        raise ValidationError("É necessário fazer login.")
    cnpj = validar_cnpj(cnpj)
    if Restaurante.objects.filter(cnpj=cnpj, status__in=[Restaurante.Status.PENDENTE, Restaurante.Status.APROVADO]).exists():
        raise ValidationError("Já existe uma solicitação ativa para este CNPJ.")
    restaurante = Restaurante(nome=nome, tipo_cozinha=tipo_cozinha, endereco=endereco, cidade=cidade, cnpj=cnpj,
                             descricao=descricao, criado_por=usuario)
    restaurante.full_clean()
    restaurante.save()
    return restaurante


@transaction.atomic
def aprovar_restaurante(restaurante):
    restaurante.status = Restaurante.Status.APROVADO
    restaurante.motivo_rejeicao = ""
    restaurante.full_clean()
    restaurante.save(update_fields=["status", "motivo_rejeicao"])
    return restaurante


@transaction.atomic
def rejeitar_restaurante(restaurante, motivo):
    if not motivo or not motivo.strip():
        raise ValidationError("Informe o motivo da rejeição.")
    restaurante.status = Restaurante.Status.REJEITADO
    restaurante.motivo_rejeicao = motivo.strip()
    restaurante.full_clean()
    restaurante.save(update_fields=["status", "motivo_rejeicao"])
    return restaurante
