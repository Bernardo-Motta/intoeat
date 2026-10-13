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
        self.restaurante = Restaurante.objects.create(nome="Restaurante Teste", endereco="Rua A", tipo_cozinha="Café")

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

    def test_comentario_opcional(self):
        aprovar_restaurante(self.restaurante)
        sem_comentario = registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=4)
        espacos = registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=3, comentario="   ")
        self.assertEqual(sem_comentario.comentario, "")
        self.assertEqual(espacos.comentario, "")

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


    def test_nota_zero_sem_comentario_e_sem_tags_via_formulario(self):
        aprovar_restaurante(self.restaurante)
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse("avaliacoes:criar", args=[self.restaurante.pk]), {"nota": "0"})
        self.assertRedirects(resposta, reverse("restaurantes:perfil", args=[self.restaurante.pk]))
        avaliacao = Avaliacao.objects.get()
        self.assertEqual(avaliacao.nota, 0)
        self.assertEqual(avaliacao.comentario, "")
        self.assertEqual(avaliacao.caracteristicas.count(), 0)

    def test_nota_obrigatoria_no_formulario(self):
        aprovar_restaurante(self.restaurante)
        self.client.force_login(self.usuario)
        for valor in (None, "", "6", "-1", "2.5"):
            with self.subTest(nota=valor):
                dados = {"comentario": "Opcional"}
                if valor is not None:
                    dados["nota"] = valor
                resposta = self.client.post(reverse("avaliacoes:criar", args=[self.restaurante.pk]), dados)
                self.assertEqual(resposta.status_code, 200)
                self.assertIn("nota", resposta.context["form"].errors)
        self.assertEqual(Avaliacao.objects.count(), 0)

    def test_tags_predefinidas_disponiveis(self):
        from restaurantes.models import Caracteristica
        esperadas = {
            "Romântico", "Tranquilo", "Música ao vivo", "Área externa",
            "Adequado para crianças", "Pet friendly", "Preço acessível",
            "Sofisticado", "Animado",
        }
        self.assertTrue(esperadas.issubset(set(Caracteristica.objects.values_list("nome", flat=True))))

    def test_multiplas_tags_opcionais_via_formulario(self):
        from restaurantes.models import Caracteristica
        aprovar_restaurante(self.restaurante)
        romantico = Caracteristica.objects.get(nome="Romântico")
        tranquilo = Caracteristica.objects.get(nome="Tranquilo")
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse("avaliacoes:criar", args=[self.restaurante.pk]), {
            "nota": "5", "comentario": "Ótimo ambiente",
            "caracteristicas": [str(romantico.pk), str(tranquilo.pk)],
        })
        self.assertRedirects(resposta, reverse("restaurantes:perfil", args=[self.restaurante.pk]))
        avaliacao = Avaliacao.objects.get()
        self.assertCountEqual(avaliacao.caracteristicas.all(), [romantico, tranquilo])
        self.assertContains(self.client.get(reverse("restaurantes:perfil", args=[self.restaurante.pk])), "Romântico")
        self.assertContains(self.client.get(reverse("avaliacoes:minhas")), "Tranquilo")

    def test_tag_inexistente_e_rejeitada(self):
        aprovar_restaurante(self.restaurante)
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse("avaliacoes:criar", args=[self.restaurante.pk]), {
            "nota": "4", "caracteristicas": ["999999"],
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("caracteristicas", resposta.context["form"].errors)
        self.assertEqual(Avaliacao.objects.count(), 0)

    def test_servico_rejeita_tag_nao_cadastrada(self):
        from restaurantes.models import Caracteristica
        aprovar_restaurante(self.restaurante)
        with self.assertRaises(ValidationError):
            registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante,
                                nota=4, caracteristicas=[Caracteristica(pk=999999, nome="Falsa")])
        self.assertEqual(Avaliacao.objects.count(), 0)

class HistoricoAvaliacoesTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user(email="ana@example.com", password="senha123456", nome_completo="Ana")
        self.bruno = Usuario.objects.create_user(email="bruno@example.com", password="senha123456", nome_completo="Bruno")
        self.restaurante = Restaurante.objects.create(nome="Café Histórico", endereco="Rua B", tipo_cozinha="Café")
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
        outro = Restaurante.objects.create(nome="Outro café", endereco="Rua C", tipo_cozinha="Café")
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

    def test_tags_antigas_no_historico_e_so_atuais_no_restaurante(self):
        from restaurantes.models import Caracteristica
        tag_antiga = Caracteristica.objects.get(nome="Romântico")
        tag_nova = Caracteristica.objects.get(nome="Tranquilo")
        registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=2,
                            caracteristicas=[tag_antiga])
        registrar_avaliacao(usuario=self.ana, restaurante=self.restaurante, nota=5,
                            caracteristicas=[tag_nova])
        self.client.force_login(self.ana)
        historico = self.client.get(reverse("avaliacoes:minhas"))
        self.assertContains(historico, "Romântico")
        self.assertContains(historico, "Tranquilo")
        perfil = self.client.get(reverse("restaurantes:perfil", args=[self.restaurante.pk]))
        self.assertContains(perfil, "Tranquilo")
        self.assertNotContains(perfil, "Romântico")
        self.assertEqual(perfil.context["resumo"]["media"], 5)


class FrontendWireframeTests(TestCase):
    def setUp(self):
        from restaurantes.models import Caracteristica, Ocasiao
        self.usuario = Usuario.objects.create_user(email="perfil@example.com", password="senha123456", nome_completo="Pessoa do Perfil")
        self.restaurante = Restaurante.objects.create(nome="Casa do Sabor", endereco="Rua Central", tipo_cozinha="Brasileira", descricao="Sobre a casa")
        aprovar_restaurante(self.restaurante)
        self.romantico = Caracteristica.objects.get(nome="Romântico")
        self.tranquilo = Caracteristica.objects.get(nome="Tranquilo")
        self.ocasiao = Ocasiao.objects.create(nome="Data especial")

    def test_pagina_inicial_redireciona_para_restaurantes(self):
        self.assertRedirects(self.client.get("/"), reverse("restaurantes:lista"))

    def test_formulario_tema_e_opcoes(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("avaliacoes:criar", args=[self.restaurante.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "IntoEat")
        self.assertContains(resposta, "0 estrelas")
        self.assertContains(resposta, "5 estrelas")
        self.assertContains(resposta, "Romântico")
        self.assertContains(resposta, "Música ao vivo")
        self.assertContains(resposta, "intoeat/css/site.css")

    def test_caracteristicas_e_ocasioes_ignorando_avaliacao_antiga(self):
        antiga = registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=1, caracteristicas=[self.romantico])
        antiga.ocasioes.add(self.ocasiao)
        registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=5, caracteristicas=[self.tranquilo])
        resposta = self.client.get(reverse("restaurantes:perfil", args=[self.restaurante.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["resumo"]["media"], 5)
        self.assertEqual([item["nome"] for item in resposta.context["caracteristicas_destaque"]], ["Tranquilo"])
        self.assertEqual(resposta.context["ocasioes_destaque"], [])
        self.assertNotContains(resposta, "Romântico")
        self.assertContains(resposta, "Fotos do Restaurante")

    def test_historico_exibe_perfil_e_as_avaliacoes_anteriores(self):
        registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=1, comentario="Primeira visita")
        registrar_avaliacao(usuario=self.usuario, restaurante=self.restaurante, nota=5, comentario="Segunda visita")
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("avaliacoes:minhas"))
        self.assertContains(resposta, "Pessoa do Perfil")
        self.assertContains(resposta, "Restaurantes Visitados")
        self.assertContains(resposta, "Primeira visita")
        self.assertContains(resposta, "Segunda visita")
