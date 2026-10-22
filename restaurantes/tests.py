import shutil
import tempfile
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from avaliacoes.models import Avaliacao
from avaliacoes.services import registrar_avaliacao
from usuarios.models import Usuario
from .models import Caracteristica, FotoRestaurante, Restaurante
from .views import AVALIACOES_POR_PAGINA
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


SENHA = "SenhaForte#2026"
BOTAO_ANTERIOR = 'data-carousel-prev aria-label="Foto anterior"'
BOTAO_PROXIMO = 'data-carousel-next aria-label="Próxima foto"'
GIF_MINIMO = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00"
    b",\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class PerfilRestauranteTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        media = tempfile.mkdtemp()
        cls.enterClassContext(override_settings(MEDIA_ROOT=media))
        cls.addClassCleanup(shutil.rmtree, media, True)

    def setUp(self):
        self.restaurante = Restaurante.objects.create(
            nome="Casa do Sabor", endereco="Rua Central, 10", cidade="São João del Rei",
            descricao="Comida mineira caseira.", tipo_cozinha="Mineira",
            horario_funcionamento="Seg a Sáb, 11h às 22h", telefone="(32) 3333-4444",
            status=Restaurante.Status.APROVADO,
        )
        self.url = reverse("restaurantes:perfil", args=[self.restaurante.pk])
        self._n = 0

    # ---- auxiliares
    def novo_usuario(self):
        self._n += 1
        return Usuario.objects.create_user(
            email=f"pessoa{self._n}@example.com", password=SENHA, nome_completo=f"Pessoa {self._n}"
        )

    def avaliar(self, nota, usuario=None, **kwargs):
        return registrar_avaliacao(
            usuario=usuario or self.novo_usuario(), restaurante=self.restaurante, nota=nota, **kwargs
        )

    def adicionar_foto(self, ordem, legenda=""):
        return FotoRestaurante.objects.create(
            restaurante=self.restaurante, ordem=ordem, legenda=legenda,
            imagem=SimpleUploadedFile(f"foto{ordem}.gif", GIF_MINIMO, content_type="image/gif"),
        )

    # ---- URL, status 200 e 404
    def test_url_de_detalhe(self):
        self.assertEqual(self.url, f"/restaurantes/{self.restaurante.pk}/")

    def test_perfil_existente_retorna_200_com_dados_do_restaurante(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        for texto in ("Casa do Sabor", "Comida mineira caseira.", "Rua Central, 10",
                      "Seg a Sáb, 11h às 22h", "(32) 3333-4444"):
            self.assertContains(resposta, texto)

    def test_horario_e_telefone_ausentes_mostram_nao_informado(self):
        Restaurante.objects.filter(pk=self.restaurante.pk).update(horario_funcionamento="", telefone="")
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Não informado", count=2)

    def test_perfil_inexistente_retorna_404(self):
        self.assertEqual(self.client.get(reverse("restaurantes:perfil", args=[999999])).status_code, 404)

    def test_perfil_de_restaurante_nao_aprovado_retorna_404(self):
        for status in (Restaurante.Status.PENDENTE, Restaurante.Status.REJEITADO):
            with self.subTest(status=status):
                Restaurante.objects.filter(pk=self.restaurante.pk).update(status=status)
                self.assertEqual(self.client.get(self.url).status_code, 404)

    # ---- nota média e total
    def test_media_e_total_de_avaliacoes(self):
        for nota in (5, 4, 3):
            self.avaliar(nota)
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["resumo"]["media"], 4)
        self.assertEqual(resposta.context["resumo"]["total"], 3)
        self.assertContains(resposta, "3 avaliações")

    def test_media_com_casas_decimais(self):
        self.avaliar(5)
        self.avaliar(4)
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["resumo"]["media"], 4.5)
        self.assertContains(resposta, "4,5/5")

    def test_media_considera_apenas_a_avaliacao_mais_recente_de_cada_usuario(self):
        usuario = self.novo_usuario()
        self.avaliar(1, usuario=usuario)
        self.avaliar(5, usuario=usuario)
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["resumo"]["media"], 5)
        self.assertEqual(resposta.context["resumo"]["total"], 1)

    def test_media_com_nota_zero_nao_e_tratada_como_sem_avaliacao(self):
        self.avaliar(0)
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["resumo"]["media"], 0)
        self.assertEqual(resposta.context["resumo"]["total"], 1)
        self.assertContains(resposta, "0,0/5")
        self.assertNotContains(resposta, "Sem avaliações")

    def test_sem_avaliacoes(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertIsNone(resposta.context["resumo"]["media"])
        self.assertEqual(resposta.context["resumo"]["total"], 0)
        self.assertContains(resposta, "Sem avaliações")
        self.assertContains(resposta, "Nenhuma avaliação por enquanto")

    # ---- características (tags mais citadas)
    def test_caracteristicas_mais_citadas(self):
        tranquilo = Caracteristica.objects.get(nome="Tranquilo")
        animado = Caracteristica.objects.get(nome="Animado")
        self.avaliar(5, caracteristicas=[tranquilo, animado])
        self.avaliar(4, caracteristicas=[tranquilo])
        resposta = self.client.get(self.url)
        self.assertEqual(
            resposta.context["caracteristicas_destaque"],
            [{"nome": "Tranquilo", "total": 2}, {"nome": "Animado", "total": 1}],
        )

    # ---- carrossel de fotos
    def test_sem_fotos_exibe_imagem_padrao_sem_botoes(self):
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "intoeat/img/sem-foto.svg")
        self.assertNotContains(resposta, BOTAO_ANTERIOR)
        self.assertNotContains(resposta, BOTAO_PROXIMO)

    def test_uma_foto_exibe_a_foto_sem_botoes(self):
        foto = self.adicionar_foto(0, "Salão principal")
        resposta = self.client.get(self.url)
        self.assertContains(resposta, foto.imagem.url)
        self.assertContains(resposta, "Salão principal")
        self.assertNotContains(resposta, "intoeat/img/sem-foto.svg")
        self.assertNotContains(resposta, BOTAO_ANTERIOR)
        self.assertNotContains(resposta, BOTAO_PROXIMO)

    def test_varias_fotos_exibem_botoes_anterior_e_proximo(self):
        for ordem in range(3):
            self.adicionar_foto(ordem)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, BOTAO_ANTERIOR, count=1)
        self.assertContains(resposta, BOTAO_PROXIMO, count=1)
        self.assertContains(resposta, '<figure data-slide', count=3)
        self.assertContains(resposta, "1 / 3")

    def test_fotos_seguem_a_ordem_definida(self):
        terceira = self.adicionar_foto(2)
        primeira = self.adicionar_foto(0)
        segunda = self.adicionar_foto(1)
        resposta = self.client.get(self.url)
        html = resposta.content.decode()
        posicoes = [html.index(foto.imagem.url) for foto in (primeira, segunda, terceira)]
        self.assertEqual(posicoes, sorted(posicoes))
        # Somente a primeira fica visível ao abrir a página.
        self.assertNotIn("hidden", html[html.index("data-slide"):html.index(primeira.imagem.url)])
        self.assertContains(resposta, " hidden>", count=2)

    # ---- lista de avaliações e paginação
    def test_avaliacoes_da_mais_recente_para_a_mais_antiga(self):
        agora = timezone.now()
        for dias, comentario in ((5, "antiga"), (1, "recente"), (3, "meio")):
            avaliacao = self.avaliar(4, comentario=comentario)
            Avaliacao.objects.filter(pk=avaliacao.pk).update(data=agora - timedelta(days=dias))
        resposta = self.client.get(self.url)
        self.assertEqual([a.comentario for a in resposta.context["avaliacoes"]], ["recente", "meio", "antiga"])

    def test_avaliacao_exibe_autor_nota_comentario_e_data(self):
        usuario = self.novo_usuario()
        avaliacao = self.avaliar(4, usuario=usuario, comentario="Ótimo atendimento")
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Pessoa 1")
        self.assertContains(resposta, "Ótimo atendimento")
        self.assertContains(resposta, "Nota 4 de 5")
        self.assertContains(resposta, timezone.localtime(avaliacao.data).strftime("%d/%m/%Y"))

    def test_avaliacoes_sao_paginadas(self):
        total = AVALIACOES_POR_PAGINA * 2 + 2
        agora = timezone.now()
        for i in range(total):
            avaliacao = self.avaliar(3, comentario=f"comentario-{i}")
            Avaliacao.objects.filter(pk=avaliacao.pk).update(data=agora - timedelta(minutes=i))

        pagina1 = self.client.get(self.url)
        self.assertEqual(len(pagina1.context["avaliacoes"]), AVALIACOES_POR_PAGINA)
        self.assertEqual(pagina1.context["avaliacoes"].paginator.num_pages, 3)
        self.assertContains(pagina1, "comentario-0")
        self.assertNotContains(pagina1, f"comentario-{AVALIACOES_POR_PAGINA}<")
        self.assertContains(pagina1, "?pagina=2")
        # O total e a média continuam sobre todas as avaliações, não só a página atual.
        self.assertEqual(pagina1.context["resumo"]["total"], total)

        pagina3 = self.client.get(self.url, {"pagina": 3})
        self.assertEqual(len(pagina3.context["avaliacoes"]), 2)
        self.assertContains(pagina3, f"comentario-{total - 1}")
        self.assertNotContains(pagina3, "?pagina=4")
        self.assertEqual(pagina3.context["resumo"]["total"], total)

    def test_pagina_invalida_nao_quebra(self):
        for _ in range(AVALIACOES_POR_PAGINA + 1):
            self.avaliar(3)
        self.assertEqual(self.client.get(self.url, {"pagina": "abc"}).context["avaliacoes"].number, 1)
        self.assertEqual(self.client.get(self.url, {"pagina": 999}).context["avaliacoes"].number, 2)

    def test_sem_paginacao_quando_cabe_em_uma_pagina(self):
        self.avaliar(3)
        self.assertNotContains(self.client.get(self.url), "?pagina=")

    # ---- botão Avaliar / Editar avaliação / login
    def test_visitante_anonimo_e_levado_ao_login_e_volta_ao_perfil(self):
        resposta = self.client.get(self.url)
        link_login = f"{reverse('usuarios:login')}?next={self.url}"
        self.assertContains(resposta, f'href="{link_login}"')

        usuario = self.novo_usuario()
        depois = self.client.post(link_login, {"username": usuario.email, "password": SENHA})
        self.assertRedirects(depois, self.url, fetch_redirect_response=False)

    def test_usuario_logado_sem_avaliacao_ve_avaliar(self):
        self.client.force_login(self.novo_usuario())
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'id="botao-avaliar"')
        self.assertContains(resposta, f'href="{reverse("avaliacoes:criar", args=[self.restaurante.pk])}"')
        self.assertNotContains(resposta, "Editar avaliação")
        self.assertIsNone(resposta.context["minha_avaliacao"])

    def test_usuario_que_ja_avaliou_ve_editar_avaliacao(self):
        usuario = self.novo_usuario()
        self.avaliar(4, usuario=usuario)
        self.client.force_login(usuario)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Editar avaliação")
        self.assertContains(resposta, 'id="botao-editar-avaliacao"')
        self.assertNotContains(resposta, 'id="botao-avaliar"')
        self.assertContains(resposta, "(você)")

    def test_avaliacao_de_outro_usuario_nao_troca_o_botao(self):
        self.avaliar(4)  # outra pessoa
        self.client.force_login(self.novo_usuario())
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'id="botao-avaliar"')
        self.assertNotContains(resposta, "Editar avaliação")

    def test_avaliacao_em_outro_restaurante_nao_troca_o_botao(self):
        outro = Restaurante.objects.create(
            nome="Outro", endereco="Rua B", tipo_cozinha="Café", status=Restaurante.Status.APROVADO
        )
        usuario = self.novo_usuario()
        registrar_avaliacao(usuario=usuario, restaurante=outro, nota=5)
        self.client.force_login(usuario)
        self.assertContains(self.client.get(self.url), 'id="botao-avaliar"')

    # ---- consultas (prefetch_related)
    def contar_consultas(self):
        with CaptureQueriesContext(connection) as capturadas:
            resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        return len(capturadas)

    def test_numero_de_consultas_nao_cresce_com_fotos_e_avaliacoes(self):
        tags = list(Caracteristica.objects.all()[:3])
        self.adicionar_foto(0)
        self.avaliar(5, caracteristicas=tags)
        base = self.contar_consultas()

        for ordem in range(1, 6):
            self.adicionar_foto(ordem)
        for _ in range(AVALIACOES_POR_PAGINA * 2):
            self.avaliar(4, caracteristicas=tags)
        self.assertEqual(self.contar_consultas(), base)

