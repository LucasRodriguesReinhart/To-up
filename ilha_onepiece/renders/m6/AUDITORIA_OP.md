# AUDITORIA OP: Ilha 5 One Piece / Wano na altura do jogador (onda M6a)

Data: 2026-10-08. Auditor: onda M6a (só leitura). Base: `ilha_onepiece.blend` oficial de 07:43 (pós-M4, commits
063b14e/cb60c8d), copiado para o scratchpad e aberto sem regravar. Nenhum arquivo do projeto foi editado; o único
conteúdo novo é este relatório e as folhas em `renders/m6/aud/`. Runners em
`scratchpad/op_aud/` (`aud_common.py`, `aud_analyze.py`, `aud_zf.py`, `aud_holes.py`, `aud_render.py`,
`aud_conf*.py`, `aud_plan.py`, `aud_probe.py`, `aud_box.py`, `curated.py`).

**A pergunta de cada item:** isso sobrevive a close-up, com o avatar de 5, a câmera do Roblox, sem textura e de dia?

**Resposta geral.** Planta, escala, rotas e câmera de 3ª pessoa estão certas. A rua de chegada, o bairro do canal,
o canal oeste, o santuário, a casa de chá, o salão do castelo, o navio, a palafita, o summon e a ponte de saída já
sobrevivem a close-up. O que ainda lê "blockout / de IA" está em cinco lugares:
- a **pele do chão** nas juntas rua/grama/quintal (faixas de terra escura 0,5 abaixo do piso, bordas serrilhadas),
  com o pior trecho exatamente na rota chegada → summon;
- as **massas de rocha claras e chapadas**: rochedo e flancos do castelo, falésias, aro norte em colunas iguais;
  na aérea a paleta das falésias domina e está ~25% mais clara e mais quente que a concept;
- os **"espinhos verdes"** (capas de musgo geradas como prismas altos apontados para cima) no porto e nos flancos;
- **superfícies grandes sem desenho** no herói: pátio do castelo, parapeitos das subidas, paredes do porto;
- **coplanares medidos** em grande área: quintais × grama (12,9k studs²), fachada da torre, muros do pátio, canal do
  moinho, falésia × muro.

---

## Base

**Câmeras: 660**, todas em `FM_MAT_PREVIEW=roblox`, 960 × 540, FOV vertical 70, olho a +5,5 do piso andável
(raio na colisão); bonecos de escala (5,2) visíveis.
- **Rotas:** 384 câmeras = as 15 rotas do `op_qa` amostradas a cada ~25 (128 pontos), 3 quadros por ponto:
  E (+70°), F (frente, inclinada para a escada), D (−70°).
- **Close-ups automáticos por família:** 153 câmeras, 1–3 instâncias de cada um dos 107 grupos `COL_` (casas,
  lanternas, estandartes, bancos, bancas, tōrō, cabeços, mastros, escadas, portões...), a 4–16 da peça.
- **Close-ups manuais:** 88 (heróis e famílias sem colisão: torii, ponte, viaduto, telhados, janelas, rochedo,
  árvore, cais, navio, canais, caveira, espada, pagode, portão OPM).
- **Confirmação:** 26 câmeras livres `Z_*` (algumas com objetos escondidos para achar o dono) + 9 aéreas `V_*`
  (câmeras do projeto) + planta ortográfica.

**Medidas objetivas** (sobre 42.238 ilhas de malha e 292.168 faces visíveis):

| Medida | Critério | Resultado |
|---|---|---|
| Z-fight real | faces paralelas de mesma orientação, ≤ 0,12, materiais diferentes, sobreposição por triangulação e **as duas faces expostas** (raio de 0,6 livre) | 341 pares de material, 5.931 faces, 26,2k studs²; ~80% da área em 5 itens (04, 17, 26, 27, 43) |
| Pele do chão | grade de 0,75 em todo piso andável (COL de piso/escada/ponte); malha visível a ±0,35 do topo da colisão | **269 grupos rasos** (vê-se a malha 0,35–1,0 abaixo: `Dirt_OP_Dark` −0,5) = 4,6k studs²; grupos fundos (> 1,0) quase todos na borda da colisão (aceitos), exceto o item 36 |
| Interpenetração | `BVH.overlap` vegetação × prédios/props, props × prédios/rocha, árvore × castelo, prédio × prédio | 60 pares de objetos; os reais nos itens (troncos e props enraizados nos quintais são esperados) |
| Peças sem apoio | vão de 0,15–3 abaixo e sem contato com outra ilha | 1.000 candidatas; reais nos itens 07, 10, 11, 13, 20, 31, 32, 39, 42, 46 |
| Primitivas cruas | ilha de 8 vértices / 6 faces ≥ 1,0 | as que leem como bloco: itens 02 e 24 |
| Pé-direito e 3ª pessoa | 1.001 pontos de rota a cada 4; câmera 12 atrás + 4 acima | pé-direito ≥ 7,7 em todos; câmera bloqueada em **11/1.001** (5 na subida do castelo, 3 no porto, 3 no oeste/bairro): funciona |
| Cores Roblox | `fm_lib.rbx_color` de 68 materiais; área por material | falésias = 50% da área vertical (item 51) |

**Escala (confere com o avatar de 5,2):**

| Peça | Medida | Leitura |
|---|---|---|
| Portas do kit / casas leves | 8,4 / 7,6 de vão | Certa |
| Espelhos de escada | 0,667–0,767 | Certos |
| Guarda-corpos vermelhos | 3,5–4 | Certos |
| Bancos | 1,7 | Certos |
| Postes de lanterna / tōrō | 8,6 / 4–5 | Certos |
| Viga do portão da Subida A | 7,7 do piso | Fecha a câmera (item 33) |
| Castelo × praça | torre 129 acima da praça | Pequeno perto da concept (item 34) |

**Legenda.**
- **P** = obrigatório na M6b: quebra na câmera do jogador, numa rota principal, num herói ou na aérea de referência.
- **L** = leve.
- **Coordenadas** no referencial local do plano (x, y, z absoluto).
- **Folhas** em `renders/m6/aud/`:

| Folha | Conteúdo |
|---|---|
| `A00_planta_itens.jpg` | Planta (modo roblox) com os números deste relatório (vermelho = P) |
| `A01..A16_*.jpg` | Uma folha por achado principal (rótulo = câmera e posição do olho) |
| `rota_<RR>_n.jpg` | Rotas: cada linha é uma amostra E \| F \| D. RR = DE, EP, ES, PS, SP, PC, PH, PX, SX, PO, PT, EB, BO, PN, NS |
| `close_01..10.jpg` | Grades 4 × 4 dos close-ups (01–04 automáticos por família, 05–10 manuais) |
| `conf_01..03.jpg` | Lote de confirmação `Z_*` |
| `vistas_gerais.jpg` | Ref_01, Ref_02, Front, Back, Left, Right, Castle, Tree, Harbor |

**Câmeras descartadas** (a câmera caiu dentro da malha; o quadro não serve): `C_Cap_E5/Moinho/NWfundo/Telhados/U1/X2`
(dentro das casas leves, que são cascas fechadas: ok), `C_Port_Armazem`, `C_Port_Cais`, `C_Port_RuaAlta`,
`C_Ship_Popa`, `C_Sum_Base`, `C_Ter_Arrimo`, `C_Lmk_Pagode`, `C_Lmk_Caveira`, `C_Wat_CanalL/CanalO/QuedaO`,
`C_Tree_CopaDoPatio`, `C_Tree_Arco`, `C_Port_Espinhos`, `Z_ParapeitoSubida`, `Z_PortoA_Lateral`, `Z_FundoIlha_Olho`
e as automáticas de casa encostadas na parede (`A_OP_CapHouseC1/C2/C6/C7/E5`). As que importavam foram refeitas
como `Z_*`.

---

## op_terrain (OP_Ter_*)

### 01 [P] Pele do chão com faixas de terra escura 0,5 abaixo do piso
- **Onde (maiores grupos, de 269):**

  | Trecho | x | y | Área | Rota |
  |---|---|---|---|---|
  | Viela leste → summon (curva) | 98..148 | 106..202 | 787 | ENTRY→SUMMON, PLAZA→HARBOR |
  | Terraço alto (W3) | −174..−103 | 300..385 | 520 | PLAZA→TERRACO_ALTO |
  | Terraço do summon (bordas dos canteiros) | 116..195 | 181..261 | 370 | PLAZA→SUMMON / EXIT |
  | Crista sul do T1 (atrás das casas B/SW) | −116..57 | 34..39 | 173 | 1º quadro depois do torii |
  | Quintal × rua do bairro | −69..−17 | 70..80 | 58 | ENTRY→BAIRRO (citado pelo agente de props: −60..−57, 71..72) |
  | Canto SO da praça | −115,5..−113 | 120..168 | 55 | PLAZA→OESTE |
  | C7 × viela leste | 17..39 | 103..104,5 | 26 | ENTRY→SUMMON (citado: x 17..38, y 101,5..104,5) |
  | Pé da escada do adro / borda N da praça | −14..15 / 51..90 | 311 / 310..313 | 83 | PLAZA→CASTLE |

  Câmeras `C_Lst_ChaoViela`, `C_Lst_ChaoSummonS`, `Z_TrincheiraLeste_Alto/Olho`, `C_Rua_VielaLesteChao`,
  `C_Rua_QuintalBairro`, `Z_CantoSO_Praca`, `R_ES_04..07`, `R_PT_06..09`, `R_PH_01..03`, `R_BO_04..05`.
- **Problema:** onde as manchas de grama, as calçadas e os quintais não se encontram, a raycast vê a "saia"
  `Dirt_OP_Dark` (112/92/70) a 87,7 sob piso 88,2 (ou 99,7 sob 100,2). Na câmera lê como **valeta marrom de
  borda serrilhada** entre grama e laje, e as manchas de grama têm contorno de papel recortado. Na curva viela →
  summon (a rota mais frequente depois da praça) o chão inteiro lê inacabado.
- **Correção:**
  - Topo do corpo de terreno (a "saia") a piso − 0,12, com `Grass_OP` (terraços) ou `Dirt_OP` (ruas, quintais),
    não `Dirt_OP_Dark`; `Dirt_OP_Dark` só abaixo de piso − 1,5 (falésia/leito).
  - Pele por **união com sobreposição de 0,6** sob calçadas, lajes e quintais (recortar o que fica por cima, não
    deixar vão entre os dois polígonos).
  - Borda das manchas de grama: chanfro 0,15 a 45°, contorno de 2–3 entalhes por lado (não serrilhado aleatório).
  - Gate: `aud_holes.py` com 0 grupos > 2 studs² a menos de 25 de qualquer rota.
- **Evidência:** `A01_pele_chao_faixas.jpg`, `rota_ES_1.jpg`, `rota_ES_2.jpg`, `rota_PT_2.jpg`, `rota_PH_1.jpg`.

### 02 [P] "Espinhos verdes": capas de musgo como prismas altos apontados para cima
- **Onde:** `OP_Ter_Ground`, ilhas `Grass_OP_Deep`/`Cliff_OP_Moss`:
  - parede sul do porto: (130,4; 21,1) 46 de altura, (169,2; 21,4) 89 × 14 × 44, (171,1; 22,2) 41, (212,6; 24,6)
    36, (218,1; 33,1) 39 — de z 42 a 80–88;
  - parede leste para o porto: caixas cruas de 8 vértices (127,2; 109,4) 1,2 × 5,3 × 22,7, (125; 103,4) 21,4,
    (122,5; 89) 18, (122,4; 73,5) 8,3;
  - flancos do castelo e fundo: (68,7..72,6; 370..421) 23–26, (−58,9; 367,4) 30, (−97,3; 459,9) 26,
    (−28,8; 492,6) 40, (1,2; 495,1) 45, (77,2; 494,4) 56.
- **Problema:** em vez de cair da crista, a capa sobe do cais em triângulos verde-escuros finos (cones de 30–46)
  que leem como ciprestes de papel / dentes. Vistos de toda a rota do porto (`R_PH_07E`, `R_PH_09F`, `R_PH_10E`),
  do summon (`R_ES_05D`) e do mar. Com `OP_Veg_*` escondido eles continuam: o dono é o terreno.
- **Correção:**
  - Capa pendurada da crista: borda de cima seguindo o lábio, pontas **para baixo**, comprimento 30–55% da altura da
    face (nunca a face inteira), espessura 0,6–1,2 a 0,15 da face, base ≥ 2 de largura; 3 larguras (4, 7, 11)
    alternadas.
  - Apagar as caixas verticais de 8 vértices (lista acima).
- **Evidência:** `A02_espinhos_verdes.jpg` (`Z_Espinhos_Cais`, `_soTerreno`, `_DoMar`), `rota_PH_2.jpg`.

### 03 [P] Rochedo e flancos do castelo em lajes claras chapadas
- **Onde:** `OP_Ter_CastleRock` (face da proa 98 → 136,2: lajes `Cliff_OP_Warm` de 6–11 × 22–33 em um plano) e
  `OP_Ter_Walls` dos flancos (−104..−50 e 50..73; y 340..480). Câmeras `Z_RochaCastelo_Praca`,
  `Z_RochaCastelo_Lado`, `R_PC_01..05F`, `R_PT_02D/03D`, `R_PN_02E`, `V_Ref_02`.
- **Problema:** a concept põe o castelo sobre uma falésia própria, escura, fendida, com quedas e verde. Aqui o
  rochedo é um biombo de placas cinza-claro alinhadas e os flancos são caixas empilhadas com tampa verde ("bolo de
  camadas"), justamente no enquadramento-herói da praça (Ref_02).
- **Correção:**
  - Proa em 5–7 colunas facetadas de 8–14 de largura, recuo alternado de 1,5–3, chanfro vertical em cada aresta.
  - Fendas `Cliff_OP_Dark` (ou o novo tom de fenda do item 51) de 0,8–1,5 entre as colunas.
  - Drapes do item 02 descendo 25–40% a partir da crista; 2–3 blocos caídos na base junto à bacia.
  - Flancos: quebrar as tampas retas em 2–3 níveis por massa, sem a laje verde de borda reta.
- **Evidência:** `A03_rochedo_castelo.jpg`, `rota_PC_1.jpg`.

### 04 [P] Z-fight falésia × muro (Ground × Walls)
- **Onde e medida:**
  - `Cliff_OP_Cool` (Ground) × `Cliff_OP_Warm` (Walls) a **0,06**, 54 faces, 1.071 studs², em (204,3; 258,3; 67,4):
    face sob a cabeça da ponte de saída, vista do porto, do navio e da ponte.
  - `Cliff_OP_Cool` × `Stone_OP_Dark` a 0,12, 49 faces, 1.870 studs², em (162,8; 149,9; 67,6): lateral da PortoA.
- **Correção:** recuar o corpo do `OP_Ter_Ground` 0,3 atrás das faces de `OP_Ter_Walls` (ou recortar).
- **Evidência:** `zf.json` (scratchpad), `rota_PH_1.jpg`.

### 05 [L] Aro norte em colunas hexagonais iguais; agulhas claras prismáticas
- **Onde:** crista norte/fundo (x −130..150, y 460..520) e esporão; agulhas no pátio/subida do castelo e no fundo.
  Câmeras `Z_ColunasAro`, `C_Tree_Base`, `R_PC_10F/11F`, `C_Lmk_Espada`; planta `A00`.
- **Problema:** ~14 topos hexagonais de diâmetro e altura parecidos em fila (a seção 16 do prompt pede para evitar
  "colunas rochosas iguais"); as agulhas são prismas claros de 4–6 faces com tampa verde (leem concreto).
- **Correção:** diâmetro 0,6–1,6×, altura ±35%, agrupar 2–3, 1 em 3 inclinada 4–8°, tampa de musgo irregular;
  agulhas com 7–9 faces, afinamento 0,6 no topo e 1 fenda escura.
- **Evidência:** `A16_colunas_fundo.jpg`, `vistas_gerais.jpg` (Back).

### 06 [L] Muro do cais em fiadas regulares
- **Onde:** `OP_Ter_Walls`/`Stone_OP_Wall` ao longo do cais (x 205..222, y 60..112). Câmeras `R_PH_13E..17E`.
- **Problema:** retângulos do mesmo tamanho em fiadas contínuas, face plana: lê "parede de blocos" (mesma lição do
  ishigaki da DS).
- **Correção:** altura 0,8–1,6 por pedra, 30% ocupando 2 fiadas, recuo ±0,08, talude 8° acima de 6 de altura.
- **Evidência:** `A08_porto_paredes_cais.jpg`, `rota_PH_3.jpg`.

### 07 [L] Tampas de musgo sem apoio
- **Onde:** `Cliff_OP_Moss` 0,5 acima da rocha em (170,7; 351,3; 103,7) 28 × 4,5, (162,8; 355), (120,2; 362,5),
  (104; 367,5; 119,7), (97,5; 349,6).
- **Correção:** baixar 0,55 (enterrar 0,05).
- **Evidência:** `analysis.json` → `floating`.

### 08 [L] Coplanares pequenos do terreno
- `Cliff_OP_Cool` × `Cliff_OP_Moss` 0,011 em (−79,5; 415,5; 95,7), 164 faces.
- `Dirt_OP` × `OP_Ter_M2_Arrimo` 0,04 em (110,5; 144; 92,2), 61 studs².
- `Cliff_OP_Cool` × `Stone_OP_Path` 0,075 em (0; 335; 80,9) (sob a bacia).
- `OP_Cas_Adro` × `Cliff_OP_Cool` 0,05 em (−63,8; 381; 95), 96 studs².
- **Correção:** afastar 0,15 ou recortar.

### 09 [L] Faixa escura nas cristas externas
- **Onde:** borda oeste do "Além" (x −223..−216, y 130..283, prof. 0,77), fundo do terraço alto (x −207..−104,
  y 407..435, prof. 0,97), promontório (x 285..328, y 274..297).
- **Correção:** mesma regra do item 01 (pele até a crista; o lábio é pedra/musgo, não terra escura).

---

## op_entry (OP_Ent_*)

### 10 [L] Ponte de chegada: tábuas soltas na cabeceira e juntas transversais
- **Onde:** 7 tábuas de y −120 a −113 com 1,0 de vão até a estrutura (sem longarina); juntas entre módulos em
  y −107,75, −104,75, −93,5, −82,25, −79,25, −71, −68, −56,75, −28,25, −20, −17 (fresta por onde se vê o
  viaduto). Câmeras `Z_PonteFendas`, `C_Ent_PonteDeck`.
- **Correção:** 2 longarinas sob as tábuas da cabeceira; módulos sobrepostos 0,05 (sem fresta).
- **Evidência:** `A13_entrada.jpg`.

### 11 [L] Viaduto: coplanares e cintas soltas
- `Stone_OP` × `Stone_OP_Dark` a 0,0 em z 26 (abaixo do mar local, mas visível da DS, onde Wano "flutua"): 933
  studs². Cintas 24,7 × 0,28 a 2,2–2,5 da face em y −7 (z 44–65).
- **Correção:** recuar 0,15; encostar as cintas.

### 12 [L] Ombros de rocha do pátio T0 com capa verde de placa
- **Onde:** (±22; 16). Câmeras `C_Ent_PatioOeste/Leste`.
- **Problema:** a grama é uma placa plana de borda reta sobre a rocha facetada.
- **Correção:** capa com chanfro e transbordo de 0,4 nas arestas, 2 tufos.

---

## op_exit (OP_Exit_*) + encontro com op_summon

### 13 [L] Escoras sob a ponte vermelha soltas
- **Onde:** `Wood_OP_Dark` 4,8 × 14,5 a 0,56–1,08 do arco: (232,8; 243,2; 77), (264,2; 251,6; 77), (237,1;
  244,3; 81,4), (259,9; 250,4; 81,4), (242,5..254,5; 84,2). Câmera `Z_PonteSaida_Sob`.
- **Correção:** prolongar até o arco/pilar (contato de 0,1).
- **Evidência:** `A14_saida.jpg`.

### 14 [L] Guarda do summon fundida na guarda da ponte
- **Onde:** (205,4; 225,6) e (205,4; 246,2): `OP_Sum_Rail` × `OP_Exit_Bridge`, 124 + 105 pares de faces.
- **Correção:** encerrar o guarda-corpo do summon 0,6 antes do 1º pilarete da ponte, com remate dourado (dono
  `op_summon`, ajuste no `op_exit` se o pilarete mudar).
- **Evidência:** `Z_SumRail_PonteSaida` em `A14_saida.jpg`.

### 15 [L] Coplanares da pedra da saída
- `Stone_OP_Dark` × `Stone_OP_Wall` 0,0 em (204,4; 236; 85,5); `OP_Exit_Stone` × `Grass_OP_Deep` 0,068 em (286;
  258,1; 86,2). Afastar 0,15.

---

## op_summon (OP_Sum_*)

### 16 [L] Base Wano: coplanares e canteiros
- `OP_Sum_Garden` (`Dirt_OP`) atravessa `OP_Sum_Stone` nas bordas dos canteiros (193,1; 163,9) e (186,5; 256,1);
  `Metal_Gold_OPOld` × `Stone_OP` 0,12 (179,4; 205,4), `Stone_OP` × `Stone_OP_Dark` 0,03 (168,8; 208,8).
- **Correção:** só na base Wano (não mexer no alias da torre): terra 0,15 abaixo da borda; pedra 0,15 afastada.
- A torre AMS, o pódio e as tōrō sobrevivem a close-up (`close_01.jpg`, `R_ES_08/09`).

---

## op_capital (OP_Cap_*) — com op_kit

### 17 [P] Quintais de terra a +0,06 sobre a grama (z-fight em 12,9k studs²)
- **Onde:** `YARDS` do `op_capital` (`mb.prism(..., z - 0.3, z + 0.06, DIRT)`) sobre a pele de grama do
  `OP_Ter_Ground` a z:

  | Setor | Ponto | Área |
  |---|---|---|
  | Leste | (72,3; 68,9) | 4.347 |
  | Bairro | (−96,5; 55,8) | 3.603 |
  | NE | (181,6; 289,9) | 2.214 |
  | Além | (−206,3; 192,3) | 1.976 |
  | Oeste | (−142,4; 205,3) | 753 |

  Mais as calçadas a +0,15 sobre a terra a +0,06 (0,09): 1,6k studs² no NE e no Leste.
- **Problema:** 0,06 entre dois materiais claros grandes é cintilação certa no Roblox a qualquer distância (regra
  do brief: piso sobre piso ≥ 0,3 ou só um deles).
- **Correção:** recortar a grama do `OP_Ter_Ground` nos polígonos de `YARDS` (só um piso; dono do recorte:
  `op_terrain`, lista exportada pelo `op_capital`), ou subir o quintal para +0,3 com chanfro 0,15 e as lajes de
  calçada para +0,45.
- **Evidência:** `A10_quintais_zfight.jpg` (a cintilação não aparece em still; medida em `zf.json`).

### 18 [L] Madeiramento das casas leves (famílias B/C) a 0,10 do reboco
- **Onde:** `Plaster_OP*` × `Wood_OP_Dark` a 0,10 em OesteFundo (−211,2; 202,5) 216, Leste (74,8; 56,5) 130,
  Oeste (−141,8; 221,9) 130, Bairro (−60,3; 45,8) 103 e (−89,8; 99) 90, NE (164,2; 328,5) 37 (studs²), mais
  `Wood_Dark` × `Wood_Mid` 0,10–0,12 e `Roof_OP_Blue` × `Wood_OP_Dark` 0,10 nos beirais.
- **Correção:** pilares/vigas 0,14–0,18 à frente do reboco em `wall_lo`/`lo_house`.

### 19 [L] Empenas lisas e janela única
- **Onde:** laterais e fundos de casas leves: N2 (205; 284), fundos de C6/C7 no beco (45; 60..100), E7/E8,
  traseira de W-row; janela 2 × 2 "papel" igual em todas as famílias. Câmeras `A_OP_CapHouseN2_1`, `C_Cap_Beco`,
  `A_OP_CapHouseE8_1`, `R_BO_02D/03E`.
- **Correção:** em lados > 12 sem abertura, rodapé de tábuas + 1 janela gradeada (koshi) ou respiro; 3 tipos de
  janela por família (2 × 2, 3 × 2 com grade, koshi vertical).
- **Evidência:** `A11_casas_fundos_janelas.jpg`, `close_02.jpg`.

### 20 [L] Pedras de passo e pedrinhas sem apoio
- 37 pedras de passo `Stone_OP_Path` 2,4 × 2,4 a 0,4 do chão no Além (x −186, y 133..257); 0,42³ `Stone_OP` a 0,2
  em (−16,9; 98,9; 92,7), (−36,5; 93,9), (17,9; 88,1), (33,8; 100,1) e em `OP_Cap_Oeste` (−126,4; 147,1).
- **Correção:** assentar (topo a +0,12 do quintal).

### 21 [L] Quintal do Além vazio
- **Onde:** x −216..−190, y 127..295: 4,5k studs² de terra lisa com uma trilha de pedras de passo. Câmera
  `R_PO_10E`.
- **Correção:** 2 hortas cercadas, 1 varal, 1 pilha de lenha e 2 árvores pequenas (dono do conteúdo: `op_props` /
  `op_veg`).

---

## op_m2_trecho (OP_Cap_M2_*, OP_Plz_M2_*, OP_Ter_M2_*)

### 22 [L] Coplanares da borda/arrimo sul
- `Stone_OP_Dark` × `Stone_OP_Wall` 0,12 em (85,6; 122,6; 87,9) 191 studs² (arrimo) e (87,1; 122,7; 93,1) 118
  (borda). O trecho em si (lojas, rua, escadaria, lanternas) sobrevive a close-up (`rota_EP_1.jpg`).
- **Correção:** capa 0,15 à frente.

---

## op_plaza (OP_Plz_*, OP_Prop_Plz_*)

### 23 [L] Mureta leste encravada no arrimo
- **Onde:** `OP_Plz_Mureta` × `OP_Ter_Walls`, x 115,3, y 204–261 (103 pares) e coplanar 0,0 em (115,1; 169; 93,3).
- **Correção:** recuar a mureta 0,2 para dentro da praça.
- Piso, anéis, emblema, estandartes, bancos e lanternas da borda: ok (`close_05.jpg`, `rota_PO_1.jpg`).

---

## op_castle (OP_Cas_*)

### 24 [P] Parapeitos das subidas A/B são caixas cruas de 18 de altura
- **Onde:** `OP_Cas_Adro`, caixas de 8 vértices `Stone_OP_Path` 1,5 × 42,8 × 18,4 em x −77,6 e −64,4 (Subida A,
  y 337–380; Subida B, y 395–438). Câmeras `R_PC_09E`, `R_PC_10D`, `R_PC_11F`, `R_PT_05F`.
- **Problema:** a face externa oeste é um painel liso de 43 × 18 visto do adro e do terraço alto; de dentro, a
  bochecha é uma régua contínua.
- **Correção:** muro de ishigaki com talude 10° (mesmo construtor do `OP_Ter_CastleWall`), altura visível ≤ 1,1
  acima do degrau, capa em peças de 2,5 com pingadeira 0,1; o volume abaixo vira rocha do `op_terrain`.
- **Evidência:** `A06_parapeito_subidas.jpg`, `rota_PC_2.jpg`.

### 25 [P] Pátio do castelo: plano bege único
- **Onde:** honmaru x −60..70, y 352..475 (~11k studs² de `Stone_OP_Path` 206/196/172 sem junta). Câmeras
  `Z_PatioCastelo_Alto`, `R_PC_13..18`, `C_Cas_Lateral/Traseira/Mirante`.
- **Problema:** é o capítulo-herói e lê estacionamento; de dia é a maior área clara depois da praça.
- **Correção:**
  - Lajes 4 × 4 com junta rebaixada (como a praça) numa faixa de 8 em volta da torre e no eixo porta → mirante.
  - Resto em cascalho em tom −10% (material novo `Stone_OP_Court` ~182/174/156, item 51).
  - Borda de pedra de 0,8 junto aos muros; 2 kuromatsu + as 4 tōrō existentes em pares.
- **Evidência:** `A07_patio_castelo.jpg`, `rota_PC_3.jpg`.

### 26 [P] Fachada da torre: madeira coplanar ao reboco
- **Onde:** `Plaster_OP` × `Wood_OP_Dark` a **0,0**, 390 faces, 533 studs², em (3; 382; 142,8) e nas faixas do 1º
  e 2º andar; `Wood_OP_Dark` × `Wood_OP_Mid` 0,05 em (0; 418; 136,9); `Roof_OP_Blue` × `Wood_OP_Dark` 0,12.
- **Correção:** madeiramento 0,14 à frente do reboco; piso de madeira 0,15 sobre o barrote.
- **Evidência:** `Z_KeepFachada` em `A12_castelo_detalhes.jpg`.

### 27 [P] Muros do pátio: blocos coplanares ao muro de fundo
- **Onde:** `OP_Cas_Court` `Stone_OP_Dark` × `Stone_OP_Wall` 0,08 em (58; 365; 133,1) 808 studs²; `Stone_OP` ×
  `Stone_OP_Dark` 0,08 (58; 365; 129,5) 488; `Stone_OP_B` × `Dark` (−57; 367; 127) 465; `B` × `Wall` 0,02
  (−61,9; 367,4; 123,2) 230; `Stone_OP` × `Wall` 0,02 (−57,8; 362,2; 123,2) 221.
- **Problema:** é a parede que o jogador tem do lado em toda a subida B e no mirante.
- **Correção:** muro de fundo 0,2 atrás da face dos blocos.

### 28 [L] Telhado do muro (dobei) coplanar
- `Roof_OP_Blue` × `Wood_OP_Dark` 0,01 em (−84,5; 438,5; 140,7), 169 faces. Afastar 0,12.

### 29 [L] Base da torre em "colcha"
- **Onde:** ishigaki da torre (`R_PC_15E/16E`).
- **Problema:** blocos `Stone_OP_B/Dark` espalhados ao acaso leem remendo.
- **Correção:** 1 em 6 escura, nunca 2 vizinhas, alturas 0,8–1,6; cantos em sangi-zumi.

### 30 [L] Yagura e torres de canto são caixas brancas
- **Onde:** (43; 369) e (−43; 369). Câmeras `C_Cas_Yagura`, `A_OP_CasTurret_1/2`.
- **Correção:** ishi-otoshi saliente 0,6 na base, rodapé escuro, 2 janelas por face, base de pedra com talude.

### 31 [L] Balaústres do mirante sem apoio
- `Wood_OP_Lacquer` 0,14 × 0,14 × 1,3 a 0,24 do piso em y 352,8, x −22,7..−10,7 (24 peças). Encostar.

### 32 [L] Canais de telha do telhado traseiro soltos
- `Roof_OP_Blue` 0,6 × 3,3 × 1,7 a 0,29 da placa em y 428,8, x −11,6..5,8. Baixar 0,3.

### 33 [L] Viga do portão da Subida A na câmera
- Pé-direito 7,7 sob a viga em (−71; 335; 98,2): a câmera de 3ª pessoa encosta a 0,6 (`R_PC_08F/D`). Subir a
  nuki para ≥ 9.

---

## op_tree (OP_Tree_*)

### 34 [P] Arco alto e estreito demais para a composição da concept
- **Medidas (studs):** praça 92,2; pátio 136,2; cumeeira da torre **221,5**; topo do tronco **292,2**; galhos
  301,1; topo da copa **322,8**; base da copa 194,8. Vão do arco em x: −65,6..101,4 (167).
- **Comparação na mesma câmera (`CAM_OP_Ref_01` × `ref_01`), em fração da altura castelo-sobre-praça (portão do
  adro → cumeeira):**

  | | Concept | Wano hoje |
  |---|---|---|
  | Ápice do tronco acima da cumeeira | ~0,17 | 0,62 (render) / 0,55 (studs: 70,7 / 129,3) |
  | Topo da copa acima da cumeeira | ~0,27–0,30 (cortado no quadro) | 0,88 / 0,78 |
  | Largura do arco / largura do castelo | ~2,7 | ~1,9 |

- **Leitura:** o arco atual é um "C" alto e estreito (de lado lê poste em S: `Z_Arvore_Castelo_Lado`); na concept
  ele abraça o castelo, mais largo e mais baixo. A ref_02 (anime) admite arco mais alto, por isso não proponho o
  valor total da concept.
- **Correção (proposta):**
  - Topo da copa 322,8 → **285–290** (−11%), ápice do tronco 292,2 → **255–260**, galhos ≤ 268.
  - Abrir o vão 15% (x −80..112) mantendo a base e as raízes no fundo-leste; a curva desce mais cedo à esquerda.
  - Base da copa ≥ 200 sobre a torre (não esconder telhados) e as 2 massas principais do item 35 no topo-esquerdo.
  - Opcional (`op_castle`, L): a torre lê pequena perto da concept; esticar os 2 andares de cima 8% (cumeeira
    221,5 → ~228) sem mudar cotas.
- **Evidência:** `A05_arvore_altura.jpg`, `vistas_gerais.jpg`.

### 35 [L] Copa em colar de nuvens
- **Problema:** ~10 almofadas iguais ao longo do arco, sem massa principal (`V_Back`, `V_Ref_02`).
- **Correção:** 2 massas principais de 14–18 (topo e ponta esquerda), 5–7 secundárias, aberturas para o céu
  preservadas; tom `Flower_OP_Deep` só nas faces de baixo.

---

## op_harbor (OP_Port_*)

### 36 [P] Piso invisível sobre a água na raiz do pier
- **Onde:** colisão do cais (42,2) sem malha visível em x 224–232, y 104–111 (~60 studs²): entre a borda do cais
  (x 222) e o início das pranchas (y 112). Câmeras `Z_PierRaiz`, `R_PH_16F`.
- **Problema:** o jogador anda sobre a água na rota PLAZA → HARBOR.
- **Correção:** estender as pranchas e 2 pares de estacas até y 103 (ou recortar a colisão).
- **Evidência:** `A09_piso_invisivel_pier.jpg`.

### 37 [P] Laterais das escadas PortoA/B em painéis lisos
- **Onde:** `OP_Port_Built` `Stone_OP_Dark` 1,74 × 11,9 × 23 em (147,7; 140; 76,4), (149,4; 140; 76) e
  (160; 99,2; 53,4), (160; 97,3; 53) (648 studs² cada). Câmeras `Z_Porto_Muro`, `A_OP_PortProp_1`, `R_PH_04E`.
- **Problema:** painel escuro de 23 de altura colado no muro claro do cais: duas linguagens de muro no mesmo canto.
- **Correção:** revestir com o ishigaki do kit (talude, fiadas variadas, capa clara) e 1 moita no pé.
- **Evidência:** `A08_porto_paredes_cais.jpg`.

### 38 [L] Piso do cais sem desenho
- **Onde:** x 120..222, y 24..112. Câmeras `R_PH_12..17`.
- **Correção:** lajes 3 × 6 com junta rebaixada, faixa de borda clara de 1,2 na beira d'água, 4 argolas.

### 39 [L] Tábuas de papel soltas
- `Wood_OP_Dark` 4,24 × 0,04 × 3 a 1,5 do apoio em (136; 51; 56,7) e (176; 114; 79,7). Espessura 0,15, encostar.

### 40 [L] Palafita e noren
- `Wood_OP_Dark` × `Wood_OP_Lacquer` 0,03 em (239,2; 49,1; 49), 32 faces; noren `Cloth_OP_Indigo` pendurado 2,1
  sobre a água sob o pier (229; 210..216; 40,1).

---

## op_ship (OP_Ship_*)

### 41 [L] Colisão do castelo de popa 2,6 acima do tombadilho
- **Onde:** y 180–192: colisão a 56,4, tombadilho visual a 53,8 (`POOP` = 46,2 + 7,6). Câmera `Z_PopaNavio`.
- **Correção:** topo do `COL_OP_ShipCabin` = `POOP` (ou impedir a subida).

### 42 [L] Pilaretes e vela
- Pilaretes `Wood_OP_Lacquer` 0,36 × 0,36 × 1,6 a 0,28 da amurada em (240,4; 131,5), (255,5; 127,5), (255,6;
  149,2)...; caveira da vela `Cloth_OP_Black` × `Cloth_OP_White` a 0,116 (156 faces) → 0,15.
- Casco, mastros, velas apoiadas, prancha e convés: ok (`close_09.jpg`, `rota_PH_3.jpg`).

---

## op_water (OP_Water_*, VFX_OP_Wheel)

### 43 [P] Cantaria do canal do moinho coplanar
- **Onde:** `Stone_OP_Dark` × `Stone_OP_Wall` a 0,103, **435 faces**, 748 studs², em (−177,8; 84; 87,5) e ao longo
  do canal até a roda.
- **Correção:** fundo 0,2 atrás da face das pedras.
- Canais, pontes vermelhas e roda: ok (`C_Wat_PonteCanal`, `rota_PO_2.jpg`).

### 44 [L] Pedra solta na bacia
- `Cliff_OP_Dark` 2,3 × 1,8 × 2 a 0,4 do fundo em (−6,5; 345,2; 96,8). Assentar.

---

## op_landmarks (OP_Lmk_*)

### 45 [L] Pagode e caveira
- Pagode: `Wood_OP_Dark` × `Wood_OP_Lacquer` a 0,0 em (−246; 372; 164,7), 365 studs² (só de longe).
- Caveira: olhos `Glass_OP_Lantern` (Neon) soltos 0,9 dentro das órbitas em (297,9; 192,1; 113,7) e (302,2;
  176,2); encostar no fundo da órbita.
- Caveira integrada à rocha, espada rígida (lâmina, guarda, cabo) e pagode no pináculo: ok (`close_07.jpg`).

---

## op_veg (OP_Veg_*)

### 46 [L] Copas soltas na crista
- 1–2,8 acima do apoio: (−80,6; 499,5; 76,6), (11,9; 498,3; 97,1), (−88,4; 490; 71,5), (98,8; 499,6; 119,4),
  (−121,5; 476,7; 88,4), (−230,1; 288,9; 91,5), (125,7; 12,8; 65,1), (329,2; 307,3; 62,2), (209,5; 391,9; 114,2),
  (145,2; 510,8; 91,9). Baixar até enterrar 0,1 ou ancorar na face.

### 47 [L] Moitas facetadas no chão da viela leste
- **Onde:** x 98..130, y 110..150. Câmeras `R_ES_04E/05E`.
- **Problema:** almofadas grandes e baixas, de faceta única, sobre a valeta do item 01: leem papel amassado.
- **Correção:** depois do item 01, trocar pela moita da família (2–3 almofadas) a ≥ 1,5 da calçada.

### 48 [L] Árvores largas no canto do cais
- **Onde:** x 130..210, y 12..30 (5 copas "brócolis"). Câmera `R_PH_11F`.
- **Correção:** tirar 2 e manter 1 pinheiro na ponta; o canto do cais respira.
- Cerejeiras (moldura do torii, praça, santuário), kuromatsu e troncos fora das rotas: ok; nenhum tronco
  atravessando prop ou casa (os 60 overlaps são raízes nos quintais).

---

## op_props (OP_Prop_*)

Sem item P/L próprio: as 21 lanternas de poste, 5 tōrō, 12 estandartes, 10 bancos, 5 bancas, 6 cargas, 2 carrinhos,
2 poços, chozuya, ema, saisen, placas e varais assentam no chão (0 flutuando), têm estrutura (tampo, pernas,
travessas, boca/borda nos jarros) e Neon só dentro da armação (`close_04.jpg`, `rota_EB_1.jpg`). Conteúdo do
item 21 (quintal do Além) e o reposicionamento do item 47 passam por aqui.

---

## op_lights / op_vfx (+ portão da galeria)

### 49 [L] Prévia de pétalas no modo roblox
- `PREVIEW_VFX_Petals` deixa quads rosa no chão e no ar nas folhas (`R_PC_15D/16D`, `A_OP_EntStair_1`). Só prévia;
  esconder quando `PREVIEW == "roblox"`.

### 50 [L] Portão OPM: Neon amarelo de dia
- **Onde:** `GATE_OnePunchMan_Barrier` `P_Gold_Glow` (255/195/30, Neon) 4,6 × 15,6 × 18 no promontório
  (`C_Exit_Portao`, `R_PX_07F/08F`); coplanar `P_Gold_Glow` × `P_OPM_DarkGlass` 0,1 no quadro.
- **Problema:** de dia é o objeto mais luminoso da ilha depois do céu. Asset da galeria (`il_gate_opm`), pendência
  já registrada no plano: **não mexer sem o OK do usuário**; só anotar.

---

## op_lib (paleta) — com op_terrain

### 51 [P] Falésias claras dominam a aérea
- **Medida:** área vertical visível por material: `Cliff_OP_Cool` (136/138/146) **42,4%**, `Cliff_OP_Dark` 12,9%,
  `Cliff_OP_Warm` (178/170/156) 8,3% (reboco 3,0%). Média de cor no render Ref_01 (modo roblox): falésia frontal
  **(161, 164, 153)**; concept no mesmo trecho: (111, 123, 153), (143, 138, 149), (88, 103, 132), rochedo do castelo
  (97, 109, 142). As falésias de Wano estão ~25–35% mais claras e puxadas para o bege/verde; na concept são
  cinza-azuladas médias com fendas escuras e muito verde.
- **Problema:** na aérea a ilha lê "bolo de pedra bege", e o reboco do castelo e das casas (234/228/212) perde o
  contraste que a concept usa para destacar a cidade.
- **Correção (regra do brief: só linhas novas no `op_lib`; o `op_terrain` troca os nomes):**
  - `Cliff_OP_Face` ≈ 138/136/140 no lugar de `Cliff_OP_Warm` nas faces;
  - `Cliff_OP_Shade` ≈ 108/114/132 no lugar de `Cliff_OP_Cool` nas massas grandes;
  - `Cliff_OP_Crevice` ≈ 70/76/94 nas fendas entre colunas (itens 03 e 05);
  - `Stone_OP_Court` ≈ 182/174/156 para o pátio do castelo (item 25);
  - verde na crista e escorrendo (item 02) em 20–30% do terço de cima das faces.
  - Validar na mesma câmera Ref_01: falésia frontal com média ≤ (135, 138, 145).
- **Evidência:** `A04_paleta_falesias.jpg`, `vistas_gerais.jpg`.

---

## Tabela por família de assets

| Família | Função visual | Proximidade do jogador | Padrão esperado | Problemas (itens) | Evidência |
|---|---|---|---|---|---|
| Pele do chão (grama, terra, quintais) | Fundo de todas as ruas e terraços | Pé do jogador | Contínua, juntas fechadas, borda chanfrada | Valetas escuras −0,5 (01, 09); quintal +0,06 z-fight (17); quintal vazio (21) | A01, A10, rota_ES/PT |
| Falésias e borda da ilha | Silhueta e aérea | Longe / porto | Massas variadas, fendas, verde no topo | Paleta clara (51); aro em colunas iguais (05); coplanar (04, 08) | A04, A16 |
| Rochedo e flancos do castelo | Pedestal do herói | Praça / adro | Falésia própria, escura, fendida, quedas | Lajes chapadas e "bolo" (03) | A03 |
| Capas verdes / musgo | Verde escorrendo | Porto / flancos | Penduradas da crista, pontas para baixo | Espinhos para cima (02); tampas soltas (07) | A02 |
| Arrimos / ishigaki | Contenção dos terraços | Lado da rota | Pedras variadas, talude, capa em peças | Cais em fiadas (06); arrimo sul coplanar (22) | A08 |
| Agulhas / colunas de rocha | Fundo e moldura | Médio | Prismas irregulares, afinamento | Prismas claros iguais (05) | A16 |
| Ponte de chegada + viaduto | 1º quadro do jogo | Pé do jogador | Tabuleiro contínuo, apoio visível | Tábuas soltas, frestas (10); coplanar sob o mar, cintas (11) | A13, rota_DE |
| Grande torii + pátio T0 | Moldura da chegada | Perto | Pilares, kasagi, base | Ombros com capa plana (12); torii ok | A13, close_05 |
| Casas família A (kit: C1–C7, Chá, haiden) | Rua de chegada, praça | Perto | Telhado grosso, beiral, janela recuada | Ok (close_01, rota_EP) | close_01, rota_EP |
| Casas família B/C (leves, 41) | Massa da capital | Médio / fundos de rua | Madeira 0,14 à frente, lados com abertura | Madeira a 0,10 (18); empenas lisas, janela única (19) | A11, close_02 |
| Telhados (irimoya, kirizuma, saias) | Cor por conjunto, ritmo | Médio / aérea | Espessura, cumeeira, onigawara | Ok na capital; castelo: telhas soltas (32), dobei coplanar (28) | rota_PO, A12 |
| Janelas e portas | Escala, vida | Perto | Moldura, recuo, papel ≥ 0,12 atrás | Janela 2 × 2 repetida (19); acesas ok de dia | A11 |
| Lanternas (poste, tōrō, andon, chōchin) | Ritmo de rua | Perto | Tampa, base, papel na armação | Ok (props); olhos da caveira soltos (45) | close_01, close_04 |
| Estandartes / nobori | Marcar lugares | Médio | Mastro, suporte, brasão limpo | Ok | close_03, close_06 |
| Escadas | Circulação | Pé do jogador | Espelho 0,67–0,77, bochecha | Parapeitos das subidas = caixas (24); viga baixa (33); laterais PortoA/B (37) | A06, A08 |
| Pontes (canal, saída) e guarda-corpos vermelhos | Assinatura vermelha | Perto | Tabuleiro contínuo, arco, encontro | Escoras soltas (13); guarda dupla (14); coplanares (15) | A14 |
| Torii pequeno / santuário | Recanto NE | Perto | Laca, estrado, sino | Ok | rota_PN, close_03 |
| Bancas, bancos, barris, jarros, cestos, carga | Comércio cenográfico | Perto | Tampo, pernas, boca e borda | Ok | close_04 |
| Praça (piso, anéis, emblema, mureta) | Gameplay | Pé do jogador | Livre, juntas, emblema rente | Mureta encravada (23); canto SO (01) | rota_PO, rota_PT |
| Castelo: torre | Marco principal | Herói | 360°, madeira à frente do reboco | Coplanar 0,0 (26); base "colcha" (29); escala vs concept (34) | A12 |
| Castelo: pátio, muros, yagura | Capítulo herói | Pé do jogador | Piso com desenho, muros com profundidade | Plano único (25); muros coplanares (27); yagura caixa (30); balaústres (31) | A07, A12 |
| Castelo: salão interior | Interior acessível | Dentro | Piso, forro, luz, retorno | Ok | rota_PC_4 |
| Árvore monumental | Marco principal | Longe / pátio | Arco que abraça, copa em massas | Alta e estreita (34); colar de nuvens (35) | A05 |
| Cerejeiras / kuromatsu / árvores largas / moitas | Moldura e respiro | Médio | Família, troncos fora das rotas | Copas soltas (46); moitas facetadas (47); excesso no cais (48) | A15 |
| Cais, pier, palafita, armazéns | Setor porto | Pé do jogador | Estrutura, estacas, piso desenhado | COL sobre a água (36); painéis lisos (37); cais liso (38); tábuas de papel (39) | A08, A09 |
| Navio | Marco do porto | Perto (convés) | Casco, mastros, velas apoiadas | COL da popa (41); pilaretes, vela coplanar (42) | A09, close_09 |
| Água (canais, bacia, quedas, roda) | Origem → término | Médio | Cantaria, contato com a roda | Cantaria coplanar (43); pedra solta (44) | rota_PO_2 |
| Caveira, espada, pagode | Secundários | Longe | Formação integrada, lâmina rígida | Coplanar do pagode, olhos soltos (45) | close_07 |
| Summon (torre AMS + base Wano) | Sistema | Perto | Torre preservada, base Wano | Canteiros e coplanares da base (16); guarda × ponte (14) | close_01, rota_ES_2 |
| Portão OPM (galeria) | Progressão | Perto | Asset aprovado sem redesenho | Neon amarelo de dia (50, pendência do usuário) | A14 |
| Prévia de VFX | Só folhas | — | Invisível no modo roblox | Pétalas no chão (49) | rota_PC_3 |

---

## Resumo

| Dono | P | L | Total |
|---|---|---|---|
| op_terrain | 4 (01–04) | 5 (05–09) | 9 |
| op_entry | 0 | 3 (10–12) | 3 |
| op_exit | 0 | 3 (13–15) | 3 |
| op_summon | 0 | 1 (16) | 1 |
| op_capital (+ op_kit) | 1 (17) | 4 (18–21) | 5 |
| op_m2_trecho | 0 | 1 (22) | 1 |
| op_plaza | 0 | 1 (23) | 1 |
| op_castle | 4 (24–27) | 6 (28–33) | 10 |
| op_tree | 1 (34) | 1 (35) | 2 |
| op_harbor | 2 (36, 37) | 3 (38–40) | 5 |
| op_ship | 0 | 2 (41, 42) | 2 |
| op_water | 1 (43) | 1 (44) | 2 |
| op_landmarks | 0 | 1 (45) | 1 |
| op_veg | 0 | 3 (46–48) | 3 |
| op_props | 0 | 0 | 0 |
| op_lights / op_vfx (+ galeria) | 0 | 2 (49, 50) | 2 |
| op_lib (paleta) | 1 (51) | 0 | 1 |
| **Total** | **14** | **37** | **51** |

**Os 10 mais graves** (ordem de ataque na M6b):
1. **01:** pele do chão com valetas escuras e borda serrilhada, pior na rota chegada → summon (787 studs²) e no
   terraço alto; 269 grupos medidos.
2. **17:** quintais a +0,06 da grama: 12,9k studs² de z-fight em toda a capital.
3. **03 + 51:** rochedo do castelo em lajes claras chapadas e falésias ~30% claras demais; a aérea lê "bolo bege".
4. **02:** "espinhos verdes" (capas de musgo em prismas de 30–46 apontados para cima) no porto e nos flancos.
5. **34:** árvore alta e estreita: copa 322,8 → 285–290, tronco 292,2 → 255–260, vão +15%.
6. **25 + 24:** pátio do castelo plano único sem junta e parapeitos das subidas em caixas cruas de 18.
7. **36:** piso invisível sobre a água na raiz do pier (rota do porto).
8. **26 + 27:** coplanares do herói (fachada da torre a 0,0; muros do pátio a 0,02–0,08).
9. **37 + 06:** paredes do porto (painéis lisos de 23 nas escadas, muro do cais em fiadas).
10. **43 + 04:** cantaria do canal do moinho (435 faces a 0,103) e falésia × muro sob a cabeça da ponte de saída
    (0,06).

**O que já sobrevive a close-up:** rua de chegada (trecho M2), bairro do canal, canal oeste e pontes, casa de chá
por dentro, santuário NE, salão do castelo, summon (torre e tōrō), ponte de saída, navio (casco, mastros, velas,
prancha), palafita, props (bancas, poço, chozuya, carrinho, lanternas), ponte de chegada vista do tabuleiro, grande
torii. Navegação, pé-direito e câmera de 3ª pessoa: sem problema estrutural (11/1.001 pontos encostam; item 33).
