# HU02 + integração HU06 — IntoEat

## Incluído
- HU02: nota de 0 a 5 obrigatória, comentário opcional, escolha de zero ou várias tags (`Caracteristica`).
- Histórico do usuário preserva todas as avaliações; perfil do restaurante usa somente a última de cada usuário para exibição e média.
- HU06: solicitação com CNPJ válido, `tipo_cozinha`, `criado_por` e status pendente/aprovado/rejeitado; status no Django Admin; apenas aprovados recebem avaliações.
- Migrações incrementais preservam campos e dados existentes: `restaurantes/0002`, `0003`, `0004` e `avaliacoes/0002`.
- Testes das principais regras do serviço e das views.

## Pontos de integração
- O frontend é um conjunto de templates HTML básicos e ainda precisa seguir os wireframes.
- A aplicação original não inclui a UI de login/cadastro da HU01; views de avaliação/cadastro exigem login.
- A HU03 (ocasiões) ainda não está integrada ao formulário; tags características (HU04) estão disponíveis.
- HU05 terá de integrar os percentuais coletivos de ocasião e características, usando apenas avaliações mais recentes conforme a regra definida para esta implementação.
- `criado_por` é o usuário responsável pelo cadastro, antigo `solicitante` (dados preservados); `tipo_cozinha` é o antigo campo `categoria`.
- Não sobrescreva trabalho recente de colegas ao integrar a branch.

## Rodar
```bash
source .venv/bin/activate
docker compose up -d
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test restaurantes avaliacoes
python manage.py runserver
```
