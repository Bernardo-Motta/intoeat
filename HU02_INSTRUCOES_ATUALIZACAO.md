# IntoEat — atualização HU02: nota, comentário opcional e tags

## O que mudou
- `Avaliacao.comentario` passa a aceitar texto vazio (`blank=True`). A nota inteira de 0 a 5 continua obrigatória.
- O formulário apresenta caixas de seleção para as tags de `Caracteristica` (0, 1 ou várias).
- A camada de serviços valida a nota, comentário opcional e tags existentes antes de salvar.
- A migração de dados cria as nove tags definidas na história, sem duplicar nomes já existentes.
- Histórico individual mantém todas as avaliações e tags. Perfil do restaurante exibe apenas a última avaliação de cada usuário (nota, comentário opcional e tags) e calcula a média só com essas últimas avaliações.
- `Restaurante.categoria` é renomeado para `Restaurante.tipo_cozinha` e `Restaurante.solicitante` para `Restaurante.criado_por`.
- As migrations de renomeação **preservam dados** existentes (não apagar o banco).

## Aplicar no repositório Git existente

Use o ZIP como referência e copie os arquivos alterados para sua branch `feature/HU02-avaliar-restaurante`.
Não substitua automaticamente alterações recentes dos colegas. Confira `git diff`.

```bash
git switch feature/HU02-avaliar-restaurante
git status
# Após copiar os arquivos atualizados do ZIP para o repositório:
source .venv/bin/activate
docker compose up -d
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test avaliacoes restaurantes
python manage.py runserver
```

> Antes de migrar, faça backup do PostgreSQL se houver dados importantes. Não edite as migrações 0001 e 0002 previamente aplicadas.

## Migrações incluídas
- `avaliacoes/0002_comentario_opcional.py`: libera comentário vazio.
- `restaurantes/0003_renomear_campos.py`: renomeia categoria → tipo_cozinha, solicitante → criado_por sem perder dados.
- `restaurantes/0004_tags_predefinidas.py`: cadastra as tags padrão de forma idempotente.

O antigo fixture `dados_iniciais.json` agora contém somente ocasiões. As características são cadastradas pela migração de dados, evitando colisões de chaves primárias entre o fixture e a migração. Características antigas já presentes no banco são preservadas.

## Git (após os testes)
```bash
git status
git diff --check
git add avaliacoes/ restaurantes/ HU02_INSTRUCOES_ATUALIZACAO.md HU02_TASK_JIRA.md HU02_HISTORICO_E_MEDIA.md HU02_HU06_INTEGRACAO.md HU02_LEIA-ME.md
git diff --cached --stat
git commit -m "HU02: comentario opcional e multiplas tags nas avaliacoes"
git push -u origin feature/HU02-avaliar-restaurante
```

## Limitações de integração
- Frontend em templates Django HTML básicos; adequação aos wireframes ainda pendente.
- O projeto continua sem tela própria de login (HU01) e sem homepage na rota `/`.
- Consultas futuras do perfil coletivo e busca precisam usar `avaliacoes_mais_recentes()` para serem coerentes com a regra do histórico.
- Como HU06 pode estar sendo implementada por outra pessoa, revise cuidadosamente as renomeações em `restaurantes/` antes do merge.
