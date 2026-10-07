# Ilha 4 Demon Slayer: as linhas a acrescentar no jogo

Nenhum destes arquivos foi editado pelo agente. Os patches abaixo são aplicados na Onda 5, no Studio, com o Studio livre.

## 1. `ServerScriptService.Core.IslandWorld`: 2 linhas

O `AreaBuilder` chama `IslandWorld.build(mod, area)` para as áreas 1 a 6 (`AreaBuilder.lua:397`). As ilhas montadas entram no `IslandWorld.build` por uma linha de despacho cada, testando a fonte em `ServerStorage`. As Ilhas 1 e 2 já fazem assim (`ServerScriptService.Core.IslandWorld.module.lua:93-97` na cópia de 2026-09-28 em `ilha_shadowgarden/_audit/scripts/`; `M.build` na linha 92).

**a) No topo, junto dos outros `require`** (depois de `local DragonBall=require(script.Parent.DragonBallIsland)` e da linha da Ilha 3):

```lua
local DemonSlayer=require(script.Parent.DemonSlayerIsland)
```

**b) A primeira linha dentro de `function M.build(parent,area)`**, antes de qualquer outro despacho e do ramo procedural:

```lua
 if area.tema=='nichirin' and game:GetService('ServerStorage'):FindFirstChild('IlhaDemonSlayer') then return DemonSlayer.build(parent,area) end -- Ilha 4 Demon Slayer (Onda 5); o Natagumo procedural fica para rollback
```

**Por que `area.tema=='nichirin'` e não `area.id==4`:** desde a troca 3↔4 (`ilha_shadowgarden/DECISOES.md`, D1), os ramos do `IslandWorld` seguem o tema. O Monte Natagumo é o tema `nichirin`, hoje com id 4. A linha continua certa se os ids mudarem de novo.

**Por que primeiro:** a cópia antiga tem `if area.id==4 and …FindFirstChild('ShadowGardenKit') then return ShadowGarden.build(...)`. Ela é inerte sem o kit, mas qualquer linha antiga que retorne para a área 4 tem de ficar **depois** desta.

**Antes de colar:**
- `script_grep "M.build"` no IslandWorld do Studio.
- Confirme onde estão os `require` e a linha da Ilha 3. A versão do Studio é posterior à cópia do repositório.

**Rollback:** renomear `ServerStorage.IlhaDemonSlayer`. A área 4 volta ao procedural antigo (`01_Relevo` / `02_Arquitetura`), que fica intocado.

**Nada mais muda nos sistemas:**

| Sistema | Situação |
|---|---|
| `AreaBuilder` | Chama o `IslandWorld` para as áreas 1 a 6 e usa `spawns` / `boss` / `returnPad` / `zonas` |
| `ILHAS_Cliente` | Já tem `GATES.OnePiece = 5` |
| `PortoesCompra` / `ILHA_NARUTO_Movel` | Regravados pelo montar, com conteúdo igual |
| `Core.Main` | Liga o prompt a toda peça `NextAreaId` dentro de `workspace.Areas` no boot, depois do `AreaBuilder` |
| `IslandTravel` / `IslandVisibility` | Leem `BoundsCenter`, `BoundsHalfSize`, `BoundsMinY` e `SafeMaxY` |

## 2. Guarda da âncora da Ilha 3 (Shadow Garden)

**O que é:** a ponta da ilhota do portão DS na SG tem a guarda provisória `SG_Exit_AnchorGuard` (Model atômico) e `COL_SGAnchorGuard_001` (colisão). O montar da SG grava nelas o atributo `next_island_guard = true` (`ilha_shadowgarden/export/montar_ilha_shadowgarden.lua:3276-3279`). A ponte de chegada da Ilha 4 encosta exatamente nessa âncora, então a guarda tem de sair quando a fonte da Ilha 4 existe. É o mesmo bloco que a Ilha 2 usa para a Ilha 3 (`ilha_dragonball/roblox/DragonBallIsland.lua:195-201`).

**Onde:** `ilha_shadowgarden/roblox/JardimSombrasIsland.lua` (= `ServerScriptService.Core.JardimSombrasIsland` no Studio), dentro de `function M.build` (linha 342), **entre a linha 349 e a 350**. Os números são do commit `ee5a105`.

**Antes de editar:** a outra sessão está mexendo nos efeitos da Ilha 3. Aplique pelo texto-âncora, não pelo número da linha, e só quando ela liberar o arquivo.

**Antes** (linhas 347-351):
```lua
	local model = source:Clone()
	model.Name = 'ILHA_SHADOWGARDEN'
	model.Parent = parent
	local mk = {}
	for _, m in ipairs(model.GAMEPLAY_MARKERS:GetChildren()) do mk[m.Name] = m end
```

**Depois:**
```lua
	local model = source:Clone()
	model.Name = 'ILHA_SHADOWGARDEN'
	model.Parent = parent
	-- Ilha 4 (Demon Slayer, ServerStorage.IlhaDemonSlayer) instalada: a ponte dela encosta no
	-- ISLAND_NEXT_ANCHOR_DemonSlayer, entao sai a guarda provisoria da ponta (SG_Exit_AnchorGuard + COL_SGAnchorGuard_*)
	if SS:FindFirstChild('IlhaDemonSlayer') then
		for _, d in ipairs(model:GetDescendants()) do
			if d.Parent and d:GetAttribute('next_island_guard') then d:Destroy() end
		end
	end
	local mk = {}
	for _, m in ipairs(model.GAMEPLAY_MARKERS:GetChildren()) do mk[m.Name] = m end
```

Ponto de atenção: o `SS` já existe no módulo (linha 13: `local SS = game:GetService('ServerStorage')`).

**Conferir no Play:**
- `#workspace.Areas.Area3:GetDescendants()` não tem mais nada com `next_island_guard`;
- a pé, a ponte passa da SG para a Ilha 4 sem bater em nada.

**Rollback:** sem `ServerStorage.IlhaDemonSlayer`, a guarda volta sozinha.

## 3. `AreaAtmosphere`: perfil `[4]`

Está em `AreaAtmosphere_area4.lua`, nesta pasta. É o script inteiro, com 3 trechos marcados `-- [DS]`:
- o perfil `[4]` novo;
- `Brightness=profile.brightness or 2`;
- `NatagumoMood` publicado antes do `ShadowGardenMood`.

Se o `AreaAtmosphere` do Studio mudou depois de 2026-10-06, aplique só esses 3 trechos.

## 4. Scripts novos

| Instância no Studio | Arquivo |
|---|---|
| `ServerScriptService.Core.DemonSlayerIsland` (ModuleScript) | `DemonSlayerIsland.lua` |
| `StarterPlayer.StarterPlayerScripts.CeuNatagumo` (LocalScript) | `CeuNatagumo.client.lua` |
