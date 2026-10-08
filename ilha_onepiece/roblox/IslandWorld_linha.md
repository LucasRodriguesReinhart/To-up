# Ilha 5 One Piece (Wano): as linhas a acrescentar no jogo

Nenhum script do Studio foi editado pelo agente. Os patches abaixo são aplicados no M5, no Studio, com o Studio livre.

## 1. `ServerScriptService.Core.IslandWorld`: 1 linha

O `AreaBuilder` chama `IslandWorld.build(mod, area)` para as áreas 1 a 6. Cada ilha montada entra no `IslandWorld.build` por uma linha de despacho que testa a fonte em `ServerStorage`.

**Forma usada no Play da Ilha 4 (2026-10-07):** sem `require` no topo. A linha fica logo depois de `local SS=game:GetService('ServerStorage')`, dentro de `function M.build(parent,area)`, junto da linha da Ilha 4:

```lua
 if area.tema=='mare' and SS:FindFirstChild('IlhaOnePiece') and script.Parent:FindFirstChild('OnePieceIsland') then return require(script.Parent.OnePieceIsland).build(parent,area) end -- Ilha 5 One Piece / Wano (M5); a construcao generica da area 5 fica para rollback
```

**Se o `M.build` do Studio não tiver o `local SS`**, use a mesma linha com o serviço por extenso:

```lua
 if area.tema=='mare' and game:GetService('ServerStorage'):FindFirstChild('IlhaOnePiece') and script.Parent:FindFirstChild('OnePieceIsland') then return require(script.Parent.OnePieceIsland).build(parent,area) end
```

**Por que `area.tema=='mare'` e não `area.id==5`:** os ramos do `IslandWorld` seguem o tema desde a troca 3↔4 (`ilha_shadowgarden/DECISOES.md`, D1). A área 5 é o tema `mare` ("Grand Line" no `Config.Areas`).

**Por que sem `require` no topo:** foi assim que a Ilha 4 entrou no Play. Sem `OnePieceIsland` no `Core`, a linha não faz nada, e um erro de carga do módulo não derruba o `IslandWorld` das outras áreas no boot.

**Onde exatamente:** antes do ramo procedural (`local p=palettes[area.id] ...`) e antes de qualquer linha antiga que retorne para a área 5. Hoje não há nenhuma: a área 5 cai no procedural genérico (`01_Relevo...`, EntryPosition (0; 9,5; 2015)).

**Antes de colar:**
- `script_grep "M.build"` e `script_grep "DemonSlayer"` no IslandWorld do Studio.
- Confirme onde está a linha da Ilha 4 e se o `local SS` existe. A versão do Studio é posterior às cópias do repositório.

**Rollback:** renomear `ServerStorage.IlhaOnePiece`. A área 5 volta ao procedural genérico, que fica intocado. Atenção: sem `IlhaOnePiece`, a guarda da âncora da DS volta sozinha (é o `DemonSlayerIsland` que a remove).

## 2. Guarda da âncora da Ilha 4 (Demon Slayer): nada a fazer

O `Core.DemonSlayerIsland` (aplicado no Studio) já tem:
- `M.FONTE_PROXIMA = 'IlhaOnePiece'`;
- o bloco que destrói tudo com `next_island_guard` (`DS_Exit_AnchorGuard` e `COL_DSAnchorGuard_*`) quando essa fonte existe.

A ponte de chegada de Wano (120, reta, 80,2 → 84,2) encosta exatamente no `ISLAND_NEXT_ANCHOR_OnePiece` da DS. O `pos_montagem_onepiece` confere o `M.FONTE_PROXIMA` no Source da DS.

**Conferir no Play:** nada com `next_island_guard` em `workspace.Areas.Area4`, e a pé a ponte passa da DS para Wano sem bater em nada.

## 3. Guarda da âncora de Wano (One Punch Man, área 6): fica

A área 6 (Cidade Z, tema `serio`) **ainda não existe como ilha**. A ponta do promontório termina na guarda provisória `OP_Exit_AnchorGuard` + `COL_OPAnchorGuard_001` (`next_island_guard`, tag `GuardaProximaIlha`). Ela é o término seguro, testado no blockout.

O `Core.OnePieceIsland` remove essa guarda quando existir **`ServerStorage.IlhaOnePunchMan`**. Esse nome é **suposto** (`M.FONTE_PROXIMA`, linha 38 do módulo). A integração da área 6 deve usar esse nome ou mudar a constante. A ponte da área 6 deve encostar em `ISLAND_NEXT_ANCHOR_OnePunchMan`:
- posição (−2553,25; 88,2; 1679,39);
- frente (−0,9397; 0; −0,3420);
- largura 18 e altura livre 22.

O disco livre tem r 300, centrado 350 à frente da âncora (PLANO_OP seção 3).

## 4. `AreaAtmosphere`: perfil `[5]` + `WanoMood`

Está em `AreaAtmosphere_area5.lua`, nesta pasta. É o script inteiro, a partir da versão aplicada hoje (`ilha_demonslayer/roblox/AreaAtmosphere_area4.lua`). As 3 linhas `[DS]` estão iguais. As linhas `-- [OP]`, todas aditivas, são:

1. o perfil `[5]` diurno (troca a linha `[5]` antiga, mantendo `name='GrandLine'`);
2. `base` guarda também `GeographicLatitude`, `EnvironmentDiffuseScale` e `EnvironmentSpecularScale` (linha nova logo depois de `local base=...`);
3. no `tween(Lighting,{...})`, a linha nova `GeographicLatitude=... EnvironmentDiffuseScale=... EnvironmentSpecularScale=...`, entre a linha `[DS]` e a de `ColorShift_Top`;
4. `tween(correction,{Brightness=profile.cbright or 0})` depois do tween da correção, e `tween(correction,{Brightness=0})` no `else`;
5. `player:SetAttribute('WanoMood',profile~=nil and profile.name=='GrandLine')`, linha nova depois da linha dos moods.

Se o `AreaAtmosphere` do Studio mudou depois de 2026-10-07, aplique só esses trechos.

**Valores do perfil `[5]`:** são os da seção 10 do PLANO_OP (valores iniciais). Na hora da entrega não havia `AreaAtmosphere_area5.md` do agente de luz nesta pasta. Se ele aparecer, os valores dele mandam: troque só a linha `[5]`.

## 5. Scripts novos

| Instância no Studio | Arquivo |
|---|---|
| `ServerScriptService.Core.OnePieceIsland` (ModuleScript) | `OnePieceIsland.lua` |
| `StarterPlayer.StarterPlayerScripts.CeuWano` (LocalScript) | `CeuWano.client.lua` |

## 6. Nada mais muda nos sistemas

| Sistema | Situação |
|---|---|
| `AreaBuilder` | Usa `spawns`, `boss`, `returnPad` e `zonas` (lista de células + bloqueios), igual às Ilhas 3 e 4 |
| `ILHAS_Cliente` | Já tem `GATES.OnePunchMan = 6` (`ilha_dragonball/roblox/ILHAS_Cliente.client.lua:12`) |
| `PortoesCompra` / `ILHA_NARUTO_Movel` | Regravados pelo montar, com conteúdo igual |
| `Core.Main` | Liga o prompt a toda peça `NextAreaId` dentro de `workspace.Areas` no boot, depois do `AreaBuilder` |
| `IslandTravel` / `IslandVisibility` | Leem `BoundsCenter`, `BoundsHalfSize`, `BoundsMinY` (28) e `SafeMaxY` (150) |
| `Config` | Área 5 `mare` "Grand Line" e área 6 `serio` "Cidade Z" já existem. `Gacha_mare` é o motor do summon. `AudioCatalog.Music[5]` ("Pirate King") já existe. |
