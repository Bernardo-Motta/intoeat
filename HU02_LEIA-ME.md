# HU02 — Avaliar um restaurante

Implementação em `avaliacoes/`, com models, forms, views, services, templates, URLs, testes e migração inicial.

## Limitação da versão fornecida

O `restaurantes.Restaurante` deste ZIP **não tem campo `status`**. A arquitetura exige que **somente restaurantes aprovados** recebam avaliações. Por segurança, o serviço bloqueia avaliações enquanto HU06 não disponibilizar esse campo. **Não foi alterado `restaurantes/models.py`** para evitar conflitos com o colega responsável.

Quando HU06 for integrada, o serviço reconhecerá `status == "aprovado"` (confirmar o valor efetivo usado no modelo). Para testar a integração real, criar um restaurante aprovado e rodar os testes novamente. O teste unitário do registro usa mock somente para isolar essa dependência.

## Instalação

```bash
# Em uma branch própria do projeto Git; copiar avaliacoes/ e alterações em config/
python manage.py migrate
python manage.py test avaliacoes
python manage.py runserver
```

Rota: `/restaurantes/<id>/avaliar/`. Login obrigatório. O redirecionamento atual vai para uma página de confirmação interna porque a view de perfil HU05 ainda não existe. Após HU05, redirecionar para a página do restaurante, como previsto na arquitetura.

## Escopo

HU02: nota inteira de 0 a 5 e comentário obrigatório. Os relacionamentos M2M para ocasiões e características foram preparados no modelo, mas o formulário dessas opções fica para HU03/HU04. O documento de arquitetura deixa em aberto a regra de múltiplas avaliações do mesmo usuário no mesmo restaurante; nenhuma unicidade foi imposta.
