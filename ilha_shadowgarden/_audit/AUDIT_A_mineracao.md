# AUDIT A — Mineração, spawn de minérios e contrato do builder de ilha (antes da Ilha 4 Shadow Garden)

Data: 2026-09-28. Fonte: scripts exportados em `_audit/scripts/` (lidos linha a linha) e árvores `_audit/tree_*.txt`.
Referência de contrato: `ilha_dragonball/INTEGRACAO_JOGO.md` e `Core.DragonBallIsland`.

Abreviações de arquivo (todos em `_audit/scripts/`):

| Sigla | Arquivo |
|---|---|
| **MAIN** | `ServerScriptService.Core.Main.server.lua` |
| **MIN** | `ServerScriptService.Core.Mineracao.module.lua` |
| **SPW** | `ServerScriptService.Core.SpawnMinerio.module.lua` |
| **AB** | `ServerScriptService.Core.AreaBuilder.module.lua` |
| **IW** | `ServerScriptService.Core.IslandWorld.module.lua` |
| **ECO** | `ServerScriptService.Core.Economia.module.lua` |
| **BOSS** | `ServerScriptService.Core.BossService.module.lua` |
| **NAR** | `ServerScriptService.Core.NarutoIsland.module.lua` |
| **DBI** | `ServerScriptService.Core.DragonBallIsland.module.lua` |
| **SGI** | `ServerScriptService.Core.ShadowGardenIsland.module.lua` |
| **SGL** | `ServerScriptService.Core.ShadowGardenLayout.module.lua` |
| **TRV** | `ServerScriptService.Core.IslandTravel.module.lua` |
| **CFG** | `ReplicatedStorage.Config.module.lua` |
| **EV31** | `ReplicatedStorage.EconomiaV31.module.lua` |
| **GEO** | `ReplicatedStorage.MiningGeometry.module.lua` |
| **VFX** | `ReplicatedStorage.OreVFX.module.lua` |
| **AUTO** | `StarterPlayer.StarterPlayerScripts.AutoMinerar.client.lua` |
| **MV** | `StarterPlayer.StarterPlayerScripts.MineracaoVisual.client.lua` |
| **SGW** | `StarterPlayer.StarterPlayerScripts.ShadowGardenWater.client.lua` |
| **VIS** | `StarterPlayer.StarterPlayerScripts.IslandVisibility.client.lua` |

---

## 1. A cadeia de mineração completa

### 1.1 Boot (ordem)
`MAIN:28` roda `AreaBuilder.construir()`. Depois `IslandTravel.start()` (`MAIN:29`), `Mineracao.iniciar(IgnisService)` (`MAIN:30`) e `BossService.iniciar(Mineracao)` (`MAIN:32`).

`AB.construir` (`AB:380-492`) faz o seguinte:
- apaga `workspace.Areas` (`AB:382-383`). A pasta `Areas` que aparece em `tree_workspace.txt`, com Area2..6 na grade antiga de 1600, é **snapshot de Edit, obsoleta**, e é refeita em runtime;
- para cada área cria `Areas.AreaN` (Model, atributo `AreaId`) e chama `IslandWorld.build(mod, area)` para as áreas 1 a 6 (`AB:397`);
- depois cria `AreaN.Rochas` (`AB:422`), o pool de pontos (`AB:424-440`), os minérios iniciais (`AB:441-454`), a arena do chefe (`AB:474`) e o pad `VoltarLobby` (`AB:479-487`).

`MIN.iniciar` (`MIN:358-370`) liga o `ClickDetector` de todo `BasePart` com `HPMax` sob `workspace.Areas`.

### 1.2 Como o minério é escolhido (tipo/variante)
- **Tipos** (`CFG:32-46`): `comum`, `incomum`, `raro`, `epica`, `lendaria`.
  - `raro` usa o modelo `incomum` e `lendaria` usa o modelo `epica`; os dois ganham cor própria (`variante.cor`).
  - `hp` relativo vem de `EV31.HP_REL`: 1 / 3 / 8 / 20 / 50, chefe 2000.
  - Também vêm de EV31: `peso`, `espaco`, `hatChance` e `hatSorte`.
- **HP por área** (`CFG:623-636`): `a.hp[v] = EV31.HP_COMUM[área] × HP_REL[v]`. Super (chefe) = `HP_COMUM × 2000`.
- **Servidor novo** (`AB:442-454`) nasce com `Config.SPAWN.inicial` = `{incomum=8, raro=3, epica=1, lendaria=0}` (`CFG:508`). O resto é `comum`, até `min(Config.SPAWN.minerios = 70, #pontos-2)` (`AB:447`, `CFG:509`).
- **Depois disso não há sorteio** (tudo por "energia", `CFG:482-524`):
  - cada quebra de variante `v` põe `energiaPorQuebra[v] = HP_REL[v]` na barra da variante de cima (`SPW:168-186`);
  - `barras[v_i] = {vem=v_{i-1}, custo=quebras×hp/nascem, porVivo=0.05}` (`CFG:520-523`);
  - com a barra cheia, `processarEnergia` (`MIN:213-267`) amplifica o minério de nível abaixo mais próximo de quem quebrou (`candidatoAmplificar`, raio 3D 70, `MIN:197-209`, `CFG:498`). Sem candidato, cria um novo em ponto livre.
- **Efeitos** `dourado` e `arcoiris` (`CFG:499-502`, `SPW:176-196`) aplicam `Highlight`, `Sparkles` e uma etiqueta (`AB:198-229`). Pagam moedas extras na quebra (`MIN:150-155`).
- `Config.varianteSorteada` (`CFG:790-799`) só é usada no caminho legado sem builder (`AB:456-470`).

### 1.3 Onde nasce (SpawnMinerio)

**`SPW.registrarPontos(area, originais, ignorar, evitar, zonas)`** (`SPW:30-96`), chamada em `AB:439`:
- `originais` = `custom.spawns[].pos` + `custom.boss` (`AB:427-429`).
  - Entram **sem checagem nenhuma**, só com `longe(p, 7)` (`SPW:62-64`).
  - Por isso NAR/DBI pré-filtram os marcadores `ORE_*` com bloqueios e caixa 7×8×7 livre (`NAR:266-277`, `DBI:249-259`).
- `ignorar` = `{rochas}`. Os `RaycastParams` e `OverlapParams` usam `RespectCanCollide = true` (`SPW:32-39`). Resultado: **só partes com CanCollide contam** (visual com CanCollide=false é ignorado, colisor invisível conta).
- `evitar` exclui um raio horizontal de **16 studs** (`SPW:51-53`) em volta de:
  - `EntryPosition` e `GachaPosition`;
  - `returnPad`;
  - toda peça com `NextAreaId` ou `Destino` (`AB:431-438`).
- **Com `zonas`** (caminho de NAR/DBI), `SPW:65-85`, para cada zona:
  1. Grade de **8 studs** com jitter de ±2 e margem de 4 studs.
  2. Raycast de `z.centro + (x, **+12**, z)` para baixo, com comprimento **30** (`SPW:76`).
  3. Aceita se `Normal.Y > 0.85` **e** `hit.Y` está na **janela (centro.Y − 1, centro.Y + 5)** **e** o ponto não cai em nenhum bloqueio circular XZ (`SPW:66-70`, `77`).
  4. Depois vem `aceitar`: caixa **7×8×7** em `pos + (0,5,0)`, ou seja, de pos+1 a pos+9, sem partes com colisão, e `longe(pos, 7)` (`SPW:56-60`).
  5. O teste de altura ±3 é inócuo aqui (compara o ponto consigo mesmo).
- **Sem `zonas`** (caminho legado, é o que a área 4 usa HOJE), `SPW:86-93`:
  - grade de ±124 em volta de `area.centro`;
  - raycast de `chaoY + 40` para baixo, comprimento 70, em que `chaoY` = mediana dos originais (`SPW:42-45`);
  - aceita se o acerto estiver a até ±3 de `chaoY`.
- O pool fica em `pontos[area.id]` (`SPW:83/94`), **um pool por área** (não existe por zona).

**`SPW.posicaoLivre(areaId, pastaRochas, ignorarGrupo, ehChefe)`** (`SPW:100-140`):
- embaralha o pool e devolve o primeiro ponto com folga ≥ 0;
- a folga é medida contra cada `Hitbox` da pasta, com `distanciaMin = 9` e `distanciaChefe = 20` (`CFG:510-511`);
- sem ponto com folga, devolve o de maior folga. **Se o pool for pequeno, os minérios empilham**; o comentário em `NAR:281-284` explica por que o pool precisa sobrar;
- para chefe, exige ainda a caixa **16×14×16** em `p + (0,8,0)` (de p+1 a p+15) sem nada com colisão (`SPW:131-133`). Se nenhum ponto couber, devolve `nil` e o chefe usa `arena.pos = custom.boss` (`AB:367`, `AB:474`).

**Criação** `criarRocha` (`AB:231-351`):
- clona `ServerStorage.Modelos.minerio_<tema>_<modelo>` (`CFG:833`).
  - Para `tema == "sombra"`, tenta antes o modelo autoral por variante: `minerio_sombra_raro` e `minerio_sombra_lendaria` (`AB:235-238`).
- escala `5.2` para minério e `6.5` para chefe nas áreas 1 a 6 (`AB:255`). Raro ×1.08 e lendária ×1.25 (`AB:254`).
- visual: `CanCollide=false`, `CanQuery=true` (`AB:257-265`).
- `Hitbox` invisível (`CanCollide=false`, `CanQuery=true`) cobrindo `massa_minerio*` e `plinto` (`AB:299-318`).
- atributos (`AB:320-326`): `AreaId`, `SpawnPos`, `Tema`, `Variante`, `HPMax`, `HP` e `Chefe`. Mais `OreType` e `Rarity`, que ligam o `OreVFX.Attach` (`AB:329-336`).
- `ClickDetector` com alcance 30 (55 no chefe) (`AB:338-340`) e etiqueta `Vida` (`AB:42-142`, desligada até o 1º golpe).

### 1.4 Golpe (validação do remote)
Remote `Golpear` (`MAIN:208-214`) checa:
- `typeof Instance`, `IsA BasePart`, `Name == "Hitbox"`;
- atributo `HPMax` presente;
- `IsDescendantOf(workspace)`.

Depois `MIN.golpear` (`MIN:281-346`) valida:

| Checagem | Linha | Detalhe |
|---|---|---|
| `Geometry.valid` | `GEO:45-48` | Hitbox com `CanQuery` e HP > 0 |
| **Dentro de `workspace.Areas`** | `MIN:283` | minério fora de `Areas` é ignorado em silêncio |
| Tool `Picareta` + `canReach` | `MIN:284`, `GEO:49-62` | distância root → ponto de contato ≤ **3.35** (`Reach`) + raycast de linha de visada com `RespectCanCollide` |
| Cooldown | `MIN:287-289` | `intervalo` da picareta − 0.06 e um golpe pendente por vez |
| **Posse da área** | `MIN:290-293` | `perfil.areas[AreaId]`. **Não** compara com `CurrentAreaId` |
| Mochila cheia | `MIN:295-299` | AutoSell se tiver o passe; senão aviso e oferta (`MIN:270-278`) |

O dano só é aplicado depois de `ImpactTime + 0.05` (≈ 0.33 s), com revalidação de tool, alcance e mochila (`MIN:306-312`):
- `dano = PlayerData.dano(perfil)`, que é (base + hats) × mult. da picareta × (1 + pets);
- `HP -= dano` (`MIN:314-316`);
- no chefe, `BossService.aplicarDano` (`MIN:317-318`);
- barra, `OreVFX.Hit`, `AnimarPicareta` (impacto) e `FeedbackMina "golpe"` (`MIN:324-340`);
- `ECO.registrarGolpe` (`MIN:301`) só marca o jogador como "ativo" (`ECO:15-29`); isso escala o HP do chefe.

**Não existe dono do minério:** qualquer jogador com a área comprada bate em qualquer minério.

### 1.5 Quebra e recompensa (`MIN:111-190`)
- **Chefe:** `BossService.morreu` + VFX + `esconder`, e o grupo é destruído em 2 s (`MIN:116-124`).
- **Minério normal:**
  1. Se a mochila estiver cheia no momento da quebra, **o HP volta para `HPMax`** (`MIN:132-138`), o que dá um HP ≤ 0 transitório.
  2. `perfil.mochila[Config.idMinerio(Tema, Variante)] += 1`, com o id `"<tema>_<variante>"` (`MIN:144`, `CFG:808`).
  3. `SpawnMinerio.quebrou(areaId)` (energia) e `BossService.quebra(areaId)` (contador do chefe) (`MIN:147-148`).
  4. Missões `minerar` e `epico` (`MIN:156-159`), chance de hat do tema (`MIN:161-166`) e `FeedbackMina "quebrou"` (`MIN:168`).
  5. `esconder`: transparência 1, `CanQuery=false`, ClickDetector desligado (`MIN:90-108`).
- **Venda:** `IgnisService.vender` usa `Config.infoMinerio(id).valor = hp × MOEDA_POR_HP (0.4)` (`CFG:630`, `817-830`).

### 1.6 Renascimento (`MIN:174-189`)
- A pasta de destino é `pasta = (grupo.Parent, ou o pai dele se o nome for "Rochas"):FindFirstChild("Rochas")` (`MIN:175-177`).
- Depois de `RESPAWN_ROCHA = 1.2 s` (`CFG:783`):
  - se o minério era `comum`, `AreaBuilder.novoMinerio(area, pasta, grupo, "comum")` o recria em **outro ponto livre do pool da área** (`AB:355-359`);
  - destrói o grupo;
  - chama `processarEnergia(area, pasta, perto)`.
- **Se `pasta` for nil, o `task.delay` retorna antes de tudo** (`MIN:181`): não há respawn nem energia, e o grupo escondido **não** é destruído.

### 1.7 Chefe global (BOSS)
`BOSS.iniciar` (`BOSS:142-164`) roda um laço a cada 2 s por área. O chefe nasce (`B.nascer`, `BOSS:49-72`) quando **não há chefe vivo** e **há alguém com `CurrentAreaId` da área**, em dois casos:
- `quebras ≥ 500` (`EV31.CHEFE_QUEBRAS_SERVIDOR`) e já passaram ≥ 9 min;
- ou já passaram ≥ 13 min.

Detalhes da luta:
- `hpLuta = hp.super × max(1, ativos) / hpEscalaJogadores`;
- a posição sai de `AreaBuilder.novoChefe`, com `posicaoLivre(ehChefe)`, e o fallback é `custom.boss` (`AB:364-369`);
- o chefe nasce **na mesma pasta `Rochas` da área**;
- recompensa por contribuição (`BOSS:88-125`): quem causou ≥ 2 % do HP da luta leva tudo;
- também nasce pelo produto `invocar` (máx. 2 vivos + fila, `BOSS:128-140`) e pelo debug `chefe` (`MAIN:525-526`).

---

## 2. Contrato do builder de ilha (`M.build(parent, area)`)

`parent` = `workspace.Areas.AreaN` (Model já com `AreaId`, `AB:389-390`); `area` = entrada de `Config.Areas`. O builder clona a ilha para dentro de `parent`.

### 2.1 O retorno (lido por AB:424-487)
```lua
return {
  spawns    = { {pos=Vector3}, ... },   -- OBRIGATORIO (tabela; AB:428 itera). So POSICAO: variante vem do SpawnMinerio.
  boss      = Vector3,                  -- ponto extra do pool (AB:429) + fallback do chefe (AB:474, AB:367)
  returnPad = Vector3,                  -- pad VoltarLobby (AB:480; Touched -> lobby, MAIN:308-315). Sem ele o pad cai em area.centro (errado p/ ilha deslocada)
  zonas = { lista = { {nome=, centro=Vector3(Y = piso), tamanho=Vector3(x,0,z)} , ...},
            bloqueios = { {pos=Vector3, raio=n}, ... } },   -- recomendado; sem zonas cai no caminho legado SPW:86-93
}
```
Retornar `nil` faz o AreaBuilder cair no laço legado de rochas aleatórias em `area.centro` (`AB:455-470`), com minérios flutuando.

### 2.2 Atributos em `parent` (quem lê)

| Atributo | Obrigatório? | Leitor(es) | Observação |
|---|---|---|---|
| `EntryPosition` | **sim** | `MAIN:283` (portões `NextAreaId`, discos do lobby), `TRV:18`, `AB:432` (evitar), `ExpeditionTravel:73` | posição do **root** (piso + ~3.5, como `NAR:239`/`DBI:201`) |
| `BoundsHalfSize` | **sim** | `TRV:25`, `VIS:23` | região da área. `inside` usa **Y absoluto**: `pos.Y > -12` e `pos.Y < half.Y + 5` (`TRV:36`) |
| `BoundsCenter` | **sim para a SG** | `TRV:27`, `VIS:25` | sem ele a caixa fica centrada em `Config.centro` = (0,0,1680) (`CFG:771-781`). A SG nova encosta na âncora da Ilha 2, perto de (-560, 32, 655). Sem `BoundsCenter`, o IslandTravel "recupera" o jogador e a visibilidade quebra |
| `EntryForward` | recomendado | `TRV:84` | orientação na chegada |
| `SafeMaxY` | **sim se houver piso acima de centro.Y + 18** | `TRV:173-174` | sem ele, a posição segura só é gravada abaixo de `BoundsCenter.Y + 18` |
| `RotaPropria` = true | **sim** | `TravessiaCorredores:89`, `:144`; `Paredes:308` | sem ele, `abrirFaixa` **destrói colisores invisíveis** nas faixas Z de `area.centro` (`TravessiaCorredores:69-80`) |
| `TravessiaKeep` (em cada `COL_*`) | sim | `TravessiaCorredores:71`, `PortoesDeIlha:164` | como `NAR:252-257` e `DBI:217-219` |
| `GachaPosition` | não (área 4 não tem gacha: `EV31.GACHA_MUNDO[4] = false`) | `AB:432` | |
| `NextAnchor*` | para a ilha 5 | documental (DBI:209-216) | |
| `WorldRevision`, `OrePontos*`, `SafePosition` | não | ninguém lê `SafePosition` como atributo | só QA |
| `parent.ModelStreamingMode = PersistentPerPlayer` | **sim** | `TRV:65-76` (AddPersistentPlayer da área atual + vizinhas) | |

Outros pontos do contrato:
- **Peça com `NextAreaId=N`:** o `Core.Main` põe o prompt "Viajar" nela no boot (`MAIN:287-305`); se a área estiver bloqueada, abre a compra.
- **Portão de compra da ilha seguinte (área 5):** a chave em `ILHAS_Cliente` é `OnePiece = 5` (`ILHAS_Cliente:12`).

### 2.3 Como o IslandWorld despacha a área 4 hoje
- `IW:7` faz `require(ShadowGardenIsland)`, que por sua vez faz `require(ShadowGardenLayout)` (`SGI:3`). **O JSON de 38 KB é decodificado em todo boot**, mesmo sem uso.
- `IW:93`: `if area.id==4 and ServerStorage:FindFirstChild('ShadowGardenKit') then return ShadowGarden.build(parent, area) end`.
- **`ServerStorage.ShadowGardenKit` não existe** (`tree_serverstorage.txt`). Existe só `ShadowGardenPreviewKit` com `PreviewOnly=true`, que `SGI:85` recusaria de qualquer forma.
- **Hoje, portanto, a área 4 é a ilha procedural genérica do IslandWorld** (`IW:98-429`, ramo `id==4` "CatedralDasSombras", `IW:255+`):
  - 22 pontos (`IW:416`) e **sem `zonas`** (usa o caminho legado `SPW:86-93`);
  - `BoundsHalfSize (146,120,146)` sem `BoundsCenter`, no centro (0,0,1680);
  - pad com `NextAreaId = 5` (`IW:403`).

### 2.4 ShadowGardenIsland + ShadowGardenLayout (tentativa antiga)
**O que faz:**
- `SGL` é um JSON gerado pelo Blender com 202 instâncias de 53 assets, 193 colisores, 66 marcadores (61 `ore`, `entry`, `safe`, `return`, `boss`, `next`), paleta e lista de assets.
- `SGI.scene` clona os assets de `ShadowGardenKit`, com **todas as malhas `CanCollide=false` e `CanQuery=false`** (`SGI:56`).
- Cria colisores `Part` invisíveis (`SGI:68-71`). Nos prédios, põe uma caixa "EdificioFechado" **sólida** (`SGI:57-58`), inclusive em `Salao_Sete_Sombras`, o que deixaria o salão maciço.
- Cria luzes, cachoeira em Beam e o atributo `ShadowWaterRipple`, animado por `SGW`.
- `SGI.build` cumpre só parte do contrato:
  - seta `EntryPosition`, `SafePosition` e `BoundsHalfSize (203,160,208)`;
  - cria o pad `NextAreaId=5`;
  - declara 3 zonas: `PedreiraSombria` 110×108, `MinaArcana` e `Cripta` (`SGI:100-104`);
  - **não** seta `BoundsCenter`, `RotaPropria`, `EntryForward`, `SafeMaxY` nem `TravessiaKeep`, e não tem portão de compra (`SGI:84-106`).

**Está em uso?** **Não.** O kit não existe. Sobras vivas:
- `workspace.ShadowGarden_Review` (`PreviewOnly`, ~364×209×394 em z≈4993, com 199 colisores): **carregado no servidor para todos**, fora de `Areas`, então o IslandVisibility não o esconde;
- `ServerStorage.ShadowGardenPreviewKit`;
- o backup `BeforeShadowGarden_20260917`;
- `RevertedShadowGardenProduction_20260926`, desfeito a pedido do usuário.

**Manter / remover:**
- **Manter** (são ganchos da ilha 4 no código compartilhado):
  - `AB:235-238` (modelo autoral por variante para `sombra`);
  - `AB:269` (cor da incomum na área 4);
  - `AB:274` (atributo `ShadowGardenPalette` no template para não repintar raro/lendária);
  - `SGW` **só** se a ilha nova usar `ShadowWaterRipple`.
- **Substituir:**
  - reescrever `Core.ShadowGardenIsland` com o contrato do DBI: fonte `ServerStorage.IlhaShadowGarden` e marcadores `GAMEPLAY_MARKERS`;
  - trocar a condição de `IW:93` para o nome novo, **nunca** reutilizar `ShadowGardenKit`, que ativaria o layout velho e daria assert em malha faltando;
  - **só depois** arquivar `ShadowGardenLayout` em ServerStorage. Hoje `IW:7` depende da cadeia de `require`.
- **Remover do workspace:** `ShadowGarden_Review`, movendo para ServerStorage.

---

## 3. CRÍTICO — mineração DENTRO do salão do castelo (com teto)

### 3.1 O que quebra ou pede cuidado

| Sistema | Onde | Risco indoor |
|---|---|---|
| Pool com zonas | `SPW:76-77` | Raio nasce em **piso + 12** e só aceita acerto em **(piso − 1, piso + 5)**. Qualquer peça **com colisão** entre piso + 5 e piso + 12 (lustre, viga, mezanino, colisor de teto baixo) é atingida antes e **o ponto é perdido**. Mezanino entre piso − 1 e piso + 5 **recebe minério em cima**. Teto (visual) com CanCollide=false é ignorado (RespectCanCollide) |
| Caixa livre | `SPW:58` | 7×8×7 de piso + 1 a piso + 9: **pé-direito livre de colisão ≥ 9** em cima de cada ponto. Colunas e paredes a menos de 3.5 do ponto cortam o ponto |
| Pool sem zonas | `SPW:86-93` | Raio de `chaoY + 40` para baixo: **bate no telhado com colisão** e rejeita tudo dentro do salão. **É obrigatório passar `zonas`** |
| Tamanho do pool | `AB:447`, `SPW:100-140`, `NAR:281-284` | O servidor tenta **70** vivos com 9 studs de distância. Área útil mínima ≈ 70 × 81 × 0.87 ≈ **4.900 studs²** livres, ou seja, **salão com ~75×75 de piso útil** depois dos bloqueios, e pool ≥ 72 (ideal 100+). Menos que isso empilha minério |
| Tamanho visual | `AB:254-255` | Com escala 5.2, o template `minerio_sombra_epica` (bbox ~3×2×3) vira algo como ~15×10×15 (lendária ×1.25). Números de ordem de grandeza, **medir no Studio**. A etiqueta `Vida` fica a `t2.Y × 0.7` acima. Os minérios atravessam paredes (sem colisão), mas o visual pode furar coluna e teto |
| Chefe | `SPW:131-133`, `AB:255` | Caixa 16×14×16 (até piso + 15) com **colisão**. Visual ~6.5 × (4,2,4) ≈ 26×13×26. Com **teto colidível abaixo de ~15**, nenhum ponto do salão cabe e o chefe vai para outro ponto ou para `custom.boss`. Com **teto não colidível**, a checagem passa e o chefe atravessa o teto |
| Auto-caminho | `AUTO:284-313`, `GEO:12-40` | **Anda em linha reta** até o ponto de contato (sem pathfinding). Colunas, móveis e degraus entre minérios travam o personagem; há só a "rede" de 0.25 s (`AUTO:302-311`). `canReach` exige linha de visada sem colisão (`GEO:56-61`) |
| Câmera | Poppercam padrão do Roblox (sem código custom; nenhum script mexe em `CameraMaxZoomDistance`) | A câmera só é empurrada para dentro por peças **opacas (Transparency < 0.25) E CanCollide = true**. Teto de malha com CanCollide=false (padrão do SGI antigo, `SGI:56`) ou colisor invisível **não seguram a câmera**: ela sai por cima e o jogador vê o telhado por fora |
| Seleção do alvo | `AUTO:84-104` | O raio da câmera pula até 6 peças transparentes ou sem colisão, mas **para na primeira peça opaca com colisão**. Câmera fora do teto opaco: clicar no minério é impossível. Teto com `CanCollide=false`: o clique passa, mas não se enxerga nada |
| Shake | `MV:98-118` | Soma até 0.22 stud no `CFrame` da câmera depois do passo de câmera. Em pé-direito apertado pode encostar na parede; é irrelevante com pé-direito ≥ 20 |
| VFX | `VFX:959-1025`, `MV:209-242` | Partículas e luzes não colidem. `VFX_SkyTop` (`VFX:969`) é criado mas não usado (sem beam para o céu). Aura tier 4 = chamas curtas. Sem risco |
| Luz | `AreaAtmosphere:16` | Área 4 = **noite** (`ClockTime 0.6`), `Ambient` roxo. Dentro do salão só `Ambient` + luzes locais iluminam. `sombra_comum` e `incomum` **não ganham PointLight**: `CoresProprias`, sem pintar, `AB:274`, `AB:184-194`. O salão precisa de iluminação própria |
| Visibilidade | `VIS:44-54` | Escreve `LocalTransparencyModifier` em **todo BasePart de `Areas`** quando a área muda. Um cutaway de teto por LTM seria sobrescrito; se precisar, usar `Transparency` local |
| Streaming | `TRV:65-76`, `IW/DBI` `PersistentPerPlayer` | Tudo sob `Areas.Area4` é persistente para quem está na área 4 ou numa vizinha. O salão **tem que ficar sob `Areas.Area4`**, o que também é exigência de `MIN:283` |
| Região/recuperação | `TRV:32-37`, `173-178` | O piso do salão tem que estar dentro de `BoundsCenter ± BoundsHalfSize`, com **Y absoluto entre −12 e half.Y + 5**. Se o piso estiver acima de `BoundsCenter.Y + 18`, é preciso setar `SafeMaxY` |
| Evitar | `SPW:51-53`, `AB:431-438` | Raio de 16 em volta de Entry, NextAreaId e returnPad: não pôr a entrada do salão nem o portão dentro da zona |

### 3.2 Forma mínima e segura (sem sistema novo, só o builder da ilha)
1. **Zona do salão** em `zonas.lista`: `centro.Y = piso do salão` (plano). Se o salão tem degrau, uma zona por nível. `bloqueios` circulares em cada coluna (raio = meia-largura + 5), no trono/altar, na porta e nos degraus. A lista aceita várias zonas: salão + pátio/pedreira externa para completar os 70.
2. **Pool no builder, igual ao DBI:**
   - marcadores `ORE_*` pré-filtrados (bloqueio + caixa 7×8×7), como em `DBI:249-259`;
   - grade hexagonal de 7.5 no piso do salão, com raycast de piso + 12 e `|hit.Y − piso| < 0.5`, como em `DBI:263-281`;
   - meta: ≥ 100 pontos no total.
3. **Pé-direito:**
   - nenhuma peça com colisão entre piso + 0.5 e piso + 12 sobre a zona;
   - teto interno ≥ **24–30 studs** (câmera, visual épico/lendário e caixa do chefe);
   - sem mezanino sobre a zona.
4. **Teto que segura a câmera:** uma casca interna simples (Part opaca, CanCollide=true, CanQuery=true, `CastShadow` à escolha) logo abaixo da malha do telhado. Alternativa: a própria malha com `CanCollide=true` e `CollisionFidelity=Box`. Como fica acima de piso + 12, não interfere no spawn.
5. **Corredores retos** de ≥ 8 studs entre colunas. Não deixar móveis colidíveis dentro da zona.
6. **Chefe:** pôr `boss` (marcador) no centro livre do salão ou num pátio aberto. Com teto ≥ 16 colidível, a checagem 16×14×16 funciona sozinha.
7. **Atributos:** `BoundsCenter`, `BoundsHalfSize` (Y ≥ o piso mais alto + margem), `SafeMaxY` (> piso do salão), `RotaPropria=true`, `TravessiaKeep` nos colisores e `EntryForward`.
8. **Luz:** PointLights ou SurfaceLights no salão (ClockTime da área 4 é 0.6).
9. Opcional, só se o salão não comportar 70 minérios: um atributo por área, por exemplo `AreaN:GetAttribute('MaxMinerios')`, lido em `AB:447` no lugar de `Config.SPAWN.minerios`. É uma linha de código. Não é necessário se houver segunda zona externa.

---

## 4. Minérios TEMPORÁRIOS para uma sala "masmorra" (trial)

### 4.1 O que já dá para reusar SEM mudar nada
- **Criar num ponto fixo com HP próprio:**
  1. `AreaBuilder.novoMinerio(area4, pastaSala, nil, varianteId, posFixa, efeitoId)` (`AB:355-359`). Com `posFixa` não usa o pool.
  2. Em seguida, `hit:SetAttribute('HPMax', x)` e `hit:SetAttribute('HP', x)`. A etiqueta fica desligada até o 1º golpe e `atualizarBarra` corrige o texto (`MIN:64-80`).
  3. Depois, `Mineracao.registrar(hit)` para o ClickDetector. O remote `Golpear` funciona mesmo sem ele.
  4. Mais limpo ainda: expor `criarRocha(..., hpForcado)`, que já existe como parâmetro (`AB:231`, `245`).
- **Golpe, dano, VFX, recompensa, hats e missões** são os mesmos (`MIN:281-346`, `111-172`).
- **Evitar respawn e amplificação:** usar uma pasta **com nome diferente de "Rochas"** e **sem filho "Rochas"**, por exemplo `Areas.Area4.Masmorra_<UserId>`.
  - Em `MIN:175-181`, `pasta` fica `nil` e o delay retorna, o que significa sem respawn e sem `processarEnergia`.
  - `candidatoAmplificar` só varre `AreaN.Rochas` (`MIN:197-209`), então os minérios da sala nunca são amplificados.
  - **Nunca** colocá-los em `Area4.Rochas`: entrariam no respawn aleatório, na amplificação e na ocupação do pool.
- **Detectar "todos quebrados" sem mudar nada:** `hit:GetPropertyChangedSignal('CanQuery')` → `false`. Só o `esconder` faz isso (`MIN:102`). **Não** use `HP <= 0`: com a mochila cheia o HP volta para `HPMax` (`MIN:132-135`).

### 4.2 Limites de hoje (o que força uma extensão mínima)

| Limite | Linha | Consequência |
|---|---|---|
| A sala precisa estar **sob `workspace.Areas`** | `MIN:283` | |
| A sala precisa estar dentro da caixa da área 4 | `TRV:36`, Y > −12 | senão o IslandTravel teleporta o jogador de volta |
| `AreaId=4` exige `perfil.areas[4]` | `MIN:290` | |
| **Sem dono** | | outro jogador pode quebrar os minérios da sala |
| A quebra ainda chama `SpawnMinerio.quebrou(4)`, `BossService.quebra(4)` e missões | `MIN:147-159` | a trial alimentaria a energia e o chefe da ilha |
| **Não há callback** com o jogador que quebrou | | só o `FeedbackMina` para o cliente |
| O grupo escondido **não é destruído** no caminho `pasta == nil` | | o controlador limpa a pasta no fim |
| Mochila cheia bloqueia o golpe | `MIN:296-299` | decidir se a trial dá minério na mochila. O espaço de `sombra_*` é grande: `ESPACO × ESPACO_MUNDO[4]=50`, logo comum = 50 e lendária = 400 |

### 4.3 Extensão mínima proposta (≈ 10 linhas em `Core.Mineracao`, nada duplicado)
```lua
-- topo do modulo
Mineracao.Quebrou = Instance.new("BindableEvent")          -- (rocha, player) para quem quiser ouvir

-- em Mineracao.golpear, logo apos MIN:283
local dono = rocha:GetAttribute("DonoUserId")
if dono and dono ~= player.UserId then return end

-- em quebrar, trocar MIN:147-148 por
if not rocha:GetAttribute("Temporario") then
	SpawnMinerio.quebrou(areaId, varianteId)
	BossService.quebra(areaId)
end

-- em quebrar, depois de esconder(rocha) (MIN:172), antes do bloco de respawn
if rocha:GetAttribute("Temporario") then
	Mineracao.Quebrou:Fire(rocha, player)
	task.delay(2, function() if grupo then grupo:Destroy() end end)
	return
end
```
Opcional em AB: `function AreaBuilder.minerioFixo(area, pasta, pos, varianteId, hp, efeito) return criarRocha(area, pos, Config.variantePorId(varianteId), false, pasta, efeito, hp) end`.

**Controlador da trial** (módulo novo, só orquestra):
1. Cria `Areas.Area4.Masmorra_<UserId>`.
2. Para cada marcador da sala, chama `novoMinerio` ou `minerioFixo` e seta `Temporario=true`, `DonoUserId` e HP.
3. Chama `Mineracao.registrar(hit)` e conta os minérios.
4. Ouve `Mineracao.Quebrou`: quando `restantes == 0`, paga o prêmio e destrói a pasta.
5. Timeout e `PlayerRemoving` também limpam.

Missões e hats continuam valendo; se não for o desejado, basta pular `progredirMissao` e o hat sob o mesmo atributo.

**Salas por jogador:** se a sala física for compartilhada, as instâncias se sobrepõem. O `DonoUserId` evita roubo, mas não sobreposição visual. Use uma sala por instância, ou posições deslocadas dentro da caixa da área 4.

---

## 5. Área / tema / minérios da Shadow Garden

**Área e tema:** `id = 4`, `tema = "sombra"`, nome **"Jardim das Sombras"** (`CFG:619`). Cor do tema `(150,90,230)` (`CFG:24`).
- Custo do portal: `EV31.PORTAIS[4] = 2.500.000`.
- `HP_COMUM[4] = 198.000` (`EV31:6`).
- `ESPACO_MUNDO[4] = 50`.

**Itens da mochila** (`CFG:808`) e HP (`CFG:629`):

| Item | HP |
|---|---|
| `sombra_comum` | 198k |
| `sombra_incomum` | 594k |
| `sombra_raro` | 1,58M |
| `sombra_epica` | 3,96M |
| `sombra_lendaria` | 9,9M |
| chefe | 396M |

- Nomes de UI: "Sombra", "Sombra Incomum", "Sombra Raro", "Sombra Épico" e "Sombra Lendário" (`CFG:822`).
- Valor = HP × 0.4.

**Modelos** (`ServerStorage.Modelos`): `minerio_sombra_comum`, `_incomum`, `_epica` e `_chefe`. Todos com `OreType=ShadowMana` e `CoresProprias=true`, **sem** `ShadowGardenPalette`.
- `raro` usa o modelo `incomum` e `lendaria` usa `epica`, repintados com `variante.cor` (`AB:271-276`).
- `minerio_sombra_raro` e `minerio_sombra_lendaria` autorais seriam usados automaticamente se existissem (`AB:235-238`).
- O VFX é o tema `ShadowMana` (`VFX:744-826`).

**Outros:**
- Hats do tema `sombra` (`CFG:176-189`).
- **Área 4 não tem pets** (`PETS_POR_AREA` pula o [4], `CFG:347-390`) **nem gacha** (`EV31.GACHA_MUNDO[4] = false`; `Gacha_sombra` está em `ServerStorage.GachaSombra_Backup`). A ilha não precisa de torre de invocação nem de `GachaPosition`.
- Picaretas do mundo 4: sombria, rúnica, vazio, eminence (`CFG:63-66`). Mochilas: rúnica e sombria (`CFG:90-91`).

**Pendência herdada** (não é deste escopo, mas trava o teste): `Progresso.comprarArea` exige a área anterior (`Progresso:17-20`). Quem sai da Ilha 2 pelo portão SG recebe "Compre Monte Natagumo antes".
