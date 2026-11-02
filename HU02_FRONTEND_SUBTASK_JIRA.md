# Subtask — Implementar frontend das avaliações e do perfil do restaurante

**Descrição:** Desenvolver e estilizar as interfaces da HU02 em templates Django, seguindo os wireframes do IntoEat (tema marrom escuro, contornos laranja, cabeçalho, cartões e rodapé). Integrar formulário, histórico individual e perfil do restaurante às views e às regras existentes.

**Atividades:**

- Criar um template-base compartilhado com cabeçalho, links de navegação e rodapé do IntoEat.
- Criar o CSS do tema, seguindo cores, bordas, tipografia e disposição dos elementos dos wireframes.
- Implementar o formulário de avaliação com nota obrigatória de 0 a 5 estrelas, caixa de comentário opcional e seleção de nenhuma, uma ou várias tags.
- Adaptar a página de histórico ao layout de perfil do usuário, exibindo informações disponíveis, guias de navegação e todas as avaliações (inclusive antigas).
- Adaptar a página do restaurante com espaço reservado para carrossel, nome, tipo de cozinha, endereço, descrição, nota média, três características e três ocasiões mais frequentes, além de cartões de avaliações.
- Exibir na página do restaurante apenas a avaliação mais recente de cada usuário, usando essa mesma seleção para a nota média e os destaques.
- Permitir a leitura de comentários longos e exibir tags nas avaliações.
- Implementar layout responsivo, estados vazios, tratamento visual de erros e acessibilidade básica.
- Integrar os templates às rotas do Django e validar a renderização e o funcionamento dos formulários.

**Critérios de aceitação:**

- O formulário funciona com nota obrigatória, comentário opcional e tags opcionais/múltiplas.
- O histórico apresenta todas as avaliações do usuário logado, incluindo as versões antigas.
- O perfil do restaurante mostra apenas a avaliação mais recente de cada usuário e a média correspondente.
- O cabeçalho, cartões, disposição geral, paleta e rodapé seguem os wireframes fornecidos.
- As informações exibidas vêm dos modelos existentes; campos ainda não implementados não exibem dados fictícios.
- As telas são utilizáveis em desktop e dispositivos móveis.
- As alterações não modificam as regras de negócio existentes e passam pelos testes automatizados da HU02.

**Dependências e observações:** O modelo atual ainda não tem fotos de restaurante, foto/biografia/interesses de usuário nem URLs próprias de autenticação. As respectivas áreas visuais usam placeholders explícitos até serem integradas às histórias responsáveis. O bloco de fotos não constitui um carrossel funcional enquanto não existir um cadastro de imagens.
