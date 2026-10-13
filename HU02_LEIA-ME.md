# HU02 — Avaliar um restaurante

## Funcionalidade
- Nota obrigatória de 0 a 5 estrelas (inclusive 0).
- Comentário opcional (texto vazio permitido).
- Tags predefinidas (modelo `Caracteristica`) com seleção de zero, uma ou várias tags.
- Apenas usuários autenticados podem avaliar restaurantes aprovados.
- Múltiplas avaliações pelo mesmo usuário são preservadas no histórico; somente a mais recente por usuário aparece no perfil do restaurante e conta na média.

## Integração com HU06
- `Restaurante.tipo_cozinha` substitui `categoria`.
- `Restaurante.criado_por` substitui `solicitante`.
- Migrações incrementais de renomeação preservam o banco anterior.

## Instalação
Veja `HU02_INSTRUCOES_ATUALIZACAO.md` para instruções de testes, migrações e Git.
