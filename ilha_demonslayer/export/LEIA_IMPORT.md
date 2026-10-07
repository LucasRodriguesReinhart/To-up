# Ilha 4 Demon Slayer: import no Studio (export 9cc4bef4)

Gerado na Onda 6c (integração final, depois do finesse 6b) em 2026-10-06 por `./run.sh export`. Resultado: EXPORT OK, nenhum dono estourou e a CONEXAO ficou em 0,0004. Substitui o export `ef639523` da Onda 4b/5: os FBX antigos saíram da pasta (as pastas `*_ef6395.fbm` que sobraram não são usadas).

## Ordem dos FBX
Importe um FBX por vez, pelo botão Import do ribbon, para dentro de `workspace.ILHA_DEMONSLAYER`. Espere ~14 s entre um arquivo e outro. **Apague antes o conteúdo importado do `ef639523`** (o montar confere o `EXPORT_ID` e os nomes mudaram).

| # | FBX | Malhas | Tris |
|---|---|---|---|
| 1 | `ILHA4_02_TERRAIN_9cc4be.fbx` | 57 | 106.981 |
| 2 | `ILHA4_03_CLEARING_9cc4be.fbx` | 9 | 9.191 |
| 3 | `ILHA4_18_ENTRY_9cc4be.fbx` | 25 | 22.720 |
| 4 | `ILHA4_05_VILLAGE_9cc4be.fbx` | 100 | 107.126 |
| 5 | `ILHA4_04_FORGE_9cc4be.fbx` | 81 | 117.725 |
| 6 | `ILHA4_06_SUMMON_9cc4be.fbx` | 24 | 28.096 |
| 7 | `ILHA4_07_WATER_9cc4be.fbx` | 11 | 4.640 |
| 8 | `ILHA4_09_PROPS_9cc4be.fbx` | 47 | 47.549 |
| 9 | `ILHA4_10_VEGETATION_9cc4be.fbx` | 76 | 115.236 |
| 10 | `ILHA4_08_NEXT_ISLAND_9cc4be.fbx` | 27 | 23.024 |
| 11 | `ILHA4_08_PURCHASE_GATES_9cc4be.fbx` | 18 | 12.668 |
| 12 | `ILHA4_12_VFX_HELPERS_9cc4be.fbx` | 25 | 4.648 |

**Total:** 500 MeshParts e 599.604 tris (teto 630k / 650), 74 materiais, 863 colisões depois da união (1.232 caixas no .blend), 231 MeshParts com sombra.

Depois do import:
1. Rode `montar_ilha_demonslayer.lua` na Command Bar. Ele confere a importação, alinha, cria as colisões, os marcadores e as luzes.
2. Se algum grupo vier girado em 180°, como aconteceu nas Ilhas 2 e 3, alinhe esse grupo sozinho e rode o montar de novo com `ALINHAR = false`.

**O que mudou no montar** (regenerado; a lógica é a mesma do `ef639523`, só mudaram o `EXPORT_ID`, a lista de FBX e as tabelas de malhas/colisões):
- `Glass_DS_Lantern` (papel aceso) agora sai **(214, 144, 88)** Neon: é a cor da 6b (item 55). O ajuste manual da Onda 5 (232, 146, 66) não vale mais.
- Materiais novos: `Stone_DS_Ishi` (100, 98, 92) e `Stone_DS_IshiD` (86, 84, 80) do ishigaki; `Bamboo_DS` mais escuro (90, 116, 56).
- A água da lagoa (sem a camada ForceField por triângulo) é do `roblox/DemonSlayerIsland.lua`, que não é regenerado: o ajuste da Onda 5 continua.

## Nomes longos
O importador trunca com "…" os nomes de mais de ~50 caracteres. Na Ilha 2, nomes de 53 e 56 caracteres foram cortados e os de 49 passaram.

Nesta ilha **nenhum nome passa de 48**. As lanternas de caminho do sul chegavam a 49 (`DS_Prop_PathLamps_SulClareira__Stone_DS_Path_g1_7`), e o objeto virou `DS_Prop_PathLamps_SulClr`. Os mais longos agora são:
- `GATE_OnePiece_Barrier__Energy_Core_OnePiece_Glow` (48);
- `DS_Prop_PathLamps_VilaForja__Wood_DS_Dark_g1_5` / `_g2_6` (46);
- `GATE_OnePiece_Lock__Energy_Core_OnePiece_Glow` e `DS_Prop_PathLamps_VilaForja__Glass_DS_Lantern` (45).

Se o montar acusar alguma malha faltando, procure "…" nesses nomes e renomeie a peça antes de rodar de novo.

## Peças móveis (tag `IlhaMovel`, 13 peças)
- **Roda d'água:** `VFX_DS_Wheel`.
- **Pilão kine:** eixo `VFX_DS_KineAxle` e pilões `VFX_DS_Kine_A` e `VFX_DS_Kine_B`.
- **Summon:** anéis `VFX_DSSUM_Ring_1..3` e estrela `VFX_DSSUM_Star`.
- **Portão One Piece:** `VFX_GATE_OnePiece_Hat_1..4` e `VFX_GATE_OnePiece_Needle`.

O portão recebe a tag `PortaoCompra`, e o lock é `COL_GateOnePieceLock_001`. A guarda provisória da âncora, `DS_Exit_AnchorGuard` com `COL_DSAnchorGuard_*`, recebe a tag `GuardaProximaIlha`.

## Luzes
São 58 luzes: 17 acesas de dia (o limite é 36) e 41 `NightOnly` (`L_DSProp_*`).

Overrides de interior (`LUZ_DS`):

| Luz | Range | Brightness |
|---|---|---|
| Boca da fornalha | 28 | 2,0 |
| Fornalha | 28 | 2,5 |
| V6 irori | 14 | 0,67 |
| V6 andon | 14 | 0,56 |
| V1 chochin | 12 | 0,56 |

## Marcadores e atributos da área (para o `Core.DemonSlayerIsland`, Onda 5)
Coordenadas no Roblox. Siga o contrato do `JardimSombrasIsland`.

**Entrada e conexão:**
- `WORLD_FROM_PREV`: (-1534,493; 52,2; 962,443). Encaixe na âncora da SG com distância 0,0004.
- `EntryPosition`: vem de `WORLD_ENTRY_DemonSlayer` (-1627,951; 54,4; 1040,863), com `EntryForward` (-0,766; 0; 0,643). Some `HRP - 0,2` em Y, como na SG.

**Próxima ilha:**
- `NextAnchorPosition`: `ISLAND_NEXT_ANCHOR_OnePiece` (-2054,391; 80,2; 1551,759).
- `NextAnchorForward`: (-0,5736; 0; 0,8192).
- `NextAnchorWidth`: 18.
- `NextAnchorClearHeight`: 22.
- `NextAnchorKey`: OnePiece. A área 5 tem `GATE_OnePiece` com `area_id` 5.

**Limites da caixa** (estimados pelas malhas exportadas; o `caixa(model)` do Core recalcula):
- `BoundsCenter` ≈ (-1818; 0; 1263,5);
- `BoundsHalfSize` ≈ (300; 162; 319). Y é o topo, a chaminé em 152,2 + 10;
- `BoundsMinY` ≈ -85 (a quilha desce a ~-75).

**Constantes:**
- `SafeMaxY` = **100**: a forja e a saída ficam em 80,2.
- `OreMax` = **80**, com meta de 70 simultâneos.

**Mineração:**
- `MiningZone_DemonSlayer` em (-1835,365; 60,2; 1156,161), com `sx` 112, `sy` 150, `floor` 60,2 e céu aberto (sem `ceil`; o script usa piso + 28).
- 72 `ORE_*`: 38 common, 22 uncommon, 10 epic e 2 superlegendary.
- 81 `GP_Block_*`: 48 de borda, 28 de canto e 5 de corredor.

**Summon:**
- `SUMMON_Main` (-1959,184; 70,2; 1078,606);
- `SUMMON_Interact`;
- `SUMMON_PlayerPosition`.

**Outros marcadores:** 13 `SAFE_*`, 8 `AUDIO_*` e os `FX_*` / `WATER_*`. `FX_Forge_Smoke_Vent` é novo, criado na Onda 3c.

Total: 217 marcadores em `GAMEPLAY_MARKERS`.

No `9cc4bef4` as posições dos 217 marcadores são **as mesmas** do `ef639523` (conferido no `ilha4_data.json`). Só mudaram os atributos de largura de `FX_Fall_1_Lip`, `FX_Fall_1_Step` e `FX_Fall_1_Base` (cascata mais larga, item 42 da 6b): `width` 2,6→3,0 / 3,8→4,6 / 5,5→6,5 e os `widths` da cortina.
