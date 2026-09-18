# Auditoria de mineração e interfaces secundárias

Escopo: cópia dos scripts vivos em `before/`, obtida antes de qualquer alteração. Revisão de contratos, não substituição da lógica de mineração.

## Inventário e dependências

| Interface | Origem / abertura | Dados e contratos preservados | Diagnóstico |
|---|---|---|---|
| HoldModeGui.HoldMode | AutoMinerar; sempre disponível no gameplay, tecla T / mouse / touch / RT | Golpear, HoldMode, MiningTargetSelected, CurrentAreaId, MiningGeometry.destination/canReach; cooldown publicado IntervaloGolpe | Controles atendem todos os inputs. Texto em inglês, botão recriado por qualquer troca de input, escala independente e ações continuam sob modais. |
| Vida / Nome / Fundo / Interno / Barra / HPTexto / Recompensa | AreaBuilder.etiqueta; chefe sempre, minério ao receber golpe | Mineracao.atualizarBarra encontra Barra e HPTexto recursivamente. HP/HPMax são autoritativos do servidor | Preservar nomes. Fredoka e strokes grossos conflitam com nova direção. Cor de HP é reescrita por Mineracao; não basta pintar uma vez. |
| Dano flutuante / Rastro / Flash | MineracaoVisual; FeedbackMina(golpe) / AnimarPicareta | Não modifica dano. Previsão usa startedAt + MiningAnimations.CONTATO; servidor elimina duplicação | Dano limitado a 9 números, VFX a 90 studs e sons a 70. Base boa. Falta respeitar efeitos reduzidos, limpeza de previsão ao sair jogador, limite de explosões e progressão de quebra com fragmentos. |
| IslandTransition | player.AreaTransition publicado pelo servidor; fecha quando nil | Config.areaPorId, Temas, Theme.areaImage, Assets.lobby/logo | Compartilha Theme, cancela tweens e tem revisão antirace. Track não recorta fill, conteúdo muito espalhado, animação decorativa longa, input não bloqueado. |
| NomePet / Nome / Raridade | PetsSeguidores cria na equipagem; altera nome por PetsApelidos | PetsEquipados, PetsApelidos, PreviewModelos.Pets; posição 6 studs atrás + caminhada | Movimentação e equipagem estão corretas e devem ficar. Nome usa Fredoka e raridades duplicadas. RenderStepped faz raycast por pet sem culling; melhoria visual independente da lógica do seguidor. |
| Notificações e loot | Notify.init / push / feed / banner / reveal; ExpeditionClient recebe FeedbackMina e dados | Métodos públicos atuais; fila e callbacks onClose | Toasts 3+4 e feed 5 já limitados; agrupamento já existe. Reveal ilimitado, abre mesmo com modal e não publica bloqueio de mineração. Grandes efeitos em qualquer raridade e viewport fixo 360x486. |
| Placas de área / portal / retorno | AreaBuilder linhas 213, 406, 480 | ProximityPrompts / textos informativos; portais continuam controlados pelos serviços de viagem | Tipografia legada; preservar conteúdo e interação. |
| SurfaceGuis de cenografia | CapsuleIsland, KonohaIsland, IslandArt, IslandWorld, ThemeIslands, RemainingIslands, FolhaEnvironment | Sinais, placas e motivos diegéticos, sem remotes próprios | Não são menus legados; manter identidade do cenário. Normalizar apenas placas funcionais se fonte/contraste falhar, evitando repintar símbolos de anime. |

## O que já funciona e será mantido

- MiningSwing, MiningAnimations, LocomocaoBigAxe, Tool.Grip e toda a postura, sincronização do contato e servidor validador.
- Um núcleo sonoro `SomJogo` com grupos, variações, camadas, cooldown de voz, volume espacial e combo de coleta. Não há justificativa para substituí-lo.
- Reação da rocha, trilha curta, som de contato previsto, dano real do servidor, rastro de vida e explosão por raridade. Aprimorar acabamento e limites.
- Seguidores atrás do jogador com animação de caminhada; conexões por jogador já são desconectadas em PlayerRemoving.
- Vida e recompensa de minérios continuam sendo criadas no servidor, com nomes consumidos por Mineracao e MineracaoVisual.

## Alterações necessárias e realizadas no pacote src

1. AutoMinerar: suspender aquisição de alvo e pedidos de golpe quando OpenPage, PopupOpen, RevealOpen, AreaTransition, TravelTransition ou foco de TextBox. Cancelar MoveTo e fila ao bloquear; preservar preferência HoldMode, sem retomar o alvo antigo automaticamente. Raycast de aquisição a 20 Hz. Botão único que muda texto, tamanho e visibilidade sem ser recriado a cada input; rótulo português.
2. IslandTransition: painel compacto, destino prioritário, loading indeterminado recortado, sem falso percentual. Estado TravelTransition impede input durante entrada/saída. Cancelamento por revisão e fallback seguro para tema ausente. ReducedMotion mostra transição simples.
3. MineracaoVisual: tipografia numérica Theme; escalas/contornos contidos, câmera apenas com motion habilitado, partículas opcionais, quebra com fragmentos breves por raridade, limites de efeitos, previsão limpa quando jogadores saem. Contratos de golpe e animação intactos.
4. Notify: superfícies sólidas, largura adaptativa e número máximo de linhas, filas limitadas, deduplicação, reveal reservado a momentos de maior valor; menores viram confirmação breve. Reveal aguarda modal/viagem, publica RevealOpen e é responsivo. Som e motion usam Theme. Callbacks executados uma vez.

## Contratos extras

- `PlayerGui.ExpeditionUI.OpenPage`: string, vazia quando HUD livre.
- `PlayerGui.ExpeditionUI.PopupOpen`: bool enquanto popup da shell está aberto.
- `player.TravelTransition`: bool mantido por IslandTransition enquanto tela de viagem estiver visível.
- `player.RevealOpen`: bool mantido por Notify enquanto reveal estiver visível.
- `player.ReducedMotion`: bool; `Theme.motionEnabled()` também considera ExpeditionEffectsEnabled.
- Theme conserva todas as APIs anteriores e acrescenta `F.number` / `motionEnabled()`.

## Validação de integração necessária

Testar seleção e fila de minérios, um contato por swing, abrir menu enquanto caminha/minera, fechar menu e apontar outro minério, foco em busca, popup, reveal, viagem repetida, resize durante reveal/viagem, RT e touch. Conferir sons comuns/raros e configurações, HP/dano/loot/contador, mochila cheia e chefe. Não afirmar persistência ou equipagem só a partir de atributos sintéticos.

Verificação realizada: os quatro arquivos src foram compilados por `loadstring` no Studio em modo Edit, sem instalação nem execução, todos com `compiled=true`. A checagem confirma sintaxe; não substitui validação de runtime e visual em Play.

## Pendências de apresentação de mundo fora destes quatro arquivos

Root informou integração de `Tokens.lua` puro para fonte/paleta de AreaBuilder e NomePet, preservando nomes da Vida. Conferir placas funcionais no inventário global. Cenografia com SurfaceGui possui justificativa funcional/visual; não é leftover de menu.
