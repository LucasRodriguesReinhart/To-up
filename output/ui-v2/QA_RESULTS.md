# Validação da reconstrução UI V2

Estado: direção visual reconstruída, integrada e verificada no jogo. Salvamento no Roblox confirmado pelo Output do Studio às 00:56:06.333 de 17/09/2026; Studio deixado em Edit. Limites de teste abaixo permanecem explícitos.

## Evidências já obtidas nesta execução

- Backup de 62 fontes anteriores em `before/` e em `ServerStorage.BeforeUIV2_20260917_Expedition`, como StringValues inertes com caminho original.
- Os 10 scripts da primeira integração compilaram no Studio. A revisão viva de Theme/Inventory/Menus/Client/AutoMinerar também compilou. O último ciclo recompilou Menus (57.137 bytes), Notify (18.713) e Client (67.622 antes dos últimos ajustes de áudio/tablet).
- Play iniciou com 6 áreas e 420 rochas, sem erro de aplicação no ciclo inspecionado.
- Pela interface real: busca `Madara` retornou apenas `Item_p406`; filtro Secreto exibiu estado vazio; limpar o filtro restaurou os cards.
- Desequipar Muzan removeu `p49` da equipe e trocou o CTA para Equipar. Reequipar e Equipar melhores restauraram a ordem original `[p49,p168,p318]`. Nessa sequência: quatro pets, 54.415.637.572 moedas e mochila 550 permaneceram iguais.
- O botão Ir ao banner viajou à ilha 1, publicou CurrentAreaId=1, encerrou TravelTransition e habilitou Invocar. A transição e validação de proximidade vieram do jogo normal.
- HoldModeGui ficou desabilitada enquanto o inventário/invocação estavam abertos.
- Imagens do palco/ilhas carregaram no runtime (`IsLoaded=true`); uma captura feita imediatamente ao abrir pode preceder o carregamento da imagem.
- A revisão estática corrigiu sobreposições de carteira/tracker e equipe/navegação no modo paisagem compacto. Popups agora refazem o layout preservando seleção, texto, foco e scroll; o shadow anterior é destruído.

## Limites

- As teclas virtuais Escape/ButtonB foram recusadas pelo tool por vínculo permanente ao CoreGui. Isso não comprova comportamento com controle físico.
- O require de PlayerData pelo ambiente de comandos foi recusado por capacidades. A fixture proposta não foi instalada nem executada; nenhuma cópia de fonte ou execução indireta foi usada para contornar o limite.
- Compra, fusão/consumo, giro com débito, resgate e persistência econômica não foram exercitados pela tarefa de UI em um perfil descartável. Cancelar/revisar é distinto de concluir essas operações.
- A tarefa paralela de áudio tem seu próprio escopo/QA. O merge preserva o novo visual; seus resultados técnicos não são presumidos como validação perceptual da UI.
- Dispositivo emulado não equivale a teste em telefone físico. Publicação e salvamento do place precisam de confirmação própria de ferramenta.

## Integração de áudio

As fontes de Menus e ExpeditionClient receberam o merge de `output/audio-v3/merged-ui-final` após conferir os hashes das bases. MineracaoVisual e IslandTransition também preservam os novos marcadores/eventos de áudio; não reinstalar versões anteriores desses arquivos por cima da integração.

## Ciclo visual final

- Inventário em 1365×768: tela inteira violeta, grade à esquerda, retrato central e ficha à direita. 21 imagens carregadas e nenhum texto excedendo o espaço no diagnóstico. Captura real: `screenshots/inventory.png`; dados: `qa/INVENTORY_1366.json`.
- Inventário em 2559×1440: composição preservada, janela 2557×1381, nenhum texto excedendo a largura na revisão automática. Captura inspecionada no Studio.
- Diário em 1365×768: base preta/laranja, quatro colunas, artes e estados grandes. Removidas quatro rotações de raster e adicionado recorte da arte por prêmio; a captura final confirma que o conteúdo não vaza da grade. `screenshots/daily.png`.
- Invocação em 1365×768: rail ilustrado, palco com Kakashi/Madara/Itachi, raridades reais, botões x1/x10 verdes e barras de garantia. Ir ao banner viajou normalmente à ilha 1 e habilitou a ação. Nenhum giro foi comprado. `screenshots/summon.png`.
- Banner de chegada: após abrir inventário, o aviso Vila da Folha ficou `Visible=false`; fechar pela cruz restaurou `Visible=true`; o aviso expirou e a contagem voltou a zero. O mesmo objeto pausa seu relógio e não repete som.
- Telefone emulado 401×776: coleção em três colunas com controles maiores; slots do HUD medidos em 44,2×44,2 px após o ajuste.
- Configurações em 401×776: área de rolagem 342×586, canvas 1788; cinco controles de volume, reset e toggles com 44,2 px de altura; nenhum texto transbordando.
- Popup de chances aberto por clique real no notebook permaneceu aberto ao mudar para 401×776 e 749×361. Conteúdo refez a largura/altura e manteve rolagem, sem acumular sombras.
- Tablet 1022×767 revelou controles de 36,9 px. Corrigido com piso de UIScale 0,85 e alvos maiores no HUD quando TouchEnabled. Nova execução confirmou slots/venda em 44,2 px e nenhum alvo menor que 44 na ficha. O filtro foi abreviado para Estado: todos para caber nessa largura. O viewport dos buffs termina 12 unidades antes do tracker em paisagem.
- Tentativas virtuais de mouse e ButtonA em cards no dispositivo de telefone não comprovaram ativação. O mesmo layout estreito, em 400×776 com mouse habilitado, abriu o detalhe por clique real no card e criou BackToGrid/Detail corretamente. Toque físico continua não validado.
- Console do ciclo inspecionado não mostrou erro do jogo. Erros produzidos por consultas de QA a caminhos já destruídos/recriados e pelo nome de método do simulador foram separados de erros de aplicação.

## Integração técnica de áudio nesta sessão

Harness oficial da tarefa paralela: 31 assets carregados, zero erros, 100 golpes/5 variantes sem repetição imediata, burst de 100 coletas agregado, pico de 20 vozes no limite 24, uma música ativa. Resultado `../audio-v3/qa/FINAL_QA_UI_SESSION.json`. Isso é regressão técnica, não aprovação auditiva. AudioQA foi removido antes do último ciclo de UI.

## Fechamento

- Últimos patches de áudio instalados; smoke final passou: `../audio-v3/qa/FINAL_SMOKE_UI_SESSION.json`. 31 assets, nove grupos, 24 vozes criadas, fila/vozes zeradas após StopEffects. Console do último Play sem erros de aplicação (`qa/FINAL_RUNTIME.json`).
- Dez fontes de UI em Edit compilaram e seus bytes/checksums normalizados coincidiram com as fontes locais. A conferência paralela de áudio confirmou 19 fontes finais.
- AudioQA, AudioPolishQA e AudioFinalSmoke foram removidos e a ausência dos três foi verificada em Edit. Simulação de dispositivo encerrada. A API não aceitou Sensor; não foi declarado que essa orientação foi restaurada.
- Output nativo confirmou: `00:56:06.333 Saved new changes in "Anime Mining Simulator" to Roblox.` Evidência em `qa/SAVE_CONFIRMED.json`. Foi um salvamento do projeto, sem executar publicação pública.
- A cópia adicional em .rbxl não foi gerada: a captura/entrada nativa não disponibilizou o diálogo de Save As. O código e os backups estão preservados localmente em src/ e before/; não confundir esse pacote de fontes com uma cópia completa do place.
