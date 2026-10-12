from django.test import TestCase
from django.urls import reverse

from .models import Usuario

SENHA = "SenhaForte#2026"


class CadastroLoginTests(TestCase):
    def test_cadastro_cria_usuario_e_faz_login(self):
        resposta = self.client.post(reverse("usuarios:cadastro"), {
            "nome_completo": "Maria Silva",
            "email": "maria@exemplo.com",
            "password1": SENHA,
            "password2": SENHA,
        })
        self.assertRedirects(resposta, reverse("home"))
        self.assertTrue(Usuario.objects.filter(email="maria@exemplo.com").exists())

    def test_email_duplicado_e_rejeitado(self):
        Usuario.objects.create_user(
            email="joao@exemplo.com", password=SENHA, nome_completo="Joao"
        )
        resposta = self.client.post(reverse("usuarios:cadastro"), {
            "nome_completo": "Outro Joao",
            "email": "JOAO@exemplo.com",
            "password1": SENHA,
            "password2": SENHA,
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            Usuario.objects.filter(email__iexact="joao@exemplo.com").count(), 1
        )

    def test_login_com_email(self):
        Usuario.objects.create_user(
            email="ana@exemplo.com", password=SENHA, nome_completo="Ana"
        )
        resposta = self.client.post(reverse("usuarios:login"), {
            "username": "ana@exemplo.com",
            "password": SENHA,
        })
        self.assertRedirects(resposta, reverse("home"))