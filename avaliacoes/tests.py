from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from usuarios.models import Usuario
from restaurantes.models import Restaurante
from restaurantes.services import aprovar_restaurante
from .models import Avaliacao
from .services import registrar_avaliacao


class AvaliacaoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(email="teste@example.com", password="senha123456", nome_completo="Teste")
        self.restaurante = Restaurante.objects.create(nome="Restaurante Teste", endereco="Rua A", categoria="Café")

    def test_nao_avalia_pendente(self):
        with self.assertRaises(ValidationError):
            registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=5, comentario="Bom")
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("avaliacoes:criar", args=[self.restaurante.pk])).status_code, 404)

    def test_nao_avalia_rejeitado(self):
        self.restaurante.status = Restaurante.Status.REJEITADO
        self.restaurante.save()
        with self.assertRaises(ValidationError):
            registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=5, comentario="Bom")

    def test_nota_invalida(self):
        aprovar_restaurante(self.restaurante)
        for nota in (-1, 6, 2.5, True):
            with self.subTest(nota=nota), self.assertRaises(ValidationError):
                registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=nota, comentario="Bom")

    def test_comentario_obrigatorio(self):
        aprovar_restaurante(self.restaurante)
        with self.assertRaises(ValidationError):
            registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=4, comentario="   ")

    def test_registro_valido(self):
        aprovar_restaurante(self.restaurante)
        avaliacao = registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=5, comentario=" Muito bom ")
        self.assertEqual(avaliacao.comentario, "Muito bom")
        self.assertEqual(avaliacao.usuario, self.usuario)

    def test_login_obrigatorio(self):
        aprovar_restaurante(self.restaurante)
        self.assertEqual(self.client.get(reverse("avaliacoes:criar", args=[self.restaurante.pk])).status_code, 302)

    def test_post_avaliacao_e_perfil(self):
        aprovar_restaurante(self.restaurante)
        self.client.force_login(self.usuario)
        response = self.client.post(reverse("avaliacoes:criar", args=[self.restaurante.pk]), {"nota": "5", "comentario": "Excelente"})
        self.assertRedirects(response, reverse("restaurantes:perfil", args=[self.restaurante.pk]))
        self.assertEqual(Avaliacao.objects.count(), 1)
        self.assertContains(self.client.get(reverse("restaurantes:perfil", args=[self.restaurante.pk])), "Excelente")


class HistoricoAvaliacoesTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user(email="ana@example.com", password="senha123456", nome_completo="Ana")
        self.bruno = Usuario.objects.create_user(email="bruno@example.com", password="senha123456", nome_completo="Bruno")
        self.restaurante = Restaurante.objects.create(nome="Café Histórico", endereco="Rua B", categoria="Café")
        aprovar_restaurante(self.restaurante)

    def test_multiplas_avaliacoes_e_media_mais_recente(self):
        registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=2, comentario="Antiga Ana")
        registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=5, comentario="Nova Ana")
        registrar_avaliacao(usuario=self.bruno, restaurante=self.restaurante, nota=4, comentario="Bruno")
        self.assertEqual(Avaliacao.objects.count(), 3)
        resposta = self.client.get(reverse("restaurantes:perfil", args=[self.restaurante.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["resumo"]["media"], 4.5)
        self.assertEqual(resposta.context["resumo"]["total"], 2)
        self.assertContains(resposta, "Nova Ana")
        self.assertContains(resposta, "Bruno")
        self.assertNotContains(resposta, "Antiga Ana")

    def test_perfil_usuario_mostra_historico_completo(self):
        registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=2, comentario="Antiga Ana")
        registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=5, comentario="Nova Ana")
        registrar_avaliacao(usuario=self.bruno, restaurante=self.restaurante, nota=4, comentario="Bruno")
        self.client.force_login(self.ana)
        resposta = self.client.get(reverse("avaliacoes:minhas"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.context["avaliacoes"]), 2)
        self.assertContains(resposta, "Antiga Ana")
        self.assertContains(resposta, "Nova Ana")
        self.assertNotContains(resposta, "Bruno")

    def test_historico_exige_login(self):
        resposta = self.client.get(reverse("avaliacoes:minhas"))
        self.assertEqual(resposta.status_code, 302)

    def test_mais_recente_e_por_restaurante(self):
        outro = Restaurante.objects.create(nome="Outro café", endereco="Rua C", categoria="Café")
        aprovar_restaurante(outro)
        registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=2, comentario="Primeiro café")
        registrar_avaliacao(usuario=self.ana, restaurante=outro, nota=5, comentario="Segundo café")
        resposta = self.client.get(reverse("restaurantes:perfil", args=[self.restaurante.pk]))
        self.assertEqual(resposta.context["resumo"]["media"], 2)
        self.assertEqual(resposta.context["resumo"]["total"], 1)

    def test_empate_data_desempata_por_id(self):
        from django.utils import timezone
        from avaliacoes.services import avaliacoes_mais_recentes
        primeira = registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=1, comentario="Primeira")
        segunda = registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=5, comentario="Segunda")
        instante = timezone.now()
        Avaliacao.objects.filter(pk__in=[primeira.pk, segunda.pk]).update(data=instante)
        self.assertEqual(list(avaliacoes_mais_recentes(self.restaurante).values_list("pk", flat=True)), [segunda.pk])
