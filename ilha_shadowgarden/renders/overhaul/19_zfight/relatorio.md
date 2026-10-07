# Auditoria de z-fighting - Ilha 3 Shadow Garden (export 58cdd0bf)

## Resumo (o que está piscando nas fotos)

1. **Janelas acesas (laranja) = CRÍTICO, causa confirmada:** o miolo das janelas pequenas do castelo é pintado em cima de
   uma face CEGA (fuste de torre, parede de ala, empena), sem vão. O cômodo aceso (`SG_VilRoom_Glow`, Neon) fica
   **0,00 a 0,02 atrás ou no plano da pedra** e o vidro âmbar/violeta/veneziana fica **+0,04 a +0,07 na frente**.
   No Roblox a pedra e o Neon disputam o mesmo pixel e a luz "treme", mais de longe. Fonte: `sg_castle.lancet_win()`
   (e `slit()`/`wlancet()`, que chamam `lancet_win`) e as chamadas de `sg_castle.window()` com `t_glass = ±0,02` em
   face cega. São 784 regiões em `SG_Cas_Torres`, `SG_Cas_Alas`, `SG_Cas_Coroa`, `SG_Cas_Muralha` (torres),
   `SG_Cas_Nave` (empenas e clerestório), `SG_Cas_Fachada` e `SG_Cas_Telhados` (lucarnas). A correção é deslocar
   o miolo para ficar pelo menos 0,12 na frente da face (F1).
2. **Suspeito nº 1 (`back_m` de obsidiana) = NÃO confirmado como causa da luz piscando.** Ele fica 0,16–0,18 atrás
   do cômodo aceso, o que é seguro até cerca de 300 studs. O único z-fight dele é interno: a face de dentro do
   `back_m` está no mesmo plano (d = 0) da face de dentro do mainel e da travessa violeta. Isso só se vê de dentro
   do salão, através do vitral (Glass 0,3), e soma ~97 studs² nas 8 janelas (F8).
3. **Muralhas = ALTO, 3 causas:**
   - **F3:** a base externa da muralha foi construída DUAS vezes. A alvenaria de arrimo do terreno
     (`sg_terrain.terrace_edges` → `masonry`, nos trechos `mur`) e o silhar da própria muralha
     (`sg_castle.muralha` → `ashlar`) estão a 0,03–0,04 um do outro, com juntas diferentes. É a face que o jogador
     vê subindo do P2 para o portão; ver render 03, onde aparecem as duas fiadas sobrepostas.
   - **F4:** a capa de obsidiana da cortina oeste tem o topo e as pontas no mesmo plano do corpo.
   - **F2:** os tampos dos anéis de coroamento das torres (`parapet_ring`: obsidiana × remate violeta × anel de
     prata do `spire`) estão no mesmo plano ou a 0,05.
4. **Pisos sobre o terreno = ALTO (F5), maior área:** ruas, praça, eixo nobre, pátio da dungeon e cabeça da saída
   ficam 0,01–0,13 acima do topo do patamar do terreno. A grama ou o calçamento do terreno pisca por cima, em
   ângulo rasante e de longe.
5. **Faces opostas (costas com costas):** 9.428 regiões e 165 mil studs². São **inertes**, porque a MeshPart é de
   face única e não pisca. Não precisam de correção.


Somente leitura: nenhum `sg_*.py` foi editado. Geometria = `ilha_shadowgarden.blend` de 30/09 00:40 (o build do export `58cdd0bf`, copiado para o scratchpad antes da análise). Coordenadas no **referencial do projeto** (Blender, 1 unidade = 1 stud, z para cima), antes da matriz `sg_layout.world_matrix()` do export.

## Como foi medido
- Detector headless (`zf_detect.py` + `zf_contact.py` no scratchpad `zf/`): as 125 malhas das coleções do export (`ER.GROUPS` do `export_sg.py`, mesmos `SKIP_PREFIX`), trianguladas no mundo (745.092 tris).
- O material de cada tri é o **material final do export**: alias + `variant_remap()` + núcleos de cristal + `_fold()` por objeto (materiais pequenos fundidos no vizinho) + regra `Glow -> Neon`. Dois tris com o mesmo material final não contam (mesma cor = z-fight invisível).
- Par candidato: BVH (`find_nearest_range` no centroide com raio = circunraio + 0,2), materiais finais diferentes, |dot das normais| > 0,995 e vértices a < 0,2 do plano. Area de interseção projetada por amostragem baricêntrica (passo 0,25) dentro do outro tri; guardadas 2 faixas: **< 0,05** (regra pedida) e **0,05-0,2** (só pisca de longe). Ocorrência = componente conexa (células de 3 studs) de um mesmo par objeto/material; descartadas < 0,05 studs2.
- Visível/oculto (heurística): face oposta coplanar no mesmo ponto = apoio/encosto -> oculto; exterior: algum raio do hemisfério da face (64 direções) sai para o céu; interior (salão, dungeon, alquimia): raio para cima não bate por tras numa face e algum raio sai livre. 8 amostras por ocorrência.
- Risco (`score`) = área x fração visível x contraste Roblox (dist. de cor sRGB + troca de Enum/transparencia) x faixa (coplanar 1; <0,05 0,6 fora / 0,2 dentro; 0,05-0,2 0,25 fora / 0,02 dentro) x 3 se Neon/luz.
- Profundidade no Roblox (estimativa, near 0,1, 24 bits): o gap que pisca cresce com a distância ao quadrado - ~0,02 a 100 studs, ~0,05 a 170, ~0,15 a 300 (mais em ângulo rasante). Por isso 0,02-0,06 pisca na praça olhando o castelo e 0,1-0,2 só pisca de muito longe.

## Totais
| | ocorrências | área (studs2) |
|---|---:|---:|
| pares de tris candidatos (planos paralelos a < 0,2, materiais diferentes) | 1.810.811 | - |
| ocorrências (regiões sobrepostas >= 0,05 studs2) | 15797 | 294109,49 |
| mesmo sentido, visíveis | 3021 | 88966,20 |
| mesmo sentido, ocultas | 3348 | 39629,73 |
| mesmo sentido, visíveis e < 0,05 | 990 | 17541,29 |
| mesmo sentido, visíveis e coplanares exatas (< 0,005) | 241 | 5270,06 |
| faces opostas (costas com costas / apoio) - inertes no Roblox | 9428 | 165513,55 |

## Grupos por gravidade (famílias de causa)
| fam. | gravidade | o que é | ocorr. | área | área visível | score | gap (min-max) | objetos principais |
|---|---|---|---:|---:|---:|---:|---|---|
| F1 | **CRÍTICO** | Janelas acesas pintadas numa face CEGA do castelo (luz/vidro a -0,02..+0,07 da pedra) | 784 | 2768,21 | 1705,01 | 1462,92 | 0,00-0,20 | `SG_Cas_Coroa`, `SG_Cas_Alas`, `SG_Cas_Nave`, `SG_Cas_Torres` |
| F5 | **ALTO** | Pisos (rua, praça, eixo nobre, pátio da dungeon, saída) sobre o topo do patamar do terreno | 104 | 18894,61 | 11697,14 | 2169,51 | 0,00-0,20 | `SG_Ter_Terrace_P2`, `SG_Ter_Terrace_P1`, `SG_Ter_Terrace_P3`, `SG_Vil_Streets_P2` |
| F2 | **ALTO** | Tampos coplanares em aneis de coroamento (obsidiana x remate violeta x anel de prata) | 111 | 10243,13 | 900,87 | 615,11 | 0,00-0,20 | `SG_Cas_Alas`, `SG_Cas_Torres`, `SG_Cas_Coroa`, `SG_Cas_Muralha` |
| F4 | **ALTO** | Capa de obsidiana da cortina oeste com topo e pontas no plano do corpo | 8 | 501,00 | 335,93 | 271,38 | 0,00-0,14 | `SG_Cas_Muralha` |
| F3 | **ALTO** | Base da MURALHA vestida duas vezes (arrimo do terreno + silhar da muralha no mesmo plano) | 31 | 413,17 | 251,58 | 13,86 | 0,00-0,20 | `SG_Ter_Wall_P3`, `SG_Cas_Muralha` |
| F5b | **MÉDIO** | Camadas do próprio piso quase coplanares (leito x paralelepípedo x laje x faixa) | 64 | 6208,33 | 5588,85 | 579,87 | 0,00-0,20 | `SG_Vil_Streets_P2`, `SG_Vil_Plaza`, `SG_Vil_Streets_P1`, `SG_Prop_NobleAxis_P2P3` |
| F6 | **MÉDIO** | Outras faces coplanares no castelo (frisos, faixas, cordões, mainel, pontas de caixa) | 722 | 10261,72 | 1951,75 | 274,71 | 0,00-0,20 | `SG_Cas_Muralha`, `SG_Cas_Alas`, `SG_Cas_Nave`, `SG_Cas_Torres` |
| F12 | **MÉDIO** | Summon | 273 | 1593,54 | 564,95 | 209,36 | 0,00-0,20 | `SG_Sum_Tower_Stone`, `SG_Sum_Bridge`, `SG_Sum_Base`, `SG_Sum_Tower_Silver` |
| F10 | **MÉDIO** | Salão (interior) | 609 | 4383,54 | 1340,09 | 179,24 | 0,00-0,20 | `SG_Hall_Altar`, `SG_Hall_Walls`, `SG_Hall_Windows`, `SG_Hall_Floor` |
| F8 | **MÉDIO** | `back_m` (fundo de obsidiana das janelas da nave) - SUSPEITO nº 1 | 16 | 1132,17 | 0,00 | 0,00 | 0,00-0,18 | `SG_Cas_Nave` |
| F14 | **BAIXO** | Casas da vila | 1259 | 10102,80 | 1238,08 | 303,63 | 0,00-0,20 | `SG_Vil_Houses_P1E`, `SG_Vil_Houses_P2W`, `SG_Vil_Houses_P1W`, `SG_Vil_Houses_P2E` |
| F15 | **BAIXO** | Terreno (arrimos com variantes, falésias) | 396 | 4392,47 | 1280,38 | 285,05 | 0,00-0,20 | `SG_Ter_Mounds`, `SG_Ter_Cliff_N`, `SG_Ter_Wall_P2`, `SG_Ter_Wall_P3` |
| F16 | **BAIXO** | Outros | 550 | 8471,70 | 1582,25 | 251,71 | 0,00-0,20 | `SG_Exit_Bridge`, `SG_Ent_Parapets`, `SG_Prop_NobleAxis_P2P3`, `SG_Ent_Bridge` |
| F11 | **BAIXO** | Dungeon (interior e túneis) | 540 | 25711,66 | 8767,42 | 183,67 | 0,00-0,20 | `SG_Dun_Rooms_Floor`, `SG_Dun_Rooms_Kit`, `SG_Dun_Rooms_Shell`, `SG_Dun_Approach_Floor` |
| F13 | **BAIXO** | Alquimia | 549 | 4608,04 | 1903,39 | 117,82 | 0,00-0,20 | `SG_Craft_Furnishings`, `SG_Craft_Shell`, `SG_Craft_Cauldron`, `SG_Craft_Dome` |
| F9 | **BAIXO** | Faces de baixo (normal para baixo) coplanares no castelo | 308 | 8954,38 | 185,17 | 100,88 | 0,00-0,20 | `SG_Cas_Alas`, `SG_Cas_Muralha`, `SG_Cas_Torres`, `SG_Cas_Coroa` |
| F7 | **BAIXO** | Face interna da nave (Stone_SGCasInterior) 0,10 atrás das paredes/abobada/altar do salão | 45 | 9955,47 | 8603,62 | 95,77 | 0,10-0,20 | `SG_Cas_Nave`, `SG_Hall_Walls`, `SG_Hall_Vault`, `SG_Hall_Altar` |
| F0 | **INERTE** | Faces OPOSTAS coplanares (duas cascas encostadas de costas / face apoiada em face) | 9428 | 165513,56 | 31442,63 | 0,00 | 0,00-0,20 | `SG_Cas_Nave`, `SG_Cas_Muralha`, `SG_Cas_Alas`, `SG_Exit_Bridge` |

## Origem e correção por família
### F1 - Janelas acesas pintadas numa face CEGA do castelo (luz/vidro a -0,02..+0,07 da pedra) (CRÍTICO)
- **Origem:** `sg_castle.lancet_win()` (também via `slit()`/`wlancet()`) e `sg_castle.window()` chamada com `t_glass=+-0,02, t_out=0` em face sem vão: torres `towers()` (l.1693), coroa `crown()` (l.1852, 1860, 1879, 1915), alas `wings()` (l.1988, 1999, 2017), telhados `roofs()` (l.1393, 1420), muralha (seteiras das torres), fachada (empenas `wlancet(t=TW+0,02)` l.1147/1173) e clerestório da nave (`window(..., 2.05, 2.0)` l.1230)
- **Correção:** No `lancet_win`: somar +0,14 a TODOS os t do miolo (cômodo `ROOM` t-0,16..t-0,02 -> t-0,02..t+0,12; `Window_Warm`/vidro t-0,10..t+0,04 -> t+0,04..t+0,18; chumbo t+0,04..t+0,12 -> t+0,18..t+0,26). A moldura (`dp` >= 0,22) continua mais saliente. Nas chamadas de `window()` em face cega trocar `t_glass` -0,02/0,02 por **0,16** (cômodo na frente a 0,18, vidro/veneziana/violeta a 0,24); clerestório: `t_glass` 2,05 -> 2,20. Regra: nada de miolo a menos de 0,12 da face que ele cobre.

### F5 - Pisos (rua, praça, eixo nobre, pátio da dungeon, saída) sobre o topo do patamar do terreno (ALTO)
- **Origem:** `sg_terrain` (topo dos `SG_Ter_Terrace_P1/P2/P3/Entry`) x `sg_village.plaza()` (leito `z+0,02`), `sg_village` ruas (`prism(poly, z-0,25, z+0,05, M_JNT/M_COB)`), `sg_court` eixo nobre (`SG_Prop_NobleAxis_*`), `sg_dungeon` `SG_Dun_Approach_Floor`, `sg_exit` `SG_Exit_Head`, `sg_garden` `SG_Veg_Gdn_LawnTone`: 0,01-0,13 acima do topo do patamar; de longe/em ângulo rasante o verde ou o calçamento do terreno pisca por cima
- **Correção:** Preferido: o terreno NAO emite o topo sob os pisos (recortar o polígono do patamar pelos pisos) ou baixa esse trecho do topo 0,3. Alternativa: pisos com leito >= +0,12 acima do patamar.

### F2 - Tampos coplanares em aneis de coroamento (obsidiana x remate violeta x anel de prata) (ALTO)
- **Origem:** `sg_castle.parapet_ring()` (frustum do corpo OB `z0..z0+h` com tampa + frustum `cap_m` VI `z0+h-0,45..z0+h`: os dois tampos em z0+h); a mesma receita solta em `crown()` (l.1861-1862 e 1905-1906), passagem leste (l.952-953); `spire()` poe o anel de prata `z0-0,35..z0+0,05` 0,05 acima desse tampo
- **Correção:** Corpo do parapeito com `top=False` (o tampo do remate VI fica sozinho) OU remate subindo +0,04 (`z0+h-0,45 .. z0+h+0,04`); no `spire()` o anel do beiral vai a `z0+0,15` (0,15 acima do tampo) ou afunda inteiro abaixo dele. Mesma troca nas 3 cópias soltas.

### F4 - Capa de obsidiana da cortina oeste com topo e pontas no plano do corpo (ALTO)
- **Origem:** `sg_castle.muralha()`, bloco 'torre de canto sudoeste + cortina oeste': `mb.box((ln+th, th+0.8, 1.2), ..., top-0.6)` OB tem o MESMO topo (Z+10) e as mesmas pontas (ln+th) do corpo `mb.box((ln+th, th, top-ZT), ...)` Stone_SG_Block
- **Correção:** Capa sobe 0,06 (centro `top-0,54`) e fica 0,1 mais comprida (`ln+th+0,1`) -> sem tampo nem ponta coplanar; ou encurtar o corpo 0,1 nas pontas.

### F3 - Base da MURALHA vestida duas vezes (arrimo do terreno + silhar da muralha no mesmo plano) (ALTO)
- **Origem:** `sg_terrain.terrace_edges()` -> `masonry()` nos trechos `R['mur']` (face do P3 sob a muralha) E `sg_castle.muralha()` -> `ashlar(mb, Wo, ..., Z2+3,56 .. Z-0,72)` na face externa (`front = wy0-0,3`): blocos a 0,03-0,04 um do outro, com juntas diferentes, y ~ -9,4, x 8..106 e -80..-8, z 47,9..51,4
- **Correção:** Tirar a alvenaria do terreno onde a muralha já veste a face: em `terrace_edges`, para `R['mur']`, não chamar `masonry()` (nem `buttresses()`) acima de Z2+3,5; OU recuar o arrimo 0,15 para dentro. O cordão CAPL do arrimo fica.

### F5b - Camadas do próprio piso quase coplanares (leito x paralelepípedo x laje x faixa) (MÉDIO)
- **Origem:** `sg_village.plaza()`/`slab_ring()` (leito z+0,02, lajes z+0,07), ruas (leito e peças no mesmo topo z+0,05), `sg_court` eixo nobre (mármore x obsidiana 0,025), `sg_dungeon` approach (mármore x obsidiana), `SG_Prop_Court` (terra x cascalho 0,04)
- **Correção:** Diferença mínima de 0,08 entre camadas vistas de cima (leito sempre >= 0,08 abaixo da peça). Contraste baixo na maioria (dc ~13-30): prioridade depois de F1-F5.

### F6 - Outras faces coplanares no castelo (frisos, faixas, cordões, mainel, pontas de caixa) (MÉDIO)
- **Origem:** `sg_castle` (várias: faixas SIDE_BANDS, `ledge`/`panel` com a mesma cota da parede, cunhais das alas, `socle()` com anel de prata `z1-0,05`, `wings()` com as caixas soco/cornija alinhadas no mesmo x da ala leste `ex0`)
- **Correção:** Caso a caso: recuar 0,05-0,1 a peça de tras ou encurtar a ponta 0,1. Ver a lista das piores.

### F12 - Summon (MÉDIO)
- **Origem:** `sg_summon`
- **Correção:** Glow do portal 0,05-0,16 sobre o piso: recuar o piso ou subir o glow para >= 0,12

### F10 - Salão (interior) (MÉDIO)
- **Origem:** `sg_hall` (walls/ribs/floor)
- **Correção:** Recuar 0,05 a faixa/cordao que está na mesma cota da parede (ex.: `SG_Hall_Walls` Castle_B x Obsidian em y 44,0, z ~87)

### F8 - `back_m` (fundo de obsidiana das janelas da nave) - SUSPEITO nº 1 (MÉDIO)
- **Origem:** `sg_castle.window(..., back_m=OB)` (l.267-271) chamado em `nave()` l.1090
- **Correção:** Não é a causa da luz laranja piscando. O único z-fight real: a face de DENTRO do `back_m` (t_glass-0,30) está no mesmo plano da face de dentro do mainel e da travessa (t_glass-0,30, Stone_SG_Violet), visível só de dentro do salão pelo vitral. Correção: `back_m` de `t_glass-0,28` a `t_glass-0,16`.

### F14 - Casas da vila (BAIXO)
- **Origem:** `sg_village`
- **Correção:** Soco Block_B x Obsidian a 0,10-0,16, reboco x madeira 0,15-0,2: baixo contraste/distancia.

### F15 - Terreno (arrimos com variantes, falésias) (BAIXO)
- **Origem:** `sg_terrain`
- **Correção:** Variantes do mesmo tom; baixo.

### F16 - Outros (BAIXO)
- **Origem:** -
- **Correção:** -

### F11 - Dungeon (interior e túneis) (BAIXO)
- **Origem:** `sg_dungeon`
- **Correção:** Gaps de 0,12-0,2 vistos de perto: baixo risco.

### F13 - Alquimia (BAIXO)
- **Origem:** `sg_craft`
- **Correção:** Janelas Window_Warm a 0,06-0,11 da parede escura: levar a >= 0,12.

### F9 - Faces de baixo (normal para baixo) coplanares no castelo (BAIXO)
- **Origem:** vários
- **Correção:** Só se veem de baixo; ignorar.

### F7 - Face interna da nave (Stone_SGCasInterior) 0,10 atrás das paredes/abobada/altar do salão (BAIXO)
- **Origem:** `sg_castle.nave()` `wall_run(..., inner_m=IM)` x `sg_hall.walls()/vault()/altar()`
- **Correção:** Visto só de dentro (< ~100 studs): 0,10 aguenta. Otimização: não gerar a face IM onde o salão cobre.

### F0 - Faces OPOSTAS coplanares (duas cascas encostadas de costas / face apoiada em face) (INERTE)
- **Origem:** todos os módulos
- **Correção:** MeshPart do Roblox é de face única (DoubleSided = false): de cada lado só uma das duas faces é desenhada, então NAO pisca. Não precisa corrigir.

## Agrupamento por par de objeto x material (mesmo sentido, 45 maiores por risco)
| # | fam. | objeto A / material A | objeto B / material B | ocorr. | área | área vis. | gap | contraste | score | pior (centro) |
|---:|---|---|---|---:|---:|---:|---|---:|---:|---|
| 1 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SG_Floor | 3 | 2204,02 | 1929,18 | 0,05-0,05 | 88 | 424,67 | (-57,9; -44,5; 44,2) |
| 2 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SGVilCobble | 3 | 1740,70 | 1677,17 | 0,09-0,09 | 100 | 419,29 | (-58,1; -44,5; 44,2) |
| 3 | F1 | `SG_Cas_Coroa` / SG_VioletSoft_Glow | `SG_Cas_Coroa` / Stone_SG_Castle_B | 12 | 522,67 | 412,36 | 0,04-0,06 | 92 | 288,13 | (-12,1; 151,1; 169,1) |
| 4 | F2 | `SG_Cas_Torres` / Stone_SG_Obsidian | `SG_Cas_Torres` / Stone_SG_Violet | 12 | 1660,62 | 328,16 | 0,00-0,18 | 91 | 273,32 | (58,0; 42,0; 110,5) |
| 5 | F1 | `SG_Cas_Alas` / SG_VilRoom_Glow | `SG_Cas_Alas` / Stone_SG_Castle | 55 | 151,85 | 134,62 | 0,02-0,04 | 150 | 242,32 | (60,5; 59,0; 57,3) |
| 6 | F5 | `SG_Dun_Approach_Floor` / Stone_SG_Obsidian | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | 1 | 1233,19 | 924,89 | 0,07-0,13 | 99 | 230,39 | (100,0; 46,5; 52,2) |
| 7 | F1 | `SG_Cas_Torres` / SG_VilRoom_Glow | `SG_Cas_Torres` / Stone_SG_Castle | 44 | 107,64 | 83,47 | 0,00-0,02 | 150 | 195,87 | (-67,2; 42,0; 132,4) |
| 8 | F4 | `SG_Cas_Muralha` / Stone_SG_Block | `SG_Cas_Muralha` / Stone_SG_Obsidian | 37 | 1102,06 | 261,07 | 0,00-0,19 | 123 | 181,65 | (-80,2; 16,1; 62,0) |
| 9 | F5 | `SG_Dun_Approach_Floor` / Stone_SG_MarbleBlack | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | 1 | 800,87 | 800,87 | 0,13-0,13 | 78 | 157,65 | (100,0; 43,6; 52,2) |
| 10 | F1 | `SG_Cas_Nave` / SG_VilRoom_Glow | `SG_Cas_Nave` / Stone_SG_Castle | 32 | 120,92 | 106,64 | 0,00-0,07 | 150 | 152,53 | (-22,0; 82,4; 124,0) |
| 11 | F2 | `SG_Cas_Muralha` / Stone_SG_Obsidian | `SG_Cas_Muralha` / Stone_SG_Violet | 20 | 1031,99 | 172,34 | 0,00-0,19 | 91 | 129,71 | (-82,0; 16,0; 78,0) |
| 12 | F5b | `SG_Vil_Streets_P2` / Stone_SGVilCobble | `SG_Vil_Streets_P2` / Stone_SG_Floor | 10 | 1738,87 | 1673,98 | 0,00-0,20 | 12 | 128,57 | (-58,0; -44,5; 44,2) |
| 13 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Dirt_SG | 6 | 290,93 | 285,57 | 0,03-0,03 | 71 | 122,64 | (-58,2; -49,3; 44,2) |
| 14 | F1 | `SG_Cas_Torres` / Stone_SG_Castle | `SG_Cas_Torres` / Window_Warm | 44 | 106,07 | 96,39 | 0,04-0,06 | 139 | 115,78 | (-58,0; 32,8; 136,1) |
| 15 | F5 | `SG_Exit_Head` / Stone_Paving_SG | `SG_Ter_Terrace_P2` / Grass_SG_B | 1 | 249,18 | 190,78 | 0,03-0,03 | 134 | 114,47 | (152,2; -38,0; 44,2) |
| 16 | F5 | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | 1 | 866,32 | 433,16 | 0,01-0,05 | 99 | 107,90 | (0,1; 16,2; 52,2) |
| 17 | F4 | `SG_Cas_Muralha` / Stone_SG_Block_B | `SG_Cas_Muralha` / Stone_SG_Obsidian | 9 | 163,04 | 101,57 | 0,00-0,20 | 109 | 101,57 | (-70,4; 50,4; 62,0) |
| 18 | F5 | `SG_Ter_Terrace_P1` / Stone_Paving_SG_B | `SG_Vil_Plaza` / Stone_SG_Floor | 1 | 2106,93 | 526,73 | 0,02-0,02 | 30 | 95,86 | (-0,0; -128,0; 36,2) |
| 19 | F5b | `SG_Prop_NobleAxis_P2P3` / Stone_SG_MarbleBlack | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | 6 | 1510,65 | 757,54 | 0,03-0,15 | 20 | 93,65 | (-0,0; -54,5; 44,2) |
| 20 | F2 | `SG_Cas_Coroa` / Stone_SG_Obsidian | `SG_Cas_Coroa` / Stone_SG_Violet | 13 | 1768,79 | 131,55 | 0,00-0,19 | 91 | 92,17 | (-0,0; 158,0; 143,6) |
| 21 | F1 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / Wood_SG_Dark | 6 | 386,34 | 354,14 | 0,06-0,06 | 100 | 88,54 | (-7,0; 170,1; 169,1) |
| 22 | F5b | `SG_Vil_Streets_P1` / Stone_SGVilCobble | `SG_Vil_Streets_P1` / Stone_SG_Floor | 4 | 1123,34 | 1123,02 | 0,04-0,06 | 12 | 86,26 | (67,2; -118,5; 36,2) |
| 23 | F1 | `SG_Cas_Alas` / Stone_SG_Castle | `SG_Cas_Alas` / Window_Warm | 55 | 165,61 | 57,69 | 0,04-0,10 | 139 | 77,09 | (60,5; 104,0; 59,7) |
| 24 | F12 | `SG_Sum_Tower_Glow` / SG_SumPortalDeep_Glow | `SG_Sum_Tower_Stone` / Stone_SG_Floor | 3 | 121,73 | 100,95 | 0,05-0,16 | 96 | 72,82 | (-157,8; -118,0; 66,6) |
| 25 | F5 | `SG_Ter_Terrace_P1` / Stone_Paving_SG_B | `SG_Vil_Streets_P1` / Stone_SG_Floor | 2 | 1512,82 | 945,33 | 0,05-0,05 | 30 | 71,68 | (-60,5; -118,9; 36,2) |
| 26 | F15 | `SG_Cas_Muralha` / Stone_SG_Obsidian | `SG_Ter_Terrace_P2` / Cliff_Rock_SG_Dark | 1 | 110,52 | 110,52 | 0,00-0,00 | 62 | 68,62 | (-80,5; -8,1; 33,0) |
| 27 | F5b | `SG_Prop_NobleAxis_P2P3` / Metal_SG_Silver | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | 5 | 174,27 | 106,91 | 0,00-0,15 | 304 | 64,15 | (0,0; 20,3; 52,1) |
| 28 | F2 | `SG_Cas_Alas` / Stone_SG_Obsidian | `SG_Cas_Alas` / Stone_SG_Violet | 8 | 658,25 | 84,93 | 0,00-0,18 | 91 | 63,29 | (-95,0; 133,0; 104,0) |
| 29 | F11 | `SG_Dun_Rooms_Kit` / Stone_SGDunVault | `SG_Dun_Rooms_Shell` / Stone_SG_Castle | 15 | 3698,45 | 3426,35 | 0,12-0,18 | 84 | 58,07 | (-51,0; 101,9; 8,8) |
| 30 | F10 | `SG_Hall_Walls` / Stone_SG_Castle_B | `SG_Hall_Walls` / Stone_SG_Obsidian | 45 | 112,73 | 67,86 | 0,00-0,15 | 91 | 56,94 | (18,0; 44,0; 87,2) |
| 31 | F5 | `SG_Dun_Cave_Interior` / Stone_SG_Obsidian | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | 1 | 334,72 | 219,66 | 0,06-0,06 | 99 | 54,72 | (100,0; 65,7; 52,2) |
| 32 | F5 | `SG_Ter_Terrace_P1` / Stone_Paving_SG_B | `SG_Vil_Streets_P1` / Stone_SGVilCobble | 2 | 1127,70 | 1127,70 | 0,09-0,09 | 18 | 50,75 | (67,3; -118,4; 36,2) |
| 33 | F5 | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | `SG_Ter_Terrace_P2` / Grass_SG_B | 1 | 777,53 | 291,57 | 0,02-0,05 | 68 | 49,94 | (0,0; -54,5; 44,2) |
| 34 | F5b | `SG_Vil_Plaza` / Stone_Paving_SG_B | `SG_Vil_Plaza` / Stone_SG_Floor | 1 | 654,74 | 654,74 | 0,05-0,05 | 30 | 49,65 | (0,0; -128,0; 36,2) |
| 35 | F5 | `SG_Dun_Cave_Interior` / Stone_SG_MarbleBlack | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | 1 | 251,83 | 251,83 | 0,12-0,12 | 78 | 49,57 | (100,0; 65,6; 52,2) |
| 36 | F13 | `SG_Craft_Furnishings` / Stone_SG_Castle_B | `SG_Craft_Shell` / Stone_SGCraftDark | 1 | 1014,15 | 554,61 | 0,05-0,05 | 44 | 48,91 | (92,5; -60,0; 54,4) |
| 37 | F15 | `SG_Cas_Muralha` / Stone_SG_Obsidian | `SG_Ter_Terrace_P3` / Cliff_Rock_SG_Dark | 4 | 98,06 | 72,05 | 0,00-0,10 | 62 | 44,74 | (-76,9; -4,8; 33,0) |
| 38 | F5 | `SG_Prop_NobleAxis_P2P3` / Metal_SG_Silver | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | 3 | 81,52 | 81,09 | 0,03-0,06 | 205 | 44,50 | (0,2; 20,1; 52,2) |
| 39 | F5 | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Floor | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | 2 | 471,99 | 235,21 | 0,03-0,03 | 30 | 42,81 | (-27,6; 20,1; 52,2) |
| 40 | F15 | `SG_Cas_Alas` / Stone_SG_Obsidian | `SG_Ter_Terrace_P3` / Cliff_Rock_SG_Dark | 2 | 68,10 | 63,40 | 0,00-0,00 | 62 | 39,36 | (55,3; 150,8; 33,0) |
| 41 | F5b | `SG_Prop_NobleAxis_P1` / Stone_SG_MarbleBlack | `SG_Prop_NobleAxis_P1` / Stone_SG_Obsidian | 4 | 629,36 | 305,24 | 0,03-0,15 | 20 | 38,42 | (-0,0; -170,3; 36,2) |
| 42 | F1 | `SG_Cas_Muralha` / SG_VilRoom_Glow | `SG_Cas_Muralha` / Stone_SG_Castle | 18 | 27,42 | 20,72 | 0,02-0,02 | 150 | 37,30 | (-19,1; -7,9; 80,9) |
| 43 | F14 | `SG_Vil_Houses_P2W` / Stone_SG_Block_B | `SG_Vil_Houses_P2W` / Stone_SG_Obsidian | 3 | 430,75 | 148,76 | 0,10-0,16 | 109 | 37,19 | (-62,0; -66,0; 45,1) |
| 44 | F14 | `SG_Vil_Houses_P1W` / Stone_SG_Block_B | `SG_Vil_Houses_P1W` / Stone_SG_Obsidian | 3 | 430,75 | 145,12 | 0,10-0,16 | 109 | 36,28 | (-50,0; -146,0; 37,1) |
| 45 | F14 | `SG_Vil_Houses_P1E` / Stone_SG_Block_B | `SG_Vil_Houses_P1E` / Stone_SG_Obsidian | 3 | 430,75 | 142,54 | 0,10-0,16 | 109 | 35,64 | (72,0; -94,0; 37,1) |

## As 30 piores ocorrências (mesmo sentido, por risco)
| # | fam. | A | B | área | gap | visível | centro (x; y; z) | normal | caixa min .. max |
|---:|---|---|---|---:|---|---:|---|---|---|
| 1 | F5 | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | `SG_Dun_Approach_Floor` / Stone_SG_Obsidian | 1233,19 | 0,07-0,13 | 75% | (100,0; 46,5; 52,2) | (0,0; 0,0; 1,0) | (78,0; 23,0; 52,2) .. (122,0; 59,0; 52,2) |
| 2 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SG_Floor | 936,73 | 0,05-0,05 | 88% | (-57,9; -44,5; 44,2) | (0,0; 0,0; 1,0) | (-110,0; -49,5; 44,2) .. (-6,0; -39,7; 44,2) |
| 3 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SGVilCobble | 721,14 | 0,09-0,09 | 100% | (-58,1; -44,5; 44,2) | (0,0; 0,0; 1,0) | (-110,0; -48,8; 44,2) .. (-6,3; -40,2; 44,2) |
| 4 | F5 | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | `SG_Dun_Approach_Floor` / Stone_SG_MarbleBlack | 800,87 | 0,13-0,13 | 100% | (100,0; 43,6; 52,2) | (0,0; 0,0; 1,0) | (78,2; 23,1; 52,2) .. (121,8; 58,9; 52,2) |
| 5 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SG_Floor | 636,29 | 0,05-0,05 | 100% | (130,5; -37,5; 44,2) | (0,0; -0,0; 1,0) | (103,7; -44,0; 44,2) .. (157,0; -30,3; 44,2) |
| 6 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SGVilCobble | 511,35 | 0,09-0,09 | 100% | (130,4; -37,5; 44,2) | (0,0; -0,0; 1,0) | (103,7; -43,4; 44,2) .. (156,9; -30,8; 44,2) |
| 7 | F2 | `SG_Cas_Torres` / Stone_SG_Obsidian | `SG_Cas_Torres` / Stone_SG_Violet | 337,40 | 0,00-0,00 | 38% | (58,0; 42,0; 110,5) | (0,0; 0,0; 1,0) | (48,0; 32,0; 110,5) .. (68,0; 52,0; 110,5) |
| 8 | F2 | `SG_Cas_Torres` / Stone_SG_Obsidian | `SG_Cas_Torres` / Stone_SG_Violet | 336,05 | 0,00-0,00 | 38% | (-58,0; 42,0; 110,5) | (0,0; 0,0; 1,0) | (-68,0; 32,0; 110,5) .. (-48,0; 52,0; 110,5) |
| 9 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Exit_Head` / Stone_Paving_SG | 249,18 | 0,03-0,03 | 77% | (152,2; -38,0; 44,2) | (0,0; -0,0; 1,0) | (147,5; -51,1; 44,2) .. (157,0; -24,9; 44,2) |
| 10 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SGVilCobble | 508,21 | 0,09-0,09 | 88% | (41,2; -47,3; 44,2) | (0,0; 0,0; 1,0) | (6,2; -63,1; 44,2) .. (73,6; -41,2; 44,2) |
| 11 | F5 | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | 866,32 | 0,01-0,05 | 50% | (0,1; 16,2; 52,2) | (0,0; 0,0; 1,0) | (-39,9; -8,9; 52,2) .. (43,1; 40,0; 52,2) |
| 12 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Vil_Streets_P2` / Stone_SG_Floor | 631,00 | 0,05-0,05 | 75% | (40,8; -47,2; 44,2) | (0,0; 0,0; 1,0) | (6,0; -63,4; 44,2) .. (74,1; -40,7; 44,2) |
| 13 | F4 | `SG_Cas_Muralha` / Stone_SG_Block_B | `SG_Cas_Muralha` / Stone_SG_Obsidian | 154,77 | 0,00-0,00 | 66% | (-70,4; 50,4; 62,0) | (-0,0; 0,0; 1,0) | (-81,6; 38,8; 61,0) .. (-58,9; 63,5; 62,2) |
| 14 | F4 | `SG_Cas_Muralha` / Stone_SG_Block | `SG_Cas_Muralha` / Stone_SG_Obsidian | 258,20 | 0,00-0,05 | 62% | (-80,2; 16,1; 62,0) | (-1,0; 0,0; 0,0) | (-83,5; -10,7; 60,0) .. (-77,9; 41,8; 66,2) |
| 15 | F5 | `SG_Ter_Terrace_P1` / Stone_Paving_SG_B | `SG_Vil_Plaza` / Stone_SG_Floor | 2106,93 | 0,02-0,02 | 25% | (-0,0; -128,0; 36,2) | (0,0; -0,0; 1,0) | (-25,7; -153,7; 36,2) .. (25,8; -102,2; 36,2) |
| 16 | F2 | `SG_Cas_Coroa` / Stone_SG_Obsidian | `SG_Cas_Coroa` / Stone_SG_Violet | 858,65 | 0,00-0,00 | 9% | (-0,0; 158,0; 143,6) | (0,0; -0,0; 1,0) | (-16,3; 141,7; 143,6) .. (16,3; 174,3; 143,6) |
| 17 | F15 | `SG_Ter_Terrace_P2` / Cliff_Rock_SG_Dark | `SG_Cas_Muralha` / Stone_SG_Obsidian | 110,52 | 0,00-0,00 | 100% | (-80,5; -8,1; 33,0) | (0,0; 0,0; -1,0) | (-87,4; -13,1; 33,0) .. (-73,7; -4,2; 33,0) |
| 18 | F5b | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | `SG_Prop_NobleAxis_P2P3` / Metal_SG_Silver | 168,81 | 0,00-0,05 | 62% | (0,0; 20,3; 52,1) | (-0,0; 0,0; 1,0) | (-10,2; 10,7; 52,1) .. (10,2; 29,7; 52,2) |
| 19 | F5b | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | `SG_Prop_NobleAxis_P2P3` / Stone_SG_MarbleBlack | 476,97 | 0,03-0,03 | 100% | (-0,0; -54,5; 44,2) | (-0,0; 0,0; 1,0) | (-4,9; -82,9; 44,2) .. (4,9; -26,1; 44,2) |
| 20 | F5b | `SG_Vil_Streets_P2` / Stone_SG_Floor | `SG_Vil_Streets_P2` / Stone_SGVilCobble | 721,76 | 0,04-0,04 | 100% | (-58,0; -44,5; 44,2) | (0,0; 0,0; 1,0) | (-109,9; -48,8; 44,2) .. (-6,2; -40,2; 44,2) |
| 21 | F5 | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | `SG_Dun_Cave_Interior` / Stone_SG_Obsidian | 334,72 | 0,06-0,06 | 66% | (100,0; 65,7; 52,2) | (0,0; 0,0; 1,0) | (88,0; 58,9; 52,2) .. (112,0; 72,5; 52,2) |
| 22 | F5 | `SG_Ter_Terrace_P2` / Grass_SG_B | `SG_Prop_NobleAxis_P2P3` / Stone_SG_Obsidian | 777,53 | 0,02-0,05 | 38% | (0,0; -54,5; 44,2) | (0,0; -0,0; 1,0) | (-6,0; -82,8; 44,2) .. (6,0; -26,1; 44,2) |
| 23 | F5b | `SG_Vil_Plaza` / Stone_Paving_SG_B | `SG_Vil_Plaza` / Stone_SG_Floor | 654,74 | 0,05-0,05 | 100% | (0,0; -128,0; 36,2) | (-0,0; 0,0; 1,0) | (-22,9; -150,9; 36,2) .. (22,9; -105,1; 36,2) |
| 24 | F5 | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | `SG_Dun_Cave_Interior` / Stone_SG_MarbleBlack | 251,83 | 0,12-0,12 | 100% | (100,0; 65,6; 52,2) | (0,0; 0,0; 1,0) | (88,8; 59,2; 52,2) .. (111,2; 72,4; 52,2) |
| 25 | F13 | `SG_Craft_Furnishings` / Stone_SG_Castle_B | `SG_Craft_Shell` / Stone_SGCraftDark | 1014,15 | 0,05-0,05 | 55% | (92,5; -60,0; 54,4) | (0,8; 0,6; 0,0) | (78,5; -73,3; 47,2) .. (103,3; -46,6; 61,6) |
| 26 | F5b | `SG_Vil_Streets_P1` / Stone_SG_Floor | `SG_Vil_Streets_P1` / Stone_SGVilCobble | 595,84 | 0,04-0,04 | 100% | (67,2; -118,5; 36,2) | (0,0; 0,0; 1,0) | (24,4; -123,8; 36,2) .. (110,2; -112,2; 36,2) |
| 27 | F5 | `SG_Ter_Terrace_P3` / Stone_Paving_SG_B | `SG_Prop_NobleAxis_P2P3` / Metal_SG_Silver | 69,22 | 0,03-0,05 | 100% | (0,2; 20,1; 52,2) | (0,0; 0,0; 1,0) | (-9,5; 11,0; 52,2) .. (9,4; 28,6; 52,2) |
| 28 | F5 | `SG_Ter_Terrace_P1` / Stone_Paving_SG_B | `SG_Vil_Streets_P1` / Stone_SG_Floor | 711,24 | 0,05-0,05 | 77% | (-60,5; -118,9; 36,2) | (0,0; 0,0; 1,0) | (-99,9; -124,4; 36,2) .. (-21,0; -113,5; 36,2) |
| 29 | F5b | `SG_Vil_Streets_P1` / Stone_SG_Floor | `SG_Vil_Streets_P1` / Stone_SGVilCobble | 526,46 | 0,04-0,04 | 100% | (-62,2; -119,0; 36,2) | (0,0; 0,0; 1,0) | (-100,1; -123,8; 36,2) .. (-24,4; -114,2; 36,2) |
| 30 | F5b | `SG_Vil_Streets_P2` / Stone_SG_Floor | `SG_Vil_Streets_P2` / Stone_SGVilCobble | 514,08 | 0,04-0,04 | 100% | (130,5; -37,5; 44,2) | (0,0; -0,0; 1,0) | (103,7; -43,4; 44,2) .. (156,9; -30,7; 44,2) |

### Janelas e luz (F1): as 20 piores por janela (cada linha = 1 janela / 1 regiao)
| # | A | B | área | gap | visível | centro (x; y; z) | normal |
|---:|---|---|---:|---|---:|---|---|
| 1 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 64,39 | 0,06-0,06 | 88% | (-12,1; 151,1; 169,1) | (-0,9; -0,5; 0,0) |
| 2 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 64,39 | 0,06-0,06 | 88% | (12,1; 151,1; 169,1) | (0,9; -0,5; 0,0) |
| 3 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 64,39 | 0,06-0,06 | 75% | (-12,1; 164,9; 169,1) | (-0,9; 0,5; 0,0) |
| 4 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 64,39 | 0,06-0,06 | 75% | (0,0; 171,9; 169,1) | (0,0; 1,0; 0,0) |
| 5 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 64,39 | 0,06-0,06 | 75% | (12,1; 164,9; 169,1) | (0,9; 0,5; 0,0) |
| 6 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 38,17 | 0,06-0,06 | 88% | (14,4; 161,9; 116,7) | (0,9; 0,5; 0,0) |
| 7 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 64,39 | 0,06-0,06 | 50% | (-0,0; 144,1; 169,1) | (0,0; -1,0; 0,0) |
| 8 | `SG_Cas_Torres` / Stone_SG_Castle | `SG_Cas_Torres` / SG_VilRoom_Glow | 9,07 | 0,00-0,00 | 77% | (-67,2; 42,0; 132,4) | (-1,0; 0,0; 0,0) |
| 9 | `SG_Cas_Torres` / Stone_SG_Castle | `SG_Cas_Torres` / SG_VilRoom_Glow | 9,07 | 0,00-0,00 | 77% | (-58,0; 32,8; 132,4) | (0,0; -1,0; 0,0) |
| 10 | `SG_Cas_Torres` / Stone_SG_Castle | `SG_Cas_Torres` / SG_VilRoom_Glow | 9,07 | 0,00-0,00 | 77% | (-58,0; 51,2; 132,4) | (0,0; 1,0; 0,0) |
| 11 | `SG_Cas_Torres` / Stone_SG_Castle | `SG_Cas_Torres` / SG_VilRoom_Glow | 9,07 | 0,00-0,00 | 77% | (58,0; 32,8; 132,4) | (0,0; -1,0; 0,0) |
| 12 | `SG_Cas_Torres` / Stone_SG_Castle | `SG_Cas_Torres` / SG_VilRoom_Glow | 9,07 | 0,00-0,00 | 77% | (58,0; 51,2; 132,4) | (0,0; 1,0; 0,0) |
| 13 | `SG_Cas_Torres` / Stone_SG_Castle | `SG_Cas_Torres` / SG_VilRoom_Glow | 9,07 | 0,00-0,00 | 77% | (67,2; 42,0; 132,4) | (1,0; 0,0; -0,0) |
| 14 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / SG_VioletSoft_Glow | 38,17 | 0,06-0,06 | 77% | (-14,4; 161,9; 116,7) | (-0,9; 0,5; 0,0) |
| 15 | `SG_Cas_Coroa` / Wood_SG_Dark | `SG_Cas_Coroa` / Stone_SG_Castle_B | 64,39 | 0,06-0,06 | 100% | (-7,0; 170,1; 169,1) | (-0,5; 0,9; 0,0) |
| 16 | `SG_Cas_Coroa` / Wood_SG_Dark | `SG_Cas_Coroa` / Stone_SG_Castle_B | 64,39 | 0,06-0,06 | 100% | (7,0; 145,9; 169,1) | (0,5; -0,9; 0,0) |
| 17 | `SG_Cas_Coroa` / Wood_SG_Dark | `SG_Cas_Coroa` / Stone_SG_Castle_B | 64,39 | 0,06-0,06 | 100% | (13,9; 158,0; 169,1) | (1,0; 0,0; 0,0) |
| 18 | `SG_Cas_Coroa` / Glass_SGHallMoon | `SG_Cas_Coroa` / Stone_SG_Castle | 61,64 | 0,06-0,06 | 100% | (-1,6; 173,4; 71,8) | (0,0; 1,0; 0,0) |
| 19 | `SG_Cas_Coroa` / Stone_SG_Castle_B | `SG_Cas_Coroa` / Glass_SGHallMoon | 61,64 | 0,06-0,06 | 100% | (1,6; 173,4; 71,8) | (0,0; 1,0; 0,0) |
| 20 | `SG_Cas_Coroa` / Wood_SG_Dark | `SG_Cas_Coroa` / Stone_SG_Castle_B | 64,39 | 0,06-0,06 | 88% | (-13,9; 158,0; 169,1) | (-1,0; -0,0; -0,0) |


## Renders (modo roblox: `FM_MAT_PREVIEW=roblox` aplicado no .blend do 58cdd0bf, EEVEE 1280x720)
No Blender a profundidade é precisa e o z-fight quase não aparece. Por isso cada close tem uma versão `_marcado`,
com a região sobreposta cercada por uma moldura magenta (`PREVIEW_ZF_*`, só no render).

| arquivo | caso | família |
|---|---|---|
| `01_torre_janela_coplanar_close(_marcado).jpg`, `01_..._longe(_marcado).jpg` | torre da fachada (`SG_Cas_Torres`, `towers()` l.1693: `window(..., -0,02, 0,0)`): cômodo aceso `SG_VilRoom_Glow` EXATAMENTE no plano do fuste (d = 0), centro (-67,2; 42,0; 132,4) | F1 |
| `02_ala_leste_janela_close.jpg`, `02_..._longe(_marcado).jpg` | ala leste (`wings()` l.2017, `t_glass = 0,02`): cômodo a 0,04 e vidro âmbar a 0,10 da parede, (60,5; 59,0; 57,3) | F1 |
| `03_muralha_base_arrimo_close(_marcado).jpg`, `03_..._longe(_marcado).jpg` | base externa da muralha: silhar da muralha sobre a alvenaria do arrimo do terreno, 0,03–0,04, (79,7; -9,4; 49,5). No close dá para ver as duas fiadas com juntas diferentes, uma sobre a outra | F3 |
| `04_cortina_oeste_capa_close(_marcado).jpg` | cortina oeste: topo e pontas da capa de obsidiana no plano do corpo de `Stone_SG_Block`, (-80,2; 16,1; 62,0) | F4 |
| `05_coroa_lancetas_violeta_close.jpg` (+ `_marcado`, `_longe`) | campanário da coroa (`crown()` l.1879): lanceta `SG_VioletSoft_Glow` e veneziana `Wood_SG_Dark` a 0,06 do fuste, (-12,1; 151,1; 169,1) | F1 |
| `06_rua_P2_sobre_grama_close(_marcado).jpg` | rua do P2 (`sg_village`, leito `z+0,05`) sobre a grama do patamar `SG_Ter_Terrace_P2`, na altura do olho do jogador, (-57,9; -44,5; 44,2) | F5 |
| `07_topo_torre_anel_coplanar_close(_marcado).jpg` | topo do anel de coroamento da torre da fachada: tampo de obsidiana × remate violeta no mesmo plano (z 110,5), (58,0; 42,0; 110,5) | F2 |

## Limites da auditoria
- A visibilidade é heurística (8 amostras por região). Superfícies dentro de sótãos fechados, como o topo do corpo
  das alas sob o telhado, podem ter passado como "visíveis" se o sótão não for uma casca fechada. As faces com
  normal para baixo foram separadas (F9) porque o jogador quase não as vê.
- O `material_cap()` global do export (remapeamento final por teto de materiais) não foi simulado: pode fundir mais
  alguns pares de tom parecido, o que só reduz a lista.
- O limite de gap que pisca depende da distância e do formato do depth buffer do Roblox. Os valores de 0,02/0,05/0,15
  são estimativas para near 0,1 e 24 bits.
- Scripts (scratchpad `zf/`): `zf_detect.py` (detector), `zf_contact.py` (contato + céu), `zf_final.py` e
  `zf_report.py` (classificação e este relatório), `zf_render.py` (closes). Os dados brutos estão em
  `zf_out2_contact.json`. Nenhum arquivo do pipeline foi alterado e o .blend oficial não foi salvo.
