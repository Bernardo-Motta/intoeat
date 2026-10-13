# HU02 — Histórico de avaliações e média por usuário

- Um usuário pode avaliar o mesmo restaurante várias vezes; cada avaliação continua armazenada.
- `GET /minhas-avaliacoes/`: histórico completo do usuário autenticado, com notas, comentários quando existirem e tags.
- O perfil do restaurante exibe apenas a avaliação mais recente de cada usuário, com as tags daquela avaliação.
- Média e contagem consideram somente essas avaliações mais recentes; desempate por maior ID.
- `avaliacoes.services.avaliacoes_mais_recentes()` centraliza a regra.
- Nota de 0 a 5 é obrigatória; comentário e tags são opcionais. Várias tags podem ser selecionadas.
- Migração de comentário opcional: `avaliacoes/0002_comentario_opcional.py`.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test avaliacoes restaurantes
```

**Integração:** a implementação da HU05 e da busca deve reutilizar a função de avaliações mais recentes para não considerar múltiplas notas de uma mesma pessoa.
