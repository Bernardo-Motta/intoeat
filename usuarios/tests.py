import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Usuario

SENHA = "SenhaForte#2026"
MEDIA_TEMPORARIA = tempfile.mkdtemp()


def imagem_de_teste():
    """Gera um PNG valido em memoria para testar o upload de foto."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "red").save(buffer, format="PNG")
    return SimpleUploadedFile("foto.png", buffer.getvalue(), content_type="image/png")


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

    def test_login_com_email_em_maiusculas(self):
        Usuario.objects.create_user(
            email="ana@exemplo.com", password=SENHA, nome_completo="Ana"
        )
        resposta = self.client.post(reverse("usuarios:login"), {
            "username": "ANA@Exemplo.com",
            "password": SENHA,
        })
        self.assertRedirects(resposta, reverse("home"))


@override_settings(MEDIA_ROOT=MEDIA_TEMPORARIA)
class PerfilViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORARIA, ignore_errors=True)

    def setUp(self):
        self.url = reverse("usuarios:perfil")
        self.usuario = Usuario.objects.create_user(
            email="ana@exemplo.com",
            password="senha-forte-123",
            nome_completo="Ana Souza",
            biografia="Adoro comida japonesa.",
        )

    def test_visitante_e_redirecionado_para_o_login(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("usuarios:login"), resposta.url)

    def test_usuario_logado_ve_nome_login_e_biografia(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "usuarios/perfil.html")
        self.assertContains(resposta, "Ana Souza")
        self.assertContains(resposta, "ana@exemplo.com")
        self.assertContains(resposta, "Adoro comida japonesa.")

    def test_sem_biografia_mostra_mensagem_padrao(self):
        self.usuario.biografia = ""
        self.usuario.save()
        self.client.force_login(self.usuario)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "ainda não escreveu uma biografia")

    def test_sem_foto_mostra_inicial_do_nome(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(self.url)
        self.assertNotContains(resposta, "<img")
        self.assertContains(resposta, "foto-padrao")

    def test_com_foto_mostra_a_imagem(self):
        self.usuario.foto = imagem_de_teste()
        self.usuario.save()
        self.client.force_login(self.usuario)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "<img")
        self.assertContains(resposta, self.usuario.foto.url)

    def test_mostra_apenas_os_dados_do_proprio_usuario(self):
        Usuario.objects.create_user(
            email="bia@exemplo.com",
            password="senha-forte-123",
            nome_completo="Bia Lima",
            biografia="Bio da Bia.",
        )
        self.client.force_login(self.usuario)
        resposta = self.client.get(self.url)
        self.assertNotContains(resposta, "Bia Lima")
        self.assertNotContains(resposta, "bia@exemplo.com")

    def test_pagina_tem_links_de_editar_e_avaliacoes(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Editar perfil")
        self.assertContains(resposta, "Minhas avaliações")