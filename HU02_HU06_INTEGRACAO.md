# HU02 + integração HU06 — IntoEat

## Incluído
- HU02: formulário de nota (0–5) e comentário, validação em serviço, login obrigatório, gravação no PostgreSQL e exibição no perfil.
- HU06: solicitação com CNPJ validado, cidade, solicitante e status pendente/aprovado/rejeitado; acompanhamento em "Meus restaurantes"; aprovação/rejeição no Django Admin; somente aprovados aparecem e recebem avaliações.
- Perfil mínimo com nota média e avaliações, como ponto de integração com HU05 (percentuais de ocasião/características ficam para HU03–HU05).
- Migração incremental `restaurantes/0002_hu06_aprovacao.py`, sem alterar a migração inicial.
- Testes de serviços, HTTP, validação e regras de aprovação.

## Atenção à integração
- Este pacote parte do ZIP original enviado, **não** das mudanças recentes que colegas possam ter feito. Faça merge por arquivo, não sobrescreva código novo da main.
- A migração acrescenta campos `cnpj` e `solicitante` opcionais para compatibilidade com registros antigos. **Restaurantes antigos ficam pendentes**, devendo ser revisados e aprovados manualmente. Novas solicitações exigem CNPJ válido.
- A ação de rejeição em lote no Admin utiliza um motivo padrão. Para um motivo individual, evoluir o formulário/ação administrativa em outra tarefa.
- A regra de múltiplas avaliações do mesmo usuário permanece aberta no documento de arquitetura: nenhuma restrição de unicidade foi adicionada.
- HU03/HU04 não foram implementadas no formulário; os M2M permanecem disponíveis no modelo.
- A interface HTML é mínima; ajustar aos wireframes quando estiverem disponíveis.

## Execução (Linux)
```bash
source .venv/bin/activate
docker compose up -d
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test restaurantes avaliacoes
python manage.py runserver
```

Rotas: `/restaurantes/`, `/restaurantes/novo/`, `/restaurantes/meus/`, `/restaurantes/<id>/`, `/restaurantes/<id>/avaliar/` e `/admin/`.

## Fluxo manual
1. Faça login como usuário (ou use o Django Admin para criar um usuário).
2. Solicite um restaurante em `/restaurantes/novo/`.
3. Entre em `/admin/` como staff e execute a ação de aprovação.
4. Acesse `/restaurantes/`, abra o perfil e clique em "Avaliar este restaurante".
5. Envie nota e comentário; confira o retorno ao perfil e a média.

> A aplicação original não contém telas de login/cadastro HU01. Para testes locais, pode-se criar usuários no Admin e usar o login do Admin. Integre as telas de autenticação quando HU01 estiver pronta.
