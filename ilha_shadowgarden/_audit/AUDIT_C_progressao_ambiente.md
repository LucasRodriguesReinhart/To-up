# Auditoria C: progressão, portões, viagem, invocação, tempo, luz, áudio, VFX e desempenho

Data: 2026-09-28. Esta auditoria foi feita só com leitura. Nada no jogo foi alterado.

**Fontes lidas:**
- `_audit/scripts/*` (export dos scripts). As referências abaixo usam o nome curto do arquivo e a linha: `Config:615` é `ReplicatedStorage.Config.module.lua`, linha 615.
- `_audit/tree_*.txt`
- `ilha_dragonball/INTEGRACAO_JOGO.md`
- `ilha_dragonball/export/conexao_roblox.json`
- `ilha_naruto/INTEGRACAO_JOGO.md`
- `ilha_shadowgarden/REFERENCIA.md`

**Observação geral:** o `workspace.Areas` que aparece em `tree_workspace.txt` é resto do modo Edit (grade antiga em x = ±1600, y ≈ 110). O `AreaBuilder.construir` apaga essa pasta e reconstrói as áreas no Play (`AreaBuilder:380-391`). Por isso, as posições das Areas e das Gachas nessa árvore não valem em runtime.

---

## 1. Ordem das áreas, regra de progressão e o conflito DB → SG

### O que o código faz hoje

**Ordem das áreas** (`Config:615-621`):

| id | tema | nome |
|---|---|---|
| 1 | chakra | Vila da Folha |
| 2 | ki | Planeta Namekusei (a ilha nova é Dragon Ball) |
| 3 | nichirin | **Monte Natagumo** (Demon Slayer) |
| 4 | sombra | **Jardim das Sombras** |
| 5 | mare | Grand Line |
| 6 | serio | Cidade Z |

**A economia depende da posição na lista.** O laço `for i, a in ipairs(Config.Areas)` define:
- `a.custo = Eco.PORTAIS[i]`;
- `hp`, `valores` e `espaco` a partir de `Eco.*[i]` (`Config:623-638`).

Valores congelados em `EconomiaV31:194-196`:
- `PORTAIS = {0, 1400, 52000, 2500000, …}`;
- `HP_COMUM = {10, 220, 6600, 198000, …}` (`EconomiaV31:6`);
- `GACHA_MUNDO = {t, t, t, false, t, t}`;
- `GACHA_GIRO[4] = 0`.

Outros dados dependem do **id** (ou do tema), não da posição:
- `ORDEM_TEMA` (dano do hat por mundo, `Config:228-229`, `Config:246`);
- bônus de pet `(areaId-1)` (`Config:398`);
- `Config.Gachas` (`Config:557-560`);
- missões (`Config:681-705`, com `CPM_REFERENCIA[a.id]` e `MINUTOS_NO_MUNDO_MEDIO[a.id]`);
- `PlayerData.maiorArea`, que usa o maior id possuído (`PlayerData:356-361`) e alimenta `slotsHat`, Retenção, Produtos e Boss.

**Regra de compra** em `Progresso.comprarArea` (`Progresso:17-20`):

```lua
local anterior = Config.areaPorId(area.id - 1)
if anterior and not perfil.areas[anterior.id] then return {ok=false, msg="Compre "..anterior.nome.." antes"} end
```

A mesma regra se repete no cliente:
- `ExpeditionClient:540-541` (`buyArea`);
- `ExpeditionClient:985-987` (`nextArea` = primeira área não possuída na ordem da lista);
- `Menus:291,310-315` ("Requer …").

**Conflito:** o portão da Ilha 2 fica em `DragonBallIsland:21-22` (`GATE_AREA = 4`, `GATE_KEY = 'ShadowGarden'`, peça `NextAreaId=4`). Quem vem da Ilha 2 recebe "Compre Monte Natagumo antes" (também documentado em `INTEGRACAO_JOGO.md`, Pendências 1).

**Onde está o Demon Slayer (área 3) hoje:**
- É uma ilha **procedural**: ramo `id==3` do `IslandWorld` (`IslandWorld:235-254`, com torii, Casa da Montanha, cedros, bambu e teias).
- Centro no `Config` em (0, 0, 1260) (`Config:771-775`).
- Atmosfera `[3]` com ClockTime 18,35 (`AreaAtmosphere:15`); música "Mysterious Forest" (`AudioCatalog:109`).
- Portal de saída com `NextAreaId=4` (`IslandWorld:394-406`); gacha `Gacha_nichirin` na alcova (`IslandWorld:377-392`).
- A parede de custo da área 3 **não é construída**, porque a Area2 tem `RotaPropria` (`Paredes:306-311`). A da área 4 é construída em z = 1470.
- Resultado: o DS hoje só é alcançável por teleporte (menu Viajar ou o disco `Santuario.Portal3`, `Main:403-424`).
- `workspace.Corredores.Area2_Area3…` são restos estáticos do Edit.

**O `Paredes` tem uma brecha.** `Paredes.depositar` libera `perfil.areas[areaId]` sem checar a área anterior (`Paredes:262-283`). Hoje o bloqueio é só físico.

### Opções (nada alterado)

#### A) Recomendada: trocar os ids 3 e 4 por dados
O Jardim das Sombras vira id 3 e o Monte Natagumo vira id 4.
- A regra `id-1`, a economia por posição e os dados por id/tema continuam coerentes com a ordem a pé (Naruto → DB → SG → DS).
- É a única opção que não quebra a curva: o SG passa a usar custo 52 mil e HP comum 6.600, em vez de 2,5 milhões e 198 mil.

O que muda:

1. **`Config`**
   - `:616-621`: trocar tema e nome dos ids 3 e 4.
   - `:228-229`: `ORDEM_TEMAS`/`ORDEM_TEMA` passam a `sombra=3`, `nichirin=4`.
   - `:347-392`: `PETS_POR_AREA`, com a lista do Natagumo indo para `[4]` e pets do SG em `[3]`, se o SG tiver gacha.
   - `:342` e `:556`: comentários.
2. **`EconomiaV31`** (gerado por `gerar.py`; regenerar, não editar à mão):
   - `GACHA_MUNDO` passa a `{t,t,?,t,t,t}`;
   - `GACHA_GIRO[4]` não pode continuar 0, senão o gacha do DS fica grátis;
   - `GACHA_GIRO[3]`/`GACHA_MUNDO[3]` conforme a decisão sobre a invocação do SG.
3. **`DragonBallIsland:22`**: `GATE_AREA = 3`. Sem isso, a placa mostra "MONTE NATAGUMO" e o preço errado, porque `DragonBallIsland:153,169-170` lê o `Config`.
4. **`ILHAS_Cliente:12`**: `GATES = {…, ShadowGarden=3, DemonSlayer=4}`.
5. **`IslandWorld`**
   - A nova linha de despacho do SG passa a usar `area.id==3`.
   - Ramos de fallback procedural por id: `palettes[3]/[4]` (`:13-14`), `id==3`/`id==4` (`:116, 118, 139, 144, 173, 182, 235, 255, 365, 377, 416, 420`). Sem a troca, o DS de fallback sai como catedral.
6. **`AreaAtmosphere:15-16`**: trocar `[3]` e `[4]`; e `:38` (`ShadowGardenMood` passa a `id==3`).
7. **Áudio**
   - `AudioCatalog:109-110`: trocar `Music[3]`/`[4]`.
   - `SomJogo:295-296`: o leito "energy" passa a `area==3`.
8. **`Theme:167`** / `T.Assets.areas[3]`/`[4]`: trocar as imagens.
9. **`BannersConfig`**: `TEXTOS[3]` e `TEXTOS[4]`.
10. **Instâncias**
    - `Santuario.Portal3`/`Portal4.Disco` AreaId: trocar, ou trocar o `Tema`.
    - `workspace.Gachas.Gacha_nichirin.PadGacha` passa a `AreaId=4`; `Gacha_sombra` com `AreaId=3`.
11. **Saves**, se já houver jogadores reais:
    - migração única de `perfil.areas[3]`↔`[4]`, `perfil.paredes[3]`↔`[4]` e missões `a3_*`↔`a4_*`;
    - hats do SG e do DS mudam de mundo e, portanto, de dano;
    - minério `sombra_*`/`nichirin_*` na mochila muda de valor;
    - os pets do DS ganham `+PET_BONUS_MUNDO`.
    - Se o jogo não tem jogadores reais, a migração é trivial.

#### B) Não recomendada sozinha: pré-requisito explícito mantendo os ids
Os ids ficam como estão (SG = 4, DS = 3), e cada área ganha um campo de pré-requisito.
- `Config`: `requer` por área (4 → 2, 3 → 4, 5 → 3).
- `Progresso:17` passa a `Config.areaPorId(area.requer or area.id-1)`.
- `ExpeditionClient:540` e `:985-987`: ordenar por `requer` ou por uma `ordem`.
- `Menus:100-101, 314`.
- A saída do SG ganha `NextAreaId=3` com `Portao='DemonSlayer'`. `ILHAS_Cliente:12` já mapeia `DemonSlayer=3`.

São cerca de 5 pontos de código, mas **a curva econômica quebra**: logo depois do mundo 2 (HP 220) viria o mundo 4 (HP 198 mil, custo 2,5 milhões), e o DS depois do SG ficaria mais fácil.

Para consertar, seria preciso reordenar os índices da economia. Só que:
- `Config.Areas[n]` é indexado por id em `Paredes:48`, `TravessiaCorredores:90,145`, `Retencao:27` e `Inventory:492,653,795`;
- `PET_BONUS`, `ORDEM_TEMA`, `Gachas` e missões usam o id.

Na prática, a correção custa tanto quanto a opção A e fica mais frágil.

#### C) Status quo: não mexer
- O portão do DB continua exigindo a área 3.
- O jogador compra o DS pelo menu e viaja por teleporte.
- A saída do SG para o DS ficaria sempre "aberta" (quem tem a 4 já tem a 3).
- Não atende à missão.

### Como o portão de saída do SG deve funcionar (vale para A e para B)
Copiar o portão do DB (`DragonBallIsland:150-173`):
- **Peça de interação:** `Portao<Key>_Interacao` dentro da pasta `PORTAO_<Key>_Integracao`, com `NextAreaId=<id DS>` e `Portao='DemonSlayer'`.
  - O `ILHAS_Cliente` reconhece a peça pelo padrão `'^Portao%w+_Interacao$'` (`ILHAS_Cliente:38`).
  - O `Main:287-305` liga o prompt a toda `NextAreaId` dentro de `workspace.Areas` **uma vez, no boot**, depois do `AreaBuilder`.
- **Placa:** `BillboardGui 'CompraPortao'` com o atributo `Portao`.
- **Malhas do portão:**
  - tag `PortaoCompra`;
  - `gate='DemonSlayer'`;
  - `gate_part` = barrier, lock, openglow ou lockcol, mais `t0` (`PortoesCompra:7-14`).
- **Emissor:** `Portao_DemonSlayer` com tag `IlhaVFX`. Liberado, a taxa cai para 0,8 (`ILHAS_Cliente:94-95`).
- **Atributos na Area:** `NextAnchorPosition`, `NextAnchorForward`, `NextAnchorWidth`, `NextAnchorClearHeight` e `NextAnchorKey`, como em `DragonBallIsland:209-216`.

**Guarda provisória da Ilha 2:** a ponta da Ilha 2 tem `DB_Exit_AnchorGuard` (`next_island_guard=true`).
- O `DragonBallIsland.build` **não** remove essa guarda.
- Com a Ilha 3 presente, é preciso copiar `NarutoIsland:224-228`: `if SS:FindFirstChild('IlhaShadowGarden') then destruir next_island_guard end`.
- Âncora de chegada: `ISLAND_NEXT_ANCHOR_ShadowGarden` em (-579,23, 28,2, 650,73), frente (-0,9205, 0, -0,3907), largura 18, vão livre 22 (`conexao_roblox.json`).

---

## 2. O que o código antigo do Shadow Garden constrói hoje

- **Despacho:** `IslandWorld:93`: `if area.id==4 and ServerStorage:FindFirstChild('ShadowGardenKit') then return ShadowGarden.build(...)`.
- **O `ShadowGardenKit` não existe.** A `ServerStorage` só tem `ShadowGardenPreviewKit {PreviewOnly=true}` (`tree_serverstorage:341`), e `ShadowGardenIsland.build` rejeita `PreviewOnly` (`ShadowGardenIsland:85`).
- **Então, no Play, a área 4 é a ilha procedural genérica** do `IslandWorld`:
  - paleta 4 (`:14`);
  - ramo `id==4` (`:255-287`): Catedral das Sombras, torres, arcadas, colunas em ruína, torii, eclipse;
  - **sem alcova de invocação** (`:377`, "sem gacha no Jardim das Sombras");
  - `PortalDeProgressao` com `NextAreaId=5` (`:394-406`);
  - 22 minérios (`:416`);
  - arena do chefe;
  - `BoundsHalfSize` (146, 120, 146) sem `BoundsCenter`, usando o centro do `Config` (0, 0, 1680);
  - sem `RotaPropria`.
  - Com isso, `TravessiaCorredores` abre corredores e passarelas 3 → 4 e 4 → 5, e `Paredes` cria as paredes 4, 5 e 6.
- **`ShadowGardenIsland` + `ShadowGardenLayout`** (código morto):
  - É o antigo "Domínio da Veia Arcana" do Blender: 202 instâncias de 61 assets, 193 colisores e 66 marcadores (61 de minério, mais entry, safe, return, boss e next).
  - O marcador next usa `NextAreaId=5` e a placa diz "GRAND LINE" (`ShadowGardenIsland:75,97`).
  - Tem cachoeiras em Beam, `ShadowWaterRipple` e zonas PedreiraSombria, MinaArcana e Cripta.
  - O layout é outro, a saída é outra e não há invocação. **Não serve para a missão nova.**
- **`ShadowGarden_Review {PreviewOnly}` está no `workspace`**, na raiz, em z ≈ 4993.
  - Tem `DominioDaVeiaArcana` (199 colisões, 58 efeitos, luzes e partículas) e `Minerios_Previa` (61).
  - Vai para o jogo publicado. Deveria ir para a `ServerStorage`.
- **Histórico:** `RevertedShadowGardenProduction_20260926 {Reason="User requested full undo"}` guarda uma produção anterior do SG que foi revertida por completo a pedido do usuário.

**Substituir:**
- A área 4 passa a um `Core.<NovoSG>` com o mesmo contrato do `DragonBallIsland`:
  - atributos `EntryPosition`, `EntryForward`, `SafePosition`, `SafeMaxY`, `BoundsCenter`/`BoundsHalfSize`, `RotaPropria=true`, `GachaPosition` e `NextAnchor*`;
  - retorno `{spawns, boss, returnPad, zonas={lista, bloqueios}}`.
- A linha de despacho nova entra **antes** da `IslandWorld:93`, testando `ServerStorage.IlhaShadowGarden`.

**Manter para rollback:**
- a linha 93 e os módulos `ShadowGardenIsland`/`ShadowGardenLayout`, inertes sem o kit;
- o ramo procedural `id==4`;
- na ServerStorage: `BeforeShadowGarden_20260917` (modelo da Area4 antiga), `GachaSombra_Backup` (`Gacha_sombra` + `AlcovaDeInvocacao`), `ShadowGardenPreviewKit`, `BeforeShadowGardenProduction_20260926` (Core com 42 scripts, Config, PortoesCompra, 21 StarterPlayerScripts);
- o `ShadowGardenWater`, que pode ser reaproveitado via atributo `ShadowWaterRipple`.

**Efeitos de `RotaPropria=true` na área 4:**
- O `TravessiaCorredores` para de abrir corredores e passarelas da 4 (`:89, :144`).
- O `Paredes` deixa de construir a parede 5 (`:307-308`). A parede 4 (z = 1470, saída do DS procedural) continua existindo, inofensiva.

---

## 3. Invocação (summon)

### Fluxo genérico
1. **Máquina:** `workspace.Gachas.Gacha_<tema>`, com `PadGacha` e atributos `AreaId`/`Tema`.
2. **Prompt:** o `Main:427-468` cria o `ProximityPrompt 'GachaPrompt'` ("Invocar", alcance 14) no `cabinet_body`, ou no pad, e dispara `R.AbrirGacha(areaId)`.
   - O mesmo trecho mantém um **laço no servidor** que muda a `Transparency` do pad a cada frame (`Main:459-465`); ver desempenho.
3. **Servidor:** `GachaService.transaction` exige:
   - `Config.Gachas[areaId]`;
   - `perfil.areas[areaId]`;
   - HRP a até 60 do `PadGacha` (`GachaService:64-69`).
4. **Cliente:** `ctx.nearBanner` exige até 58 do pad (`ExpeditionClient:684-695`).
5. **UITravel 'gacha':** leva o jogador para `PadGacha.Position + (0, 4, 0)` (`ExpeditionTravel:59-68`).
6. **Menus:** só listam banners com `Config.Gachas[id]` (`Menus:400`); `BannersConfig` idem.

### Motor invisível (Naruto e DB)
Implementado em `NarutoIsland:136-177` e `DragonBallIsland:111-148`:
- gira a máquina para o pad encarar `SUMMON_PlayerPosition`;
- põe o `cabinet_body` em `SUMMON_Interact` + 2,5 Y;
- faz raycast do piso e afunda o pad 10×0,25×10 para piso − 0,9, com CanCollide, CanTouch e CanQuery falsos;
- deixa todas as outras BaseParts com `Transparency=1` e sem colisão, e desliga luzes e partículas;
- põe `BillboardGui.MaxDistance=45` e a `PlacaGacha` em Interact + 13;
- marca o atributo `MotorDaTorre`;
- devolve `GachaPosition` = XZ do pad, piso + 3,5.

O prompt "Invocar" fica no gabinete invisível, dentro do portal da torre.

### O que falta para a área 4 ter invocação
Hoje a área 4 **não tem gacha por design**:
- `EconomiaV31:195-196`: `GACHA_MUNDO[4]=false`, `GACHA_GIRO[4]=0`;
- `PETS_POR_AREA` não tem `[4]` (`Config:342, 347-392`);
- não existe missão "invocar" para a área 4 (`Config:695-696`);
- `workspace.Gachas` não tem `Gacha_sombra`. Ela está em `ServerStorage.GachaSombra_Backup` e, só como preview de UI, em `ReplicatedStorage.PreviewModelos.Gacha_sombra`.

Para funcionar:
1. **Decisão de economia:** ligar `GACHA_MUNDO`/`GACHA_GIRO` do SG (no índice 4 com a opção B, ou no 3 com a opção A), regenerando o EconomiaV31.
2. **Pets do SG:** `PETS_POR_AREA[id]` com modelos em `ReplicatedStorage.PreviewModelos.Pets[id]`, `Config.PetArte` (busto e corpo) e `BannersConfig.TEXTOS[id]`.
3. **Máquina:** devolver `Gacha_sombra` a `workspace.Gachas`, com `PadGacha {AreaId=<id SG>, Tema='sombra'}`.
4. **Builder:** chamar `invocacao()` com os marcadores `SUMMON_Interact`/`SUMMON_PlayerPosition`, igual ao DB.

Sem o item 1, a torre da missão (`REFERENCIA` item 6) fica **só decorativa**.

---

## 4. Iluminação: noite ao luar só na área 4

- **O `AreaAtmosphere` já faz isso.** É um LocalScript e o único dono do `Lighting` em runtime. Fora ele, só o `ExpeditionClient:49` cria um blur.
- **Perfil `[4] ShadowGarden`:**
  - ClockTime 0,6;
  - Ambient e OutdoorAmbient lilás, Atmosphere roxa;
  - Tint, Contrast −0,07, Saturation −0,16, Exposure +0,2 (`AreaAtmosphere:16`).
- **Aplicação:** a cada mudança de `CurrentAreaId`, com tween de 1,6 s (`:23-41`). Liga `ShadowGardenMood=true` (`:38`) e chama `Som.setArea`.
- **Por ser local, não afeta outros jogadores** nem outras áreas. Ao voltar, retorna ao perfil daquela área ou ao `base` capturado no início (`:9-10`).

### Limites atuais
1. **Não toca em:**
   - `Sky` (`CeuAnimeSky`): lua e estrelas;
   - `Bloom` e `SunRays`;
   - `EnvironmentDiffuseScale`/`EnvironmentSpecularScale`, `ColorShift_Top`, `FogColor`/`FogEnd`, `GeographicLatitude`.
   - Também força `Brightness=2` em todo perfil.
2. **O tween de ClockTime vai de 13,5 para 0,6 decrescendo.** Na travessia DB → SG, o céu passa rapidamente por meio-dia e amanhecer ao contrário.
   - Para um anoitecer natural, interpolar com "wrap": 13,5 → 24,6, ou lerp próprio.
3. **A troca acontece na ponte**, porque o `IslandTravel` decide a área por região com histerese (`IslandTravel:43-49`). Da ponte, a ilha vizinha também fica "noturna", já que a luz é global no cliente. Isso é aceitável.

### O que acrescentar (sem quebrar as outras áreas)
- **Opção preferida:** estender o `profiles[4]` (`AreaAtmosphere:16`) com campos opcionais (`bloom = {...}`, `sunrays = 0`, `envDiffuse`, `latitude`) e aplicá-los em `apply()` (`:30-37`), só quando existirem. As demais áreas não mudam.
- **Céu:** um LocalScript separado, reagindo a `player:GetAttribute('ShadowGardenMood')`, troca o `Sky`. Ele clona `ReplicatedStorage.CeuShadowGarden`, com lua grande e muitas estrelas, para o `Lighting` e devolve o `CeuAnimeSky` ao sair. Como o `AreaAtmosphere` não toca no Sky, não há conflito de dono.
- **Luzes da ilha:** PointLights dentro de `workspace.Areas` já são desligadas além de 200 studs e oscilam em 2% pelo `AmbienteFolha:15,32-34`. Isso **não** vale para SpotLight e SurfaceLight.
- **Base de comparação:** DB tem 33 luzes e Naruto 33.

---

## 5. Tempo e horários (dungeon às XX:00 e XX:30)

**Não existe agendamento por relógio de parede.**
- O chefe usa intervalo de `os.clock` por servidor, entre 9 e 13 min (`BossService:22, 61, 145-163`; `EconomiaV31:208-209`).
- O Daily usa dia UTC: `PlayerData.diaUTC` (`PlayerData:535`) e o contador `86400 - os.time()%86400` (`Menus:844`).
- Boosts usam `os.time()` (`PlayerData:527-533`).

**Como o cliente lê o relógio do servidor:** `workspace:GetServerTimeNow()`, em epoch UTC sincronizado:
- `MiningSwing:45,60`;
- `Mineracao:304,338`, que carimba o golpe no servidor;
- `AudioWorld:28`;
- `AutoMinerar:299`;
- `LocomocaoBigAxe:358`;
- `VFX_Lobby_Forja_Client:412`, onde todos os clientes veem a mesma fase.

**Padrão proposto:**
- No servidor, um laço de 1 s no estilo do `BossService.iniciar`.
- Cálculo: `slot = math.floor(workspace:GetServerTimeNow() / 1800)`; `abre = slot * 1800`; `fecha = abre + JANELA`.
- Publicar `Area<SG>:SetAttribute('DungeonAbreEm', abre)`, `'DungeonFechaEm'` e `'DungeonAberta'` (bool). Atributos replicam e sobrevivem ao streaming.
- No cliente, contagem regressiva com `attr - workspace:GetServerTimeNow()`. Sem RemoteEvent de tick.
- **Não usar `os.clock`** para isso: ele é local de cada servidor.
- XX:00 e XX:30 em UTC coincidem com XX:00 e XX:30 em fusos de hora cheia ou meia hora.

---

## 6. Ganchos de áudio e convenções de VFX para reaproveitar

### Áudio
- **Música:** `SomJogo.setArea(id)` é chamado pelo `AreaAtmosphere:39`.
  - `AudioCatalog.Music[4]` = "The Forgotten Crypt" (131334832939011, vol 0,20) (`AudioCatalog:110`).
  - Os assets estão em `ReplicatedStorage.AreaMusicAssets`.
  - Crossfade em 2 slots (`SomJogo:244-267`).
- **Leito regional:** a área 4 usa a família `energy` a 0,06; as demais usam `wind` a 0,10 (`SomJogo:295-296`).
- **Loops:** orçamento de 4 (1 região + 3 fontes mais próximas) (`AudioCatalog:5`; `SomJogo:269-325`).
- **Emissores automáticos** por nome, via `AudioWorld:14-23`:
  - Model `PortalDeProgressao` → energy, alcance 34;
  - `Texture 'FluxoCachoeira'` com BasePart pai → água, alcance 52;
  - `hot_billet` e `ForgeChimney` → fogo.
  - Para outros casos, `Som.RegisterEmitter(key, família, pos, alcance, vol)`.
- **Famílias de ambiente disponíveis:** fire, wind, water, energy (`AudioCatalog:13`). Sino da dungeon ou grilos noturnos exigem um asset novo em `Catalog.Assets`, com pré-carga (`SomJogo:71-100`).
- **Eventos prontos:** `portal_saida`/`portal_chegada` (usados pelo `IslandTransition`), `area_nova`, `invocar_inicio`, `summon_reveal`.

### VFX (cliente)
| Tag ou atributo | Contrato | Quem anima |
|---|---|---|
| `IlhaVFX` (ParticleEmitter) | `Dist` (raio de corte, padrão 260), `Rate0`. Nome `Portao_<Key>` baixa para 0,8 quando liberado | `ILHAS_Cliente:81, 86-102`, liga e desliga 2×/s |
| `IlhaPulso` (BasePart) | `Cor0` (Color3) | `ILHAS_Cliente:105-121`, 30 Hz, a menos de 360 |
| `PortaoCompra` | `gate`, `gate_part` (barrier/lock/openglow/lockcol), `t0` | `PortoesCompra` + `ILHAS_Cliente:122-134` |
| `IlhaMovel` | `movel_de` (nome do Model ancestral, ex. `ILHA_NARUTO`), `cf0_rel`, `pivot_rel`, `axis_rel`, `rpm`, `bob`, `rate` | `ILHA_NARUTO_Movel` (RenderStepped, **sem culling**) |
| `FolhaAmbient` (emitter), `IslandSway`, `IslandBird`, texturas `FluxoCachoeira`/`OndasDaIlha`/`AguaLinhas`/`AguaSombra`/`EspumaPoco`, `OndaAnel`, `CorrenteFolha` | ver `AmbienteFolha:5-15` | `AmbienteFolha`, 15 Hz, corte 200, respeita `LobbyVFXEnabled` |
| `ShadowWaterRipple` (BasePart) | a CFrame base é capturada no registro | `ShadowGardenWater`, 20 Hz, corte 190 |
| `Ore` + `OreType`/`Rarity` | modelos `minerio_sombra_*` já têm `OreType=ShadowMana` | `OreVFX_Setup` (servidor) → `OreVFX.Attach` |
| `FORJA_*` | modelo de referência: PreRender + `BulkMoveTo` só perto da câmera, pulsos a 20 Hz, luzes a 15 Hz, emissores a 2 Hz, `ReducedMotion`, `VFX_Pause` | `VFX_Lobby_Forja_Client:16-18, 405-600` |

**Recomendação:**
- emissores do SG com `IlhaVFX` + `Dist`;
- cristais com `IlhaPulso`;
- portões com `PortaoCompra`;
- nomear o Model da ilha de forma fixa (ex. `ILHA_SHADOWGARDEN`) se usar `IlhaMovel`.

---

## 7. Scripts de cliente com custo e medições existentes

### Riscos, do mais ao menos relevante
1. **`ILHA_NARUTO_Movel` (RenderStepped):**
   - chama `CS:GetTagged('IlhaMovel')` todo frame, o que aloca uma tabela;
   - faz `FindFirstAncestor` + `GetPivot` por peça e por frame;
   - não corta por distância e move peça por peça, sem `BulkMoveTo`.
   - Cresce linearmente com cada ilha, para todos os jogadores. Se o SG usar `IlhaMovel`, convém cachear e cortar por distância, no padrão FORJA.
2. **`AmbienteFolha`:** percorre **todas** as entradas a 15 Hz, inclusive toda PointLight de `workspace.Areas`, e grava `Enabled`/`Brightness` em cada tick. Cresce com as luzes do SG.
3. **Servidor, `Main:354-360` e `Main:459-465`:** laços `while … task.wait()` mudam a `Transparency` do pad da loja e de cada `PadGacha` todo frame. Isso vira replicação contínua. Os pads de Naruto e DB estão afundados e continuam sendo animados.
4. **`ILHAS_Cliente`:** 30 Hz sobre pulsos e barreiras, e 2 Hz sobre emissores. Faz só checagem de distância, com custo baixo.
5. **Varreduras completas:** `IslandVisibility`, `AudioWorld` e `ShadowGardenWater` fazem `workspace:GetDescendants()` no início mais `DescendantAdded` global. É custo pontual; na troca de área, o `IslandVisibility` é O(peças).
6. **Outros laços contínuos:** `PetsSeguidores` (RenderStepped), `MineracaoVisual` (BindToRenderStep), `AutoMinerar` (Heartbeat), `LocomocaoBigAxe` (IK por personagem), `SomJogo` (Heartbeat), `PlayerTitles` (Heartbeat).
7. **Scripts que se desligam sozinhos:**
   - `LobbyVida` espera `LobbyRenovado` e `PortaisAmbiente` espera `LOBBY_MURIM`. Nenhum dos dois existe no workspace, então ambos saem após 30 s.
   - `SakuraEffects`, `AmbienteLobby` e `ILHA_NARUTO_Cliente` estão desabilitados (`_INDEX.tsv`).
8. **Peso morto no workspace:**
   - `ShadowGarden_Review` (PreviewOnly);
   - `Yona VFX Pack`;
   - cerca de 30 peças de teste com decal em (480–604, 296, −612).

### Medições existentes
- **Ilha 1** (`ilha_naruto/INTEGRACAO_JOGO.md`, "Colisão e desempenho"):

  | Medida | Antes (Konoha) | Depois (Naruto) |
  |---|---|---|
  | Instâncias da Area1 | 9.192 | 4.154 |
  | Parts | 4.921 | 1.386 |
  | MeshParts | 319 | 773 |
  | Luzes | 37 | 33 |
  | Render CPU / GPU (ms/frame) | 11,9 / 5,7 | 7,8 / 4,4 |
  | Física por passo (ms) | 0,107 | 0,005 |
  | FPS | 60 | 60 |

  - 17 emissores `IlhaVFX` (`Dist` entre 140 e 700).
- **Ilha 2** (`ilha_dragonball/INTEGRACAO_JOGO.md`):
  - 553 MeshParts, 446 mil tris (limite 480 mil), 1.521 colisões simples, 33 luzes;
  - com as duas ilhas visíveis: 787 + 975 MeshParts;
  - **sem medição em ms.**

**Orçamento sugerido para o SG**, seguindo o DB:
- até 480 mil tris e cerca de 600 MeshParts;
- colisão só com Parts simples;
- até 35 luzes;
- até 20 `IlhaVFX` com `Dist`;
- medir Render CPU/GPU no mesmo ponto e com o mesmo método da Ilha 1.
