# Ilha 5 Wano: auditoria medida V2 (U5, U6, U8 e mapeamento U1–U16)

Data: 2026-10-09/10. Fonte medida: **cópia** de `ilha_onepiece.blend` (08/10 10:27, a mesma cena do export **37998c7c** que o usuário jogou).
- **Visual:** as 72 malhas exportadas (`ilha5_data.json`, 619.745 tris).
- **Colisão:** as **743 caixas EXPORTADAS** (as do jogo, depois da união), convertidas de Roblox para local.

No jogo, toda MeshPart sai com `CanCollide=false` (montar, export_roblox). **Só as `COL_*` seguram o jogador.** Também não colidem: a água (Part com `CanCollide=false`) e o mar local.

## Método

Os scripts estão copiados em `aud/scripts/` (rodam numa pasta de trabalho com uma cópia `aud.blend` do `.blend`; o gate V2 do `op_qa` parte deles):
- `audit_rays.py` (Blender `--factory-startup`);
- `analyze.py`, `zones_u8.py`, `u5.py`, `holes.py` e `inside.py` (análise);
- `map_*.py` e `sheet_*.py` (folhas).

**Raios de cima numa grade de 1,5:**
- Para cada célula, o script registra o 1º hit visual (cota, normal, objeto, material).
- Também registra a 1ª colisão abaixo de `visual + 1,5` e todos os hits de colisão. Desses hits saem os intervalos sólidos, os topos e os tetos.
- A grade tem origem deslocada (+0,037; +0,061), para não cair em cima das juntas exatas entre caixas (na 1ª passada isso gerou falsos buracos).

**Alcance (BFS):**
- Parte do spawn (0, 24, 84,2).
- Usa o pulo padrão do Roblox, **7,2**, e corpo de 5. A queda pode ter qualquer altura.
- O topo das guardas invisíveis conta como superfície: elas têm 1,0 de espessura e dá para subir nelas.

**Os quatro testes:**
- **U8, "chão visual sem colisão alcançável":** normal ≥ 0,7, sem colisão até 1,5 abaixo e a ≤ 6 de uma superfície alcançada, com `visual ≤ h + 7,2`.
- **U8b, "dentro do modelo":** de cada superfície alcançada sai um raio para cima. Se ele bate numa face de trás a ≥ 1,5, o corpo está dentro da malha. Se bate numa face a < 3, a cabeça está dentro.
- **U5, linhas finas:** passo de 0,2, uma linha a cada 3, nos eixos X e Y.
  - (A) vão de colisão ≥ 0,6 sob visual contínuo;
  - (B) fresta visual de 0,2 a 4 entre pisos na mesma cota (|dz| < 0,6).
- **U6:** cortes por raios múltiplos em y 182, 185, 176, 252, 255 e 246.

**Premissa a confirmar no Studio:** o jogo usa o pulo padrão (`CharacterJumpHeight` 7,2). Se o AMS dá pulo maior, os números do U8 sobem.

## Folhas

| Arquivo | Conteúdo |
|---|---|
| `U8_mapa_chao_sem_colisao.png` | Mapa local. Vermelho: chão ou rocha visual alcançável sem colisão. Laranja: telhado. Magenta: copa. Verde: chão com colisão já alcançado. |
| `U5_U8b_mapa_vaos_dentro.png` | Círculos: frestas (U5-B). Quadrados: vãos de colisão (U5-A). Ciano: corpo dentro do modelo. Azul: cabeça dentro. |
| `U6_ponte_canal_corte.png` | Corte medido da ponte do canal, com a captura 05. |
| `U_mapeamento_donos.jpg` | As 15 capturas e a folha do vídeo 3, cada uma com item U, dono e coordenadas. |
| `U8_zonas.json`, `U8b_dentro_do_visual.json`, `U5_vaos.json`, `U5_buracos_colisao_no_piso.json` | Dados brutos. |

---

## U8: chão aparente onde se cai para dentro do modelo (MEDIDO)

**Total alcançável sem colisão:**

| Tipo | Área (studs²) |
|---|---|
| Chão ou rocha | **11.671** |
| Telhado | 2.138 |
| Copa | 2.734 |

### Causas-raiz

| # | Causa | Onde está no código |
|---|---|---|
| R1 | **A colisão vem da PLANTA, não do visual.** `op_col` faz caixas maciças só nos 12 polígonos de `op_layout.floors()`. Tudo o que é visual fora deles não colide: `ROCKS` ("terreno que NÃO é piso, só visual"), a pele da borda entre piso e falésia, os canais, a bacia, os arrimos e muretas. | `op_col.py`, `op_layout.py` |
| R2 | **A guarda invisível tem 3,2** (`GUARD_H`), menos da metade do pulo de 7,2. O jogador pula a guarda (ou sobe nela e pula de novo) e cai na rocha ou pele sem colisão. | `op_col.GUARD_H` |
| R3 | **Canais e bacia são buracos sem fundo.** A água é Part sem colisão e o leito visual (89,4 / 95,4) não tem colisão: quem entra cai até o vazio e é resgatado pelo `BoundsMinY` 28. É o vídeo 1, quadro 9: a câmera sob a água. | `op_col` ("canais e bacia são BURACOS"), `op_water` |
| R4 | **As faixas 'union' de 8 do `op_col.strips` passam dos polígonos de aresta diagonal.** Isso cria **piso invisível 92,2 dentro da rocha NE** e chão de cais sob as muralhas: o jogador anda para dentro do morro. | `op_col.strips` |
| R5 | **Casa = caixa baixa.** O topo da `COL_OP_CapHouse*` fica 7 a 10 abaixo do telhado visual. Quem sobe no telhado (vídeo 3, linha 1) afunda 9 dentro da casa. | `op_capital`, `op_harbor` |

### Zonas de chão ou rocha (≥ 80 studs²)

Coordenadas locais. "Vazio" é a porcentagem das células sem nenhuma colisão abaixo (cai até o resgate).

| Zona | Área | Caixa x0..x1 / y0..y1 | Cota visual | Queda | Vazio | Dono visual |
|---|---|---|---|---|---|---|
| **Borda oeste** (lobo SO, W2b e W3: pele entre o piso e a falésia) | 1.665 | −230..−179 / 118..442 | 81–100 | ~60 | 97% | op_terrain |
| **Canal oeste** (leito + capa) | 1.620 | −179..−170 / 50..299 | 85–97 | vazio | 100% | op_terrain, op_water |
| **Canal leste + bacia do adro** | 1.422 | −18..198 / 335..347 | 89–133 | vazio | 96% | op_terrain, op_water |
| **Borda sul** (frente e entrada) | 1.249 | −170..223 / −115..44 | 17–90 | ~56 | 97% | op_terrain |
| Topos de muralha e arrimo sobre o cais | 603 | 123..246 / 41..260 | 45–92 | 30 | 0% | op_terrain (Walls), op_harbor (Muralha) |
| Corrimão e pedras do summon | 486 | 116..205 / 150..260 | 87–96 | 2,5 | 0% | op_summon |
| Borda do castelo (W3 norte, BackW) | 434 | −177..99 / 331..470 | 92–137 | vazio | 89% | op_terrain |
| Borda leste (porto e summon) | 400 | 205..345 / 52..272 | 35–92 | 12 | 99% | op_terrain |
| Rocha FrontR (ombro leste da entrada) | 382 | 45..123 / 29..43 | 86–92 | 56 | 68% | op_terrain |
| **Montanha NE (NERocksW)**: a do U11 | **369** | **192..231 / 290..337** | 100 | 7,8 (cai no piso 92,2 **dentro** da rocha) ou vazio | 65% | op_terrain |
| Rocha EntryR / EntryL (ombros do torii) | 286 / 160 | ±27..48 / 1..34 | 90 | 2,6 | 85% | op_terrain |
| Rochedo do castelo: BackW, CastleFootW, ButtressL, ButtressR | 239 / 194 / 135 / 95 | −96..55 / 338..469 | 101–136 | até 100 | 50–100% | op_terrain |
| Montanha NE: BackE e CastleFootE | 128 / 88 | 22..76 / 349..472 | 115–143 | vazio | 96–100% | op_terrain |
| Navio (amurada, casco e castelo de popa) | 223 | 240..256 / 107..188 | 43–56 | 2,5 | 89% | op_ship |
| Promontório: caveira e borda NE | 178 / 187 | 226..331 / 226..304 | 87–95 | vazio | 100% | op_terrain, op_landmarks |
| Telhados da praça (oeste, NE) / do cais | 873 / 479 | — | 96–112 / 51–94 | 9,2 / 9,5 | 0% | op_capital, op_harbor |

### "Dentro do modelo" (U8b): o jogador fica com o corpo dentro

| Onde | Área | Caixa | O que acontece |
|---|---|---|---|
| **NE**: piso de colisão 92,2 sob a rocha NERocksW (R4) | 61 corpo + 36 cabeça | 190..226 / 290..337 | anda-se para dentro do morro atrás do vilarejo |
| Pátio do castelo: raízes, tronco e base da torre sem colisão | 315 | −27..73 / 379..467 | o corpo entra na raiz ou na base |
| Cais: pier e muralha (corpo) / arrimos (cabeça) | 137 / 151 | 123..246 / 41..262 | anda-se dentro da muralha |
| W3 leste (rocha BackW) / adro (CastleFootW) / pátio do torii | 79 / 54 / 47 | — | a cabeça entra na rocha |

Há também o "pé que afunda": o visual fica 0,4 a 0,9 acima da colisão.
- Pátio do castelo: 0,9.
- Pontes do canal: 0,64.
- Pedras do summon e pátio do torii: 0,45.

---

## U5: vãos (MEDIDO na faixa do jogador)

**(A) Vão de colisão ≥ 0,6 sob visual contínuo:** quase nenhum. São 10 grupos, a maioria em telhados ou muretas (por exemplo, a mureta da bacia em (±18, 335,5) e o telhado do H5 em (135..145, 83)). **O piso de colisão é contínuo:** o problema real é o visual sem colisão (U8), não fresta na colisão.

**(B) Frestas visuais** (dá para ver o fundo; 430 ocorrências em 157 grupos):

| Onde (local) | Largura | Vê até | Dono |
|---|---|---|---|
| **Cabeça da ponte vermelha de saída** (212..221, 232..249), cota 88,3: frestas entre as tábuas | 0,2–0,6 | o cais e a terra, **46 abaixo** | op_exit |
| **Junta T1 / praça em y 117–119**, de x −113 a +59 (borda M2 × casas do bairro × arrimo) | 0,2–0,8 | o arrimo e a falésia, 86–90 | op_m2_praca/op_plaza (`OP_Plz_M2_Borda`), op_capital (Bairro/Leste), op_terrain (`M2_Arrimo`) |
| Canto leste T1 × praça (85..115, 119..149) | até 3,2 | a falésia, 88–92 | op_terrain (Ground) |
| Borda sul (x −156..−90, y 35–45) | até 2,4 | a falésia, 70–75 | op_terrain |
| Borda oeste (x −224..−214, y 135–430) e norte do W3 (−210..−171, 398–435) | 0,4–3,8 | a falésia ou rocha, 57–87 | op_terrain |
| Topo da OesteAlta / W3 (−113,6; 308,4) e (−94,6; 329,5) | até 3,6 / 0,8 | a falésia | op_terrain, op_capital |
| Rua alta do porto (148..174, 133..146) | até 3,8 | o cais, 18 abaixo | op_harbor, op_terrain |
| Promontório (335,8; 241,7) e FrontR (179,8; 23,9) | até 1,8 / 1,6 | a falésia | op_terrain |

---

## U6: ponte do canal "dentro da calçada" (MEDIDO, y 182 e 252 iguais)

| Medida | Valor |
|---|---|
| Vão real do canal | **7,0** (x −177,4..−170,4) |
| Leito | 89,4 |
| Água | 91,6, ou seja **0,6** abaixo do piso |
| Capa de pedra do canal | **93,05–93,15** (1,2 a 2,6 de largura) |
| Calçada leste | 92,29–92,35 |
| Margem oeste | 91,9–92,3 |
| Tabuleiro | **14,4** de comprimento (−181,2..−166,8), 92,79–92,92 sobre o canal e 92,50–92,69 sobre as calçadas; **flecha de 0,13** |
| Colisão | `CanalS`/`CanalN` plana a **92,2** (rampa de 10 × 16) |

**Por que lê "dentro da calçada":**
1. A **capa do canal fica 0,15 a 0,35 ACIMA do tabuleiro**. As pedras atravessam as tábuas: são as faixas cinza da captura 05.
2. **3,6 a 3,8 de tabuleiro em cada lado estão deitados sobre a calçada**, com só 0,2 a 0,35 de altura. Lê como prancha no chão.
3. Não há o que vencer: a água está a 0,6 do piso e a folga sob a ponte é de 1,2 a 1,3. Não há arco, encontro, degrau nem rampa.
4. O pé afunda 0,6 a 0,7 nas tábuas, porque a colisão está a 92,2.

**Causa no código:**
- O `op_capital.canal_bridge()` desenha o tabuleiro para uma "capa 92,5" (pedido do `op_water` no cabeçalho). Na ponte, a capa medida é 93,05–93,15: os dois donos não fecharam a cota.
- A planta (`op_layout.bridge_list`) põe a ponte PLANA na cota da praça.

---

## Mapeamento U1–U16 → donos → coordenadas (folha `U_mapeamento_donos.jpg`)

| U | Item | Dono(s) | Onde (local) | Evidência |
|---|---|---|---|---|
| U1 | Casas feias | `op_kit.house` e presets; `op_capital` (setores WEST, BEYOND, BAIRRO, TERRACE, NE, EAST e corpo "leve"); `op_m2_trecho` (C1, C2, C5, C6) | Rua de chegada x −40..40, y 44..112; oeste x −216..−122, y 125..291; bairro y 38..118; leste x 40..120; NE x 110..222, y 265..339; terraço W3 | 01, 02, 09 |
| U2 | Vila e caminhos | `op_layout.STREETS` e `BUILDINGS`; `op_capital` (yards, quintais de terra, `PAVED_CUTS`); `op_m2_trecho` (rua); `op_terrain` (`OP_Ter_Ground`) | Toda a capital; laje sobre grama (11); rua de chegada (02) | 02, 11, vídeo 3 |
| U3 | Castelo | `op_castle` (`OP_Cas_Keep`, `Court`, `Adro`) e `op_terrain` (`CastleRock`, `CastleWall`) | Torre (0, 404), pátio CC 136,2, adro CF 98,2 | 03, 14 |
| U4 | Árvore monumental e árvores menores | `op_tree` (`OP_Tree_Trunk`, `Branches`, `Bloom`); `op_veg` (9 grupos `OP_Veg_*`); `op_summon` (`OP_Sum_Garden`, pinheiros) | Base (54, 446) → arco até 301; vegetação na ilha toda | 03, 04 |
| U5 | Vãos | `op_exit` (tábuas), `op_terrain` (pele × falésia), junta M2 (`op_m2_praca`/`op_plaza` × `op_capital` × `op_terrain`) | Ver U5 acima | vídeos |
| U6 | Ponte na calçada | `op_capital.canal_bridge`, `op_water` (capa), `op_col.bridges` e `op_layout.bridge_list` (cota) | (−174, 182) e (−174, 252) | 05 |
| U7 | Pequenas estruturas | `op_props` (poço, bancas, carga), `op_kit.lantern_post`/`lantern_box_post`, `op_capital.canal_bridge`, `op_exit` | Poços em (−117, 67), (−205, 164,5) e no terraço W3 | 06, 13 |
| U8 | Cair dentro do modelo | **`op_col`** (planta, union, guarda 3,2, canais sem fundo); `op_layout.ROCKS`/`floors`; `op_terrain` (pele e rochas); `op_water` | Ver U8 acima | vídeos 1–3 |
| U9 | Porto fraco | `op_harbor` (pier, palafita, H1–H5, 3 barcos estáticos), `op_ship` (1 navio), `op_vfx` (sem peças móveis no porto), `CeuWano` (textura do mar) | Cais 42,2, x 120..246, y 24..262; navio (248, 152) | 07, vídeo 2 |
| U10 | Summon sem tema OP | `op_summon` (alias da torre `il_summon` + base Wano) | Torre (170, 214), terraço T1 | 08 |
| U11 | Vilarejo NE e montanha | `op_capital` NE (N1 santuário + N2, N3, N5–N10 soltas); `op_terrain` (NERocksW/E, BackE, CastleFootE); `op_col` (R4) | x 110..231, y 265..339; rocha 100–120 | 09, vídeo 3 |
| U12 | Sem vida por dentro | `op_kit` e `op_capital` (portas fechadas; só a casa de chá tem interior); `op_harbor` (armazéns fechados); `op_castle` (salão vazio) | Capital e porto | vídeos |
| U13 | Estrutura na montanha | **`op_landmarks` (`OP_Lmk_Pagoda` no pináculo (−246, 372), topo 158) e `op_harbor` (H3, armazém de 2 pisos no topo da muralha (176, 120, 65,2)): CONFIRMADOS** (capturas 10 e 07) | — | 10, 07 |
| U14 | Atmosfera ref_03 | `roblox/AreaAtmosphere_area5.lua` (`profiles[5]`: hoje ClockTime 9,05, lat 10, ar azul (190, 216, 246)); `roblox/CeuWano.client.lua` (bloom, nuvens brancas, skybox padrão); `roblox/OnePieceIsland.lua` (1 emissor `FX_Petals_Tree`, rate 3); `op_vfx` (marcadores FX) | Ilha toda | 12 |
| U15 | Postes feios | `op_kit.lantern_post` (poste em T com 2 chochin); 28 chamadas em `op_capital`, `op_props`, `op_harbor`, `op_m2_trecho`, `op_entry` | Capital, praça, porto | 13 |
| U16 | Excesso de bandeiras | Praça: 4 cantos + 2 na escadaria (`op_m2_trecho`) + leste (`op_plaza.BANNERS_E`); estandartes (`op_props`); nobori da ponte e do pátio (`op_entry`, 2 + 2); santuário (`op_capital`, 2); rocha do castelo (`op_castle`, 2); torre do summon (`op_summon`, 2). Cerca de 20 no total. | Ilha toda | 14, 08 |

## Orçamento atual (export 37998c7c)

| Item | Valor |
|---|---|
| Tris | 619.745 / 640k |
| MeshParts | 541 / 650 |
| Colisões | 743 / 1.300 |
| Luzes ativas de dia | 8 / 36 |
| Sombra | 260 / 260 (no teto) |
| Capital | 178k tris / 141 MeshParts (no limite do dono) |
