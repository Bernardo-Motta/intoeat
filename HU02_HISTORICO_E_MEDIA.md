# HU02 — Histórico de avaliações e média por usuário

## Regra
- Um usuário pode avaliar o mesmo restaurante diversas vezes. Cada registro é preservado.
- `GET /minhas-avaliacoes/` exibe o histórico integral do usuário autenticado.
- A página do restaurante exibe somente a avaliação mais recente de cada usuário para aquele restaurante.
- A média e a contagem usam apenas essas avaliações mais recentes, com uma contribuição por usuário.
- Empates de data são resolvidos pelo maior ID.
- A função `avaliacoes.services.avaliacoes_mais_recentes()` centraliza o filtro e retorna QuerySet, permitindo agregações no banco.
- Não é necessária migração: o esquema anterior já permite múltiplas avaliações por usuário e restaurante.

## Comandos
```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test avaliacoes restaurantes
```

## Atenção
- `restaurantes/views.py` e o template do perfil foram modificados; integrar cuidadosamente se a HU05 estiver sendo desenvolvida em paralelo.
- Outras páginas e serviços que calcularem médias devem utilizar `avaliacoes_mais_recentes()` para preservar a regra.
- A rota `/minhas-avaliacoes/` é o histórico do usuário logado, sem exposição de dados de outros usuários.
