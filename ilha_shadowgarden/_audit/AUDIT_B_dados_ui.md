# AUDIT B: dados do jogador, DataStore, inventario, recompensas, remotes, UI e boosts

Escopo: preparar a Ilha Shadow Garden (Craft de pocoes + Masmorra periodica que da INGREDIENTES) sem quebrar saves nem criar sistemas paralelos. Tudo abaixo foi lido no codigo exportado (`_audit/scripts/`). Nada foi alterado.

Abreviacoes dos arquivos (todos em `_audit/scripts/`):

| Abrev. | Arquivo |
|---|---|
| PD | `ServerScriptService.Core.PlayerData.module.lua` |
| MAIN | `ServerScriptService.Core.Main.server.lua` |
| REC | `ServerScriptService.Core.Recompensas.module.lua` |
| IGN | `ServerScriptService.Core.IgnisService.module.lua` |
| ECO | `ServerScriptService.Core.Economia.module.lua` |
| PROD | `ServerScriptService.Core.Produtos.module.lua` |
| OFE | `ServerScriptService.Core.Ofertas.module.lua` |
| RET | `ServerScriptService.Core.Retencao.module.lua` |
| COD | `ServerScriptService.Core.Codigos.module.lua` |
| MIN | `ServerScriptService.Core.Mineracao.module.lua` |
| GAC | `ServerScriptService.Core.GachaService.module.lua` |
| PROG | `ServerScriptService.Core.Progresso.module.lua` |
| DEV | `ServerScriptService.Core.DevTest.server.lua` |
| QA | `ServerScriptService.Core.UIPolishQA.server.lua` |
| CFG | `ReplicatedStorage.Config.module.lua` |
| E31 | `ReplicatedStorage.EconomiaV31.module.lua` |
| MON | `ReplicatedStorage.MonetizacaoConfig.module.lua` |
| TH | `ReplicatedStorage.ExpeditionUI.Theme.module.lua` |
| MEN | `ReplicatedStorage.ExpeditionUI.Menus.module.lua` |
| INV | `ReplicatedStorage.ExpeditionUI.Inventory.module.lua` |
| NOT | `ReplicatedStorage.ExpeditionUI.Notify.module.lua` |
| CLI | `StarterPlayer.StarterPlayerScripts.ExpeditionClient.client.lua` |

---

## 1. Perfil (schema), DataStore e migracao

### 1.1 Armazenamento
- DataStore `"MineracaoSim_v2"`, chave `"u_" .. UserId` (PD:29, PD:249). Um unico registro por jogador; nao existe segundo DataStore (MAIN:53 reforca: "never a new DataStore").
- Sondagem real com `GetAsync("__sonda__")`; se falhar cai para `storeMemoria` (tabela em RAM, PD:12-45) e avisa no Output (PD:47-59). `USANDO_MEMORIA` exposto via global `PlayerDataUsandoMemoria()` (PD:61).
- Trava de sessao: `carregar` usa `UpdateAsync` gravando `sessao = {id = sessaoId, t = os.time()}`; outra sessao com trava de menos de 180 s (`TRAVA_VALIDA`, PD:66) faz tentar de novo ate 5 vezes com 2 s de espera (PD:252-272).
- Se nao carregar: `perfilNovo()` com `__semSalvar = true`, perfil temporario que NUNCA grava (PD:277-282).
- `salvar` so grava se a trava ainda for desta sessao (PD:326-348); ignora `__semSalvar` (PD:329) e `__dev` sem `__devSalvar` (PD:330). Soma `tempoJogado` (PD:331-334).
- `copiaParaSalvar` copia TODA chave de string que nao comeca com `__` (PD:316-323). Portanto **qualquer campo novo no perfil e salvo automaticamente**, e qualquer campo `__x` e transitorio.
- Autosave a cada 120 s (MAIN:133-140), `BindToClose` salva todos com `liberar=true` (MAIN:125-130), `PlayerRemoving` -> `descarregar` (MAIN:114-123, PD:350-353).

### 1.2 Todos os campos de `perfilNovo()` (PD:68-106)

| Campo | Tipo / formato | Obs. |
|---|---|---|
| `ui` | `UIPreferences.sanitize()` | escala de UI (PD:70, PD:306-311) |
| `movementSpeed` | number 1..2 (passo .25) | so vale com passe Speed2x (PD:422-438) |
| `audio` | `AudioPreferences.sanitize()` | PD:72, PD:296-304 |
| `moeda` | number | |
| `picareta` | id string | `"enferrujada"` |
| `mochilaTier` | id string de `Config.Mochilas` | `"saco_pano"` |
| `mochila` | `{[idMinerio] = qtd}` | **so minerios**, id `tema_variante` (ex. `chakra_incomum`, CFG:808) |
| `hats` | legado empilhado | so migracao (PD:183-200) |
| `hatsInv` | `{[uid "hN"] = {id, nivel, xp, xpTotal}}` | 1 entrada por item (PD:110-116) |
| `hatSeq` | int | gerador de uid |
| `equipados` | lista de uid de hats | |
| `pets` | legado empilhado | so migracao (PD:162-182) |
| `petsInv` | `{[uid "pN"] = {id, nivel, xp, xpTotal, apelido?}}` | PD:119-125 |
| `petSeq` | int | |
| `petsEquipados` | lista de uid | limitado a `PET_SLOTS_BASE` na carga (PD:231-239) |
| `apelidos` | legado | |
| `picaretasCompradas` | `{[id]=true}` | |
| `missoes` | `{[idMissao] = {p, r}}` | |
| `codigos` | `{[CODIGO]=true}` | |
| `minerados` | int | placar |
| `areas` | `{[areaId]=true}` | `{[1]=true}` |
| `paredes` | `{[areaId] = moeda depositada}` | Paredes de custo |
| `econVersao` | string | reescrita na carga (PD:245) |
| `pity` | `{l, m}` | |
| `giros` | int | |
| `index` | `{pets={}, hats={}}` | colecao |
| `daily` | `{dia, ultimo}` | `ultimo` = dia UTC |
| `boosts` | `{sorte = ts, moedas = ts}` | **os.time() em que termina** (PD:98) |
| `recibos` | `{[PurchaseId] = os.time()}` | podado apos 60 dias (PD:240-244) |
| `compras` | `{[chaveProduto] = qtd}` | |
| `cosmeticos` | `{[id]=true}` | |
| `tel` | `{[marco] = os.time()}` | marcos de telemetria/onboarding |
| `exp` | tabela | ExperimentService |
| `tempoJogado` | segundos | |
| `criadoEm` | os.time() | |

Campos transitorios (nunca salvos): `__semSalvar`, `__dev`, `__devSalvar`, `__entrouEm`, `__player`, `__multMoedas`, `__friendBoost`, `__luckyMult`, `__invCheio` (PD:280-284, ECO:84-89, REC:26-29), `sessao` e gerenciado pelo proprio PD.

### 1.3 Capacidades (regras reais)
- Mochila (minerios): `capacidade = Config.Mochilas[tier].capacidade` (PD:386-389; valores em E31:157-193). Ocupacao = soma `qtd * Config.espacoMinerio(id)` (PD:496-500), onde `espacoMinerio = espacoVariante * espacoMundo` (CFG:748-755; E31 `ESPACO`/`ESPACO_MUNDO` :24-25). `mochilaCheia` (PD:508-511). **Atencao: `espacoMinerio` devolve 1 para qualquer id que nao seja minerio** (CFG:754) -> um item nao-minerio dentro de `mochila` ocuparia espaco e bloquearia a mineracao.
- Hats: `Config.capacidadeHats()` = 50 (`E31.INVENTARIO`, CFG:265-268) + passes Inventario(+50)/Inventory300/Inventory1000 (PD:453-455, PD:475-477). Pets idem (PD:456-458).
- Slots: hats `Config.slotsHat(maiorArea)` + HatSlot(+3) (PD:471-473); pets `PET_SLOTS_BASE` (3) + PetSlots(+3) (PD:440).
- Nao existe limite de pilha (stack) em nenhum lugar: `mochila[id]` so e limitada pelo espaco total.

### 1.4 Como a migracao funciona (onde colocar campo novo)
`normalizar(p)` (PD:142-247) roda em toda carga bem-sucedida (PD:276):
1. **Merge raso**: para cada chave de `perfilNovo()` ausente no save, copia o default (PD:143-146). Logo, **um campo NOVO DE TOPO adicionado em `perfilNovo()` migra sozinho** para saves antigos.
2. **Chaves aninhadas NAO migram sozinhas**. Exemplo real: `p.boosts.sorte, p.boosts.moedas = ... or 0` (PD:154) e `p.index.pets = p.index.pets or {}` (PD:150-151). Se for adicionado `boosts.dano`, e obrigatorio acrescentar `p.boosts.dano = p.boosts.dano or 0` aqui, senao `PlayerData.snapshot` quebra em `perfil.boosts.X - agora` (padrao de PD:586) com nil.
3. Limpeza de ids que sairam do catalogo (hats/pets, PD:201-223) -> repetir o mesmo padrao para ingredientes/pocoes (remover id desconhecido, `math.floor`, clamp >= 0, clamp no stackMax).
4. `carregarVazio()` = `normalizar(perfilNovo())` (PD:314) -> campo novo aparece tambem no perfil zerado de teste.

Receita segura para os sistemas novos:
- Em `perfilNovo()` (PD:68-106) acrescentar **`itens = {}`** (pilhas `[idItem] = qtd`, ver secao 3) e, se a masmorra precisar de estado por jogador, **`masmorra = { ultimaEntrada = 0, runs = 0 }`** (ou similar). Nada mais em lugar nenhum e necessario para salvar.
- Em `normalizar` (depois de PD:154) sanitizar: `for id,q in pairs(p.itens) do if not Config.itemPorId(id) or type(q)~="number" then p.itens[id]=nil else p.itens[id]=math.clamp(math.floor(q),0,def.stackMax) end end`, e garantir sub-chaves de `masmorra`/novos `boosts`.
- Em `snapshot` (PD:537-593) expor `itens = perfil.itens` e os boosts novos (ver 2.4).
- Em DEV `limparTudo` (DEV:79-95) zerar `perfil.itens = {}` (hoje ele reseta campos um a um; campo novo ficaria sujo).

---

## 2. Boosts / consumiveis existentes (Craft DEVE reutilizar isto)

### 2.1 Armazenamento
- `perfil.boosts = { sorte = <os.time fim>, moedas = <os.time fim> }` (PD:98). Nao ha outro conceito de consumivel/pocao no jogo (grep por craft/pocao/ingrediente/dungeon/masmorra: zero resultados). O unico "item consumivel" hoje e o proprio boost temporizado.

### 2.2 API (PD:525-533)
```lua
function PlayerData.boostAtivo(perfil, tipo) return (perfil.boosts[tipo] or 0) > os.time() end
-- boosts do mesmo tipo somam TEMPO, nunca multiplicador
function PlayerData.adicionarBoost(perfil, tipo, minutos)
	perfil.boosts[tipo] = math.max(perfil.boosts[tipo] or 0, agora) + math.floor(minutos * 60)
end
```
- Generica por `tipo` (qualquer string). Expiracao implicita: compara com `os.time()`; nunca e limpo (o timestamp velho so fica no passado). Funciona offline (relogio de parede), ou seja, o tempo corre com o jogador fora do jogo.
- Nao ha nivel/forca por boost: um tipo = um multiplicador fixo.

### 2.3 Quem da boost hoje
- Produtos Robux: `prod.boost/prod.minutos` e `conteudo.boosts` (PROD:28-35; catalogo MON:23-24 BoostSorte 15 min, BoostMoedas 30 min; Starter MON:31-33).
- Daily: itens `{tipo="boost", boost="sorte"|"moedas", minutos}` (CFG:667, CFG:670; entrega RET:42-45).
- Codigos: nao dao boost (COD:12-16).

### 2.4 Onde os boosts sao APLICADOS
| Multiplicador | Formula | Aplicado em |
|---|---|---|
| Moedas | `ECO.multMoedas` = VIP 1.10 x boost `moedas` 2.0 x (1+FriendBoost) (ECO:68-73; MON:36-43) | venda Ignis (IGN:36-42), bonus de efeito do minerio (MIN:153), chefe (BossService:103) |
| Sorte | `ECO.luckyMult` = Lucky 1.25 x LuckyPlus 1.5 x boost `sorte` 1.5 (ECO:76-82) | raridade de hat drop (REC:64-68 via `Config.aplicarLucky`, CFG:278-287, so Epico+), gacha (GAC:72), taxas mostradas na UI via `__luckyMult` |
| **Dano** | `PD.dano = (DANO_BASE + hats) * picareta.mult * (1 + bonusPets)` (PD:373-379) | **nenhum boost de dano existe**. Golpe usa `PlayerData.dano(perfilAgora)` (MIN:314) |

- Valores transitorios para o cliente: hook `PlayerData.antesDeSincronizar` preenchido por Economia (ECO:84-89) -> `snapshot.multMoedas/friendBoost/luckyMult` (PD:589-591).
- Snapshot envia **segundos restantes**, nao timestamp: `boosts = { sorte = max(0, fim-agora), moedas = ... }` (PD:586). **Hardcoded nas 2 chaves.**

### 2.5 Pontos hardcoded que precisam virar tabela ao criar pocoes
1. PD:154 defaults `sorte/moedas`.
2. PD:586 snapshot `sorte/moedas`.
3. CLI:1019-1053 `renderBuffs` monta chips so para `moedas` e `sorte` (textos/cores/icones fixos).
4. CLI:1190-1196 som "boost" ao detectar aumento, laco fixo `{ "sorte", "moedas" }`.
5. PROD:34 e RET:45 rotulo `(b.boost == "sorte" and "Sorte " or "Moedas x2 ")` -> um boost novo seria rotulado "Moedas x2".
6. MON:39-40 um multiplicador por tipo (`BOOST_SORTE_MULT`, `BOOST_MOEDAS_MULT`).

### 2.6 Recomendacao para pocoes
- Pocao = item empilhavel em `perfil.itens` (secao 3). **Beber** = remover 1 unidade e chamar `PlayerData.adicionarBoost(perfil, def.boost, def.minutos)`. Mesmo campo, mesma expiracao, mesma soma de tempo que Daily/Robux. Nada de timer paralelo.
- Criar um catalogo unico de tipos de boost (ex.: `MON.BOOSTS = { sorte={mult=1.5,nome="Sorte",icone="potion",cor="success"}, moedas={mult=2,...}, dano={mult=1.25,...} }`) e trocar os 6 pontos acima para iterar sobre ele.
- Pocao de dano: adicionar o termo em `PlayerData.dano` (PD:374-379), p.ex. `* (PlayerData.boostAtivo(perfil,"dano") and Mon.BOOSTS.dano.mult or 1)`. **Nao** colocar em Economia: Economia requer PlayerData (ECO:7), PlayerData requerer Economia criaria ciclo. PlayerData pode requerer `RS.MonetizacaoConfig` (ou modulo de config novo) sem ciclo.
- Pocoes "mais fortes" do mesmo efeito: o modelo so tem 1 multiplicador por tipo; usar chaves distintas (`sorte`, `sorte2`) em vez de mudar a estrutura (numero = timestamp) para manter compatibilidade.
- Ao expirar nao ha sync: o `dano` do HUD fica velho ate o proximo `sincronizar` (acontece a cada minerio quebrado, MIN:169). Aceitavel; se quiser exato, agendar `task.delay(restante, sincronizar)` ao beber.

---

## 3. Categorias "ingrediente" e "pocao" no inventario existente

### 3.1 O que existe
- 3 armazenamentos: `mochila` (pilhas de minerio, buffer de venda), `hatsInv` e `petsInv` (instancias por uid com nivel/xp).
- A pagina Inventario (INV) so conhece `kind = "pet" | "hat"` (INV:14-17, INV:20-23, INV:848); cartas vem do catalogo `Config.Pets/Hats` + instancias (INV:93-163), com hero de personagem, equipar/fundir/alimentar.
- A mochila so aparece na Forja (MEN:523-574), filtrada por `Config.infoMinerio(id)` (MEN:526).

### 3.2 Por que NAO guardar ingrediente/pocao em `perfil.mochila`
1. `IgnisService.vender` apaga a mochila INTEIRA: `perfil.mochila = {}` (IGN:57), mesmo para ids que `infoMinerio` nao reconhece (IGN:39-49 so ignora no calculo). Auto Sell (MIN:270-278) chama o mesmo. Ingredientes seriam destruidos na venda.
2. `itensNaMochila` conta tudo com `espacoMinerio` = 1 para ids desconhecidos (PD:496-500, CFG:748-755): ingredientes ocupariam capacidade e disparariam "Mochila cheia" na mineracao (MIN:296, MIN:311).
3. `infoMinerio` usa o padrao `^(%a+)_(%a+)$` (CFG:817-821): um id tipo `sombra_raro` seria tratado como minerio vendavel.
4. A Forja nao listaria (MEN:526), entao o jogador perderia itens invisiveis.

### 3.3 Recomendacao: um unico armazenamento de pilhas `perfil.itens`
- `perfil.itens = { [idItem] = qtd }` para AMBAS as categorias. A categoria vem do catalogo, nao do save. Nao e paralelo: e o complemento empilhavel de hatsInv/petsInv (que sao por instancia); a mochila continua sendo so o buffer de venda de minerios.
- Catalogo (estrutura) em Config, p.ex. `Config.Itens = { {id="sg_po_sombra", nome=..., categoria="ingrediente", raridade="raro", icone=..., stackMax=999}, {id="sg_pocao_sorte", categoria="pocao", boost="sorte", minutos=15, stackMax=99, receita={...}} }` + `Config.itemPorId(id)`. **Regra do projeto**: CFG:3-5 diz "Nao coloque numero de economia neste arquivo" e E31 e gerado ("NAO EDITE A MAO", E31:1-2). Numeros de receita/drop/duracao devem ir num modulo proprio (ex. `RS.AlquimiaConfig`) ou no pipeline do gerador, nao em Config/E31 a mao.
- Ids: prefixo proprio (ex. `sg_`) e sem colidir com `tema_variante`.
- Funcoes centrais (seguir o padrao de `novoHat/novoPet`, PD:110-125):
  - `PlayerData.darItem(perfil, id, qtd) -> qtdEntregue` (clamp no `stackMax`, rejeita id desconhecido).
  - `PlayerData.gastarItens(perfil, custos) -> bool` (verifica tudo antes de debitar, atomico).
  - `Recompensas.darItem(player, perfil, id, qtd, origem)` como wrapper com `FeedbackMina {tipo="item", ...}` e Telemetria, igual REC:46-61 faz para hats (REC e "unico lugar que entrega", REC:1-2).
- Capacidade: pilhas NAO usam a capacidade da mochila nem a de hats/pets. Limite por `stackMax` por item; ao exceder, entregar o que cabe e avisar ("cheia") como REC:23-33.
- Venda: com armazenamento separado, IGN nao precisa de mudanca (so le `perfil.mochila`). Se no futuro quiser vender ingrediente, fazer remote proprio.
- Masmorra: pedras da masmorra devem ter atributo proprio (ex. `Masmorra=true`) e desviar ANTES da mochila em `quebrar` (MIN:126-144) e no teste de mochila cheia do golpe (MIN:294-297, MIN:311), como o chefe ja faz com `ehChefe`. A recompensa sai por `Recompensas.darItem`.

### 3.4 UI do inventario para itens
- Adicionar terceira aba em `tabsFor` (CLI:771-774): `{ id="item", label="Materiais", icon="potion" }`.
- `Inventory.render` hoje trata tudo que nao e "pet" como "hat" (INV:848). Inserir no inicio de `M.render` (INV:844) um desvio `if ctx.collection=="item" then return renderPilhas(ctx,parent,w,h) end` com grade simples (T.scroll + T.tile + quantidade "x12" + botao "Beber" para pocoes). Nao reutilizar `collect/card` (dependem de nivel/equipar/hero de personagem).
- `pageTitle` (CLI:745-753) calcula "total / cap" so para pet/hat: tratar "item".
- **Obrigatorio**: incluir `itens` em `inventorySignature` (CLI:1011-1017). Sem isso, mudar so `itens` NAO redesenha a pagina Inventario (CLI:1208-1227 so da refresh por assinatura ou para paginas listadas em CLI:1225).

---

## 4. Convencoes de Remotes

### 4.1 Inventario de remotes
- Estaticos no place (`tree_replicated.txt:2-29`), pasta `ReplicatedStorage.Remotes`: AtualizarDados (RE), AbrirIgnis (RE), FeedbackMina (RE), Vender, ComprarPicareta, EquiparHat, PedirDados, ComprarMochila, FundirHat, EquiparMelhores, DesequiparTodos (RF), AbrirLoja, AbrirGacha (RE), RolarGacha, EquiparPet, FundirPet, EquiparMelhoresPets, DesequiparPets (RF), Balancar, Golpear, AnimarPicareta (RE), EquiparPicareta, AlimentarPet, RenomearPet, ResgatarMissao, ComprarArea, ResgatarCodigo (RF).
- Criados em runtime (cliente usa `WaitForChild`): via `remoteNovo(nome, classe)` (MAIN:37-42): AtualizarUIProfile, AtualizarAudioProfile, ResgatarDaily, ConcluirReveal (RE), AtualizarVelocidade, DebugV31 (so Studio). Via `criar` em OFE:90-100: OfertaMostrar (RE), OfertaAcao (RE), ComprarRobux (RF). UITravel (RF, ExpeditionTravel.server.lua:135-145). Excecao fora da pasta: `RS.ParedeAtualizar` (RE, Paredes.module.lua:289-296).

### 4.2 Convencoes observadas
- Nome em portugues, verbo + objeto: `ComprarX`, `EquiparX`, `ResgatarX`, `AtualizarX`, `AbrirX` (servidor -> cliente para abrir tela), `PedirDados`.
- **RemoteFunction** para toda acao do jogador com resposta: devolve sempre tabela `{ ok = bool, msg = string?, semAcesso = "Passe"?, ... }` (ex. IGN:29-65, PROG:11-35). **RemoteEvent** para push do servidor (AtualizarDados, FeedbackMina, AbrirIgnis/AbrirLoja/AbrirGacha, OfertaMostrar) e fire-and-forget do cliente (Golpear MAIN:208-214, ConcluirReveal MAIN:219, OfertaAcao OFE:50-58).
- Registrar handler novo: preferir `remoteNovo("NomeNovo","RemoteFunction").OnServerInvoke = ...` em MAIN (nao precisa editar o place). O cliente ja faz `R:FindFirstChild(name) or R:WaitForChild(name, 3)` (CLI:401).
- Validacao: inline, sem modulo helper. Padrao: `type(x) ~= "string"/"table"/"number"` no MAIN antes de delegar (MAIN:157, 163, 186, 232, 237, 242, 249) e checagem de tamanho de lista (`#lista > 300`, MAIN:163, MAIN:249); NaN/inf em GAC:104 e PD:422-425; tamanho do requestId 8..64 (GAC:104). Proximidade sempre recalculada no servidor pela posicao real (IGN:17-23 "Never trust a client-provided NPC flag"; GAC:66-69; MAIN:295-296).
- Rate limit: **nao ha helper generico**; cada remote tem o seu:
  - intervalo fixo 0.2 s por jogador: AtualizarUIProfile (MAIN:43-51), AtualizarVelocidade (MAIN:220-225);
  - token bucket 8 fichas, +4/s: AtualizarAudioProfile (MAIN:54-66);
  - 1.5 s: ResgatarCodigo (COD:25-27);
  - trava `ocupado[player]`: ResgatarDaily (RET:10-20);
  - trava + 1.1 s + requestId idempotente: RolarGacha (GAC:103-113);
  - cooldown do golpe pelo intervalo da picareta: Golpear (MIN:287-289);
  - todas as tabelas limpas em `PlayerRemoving` (MAIN:51, 66, 225, 273; COD:66; RET:76).
  - No cliente, `actionBusy[name]` impede 2 invocacoes simultaneas do mesmo remote (CLI:400-407).
- Autoridade: todo estado vive no perfil do servidor; o cliente so manda ids/chaves. Transacoes marcam o estado ANTES de entregar (RET:23-25) e verificam tudo antes de cobrar (GAC:80-82, testado em QA:53-55).
- Persistencia de transacao valiosa: `task.spawn(PlayerData.salvar, player)` apos entregar (RET:63); compras Robux so confirmam se o save deu certo (PROD:55-58, PROD:84-86).
- Para Craft recomendado: `remoteNovo("FabricarItem","RemoteFunction")` com args `(receitaId: string, qtd: number, requestId: string)`; validar tipo/NaN/`1 <= qtd <= 10`; trava por jogador + idempotencia por requestId (copiar GAC:103-113); checar proximidade da bancada no servidor; `gastarItens` atomico -> `darItem`; `sincronizar`; `task.spawn(salvar)`. Beber: `remoteNovo("UsarItem","RemoteFunction")` `(idItem)`. Masmorra: se a entrada for paga/limitada, `remoteNovo("EntrarMasmorra","RemoteFunction")`; se for por ProximityPrompt, validar no `Triggered` como MAIN:294-303.
- Nota de toast no cliente: `ctx.invoke` mostra `res.msg` com tipo "reward" se o nome contem "Resgatar" ou "Comprar", senao "success" (CLI:456). Escolher o nome do remote de acordo.

### 4.3 Como o snapshot chega ao cliente
- Servidor: `PlayerData.sincronizar(player, audioContext?)` (PD:598-634): roda `antesDeSincronizar` (ECO:84-89), monta `snapshot(perfil)` (PD:537-593), adiciona `passes = Passes.todos(player)`, `AtualizarDados:FireClient(player, snap)`, atualiza atributos (`PetsEquipados`, `PetsApelidos`, `IntervaloGolpe`, `VIPOwned`), leaderstats e WalkSpeed. Chamado apos quase toda mutacao (ex. MIN:169 a cada minerio quebrado, IGN:60, RET:62). **O snapshot inteiro vai a cada evento**: manter campos novos compactos.
- `PedirDados` (RF) devolve o mesmo snapshot + passes (MAIN:143-149); o cliente tenta 8 vezes na hidratacao (CLI:1329-1338).
- Cliente: `acceptData` (CLI:1173-1228) exige `hatsInv` e `petsInv` como tabela (CLI:1176), guarda em `ctx.data` e `ctx.dataClock` (tempo local para contagem regressiva de boosts), atualiza HUD e redesenha por assinatura (CLI:1208-1227). Outros leitores do snapshot: `ILHAS_Cliente.client.lua:67-69`.
- Estado GLOBAL do servidor (nao por jogador) e publicado como atributos numa pasta em RS, ex. `RS.EnergiaIlhas` (SpawnMinerio.module.lua:143-160). Esse e o padrao certo para o relogio da masmorra (secao 5.3), nao o snapshot.

---

## 5. UI: como adicionar Craft e o widget da Masmorra

### 5.1 Arquitetura
- Um unico ScreenGui `ExpeditionUI` (CLI:31-34) com camadas: `HUD`, `ModalBackdrop`, `ModalLayer` (janela de pagina), `Notifications` (toasts, Z70), `PopupLayer/Dialogs` (Z90), `TooltipLayer` (Z120) (CLI:35-48). Tudo em coordenadas virtuais 1440x850 com UIScale (CLI:28, CLI:1289-1314).
- Estado da UI em `ctx` (CLI:51-53); modulos recebem `ctx` e desenham com Theme.
- Paginas: tabela `PAGE` (CLI:189-199). `ctx.open(page)` so abre chave existente em PAGE (CLI:599) e bloqueia durante reveal/viagem (CLI:592). `drawWindow` -> `drawHeader` (abas via `tabsFor`, CLI:770-807) -> `drawBody`: `Inventory.render` para "Inventory", senao `Menus.render` (CLI:826-827), que despacha por `ctx.page` (MEN:996-1014).
- Popups: `ctx.popup(titulo, builder(area,w,h,reflow), w, h, {color, modal, onClose})` (CLI:308-317); o builder e re-executado no resize preservando texto/scroll (CLI:239-306). `ctx.confirm(titulo, msg, callback, {cost, confirmText, tone, preview, previewH})` (CLI:324-356). `ctx.closePopup`, `ctx.refreshPopup` (CLI:235, 319-321).
- Chamadas ao servidor: `ctx.invoke(nome, ...)` (CLI:398-458). Botoes de pagina: helper `action(ctx, p, name, caption, x, y, w, h, fn, enabled, reason, tone, guard, visual)` em MEN:59-87 (trava "Aguarde...", toast de razao quando desabilitado).
- Abrir pagina a partir do mundo: o servidor dispara um RemoteEvent `AbrirX` e o cliente abre (ex. AbrirIgnis MAIN:334-335 -> CLI:1280).

### 5.2 Passos para a pagina/popup de Craft
1. CLI:189-199: `Craft = { title = "Alquimia", icon = "potion", color = P.violet, sub = "Pocoes com ingredientes da Masmorra" }`.
2. TH:109-112: `T.Page.Craft = <cor>` (a cor da janela e dos botoes do HUD vem daqui, CLI:950).
3. MEN:1007-1013: `elseif ctx.page == "Craft" then M.craft(ctx, p, w, h)`; implementar `M.craft` no mesmo arquivo usando `panel`, `artSurface`, `label`, `text`, `action` (MEN:15-87), `T.scroll`, `T.tile(p,name,x,y,w,h,raridade,opts)` (TH:405), `T.emptyState` (TH:1191), `T.progress` (TH:682). Botao Fabricar via `action(... function() local res = ctx.invoke("FabricarItem", receitaId, 1, guid) if res.ok then ctx.refresh() end end ...)`. Para quantidade/confirmacao usar `ctx.popup` ou `ctx.confirm` (sem `cost` de moedas, ou mostrar ingredientes no `preview`).
4. CLI:855-856 (`windowRect`): tamanho da janela (senao usa 1280x780).
5. CLI:1225: incluir `"Craft"` na lista de paginas que dao refresh em todo snapshot (ou garantir via assinatura com `itens`).
6. Entrada: NPC/bancada com ProximityPrompt no servidor (padrao MAIN:317-337) + `remoteNovo("AbrirCraft","RemoteEvent")` + `connect(R:WaitForChild("AbrirCraft").OnClientEvent, function() ctx.open("Craft") end)` perto de CLI:1280. Opcional: botao no rail `NAV` (CLI:901-909) se o Craft for acessivel de qualquer lugar.
7. Resultado: `Notify.banner({ title = "POCAO CRIADA!", subtitle = nome, color = P.violet })` ou `Notify.reveal` para raridade Epico+ (NOT:466-470). Sons via `T.som(nome)` / `Som.tocar` (catalogo em SomJogo).

### 5.3 Widget de status/contagem da Masmorra
- Estado global: servidor publica atributos numa pasta `RS.MasmorraEstado` (mesmo padrao de `EnergiaIlhas`, SpawnMinerio:143-160): `AbreEm`/`FechaEm` como `workspace:GetServerTimeNow()` (epoch sincronizado), `Aberta` bool. Cliente calcula `restante = AbreEm - workspace:GetServerTimeNow()` e formata com `T.clock` (TH:920-927). Nao usar o snapshot para isso.
- Onde desenhar: a faixa de chips do topo `hudRefs.buffs` (CLI:938-939) ja e redesenhada a cada 1 s pelo laco CLI:1055-1061 via `renderBuffs` (CLI:1019-1053). Acrescentar um item `{ "Dungeon", "MASMORRA  " .. T.clock(restante), P.violet, "summon", "Proxima abertura" }` na `list` e chips aparecem com `T.chip(root, nome, texto, x, 0, 32, cor, {icon, size=15, w})` (TH:758-779). Como a chave "Dungeon" entra na assinatura `sig`, os textos sao so atualizados sem recriar (CLI:1035-1040).
- Alternativa (widget maior): criar dentro de `drawHUD` (CLI:911-970), guardar em `hudRefs`, e atualizar no mesmo laco de 1 s. Tudo criado fora de `drawHUD` some no `T.clear(hud)` a cada resize (CLI:912, CLI:1308).
- Aviso de abertura: servidor manda `FeedbackMina {tipo="area", texto="A Masmorra das Sombras abriu!"}` (vira toast, CLI:1273-1275) ou um tipo novo com `Notify.banner`.

### 5.4 Toasts, feed e banners (NOT)
- `Notify.push(texto, kind)` com kind `success|info|warning|error|reward` (NOT:137-141, NOT:199); no cliente use `ctx.toast(texto, nil, kind)` (CLI:208-210).
- `Notify.feed(key, nome, cor, qtd, {icon|ore})` agrupa loot repetido "+N nome" (NOT:247-276): ideal para ingredientes da masmorra.
- `Notify.banner({title, subtitle, color, sound, big, duration})` (NOT:384-394), fila de 4, dedup por titulo+subtitulo.
- `Notify.reveal({kind, id, name, rarity, tag, subtitle})` so Epico+ (NOT:466-471).
- `FeedbackMina` hoje trata `hat, quebrou, cheia, bloqueada, venda, area, comprarArea` (CLI:1240-1279). Para ingredientes adicionar `elseif info.tipo == "item" then Notify.feed("item:"..info.id, info.texto, T.rar(info.raridade).cor, info.qtd or 1, { icon = info.icone or "items" })`.

### 5.5 Tokens do tema
- Cores `T.P` (TH:18-24): ink, bg0..bg4, line, lineSoft, text/text2/text3, accent, gold, violet, magenta, success, danger, warning, info, teal, ember, pink, robux, neutral. Aliases `T.C` (TH:82-86). Raridades `T.Rarity` / `T.rar(key)` (TH:89-107, tambem aceita ids de variante de minerio).
- Espacos/raios/movimento/tipos: `T.Space`, `T.Radius`, `T.Motion`, `T.Type` (TH:25-28); fontes `T.F` (Gotham Heavy/Bold, TH:117-123).
- Icones do atlas: `T.IconIndex` inclui **`potion = 12`** (TH:164), `shiny`, `gift`, `items`, `summon`, `forge` etc. `T.icon(p, key, x, y, w, h)` (TH:268-291). Ingrediente nao tem arte: usar `items`/`shiny` ou acrescentar ids em `T.Assets` com `comFallback` (TH:296-305).
- Estilo: texto em PT-BR com acentos na UI (o codigo Lua em si evita acentos em identificadores), maiusculas via `T.upper` (TH:129-133), numeros via `T.format` (= `Config.formatar`, TH:916-918).

---

## 6. Ganchos de teste

### 6.1 `DebugV31` (RemoteFunction, so existe no Studio: MAIN:480-575)
Chamada `DebugV31:InvokeServer(acao, a, b)`; ao final (exceto os que retornam antes) faz `sincronizar` e devolve `{ok=true}` (MAIN:572-573).

| acao | efeito | linha |
|---|---|---|
| `semSalvar` | `__semSalvar = true` (nada vai para o DataStore) | MAIN:485-488 |
| `modoTeste` | `__dev = true, __devSalvar = false` (nao salva, mas compra Robux roda inteira; PROD:56) | MAIN:489-494 |
| `perfilNovo` | zera o perfil EM MEMORIA com `carregarVazio()`; marca `__semSalvar` se nao for dev | MAIN:502-508 |
| `estado` | devolve moeda, pity, giros, dano, intervalo, slots, capHats, hats, pets, lb, daily, tel, recibos, compras, **boosts**, minerados, index, exp, equipados, area, mochila, capMochila, dev | MAIN:509-516 |
| `tel` | historico de telemetria do jogador | MAIN:517-520 |
| `moedas` a | `perfil.moeda = a` | MAIN:521-522 |
| `areas` a | libera areas 1..a | MAIN:523-524 |
| `chefe` / `chefeVida` a | nasce chefe / ajusta HP | MAIN:525-526, 495-501 |
| `recibo` chave, purchaseId | simula ProcessReceipt de produto (inclusive boosts) | MAIN:527-535 |
| `hats` n | n hats aleatorios via Recompensas | MAIN:536-538 |
| `gacha_sim` n, area | simula distribuicao sem mexer no perfil | MAIN:539-549 |
| `golpear` rocha | golpe direto | MAIN:550-552 |
| `vender`, `comprarPicareta`, `comprarMochila`, `comprarArea`, `gacha`, `daily`, `equiparMelhores`, `fundirTudo`, `missao`, `oferta`, `tempo` (min), `salvar` | atalhos para os servicos reais | MAIN:553-571 |

Observacao: `estado` nao inclui campos novos; acrescentar `itens`, `masmorra` e os boosts novos ali.

### 6.2 Outros ganchos
- `DevTest` (DEV): so Studio e so `DEV_IDS` (DEV:5-10, 23-30); chat `/dev` da tudo e mantem moeda 1e15 com `__dev`/`__devSalvar=false` (DEV:32-77, 125-143); `/devoff` zera (DEV:79-95, precisa incluir `itens`). Atributo `Desligado` no script desliga sem editar (DEV:24-25).
- `UIPolishQA` (QA): teste automatizado no Studio com jogador falso, `PD.carregarVazio()` e mocks de `Passes.possui`, `PD.get`, `PD.sincronizar` (QA:13-19), resultado em atributos `Passed`/`Results` (QA:58). Modelo ideal para testes do Craft (debito atomico, idempotencia de requestId, stackMax, ingrediente nao vendido pelo Ignis).
- `Produtos._processar` exposto para testes (PROD:106).
- `PolishQA` no cliente (Studio): atributo `PolishQA` no ScreenGui abre paginas/estados (CLI:1357-1379); acrescentar `"Craft"` ali permite capturar a pagina sem clicar.
- `PlayerData.audioPersistente(perfil)` diz se a sessao persiste (PD:292-294); o snapshot expoe `uiPersistent`/`audioPersistent`.

---

## 7. Riscos e pontos de atencao (resumo)
1. **Nao usar `perfil.mochila` para ingrediente/pocao**: venda zera tudo (IGN:57), capacidade conta 1 por unidade desconhecida (CFG:754), Forja nao mostra (MEN:526).
2. Chave aninhada nova (ex. `boosts.dano`) exige default explicito em `normalizar` (padrao PD:154) ou quebra o snapshot.
3. Boosts sao multiplicador fixo por tipo e somam tempo; 6 pontos hardcoded em `sorte/moedas` (secao 2.5) precisam ser generalizados antes da primeira pocao.
4. Nao ha boost de dano; adicionar em `PlayerData.dano` sem requerer Economia (ciclo).
5. Sem helper de rate limit: craft precisa de trava + requestId (copiar GAC:103-113).
6. `inventorySignature` (CLI:1011-1017) precisa incluir `itens` senao a UI nao atualiza.
7. Numeros de balanceamento nao podem entrar em Config nem em E31 a mao (CFG:3-5, E31:1-2).
8. `Config.Areas[4]` ja e "Jardim das Sombras", tema `sombra`, sem gacha (CFG:619, E31:196). O passe `AutoSell` usado em MIN:271/IGN:25 nao existe em `MON.PASSES` (sempre falso), entao Auto Sell hoje nunca dispara.
