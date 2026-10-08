# Ilha 5 One Piece / Wano: import no Studio (export 37998c7c)

Gerado na M6c (integração final, depois do finesse M6b) em 2026-10-08 por `./run.sh export`.

**Resultado do export:**
- EXPORT OK, e nenhum dono estourou;
- CONEXAO `WORLD_FROM_PREV` × âncora da Ilha 4: **0,0000**;
- esta pasta só tem o export `37998c7c` (não há FBX nem `.fbm` antigos).

O passo a passo completo (backup, scripts, patches e Play) continua em `../roblox/LEIA_M5.md`. Este arquivo cobre só o que mudou no import.

## Ordem dos FBX

Importe um FBX por vez, pelo botão **Import** do ribbon, para dentro de `workspace.ILHA_ONEPIECE`. Espere uns 14 s entre um arquivo e outro.

Se houver um import anterior da ilha no place, **apague antes o conteúdo dele**: o montar confere o `EXPORT_ID` e os nomes das malhas mudaram. O trecho do M2 (`workspace.ILHA_ONEPIECE_M2`) também sai: o `pos_montagem` avisa.

| # | FBX | Malhas | Tris | Conteúdo |
|---|---|---|---|---|
| 1 | `ILHA5_02_TERRAIN_37998c.fbx` | 56 | 72.985 | Falésias, pele, arrimos, rochedo do castelo, lajeado do cais |
| 2 | `ILHA5_03_PLAZA_37998c.fbx` | 28 | 31.634 | Praça de mineração, faixa sul do M2, mureta |
| 3 | `ILHA5_18_ENTRY_37998c.fbx` | 29 | 28.748 | Ponte de chegada, viaduto, grande torii, pátio |
| 4 | `ILHA5_05_CAPITAL_37998c.fbx` | 141 | 178.336 | Casas do kit e leves, ruas, quintais, santuário, casa de chá |
| 5 | `ILHA5_04_CASTLE_37998c.fbx` | 67 | 113.687 | Castelo (82,0k) e árvore arqueada (31,7k) |
| 6 | `ILHA5_06_SUMMON_37998c.fbx` | 24 | 30.740 | Torre AMS e base Wano |
| 7 | `ILHA5_07_WATER_37998c.fbx` | 9 | 6.680 | Cantaria dos canais, bacia e roda d'água |
| 8 | `ILHA5_16_HARBOR_37998c.fbx` | 52 | 55.405 | Porto (36,7k) e navio (18,7k) |
| 9 | `ILHA5_09_PROPS_37998c.fbx` | 29 | 25.538 | Props |
| 10 | `ILHA5_10_VEGETATION_37998c.fbx` | 47 | 47.380 | Vegetação |
| 11 | `ILHA5_17_LANDMARKS_37998c.fbx` | 15 | 9.660 | Caveira, espada e pagode |
| 12 | `ILHA5_08_NEXT_ISLAND_37998c.fbx` | 10 | 8.544 | Ponte vermelha de saída e guarda provisória |
| 13 | `ILHA5_08_PURCHASE_GATES_37998c.fbx` | 15 | 7.180 | Portão One Punch Man (galeria) |
| 14 | `ILHA5_12_VFX_HELPERS_37998c.fbx` | 19 | 3.228 | Peças móveis: roda d'água, anéis e estrela do summon |

**Totais:**

| Item | Valor |
|---|---|
| MeshParts | 541 (teto 650) |
| Tris | 619.745 (teto 640k) |
| Materiais | 65 |
| Colisões | 743 depois da união (1.214 caixas no .blend; teto 1.300) |
| Marcadores | 219 |
| Luzes | 64: 8 ativas de dia (teto 36) e 56 `NightOnly` |
| MeshParts com sombra | 260 |
| Peças móveis | 9 |

Depois do import:
1. Rode `montar_ilha_onepiece.lua` na Command Bar. O montar regenerado tem `EXPORT_ID = 37998c7c`, a lista de FBX e as tabelas de malhas e colisões.
2. Se algum grupo vier girado em 180°, como aconteceu nas Ilhas 2 e 3, alinhe esse grupo sozinho e rode de novo com `ALINHAR = false`.
3. Depois rode o `pos_montagem_onepiece.lua`.

## Nomes longos

O importador trunca com "…" os nomes de mais de ~50 caracteres, e o montar procura o nome exato. Nesta ilha **nenhum nome passa de 48**. O mais longo tem 41.

Só o portão One Punch Man passava do limite:
- `GATE_OnePunchMan_Barrier__Energy_Core_OnePunchMan_Glow` tinha 54;
- `GATE_OnePunchMan_Lock__Energy_Core_OnePunchMan_Glow` tinha 51.

O material da energia sai com nome curto **só no export**: `Energy_OPM_Glow`. Ele tem a mesma cor (255, 226, 140) e continua Neon.

O objeto e o asset da galeria não mudaram:
- o montar continua casando `^GATE_(%w+)_(%a+)` com a chave `OnePunchMan`;
- o Neon do portão (item 50) segue como pendência do usuário.

Os mais longos agora são:

| Nome | Caracteres |
|---|---|
| `GATE_OnePunchMan_Barrier__Energy_OPM_Glow` | 41 |
| `GATE_OnePunchMan_Frame__Metal_GateOPM_Red` | 41 |
| `GATE_OnePunchMan_Frame__Stone_Wall_Light` | 40 |
| `VFX_GATE_OnePunchMan_Star_1__Metal_Gold` | 39 |

## O que mudou desde o export do M4/M5

**Faces de um lado só.** O Roblox desenha só a frente da face. Na M6c, cerca de 11 mil acertos de "avesso" visto do jogador e das câmeras foram corrigidos na fonte:
- muralhas e arrimos;
- paredes, janelas acesas e empenas das casas;
- telhados vistos de cima;
- lajes da praça;
- telhados do pagode.

Se no Studio aparecer algum buraco "de papel" (vê-se através de uma parede), anote a posição: é face invertida.

**Atributo novo no marcador `FX_Fall_Castle_Lip`:**
- `spout_waypoints_world` traz a bica da cachoeira do castelo **já no mundo do Roblox**;
- `spout_waypoints` (local) continua lá, para um `OnePieceIsland` antigo;
- o `roblox/OnePieceIsland.lua` novo usa a versão `_world` e só converte a local se ela faltar. Não há conversão dupla em nenhuma combinação.
- Reinstalar o módulo é recomendado, mas não é obrigatório para este export.

**Colisão do encontro oeste da ponte de saída** (`COL_OP_ExitAbut`): o topo desceu para o topo da pedra (86,4). Antes ficava em 87,2, 0,8 acima da pedra em (208, 224). A planta não mudou.

**Lajeado do cais:** 606 lajes, com topo 0,12 acima da colisão do cais (42,2), como nas ruas.

**Cores das falésias:** a família `Cliff_OP_Face/Shade/Crevice` agora vale também no pináculo do pagode e nas lascas da espada. Nenhuma malha usa mais `Cliff_OP_Warm/Cool`.

## Atributos da área 5 para o `Core.OnePieceIsland`

O módulo lê os marcadores de `GAMEPLAY_MARKERS` e escreve na área. Nada aqui é digitado à mão; a tabela serve para conferir no Play.

| Atributo | Valor / origem |
|---|---|
| `EntryPosition` / `EntryForward` | `WORLD_ENTRY_OnePiece` (-2136,986; 84,4; 1669,717); `HRP` 3,5 acima do piso |
| `SafePosition` / `SafeMaxY` | entrada + 8 na frente / 150 (salva até o pátio do castelo, 136,2) |
| `BoundsCenter` / `BoundsHalfSize` / `BoundsMinY` | caixa do modelo (centro em Y 0) / `BoundsMinY` 28 (abaixo do mar local 36) |
| `PisoY` / `OreMax` | 92,2 (praça) / 80 (72 marcadores de minério na `MiningZone_OnePiece`, 0 fora da zona) |
| `Portao` / `NextAreaId` | `OnePunchMan` / 6 |
| `NextAnchorPosition` / `NextAnchorForward` | `ISLAND_NEXT_ANCHOR_OnePunchMan` (-2553,248; 88,2; 1679,39) / (-0,94; 0; -0,342) |
| `GachaPosition` / `MotorDaTorre` | `SUMMON_Main` (-2385,221; 88,2; 1727,848) / torre AMS por alias |
| `MarLocalNivel` / `MarLocalCentro` / `MarLocalTamanho` / `MarLocalCor` | 36 / `WATER_Sea` (-2321,499; 36; 1828,622) / do marcador |
| `RotaPropria` / `TravessiaKeep` / `WorldRevision` | `true` / do módulo / 1 |

`conexao_roblox.json` tem as posições dos marcadores de conexão.
