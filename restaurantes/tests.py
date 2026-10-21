from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from usuarios.models import Usuario
from .models import Restaurante
from .services import validar_cnpj, solicitar_restaurante, aprovar_restaurante, rejeitar_restaurante


class RestauranteTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(email="dono@example.com", password="senha123456", nome_completo="Dono")

    def test_cnpj(self):
        self.assertEqual(validar_cnpj("11.222.333/0001-81"), "11222333000181")
        for cnpj in ("11111111111111", "11222333000182", "123"):
            with self.assertRaises(ValidationError):
                validar_cnpj(cnpj)

    def test_fluxo_solicitar_aprovar_e_listar(self):
        restaurante = solicitar_restaurante(usuario=self.usuario, nome="Café", tipo_cozinha="Café", endereco="Rua A", cidade="SP", cnpj="11222333000181")
        self.assertEqual(restaurante.status, Restaurante.Status.PENDENTE)
        self.assertEqual(restaurante.criado_por, self.usuario)
        self.assertEqual(restaurante.tipo_cozinha, "Café")
        self.assertNotContains(self.client.get(reverse("restaurantes:lista")), "Café")
        aprovar_restaurante(restaurante)
        self.assertContains(self.client.get(reverse("restaurantes:lista")), "Café")
        self.assertEqual(Restaurante.objects.aprovados().count(), 1)

    def test_cnpj_duplicado_ativo(self):
        kwargs = dict(usuario=self.usuario, nome="Café", tipo_cozinha="Café", endereco="Rua A", cidade="SP", cnpj="11222333000181")
        solicitar_restaurante(**kwargs)
        with self.assertRaises(ValidationError):
            solicitar_restaurante(**kwargs)

    def test_rejeitado_pode_ser_solicitado_novamente(self):
        kwargs = dict(usuario=self.usuario, nome="Café", tipo_cozinha="Café", endereco="Rua A", cidade="SP", cnpj="11222333000181")
        restaurante = solicitar_restaurante(**kwargs)
        rejeitar_restaurante(restaurante, "Dados incompletos")
        self.assertEqual(solicitar_restaurante(**kwargs).status, Restaurante.Status.PENDENTE)

    def test_solicitacao_exige_login(self):
        self.assertEqual(self.client.get(reverse("restaurantes:cadastrar")).status_code, 302)
