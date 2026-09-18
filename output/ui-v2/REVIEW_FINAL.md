# Revisão técnica — UI V2

> Fechamento posterior do agente principal: últimas fontes sincronizadas e compiladas, tablet medido em runtime, três scripts temporários removidos e save no Roblox confirmado em 17/09/2026 às 00:56:06.333. Veja `QA_RESULTS.md` e `qa/SAVE_CONFIRMED.json`. As passagens históricas abaixo não substituem esse registro final.

Revisão estática de 17/09/2026 sobre os dez scripts de UI, comparados aos correspondentes em `before`, e conferência posterior do merge de áudio. A direção vigente usa Inventory fullscreen/violeta, Fredoka com contorno seletivo, raridade forte, botões com volume, Summon com palco/banners e Diário preto/laranja. **A direção já tem evidência em Play; últimos patches e salvamento permanecem em fechamento.** Esta revisão leu [QA_RESULTS.md](QA_RESULTS.md) e distingue essa evidência obtida pelo agente principal da análise estática abaixo. Não afirma persistência do place.

## Compatibilidade encontrada

A comparação das declarações públicas (`T`, `I`, `M`, `N`, `ctx`) e dos nomes literais em `ctx.invoke`, complementada pela leitura dos calls dinâmicos, não encontrou remoção das APIs ou ações de gameplay do baseline. A etapa original de UI não acrescentava remotes; o merge de áudio acrescentou intencionalmente `AtualizarAudioProfile` e `AudioPreferences`, descritos abaixo. Não tratar essa adição coordenada como remoção de compatibilidade.

| Script | Resultado de contrato |
|---|---|
| Theme | APIs públicas, Face.Caption, Disabled, ToneColor, Fill/Tint, assets e fallbacks de preview mantidos. Não exige módulo Tokens. |
| Inventory | Equipamento usa UID. Mantidos EquiparPet/EquiparHat, melhores, desequipar, AlimentarPet/FundirHat e RenomearPet; filtro do servidor preservado. |
| Menus | ComprarPicareta/ComprarMochila/EquiparPicareta, ComprarRobux, Vender, ResgatarMissao/Daily/Codigo mantêm argumentos. Chances vêm de Config e sorte real. |
| Notify | APIs toast/feed/banner/levelUp/reveal/relayout preservadas; bloqueio local, sem recompensa concedida pelo cliente. |
| ExpeditionClient | PedirDados, AtualizarDados, AbrirIgnis/Loja/Gacha, FeedbackMina, OfertaMostrar/Acao, UITravel, ComprarArea e RolarGacha presentes; merge de áudio adiciona AtualizarAudioProfile e hidratação das preferências. |
| AutoMinerar | Golpear:FireServer(Hitbox) e sincronização preservados. Bloqueio de input/target/movimento sob interfaces adicionado. |
| IslandTransition | AreaTransition do Player autoritativo; TravelTransition cobre período visual até fim do fade. |
| MineracaoVisual | AnimarPicareta/FeedbackMina preservados. VFX, tipografia, motion reduzido e limites alterados. |
| AreaBuilder | Diff completo limitado a Theme, tipografia, tintas/strokes; geração/spawn/hitbox intactos. |
| PetsSeguidores | Diff completo limitado às placas. Movimento, offsets e equipamento intactos. |

Os dez scripts de UI não alteram preços, chances ou distribuição de recompensas de gameplay. As mudanças de perfil/servidor da tarefa paralela de áudio têm escopo e evidência próprios; a afirmação anterior de ausência de qualquer extensão de save não se aplica a esse merge posterior.

## Referências externas conferidas

- ReplicatedStorage.Remotes continua raiz. petsInv[UID]/hatsInv[UID] diferem de ID de catálogo; petsEquipados/equipados são listas de UID.
- PlayerGui.ExpeditionUI, Canvas.ModalLayer.Window.Body, HoldModeGui e IslandTransition permanecem identificáveis.
- Hitbox.Vida, Nome, Fundo, Barra, HPTexto e Recompensa permanecem. O servidor Mineracao ainda encontra Vida/Barra/HPTexto; HP e geometria não foram renomeados.
- Workspace.Gachas.Gacha_<tema>.PadGacha, Workspace.Areas.Area<id>.EntryPosition, Barreira.LiberaComArea e grupo Visual permanecem os caminhos usados por UI/gameplay.
- Theme também é requerido por AreaBuilder no servidor. Manter código dependente de LocalPlayer dentro de funções/guardas de cliente; o uso de cores/fontes não cria UI no servidor por si só.

## Corrigido nesta passagem

1. **Resultados recortados:** cols/cw agora vêm da largura real, descontando scrollbar. Cálculo executado em Python em 16 combinações de largura virtual 376/470/900/1440 e 1/2/5/10 resultados: todas cabem, cards com pelo menos 150 unidades nesses casos.
2. **Popup encolhia na rotação:** UIScale adicional substituído por reflow do builder. Closure, texto, cursor, foco e CanvasPosition conservados; onClose não é acionado. Reflow de resultados não repete sons/animação de abertura.
3. **Confirmação com preview em landscape curto:** corpo rolável, preço/descrição sequenciais e CTAs 52 fixos. Acesso Ignis/ofertas receberam a mesma separação.
4. **X pequeno:** tamanho considera escala física para chegar a pelo menos 44 pixels.
5. **P1 HUD compacto resolvido estaticamente:** Currency foi à esquerda, Tracker reduzido à direita e Hotbar foi para cima de Bag. AutoMinerar também trata altura física abaixo de 560 como paisagem compacta, elevando Hold mesmo com mouse. Nenhuma interseção entre Currency, Tracker, TeamLabel, Hotbar, Bag, Navigation e Hold nos quatro casos calculados (900×400 e 472×845 virtuais, mouse/touch, escala .85).
6. **Alvos do HUD touch corrigidos:** largeTargets considera portrait, compact ou Input.TouchEnabled. Slots e venda usam 52 unidades também no tablet; equipe fica acima da mochila. QA_RESULTS registra 44,2×44,2 pixels físicos no telefone 401×776; a correção específica do tablet foi conferida no código e depende da última instalação live.
7. **Overflow de buffs corrigido:** Buffs agora é ScrollingFrame com direção X, scrollbar e CanvasSize igual ao conteúdo. Três/quatro efeitos podem ser alcançados horizontalmente no telefone. Em landscape, a largura também termina 12 unidades antes do Tracker; em 900×400, o viewport vai de x24 a574 e o Tracker começa em 586, encerrando a interseção detectada após a primeira conversão para scroll.
8. **Request de consumo durante rotação corrigido no código:** Inventory confere o parent antigo e chama ctx.refreshPopup() quando ele foi destruído. Estado busy volta a false antes da reconstrução. O ajuste já está integrado, não apenas encaminhado.
9. **Race do banner de chegada corrigida e observada em Play:** Notify observa OpenPage/PopupOpen/AreaTransition/TravelTransition centralmente, oculta o banner ativo, conserva duração restante e invalida timers antigos. Retoma o mesmo objeto sem som repetido e protege onClose contra chamada duplicada. QA_RESULTS registra Visible=false ao abrir inventário, Visible=true ao fechar e expiração até zero banners.
10. **Controles de áudio:** ResetAudio foi ajustado para 52; QA_RESULTS registra cinco controles de volume/reset/toggles com 44,2 pixels no telefone e nenhum texto excedendo os limites.

Chances já usam scroll integral; rename já é rolável; alimentação/fusão mantêm seleção/revisão na closure e layout mínimo rolável. QA_RESULTS confirma popup de chances preservado ao passar do notebook para 401×776 e 749×361, sem acumular sombras. Isso não equivale a executar consumo econômico.

## Achados e limites restantes

- **Observação de baseline inativo, fora do escopo ativo:** OfertaMostrar(oferta,dados) ignora dados; Inventario presume hats e X/Escape não registram OfertaAcao("fechada",oferta). IDs 0 impedem abrir essas ofertas no fluxo atual. Reavaliar o contexto e a telemetria quando a monetização for configurada; não listar como falha ativa do novo visual.
- **P2, validar no toque:** páginas/consumo em landscape curto podem conter scroll externo e interno. Controles ficam alcançáveis, mas o gesto precisa de teste em emulador/dispositivo.
- **Inputs:** restauração usa nomes estáveis de TextBox/ScrollingFrame dentro do popup. Não duplicar nomes sem estender a chave de restauração.
- **Limite econômico de QA:** consumo/fusão, giro com débito, compra e resgates não foram exercitados em perfil descartável. A fixture não foi instalada; acesso direto a PlayerData foi recusado por capacidades, conforme QA_RESULTS. Revisão/cancelamento não comprovam conclusão dessas transações.
- **Compra real não comprovada:** produtos/passes com id 0 continuam Em breve. ok=true de ComprarRobux significa início de prompt, não entrega.
- **Última integração:** existe evidência visual/IsLoaded/ausência de overflow para telas e dimensões listadas em QA_RESULTS. Não generalizar isso a dispositivo físico, controle físico, toda transação econômica ou ao salvamento do place. A instalação final de áudio, confirmação live do piso de escala no tablet e save continuam exigindo evidência própria.

## Evidência local dos popups

ExpeditionClient.lua ao liberar as alterações: 1252 linhas; SHA256 `69A6679C2A7AB393414376FB1FBEB8C6D6187EC7720404F7718268B05BAC28EB`. Mudanças posteriores no shell tornam esse hash histórico, não erro de instalação. Nenhum controle de Studio ou alteração live realizado por esta revisão.

Na leitura posterior do novo Theme/client: T.F.display/title/label/number usam Fredoka; Face.Caption, Disabled/ToneColor e Fill/Tint continuam presentes; o novo fundo fullscreen preserva Window.Body. O agente principal corrigiu também o ownership de state.shadow, destruindo a sombra anterior no reflow. Não foi encontrada remoção real de contrato nesta nova passagem.

## Cálculo do HUD após correção

Fonte: fórmulas de drawHUD e AutoMinerar.posicionarBotao. Coordenadas abaixo são virtuais; Hold usa escala local .96, convertida para o canvas .85. A tabela foi atualizada para slots de 52. `HUD_LAYOUT_REVIEW.json` preserva o cálculo histórico anterior ao aumento dos slots e não foi regravado nesta passagem. Não inclui conteúdo variável dos buffs nem botões CoreGui Roblox.

| Elemento | Compact 900×400: x / y | Portrait 472×845: x / y |
|---|---|---|
| Currency | 24..364 / 14..74 | 16..356 / 14..74 |
| Tracker | 586..876 / 14..114 | 16..436 / 126..226 |
| Buffs (viewport) | 24..574 / 82..118 | 16..456 / 82..118 |
| TeamLabel | 24..154 / 169..186 | 16..146 / 562..579 |
| Hotbar | 24..376 / 190..242 | 16..368 / 583..635 |
| Bag | 261..639 / 248..300 | 16..456 / 641..693 |
| Navigation | 141..759 / 312..386 | 13..459 / 705..831 |
| Hold | 643,8..876,5 / 162,2..214,1 | 215,8..448,5 / 510,7..562,6 |

Compact: Currency/Tracker têm 222 de separação; Hotbar/Bag têm 6 e Bag/Navigation têm 12. Portrait: Hold passa acima da equipe, sem interseção horizontal com TeamLabel; Hotbar/Bag têm 6 e Bag/Navigation têm 12. Nav portrait usa duas linhas de 60, gap de 6 e BottomReserved de 184; Hold usa max(240,184+56), chegando a 44,16 pixels físicos de altura. Salvamento permanece sob confirmação do agente principal.

## Merge de áudio e piso touch conferidos

ExpeditionClient e Menus agora requerem ReplicatedStorage.AudioPreferences. ctx.setAudioPreference aplica localmente a whitelist, agrega alterações rápidas e chama Remotes.AtualizarAudioProfile(patch). O retorno esperado tem ok, audio e persistent; a hidratação usa data.audio/audioPersistent. Respostas antigas não sobrescrevem uma edição mais recente ainda pendente. Erros guardam campos para próxima edição deliberada, sem retry infinito. Estado de perfil confirmado pelo protocolo não é prova de salvamento do place nem de persistência econômica exercitada nesta revisão.

No controlador atual, Input.TouchEnabled impõe piso UIScale de 0,85 também fora de portrait/compact. O HUD usa largeTargets com a mesma inclusão de TouchEnabled, portanto slots/venda não ficam mais em 44/32 unidades no tablet. Controles de 52 passam a 44,2 pixels nesse piso; QA_RESULTS mantém a confirmação live do tablet como pendência da última instalação. O merge também preserva áudio de transação e assinatura única de raridade por conjunto de resultados, com flags na closure para não repetir a assinatura após reflow.

QA_RESULTS registra regressão técnica de áudio da tarefa paralela (31 assets carregados, zero erros, pico de 20/limite de 24 vozes e uma música ativa). Esses dados não representam aprovação auditiva, salvamento do place ou autorização para reverter os arquivos ao estado anterior ao merge.
