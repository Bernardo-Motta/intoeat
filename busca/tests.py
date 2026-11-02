from django.test import TestCase
from django.urls import reverse

from avaliacoes.models import Avaliacao
from avaliacoes.services import registrar_avaliacao
from restaurantes.models import Caracteristica, Ocasiao, Restaurante
from restaurantes.services import aprovar_restaurante
from usuarios.models import Usuario

from .services import buscar_restaurantes


class BuscaSprintIITests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user(email="buscaana@exemplo.com", password="senhaforte123", nome_completo="Ana")
        self.bia = Usuario.objects.create_user(email="buscabia@exemplo.com", password="senhaforte123", nome_completo="Bia")
        self.carla = Usuario.objects.create_user(email="buscacarla@exemplo.com", password="senhaforte123", nome_completo="Carla")
        self.encontro, _ = Ocasiao.objects.get_or_create(nome="Encontro")
        self.familia, _ = Ocasiao.objects.get_or_create(nome="Família")
        self.romantico, _ = Caracteristica.objects.get_or_create(nome="Romântico")
        self.tranquilo, _ = Caracteristica.objects.get_or_create(nome="Tranquilo")
        self.cantina = self.restaurante("Cantina da Praça", "Italiana", aprovado=True)
        self.churrascaria = self.restaurante("Churrasco Bom", "Brasileira", aprovado=True)
        self.pendente = self.restaurante("Pendente", "Italiana", aprovado=False)

    def restaurante(self, nome, tipo, aprovado):
        r = Restaurante.objects.create(nome=nome, endereco="Rua A, 10", tipo_cozinha=tipo)
        if aprovado:
            aprovar_restaurante(r)
        return r

    def avaliar(self, usuario, restaurante, nota, ocasioes=None, tags=None):
        return registrar_avaliacao(
            usuario=usuario, restaurante=restaurante, nota=nota, comentario="Teste",
            ocasioes=ocasioes or [], caracteristicas=tags or [],
        )

    def test_hu07_filtra_por_nome_ou_tipo_de_cozinha(self):
        self.assertEqual([r.restaurante.pk for r in buscar_restaurantes(texto="cantina")], [self.cantina.pk])
        self.assertEqual([r.restaurante.pk for r in buscar_restaurantes(texto="italiana")], [self.cantina.pk])
        self.assertEqual([r.restaurante.pk for r in buscar_restaurantes(texto="brasileira")], [self.churrascaria.pk])

    def test_hu07_nao_mostra_restaurantes_pendentes(self):
        resultados = buscar_restaurantes()
        self.assertNotIn(self.pendente.pk, [r.restaurante.pk for r in resultados])
        self.assertEqual(len(resultados), 2)

    def test_hu07_prioriza_compatibilidade_e_nao_apenas_nota(self):
        self.avaliar(self.ana, self.cantina, 3, [self.encontro], [self.romantico])
        self.avaliar(self.bia, self.cantina, 3, [self.encontro], [self.romantico])
        self.avaliar(self.ana, self.churrascaria, 5, [self.familia], [self.tranquilo])
        self.avaliar(self.bia, self.churrascaria, 5, [self.familia], [self.tranquilo])
        resultados = buscar_restaurantes(ocasioes=[self.encontro], caracteristicas=[self.romantico])
        self.assertEqual(resultados[0].restaurante, self.cantina)
        self.assertLess(resultados[0].nota_media, resultados[1].nota_media)
        self.assertGreater(resultados[0].compatibilidade, resultados[1].compatibilidade)

    def test_suavizacao_evitar_preferencia_por_um_unico_voto(self):
        self.avaliar(self.ana, self.cantina, 5, [self.encontro])
        self.avaliar(self.ana, self.churrascaria, 5, [self.encontro])
        self.avaliar(self.bia, self.churrascaria, 5, [self.encontro])
        resultados = buscar_restaurantes(ocasioes=[self.encontro])
        self.assertEqual(resultados[0].restaurante, self.churrascaria)

    def test_apenas_ultima_avaliacao_conta_nos_percentuais(self):
        self.avaliar(self.ana, self.cantina, 5, [self.encontro], [self.romantico])
        self.avaliar(self.ana, self.cantina, 2, [self.familia], [self.tranquilo])
        self.avaliar(self.bia, self.cantina, 4, [self.encontro], [self.romantico])
        resultado = next(r for r in buscar_restaurantes(ocasioes=[self.encontro], caracteristicas=[self.romantico]) if r.restaurante == self.cantina)
        self.assertEqual(Avaliacao.objects.filter(restaurante=self.cantina).count(), 3)
        self.assertEqual(resultado.total_avaliacoes, 2)
        self.assertEqual(resultado.nota_media, 3)
        self.assertEqual(resultado.percentual_ocasioes, 50)
        self.assertEqual(resultado.percentual_caracteristicas, 50)

    def test_avaliar_com_ocasioes_opcionais_e_validacao(self):
        self.client.force_login(self.ana)
        url = reverse("avaliacoes:criar", args=[self.cantina.pk])
        resposta = self.client.post(url, {"nota": "4", "ocasioes": [str(self.encontro.pk), str(self.familia.pk)]})
        self.assertRedirects(resposta, reverse("restaurantes:perfil", args=[self.cantina.pk]))
        self.assertEqual(Avaliacao.objects.get().ocasioes.count(), 2)
        resposta = self.client.post(url, {"nota": "2", "ocasioes": ["999999"]})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("ocasioes", resposta.context["form"].errors)
        self.assertEqual(Avaliacao.objects.count(), 1)

    def test_hu07_pagina_publica_e_campos_validos(self):
        url = reverse("busca:filtros")
        self.assertEqual(self.client.get(url).status_code, 200)
        resposta = self.client.get(url, {"q": "cantina", "ocasioes": [self.encontro.pk], "caracteristicas": [self.romantico.pk]})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Cantina da Praça")
        self.assertNotContains(resposta, "Churrasco Bom")
        resposta = self.client.get(url, {"ocasioes": ["999999"]})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("ocasioes", resposta.context["form"].errors)

    def test_hu08_intencoes_publicas_e_ordenacao(self):
        self.avaliar(self.ana, self.cantina, 4, [self.encontro])
        self.assertEqual(self.client.get(reverse("busca:intencoes")).status_code, 200)
        resposta = self.client.get(reverse("busca:resultado_intencao", args=["encontro"]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["resultados"].object_list[0].restaurante, self.cantina)
        self.assertEqual(self.client.get(reverse("busca:resultado_intencao", args=["inexistente"])).status_code, 404)
        self.assertEqual(self.client.get(reverse("busca:resultado_intencao", args=["descobrir"])).status_code, 200)

    def test_hu15_ocasiões_com_paginas_e_perfil(self):
        self.avaliar(self.ana, self.cantina, 4, [self.encontro])
        self.assertContains(self.client.get(reverse("busca:ocasioes")), "Encontro")
        resposta = self.client.get(reverse("busca:resultado_ocasiao", args=[self.encontro.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Cantina da Praça")
        self.assertEqual(self.client.get(reverse("busca:resultado_ocasiao", args=[999999])).status_code, 404)

    def test_sem_avaliacoes_nunca_supera_resultado_com_avaliacoes_positivas(self):
        self.avaliar(self.ana, self.cantina, 4, [self.encontro])
        resultados = buscar_restaurantes(ocasioes=[self.encontro])
        self.assertEqual(resultados[0].restaurante, self.cantina)
        self.assertEqual(resultados[1].compatibilidade, 0)
