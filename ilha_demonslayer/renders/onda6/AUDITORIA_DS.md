# AUDITORIA DS: Ilha 4 Demon Slayer na altura do jogador (onda 6a, export ef639523)

Data: 2026-10-06. Auditor: onda 6a (só leitura). Nenhum arquivo do projeto foi editado. O único conteúdo novo é este
relatório e as folhas em `renders/onda6/aud/`. O `.blend` do projeto foi só aberto, sem regravar; os runners ficaram
no scratchpad (`ds_aud/aud_*.py`).

**A pergunta de cada item:** isso sobreviveria a close-up, com o avatar de 5 e a câmera do Roblox, sem textura e com
bloom? A resposta geral é que a **planta, a escala e a navegação estão certas**. A vila e o interior da forja já
sobrevivem a close-up. O que ainda lê "blockout / de IA" está em quatro lugares:
- as **grandes superfícies** que o jogador atravessa: o T4 oeste, o pátio da forja, as paredes da SubidaA e o
  miolo da clareira;
- o **ishigaki**, que lê como tijolo;
- as **peças repetidas do kit** (escada, lanterna de papel, soleira);
- uma série de **coplanares medidos** entre materiais diferentes.

## Base

**Câmeras:** 419, todas em `FM_MAT_PREVIEW=roblox` (a cor que o Roblox recebe), 960 × 540, FOV vertical 70 (o do
Roblox) e olho a +5,5 do piso andável. Os bonecos de escala (5,2) ficaram visíveis.
- **Rotas:** 297 câmeras. Todas as 12 rotas do `ds_qa` foram amostradas a cada ~25 (99 pontos). Em cada ponto há 3
  quadros: E (+70°), F (frente, inclinada para a escada) e D (−70°).
- **Close-ups:** 94 câmeras, a 2–6 de cada herói e de cada tipo de peça repetida: casa, lanterna, cerca, tōrō, árvore,
  bambu, pedra, ishigaki, escada, ponte, torii, roda, espadas e portão.
- **Confirmação:** 28 câmeras do lote de confirmação.

**Medidas objetivas** (`aud_analyze.py` / `aud_zf.py` sobre as 30.799 ilhas de malha e 268.728 faces):

| Medida | Critério | Resultado |
|---|---|---|
| Z-fight real | Faces paralelas com a mesma orientação, ≤ 0,12 de distância, materiais diferentes, sobreposição medida por triangulação e as **duas faces expostas** (raio de 0,6 livre à frente de cada uma) | 257 pares de material, 3.885 faces; só os expostos estão nos itens |
| Interpenetração | `BVH.overlap` entre vegetação × edifícios, cercas × pedra, lanternas × edifícios/pedra/cercas e props × edifícios | 12 pares de objetos |
| Peças sem apoio | Vão de 0,15–3 abaixo e sem contato com nenhuma outra ilha | 402 candidatas; as reais estão nos itens |
| Pé-direito e câmera de 3ª pessoa | 676 pontos das rotas, a cada 4 | Ver abaixo |
| Cores Roblox | `fm_lib.rbx_color` dos 78 materiais | Pares quase iguais nos itens 8 e 48 |

**Pé-direito e câmera de 3ª pessoa:**
- Livre até piso +10 em toda rota, exceto 2 pontos sob a pérgola do bambuzal (10,1–10,3).
- A câmera a 12 atrás e 4 acima é bloqueada em só 5 de 676 pontos: 2 na pérgola, 2 na boca da forja (artefato: a rota
  começa sob o beiral) e 1 na árvore em (−66; 324). **A câmera do jogador funciona.**

**Escala:**

| Peça | Medida | Leitura |
|---|---|---|
| Porta do kit | 5,6 × 8,4 | Certa |
| Espelho das escadas | 0,75–0,78 | Certo |
| Guarda | 4 | Certa |
| Cerca | 2,5 (altura do quadril) | Certa |
| Poste de lanterna | 5,8–6,6 | Certo |
| Banco | 1,7 | Certo |
| Chōchin da V1 | 6,4 do piso | Fora (item 31) |
| Cachos de glicínia do summon | 1–2 do piso | Fora (item 21) |

**Fonte no jogo:** `renders/ingame/` (Studio em Play, com bloom). A prévia do Blender é mais clara que o jogo. As
lanternas no jogo estouram mais que no `R/`.

**Legenda:**
- **P** = obrigatório na 6b: quebra na câmera do jogador, numa rota principal ou num herói.
- **L** = leve.
- **Coordenadas** no referencial local do plano (x, y, z absoluto).
- **Folhas** em `renders/onda6/aud/`:

| Folha | Conteúdo |
|---|---|
| `A00_planta_itens.jpg` | Planta com os números deste relatório (vermelho = P) |
| `A01..A14_*.jpg` | Uma folha por achado |
| `rota_<RR>_n.jpg` | Rotas: cada linha é uma amostra E \| F \| D |
| `close_nn.jpg` / `conf_nn.jpg` | Grades 2 × 2 com o nome da câmera e a posição no rótulo |

**Câmeras descartadas** (a câmera caiu dentro da geometria, o quadro não serve): `C_Arv_Cedro`, `C_Ent_QuilhaDaPonte`,
`C_Ped_Borda`, `C_Sum_Podio`, `C_Ter_ClareiraBordaO`, `C_Ter_FalesiaLeste`, `C_Ter_Ishigaki{Patamar,Trilha,Vila}`,
`C_Vil_V2_Beiral`, `C_Vil_Hokora`, `C_Frg_TorreAlto`, `Z_ArvoreSummonFalesia`, `Z_ExitPierRock`, `Z_Forno_Carvao`,
`Z_Kura_Lado`, `Z_SummonPeEscada`, `Z_V1_Lanterna` e `Z_RuaFuraIshigaki`. As que importavam foram refeitas:
`Z_Forno_CarvaoFora`, `Z_IshigakiVila2`, `Z_SummonPeEscada2` e `Z_Hokora`.

---

## ds_terrain (DS_Ter_*, DS_Clr_*)

### 01 [P] SubidaA: paredes laterais lisas no eixo herói
- **Onde:** x 6,8 e 25,2; y 377–400; z 60–70. Câmeras `Z_SubidaA_Parede`, `R_CF_06E/D` e `R_FM_04E`.
- **Problema:**
  - Os dois lados do 1º lance da subida para a forja são faces de `DS_Ter_Bodies` (`Cliff_DS_Dark`, 46/49/57). São
    planos azul-escuros de ~23 × 5–10, com uma capa clara e 2 contrafortes.
  - Todo jogador sobe por ali. Lê como prisma de blockout (os 19 corpos de `DS_Ter_Bodies` são caixas de 8
    vértices, ex.: 16,5 × 84 × 35 em (30; 479)).
  - O raio da sonda confirma o dono: `PROBE SubidaA_parede_O/L → DS_Ter_Bodies Cliff_DS_Dark`.
- **Correção:**
  - Revestir as duas faces com o mesmo construtor do `DS_Ter_Ishigaki`, já corrigido pelo item 03: talude de 10°,
    pedras de 1,8–3,2 × 0,9–1,4, junta de 0,08, recuo da face com ±0,08 por pedra e capa em peças de 2,5 com
    pingadeira de 0,1.
  - Ou rocha em colunas como as falésias. Manter os 2 contrafortes, mas com 3 fiadas.
  - Afastar 0,15 do `Stone_DS_Path` da escada: há coplanar medido a 0,06 em (6,7; 391,4) e (25,3; 392,7).
- **Evidência:** `A01_subidaA_paredes_lisas.jpg`, `rota_CF_2.jpg` e `rota_FM_1.jpg`.

### 02 [P] Vala escura ao lado da escada Trilha (1º quadro do jogo)
- **Onde:** x 3–9, y 38–50, z 53–54. Câmeras `Z_TrilhaVala`, `R_EV_02D` e `C_Ter_EscadaTrilhaLado`; no jogo,
  `03_entrada_altura`.
- **Problema:**
  - Entre o ishigaki da trilha e a borda do terraço do bambuzal sobra um fosso de ~4 de largura e ~1,5 de fundo.
    O fundo e as paredes são `DS_Ter_Bodies`/`Cliff_DS_Dark`, com uma rocha musgosa solta dentro.
  - A borda do bambuzal mostra o lábio de terra (0,3) como uma laje fina.
  - É o primeiro enquadramento depois do torii e lê como emenda não terminada.
- **Correção:**
  - Preencher até 54,2 com talude de pedras de 1–2 (`Stone_DS_B`) e 3–4 samambaias, ou fazer um canal seco de seixos
    com meio-fio dos dois lados.
  - Fechar a borda do terraço do bambuzal com pedras de borda de 0,6 de altura (sem lábio fino visível).
- **Evidência:** `A02_vala_escada_trilha.jpg`.

### 03 [P] Ishigaki em fiadas regulares: lê tijolo, não ishigaki
- **Onde:** todo o `DS_Ter_Ishigaki` (1.702 pedras). Pior em três lugares, todos vistos de frente na chegada:
  - patamar e frente da forja (y 395–437, z 60–80);
  - arrimo T1 → T2 da vila (x −70..−50, y 230–300);
  - muros do pátio T0.
- **Problema:**
  - As pedras são retangulares, com a mesma altura em cada fiada, junta vertical reta e face plana. O canto não
    tem sangi-zumi e não há talude perceptível.
  - No jogo (`06_forja_patamar`) lê "muro de tijolo cinza / Minecraft", logo abaixo do herói.
- **Correção:**
  - Altura variando 0,8–1,6 dentro da fiada (±30%). 30% das pedras ocupam 2 fiadas, para quebrar as juntas
    contínuas.
  - Rotação de ±4° no plano da face e recuo de ±0,08 por pedra.
  - Cantos em sangi-zumi: blocos de 3:1 alternando a direção a cada fiada.
  - Talude de 10° nos muros com mais de 6 de altura e 1 pedra em 5 com `Stone_DS_B`.
  - Capa em peças de 2,5 (não uma régua contínua).
- **Evidência:** `A03_ishigaki_fiadas.jpg`, `close_03.jpg` (`C_Cer_Patamar`), `close_06.jpg` (`C_Esc_Patamar`) e
  `close_21.jpg` (`C_Ter_IshigakiForja`).

### 04 [P] Terraço T4 oeste é um polígono único de terra
- **Onde:** x −150..−20, y 372..460, z 80,2. É a chegada da OesteForja, o pátio do carvão e o início do caminho de
  saída. Câmeras `Z_PatioForjaVazio`, `R_CO_02E–04E`, `R_FO_03E`, `R_VF_05F–07E` e `R_CO_03F`.
- **Problema:**
  - `DS_Ter_Ground` tem uma face `Dirt_DS_Dark` de 278 × 167 (25.179 studs²).
  - Não há manchas, trilha nem borda. As 20 lanternas de caminho ficam espetadas no meio do vazio.
  - Lê "estacionamento", logo no capítulo herói.
- **Correção (chão):**
  - Manchas `Dirt_DS` claras de pisoteio e de grama seca (`Grass_DS_Dry`) em 25–35% da área, a +0,12 (não
    coplanar).
  - Trilha de lajes irregulares de 2,5–3 de largura, com meio-fio em `Stone_DS_B`, em três trechos:
    - topo da OesteForja (−66; 374) → pátio (−20; 446);
    - pátio (−20; 446) → caminho de saída (−104; 452);
    - topo da OesteForja (−66; 374) → carvoeira (−112; 400).
  - Faixa de grama e moitas de 3–5 ao longo da borda oeste (x < −135).
  - O conteúdo é dos itens 36 (`ds_forge`) e 51 (`ds_props`).
- **Evidência:** `A04_T4_oeste_vazio.jpg` e `A00_planta_itens.jpg`.

### 05 [L] Grama a menos de 0,12 do corpo de terra na entrada do bambuzal
- **Onde:** (46,2; 54,7; 55,6) e (51,0; 54,5; 55,6), à beira da rampa do bambuzal.
- **Problema:**
  - `DS_Ter_Bodies` (`Dirt_DS_Dark`) e `DS_Ter_Grass` (`Grass_DS`) ficam a 0,07–0,11, com 117 studs² voltados para
    cima.
  - O teste com as duas faces expostas não confirmou a cintilação, porque a grama cobre a terra. O corpo também
    encosta no bambu a 0,107 em (49,2; 61,3).
  - Confirmar no Play.
- **Correção:** baixar o topo do corpo 0,3 sob a grama, ou recortar a grama no contorno do corpo.
- **Evidência:** tabela de z-fight (`zf.json`).

### 06 [L] Miolo da clareira é um polígono liso
- **Onde:** `DS_Clr_Floor`, face `Dirt_DS` de 174 × 269 (33.310 studs²), centro (41; 262). Câmeras
  `C_Ter_ClareiraChao`, `R_CF_01–02` e `R_CS_01`.
- **Problema:** a seção 25 pede variação sutil, mas o miolo é uma cor só. No jogo, os 70 minérios cobrem boa parte,
  por isso é L.
- **Correção:**
  - 6–8 manchas `Dirt_DS_Dark` de 10–20 a +0,12.
  - 2 trilhas de pisoteio, da chegada (y 140) ao pé da subida (16; 350).
  - 30–40 seixos de 0,3–0,6 sem colisão, longe dos `ORE_*` (≥ 3).
- **Evidência:** `A10_clareira_chao.jpg`.

### 07 [L] Fragmentos de pedra planos e escuros leem buraco
- **Onde:** clareira. Câmeras `R_EC_05D`, `R_CV_02D` e `R_CF_04D`.
- **Problema:** triângulos chatos escuros no chão parecem furos ou sombras.
- **Correção:** dar 0,15–0,3 de altura com topo chanfrado e cor `Stone_DS_B`, não terra escura.
- **Evidência:** `A10_clareira_chao.jpg`.

### 08 [L] Toda a pedra no mesmo cinza médio
- **Onde:** global (com uma linha no `ds_lib` para a cor).
- **Problema:** a cor Roblox não separa as peças de pedra; ishigaki, escadas, lajes e tōrō leem como uma massa só.

  | Material | Cor Roblox |
  |---|---|
  | `Stone_DS` | 124/120/112 |
  | `Stone_DS_Laje` | 136/125/108 |
  | `Stone_DS_Path` | 156/146/128 |

- **Correção:**
  - Ishigaki para ~100/98/92, com 1 pedra em 5 em 88/86/82.
  - Pisada da escada clara e espelho `Stone_DS_Dark`.
  - Lajes de caminho mais quentes (+8 R).
- **Evidência:** `close_06.jpg`, `close_07.jpg` e `rota_CF_2.jpg`.

### 09 [L] Grama em "tapetes" de borda reta
- **Onde:** `DS_Ter_Grass` e `DS_Clr_Floor` (ex.: (−49; 168) e (37; 137)).
- **Problema:** os polígonos de grama têm 0,3 de espessura, borda reta e lábio vertical. De perto, leem como papel
  recortado.
- **Correção:**
  - Chanfrar a borda 0,15 a 45° e baixar para +0,12 sobre a terra.
  - Variar o contorno com 2–3 entalhes por lado.
- **Evidência:** `close_20.jpg` (`C_Ter_GramaTapete`) e `close_04.jpg`.

### 10 [L] Lajes do pátio T0 sobrepostas na borda oeste
- **Onde:** (−17,4; 13,3; 54,2) e (±2,3; 37,8). Câmera `C_Ent_PatioOeste`.
- **Problema:** lajes de `DS_Ter_Paving` com vão de 0,28 sob a borda e cruzadas em alturas diferentes junto à guarda.
- **Correção:** assentar todas a 54,2 + 0,02 e recortar as que cruzam a guarda.
- **Evidência:** `close_04.jpg`.

### 11 [L] Coplanares de rocha no fundo da forja e na quilha
- **Onde e problema:** coplanares com as duas faces expostas:
  - `DS_Ter_Cliff` (`Cliff_DS_Dark`) com `DS_Ter_Rocks` (`Cliff_DS_Moss`) a 0,0 em (146,3; 367,3; 66,0), 14 faces
    voltadas para cima, na borda leste da lagoa;
  - `DS_Ter_Cliff` com `DS_Ter_Keel` a 0,045 em (77,8; 89,2; 31,2);
  - `DS_Ter_Ground` com `DS_Ter_RockWalls` a 0,027 em (−21,1; 369,6; 60,7).
- **Correção:** afastar 0,15 a pedra de musgo e a terra.
- **Evidência:** tabela de z-fight.

---

## ds_entry

### 12 [P] Escada Trilha ainda é a escada de blockout
- **Onde:** pé em (−12; 40; 54,2), 12 de largura, 8 degraus. Câmeras `C_Ter_EscadaTrilha` e
  `C_Ter_EscadaTrilhaLado`; no jogo, `03_entrada_altura`.
- **Problema:**
  - `ds_entry.py:635` chama `DL.plan_stair(mb, "Trilha")`, que é a escada do blockout: cada degrau é uma laje de
    12 × 1,82 (caixa de 8 vértices) e os banzos são blocos.
  - É a primeira escada que o jogador sobe.
- **Correção:** trocar pela `K.stair_stone` já corrigida no item 24, no mesmo envelope do `ds_col`, como a
  `ds_village.plan_stair_kit` faz.
- **Evidência:** `A07_escadas_lajes_inteiricas.jpg` e `close_20.jpg`.

### 13 [L] Ponte de chegada: o mesmo painel 30 vezes
- **Onde:** y −100..0. Câmeras `R_SG_02–05` e `C_Ent_PonteGuarda`.
- **Problema:** a guarda é um único painel repetido a cada ~3,2 ao longo de 100, com só 1 par de lanternas (y −50).
- **Correção:**
  - A cada 25, um montante mais grosso (0,9 → 1,3) com giboshi, o mesmo da pontezinha do summon.
  - 2 lanternas penduradas a mais (y −80 e −20).
  - Variar 1 painel em 4 (sem a cruz central).
- **Evidência:** `A12_saida_ponte.jpg` e `rota_SG_1.jpg`.

### 14 [L] Torii de entrada: cinta preta quase coplanar
- **Onde:** (±6–7; 8; 55–60).
- **Problema:** `P_DS_Black` (nemaki) a 0,098 da laca do pilar, 70 faces. Os pilares de poucas faces aparecem em
  close.
- **Correção:**
  - Cinta 0,15 para fora.
  - Pilar com 12 faces.
  - Kasagi com +0,4 de levantamento nas pontas.
- **Evidência:** `close_05.jpg` (`C_Ent_ToriiPe`) e `close_06.jpg` (`C_Ent_ToriiTopo`).

---

## ds_exit (+ il_gate_op aprovado)

### 15 [P] Início da ponte de saída: tabuleiro coplanar com a terra
- **Onde:** (−95,3; 592,4; 80,2). Câmera `C_Exit_PonteInicio`.
- **Problema:**
  - `DS_Exit_Bridge` (`Wood_DS_Mid`) e `DS_Exit_Path` (`Dirt_DS`) a 0,1, 10,7 studs² voltados para cima.
  - Há também um degrau seco entre as lajes do caminho e o tabuleiro. É o primeiro passo na ponte.
  - No caminho de saída, `DS_Exit_Path` (`Dirt_DS`) fica coplanar (0,0) com o `DS_Ter_Ground` (`Dirt_DS_Dark`) em
    (−73,5; 500,6; 80,2), 5,3 studs² voltados para cima.
- **Correção:**
  - Rebaixar a terra 0,2 sob o tabuleiro e subir o caminho +0,12 sobre o chão do T4.
  - Soleira de pedra de 1,5 × 14 (`Stone_DS_B`, bevel de 0,05) entre o caminho e a ponte.
- **Evidência:** `A12_saida_ponte.jpg`.

### 16 [L] Ponte de saída: guarda repetida e montantes sem contato
- **Onde:** x −87..−92, y 600–618, z 80,7. Câmeras `R_CO_11–12` e `C_Exit_PontePostes`.
- **Problema:**
  - É a mesma guarda do item 13.
  - 84 montantes ficam com a base 0,38 acima da longarina, sem contato. Só é visível de fora da ponte.
- **Correção:**
  - Estender os montantes 0,45 para baixo.
  - Giboshi a cada 25.
- **Evidência:** `close_09.jpg` e `rota_CO_3.jpg`.

### 17 [L] Torii de saída: mesma cinta a 0,098
- **Onde:** (−100,8; 584,2; 81,1), 70 faces.
- **Correção:** a mesma do item 14.
- **Evidência:** `close_10.jpg`.

### 18 [L] Portão One Piece (aprovado): só registro
- **Onde:** `GATE_OnePiece_Frame`.
- **Problema:** `Metal_Dark` a 0,114–0,117 de `Wood_Dark` e `Wood_Plank`, 140 faces.
- **Correção:** não mexer sem aprovação. Se a 6b tocar no portão, afastar 0,15.
- **Evidência:** tabela de z-fight.

---

## ds_summon

### 19 [P] Z-fight do pé da escada e da pontezinha com o chão
- **Onde:** pé da escada do summon e pontezinha. Câmeras `Z_SummonPeEscada2` e `C_Wat_Pontezinha`.
- **Problema:** lajes de `DS_Sum_Stone` coplanares (0,02) com o chão:

  | Ponto | Contra | Área |
  |---|---|---|
  | (131,4; 306,3; 60,4) | `Grass_DS` | 20,5 studs² |
  | (129,1; 324,1; 60,2) | `Dirt_DS` | 18 studs² |
  | (111,4; 296,6; 60,2) | `Clr_Floor` | 13,5 studs² |
  | (111,7; 305,1; 60,4) | `Clr_Floor` | 7,7 studs² |

- **Correção:** subir as lajes do pé +0,15 com chanfro de 0,05 (ou baixar o chão 0,15 no recorte).
- **Evidência:** `A11_summon_pe_podio.jpg`.

### 20 [P] Pódio e torre: coplanares à altura do olho
- **Onde:** plataforma do summon. Câmeras `Z_SummonPodioLado`, `C_Sum_PodioPerto` e `R_CS_06F`.
- **Problema:** quatro grupos de faces quase coplanares:

  | Materiais | Distância | Faces | Onde |
  |---|---|---|---|
  | `Metal_Gold_DS` × `Cliff_DS` | 0,01 | 98 | Topo dos frisos, z 83,5 (187; 289,6/310,4) |
  | `Cliff_DS` × `Stone_DS_Dark` | 0,04–0,11 | 80 | Laterais, z 77–82 (187,5; 292,9/307,2) |
  | `Metal_Gold_DS` × `Stone_DS_Dark` | 0,055 | 14 | (193,6; 298,3; 81,1) |
  | `Stone_DS_B` × `Wood_DS_Dark` | 0,01 | 8 | (191,2; 295; 72,1) |
  | `Stone_DS_Dark` × `Wood_DS_Dark` | 0,12 | 6 | (186,5; 289,5/310,5; 73,6) |

  Ficam na plataforma, vistos de 3 a 15 studs.
- **Correção:** frisos e ferragens dourados 0,12 para fora, `Cliff_DS` recuado 0,12 e a laje 0,15 acima da madeira.
- **Evidência:** `A11_summon_pe_podio.jpg`.

### 21 [P] Glicínias do summon: prismas lilás descendo até o chão
- **Onde:** (176,6; 271,6) e (175,8; 329,0), piso 70,2. Câmeras `Z_GlicSummonPerto`, `C_Sum_Glicinia` e
  `R_CS_06E`.
- **Problema:**
  - Os cachos de `DS_Sum_Wisteria` são prismas empilhados de 0,6 que descem a 71–72 (1–2 do piso). Atravessam o
    avatar e a câmera em volta da torre e leem "blocos lilás".
  - É outra família que a da pérgola e da V6 (`DS_Veg_Wisteria`, cachos cônicos). O plano pede as 4 glicínias da
    mesma família.
- **Correção:**
  - Usar o gerador de cacho do `ds_veg` (cones de 1,2–2,4).
  - Base dos cachos ≥ piso +7 nos 3 do lado do caminho; ≥ +4,5 só na face voltada ao mar.
  - Copa 20% mais densa, para compensar.
- **Evidência:** `A09_glicinias.jpg`.

### 22 [L] Escada do summon: construtor próprio
- **Onde:** `ds_summon.plan_stair`.
- **Problema:** o construtor próprio repete a laje inteiriça.
- **Correção:** alinhar com a `K.stair_stone` do item 24.
- **Evidência:** `close_07.jpg` (`C_Esc_Summon`).

---

## ds_kit (peças repetidas: aparecem na vila e na forja)

### 23 [P] Lanterna de papel (`_box_lantern`, `lantern_post`, `lantern_wall`) lê como caixa de luz
- **Onde:** nós da vila e da forja (ex.: portão da vila (−38; 116) e boca da forja). Câmeras `C_Lan_Braco` e
  `C_Frg_Boca`; no jogo, `05_vila_baixa` e `12_vila_lanternas_v2`.
- **Problema:**
  - O papel `Glass_DS_Lantern` (Neon 232/146/66) é uma caixa inteira recuada 0,15. Na frente dela há só 2
    cruzetas de 0,08 por face.
  - No Play, com bloom, a grade some e sobra o "cubo amarelo emissivo" que a seção 22 proíbe. A `v2` do papel
    melhorou a cor, não a silhueta.
- **Correção:**
  - Cruzetas de 0,08 → 0,16 e kumiko de 2 × 3 (montantes de 0,14).
  - Montantes de canto de 0,16 → 0,22 e beiral do chapéu de 0,32 → 0,45, sombreando o topo do papel.
  - Neon só nas 2 células centrais de cada face (≤ 45% da área); o resto em `Plaster_DS_Shoji`, iluminado pela
    luz.
  - Variante redonda de 8 lados (chōchin) para as lanternas de parede.
- **Evidência:** `A06_lanternas_caixa_de_luz.jpg` e `close_15.jpg`.

### 24 [P] Escada de pedra (`stair_stone`): degrau é uma laje inteiriça e as 7 escadas são iguais
- **Onde:** SubidaA e SubidaB (`ds_forge`), VilaAlta, VilaClareira e OesteForja (`ds_village`); a Trilha e o
  Summon repetem o mesmo desenho (itens 12 e 22). Câmeras `C_Esc_*`, `R_CF_06–08` e `R_VF_04`.
- **Problema:**
  - Cada degrau é um único `stone()` de largura total (8–16), com focinho claro, sem junta.
  - De longe, lê como rampa listrada. São 7 escadas idênticas na mesma ilha.
- **Correção:**
  - 3–5 pedras por degrau (larguras de 2,4–4,2), com junta desencontrada de degrau a degrau.
  - Focinho de 0,1 com chanfro de 0,05.
  - Espelho em `Stone_DS_Dark` recuado 0,08.
  - 1 degrau em 5 com a pisada rebaixada 0,04 no centro (desgaste).
  - Degrau de arranque e patamar de chegada com laje maior.
  - Banzo em pedras de 2 alturas, não em blocos por degrau.
- **Evidência:** `A07_escadas_lajes_inteiricas.jpg` e `close_07.jpg`/`close_08.jpg`.

### 25 [P] Janela acesa a 0,06 da grade (`window`)
- **Onde:** `Window_DS_Warm` × `Wood_DS_Dark`:

  | Edifício | Distância | Faces |
  |---|---|---|
  | V2 | 0,06 | 58 |
  | V5 | 0,06 | 77 |
  | V6 | 0,06 | 54 |
  | Salão da forja | 0,06 | 48 |
  | Ala leste / moinho | 0,06 | 17 |
  | `Frg_Houses` | 0,12 (no limite) | 162 |

  Ex.: (−76,9; 163,2; 68,2) e (−94,2; 290,4; 73,1).
- **Problema:** a regra do brief é a janela acesa ≥ 0,12 atrás da grade.
- **Correção:** recuar o painel aceso para 0,15 atrás do plano da grade, em todas as variantes de `window` e `_leaf`.
- **Evidência:** tabela de z-fight; `close_25.jpg` (`C_Vil_V5`).

### 26 [P] Cumeeira coplanar com a telha e com a empena (`ridge`, `roof_*`)
- **Onde:** todas as casas. São a silhueta da vila contra o céu e cintilam de longe.
- **Problema:** contatos com as duas faces expostas:

  | Contato | Distância | Faces / lugar |
  |---|---|---|
  | `Roof_DS_Ridge` × `Wood_DS_Dark` (ponta da cumeeira × hafu) | 0,04 | Hall 16, Mill 16, V3 16, `Frg_Houses` 14, V2 12, V5 10 |
  | `Ridge` × reboco da empena | 0,08 | V2 (−78,8; 160,6; 78,4), V5 (−102,9; 277,8; 93,2), `Frg_Houses` (−63,1; 488; 103,2) |
  | `Ridge` × reboco da empena | 0,12 | Hall (0; 484,5; 101,8), Mill e V3 |
  | `Roof_DS_Tile` × `Wood_DS_Dark` | 0,06 | V2, V5 |
  | `Roof_DS_Tile` × `Wood_DS_Dark` | 0,12 | Mill, 32 faces |
  | `Plaster_DS_Kura` × `Ridge` | 0,05 | V4 |

  O contato `Ridge` × `Tile` (0,034–0,053) existe, mas fica coberto.
- **Correção:** cumeeira e onigawara 0,12 à frente da tábua hafu, empena (`gable`) recuada 0,15 da face da cumeeira
  e telha a 0,12 da madeira do beiral.
- **Evidência:** tabela de z-fight.

### 27 [L] Madeira escura e média no limite de 0,12 (`boards`, `engawa`)
- **Onde:** `Wood_DS_Dark` (58/40/30) × `Wood_DS_Mid` (104/72/48), com as faces expostas:

  | Lugar | Distância | Faces |
  |---|---|---|
  | V5 (−110,8; 278,4; 69,7) | 0,12 | 21 |
  | V2 (−77,6; 166,8; 63,5) | 0,12 | 7 |
  | Rua alta (−53,3; 278,4; 67,4) | 0,08 | 8 |

  Os casos a 0,02–0,05 da V6, do salão e da V3 ficam cobertos.
- **Problema:** é contraste alto, no limite da regra.
- **Correção:** a peça Mid 0,15 para fora.
- **Evidência:** tabela de z-fight.

### 28 [L] Soleiras octogonais idênticas e empilhadas
- **Onde:** V2, V4, V5, V6, oficina e V1. Câmeras `C_Vil_V4_Porta`, `C_Vil_V5`, `C_Frg_Oficina` e `R_EV_07E`.
- **Problema:** as pedras de soleira (kutsunugi-ishi) são "moedas" de 8 lados iguais, 2–3 por porta, empilhadas.
- **Correção:**
  - Polígono de 7–9 vértices, raio de 1,1–1,6 sorteado e topo abaulado de 0,05.
  - 1 grande + 1 menor, deslocadas, com rotação aleatória.
- **Evidência:** `A14_kit_detalhes.jpg`.

### 29 [L] Namako do kura chapado
- **Onde:** V4 (−105; 252). Câmeras `C_Vil_V4_Canto` e `C_Vil_V4_Porta`.
- **Problema:** os losangos pretos são placas sem relevo e sem a rede branca.
- **Correção:** losango com 0,06 de saliência e rede de juntas em relevo de 0,1 × 0,12 (`Plaster_DS_Kura`), bevel
  de 0,03.
- **Evidência:** `A14_kit_detalhes.jpg` e `close_25.jpg`.

---

## ds_village

### 30 [P] V6 (casa visitável): shoji, sudare e bambu coplanares
- **Onde:** V6. Câmeras `C_Vil_V6_Interior` e `C_Vil_V6_Engawa`.
- **Problema:**

  | Materiais | Distância | Faces | Ponto |
  |---|---|---|---|
  | `Plaster_DS_Shoji` × `Wood_DS_Dark` | 0,03 | 144 | (−123,5; 324,9; 73,8) |
  | `Metal_DS_Iron` × `Plaster_DS_Shoji` | 0,04 | 12 | (−123,5; 349,8; 73,8) |
  | `Bamboo_DS_Dry` × `Wood_DS_Mid/Dark` | 0,0–0,05 | 4 | (−130,1; 337,3; 69,2) |

  É o interior que o jogador visita.
- **Correção:** papel 0,12 atrás das molduras, puxadores 0,12 à frente do papel e o sudare 0,15 à frente do
  batente.
- **Evidência:** tabela de z-fight; `close_26.jpg`.

### 31 [L] V1 (casa de chá): chōchin baixo demais e braseiro de placa
- **Onde:** luz `L_DSVil_V1_Chochin` em (−64,7; 128,6; 68,3). Câmeras `C_Vil_V1_Interior` e `C_Vil_V1`.
- **Problema:**
  - O chōchin de Ø ~2 fica a 6,4 do piso (61,9), no meio do vão. A câmera de 3ª pessoa e a cabeça do avatar
    batem nele.
  - O braseiro é uma rocha escura com uma placa Neon retangular.
- **Correção:**
  - Lanterna a piso +8,5, ou 2 chōchin de Ø 1,2 nas laterais.
  - Braseiro com grelha e 5–7 brasas (`Ember_DS_Glow`) em vez da placa.
- **Evidência:** `close_24.jpg`.

### 32 [L] Rua alta encostada no ishigaki
- **Onde e problema:**
  - A terra da rua (`Dirt_DS`) atravessa o paramento do ishigaki em (−71,3; 371,7; 73,0), 115 pares de faces, no
    topo da OesteForja, e em (−104,6; 226,7; 66,2).
  - A cerca fica coplanar com a capa (`Stone_DS_Path`, a 0,02) em (−72,6; 229,4; 66,7), 54 faces.
  - As lajes ficam a 0,12 da grama em (−70,4; 281,9; 66,4).
- **Correção:** recortar a rua 0,3 antes da face do muro, a cerca 0,15 para dentro e as lajes a +0,15.
- **Evidência:** tabela de interpenetração e z-fight.

---

## ds_forge

### 33 [P] Pátio de trabalho chapado em volta do herói
- **Onde:** `DS_Frg_Ground`, caixa `Dirt_DS_Dark` de 144,7 × 30,9 com centro em (12; 452,9; 80). Câmeras
  `C_Frg_Patio`, `R_CF_09E`, `R_FM_01–02` e `R_FO_01–02`.
- **Problema:**
  - Em volta da boca acesa só há uma passarela de lajes de 2. O resto é terra lisa de uma cor.
  - O capítulo que deveria ter densidade alta lê vazio (seção 5 do plano).
- **Correção:**
  - Lajes irregulares nos 12 em frente à boca e à torre.
  - Terra batida com 4–5 manchas `Dirt_DS` claras de pisoteio e 2 de respingo escuro (têmpera).
  - Sulco de drenagem de pedra (0,6 de largura) ao longo da fachada sul.
  - Estrado de madeira de 6 × 3 sob as 2 estantes de lâminas.
  - Meio-fio na borda sul (y 436).
- **Evidência:** `A05_forja_patio_bigorna_forno.jpg`.

### 34 [P] Bigorna do pátio é cubo + caixa
- **Onde:** (−30; 459; 81,2) (`COL_DS_FrgProp_004`). Câmeras `Z_Bigorna` e `R_FO_02D`.
- **Problema:** um bloco `Stone_DS` cinza, uma caixa preta por cima e um feixe de palha. São primitivas cruas no
  herói.
- **Correção:**
  - Cepo de madeira de Ø 1,6 × 1,2, com anéis e cintas de ferro.
  - Bigorna de ferro com chifre, mesa, calcanhar e cintura (0,9 × 0,45 × 0,6).
  - Tenaz e martelo apoiados; cocho de têmpera ao lado.
- **Evidência:** `A05_forja_patio_bigorna_forno.jpg`.

### 35 [P] Carvoeira do pátio do carvão é um domo liso
- **Onde:** (−112; 400), luz `L_DSFrg_Kiln` em (−112; 393,3). Câmeras `Z_Forno_CarvaoFora` e `C_Frg_Carvao`.
- **Problema:** semiesfera lisa de `Plaster_DS_Clay` de Ø ~10, com a boca em caixa de pedra. Lê "iglu" ou esfera
  primitiva.
- **Correção:**
  - Forno de carvão em pedra: 5 anéis de pedras de 0,8 fechando em cúpula escalonada.
  - Boca em arco com lintel e 2 respiros.
  - Terra só no topo e lenha encostada.
  - Ou kiln semienterrado com muro de arrimo.
- **Evidência:** `A05_forja_patio_bigorna_forno.jpg`.

### 36 [P] Pátio do carvão vazio
- **Onde:** x −150..−40, y 372..440. Câmeras `R_CO_02–04`, `R_VF_06–07` e `R_FO_03–04`.
- **Problema:** em ~7.000 studs² há só o alpendre, 2 pilhas de lenha, 2 feixes e o forno. O plano pede "sacos e
  pilhas de lenha, carvoeira de pedra".
- **Correção:**
  - 3 pilhas de lenha de 6 × 2 × 2,5.
  - 8–12 sacos de carvão (`tawara_pile` com `charcoal=True`) em 2 grupos.
  - Carrinho (`daihachi`), 2 cestos e galpão aberto de secagem de 10 × 6.
  - Cerca baixa delimitando o pátio e a trilha do item 04.
- **Evidência:** `A04_T4_oeste_vazio.jpg`.

### 37 [P] Guarda-corpo da borda sul do pátio coplanar
- **Onde:** (−19,4; 436,6; 82,2) e ao longo de y 436. É a chegada da SubidaB, vista da clareira inteira.
- **Problema:** `Wood_DS_Dark` × `Wood_DS_Mid` a 0,1, 257 faces voltadas para −y.
- **Correção:** corrimão Mid 0,15 para fora, ou um só material.
- **Evidência:** tabela de z-fight; `close_11.jpg` (`C_Frg_CercaPatio`).

### 38 [L] Forno colado na base da torre e chaminé coplanar
- **Onde:** (~37; 480). Câmera `C_Frg_TorreBase`.
- **Problema:**
  - O forno de tijolo está encostado na alvenaria sem recorte, com grama na boca e uma junta escura atravessando a
    torre na altura do topo dele.
- **Correção:**
  - Recortar a alvenaria e dar ao forno uma cobertura própria.
  - Tirar a grama da boca.
- **Evidência:** `A14_kit_detalhes.jpg` e `close_14.jpg`.

### 39 [L] Aqueduto: calha em caixa lisa
- **Onde:** (97–100; 500–548). Câmera `C_Frg_Aqueduto`.
- **Problema:** a calha é uma caixa lisa. Também há madeira × madeira a 0,07 no topo (97,8; 534,1; 103,4), 72 faces.
- **Correção:** calha em U (fundo + 2 laterais de 0,2), travessas a cada 2,5 e topo sem coplanar.
- **Evidência:** `close_10.jpg`.

### 40 [L] Oficina e ala leste: janelas laterais em painel branco liso
- **Onde:** câmeras `C_Frg_Oficina` e `C_Frg_AlaLeste`.
- **Problema:** as janelas laterais são painéis brancos lisos, sem grade.
- **Correção:** grade koshi de 0,12 ou shoji com kumiko, como na fachada.
- **Evidência:** `close_13.jpg` e `close_10.jpg`.

### 41 [L] Coplanares menores da forja
- **Onde e problema:**

  | Peça | Materiais | Distância | Ponto |
  |---|---|---|---|
  | Lanternim do salão | `Stone_DS_Dark` × `Soot` | 0,06 | (±7,5; 468,4; 99,7), 18 faces |
  | Salão | `Soot` × `Wood_DS_Dark` | 0,004 | (5,9; 468,8; 95,9), 3 faces |
  | Salão | `Brick` × `Soot` | 0,076 | (−5,8; 469,4; 87,9), 4 faces |
  | Ala leste | `Plaster_DS_Clay` × `Wood_DS_Dark` | 0,0 | (73,6; 475; 86,8), 11 faces |
  | Fornalha | `Cloth_DS_Indigo` × `Plaster_DS_Kura` | 0,036 | (10,5; 476,4; 82,4), 12 faces |

- **Correção:** afastar 0,12.
- **Evidência:** tabela de z-fight.

---

## ds_water

### 42 [L] Cascata fina
- **Onde:** `FX_Fall_1` (112; 400). Câmera `C_Ter_Cachoeira`; no jogo, `11_cascata` e `13_lagoa_v2`.
- **Problema:** no jogo, a lâmina é estreita entre as colunas.
- **Correção:**
  - Lâmina de 3 → 5 de largura.
  - Lábio de pedra no topo (2 pedras salientes de 0,4).
  - Espuma no pé (marcador `FX_*` de névoa).
- **Evidência:** `close_19.jpg`.

### 43 [L] Pedras de borda do canal leste sem apoio
- **Onde:** 22 pedras de `DS_Water_Stone` em (118–125; 273–307; 60,1).
- **Problema:** as pedras ficam 0,2 acima do leito. Só é visível olhando para dentro do canal da pontezinha.
- **Correção:** baixar 0,25.
- **Evidência:** `close_27.jpg`.

---

## ds_veg

### 44 [P] Troncos atravessando lanterna e cerca no antecampo
- **Onde e problema:**
  - A árvore `DS_Veg_Clareira` (23,4; 137,6) engole o poste da lanterna grande `DS_Prop_Lamps` (21; 138,7):
    75 pares de faces.
  - A árvore (46; 140) atravessa a cerca `DS_Prop_Clearing`, com a travessa entrando no tronco.
  - Os troncos de `DS_Veg_Clareira` (16,1; 143,2) e `DS_Veg_ClareiraN` (−36,3; 264,6) encostam em lanternas de
    caminho.
  - É a junção de chegada à clareira.
- **Correção:**
  - Deslocar as 3 árvores 3–4 ao longo da margem, com o tronco a ≥ 2,5 de qualquer prop ou cerca.
  - Reconferir com `BVH.overlap` contra `DS_Prop_*`. A regra de colocação do lado dos props é o item 51.
- **Evidência:** `A08_troncos_em_props.jpg`.

### 45 [L] Troncos descendo a falésia
- **Onde e problema:** quatro árvores enraizadas abaixo do platô, com o tronco correndo pela falésia:

  | Árvore | Ponto | Altura do tronco | Observação |
  |---|---|---|---|
  | `DS_Veg_Summon` | (193,5; 259,4) | 35 | – |
  | `DS_Veg_Summon` | (203,9; 286,2) | 21 | Atravessa `DS_Sum_Wood` em (202,2; 286,5; 63,2) |
  | – | (140,5; 392,3) | 28 | – |
  | `DS_Veg_Carvao` | (−139; 484,6) | 37 | – |

- **Correção:** replantar na cota do topo, ou encurtar e inclinar 15° para fora da parede.
- **Evidência:** tabela de interpenetração.

### 46 [L] Folhas e brotos sem contato
- **Onde:** ilhas de `Leaf_DS_Shrub` 0,23–0,46 acima do chão em (−84,3; 289,2), (−74,6; 351,5), (−136,8; 289,7),
  (−107,8; 308,1), (−91; 300), (−126,3; 225,5), (−133,4; 231), (−48,6; 230), (93,9; 386,1), (79,2; 365,5) e
  (132; 288); broto de bambu em (23,4; 73,3).
- **Correção:** baixar até enterrar 0,1.
- **Evidência:** lista de peças sem apoio (`analysis.json`).

### 47 [L] Bambu: nós em fita clara uniforme
- **Onde:** `DS_Veg_Bamboo`. Câmeras `C_Bam_Rampa` e `C_Bam_Touceira`.
- **Problema:** o nó é um anel `Bamboo_DS_Dry` de 0,25, claro, no mesmo intervalo em todos os colmos. Lê como fita
  adesiva.
- **Correção:**
  - Nó como alargamento de 1,08× com 0,12 de altura.
  - Cor `Bamboo_DS` 15% mais escura.
  - Intervalo crescente da base ao topo (0,8× → 1,2×).
- **Evidência:** `close_02.jpg`.

### 48 [L] Arbusto da mesma cor da grama
- **Onde:** global.
- **Problema:** `Leaf_DS_Shrub` (66/104/56) quase igual a `Grass_DS_B` (76/108/58), Δ 11. As moitas somem no
  chão sem textura.
- **Correção:** moitas sobre grama com `Leaf_DS_Broad` (46/84/48), ou deixar a moita 15% mais escura.
- **Evidência:** `close_19.jpg` e `rota_CF_2.jpg`.

### 49 [L] Pérgola do bambuzal: cachos sobre o caminho
- **Onde:** (60,7; 116,9) e (63,3; 124,4). Câmera `R_EB_05`.
- **Problema:** é onde a câmera de 3ª pessoa encosta (10–12) e os cachos ocupam o topo do quadro.
- **Correção:** cachos a ≥ piso +8 numa faixa de 2,5 de cada lado do eixo do caminho.
- **Evidência:** `rota_EB_2.jpg` e `close_02.jpg`.

---

## ds_props

### 50 [P] Lanterna de caminho (`lamp_box`, 97 unidades) lê como caixa de luz
- **Onde:** todas as rotas. Câmeras `C_Lan_Poste`, `C_Lan_Andon` e `C_Lan_Forja`; no jogo, `03`, `05` e `12`.
- **Problema:**
  - O papel é uma caixa inteira de Neon. A frente tem só 2 cintas de 0,09 ("≡"), com o beiral curto de propósito
    ("o papel lê de cima").
  - No Play vira bloco aceso. É o mesmo problema do item 23, em 97 cópias.
- **Correção:**
  - Cintas de 0,09 → 0,16 e 1 montante central de 0,12 por face (grade de 2 × 3).
  - Neon só no terço do meio; o resto em `Plaster_DS_Shoji`.
  - Beiral de 0,2 → 0,35.
- **Evidência:** `A06_lanternas_caixa_de_luz.jpg`.

### 51 [L] Densidade e ritmo das lanternas
- **Onde:** antecampo (`R_EC_03`), margem leste da clareira (`R_CS_04`) e T4 (`A04`).
- **Problema:**
  - As 97 lanternas ficam a cada ~13, alternando poste alto e andon baixo **estritamente** (A/B/A/B).
  - Há 6–10 lanternas por quadro. No T4 elas ficam no vazio, sem caminho.
- **Correção:**
  - Tirar ~35% (as do meio dos trechos retos), mantendo os nós, as escadas e os portões. Espaçamento de 18–22 nos
    trechos longos.
  - Ritmo A-A-B ou trocar o tipo por trecho.
  - Na `plan_lamps`, rejeitar pontos a < 2,5 de `COL_DS_VegTrunk` (item 44).
  - No T4, só lanternas que acompanham a trilha do item 04.
- **Evidência:** `rota_EC_1.jpg`, `rota_CS_1.jpg` e `A04_T4_oeste_vazio.jpg`.

### 52 [L] Props atravessando paredes
- **Onde e problema:** `DS_Prop_Village` entra nas paredes de três casas:

  | Casa | Ponto | Pares de faces |
  |---|---|---|
  | V2 (lenheiro/bancada) | (−92; 166,9; 61,3) | 167 |
  | V5 | (−92,5; 291,9; 67,2) | 101 |
  | V3 | (−83,9; 191,1; 61,2) | 23 |

- **Correção:** recuar 0,3 da face da parede.
- **Evidência:** `conf_05.jpg` (`Z_PropV2`).

### 53 [L] Lanterna do pé da escada do summon entra na bochecha
- **Onde:** `DS_Prop_Lamps` (126,1; 293,4).
- **Problema:** a base entra na bochecha de pedra da escada (24 pares de faces).
- **Correção:** mover 1,0 para oeste.
- **Evidência:** `close_16.jpg` (`C_Lan_SumEscada`).

### 54 [L] Coplanares de props
- **Onde e problema:**
  - Varal: `Cloth_DS_Ai` × `Cloth_DS_Linen` a 0,04 em (−104,1; 176,4; 63,9), 22 faces.
  - Corda × pedra a 0,12 em (−58,4; 461,7; 80,3), 39 faces.
  - Madeira × madeira a 0,1 em (49,9; 459,9; 80,2).
  - Bambu × madeira a 0,068 em (−85,7; 188,3; 61,3), 95 faces.
- **Correção:** afastar 0,12.
- **Evidência:** tabela de z-fight.

---

## ds_lights / ds_vfx

### 55 [L] Hierarquia de luz no Play
- **Onde:** global; no jogo, `02_visao_geral` e `05_vila_baixa`.
- **Problema:** ~110 papéis Neon (232/146/66) somados ao bloom fazem um campo de pontos que compete com a boca da
  forja.
- **Correção (junto com os itens 23 e 50):**
  - Manter as 12 PointLights de nó.
  - Baixar a saturação do papel para ~220/150/90.
  - Conferir no Play que a boca (`L_DSFrg_FurnaceMouth`) e a torre ficam as luzes dominantes vistas do antecampo.
- **Evidência:** `renders/ingame/`.

### 56 [L] Prévia de VFX vira bloco branco no modo `roblox`
- **Onde:** `PREVIEW_VFX_Mist`, `PREVIEW_VFX_Embers`, `PREVIEW_VFX_Smoke` e `PREVIEW_VFX_Foam` (`00_REFERENCE`).
- **Problema:**
  - Os materiais de prévia não estão em `MATS`. Com `FM_MAT_PREVIEW=roblox`, viram principled opaco.
  - A névoa do bambuzal parece neve no chão e as brasas da boca são bolas brancas.
  - Isso polui todas as folhas de QA no modo que vale. Não afeta o export.
- **Correção:** registrar os materiais de prévia (transparentes) no `ds_vfx`, ou esconder `PREVIEW_VFX_*` quando
  `PREVIEW == "roblox"`.
- **Evidência:** `A13_previa_vfx_roblox.jpg`.

---

## Resumo

| Dono | P | L | Total |
|---|---|---|---|
| ds_terrain | 4 (01–04) | 7 | 11 |
| ds_entry | 1 (12) | 2 | 3 |
| ds_exit (+ il_gate_op) | 1 (15) | 3 | 4 |
| ds_summon | 3 (19–21) | 1 | 4 |
| ds_kit | 4 (23–26) | 3 | 7 |
| ds_village | 1 (30) | 2 | 3 |
| ds_forge | 5 (33–37) | 4 | 9 |
| ds_water | 0 | 2 | 2 |
| ds_veg | 1 (44) | 5 | 6 |
| ds_props | 1 (50) | 4 | 5 |
| ds_lights / ds_vfx | 0 | 2 | 2 |
| **Total** | **21** | **35** | **56** |

**Os 10 mais graves** (ordem de ataque na 6b):
1. **04 + 36 + 33:** o T4 inteiro (pátio do carvão, chegada da OesteForja e pátio de trabalho) é chão liso de uma
   cor com lanternas soltas. O capítulo herói lê vazio.
2. **01:** as paredes lisas da SubidaA (`DS_Ter_Bodies`) no eixo de subida da forja.
3. **03:** o ishigaki em fiadas de tijolo (patamar, vila, entrada). No jogo, lê "Minecraft".
4. **23 + 50:** as lanternas de papel leem como caixa de luz no Play: 97 de caminho e as de nó do kit.
5. **24 + 12:** as escadas em laje inteiriça. A Trilha ainda usa a escada do blockout (`DL.plan_stair`).
6. **34 + 35:** a bigorna do pátio (cubo + caixa) e a carvoeira em domo liso, primitivas no herói.
7. **02:** a vala escura ao lado da escada Trilha, no primeiro quadro do jogo.
8. **19 + 20:** os coplanares do summon (pé da escada com o chão e pódio dourado × pedra) à altura do olho.
9. **25 + 26 + 30:** os coplanares do kit em todas as casas (janela acesa a 0,06, cumeeira × hafu e empena, shoji
   da V6 a 0,03).
10. **21 + 44:** as glicínias do summon descendo até o chão (outra família) e os troncos engolindo a lanterna e a
    cerca no antecampo.

**O que já sobrevive a close-up:**
- a boca da forja e o interior do salão;
- as espadas (lâmina, tsuba, ito);
- a roda d'água;
- o hokora;
- a V6, por dentro e no jardim;
- as fachadas da vila;
- a pontezinha do summon.

Navegação, pé-direito e câmera de 3ª pessoa: sem problema estrutural.
