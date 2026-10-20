import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Usuario

MEDIA_TEMPORARIA = tempfile.mkdtemp()


def imagem_de_teste():
    """Gera um PNG valido em memoria para testar o upload de foto."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "red").save(buffer, format="PNG")
    return SimpleUploadedFile("foto.png", buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA_TEMPORARIA)
class BaseUsuarioTests(TestCase):
    """Base comum: media em pasta temporaria e um usuario (Ana) pronto."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORARIA, ignore_errors=True)

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="ana@exemplo.com",
            password="senha-forte-123",
            nome_completo="Ana Souza",
            biografia="Adoro comida japonesa.",
        )


class PerfilViewTests(BaseUsuarioTests):
    def setUp(self):
        super().setUp()
        self.url = reverse("usuarios:perfil")

    def test_visitante_e_redirecionado_para_o_login(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("admin:login"), resposta.url)

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
        self.assertContains(resposta, reverse("usuarios:editar_perfil"))
        self.assertContains(resposta, "Editar perfil")
        self.assertContains(resposta, "Minhas avaliações")


class EditarPerfilViewTests(BaseUsuarioTests):
    def setUp(self):
        super().setUp()
        self.url = reverse("usuarios:editar_perfil")
        self.url_perfil = reverse("usuarios:perfil")

    def dados(self, **alteracoes):
        """Dados validos de formulario; cada teste altera so o que importa."""
        dados = {
            "nome_completo": "Ana Souza Lima",
            "email": "ana@exemplo.com",
            "biografia": "Nova biografia.",
        }
        dados.update(alteracoes)
        return dados

    def test_visitante_e_redirecionado_para_o_login(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("admin:login"), resposta.url)

    def test_visitante_nao_consegue_enviar_o_formulario(self):
        resposta = self.client.post(self.url, self.dados(nome_completo="Invasor"))
        self.assertEqual(resposta.status_code, 302)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome_completo, "Ana Souza")

    def test_get_mostra_formulario_preenchido(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "usuarios/editar_perfil.html")
        self.assertContains(resposta, 'value="Ana Souza"')
        self.assertContains(resposta, 'value="ana@exemplo.com"')
        self.assertContains(resposta, "Adoro comida japonesa.")
        self.assertContains(resposta, "multipart/form-data")

    def test_post_valido_salva_e_redireciona_com_mensagem_de_sucesso(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(
            self.url,
            self.dados(email="ana.nova@exemplo.com"),
            follow=True,
        )
        self.assertRedirects(resposta, self.url_perfil)
        self.assertContains(resposta, "Perfil atualizado com sucesso.")
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome_completo, "Ana Souza Lima")
        self.assertEqual(self.usuario.email, "ana.nova@exemplo.com")
        self.assertEqual(self.usuario.biografia, "Nova biografia.")

    def test_pode_manter_o_proprio_email(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(self.url, self.dados())
        self.assertRedirects(resposta, self.url_perfil)

    def test_email_e_salvo_em_minusculas(self):
        self.client.force_login(self.usuario)
        self.client.post(self.url, self.dados(email="ANA.Nova@Exemplo.COM"))
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.email, "ana.nova@exemplo.com")

    def test_nome_vazio_e_rejeitado_e_nada_e_salvo(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(self.url, self.dados(nome_completo=""))
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("nome_completo", resposta.context["form"].errors)
        self.assertContains(resposta, "Corrija os erros abaixo")
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome_completo, "Ana Souza")
        self.assertEqual(self.usuario.biografia, "Adoro comida japonesa.")

    def test_email_invalido_e_rejeitado(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(self.url, self.dados(email="isso-nao-e-email"))
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("email", resposta.context["form"].errors)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.email, "ana@exemplo.com")

    def test_email_de_outro_usuario_e_rejeitado(self):
        Usuario.objects.create_user(
            email="bia@exemplo.com",
            password="senha-forte-123",
            nome_completo="Bia Lima",
        )
        self.client.force_login(self.usuario)
        # Mesmo escrevendo com maiusculas, conta como o mesmo login da Bia.
        resposta = self.client.post(self.url, self.dados(email="BIA@exemplo.com"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Já existe um usuário com este e-mail.")
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.email, "ana@exemplo.com")

    def test_edita_somente_o_proprio_usuario(self):
        bia = Usuario.objects.create_user(
            email="bia@exemplo.com",
            password="senha-forte-123",
            nome_completo="Bia Lima",
            biografia="Bio da Bia.",
        )
        self.client.force_login(self.usuario)
        self.client.post(self.url, self.dados(nome_completo="Ana Editada"))
        bia.refresh_from_db()
        self.assertEqual(bia.nome_completo, "Bia Lima")
        self.assertEqual(bia.biografia, "Bio da Bia.")

    def test_post_com_foto_valida_salva_a_foto(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(self.url, {**self.dados(), "foto": imagem_de_teste()})
        self.assertRedirects(resposta, self.url_perfil)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.foto)
        self.assertTrue(self.usuario.foto.name.startswith("fotos_perfil/"))

    def test_arquivo_que_nao_e_imagem_e_rejeitado(self):
        self.client.force_login(self.usuario)
        falso = SimpleUploadedFile("foto.png", b"isto nao e uma imagem", content_type="image/png")
        resposta = self.client.post(self.url, {**self.dados(), "foto": falso})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("foto", resposta.context["form"].errors)
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.foto)
