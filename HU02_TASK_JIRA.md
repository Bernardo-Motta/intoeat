# Task Jira — HU02: Avaliar restaurante com nota, comentário opcional e tags

**História de usuário:** Como usuário, quero avaliar um restaurante de 0 a 5 estrelas, adicionar um comentário se desejar e selecionar tags predefinidas que descrevam minha experiência, para ajudar outras pessoas a conhecer o estabelecimento.

**Descrição:** Permitir avaliações múltiplas do mesmo usuário para o mesmo restaurante. Preservar o histórico completo no perfil do usuário, mas mostrar e computar apenas a avaliação mais recente de cada usuário no perfil do restaurante. Integrar com aprovação de restaurantes (HU06). Renomear os campos do modelo Restaurante para `tipo_cozinha` e `criado_por` preservando os dados.

## Subtask 1 — Atualizar o modelo de avaliação
**Descrição:** Adequar o modelo `Avaliacao` à nota obrigatória e ao comentário opcional, preservando o histórico e os relacionamentos com características.

**Critérios de aceitação:**
- Nota inteira entre 0 e 5 é obrigatória, incluindo o valor 0.
- Comentário pode ser vazio sem impedir o salvamento.
- A avaliação continua associada a usuário, restaurante e data.
- O mesmo usuário pode criar múltiplas avaliações do mesmo restaurante, sem apagar as anteriores.

## Subtask 2 — Implementar cadastro e validações no backend
**Descrição:** Adaptar o formulário, a view e o serviço de registro de avaliações às novas regras.

**Critérios de aceitação:**
- Nota ausente ou fora de 0–5 bloqueia o envio.
- Nota válida permite envio mesmo sem comentário e sem tags.
- Comentário informado é armazenado; espaços isolados são tratados como comentário vazio.
- Somente usuário autenticado pode avaliar restaurante aprovado.
- Dados inválidos não geram registros de avaliação.

## Subtask 3 — Disponibilizar as tags predefinidas
**Descrição:** Cadastrar no banco as tags Romântico, Tranquilo, Música ao vivo, Área externa, Adequado para crianças, Pet friendly, Preço acessível, Sofisticado e Animado.

**Critérios de aceitação:**
- As nove tags estão disponíveis depois das migrações, sem execução manual de fixtures.
- Tags preexistentes não são duplicadas ou excluídas pela migração.
- Tags inexistentes não podem ser vinculadas por requisições inválidas.

## Subtask 4 — Permitir seleção múltipla e opcional de tags
**Descrição:** Exibir as tags em um grupo de caixas de seleção no formulário de avaliação e persisti-las via relação muitos-para-muitos.

**Critérios de aceitação:**
- É possível selecionar nenhuma, uma ou várias tags.
- As tags selecionadas são salvas na avaliação correta.
- Não selecionar tags não impede o envio.
- Tags vinculadas a avaliações anteriores permanecem preservadas.

## Subtask 5 — Exibir avaliações, comentários e tags
**Descrição:** Atualizar templates HTML do formulário, perfil do restaurante e histórico de avaliações.

**Critérios de aceitação:**
- O formulário apresenta seleção explícita de nota 0–5, caixa de comentário opcional e checkboxes de tags.
- Comentários existentes e tags selecionadas aparecem nas avaliações correspondentes.
- Avaliações sem comentário ou sem tags são exibidas sem erros.
- A interface HTML permanece funcional; adequação visual final aos wireframes deverá ser revisada pela equipe.

## Subtask 6 — Manter histórico completo e média correta
**Descrição:** Preservar todas as avaliações do usuário e filtrar apenas a mais recente para o perfil do restaurante.

**Critérios de aceitação:**
- O histórico do usuário contém todas as notas, comentários e tags que publicou.
- O perfil do restaurante exibe uma avaliação por usuário, a mais recente.
- A média e a contagem usam somente essas avaliações recentes.
- Em caso de empate de data, a avaliação de maior ID é selecionada.

## Subtask 7 — Renomear campos da HU06 com migrações seguras
**Descrição:** Trocar `Restaurante.categoria` por `Restaurante.tipo_cozinha` e `Restaurante.solicitante` por `Restaurante.criado_por` em modelos, formulários, serviços, views, admin e templates.

**Critérios de aceitação:**
- O cadastro e a listagem utilizam `tipo_cozinha`.
- O usuário vinculado à solicitação é salvo em `criado_por`.
- Os registros antigos mantêm seus valores após as migrações de renomeação.
- A regra de aprovação e de CNPJ da HU06 continua válida.

## Subtask 8 — Criar e executar testes automatizados
**Descrição:** Cobrir a nota 0, nota ausente ou inválida, comentário opcional, tags múltiplas e vazias, tags inválidas, histórico e cálculo de média.

**Critérios de aceitação:**
- Existem testes automatizados para todos os cenários descritos.
- `python manage.py check`, `makemigrations --check --dry-run` e `python manage.py test avaliacoes restaurantes` concluem sem erros no ambiente da equipe.
- A integração com HU01, HU05 e HU06 é conferida antes do merge.

## Subtask 9 — Versionar, revisar e integrar no GitHub
**Descrição:** Enviar as alterações pela branch da HU02 e preparar Pull Request com documentação do escopo e dependências.

**Critérios de aceitação:**
- Alterações estão em `feature/HU02-avaliar-restaurante` com commits descritivos.
- O Pull Request apresenta as migrações, alterações de backend/frontend e testes executados.
- Nenhuma credencial ou `.env` é enviada ao repositório.
- As alterações de `restaurantes/` são revisadas com o responsável pela HU06.
