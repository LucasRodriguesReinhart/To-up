# UI V2 — auditoria de dependências do snapshot LIVE

Fonte: `output/ui-v2/before`, exportação confirmada do Studio pelo agente principal. Esta análise usa o código atual, não as versões antigas em `output/revision`. Nenhum script de jogo foi modificado durante esta auditoria. A inspeção de instâncias edit/runtime e a avaliação por screenshot são complementares e pertencem ao relatório do agente principal.

## Conclusão e prioridade

A arquitetura atual já separa apresentação, dados e servidor de modo útil: `ExpeditionClient` gerencia shell/estado; `ExpeditionUI.Theme` contém componentes; `Menus`, `Inventory` e `Notify` renderizam conteúdo. Preservar a fronteira de remotes e o snapshot evita uma migração de save desnecessária. A reconstrução deve concentrar-se em estrutura, hierarquia e gestão coerente de interação.

1. **P0:** impedir a escolha de novos minérios por trás de janela, popup ou transição; hoje `AutoMinerar` continua o raycast do Hold no Heartbeat e não consulta qualquer estado modal.
2. **P0:** proteger favoritos/bloqueios locais no fluxo de alimentação/fusão. Hoje favoritos só mudam ordenação e podem ser consumidos por seleção manual ou atalho. O servidor só protege equipados. Explicar claramente o alcance “nesta sessão”.
3. **P1:** conter o inventário em janela desktop e reconstruir em grid + detalhe, com busca e filtros no conteúdo. Hoje há takeover fullscreen, 3 colunas e muito tratamento decorativo.
4. **P1:** tornar pequenos estados/páginas responsivos. Settings estreito põe Codes em y=610 num Frame sem scroll; popup de consumo coloca até 2 atalhos + Limpar + Confirmar numa única linha fixa e pode sobrepor em telas estreitas.
5. **P1:** corrigir arbitragem de janelas/rewards/ofertas e cancelar invocação de modo explícito ao navegar. `ctx.open` limpa cancelSummon mesmo durante sequência; `ctx.close` cancela a sequência, mas resultados ainda podem reabrir popup depois de fechar. `resize` fecha popups e perde seleção.
6. **P1:** reduzir reconstruções completas em cada snapshot, letras muito pequenas, cores concorrentes e animação ociosa. Preservar teardown existente em tweens e previews.
7. **P2:** melhorar foco/gamepad, tooltips dentro da tela, estados busy por botão, legenda não dependente de cor, feedback preciso de recompensa e disponibilidade de produtos.

## Inventário de interfaces

Todas as páginas centrais são geradas em runtime em `PlayerGui.ExpeditionUI.Canvas.ModalLayer.Window.Body`, com `DisplayOrder=25`. Abrem por navegação/atalhos/remotes e fecham por X, Escape ou alternância da página. O backdrop atual não tem conexão de fechamento identificada. Páginas aliased: Items → Inventory/hat, Play → Areas.

| Interface | Origem / abertura | Dados, operações e fechamento | Diagnóstico / preservar |
|---|---|---|---|
| HUD carteira/poder | ExpeditionClient.drawHUD/updateHUD | moeda, dano; contagem animada + delta; sempre ativo fora de páginas fullscreen/compactas | Excesso de pilares concorrentes; carteira atualmente na base, target coinBurst depende da posição dela |
| HUD mochila/vender | ExpeditionClient | carregado/capacidade, 85% warning, cheio=error; abre Forge | Bom feedback de limite e atalho contextual; barra + botão precisam caber em mobile |
| HUD equipamentos/6 pets | ExpeditionClient.Hotbar/rail Pickaxe | petsInv, petsEquipados, picareta; clique seleciona UID no Inventory | Número de slots desenhado fixo=6; preview correto via Config.PetArte; preservar UID |
| HUD missão/ilha | ExpeditionClient.Tracker | CurrentAreaId, missoes; primeira pronta tem prioridade; abre Quests | Área+quest+barra competem num componente; posição reage ao tamanho porém texto útil encolhe |
| HUD buffs | ExpeditionClient.renderBuffs | boosts, friendBoost, multMoedas, passes; atualiza a cada 1s | Contadores partem do snapshot/dataClock; preservar duração real |
| HUD badges | ExpeditionClient | missões prontas, daily, compra acessível, área acessível | Bons indicadores acionáveis; controlar número de acentos |
| Loja Picaretas | Menus.equipmentStore; nav Loja/Picareta | Picaretas, picaretasCompradas, picareta, moeda, dano; comprar/equipar | Possui comparação e confirmação de saldo; preservar propriedade/equipamento diferentes |
| Loja Mochilas | Menus.equipmentStore; AbrirLoja | Mochilas, mochilaTier, capacidade/moeda; compra tier | Upgrade substitui mochila; preservar pré-requisitos do servidor |
| Loja Passes/Boosts | Menus.passesStore/productCard | MonetizacaoConfig, passes, compras; ComprarRobux | TODOS IDs atuais=0; Em breve obrigatório. Preço exibido é planejado, backend usa Marketplace |
| Inventário Unidades | Inventory; H/B/nav/hotbar | petsInv por UID, petsEquipados, slotsPets, capacidadePets | Busca normaliza acentos; favoritos locais; grid + stage + detalhe; equipar/melhores/limpar |
| Inventário Hats | Inventory; J/nav Itens | hatsInv por UID, equipados, slots, capacidadeHats | Mesmo sistema, fusão em vez de alimentação; hats usam thumbnail asset |
| Busca/raridade/coleção | ExpeditionClient header + Inventory.collect | ctx.search/rarity/ownedOnly/favorites | Filtros e busca espalhados; ordem fixa equipado→favorito→raridade; falta sort controlado e filtro equipado |
| Detalhe item | Inventory.renderDetail/renderStage | nível/XP/atributos/status/origem/cópias; CTA equip/unequip | Preview em coluna separada no desktop; falta comparação contextual e estado bloqueado |
| Alimentar unidade | Inventory.selectionPopup/feedPopup | alvo UID, lista UID; preview XP; AlimentarPet | Multiseleção existe; protege equipados, mas não favoritos; ação consome itens sem confirmação posterior |
| Fundir hats | Inventory.selectionPopup/fusePopup | alvo UID, lista UID; preview XP; FundirHat | Idem; preserva maxLevel; resposta do servidor não traz nivelAntes/nivel, embora cliente tenta levelUp genérico |
| Renomear unidade | Inventory.renamePopup | até 20 codepoints; RenomearPet(uid, texto) | Filtro público no servidor; “Nome original” restaura; feedback erro/sucesso via invoke |
| Viajar / Áreas | Menus.areas | Config.Areas, areas, CurrentAreaId, areaFavorites; UITravel/buyArea | Áreas bloqueadas/desbloqueadas/aqui, favoritos locais; preservar sequência de unlock |
| Comprar área | ExpeditionClient.buyArea/confirm; FeedbackMina comprarArea | área, custo, saldo; ComprarArea | Preview da ilha + confirmação/saldo já bons; apenas compra, não viaja automaticamente |
| Invocar | Menus.summon; G/AbrirGacha | Config.Gachas, bannerArea, pity, luckyMult, giroGratis, capacidadePets, moeda | x1/múltiplos, ir ao banner, proximidade; servidor cobra cada roll e valida distância |
| Chances | Menus.rates popup | Config.distGacha(bannerArea,luckyMult), pity | Deve continuar mostrando probabilidades reais e regras de garantia |
| Revelação de invocação | ExpeditionClient.showResults | retorno petId/raridade/novo/gratis; Continue/Again | Cards escalonados, destaque melhor item; falta ownership/cancel lifecycle robusto |
| Forja | Menus.forge; AbrirIgnis/nav/vender | mochila + infoMinerio + valor/multiplicadores; Vender | Lista minérios e venda total; estado vazio presente; não inventar reward local |
| Acesso Ignis | ExpeditionClient.accessPopup | semAcesso retornado pelo servidor | Teleporte grátis priorizado + passe opcional; preservar alternativa gratuita |
| Missões | Menus.progress | Config.Missoes, missoes[id]={p,r}, areas; ResgatarMissao | Seleção por ilha, claim individual/claim all; regra de conclusão no servidor |
| Diário | Menus.daily | Config.DAILY, daily={dia,disponivel}; ResgatarDaily | Ciclo de 7 dias sem perda; UTC do servidor; não apresentar como streak que expira |
| Index | Menus.index | index.pets/hats, catálogos e origem | Progresso global/por ilha, sem recompensa de poder; falta navegação direta para itens faltantes |
| Configurações | Menus.settings | atributos locais MusicEnabled/LobbyVFXEnabled/SomMineracaoEnabled/SomInterfaceEnabled/ExpeditionBlurEnabled | Não persistem no save; sem volume slider/reduced motion; coluna estreita deve virar scroll |
| Códigos | Menus.settings | ResgatarCodigo(texto) | Empty string apenas ignora; coinBurst(500) é constante independentemente do reward real, pode ser pet-only |
| Atalhos | Menus.settings | H/J/G/T | Texto PC estático; falta variante touch/gamepad |
| Toasts | Notify.push → Notifications | success/error/warning/reward/info | Até 3 visíveis, fila até 4, dedup; erro/sucesso têm representação textual e glyph |
| Feed loot | Notify.feed → Notifications | chave minério/hat, nome/qty/cor | Agrupa por tipo; até 5 visíveis; preservar feedback leve repetitivo |
| Banners reward/área | Notify.banner/levelUp | fila de momentos importantes | Fila própria independente dos reveals/popups; pode competir no mesmo espaço |
| Reveal novo hat | Notify.reveal | id, rarity, novo; FeedbackMina hat | Fila própria com card/efeitos; primeiro comum pode sobrepor outras janelas |
| CoinBurst / CoinDelta | ExpeditionClient | amount/posição carteira | FX limitados 5–14 coins; tarefas tardias devem validar geração da carteira |
| Ofertas contextuais | ExpeditionClient.ofertaPopup; OfertaMostrar | Starter, Inventario, AutoSell; OfertaAcao fechada | UI ignora dados/contexto do evento: inventário pet cheio sugere “Fundir hats”; X/Escape não disparam caminho fechar(acao) da oferta |
| Hold Mode | AutoMinerar cria PlayerGui.HoldModeGui, DisplayOrder=2 | toggle/tecla T/RT/touch, atributo HoldMode | Já usa Theme; posição e escala paralelas ao HUD; não bloqueia raycast atrás de UI |
| Transição de ilha | IslandTransition cria ScreenGui DisplayOrder=1000 | atributo AreaTransition, Config.Areas/Temas, Theme assets | Animação guiada pelo servidor; barra indeterminada não mede carregamento; preservar cancel/revision |
| Vida minério/chefe | AreaBuilder cria Hitbox.Vida BillboardGui | HP/HPMax; Nome/Fundo/Barra/HPTexto/Recompensa | Mineracao e MineracaoVisual procuram nomes; chefes sempre visíveis, normais ativados no golpe |
| Efeito de minério | AreaBuilder cria Hitbox.EtiquetaEfeito | Config.SPAWN.efeitos, multiplicador | Banner dourado/arco-íris no mundo; não esquecer consistência |
| Números de dano | MineracaoVisual Billboards temporários | FeedbackMina dano/quebrou; posição/raridade | FX limitados/cleanup; preservar sincronização com golpe, sem segundo swing aparente |
| Nome/raridade pet seguidor | PetsSeguidores cria NomePet | PetsEquipados/PetsApelidos, Config | Paleta/fonts duplicadas fora Theme; manter pet andando atrás e nome filtrado |
| Placas/portais/gachas/NPCs | AreaBuilder + builders de ilhas | SurfaceGui/BillboardGui, nomes temáticos, preços, ProximityPrompt | Parte da identidade do mundo, não remover como lixo; padronizar tipografia onde legível sem redesenhar mundo |
| CoreGui Roblox | AutoMinerar desativa Backpack | mochila nativa desativada; leaderboard de PlayerData | Manter Backpack off; leaderboard tem Minérios/Moedas; Marketplace prompt é nativo e não deve ser substituído |

## Contratos de rede preservados

Pasta: `ReplicatedStorage.Remotes`. As ações retornam `{ok:boolean,msg?:string}` salvo PedirDados (snapshot/nil). `ctx.invoke` faz pcall, lock por nome do remote, tratamento semAcesso e som/reward. O lock não é feedback visual suficiente sozinho.

| Remote / classe | Argumentos | Consumidor no servidor / retorno relevante |
|---|---|---|
| PedirDados / RF | nenhum | Main → PlayerData.snapshot + passes |
| AtualizarDados / RE S→C | snapshot completo | PlayerData.sincronizar; ExpeditionClient.acceptData valida petsInv/hatsInv; versão protege pull inicial stale |
| EquiparPicareta / RF | id:string | IgnisService; equipamento comprado |
| ComprarPicareta / RF | id:string | IgnisService; compra+equipamento, semAcesso se fora lobby |
| ComprarMochila / RF | id:string | IgnisService; tier, custo, acesso |
| Vender / RF | nenhum | IgnisService; `{ganho,itens,semAcesso?}` |
| EquiparHat / RF | uid:string | IgnisService + HatVisual.aplicar; alterna equipar/desequipar |
| EquiparMelhores / RF | nenhum | IgnisService + HatVisual |
| DesequiparTodos / RF | nenhum | IgnisService + HatVisual |
| FundirHat / RF | alvoUid:string, listaUid:table <=300 | IgnisService; usados/msg; servidor evita alvo/equipados/duplicatas/max level |
| EquiparPet / RF | uid:string | PetService; alterna equip/unequip |
| EquiparMelhoresPets / RF | nenhum | PetService |
| DesequiparPets / RF | nenhum | PetService |
| AlimentarPet / RF | alvoUid:string, listaUid:table <=300 | PetService; levelUp,nivelAntes,nivel,xp; proteção servidor igual hats |
| RenomearPet / RF | uid:string, texto:string | PetService; texto filtrado público, 20 caracteres |
| FundirPet / RF legado | qualquer | Main devolve erro “Use Alimentar no inventario”; manter compatibilidade, não usar novo fluxo |
| ComprarArea / RF | areaId:number | Progresso; sequência/custo/snapshot |
| ResgatarMissao / RF | id | Progresso; meta/claim único, economia intacta |
| ResgatarDaily / RF runtime | nenhum | Retencao; `{dia,msg}`; save assíncrono |
| ResgatarCodigo / RF | texto:string | Codigos; case/whitespace normalization, cooldown, one-use |
| RolarGacha / RF | areaId:number | GachaService; `{petId,nome,raridade,novo,gratis,pity,ovo}`; primeiro global grátis |
| UITravel / RF runtime | action:string, id?:number | ExpeditionTravel; area 0..6, gacha 1..6, shop/ignis sem ID; cooldown 1.5s e personagem válido |
| ComprarRobux / RF runtime | chave:string | Ofertas → Marketplace prompt; ok significa prompt iniciado, não compra entregue |
| OfertaMostrar / RE S→C runtime | oferta:string, dados:table | Ofertas; cliente atual ignora dados |
| OfertaAcao / RE C→S runtime | "fechada", oferta:string | Ofertas telemetria |
| AbrirIgnis / RE S→C | nenhum | Main ProximityPrompt → Forge |
| AbrirLoja / RE S→C | nenhum | Main ProximityPrompt → Store/Mochilas |
| AbrirGacha / RE S→C | areaId | Main ProximityPrompt → Summon/bannerArea |
| Golpear / RE C→S | Hitbox:BasePart | Main/Mineracao valida classe/nome/HPMax/distância/cooldown |
| AnimarPicareta / RE S→C | miner,rock,startedAt,isImpact,position | MineracaoVisual + locomotion; não alterar tempo do impacto |
| FeedbackMina / RE S→C | info:table discriminada por tipo | ExpeditionClient + MineracaoVisual; dano/quebrou/hat/cheia/bloqueada/area/comprarArea |

## Dados e caminhos que não podem ser confundidos

- `petsInv[UID]={id,nivel,xp,apelido?...}` e `hatsInv[UID]={id,nivel,xp,...}`: equipar e consumir usam UID, thumbnails/catálogo usam `inst.id`. Uma cópia por entrada; não colapsar UIDs no envio.
- `petsEquipados` e `equipados`: listas de UID. `pets`/`hats`: resumos agregados; não substituem os inventários.
- Snapshot também inclui `picaretasCompradas,missoes,bonusDanoPets,levelBonus,slotsPets,totalPets,capacidadePets,velocidade,velPets,velPetsMax,moeda,picareta,intervalo,mochilaTier,mochila,areas,dano,danoHats,capacidade,carregado,slots,totalHats,capacidadeHats,qtdMinerios,pity,giros,giroGratis,index,daily,boosts,compras,cosmeticos,multMoedas,friendBoost,luckyMult,passes`.
- Persistente no servidor: inventário, equipamentos, área, missões, moedas, daily, codes, pity, receipts/compras, boosts, index. Local de sessão: filtros, ordenação, seleção, scroll, favoritos, favoritos de área, preferências `Player:SetAttribute`.
- `Theme.preview`: pets mapeados em `Config.PetArte[id]` usam 2D busto/corpo; outros usam `ReplicatedStorage.PreviewModelos.Pets[id]`; picaretas usam `ExpeditionPreviews.Pickaxes[def.modelo]`; hats usam `Config.HatAssets[id]` via rbxthumb. Preservar o caminho 2D de roupa em camadas.
- `Theme.button` retorna GuiButton contendo `Face.Caption`; consumidores editam Caption, `Face` para shine e `ToneColor`/`Disabled` attributes. Refactor do componente deve manter isso ou migrar TODOS consumidores.
- `ExpeditionClient` procura Window.Banner.Title, Subtitle, Tabs, e UIStroke. `OpenPage` no ScreenGui é estado público; no snapshot AutoMinerar ainda NÃO o lê.
- Mundo: `Workspace.Gachas.Gacha_<tema>.PadGacha`; `Workspace.Areas.Area<id>` atributo `EntryPosition`; `Barreira.LiberaComArea`; `Hitbox.Vida` com descendentes `Barra/HPTexto`; `Visual` no grupo de minério.
- Viagem: Player `CurrentAreaId` informa ilha; `AreaTransition` informa transição. Mining: `IntervaloGolpe`, `MiningTargetSelected`, `HoldMode`; atributos do character `MiningSwingStart/Active` e `MiningComboGolpe` mantêm animação/coleta sincronizadas.

## Presentes, parciais e ausentes

Presentes: lojas de moedas/passes/produtos, equipamentos, inventários, UID, equip melhores, alimentação/fusão multi-select, renomear filtrado, missões por ilha, daily, index, pity/probabilidades, teleporte, área unlock, notificações em filas, loot/reveal, efeitos e sons de mineração, loading de dados, empty de inventário/forja, estado de limite/owned/locked de áreas, tooltips, atalhos.

Parciais: input gamepad (`Selectable=true` e Activated, mas sem foco inicial/retorno/B), mobile (escala virtual e alguns layouts, mas linhas fixas/overflow), saved settings (só sessão), favoritos (só sessão e sem proteção), redução de motion (ausente), feedback de backend em algumas páginas sem busy visível, fila global de camadas (filas independentes), sort (fixo, sem controle), compare (equipamentos sim, unidades não), bloqueio de unidades (ausente).

Ausentes como sistema de gameplay: conquistas resgatáveis, eventos temporizados reais além de daily/index, level de jogador, trade, crafting independente, delete multi de itens, volume slider, loadout salvo. Não fabricar esses produtos nem alterar save/economia por demanda visual; explicar o que a UI representa hoje. A categoria Events chama-se “Diário & Index”, coerente com o conteúdo existente.

## Riscos técnicos e oportunidades específicas

- `Inventory` contém `fx = nil` global dentro do loop de filtros; resíduo sem função, remover na reconstrução.
- `FundirHat` retorna somente usados/msg. `ctx.invoke` detecta palavra “nivel” e chama levelUp sem dados, enquanto PetService fornece os números. UI pode inferir comparação de snapshot ou usar feedback genérico sem inventar números.
- RenderBody destrói/cria toda UI ao mudar seleção/filtro e em snapshots; 3D clones de todos os cards podem custar com capacidade 100. Usar previews estáticos em cards, apenas detalhe animado, e evitar atualização desnecessária por moedas.
- `Theme.fitText` permite tamanho 7 e multiplica leitura por até 1.3; caracteres podem ficar tecnicamente “cabendo” porém ilegíveis. Layout deve ceder espaço antes de encolher texto.
- Tooltips são MouseEnter somente e não são limitados às margens da tela. Compensação de inset deve ser validada por screenshot.
- `Theme` tem cores semânticas mas tokens de raio/espaçamento/motion dispersos; fontes principais Fredoka + contorno, stroke/gradient/gloss em quase todo componente. A mesma identidade é duplicada em AreaBuilder, PetsSeguidores e MineracaoVisual.
- Notify.banner e Notify.reveal têm filas próprias, enquanto ofertas e confirmação compartilham dialogHost. Introduzir prioridade/adiamento evita fechar confirmação de consumo com oferta tardia.
- Ofertas.inventarioCheio/mochilaCheia não verificam minutos>=5; apenas Starter faz. O comentário ético é mais estrito que execução atual; não modificar monetização sem necessidade, mas UI deve evitar interromper foco e respeitar opção grátis.
- Produtos/Passes usam Marketplace e recibos no servidor. Não acionar compra real para QA; ids atuais=0 impedem esse fluxo e devem permanecer.
- ResgatarDaily marca claim antes de entregar todos itens. Inventário cheio pode resultar em menos hats/pet que o card anuncia; apresentação deve orientar capacidade antes de resgatar e reportar retorno real. Evitar alterar lógica de rewards nesta reconstrução.
- Destruição ScreenGui atual só remove blur, enquanto listeners globais/loops no LocalScript não possuem teardown completo; inserir um controlador idempotente para impedir GUI duplicada em reload/dev é desejável, sem introduzir arquitetura paralela desnecessária.

## Qualidades a preservar

1. Servidor autoritativo, guardas de perfil, cooldown, receipts, sessão de save e perfil temporário que não sobrescreve save real.
2. Separação Theme/Notify/Inventory/Menus já existente; reutilizar em vez de adicionar um segundo framework.
3. Pull inicial com tentativa e versão de push, invocations com pcall e lock por remote.
4. Dados de gacha reais, primeiro giro grátis, garantia/pity, capacidade e proximidade do banner.
5. Nome público de pet filtrado no servidor; UID individual, equipamentos excluídos do consumo.
6. Alternativa de teleporte grátis nas ofertas e acesso ao Ignis; sem contagem falsa para compra.
7. Feedback de mineração já sincronizado com impacto, som em camadas, distância/cap de FX, cleanup de temporários; preservar pose e Tool.Grip.
8. Portrait 2D para roupas em camadas e fallback 3D/thumbnail para outros assets.
9. Filas de toast/banner/reveal, dedup de loot, diferentes intensidades de reward.
10. Tween/RenderStepped de previews e efeitos infinitos já cancelam ao Destroying; manter essa disciplina nos novos componentes.

## QA mínimo depois da reconstrução

Abrir/fechar/navegar todas 8 páginas e aliases; Escape/X/backdrop/gamepad; clique atrás da janela não deve selecionar minério; redimensionar não deve consumir/perder resultado; pesquisa/acento/sort/raridade/equipado/favorito/bloqueado/empty/capacidade cheia; equip/unequip/melhores; alimentar/fundir alvo e lista por UID sem consumir protegidos; renomear/restaurar/erro; comprar moeda sem saldo e com saldo; Robux Em breve; travel bloqueado/aqui/lobby/banner; gacha x1/multi/primeiro grátis/sem moedas/cheio/cancel; missões individual/all; daily usado/disponível/capacidade; código inválido/válido/duplicado; mining hit/break/chefe/loot/bag full/venda; preferências; sounds; labels world e pet. Validar 1366×768, 1920×1080, 2560×1440 e mobile portrait/landscape com UI real.
