# AUDITORIA 3: passe de finesse da Ilha 3 reconstruída (planta v4, export b4d23c3b)

Data: 2026-10-01. Auditor: direção de arte. Nenhum módulo de geometria foi editado: o único acréscimo é o bloco de
câmeras `CAM_A3_*` no fim de `sg_scene.py` (`a3_cams()` / `cameras_a3()`; o build não as chama).

**A pergunta de cada item:** está realmente bom de perto, na altura do jogador? O usuário chamou a ilha de BLOCKOUT. A
auditoria confirma: a planta, a escala e os sistemas estão certos, mas as **grandes superfícies** que o jogador vê
(chão, paredes de 0 a 20, abóbadas, falésia) continuam lisas, e o detalhe ficou concentrado em props pequenos.

**Base:**
- 185 câmeras novas (`CAM_A3_<setor>_<lugar>`): olho a 5,5 acima do piso em todas as rotas, mais vistas médias e de
  longe. Renderizadas a 960 × 540 nos dois modos, a partir de `ilha_shadowgarden.blend` (o build do export
  b4d23c3b, sem salvar), com os bonecos de escala `SCALE_Dummy_*` (5,2) visíveis.
- As 7 fotos do jogo em Play (Studio, luz real da área) que a coordenação tirou.
- A leitura dos módulos `sg_*.py`, da paleta em `sg_lib.SMATS` e do export de luz.

**Legenda de caminhos**

| Prefixo | Pasta |
|---|---|
| `P/` | `renders/auditoria3/previa/` (prévia do Blender, com textura procedural) |
| `R/` | `renders/auditoria3/roblox/` (`FM_MAT_PREVIEW=roblox`: cor que o Roblox recebe, sem textura, Neon brilhando) |
| `J/` | `renders/auditoria3/jogo/` (fotos do jogo) |

O nome do arquivo é o nome da câmera sem o prefixo `CAM_A3_` (ex.: `R/09_Galeria_Chegada.jpg`).

**Tiers:** A = hero (sobrevive a close-up), B = arquitetura, props e ruas na câmera do jogador, C = silhueta e fundo.

**[CRÍTICO]:** quebra na câmera normal do jogador (olho ~5,5, avatar de 5) ou na primeira impressão da área.

**Avisos sobre a fonte:**
- **A prévia do Blender é mais clara que o jogo nos interiores.** O export (`export_roblox.lights`) corta TODA luz
  para Range ≤ 20 e Brightness ≤ 1,5 (item 15.01). Então o `R/` mostra a cor certa, mas a luz ainda é a do Blender;
  o salão, o Salão Sombrio e as salas são bem mais escuros no Play (`J/06`, `J/07`).
- Nuvens, lua e as silhuetas das ilhas vizinhas são só prévia (`PREVIEW_*`, `SG_Sky_Clouds`): não auditados como
  jogo.
- `14_Quilha` ficou abaixo do mar (−110) e não mostra nada; `12_Ponte_Lado` ficou dentro da massa do encontro da
  ponte do summon. Ambos estão fora da leitura.

---

## 01 Ponte de chegada e entrada

### 01.01 [CRÍTICO] Calçada alta do spawn é um plano liso · Tier B
- **Errado:** o patamar entre o pórtico B e a praça (`EntryHigh`, 24 × 30) é um plano único de `Stone_Paving_SG`,
  sem laje, junta, bevel nem borda. É a primeira coisa que o jogador pisa e vê de perto. No jogo é um tapete lilás
  liso, e ainda leva a placa Neon do lobby (01.12).
- **Onde:** `J/01_ponte_chegada.jpg`, `P/01_Spawn_Volta.jpg`, `R/01_Spawn_Volta.jpg`.
- **Código:** `sg_terrain.py: tops()` (`base["EntryHigh"] = PAVE`, sem `pave_zone`); `sg_entry.py: porticos()` não
  pavimenta.
- **Direção:**
  - Lajes em fiadas transversais de 3 por fiada, com junta desencontrada, junta rasa (0,05) e bevel 0,04, como as
    lajes da ponte (`sg_entry.deck`).
  - Soleira de cantaria de 1,2 sob cada pórtico.
  - Meio-fio de 0,6 no contorno.
  - Rosa-dos-ventos ou disco de pedra (sem emblema) no ponto do spawn.

### 01.02 [CRÍTICO] Degraus da escadaria de entrada: lajes contínuas · Tier B
- **Errado:** os 10 degraus de 20 de largura são lajes inteiras, sem divisão em pedras, sem focinho e sem espelho
  recuado. No Roblox, lê como rampa listrada. É o item 01.01 da AUDITORIA 2 que voltou na escala nova.
- **Onde:** `P/01_Escada.jpg`, `R/01_Escada.jpg`, `P/01_PatioBaixo.jpg`.
- **Código:** `sg_entry.py: stair()` → `sg_lib.py: plan_stair` (a mesma função de todas as escadas do plano; ver
  16.03).
- **Direção:**
  - Cada degrau em 4 ou 5 pedras com junta desencontrada degrau a degrau.
  - Focinho saliente de 0,12 com chanfro de 0,06, um valor mais claro.
  - Espelho recuado, um valor mais escuro.
  - Degrau de arranque e de chegada mais largos.

### 01.03 Banzos da escadaria de entrada · Tier B
- **Errado:** prisma liso inclinado com uma capa-viga larga (≈1,75) e clara por 20 studs. Sem fiada, sem plinto e sem
  pilarete de arranque com moldura.
- **Onde:** `P/01_Escada.jpg` (direita), `R/01_Escada.jpg`.
- **Código:** `sg_entry.py: stair_wall()`.
- **Direção:** paramento em fiadas, capa em peças de 2,5 com pingadeira, plinto de 0,5 e dado moldurado no pé.

### 01.04 [CRÍTICO] Fustes dos pórticos A e B: totens lisos · Tier A
- **Errado:** os 4 fustes têm ~30 de altura e são caixas lisas. A lanceta cega é um rebaixo raso que no Roblox some
  (só sobra um painel escuro). O embasamento é uma caixa. De perto, na chegada, é o primeiro "blockout" que o jogador
  vê.
- **Onde:** `P/01_PorticoB.jpg`, `R/01_PorticoB.jpg`, `J/01_ponte_chegada.jpg` (primeiro plano), `P/01_Escada.jpg`.
- **Código:** `sg_entry.py: pylon()`, `lancet()`.
- **Direção:**
  - Quinas chanfradas de 0,3 com colunelo de canto até o friso.
  - Faixa de fiadas de 2 alturas no terço inferior (0 a 10).
  - Lanceta recuada 0,6 com peitoril, mainel e arco de espessura real.
  - Embasamento em 3 degraus (plinto, toro, talude).

### 01.05 Verga do pórtico B: viga fina sobre 2 totens · Tier A
- **Errado:** a verga é uma barra lisa e baixa sobre fustes de 30. Proporção de trave de futebol: sem arco, cimalha
  nem aduela.
- **Onde:** `P/01_PatioBaixo.jpg`, `P/02_Praca_Norte.jpg`, `R/03_EscP1P2_Topo.jpg`.
- **Código:** `sg_entry.py: lintel_b()`.
- **Direção:** arco abatido ou verga com altura ≥ 1/8 do vão, com cimalha, friso e fecho esculpido (sem emblema).

### 01.06 Parapeito da ponte: 230 studs do mesmo painel · Tier B
- **Errado:** painel liso com capa contínua e pilarete com pinha a cada tramo, idênticos do primeiro ao último stud.
  Sem ritmo e sem ênfase nos nós.
- **Onde:** `P/01_Ponte_Parapeito.jpg`, `R/01_Ponte_Ancora.jpg`, `R/01_Ponte_Lajes.jpg`.
- **Código:** `sg_entry.py: bridge_parapet()`, `post_sv()`.
- **Direção:**
  - Ritmo A-B: sobre os pilares, pilarete com remate do kit e saliência (balcão).
  - Nos tramos, painel com arcada cega rasa (0,15) só nos tramos dos nós.
  - Rodapé de 0,3 e pingadeira na capa.
  - Pinha só nos pilaretes dos nós.

### 01.07 [CRÍTICO] Encontro da ponte com a ilha · Tier B
- **Errado:** o último tramo morre num bloco retangular cravado na falésia. O arco termina dentro da rocha, com
  "dentes" de rocha pendurados dentro do vão. No tímpano sobra uma pilastra em T solta. A transição ponte × ilha é a
  pior junta da chegada.
- **Onde:** `P/01_Ponte_Encontro.jpg`, `R/01_Ponte_Encontro.jpg`, `R/14_Ilha2_Perto.jpg`.
- **Código:** `sg_entry.py: abutment()`, `arch()`, `face_spandrel()`; `sg_terrain.py: rim_cliff()`, `neck()`.
- **Direção:**
  - Encontro de cantaria em talude, com embasamento escalonado que abraça a rocha.
  - Último arco nascendo de uma imposta do encontro.
  - Tirar a rocha de dentro do vão (recorte do terreno no encontro).
  - Tirar a pilastra em T.

### 01.08 Tímpanos e intradorso dos arcos da ponte · Tier C/B
- **Errado:** tímpanos lisos; o arco é uma faixa de moldura sem aduela. De lado, os 7 arcos leem como uma chapa
  recortada.
- **Onde:** `P/01_Ponte_Lado.jpg`, `R/01_Ponte_Lado.jpg`.
- **Código:** `sg_entry.py: arch()`, `face_spandrel()`, `arcade()`.
- **Direção:** aduelas radiais nas 2 faces, cordão na cota do tabuleiro e pingadeira sob o parapeito.

### 01.09 Rochas sob os pilares da ponte · Tier C
- **Errado:** blocos hexagonais low-poly empilhados, uns sobre os outros. Família diferente do penhasco.
- **Onde:** `P/01_Ponte_Lado.jpg`, `P/14_Ilha2.jpg`.
- **Código:** `sg_entry.py: rock()`, `pier()`.
- **Direção:** a rocha em estratos do penhasco (`sg_terrain.block_strata`), com base cônica em quilha.

### 01.10 Lajes da ponte com lábios · Tier B
- **Errado:** na prévia, lajes vizinhas com topos em alturas diferentes (~0,1) e sombra embaixo. O jogador anda
  "tropeçando" visualmente.
- **Onde:** `P/01_Ponte_Lajes.jpg`.
- **Código:** `sg_entry.py: deck()`.
- **Direção:** topo comum; variação só de tom (2 tons dirigidos) e bevel 0,04.

### 01.11 Grama dos flancos do pátio baixo · Tier B
- **Errado:** talude de grama liso e escuro chegando até o parapeito, sem meio-fio, pedra ou plantio de borda.
- **Onde:** `P/01_PatioBaixo.jpg`, `P/01_PorticoA_CU.jpg`.
- **Código:** `sg_terrain.py: emit_top()` (ombro em grama), `sg_garden.py: fringe()`.
- **Direção:** meio-fio de cantaria, faixa de cascalho e touceiras agrupadas contra o parapeito.

### 01.12 Placa ciano "voltar ao lobby" no pátio de chegada · Tier B
- **Errado:** placa Neon ciano no chão do spawn: a cor mais saturada da chegada.
- **Onde:** `J/01_ponte_chegada.jpg`.
- **Código:** AreaBuilder (Roblox), fora do pipeline.
- **Direção:** **removida no Roblox** (pedido do usuário). Só registro.

---

## 02 Praça e fonte

### 02.01 [CRÍTICO] A praça é um disco num descampado liso · Tier B
- **Errado:** fora do disco de R 26, o P1 inteiro (cerca de 330 × 130) é o plano liso de `Stone_Paving_SG`. No
  Roblox, ele tem o mesmo valor das lajes da praça: o anel quase some (`R/02_Praca_Alta`). Não há borda, canteiro,
  mureta, mercado nem mobiliário. As casas ficam a mais de 60 studs, então a praça não tem "paredes". Visto do topo
  da escada P1P2, é um estacionamento vazio.
- **Onde:** `P/02_Praca_Alta.jpg`, `R/02_Praca_Alta.jpg`, `P/03_EscP1P2_Topo.jpg`, `R/03_EscP1P2_Topo.jpg`,
  `J/02_praca.jpg`.
- **Código:** `sg_terrain.py: tops()` (`base["P1"] = PAVE`); `sg_village.py: plaza()`, `streets()`.
- **Direção:**
  - Trocar o chão do P1 por campo de lajes (`sg_village.sett` em grade) ou por gramado/terra batida com meio-fio. O
    plano liso não pode sobrar em lugar nenhum.
  - Escala de valor: praça mais clara, ruas médias, sobra escura.
  - Fechar a praça com bordas que o jogador lê: muretas baixas com banco, canteiros elevados, 2 bancas de mercado,
    um poço, uma carroça.

### 02.02 Fonte pequena e empilhada para a praça · Tier A
- **Errado:** bacia de R 7 numa praça de R 26. A silhueta continua sendo 3 discos (bacia, taça, taça) sobre fuste
  torneado. As pilastras da bacia são caixas. A estátua do topo é o mesmo guardião da porta do castelo (02.03).
- **Onde:** `P/02_Fonte_CU.jpg`, `P/02_Praca_Norte.jpg`, `R/02_Fonte_CU.jpg`, `J/02_praca.jpg`.
- **Código:** `sg_village.py: plaza()` (bloco da fonte), `fountain_statue()`.
- **Direção:**
  - Escala 1,3×.
  - Bacia em 2 degraus com bordo em toro.
  - Taças com perfil contínuo (gola, bojo, bico) e carrancas nas bicas.
  - Pilastras com base e capitel.

### 02.03 Estátua da fonte = guardião da porta · Tier A
- **Errado:** é a mesma figura (`hooded_figure` "guard") das 2 estátuas da porta. O hero se repete no eixo da
  chegada.
- **Onde:** `P/02_Fonte_CU.jpg` vs `P/06_Guardas.jpg`.
- **Código:** `sg_village.py: fountain_statue()` → `sg_court.py: hooded_figure()`.
- **Direção:** figura própria para a fonte (ninfa encapuzada com cântaro, ou a lua sobre um pedestal com 4 bicas).

### 02.04 Borda do disco da praça · Tier B
- **Errado:** o anel termina num degrau baixo direto contra o plano liso, sem meio-fio nem faixa de transição.
- **Onde:** `P/02_Praca_Piso.jpg`, `P/02_Praca_Chegada.jpg`.
- **Código:** `sg_village.py: plaza()`.
- **Direção:** meio-fio de cantaria de 0,8 em segmentos de 3 e faixa de lajes radiais até o chão novo (02.01).

### 02.05 Bancos da praça · Tier B
- **Errado:** laje sobre 2 blocos com encosto-placa. Mesma peça em toda a ilha.
- **Onde:** `P/02_Praca_Chegada.jpg`, `R/02_Praca_Chegada.jpg`.
- **Código:** `sg_props.py: bench()`.
- **Direção:** pés em voluta ou garra, assento com 2 peças e frente moldurada, encosto com arco cego.

### 02.06 Muro de arrimo atrás da fonte · Tier B
- **Errado:** faixa horizontal contínua, de valor uniforme, fechando toda a vista norte da praça. É a "parede" que
  falta à praça, mas sem um acontecimento.
- **Onde:** `J/02_praca.jpg`, `P/02_Praca_Chegada.jpg`, `R/02_Praca_Chegada.jpg`.
- **Código:** `sg_terrain.py: masonry()`, `buttresses()`, `corbels()`.
- **Direção:** 2 nichos com banco ou fonte de parede de cada lado da escada, trepadeiras dirigidas e floreiras na
  capa.

### 02.07 Vista sul da praça termina no vazio · Tier B
- **Errado:** olhando para a chegada, o fundo é céu, com o pórtico B isolado e 2 ciprestes. Não há massa que emoldure.
- **Onde:** `P/02_Praca_Norte.jpg`, `R/02_Praca_Norte.jpg`.
- **Código:** `sg_village.py: build()` (layout dos lotes H1/H3), `sg_veg.py: groves()`.
- **Direção:** muretas e árvores dirigidas nos 2 lados do eixo sul, e uma arcada leve ligando o pórtico B às casas
  H1 e H3.

### 02.08 Ciprestes facetados em volta da praça · Tier B
- **Errado:** cones de 6 a 8 lados empilhados, com facetas duras.
- **Onde:** `P/02_Praca_Norte.jpg`, `P/02_Praca_Piso.jpg`.
- **Código:** `sg_veg.py: cypress()`.
- **Direção:** ver 16.04.

---

## 03 Vila (exterior)

### 03.01 [CRÍTICO] Vila esparsa: 7 casas num platô vazio · Tier B
- **Errado:** entre as casas sobram de 40 a 60 studs de chão liso (P1) ou gramado chapado (P2). As ruas têm 10 de
  largura e nada nas bordas. Não há quintal, cerca, muro de lote, galpão, poço, carroça, barril, banca nem varal.
  Não lê como lugar habitado.
- **Onde:** `P/03_Vila_Media.jpg`, `P/03_VilaAlta_Media.jpg`, `P/03_RuaP1_E.jpg`, `R/03_RuaP1_W.jpg`,
  `P/03_Gramado_P1.jpg`, `J/03_vila_rua_P2.jpg`.
- **Código:** `sg_village.py: build()`; `sg_props.py: build()` (só postes e bancos); `sg_garden.py: village_beds()`.
- **Direção:**
  - Cada lote ganha um quintal delimitado (mureta de 1,2, cerca de madeira ou sebe) com 3 a 5 props do ofício:
    - ferreiro: lenha, bigorna, carvão e tina;
    - taverna: barris, mesa externa e placa;
    - boticário: canteiro de ervas e estufa pequena;
    - minerador: carrinho, trilho e pilha de minério;
    - guarda: armeiro e alvo.
  - Anexos baixos (alpendre, galpão) encostados nas casas para fechar as ruas.
  - Poço e 2 bancas na praça.
  - Os props entram num módulo de vestir (`sg_props`), sem mexer no layout.

### 03.02 [CRÍTICO] Ruas com "faixa central" de estrada · Tier B
- **Errado:** a faixa de lajes tem 2 lajes por fiada e a junta perto do meio (42/58). A junta escura de 0,12 vai até
  o leito. Em perspectiva, a sequência de juntas centrais lê como faixa tracejada de rodovia. Acontece em todas as
  ruas da vila e no eixo P2.
- **Onde:** `R/03_RuaP1_E.jpg`, `R/03_RuaP1_W.jpg`, `P/03_EixoP2.jpg`, `J/03_vila_rua_P2.jpg`.
- **Código:** `sg_village.py: pave_strip()` (`split=(0.42, 0.58)`, junta até o leito), `_row_poly()`.
- **Direção:**
  - 3 ou 4 lajes por fiada, com junta em módulos irregulares dirigidos (0,22 / 0,31 / 0,47) que mudam de fiada para
    fiada.
  - Junta rasa de 0,05, num tom médio (não preto).
  - Meio-fio de cantaria e sarjeta rasa nas 2 bordas.

### 03.03 [CRÍTICO] Gramados chapados · Tier B
- **Errado:** `Grass_SG` (40, 62, 57) é um verde-escuro de um valor só, cobrindo o P2, o pátio, os becos e o terraço
  norte. As touceiras são pequenas e ralas e no jogo quase somem. Nenhum gramado tem bordadura.
- **Onde:** `J/03_vila_rua_P2.jpg`, `P/03_Gramado_P2.jpg`, `R/03_Gramado_P2.jpg`, `P/13_Beco_W2.jpg`,
  `P/13_Terraco_Norte.jpg`.
- **Código:** `sg_lib.py: SMATS["Grass_SG"]`; `sg_terrain.py: emit_top()`, `patch_polys()`; `sg_garden.py:
  field()`, `tuft()`, `fringe()`.
- **Direção:**
  - 2 a 3 tons de grama em manchas dirigidas: mais claro no luar e junto aos caminhos, mais escuro sob árvores e ao
    pé dos muros. São variantes de material, não ruído.
  - Touceiras de 0,8 a 1,4, agrupadas em faixas ao longo de muros, casas e caminhos, não salpicadas.
  - Bordadura em todo gramado (pedra de 0,4 ou faixa de cascalho).
  - Flores em faixas nas bordas, não no meio.

### 03.04 [CRÍTICO] Escada P1→P2: degraus em lajes contínuas · Tier B
- **Errado:** é a mesma escada-laje da entrada (01.02), com 18 de largura, bem no eixo da vila.
- **Onde:** `P/03_EscP1P2_Pe.jpg`, `R/03_EscP1P2_Pe.jpg`.
- **Código:** `sg_village.py: stairs_p1p2()` → `sg_lib.py: plan_stair`; `stair_banzo()`.
- **Direção:** ver 01.02 e 16.03.

### 03.05 Muro de arrimo P1→P2 em passo fixo · Tier B
- **Errado:** contraforte em talude, mísulas com arquinhos e fiadas, todos idênticos em passo constante por ~330
  studs. O pé encosta direto no chão liso, sem rodapé.
- **Onde:** `P/03_Arrimo_Frente.jpg`, `R/03_Arrimo_E.jpg`, `P/03_Arrimo_W.jpg`, `R/11_DoP1.jpg`.
- **Código:** `sg_terrain.py: masonry()`, `buttresses()`, `buttress_ts()`, `corbels()`.
- **Direção:**
  - Ritmo A-B: contraforte largo nos nós (escadas, eixos, quinas) e estreito nos tramos.
  - Rodapé saliente de 0,4.
  - 2 ou 3 acontecimentos: fonte de parede, nicho com banco, escadinha lateral.
  - Trepadeiras só nos tramos centrais.

### 03.06 [CRÍTICO] Trepadeiras feitas de bolotas · Tier B
- **Errado:** colunas de icosferas verdes com pontos brancos, presas às fachadas e à muralha. Primitiva óbvia na
  altura do olho, ao lado de toda porta de casa.
- **Onde:** `P/03_H1_Frente.jpg`, `P/03_H7_Frente.jpg`, `R/03_H7_Frente.jpg`, `P/05_Muralha_Dentro.jpg`.
- **Código:** `sg_garden.py: vine()`, `house_vines()`, `court_vines()`.
- **Direção:** caule visível em ramos com folhas em cards achatados (losangos dobrados), em 2 tons. Ou tirar: a
  fachada da casa já tem estrutura.

### 03.07 Floreiras-caixa em toda porta e janela · Tier B
- **Errado:** caixas lisas claras (cantaria Trim) no chão, mais floreiras de janela, de 2 a 4 por casa e quase
  iguais. No Roblox leem como concreto branco.
- **Onde:** `P/03_H4_Frente.jpg`, `P/03_H6_Frente.jpg`, `R/03_H6_Frente.jpg`, `P/03_H5_Lado.jpg`.
- **Código:** `sg_garden.py: ground_planter_planting()`, `window_box_planting()`; `sg_village.py: front_beds()`.
- **Direção:** é o filler da AUDITORIA 2 (16.08). Cortar metade. As que ficam: pedra escura com moldura ou madeira
  com cintas, rente à parede e no tom da casa.

### 03.08 Térreo das casas A repetido · Tier B
- **Errado:** H2, H3, H5 e H7 têm o mesmo térreo: porta 8 × 11 com verga em 3 blocos, loja com persiana, lanterna de
  braço e janela de pedra. De rua, parecem a mesma casa espelhada.
- **Onde:** `P/03_H3_Frente.jpg`, `P/03_H5_Frente.jpg`, `P/03_H7_Frente.jpg`, `P/03_H2_Frente.jpg`.
- **Código:** `sg_village.py: kit_house()`, `door_stone()`, `shopfront()`, `win_slots()`.
- **Direção:** variação dirigida pelo ofício:
  - H2: alpendre de madeira com a forja de mão.
  - H3: porta em arco com toldo de lona.
  - H5: portal com pingadeira gótica e degrau de pedra.
  - H7: escada externa para o andar e sacada.

### 03.09 Panos laterais cegos · Tier B
- **Errado:** as empenas e laterais das casas A e C, de cantaria e com 12 de altura, não têm janela, chaminé de
  encosto nem nada. Pano liso de 5 fiadas grandes, exatamente onde o jogador passa entre as casas.
- **Onde:** `P/03_H1_Lado.jpg`, `R/03_H1_Lado.jpg`, `P/03_H6_Lado.jpg`, `P/03_H2_Lado.jpg`.
- **Código:** `sg_village.py: kit_house()`, `win_defaults()`, `ashlar()`.
- **Direção:** 1 janela por pano lateral (ou postigo fechado), contraforte de canto, pilha de lenha ou banco
  encostado, fiadas menores (0,9) no terço inferior.

### 03.10 H4: laterais com 2 painéis de reboco enormes · Tier B
- **Errado:** a spec pede montantes cerrados (`frame="studs"`), mas a lateral tem 2 painéis lisos de ~9 × 8 entre
  postes grossos.
- **Onde:** `P/03_H4_Lado.jpg`, `R/03_H4_Frente.jpg`.
- **Código:** `sg_village.py: timber_face()` (laterais da casa C sem os montantes da frente).
- **Direção:** montantes a cada 1,6, travessa a meia altura, peitoril e mísulas, como na frente.

### 03.11 Torreão do H3 · Tier B
- **Errado:** prisma octogonal liso até 12, com faces grandes e embasamento-anel. É o "marco de quem chega", mas é a
  peça mais lisa da casa.
- **Onde:** `P/03_H3_Lado.jpg`, `R/03_RuaP1_E.jpg`.
- **Código:** `sg_village.py: turret()`.
- **Direção:** fiadas de 2 alturas, embasamento em talude com cordão, 2 frestas por andar e mísulas sob o balanço.

### 03.12 Janelas: vidraça inteira em Neon laranja · Tier B
- **Errado:** cada vidraça é um painel `Window_Warm` laranja saturado de ponta a ponta. No jogo é o laranja mais forte
  da ilha e estoura com o bloom. A AUDITORIA 2 (14.06) já pedia a luz só dentro de moldura.
- **Onde:** `J/02_praca.jpg`, `J/03_vila_rua_P2.jpg`, `P/03_H1_Frente.jpg`, `R/03_H2_Frente.jpg`.
- **Código:** `sg_village.py: window()`, `window_box()`; `fm_lib.MATS["Window_Warm"]` (compartilhado: criar
  `Window_Warm_SG` na paleta da ilha).
- **Direção:**
  - Vidro escuro (`Glass_SG_Rose` neutro) com o Neon recuado 0,4, numa faixa estreita (cortina iluminada).
  - Laranja um valor abaixo e menos saturado.
  - Metade das janelas com postigo meio fechado. Janelas do andar alternando acesa e apagada (dirigido, não
    sorteado).

### 03.13 [CRÍTICO] Vazamento de luz na base das paredes · Tier B
- **Errado:** um filete claro e brilhante corre no rodapé das laterais das casas: é a luz interna escapando pela
  fresta entre a casca e o piso interno. Aparece também no Roblox.
- **Onde:** `P/03_H1_Lado.jpg`, `R/03_H1_Lado.jpg`, `P/03_H2_Lado.jpg`, `P/03_H5_Lado.jpg`, `R/03_H7_Lado.jpg`.
- **Código:** `sg_village_int.py: linings()`, `floor_boards()` (`FLOOR = 0,30`) × `sg_village.py: socle()`.
- **Direção:** fechar a fresta. O forro desce até o soco, ou o piso encosta na casca com 0,05 de sobreposição. Depois,
  conferir com raio rente ao chão nas 4 faces das 7 casas.

### 03.14 H6 e H7 espremidas contra a muralha · Tier B
- **Errado:** o fundo das 2 casas fica a poucos studs do paramento da muralha. Sobra um corredor escuro, sem
  tratamento, onde o jogador pode entrar.
- **Onde:** `R/03_H6_Frente.jpg`, `R/03_H6_Lado.jpg`, `R/03_H7_Lado.jpg`.
- **Código:** `sg_layout.py: HOUSES` (layout travado), `sg_garden.py: plan_blocked()`.
- **Direção:** sem mover o lote: fechar o beco com mureta e portão de madeira, ou ocupar com lenha, barris e plantio.

### 03.15 Ruas que terminam em nada · Tier B
- **Errado:** a rua leste do P1 acaba no parapeito, sem destino. A rua do P2 a oeste morre na grama.
- **Onde:** `P/03_RuaP1_E.jpg`, `R/03_RuaP1_E.jpg`, `P/03_RuaP2_W.jpg`.
- **Código:** `sg_layout.py: STREETS` (não mudar); `sg_village.py: streets()`; `sg_props.py`.
- **Direção:** remate em cada ponta: mirante com banco e luneta, poço, cruzeiro de pedra ou pérgula. A vista
  enquadrada vira o destino.

### 03.16 Telhados da vila num tom só · Tier C
- **Errado:** vistos de cima e de longe, as 7 coberturas são da mesma ardósia, sem cumeeira de outra cor nem variação.
- **Onde:** `P/03_Vila_Media.jpg`, `P/14_Alto_34.jpg`.
- **Código:** `sg_village.py: slate_course()`, `roof_z()`; `sg_lib.py: SMATS["Roof_SG_Slate"]`.
- **Direção:** 2 variantes de ardósia por grupo de casas (dirigido) e cumeeira em telha escura.

---

## 04 Interiores das casas

### 04.01 [CRÍTICO] H2, H3, H5 e H7 com o interior IDÊNTICO · Tier B
- **Errado:** as 4 casas tipo A têm a mesma sala (mesa de 8 × 4, banco, cadeira junto ao fogo, estante), a mesma
  escada e o mesmo quarto (cama, guarda-roupa e tapete azul na mesma posição). Só a bancada do ofício muda, e ela
  quase não aparece. Quem entra em 2 casas percebe na hora.
- **Onde:** `P/04_H2_Sala.jpg`, `P/04_H3_Sala.jpg`, `P/04_H5_Sala.jpg`, `P/04_H7_Sala.jpg`; `P/04_H2_Quarto.jpg` =
  `P/04_H3_Quarto.jpg` = `P/04_H5_Quarto.jpg` = `P/04_H7_Quarto.jpg`.
- **Código:** `sg_village_int.py: furnish_a()`.
- **Direção:** um `furnish_*` por ofício, com o térreo virado para o trabalho:
  - ferreiro (H2): forja de mão, bigorna, ferramentas na parede, barril de têmpera;
  - boticário (H3): balcão com frascos, ervas penduradas nas vigas, prateleiras altas;
  - cartógrafo (H5): mesa de mapas, rolos em escaninhos, globo, compasso gigante;
  - mestre de armas (H7): armeiro, manequim de treino, escudos na parede.

  No andar de cima, varia a posição da cama e da mesa e o tipo de móvel.

### 04.02 [CRÍTICO] Paredes internas: reboco liso enorme · Tier B
- **Errado:** do térreo ao quarto, as paredes são panos lisos de reboco de 30 × 12, só com a faixa do rodapé e os
  postigos. Nada pendurado, nenhuma estrutura aparente. No Roblox é cinza-azulado chapado.
- **Onde:** `P/04_H2_Quarto.jpg`, `P/04_H6_Oficina.jpg`, `P/04_H1_Mezanino.jpg`, `R/04_H5_Quarto.jpg`.
- **Código:** `sg_village_int.py: linings()`.
- **Direção:**
  - Enxaimel aparente por dentro (montantes, frechal e mão-francesa), alinhado com o de fora.
  - Lambril de madeira até 3.
  - Por parede: 2 ou 3 objetos de leitura rápida (prateleira com louça, tapeçaria, ganchos com capas, quadro de
    mapa).

### 04.03 [CRÍTICO] Taverna (H1) sub-mobiliada · Tier B
- **Errado:** salão de 36 × 26 com balcão-caixa liso, mesas em tambor e banquinhos. O mezanino é um piso vazio com 2
  bancos. Não lê como taverna cheia.
- **Onde:** `P/04_H1_Taverna.jpg`, `R/04_H1_Taverna.jpg`, `P/04_H1_Mezanino.jpg`, `P/04_H1_Quarto.jpg`.
- **Código:** `sg_village_int.py: furnish_b()`.
- **Direção:**
  - Balcão com tampo saliente, painel frontal almofadado e prateleira de garrafas e barris atrás.
  - 5 ou 6 mesas com cadeiras e canecas.
  - Caldeirão na lareira e placa de cardápio.
  - Mezanino com mesas e uma galeria de quartos com cortina.

### 04.04 Fogo das lareiras em cones · Tier B
- **Errado:** a chama são 3 ou 4 cones laranja Neon sobre a grelha. Primitiva luminosa na altura do olho, em 7
  lareiras.
- **Onde:** `P/04_H2_Sala.jpg`, `R/04_H5_Sala.jpg`, `P/04_H4_Sala.jpg`.
- **Código:** `sg_village_int.py: fireplace()`.
- **Direção:** toras de lenha cruzadas, brasa escura com Neon só na base (faixa recuada) e chama em 2 lâminas finas
  curvas, sem cone.

### 04.05 Interior monocromático no Roblox · Tier B
- **Errado:** piso, vigas, escada, móveis e portas usam a mesma madeira (`Wood_SG_Dark`). No Roblox, tudo vira um
  marrom só e a sala perde a leitura.
- **Onde:** `R/04_H1_Escada.jpg`, `R/04_H5_Sala.jpg`, `R/04_H6_Oficina.jpg`.
- **Código:** `sg_village_int.py` (`WOOD` único).
- **Direção:** 3 valores: estrutura (vigas, escada) escura, móveis médios, piso um valor abaixo dos móveis.
  Estofados e tecidos em navy e vinho.

### 04.06 Peito da chaminé atravessando o forro · Tier B
- **Errado:** nas casas térreas (H4, H6), a chaminé de pedra entra na tesoura e no pano do telhado em diagonal, sem
  capa nem rufo. Lê como caixa cravada.
- **Onde:** `P/04_H4_Forro.jpg`, `P/04_H6_Forro.jpg`, `R/04_H6_Forro.jpg`.
- **Código:** `sg_village_int.py: fireplace()` (peito superior), `roof_inside()`; `sg_village.py: chimney()`.
- **Direção:** o peito sobe reto e atravessa o forro numa caixa de madeira com rufo, e a tesoura desvia (chincha).

### 04.07 Quarto do andar quase vazio · Tier B
- **Errado:** 30 × 22 com uma cama, um baú e um tapete no canto. O resto é piso.
- **Onde:** `P/04_H2_Quarto.jpg`, `R/04_H5_Quarto.jpg`.
- **Código:** `sg_village_int.py: furnish_a()`.
- **Direção:** dividir com tabique de enxaimel em 2 cômodos (quarto e escritório ou depósito) ou mobiliar o espaço
  (2 camas, mesa, lavatório, cabideiro).

### 04.08 Postigos navy fechados em todas as janelas · Tier B
- **Errado:** por dentro, toda janela é um painel navy liso. A casa parece fechada e sem relação com a luz de fora.
- **Onde:** `P/04_H2_Quarto.jpg`, `P/04_H6_Oficina.jpg`.
- **Código:** `sg_village_int.py: linings()`.
- **Direção:** metade com postigo aberto (folhas encostadas no vão) e vidraça com caixilho.

### 04.09 Forro aberto das casas térreas · Tier B
- **Errado:** tesouras finas sob um pano de ardósia escuro. Lê como sótão vazio.
- **Onde:** `P/04_H4_Forro.jpg`, `P/04_H6_Forro.jpg`.
- **Código:** `sg_village_int.py: roof_inside()`, `ceiling()`.
- **Direção:** tesouras com 2 vezes a seção, ripado aparente sob a ardósia, objetos pendurados (ervas, lanterna,
  rede).

### 04.10 Tapetes e coberta em plano liso azul · Tier B
- **Errado:** retângulos navy chapados, sem borda nem franja.
- **Onde:** `P/04_H2_Quarto.jpg`, `R/04_H5_Quarto.jpg`.
- **Código:** `sg_village_int.py: rug()`, `bed()`.
- **Direção:** borda em tom escuro de 0,4, franja nas pontas e uma faixa de desenho.

### 04.11 Velas e candelabros em cones · Tier B
- **Errado:** os lustres da taverna e as velas dos quartos usam chama em cone Neon. É a AUDITORIA 2 12.09, que
  continua.
- **Onde:** `P/04_H1_Quarto.jpg`, `R/04_H1_Mezanino.jpg`.
- **Código:** `sg_village_int.py: candle()`, `lantern()`.
- **Direção:** a vela do kit (gota pequena com pavio), com no máximo 0,4 de altura de chama.

---

## 05 Pátio-jardim e muralha

### 05.01 [CRÍTICO] Caminho nobre do pátio: faixa preta com fio Neon · Tier B
- **Errado:** o eixo portão → porta (20 de largura) é um leito de obsidiana com lajes de mármore negro brilhante e um
  fio Neon violeta no centro. No jogo é asfalto molhado com faixa de pista. É o caminho mais importante da ilha e lê
  como estrada.
- **Onde:** `J/04_patio.jpg`, `P/05_Patio_Caminho.jpg`, `R/05_Patio_Caminho.jpg`, `P/05_Patio_Volta.jpg`,
  `P/05_Portao_Vao.jpg`.
- **Código:** `sg_court.py: noble_path()` (`OBS`, `MARB`, `thread_m`).
- **Direção:**
  - Lajes de pedra média (`Stone_Paving_SG` mais clara), 4 por fiada, com faixa de borda em cantaria escura.
  - Tirar o fio Neon. Se o eixo precisar de marca, usar um embutido de pedra violeta FOSCA a cada 8 fiadas.
  - Mármore só em 2 tapetes de pedra na frente da porta e do portão.

### 05.02 [CRÍTICO] Espelhos d'água que leem como piscina · Tier B
- **Errado:** retângulos de água azul saturado (`Water_SG` 64, 96, 196), com borda fina, encostados na fachada.
  Visíveis até de longe (`P/06_Castelo_Alto`). Quebram a paleta fria e dessaturada.
- **Onde:** `P/05_Patio_E.jpg`, `R/05_Patio_E.jpg`, `P/06_Fachada_Base.jpg`, `P/06_Castelo_Alto.jpg`.
- **Código:** `sg_court.py: pool()`; `sg_lib.py: SMATS["Water_SG"]`; água no Roblox via os marcadores do
  `sg_water.court_water()`.
- **Direção:**
  - Lâmina navy escura com reflexo (o espelho reflete a lua, não é azul).
  - Bordo de cantaria largo (1,2) com pingadeira.
  - Bica de pedra na cabeceira e 3 ou 4 grupos de lírios.

### 05.03 Topiárias em cone liso e sebes-caixa · Tier B
- **Errado:** topiária é um cone de 8 lados verde-escuro. Sebe é caixa de cantos arredondados. Primitivas óbvias no
  primeiro plano do pátio e dos becos.
- **Onde:** `P/05_Patio_E.jpg`, `P/05_Patio_W.jpg`, `P/13_Beco_W1.jpg`, `R/05_Patio_E.jpg`.
- **Código:** `sg_garden.py: topiary()`, `hedge_round()`; `sg_court.py: tall_hedge()`, `cone()`.
- **Direção:** topiária em níveis (bola sobre cone, espiral), com vaso de pedra. Sebe com topo ondulado em massas,
  base com plantio de borda e quebras para os bancos.

### 05.04 Árvores-marco do pátio · Tier B
- **Errado:** são pinheiros low-poly de cones empilhados, como os da borda. A "árvore com banco" não se distingue.
- **Onde:** `P/05_Patio_E.jpg`, `P/05_Patio_W.jpg`.
- **Código:** `sg_court.py: tree_bench()`; `sg_veg.py: pine()`.
- **Direção:** uma espécie própria de árvore-marco (copa larga em 3 massas, tronco torto, raízes à vista) e banco
  circular de pedra.

### 05.05 [CRÍTICO] Face interna da muralha: pano liso de 24 · Tier B
- **Errado:** do pátio, a muralha é um pano de fiadas grandes de 24 de altura, sem arcada, escada de adarve,
  contraforte, cordão ou seteira. Com trepadeiras-bolota no pé.
- **Onde:** `P/05_Muralha_Dentro.jpg`, `R/05_Muralha_Dentro.jpg`, `P/05_Patio_Volta.jpg`.
- **Código:** `sg_castle.py: muralha()`.
- **Direção:**
  - Arcadas de descarga (arcos cegos de 8 a 10 com pilastras) em toda a face interna.
  - Escada de adarve em 2 pontos (pode ser só visual, com guarda no topo).
  - Cordão a 6 e seteiras no registro alto.

### 05.06 Passagem leste: corredor escuro entre paredões · Tier B
- **Errado:** a escada EastP3 sobe num vão de 18 entre 2 paredes cegas, sem arco nem luz. Sem remate no topo.
- **Onde:** `P/05_Passagem_Leste.jpg`, `R/05_Passagem_Leste.jpg`.
- **Código:** `sg_castle.py: muralha()`, `wall_tower()` (vão `L.EAST_WALL_GAP`).
- **Direção:** arco de passagem com aduelas sobre o vão, lanterna de braço no nó e jambas com cunhais.

### 05.07 Portão da muralha: aduelas alternadas em violeta · Tier B
- **Errado:** a arquivolta do portão alterna aduelas de pedra escura e violeta. No Roblox vira um tracejado
  roxo/preto.
- **Onde:** `R/05_Muralha_P2.jpg`, `R/05_Patio_Alto.jpg`, `R/03_EixoP2.jpg`.
- **Código:** `sg_castle.py: muralha()` (arco do portão).
- **Direção:** aduelas num tom só de pedra. Violeta só no fecho ou numa faixa de tecido.

### 05.08 Cones das torres do portão com filetes claros nas arestas · Tier B
- **Errado:** os telhados cônicos das torres do portão e das torrinhas da fachada têm filetes claros nas arestas.
  Leem como linhas de neon branco.
- **Onde:** `R/05_Patio_Alto.jpg`, `R/03_EixoP2.jpg`, `R/06_Castelo_Vila.jpg`.
- **Código:** `sg_castle.py: tower_crown()`, `fac_turret()`, `spire()`.
- **Direção:** rufos e espigões em ferro escuro (`Metal_SG_BlackIron`), não em `Stone_SG_Trim`.

### 05.09 Gramados rebaixados todos ortogonais · Tier B
- **Errado:** retângulos de grama com murete, todos alinhados e do mesmo tamanho. O "jardim natural" pedido lê como
  maquete.
- **Onde:** `P/05_Patio_E.jpg`, `P/05_Patio_Alto.jpg`, `P/05_Patio_W.jpg`.
- **Código:** `sg_court.py: lawn_rects()`, `lawn_wall()`, `floor_layers()`.
- **Direção:** manter a planta (travada), mas quebrar o retângulo com canteiros em massa nos cantos, bancos recuados
  em nicho, arbustos que transbordam o murete e caminhos de pisantes atravessando.

### 05.10 Pátio largo com zonas mortas · Tier B
- **Errado:** entre o caminho nobre, os gramados e os espelhos, sobram faixas de cascalho e grama sem nada,
  principalmente nas pontas leste e oeste (x ±70 a ±100).
- **Onde:** `P/05_Patio_Alto.jpg`, `P/05_Patio_W.jpg`.
- **Código:** `sg_court.py: court()`, `plants_half()`.
- **Direção:** um caramanchão ou pérgula em cada ponta, com banco, e floreiras altas encostadas à muralha.

---

## 06 Castelo (exterior)

### 06.01 [CRÍTICO] Faixa do jogador (0 a 20) da fachada e dos flancos: paredes lisas enormes · Tier A/B
- **Errado:** do pátio, a fachada de 280 e os flancos de 200 leem como paredes lisas: só fiadas grandes e um
  embasamento fino. Nada ao alcance do jogador: nenhuma arcada cega, nicho, porta secundária, banco de pedra ou
  contraforte com degraus. O hero está menos acabado que as casas (é o 16.05 da AUDITORIA 2, que voltou na escala
  2×).
- **Onde:** `J/04_patio.jpg`, `P/06_Fachada_Base.jpg`, `R/06_Fachada_Base.jpg`, `P/06_Torre_Pe.jpg`,
  `P/06_Flanco_E.jpg`.
- **Código:** `sg_castle.py: wall_skin()`, `socle()`, `coursed()`, `buttress()`, `front_towers()`, `tower_skin()`.
- **Direção:**
  - Embasamento de 3 em talude, com cordão e plinto.
  - Arcada cega de 8 a 10 de altura em todos os panos entre contrafortes, de 0 a 20.
  - Contrafortes com 2 degraus e pingadeira.
  - Janelas baixas gradeadas e 2 portas de serviço por flanco.
  - Bancos de pedra nos nichos e colunelos de canto nas torres até 20.

### 06.02 [CRÍTICO] Folhas da porta principal planas · Tier A
- **Errado:** cada folha de 14 × 34 é uma alma lisa com 5 tábuas largas, 4 ferragens em T e uma argola. No jogo é um
  plano marrom escuro do tamanho de um prédio.
- **Onde:** `J/04_patio.jpg`, `P/06_Guardas.jpg`, `P/06_Porta_Folha.jpg`, `R/06_Fachada_Patio.jpg`.
- **Código:** `sg_castle.py: door_leaf()`.
- **Direção:**
  - Almofadas em quadro (2 × 5) com moldura saliente de 0,3.
  - Faixas de ferro horizontais com tachões em grade.
  - Postigo (porta de homem, 4 × 8) com aldraba na folha esquerda.
  - Dobradiças de cinta longas e soleira de pedra.

### 06.03 [CRÍTICO] Estátuas dos guardas baixas para a porta · Tier A
- **Errado:** cada guardião tem ~6 de altura sobre um pedestal de 3,8, ao lado de um vão de 28 × 34 com tímpano até
  46. Parece um boneco de jardim.
- **Onde:** `J/04_patio.jpg`, `P/05_Patio_Caminho.jpg`, `P/06_Fachada_Patio.jpg`, `R/05_Patio_Caminho.jpg`.
- **Código:** `sg_court.py: statue()` → `hooded_figure()`.
- **Direção:** escala 1,8 a 2× (figura de ~11 em pedestal de 5, a mesma proporção para o vão). Ou tirar do chão e
  pôr nos nichos das torres da fachada, como guardiões monumentais de 18 a 20.

### 06.04 Teto do nártex: grade de vigas claras · Tier B
- **Errado:** o teto da passagem da porta é uma grade de vigas brancas sobre painéis escuros. No jogo lê como
  andaime.
- **Onde:** `J/04_patio.jpg`, `P/06_Porta.jpg`, `R/06_Fachada_Patio.jpg`.
- **Código:** `sg_castle.py: porch()`.
- **Direção:** abóbada de berço em pedra com 3 arcos-diafragma, ou caixotões profundos no tom da parede.

### 06.05 Arquivoltas com fios Neon · Tier A
- **Errado:** colunelos finos das 4 ordens com filetes Neon violeta verticais. No jogo, 4 riscos violeta fortes
  emolduram a porta (é a "magia do castelo" acima do pedido).
- **Onde:** `J/04_patio.jpg`, `P/05_Patio_Eixo.jpg`, `R/06_Fachada_Patio.jpg`.
- **Código:** `sg_castle.py: porch()`, `central_body()`.
- **Direção:** tirar o Neon das arquivoltas. Colunelos 2× mais grossos, com capitel e base; tímpano com relevo de
  pedra.

### 06.06 Piso xadrez preto e branco na entrada do salão · Tier B
- **Errado:** o piso do nártex e da primeira faixa do salão é um xadrez de alto contraste. Lê como tabuleiro.
- **Onde:** `J/04_patio.jpg`, `P/06_Guardas.jpg`.
- **Código:** `sg_castle.py: paving()`; `sg_hall.py: floor()`.
- **Direção:** 2 tons próximos de pedra (Floor e MarbleBlack), padrão em losango ou em faixa.

### 06.07 Flancos com contrafortes e janelas em passo fixo · Tier B
- **Errado:** cada flanco da nave tem 8 tramos idênticos (contraforte, janela 10 × 34, contraforte). De longe, 16
  janelas iguais acesas em 2 filas.
- **Onde:** `P/06_Flanco_E.jpg`, `P/13_Saida_Volta.jpg`, `P/14_Oeste.jpg`, `R/14_Leste.jpg`.
- **Código:** `sg_castle.py: nave()`, `buttress()`, `nave_window()`.
- **Direção:** ritmo A-B-A (tramo com janela, tramo com arcada cega e rosácea pequena), arcobotantes só nos tramos
  pares e pináculos de 2 alturas.

### 06.08 Pinheiros cravados no pé do castelo · Tier B
- **Errado:** no terraço norte e no beco oeste, há pinheiros a menos de 2 studs da parede, com a copa atravessando a
  cantaria.
- **Onde:** `P/06_Coroa_Norte.jpg`, `R/06_Coroa_Norte.jpg`, `P/06_Flanco_W.jpg`.
- **Código:** `sg_veg.py: site_ok()`, `castle_hit()` (folga pequena).
- **Direção:** afastamento ≥ raio da copa + 3 de qualquer parede.

### 06.09 Colunas de rocha soltas junto das rotas · Tier C/B
- **Errado:** as `CLIFF_SPIRES` (colunas de rocha de 60 a 110) ficam a poucos studs dos becos, do mirante e da
  alquimia. De perto leem como chaminé ou ruína sem função. Uma delas está inclinada.
- **Onde:** `P/06_Flanco_E.jpg`, `P/13_Beco_W2.jpg`, `P/13_Mirante.jpg`, `P/11_Rua.jpg`, `P/13_Saida_Volta.jpg`.
- **Código:** `sg_terrain.py: spires()`, `column()`; `sg_layout.py: CLIFF_SPIRES`.
- **Direção:** fundir na falésia (a coluna nasce do penhasco e o topo fica abaixo do patamar), ou baixar para a
  silhueta só de longe. Nenhuma a menos de 25 de uma rota.

### 06.10 Torres da fachada: fuste liso até 140 · Tier B/C
- **Errado:** fuste com fiadas e frestas pequenas, sem cordão, contraforte de canto ou janela até muito alto.
- **Onde:** `P/06_Torre_Pe.jpg`, `R/06_Castelo_Vila.jpg`.
- **Código:** `sg_castle.py: front_towers()`, `tower_skin()`, `shaft_band()`.
- **Direção:** cordões a cada 1/4, contrafortes de canto em degraus e janelas geminadas em 2 registros.

### 06.11 Rosácea: disco Neon com crescente · Tier A
- **Errado:** a rosácea da fachada é um disco violeta luminoso com o crescente no meio. No jogo lê como relógio.
- **Onde:** `J/01_ponte_chegada.jpg`, `R/03_EixoP2.jpg`, `P/03_EscP1P2_Pe.jpg`.
- **Código:** `sg_castle.py: rose()`.
- **Direção:** rendilhado de pedra 2× mais grosso, vidro escuro (Glass) e brilho só no óculo central. Sem crescente
  (16.06).

### 06.12 Muralha vista do P2 · Tier B
- **Errado:** pano liso de 24 com ameias pequenas, igual dos 2 lados do portão por ~150 studs.
- **Onde:** `J/03_vila_rua_P2.jpg`, `P/05_Muralha_P2.jpg`, `R/03_EixoP2.jpg`.
- **Código:** `sg_castle.py: muralha()`, `machicolations()`.
- **Direção:** machicolagem nos 40 studs de cada lado do portão, seteiras em ritmo, cordão a 8 e contrafortes em
  talude no pé.

### 06.13 Vão do portão no jogo: retângulo violeta chapado · Tier B (a confirmar)
- **Errado:** do eixo do P2, o vão do portão aparece cheio de um violeta uniforme (o pátio e a porta somem). Hipótese:
  fachada de fundo + tímpano e arquivoltas violeta + fog da área. Na prévia, o mesmo ângulo mostra o pátio
  (`P/05_Portao_Fora`).
- **Onde:** `J/03_vila_rua_P2.jpg`.
- **Código:** `sg_castle.py: porch()` (emissivos), AreaAtmosphere (fog).
- **Direção:** conferir no Play. Se for o tímpano/arquivoltas, cai junto com 06.05.

---

## 07 Salão (interior)

### 07.01 [CRÍTICO] Abóbada de "arame" · Tier A
- **Errado:** os panos da abóbada são planos navy lisos, e as nervuras são filetes finos e claros. No jogo leem como
  estrutura de arame ou de estufa. O teto de 84 é a maior superfície do hero.
- **Onde:** `J/06_salao.jpg`, `P/07_Teto.jpg`, `R/07_Nave_Porta.jpg`, `R/07_Nave_Volta.jpg`.
- **Código:** `sg_hall.py: vault()`, `ribs()`, `_vault_ys()`.
- **Direção:**
  - Nervuras 3× mais largas (≥ 1,2), com perfil (toro, filete, cavete), no tom da pedra (não prata).
  - Chaves esculpidas nos cruzamentos.
  - Panos em pedra média, um valor acima do navy, com fiadas largas.
  - Arcos-diafragma marcando cada tramo.

### 07.02 [CRÍTICO] Parede do fundo e contra-fachada: panos lisos gigantes · Tier A
- **Errado:** acima do arco triunfal sobra um pano liso de ~120 × 50 com uma rosácea pequena. Por dentro da fachada,
  outro pano liso enorme com a porta pequena no meio.
- **Onde:** `P/07_Nave_Meio.jpg`, `R/07_Nave_Meio.jpg`, `P/07_Nave_Volta.jpg`, `R/07_Nave_Volta.jpg`.
- **Código:** `sg_hall.py: end_walls()`, `triumph()`, `rose()`.
- **Direção:**
  - Fundo: arcada cega em 2 registros dos lados do arco, rosácea com R real de 14 (hoje lê menor) e 2 estátuas
    altas.
  - Contra-fachada: rosácea interna sobre a porta, tribuna ou galeria do órgão e tapeçarias.

### 07.03 Arco triunfal pequeno e seco · Tier A
- **Errado:** 40 × 60 com moldura fina. Lê como porta de capela no pano enorme.
- **Onde:** `P/07_Nave_Meio.jpg`, `P/07_Nave_Porta.jpg`.
- **Código:** `sg_hall.py: triumph()`.
- **Direção:** arquivoltas em 3 ordens com colunelos e capitéis, e um friso de arcaturas sobre o arco.

### 07.04 Tapete violeta sem bordadura · Tier B
- **Errado:** faixa violeta lisa da porta ao presbitério. Termina seca, sem franja.
- **Onde:** `J/06_salao.jpg`, `P/07_Piso.jpg`, `R/07_Nave_Meio.jpg`.
- **Código:** `sg_hall.py: floor()` (tapete).
- **Direção:** borda escura de 0,6 com debrum bronze, franja nas pontas e um desenho a cada 12.

### 07.05 Medalhão do crescente no piso · Tier B
- **Errado:** mais um crescente (o emblema já está na rosácea, no trono, nos estandartes e na porta).
- **Onde:** `P/07_Piso.jpg`.
- **Código:** `sg_hall.py: floor()`.
- **Direção:** tirar (16.06). No lugar, um ladrilho em estrela de pedra.

### 07.06 Bases dos pilares em caixa · Tier B
- **Errado:** fuste composto bom, mas a base é um bloco liso.
- **Onde:** `P/07_Pilar_CU.jpg`, `R/07_Pilar_CU.jpg`.
- **Código:** `sg_hall.py: shaft_base()`, `arcade_pier()`.
- **Direção:** plinto, toro, escócia e toro (base ática), com chanfro.

### 07.07 Naves laterais escuras e repetitivas · Tier B
- **Errado:** 8 nichos iguais por lado, cada um com uma vela. A nave lateral é um corredor escuro de 200.
- **Onde:** `P/07_Lateral_W.jpg`, `R/07_Lateral_W.jpg`, `P/07_Lateral_E_Parede.jpg`, `J/06_salao.jpg`.
- **Código:** `sg_hall.py: niche()`, `aisle_walls()`, `bay_wall()`.
- **Direção:** variação dirigida por tramo: capela com altar e luz, túmulo com jacente, armadura, estante. Luz em 1 de
  cada 2 tramos.

### 07.08 Vitrais em azul liso · Tier B
- **Errado:** as 16 janelas altas são vidro azul-claro chapado com o mesmo mainel.
- **Onde:** `P/07_Nave_Porta.jpg`, `R/07_Lateral_E_Parede.jpg`.
- **Código:** `sg_hall.py: windows()`, `lancet()`.
- **Direção:** 2 desenhos de rendilhado alternados e vidro em 2 cores (azul-noite e violeta), com caixilho de chumbo
  visível.

### 07.09 Lustres pequenos para a nave · Tier B
- **Errado:** 4 rodas de velas de ~6 de diâmetro num salão de 184 × 196 × 84.
- **Onde:** `P/07_Nave_Volta.jpg`, `J/06_salao.jpg`.
- **Código:** `sg_hall.py: chandelier()`.
- **Direção:** escala 1,6× com coroa em 2 níveis, ou 8 lustres (1 por tramo, alternando tamanho).

### 07.10 Piso de lajes enormes · Tier B
- **Errado:** módulos grandes de mármore escuro com reflexo, sem desenho de faixa.
- **Onde:** `P/07_Piso.jpg`, `R/07_Lateral_W.jpg`.
- **Código:** `sg_hall.py: floor()`, `lay_field()`.
- **Direção:** faixas de pedra clara marcando os eixos dos pilares (o tramo desenha o piso) e lajes menores entre
  elas.

---

## 08 Trono e escada caracol

### 08.01 Trono: espaldar liso com crescente gigante · Tier A
- **Errado:** o espaldar é um painel escuro liso, com um crescente pálido enorme em cima. O crescente domina o trono.
- **Onde:** `P/08_Trono_Fechado.jpg`, `P/08_Trono_34.jpg`, `R/08_Trono_Fechado.jpg`.
- **Código:** `sg_hall.py: throne()`.
- **Direção:** baldaquino ou dossel de tecido sobre o trono, painel do espaldar com moldura e almofadas, crescente em
  metal escuro com metade do tamanho.

### 08.02 Presbitério estreito e alto com panos lisos · Tier A
- **Errado:** 40 de largura e ~60 de altura, com paredes de fiadas e 2 estandartes. A abóbada tem as mesmas nervuras
  finas da nave.
- **Onde:** `P/07_Presbiterio.jpg`, `P/08_Trono_34.jpg`.
- **Código:** `sg_hall.py: chancel()`, `retable()`.
- **Direção:** cadeirais de madeira nas laterais, arcada cega e cortinas atrás do trono, com o arco secreto
  escondido nela.

### 08.03 Arco secreto com aduelas claras alternadas · Tier A
- **Errado:** o arco de 12 × 18 tem aduelas claras e escuras alternadas, e lê como tracejado branco.
- **Onde:** `P/08_Trono_Open.jpg`, `P/08_Arco_Open.jpg`.
- **Código:** `sg_hall.py: retable()`.
- **Direção:** aduelas num valor só com fecho saliente e soleira de pedra.

### 08.04 [CRÍTICO] Escada caracol: 60 degraus escuros e iguais · Tier B
- **Errado:** degraus em cunha lisa (sem focinho nem espelho) e paredes do poço lisas. Só 4 ou 5 tochinhas e um
  corrimão de barra. A face de baixo da volta de cima é feita de cunhas chapadas. São 2 voltas inteiras da mesma
  imagem, no escuro.
- **Onde:** `P/08_Caracol_Meio.jpg`, `P/08_Caracol_Patamar.jpg`, `P/08_Caracol_Meio_Cima.jpg`,
  `R/08_Caracol_Meio.jpg`.
- **Código:** `sg_cave.py: spiral_stairs()`, `tower_piece()`, `tower_openings()`, `torch_cup()`.
- **Direção:**
  - Degrau com focinho e espelho recuado, em 2 tons.
  - Núcleo com anel a cada volta.
  - Paredes com fiadas e um nicho com vela a cada 90°.
  - 1 janela ou abertura por volta para o Salão Sombrio (prévia do que vem embaixo).
  - Corrimão em corda grossa com suportes de ferro.
  - Uma tocha forte em cada meia volta.

### 08.05 Bolso do trono cru · Tier B
- **Errado:** com o trono recolhido, o bolso é uma cavidade sem moldura nem acabamento. Aparece toda vez que a
  escada abre.
- **Onde:** `P/08_Bolso_Open.jpg`.
- **Código:** `sg_hall.py: retable()` / `chancel()` (`L.THRONE_POCKET`).
- **Direção:** moldura de pedra no bolso e cortina ou painel que o trono empurra.

### 08.06 Topo da caracol sem patamar desenhado · Tier B
- **Errado:** do arco secreto, o jogador cai direto nas cunhas. Não há soleira, porta de ferro aberta ou lanterna
  marcando o início da descida.
- **Onde:** `P/08_Caracol_Topo_Open.jpg`, `P/08_Arco_Open.jpg`.
- **Código:** `sg_cave.py: spiral_stairs()`; `sg_hall.py: retable()`.
- **Direção:** patamar de lajes com soleira, grade de ferro recolhida no arco e 2 tochas.

---

## 09 Salão Sombrio

### 09.01 [CRÍTICO] No jogo é quase preto · Tier A
- **Errado:** mal se leem a galeria, a rocha e o portal. As causas, medidas:
  - a rocha `Stone_SGCaveRock` é (34, 30, 48), ~13% de valor;
  - o volume de 180 × 248 × 58 tem só 6 luzes;
  - o export corta todas para Range ≤ 20 e Brightness ≤ 1,5 (15.01);
  - o ambiente noturno da área não muda no subsolo.

  A prévia do Blender esconde o problema (luz sem corte).
- **Onde:** `J/07_caverna_galeria.jpg`, `R/09_Galeria_Chegada.jpg`, `R/09_Abobada.jpg`.
- **Código:** `sg_cave.py` (material, linha 41) e `lights()`; `lobby_area/forja_mineradora/export_roblox.py:
  lights()` (corte); `roblox/CeuSombras.client.lua` (subsolo).
- **Direção:**
  - Rocha 2 valores acima (~(70, 62, 92)), com topo de estrato mais claro.
  - 15 a 20 luzes dirigidas, com Range 40 a 60 por override no `export_sg`: tochas da escadaria, braseiros nos
    pilares, luz de recorte atrás das arcadas, cristais com PointLight fraca, forja e mapa com SpotLight.
  - Ambiente de subsolo (~(40, 36, 60)) no `CeuSombras`, ao entrar em `CAVE_Zone`.

### 09.02 [CRÍTICO] Rocha e estrutura no mesmo valor · Tier A
- **Errado:** no Roblox, a rocha, a cantaria (`Stone_SGDunRuin` 80, 74, 102), os pilares e o piso são todos
  azul-violeta escuros. Sem separação de valor, a arquitetura some na rocha.
- **Onde:** `R/09_Escadaria_Topo.jpg`, `R/09_Forja_2.jpg`, `R/09_Galeria_Chegada.jpg`.
- **Código:** `sg_cave.py` (`RK`, `RUIN`, `FL`).
- **Direção:** 3 valores separados: rocha escura e fria, cantaria clara e quente (~(120, 110, 130)), ferro preto. O
  piso fica no meio.

### 09.03 [CRÍTICO] Abóbada de rocha em triângulos aleatórios · Tier B/C
- **Errado:** o teto é um campo de triângulos de tamanhos e ângulos sorteados. Lê como papel amassado, sem massas
  nem direção.
- **Onde:** `P/09_Abobada.jpg`, `R/09_Abobada.jpg`, `P/08_Torre_Poco.jpg`.
- **Código:** `sg_cave.py: ceiling()`, `ceil_zb()`.
- **Direção:** 4 ou 5 grandes massas de rocha em estratos inclinados, estalactites agrupadas sobre a ponte e o rio e
  2 fendas no teto com luz azul (luar filtrado).

### 09.04 [CRÍTICO] Paredes em blocos e "órgão" de cilindros soltos · Tier B
- **Errado:**
  - As paredes são blocos cúbicos empilhados.
  - O órgão de basalto são prismas hexagonais de alturas sorteadas: pilha de latas ou tubos de papelão.
  - Na passarela, a rocha a 1 stud do jogador é um painel plano.
- **Onde:** `P/09_Rocha_CU.jpg`, `P/09_Forja.jpg`, `P/09_Passarela_W.jpg`, `R/09_Forja.jpg`.
- **Código:** `sg_cave.py: rock_walls()`, `wall_block()`, `basalt_organ()`, `_organ_m()`.
- **Direção:**
  - Colunas de basalto em feixes encostados (sem vão entre elas), com topos escalonados contínuos (escada natural).
  - Juntas de diáclase horizontais e tálus de blocos no pé.
  - Junto às passarelas, rocha com relevo de 1 a 2 (saliências), não plano.

### 09.05 Arcos-anel soltos atravessando o salão · Tier A
- **Errado:** arcos redondos de cantaria cruzam o salão sozinhos, sem parede nem abóbada que sustentem. Leem como
  aros de croquet. Os 5 do eixo são idênticos.
- **Onde:** `P/09_Visao_Geral.jpg`, `P/09_Galeria_Chegada.jpg`, `R/09_Galeria_Chegada.jpg`, `J/07`.
- **Código:** `sg_cave.py: nave()`.
- **Direção:** arcos-diafragma que nascem de pilares encostados à rocha e sustentam algo (passarela, viga de
  correntes, lustre). Perfil com aduelas e imposta. 3 arcos, não 5, com tamanhos decrescentes até o portal.

### 09.06 Galeria de chegada: lajes enormes e guarda-corpo de barras · Tier B
- **Errado:** piso de lajes muito grandes e lisas. O guarda-corpo é uma grade de barras finas pretas que somem no
  escuro.
- **Onde:** `P/09_Galeria_Lateral.jpg`, `J/07_caverna_galeria.jpg`, `R/09_Galeria_Chegada.jpg`.
- **Código:** `sg_cave.py: gallery()`, `iron_rail()`.
- **Direção:** lajes menores com faixa de borda de cantaria clara, e guarda-corpo com pilaretes de pedra e
  balaústres de ferro forjado com corrimão de madeira.

### 09.07 Escadaria grande: degraus em lajes · Tier B
- **Errado:** 2 lances de 12 degraus de 16 de largura em lajes contínuas.
- **Onde:** `P/09_Escadaria_Pe.jpg`, `P/09_Escadaria_Topo.jpg`.
- **Código:** `sg_cave.py: grand_stair()`.
- **Direção:** ver 16.03, mais 2 braseiros no patamar.

### 09.08 Forja: coifa-caixa e poucos props · Tier A
- **Errado:** a coifa é uma caixa com pirâmide lisa e boca brilhante. Uma bigorna, 2 barris e um rebolo numa sala de
  38 × 60.
- **Onde:** `P/09_Forja.jpg`, `R/09_Forja.jpg`, `P/09_Forja_2.jpg`.
- **Código:** `sg_cave.py: forge()`, `armor_stand()`, `sword()`.
- **Direção:** coifa com cintas de ferro e chaminé de chapa, fole de couro, tina de têmpera com água, rack de
  armas, carvoeira, bancada com moldes, armaduras em suportes e lâminas penduradas.

### 09.09 Sala do mapa com relevo raso · Tier A
- **Errado:** a mesa do mapa tem um relevo baixo, que não se lê de pé. A estante de rolos são bolotas.
- **Onde:** `P/09_Mapa.jpg`, `P/09_Mapa_2.jpg`.
- **Código:** `sg_cave.py: maproom()`, `map_relief()`.
- **Direção:** relevo com altura real (castelo de 1,5), lustre baixo sobre a mesa, armário de mapas e rolos em
  cilindros com ponta.

### 09.10 Rio do salão · Tier B
- **Errado:** no Blender o canal é uma vala escura com borda de cantaria lisa. A água é feita no Roblox (marcadores).
  A leitura depende do Play.
- **Onde:** `P/09_Rio.jpg`, `P/09_Ponte_De_Baixo.jpg`.
- **Código:** `sg_cave.py: floor()`; `sg_water.py: cave_water()`.
- **Direção:** conferir no Play. Borda do canal com pedras soltas e plantas, e queda d'água com luz.

### 09.11 Portal: disco Neon chapado · Tier A
- **Errado:** é o elemento certo para ser o mais forte, mas é um disco violeta saturado de 26 de diâmetro, plano,
  com espiral rosa. Sem profundidade.
- **Onde:** `P/09_Portal_CU.jpg`, `R/09_Galeria_Chegada.jpg`, `J/07_caverna_galeria.jpg`.
- **Código:** `sg_cave.py: portal()`, `vortex_arms()`.
- **Direção:** fundo escuro (`SG_CaveVoid_Glow` baixo) com os braços Neon finos, aro com 2 profundidades e névoa ou
  partículas no Roblox.

### 09.12 Moldura do portal · Tier A
- **Errado:** pilares quadrados lisos e um aro de aduelas grossas sobre um estrado simples.
- **Onde:** `P/09_Portal.jpg`.
- **Código:** `sg_cave.py: portal()`, `platform()`.
- **Direção:** pilares compostos com capitel, estatuária dos 2 lados e 2 escadas laterais no estrado.

### 09.13 Base secreta sem função legível · Tier B
- **Errado:** fora da forja e do mapa, o salão é piso, grade e estandarte. Falta "bat-caverna": armaria, treino,
  dormitório, depósito.
- **Onde:** `P/09_Escadaria_Topo.jpg`, `P/09_Visao_Geral.jpg`, `P/09_Volta.jpg`.
- **Código:** `sg_cave.py: build()` (falta um módulo de vestir).
- **Direção:** 3 zonas de função ao longo das naves (área de treino com bonecos e alvos, armaria em racks, mesa de
  conselho com cadeiras), sem tocar a rota.

### 09.14 Cristais pequenos e escuros · Tier B
- **Errado:** cristais `Crystal_SGCave` pequenos, poucos e quase pretos. Não ajudam a luz.
- **Onde:** `P/09_Forja.jpg`, `R/09_Forja.jpg`.
- **Código:** `sg_cave.py: crystals()`, `crystal_hex()`.
- **Direção:** 3 aglomerados grandes (paredes leste e oeste e teto), com casca escura e núcleo violeta médio, e uma
  PointLight fraca em cada.

---

## 10 Masmorra (salas R1, R2 e R3)

### 10.01 [CRÍTICO] Abóbada das salas: tenda ou estufa · Tier A
- **Errado:** abóbada de painéis lisos escuros com nervuras finas e claras em arco. Lê como estrutura de estufa ou
  tenda de circo nas 3 salas.
- **Onde:** `P/10_R1_Chegada.jpg`, `R/10_R2_Entrada.jpg`, `P/10_R3_Teto.jpg`.
- **Código:** `sg_dungeon.py: vault()`, `_vault_map()`, `vault_z()`.
- **Direção:** abóbada de pedra com fiadas, nervuras largas e perfiladas, arcos-diafragma a cada tramo e chaves.
  Panos um valor acima.

### 10.02 [CRÍTICO] R1, R2 e R3 quase iguais · Tier B
- **Errado:** mesma arcada cega em volta, mesma abóbada, mesmo lustre e mesmo piso. A "variação dirigida" (lancetas,
  escoras/grelhas, retábulo) é pequena demais para ler a 40 studs. A dungeon infinita repete a mesma imagem a cada 5
  salas.
- **Onde:** `P/10_R1_Chegada.jpg`, `P/10_R2_Entrada.jpg`, `P/10_R3_Entrada.jpg`.
- **Código:** `sg_dungeon.py: room_kit()`, `bays_between()`, `fill_bay()`, `room_walls()`.
- **Direção:** identidade forte por sala:
  - R1, cripta: sarcófagos nos nichos e colunata baixa.
  - R2, prisão: celas reais com 2 a 3 de recuo e correntes.
  - R3, templo: colunata dupla, retábulo alto e estátuas.
  - Uma cor de luz por sala (âmbar, frio, violeta).

### 10.03 Arcadas cegas com grades flutuando · Tier B
- **Errado:** a grade de ferro fica na frente de um recesso plano e escuro, sem cela atrás. As escoras de madeira são
  um pórtico solto.
- **Onde:** `P/10_R2_Parede.jpg`, `R/10_R2_Parede.jpg`.
- **Código:** `sg_dungeon.py: blind_arch()`, `grille()`, `shoring()`.
- **Direção:** recuo real (cela de 2 a 3 com chão e um prop) e grade encaixada no vão, com dobradiça.

### 10.04 Portal da próxima sala: disco dentro de caixa · Tier A
- **Errado:** aro redondo dentro de uma moldura retangular trabeada, num muro com abóbada ogival. São 3 geometrias
  que não conversam.
- **Onde:** `P/10_R2_Portal.jpg`, `P/10_R3_Portal.jpg`, `R/10_R2_Entrada.jpg`.
- **Código:** `sg_dungeon.py: next_portals()`, `portal_frame()`, `link_frame()`.
- **Direção:** moldura ogival com aduelas, que case com o disco e com o vão (o `fit_check` continua valendo).

### 10.05 Setas Neon nos medalhões e na saída · Tier A
- **Errado:** setas violeta (↑ e ↓) no medalhão sobre os portais e no aro da saída da R1. Leem como ícone de UI.
- **Onde:** `P/10_R2_Portal.jpg`, `P/10_R1_Saida.jpg`, `R/10_R1_Saida.jpg`.
- **Código:** `sg_dungeon.py: altar_medallion()`, `arrival_portal()`, `exit_arch()`.
- **Direção:** trocar pela runa do alfabeto único da ilha (`RUNE_SEGS`) ou tirar. A função "saída" já vem do prompt.

### 10.06 Runa gigante Neon no retábulo da R3 · Tier A
- **Errado:** runa violeta de ~4 de altura, chapada em Neon, e outra no altar.
- **Onde:** `P/10_R3_Retabulo.jpg`.
- **Código:** `sg_dungeon.py: retable_bay()`, `altar_retable()`.
- **Direção:** runa entalhada na pedra, com brilho só no sulco (filete), e altar com frontal moldurado.

### 10.07 Lustres pequenos para salas de 104 · Tier B
- **Errado:** uma roda de velas de ~8 numa sala de 104 × 104 × 44.
- **Onde:** `P/10_R1_Chegada.jpg`, `P/10_R3_Entrada.jpg`.
- **Código:** `sg_dungeon.py: chandelier()`.
- **Direção:** 2 ou 4 lustres por sala ou um lustre-coroa de 16, e tochas maiores nos pilares.

### 10.08 Piso de lajes iguais com faixa central · Tier B
- **Errado:** lajes grandes e uniformes com uma faixa escura central e reflexos brilhantes. Sem desenho, desgaste ou
  ralo.
- **Onde:** `P/10_R2_Diagonal.jpg`, `R/10_R1_Fundo.jpg`.
- **Código:** `sg_dungeon.py: tile_floor()`, `_floor_arc()`.
- **Direção:** lajes menores em padrão com bordadura, um círculo rúnico central entalhado e pedra fosca (sem
  reflexo).

### 10.09 Cabeceiras: empena enorme lisa · Tier B
- **Errado:** acima da arcada, a parede de cabeceira é um pano liso com 2 lancetas pequenas.
- **Onde:** `P/10_R1_Fundo.jpg`, `P/10_R2_Portal.jpg`.
- **Código:** `sg_dungeon.py: room_faces()`, `lunette_lancets()`.
- **Direção:** tribuna com arcada, estátuas nos nichos e rosácea escura.

### 10.10 Saída da R1: aro encostado na parede · Tier B
- **Errado:** anel de pedra com espiral escura colado na parede, sem nicho nem soleira.
- **Onde:** `P/10_R1_Saida.jpg`, `R/10_R1_Saida.jpg`.
- **Código:** `sg_dungeon.py: exit_arch()`.
- **Direção:** nicho recuado de 2 com soleira e 2 tochas.

### 10.11 Luz das salas no jogo · Tier B
- **Errado:** os lustres de 11k a 21k da prévia viram Range 20 no export. Em salas de 104, o centro e as paredes
  ficam fora do alcance.
- **Onde:** comparar `P/10_R2_Diagonal.jpg` com `renders/ingame_v4/03_sala_masmorra.jpg`.
- **Código:** `export_roblox.lights()` (via `export_sg`); `sg_dungeon.py: room_lights()`.
- **Direção:** ver 15.01, mais tochas com PointLight nos pilares.

---

## 11 Alquimia

### 11.01 Janelas em amarelo inteiro · Tier B
- **Errado:** as lancetas da alquimia (por dentro e por fora) são painéis `Window_Warm` amarelos inteiros, as maiores
  manchas claras do P2. A alquimia lê como casa iluminada, não como laboratório mágico.
- **Onde:** `P/11_Fundo.jpg`, `P/11_Leste.jpg`, `R/11_In_Caldeirao.jpg`, `R/11_In_Cima.jpg`.
- **Código:** `sg_craft.py: window_out()`, `windows_in()`.
- **Direção:** vidro escuro com caixilho de chumbo, quente só na faixa baixa e 1 lanceta em violeta médio por lado.

### 11.02 Caldeirão com "escotilha" · Tier A
- **Errado:** o medalhão do crescente no bojo, com aro de bronze e moldura prata, lê como janela de máquina de
  lavar.
- **Onde:** `P/11_In_Porta.jpg`, `R/11_In_Porta.jpg`, `P/11_In_Caldeirao.jpg`.
- **Código:** `sg_craft.py: cauldron()`, `medal_bezel()`.
- **Direção:** tirar o medalhão. Se ficar algo, uma placa de relevo pequena, mais cintas de ferro com rebites.

### 11.03 Disco violeta liso na parede · Tier A
- **Errado:** um disco violeta chapado na parede atrás do caldeirão, sem moldura. Lê como adesivo ou balão.
- **Onde:** `P/11_In_Porta.jpg`, `R/11_In_Porta.jpg`.
- **Código:** `sg_craft.py: walls_in()` / `windows_in()` (óculo).
- **Direção:** óculo com rendilhado e caixilho, ou tirar.

### 11.04 Círculo mágico do piso forte demais · Tier A
- **Errado:** o círculo do piso é um Neon violeta largo, que domina o interior e compete com o caldeirão.
- **Onde:** `P/11_In_Caldeirao.jpg`, `R/11_In_Prateleiras.jpg`.
- **Código:** `sg_craft.py: magic_circle()`, `floor_glyph()`.
- **Direção:** filete fino entalhado (0,15), Neon só nas runas, metade da intensidade (hierarquia: alquimia abaixo da
  dungeon).

### 11.05 Remates em pirâmide dourada · Tier B
- **Errado:** postes internos com remate em pirâmide amarela. Volta do 12.12 da AUDITORIA 2.
- **Onde:** `P/11_In_Prateleiras.jpg`, `R/11_In_Caldeirao.jpg`.
- **Código:** `sg_craft.py: circle_lanterns()`.
- **Direção:** remate do kit (`sg_emblem.lantern_head`) ou nada.

### 11.06 Alquimia plantada na grama, sem adro · Tier B
- **Errado:** o prédio sai direto do gramado. A rua chega como faixa reta e não há adro, degrau de chegada, canteiro
  ou banco.
- **Onde:** `P/11_Rua.jpg`, `P/11_Leste.jpg`, `R/03_Gramado_P2.jpg`.
- **Código:** `sg_craft.py: shell()`, `dais_step()`; `sg_terrain.py: emit_top()`.
- **Direção:** adro de lajes em anel (R 24) com 2 degraus, canteiros de ervas medicinais, 2 bancos e estacas com
  frascos.

### 11.07 Alambiques soltos em volta · Tier B
- **Errado:** os alambiques de cobre ficam pousados na grama, sem base e sem ligação com o prédio.
- **Onde:** `P/11_Fundo.jpg`, `R/11_Fundo.jpg`.
- **Código:** `sg_craft.py: lab_tanks()`.
- **Direção:** base de pedra, tubulação de cobre entrando na parede e lenha ou fornalha sob cada um.

### 11.08 Estantes em módulo único · Tier B
- **Errado:** a mesma estante com frontão ao longo de todo o perímetro interno.
- **Onde:** `P/11_In_Caldeirao.jpg`, `P/11_In_Prateleiras.jpg`.
- **Código:** `sg_craft.py: bookcases()`, `build_row()`.
- **Direção:** 2 alturas alternadas, um armário de vidro, um nicho com escada de biblioteca.

---

## 12 Invocação

### 12.01 Estrela Neon grande na esfera armilar · Tier A
- **Errado:** a estrela violeta do topo é o 2.º ou 3.º ponto mais brilhante da ilha vista da vila. Compete com a
  rosácea e passa a alquimia (hierarquia pedida: alquimia > invocação).
- **Onde:** `P/12_Ponte.jpg`, `P/12_Media.jpg`, `R/03_RuaP1_W.jpg`, `R/01_Ponte_Curva.jpg`.
- **Código:** `sg_summon.py: portal_stars_only()`, `order_dressing()` (VFX `VFX_SGSUM_*`).
- **Direção:** estrela 30% menor em violeta médio e escuro. Brilho no aro e não no corpo.

### 12.02 Véu do portal da torre saturado · Tier A
- **Errado:** arco Neon violeta saturado com estrela, lendo como placa.
- **Onde:** `P/12_Plataforma.jpg`, `P/12_Ponte.jpg`.
- **Código:** `sg_summon.py: portal_veil()`.
- **Direção:** véu mais escuro com o Neon só no filete do arco.

### 12.03 Arranque da ponte do summon na grama · Tier B
- **Errado:** a grama do ombro sobe até a balaustrada da ponte, sem encontro de cantaria.
- **Onde:** `P/12_Ponte_Parapeito.jpg`.
- **Código:** `sg_summon.py: bridge()`, `measure_bridge_faces()`; `sg_terrain.py: summon_isle()`.
- **Direção:** cabeceira de cantaria com pilaretes e degrau, e a grama terminando num meio-fio.

### 12.04 Pedestais de lanterna em caixa · Tier B
- **Errado:** pedestais lisos de cantaria com lanterna em cima, dos 2 lados do portal.
- **Onde:** `P/12_Borda.jpg`, `P/12_Plataforma.jpg`.
- **Código:** `sg_summon.py: pedestal_lantern()`, `in_pedestal()`.
- **Direção:** pedestal torneado do kit (≤ 3,5) com base moldurada.

### 12.05 Plataforma sem uso além da torre · Tier B
- **Errado:** o anel de R 22 é piso e balaustrada. Falta onde esperar a invocação: banco, pedestais de oferenda.
- **Onde:** `P/12_Media.jpg`, `P/12_Borda.jpg`.
- **Código:** `sg_summon.py: base()`, `floor_inlay()`.
- **Direção:** 2 bancos curvos encostados na balaustrada e 4 pedestais baixos com cristais apagados.

---

## 13 Saída noroeste e Jardim-Mirante

### 13.01 [CRÍTICO] Beco oeste (rota da saída): 300 studs de nada · Tier B
- **Errado:** do pátio à cabeceira da saída, o jogador anda numa faixa de lajes reta entre grama chapada e o flanco
  liso do castelo, com 1 lanterna e 2 topiárias. É a rota mais longa da ilha sem um acontecimento.
- **Onde:** `P/13_Beco_W1.jpg`, `P/13_Beco_W2.jpg`, `P/13_Beco_W3.jpg`, `R/13_Beco_W2.jpg`.
- **Código:** `sg_court.py: build()` (becos), `sg_props.py: build()`, `sg_garden.py: plant_band()`;
  `sg_layout.py: EXIT_ROUTE`.
- **Direção:**
  - Caminho com curvas leves dentro da faixa (o QA de rota continua o mesmo).
  - 2 acontecimentos: fonte de parede no flanco e um pórtico ou pérgula a meio caminho.
  - Bancos, canteiros contra o castelo e lanternas nos 3 nós.

### 13.02 Portão Demon Slayer domina a metade norte · Tier A (harmonia)
- **Errado:** o painel vermelho Neon do portão DS (asset aprovado) é o ponto mais brilhante e saturado do lado norte e
  noroeste, visível desde o pátio.
- **Onde:** `P/13_Beco_W3.jpg`, `P/13_PortaoDS.jpg`, `P/14_Norte.jpg`, `P/06_Flanco_W.jpg`.
- **Código:** asset aprovado do portão (`sg_core`), fora do escopo deste passe.
- **Direção:** só registro. Se o usuário permitir: Neon do painel um valor abaixo enquanto a área 4 estiver
  bloqueada.

### 13.03 Terraço norte: gramado liso e pinheiros encostados · Tier B
- **Errado:** entre a torre-coroa e a borda, só grama chapada e um grupo de pinheiros contra a parede (06.08).
- **Onde:** `P/13_Terraco_Norte.jpg`, `P/06_Coroa_Norte.jpg`.
- **Código:** `sg_terrain.py: emit_top()`; `sg_veg.py: groves()`.
- **Direção:** jardim de cemitério ou ermida da ordem (lápides baixas, cruzeiro, oliveira torta) ou terraço com
  bancos e vista.

### 13.04 Jardim-Mirante esparso · Tier B
- **Errado:** terraço circular com balaustrada, um banco curvo, uma árvore torta e um disco violeta no centro. Pouco
  para um "mirante do luar".
- **Onde:** `P/13_Mirante.jpg`, `P/13_Mirante_Vista.jpg`.
- **Código:** `sg_court.py: mirante()`, `moon_tree()`.
- **Direção:** pérgula ou caramanchão com trepadeira (de folhas, não bolotas), luneta de bronze, mesa de pedra com
  2 bancos e canteiros baixos na volta.

### 13.05 Caminho até o mirante: 150 de faixa reta · Tier B
- **Errado:** do EastP3 ao mirante, faixa reta de lajes no gramado chapado, encostada no flanco liso.
- **Onde:** `P/13_Mirante_Caminho.jpg`.
- **Código:** `sg_court.py: build()`; `sg_layout.py: STREETS` (leste).
- **Direção:** a mesma receita do 13.01 (curva leve, 1 acontecimento, bordadura).

### 13.06 Junção da cantaria com a laca DS · Tier B
- **Errado:** o guarda-corpo vermelho da área 4 encosta no parapeito gótico sem transição.
- **Onde:** `P/13_Saida_Volta.jpg`, `P/13_Saida_Lado.jpg`.
- **Código:** `sg_exit.py: ds_rail()`, `_islet_meet()`.
- **Direção:** pilarete de transição (pedra embaixo, laca em cima) no ponto de troca.

---

## 14 Terreno e silhueta

### 14.01 [CRÍTICO] A ilha lê como prato ou bolo · Tier C
- **Errado:** de todos os lados, o topo é plano e a falésia tem a mesma altura em todo o contorno. A quilha quase
  não aparece (a base parece cortada reta). Os 7 promontórios não quebram a linha.
- **Onde:** `P/14_Leste.jpg`, `P/14_Oeste.jpg`, `R/14_Ilha2.jpg`, `R/14_Leste.jpg`.
- **Código:** `sg_terrain.py: rim_cliff()`, `block_strata()`, `keel()`, `keels()`, `prom_w()`.
- **Direção:**
  - Falésia mais alta sob o castelo e mais baixa sob a vila.
  - Promontórios descendo em degraus.
  - Quilha em cone invertido de 1,5 a 2× a altura da falésia, com 2 ou 3 lóbulos e pontas.
  - Uma "raiz" de rocha sob a ponte de chegada.

### 14.02 [CRÍTICO] Falésia no Roblox: paliçada · Tier C/B
- **Errado:** sem textura, a falésia são prismas verticais iguais, lado a lado, e lê como cerca de tábuas. É o que se
  vê da ponte de chegada por 230 studs.
- **Onde:** `R/01_Ponte_Curva.jpg`, `R/01_Ponte_Reta.jpg`, `R/01_PorticoA_CU.jpg`, `R/14_Ilha2_Perto.jpg`.
- **Código:** `sg_terrain.py: rim_cliff()`, `hex_pts()`, `column()`, `block_strata()`.
- **Direção:** grupos de colunas com topos escalonados, 2 estratos horizontais com recuo e saliência (uma faixa
  clara de "topo ao luar") e larguras variadas por grupo (dirigido).

### 14.03 Topo da ilha visto de cima: placas lisas · Tier C
- **Errado:** de longe e de cima, o P1 (plano claro) e os gramados (verde chapado) formam 2 retângulos lisos. Leem
  como maquete.
- **Onde:** `P/14_Alto_34.jpg`, `R/14_Alto_34.jpg`, `R/02_Praca_Alta.jpg`.
- **Código:** `sg_terrain.py: tops()`; `sg_garden.py: field()`.
- **Direção:** 02.01 e 03.03 resolvem.

### 14.04 Castelo esmaga a vila na silhueta · Tier C
- **Errado:** o castelo 2× ocupa metade da ilha. A vila, de 2 andares e sem um volume alto, some ao lado.
- **Onde:** `P/14_Oeste.jpg`, `P/14_Sul.jpg`, `P/14_Ilha2.jpg`.
- **Código:** `sg_village.py: build()` (sem marco vertical).
- **Direção:** sem mudar o layout: um campanário ou torre do relógio na praça, ou a torre do H3 alta, como contraponto
  vertical da vila.

### 14.05 Nuvens da prévia · Tier C (só prévia)
- **Errado:** discos lilás em anel regular sob a ilha (só prévia). No jogo o mar escuro da área substitui.
- **Onde:** `P/14_Leste.jpg`.
- **Código:** `sg_scene.py: clouds()`.
- **Direção:** só registro. Não confiar nelas para julgar a silhueta.

---

## 15 Materiais, emissivo e luz

### 15.01 [CRÍTICO] O export corta todas as luzes para Range ≤ 20 · global
- **Errado:** `export_roblox.lights()` faz `rng = min(20, ...)` e `br = min(1.5, ...)` para toda PointLight.
  Interiores de 180 a 200 (salão, Salão Sombrio, salas) ficam com ilhas de luz de 20 e o resto no ambiente noturno.
  Explica o "quase preto" do `J/07`. A prévia do Blender esconde isso.
- **Onde:** `J/07_caverna_galeria.jpg`, `J/06_salao.jpg`, `renders/ingame_v4/03_sala_masmorra.jpg`.
- **Código:** `lobby_area/forja_mineradora/export_roblox.py: lights()` (linhas 741 a 753, compartilhado com as outras
  ilhas); `export_sg.py` (já faz override de `ER.LIGHT_KEEP`).
- **Direção:**
  - Override só da Ilha 3 no `export_sg`: prefixos `L_SGCave`, `L_SGHall` e `L_SGDun` com Range 40 a 60 e
    Brightness 1 a 2. Não mexer no `export_roblox` (lobby e ilhas 1 e 2).
  - Validar no Play com 3 fotos (galeria, nave, R2).

### 15.02 [CRÍTICO] Paleta monocromática no Roblox · global
- **Errado:** calçamento (94, 92, 114), cantaria de arrimo (100, 100, 112) e alvenaria do castelo (88, 88, 104) estão
  a ~10 de distância. No Roblox, chão, muro, muralha e castelo viram um lilás-azulado só, e a forma não se separa
  por valor.
- **Onde:** `R/01_Ponte_Reta.jpg`, `R/02_Praca_Alta.jpg`, `R/03_RuaP1_W.jpg`, `R/06_Fachada_Base.jpg`.
- **Código:** `sg_lib.py: SMATS` (`Stone_Paving_SG`, `Stone_SG_Block`, `Stone_SG_Castle`, `Stone_SG_Floor`).
- **Direção:** escala de valor dirigida:
  - chão mais escuro e um pouco quente (~(78, 74, 86));
  - paredes médias e frias;
  - cantaria de remate clara (`TrimLow`);
  - telhados escuros.

  O violeta fica só em tecido, vidro e magia.

### 15.03 [CRÍTICO] Hierarquia de emissivo fora da ordem · global
- **Errado:** a ordem pedida é dungeon > alquimia > invocação > magia do castelo > ambiente (vila quente). Medido nas
  imagens:
  - o portal DS (vermelho) e a estrela do summon são mais fortes que a alquimia;
  - a alquimia brilha em amarelo de janela, e não em magia;
  - o castelo tem rosácea Neon, arquivoltas Neon, fio do pátio e tímpano, acima do "violeta suave";
  - as janelas da vila são o laranja mais forte da ilha.
- **Onde:** `J/01_ponte_chegada.jpg`, `J/04_patio.jpg`, `P/14_Norte.jpg`, `R/03_RuaP1_W.jpg`.
- **Código:** `sg_lib.py: SMATS` (`*_Glow`); `sg_castle.py: rose()`, `porch()`; `sg_court.py: noble_path()`;
  `sg_summon.py`; `sg_craft.py: window_out()`.
- **Direção:** tabela de intensidade por zona, com teto de área Neon por zona (studs²), aplicada nos itens 05.01,
  06.05, 06.11, 11.01, 11.04, 12.01 e 03.12.

### 15.04 Água azul saturada · Tier B
- **Errado:** `Water_SG` (64, 96, 196) é o azul mais saturado da ilha (espelhos do pátio, prévia da fonte).
- **Onde:** `P/05_Patio_E.jpg`, `P/06_Castelo_Alto.jpg`.
- **Código:** `sg_lib.py: SMATS["Water_SG"]`; a água do Roblox lê `WATER_*`.
- **Direção:** navy escuro (~(30, 40, 80)), com o reflexo fazendo o trabalho.

### 15.05 Mármore negro brilhante no chão · Tier B
- **Errado:** `Stone_SG_MarbleBlack` (rough 0,25) no caminho do pátio, no salão e nas salas dá reflexos de piso
  molhado (manchas brilhantes no `P/10_*`).
- **Onde:** `P/05_Patio_Caminho.jpg`, `P/10_R2_Diagonal.jpg`, `P/07_Piso.jpg`.
- **Código:** `sg_lib.py: SMATS["Stone_SG_MarbleBlack"]` e a regra de material do Roblox (`rbx_rule`).
- **Direção:** em piso, pedra fosca (Slate). O mármore fica para pequenos embutidos.

### 15.06 Chamas em cones Neon em toda a ilha · Tier B
- **Errado:** lustres, tochas, lareiras e velas usam cones laranja e amarelo Neon (vila, salão, Salão Sombrio,
  masmorra, caracol).
- **Onde:** `P/04_H1_Quarto.jpg`, `P/08_Trono_34.jpg`, `P/08_Caracol_Meio.jpg`, `P/10_R3_Retabulo.jpg`.
- **Código:** `sg_hall.py: candle()`; `sg_dungeon.py: candle()`, `torch()`; `sg_cave.py: torch_cup()`;
  `sg_village_int.py: candle()`, `fireplace()`.
- **Direção:** uma chama do kit (gota pequena, 2 tons, ≤ 0,4) compartilhada, como pedia o 12.09 da AUDITORIA 2.

### 15.07 Ferro preto que some no escuro · Tier B
- **Errado:** guarda-corpos, corrimãos e grades em `Metal_SG_BlackIron` somem sobre o fundo escuro do subsolo.
- **Onde:** `J/07_caverna_galeria.jpg`, `R/09_Galeria_Chegada.jpg`.
- **Código:** `sg_cave.py: iron_rail()`, `chain_lite()`.
- **Direção:** no subsolo, ferro com corrimão de madeira mais clara e pilaretes de pedra clara (a silhueta lê pela
  pedra).

---

## 16 Harmonia global

### 16.01 [CRÍTICO] A faixa do jogador continua blockout · global
- **Errado:** o detalhe foi para props pequenos (lanternas, bancos, trepadeiras), mas as superfícies que enchem a
  tela continuam lisas:
  - chão do P1 e da calçada (01.01, 02.01);
  - escadas (16.03);
  - paredes de 0 a 20 do castelo e da muralha (05.05, 06.01);
  - abóbadas do salão e das salas (07.01, 10.01);
  - falésia (14.02);
  - paredes internas das casas (04.02).

  É por isso que o usuário lê "blockout".
- **Onde:** os itens citados.
- **Direção:** a ordem de ataque abaixo começa por essas superfícies, não por props.

### 16.02 [CRÍTICO] Lugar habitado sem vida · global
- **Errado:** vila (03.01), pátio (05.10), becos (13.01), mirante (13.04), Salão Sombrio (09.13) e interiores (04.01 a
  04.03) não têm os objetos de uso que contam quem mora ali.
- **Direção:** um módulo de vestir por zona, com props do ofício agrupados em "cenas" de 3 a 6 peças, sem espalhar.

### 16.03 [CRÍTICO] Todas as escadas são lajes contínuas · global
- **Errado:** Entry, P1P2, Gate, EastP3, Summon, escadaria do Salão Sombrio e a caracol: degrau-laje sem pedra,
  focinho ou espelho.
- **Onde:** `P/01_Escada.jpg`, `P/03_EscP1P2_Pe.jpg`, `P/05_Passagem_Leste.jpg`, `P/09_Escadaria_Pe.jpg`,
  `P/08_Caracol_Meio.jpg`.
- **Código:** `sg_lib.py: plan_stair` (todas as do plano); `sg_cave.py: grand_stair()`, `spiral_stairs()`.
- **Direção:** consertar o degrau UMA vez em `plan_stair` (pedras, focinho, espelho recuado e 2 tons), e repetir a
  receita nas 2 escadas do `sg_cave`.

### 16.04 Vegetação de cones contra a arquitetura detalhada · global
- **Errado:** pinheiros, ciprestes e topiárias são cones facetados empilhados. Ao lado da cantaria e do enxaimel,
  leem como brinquedo. Aparecem na altura do olho em todas as zonas.
- **Onde:** `P/03_Arrimo_W.jpg`, `R/03_Arrimo_E.jpg`, `P/06_Coroa_Norte.jpg`, `P/05_Patio_E.jpg`,
  `P/02_Praca_Norte.jpg`.
- **Código:** `sg_veg.py: pine()`, `cypress()`, `crown_r()`; `sg_garden.py: topiary()`.
- **Direção:**
  - Perto das rotas (< 30), pinheiro com camadas de galho em cards caídos e tronco à vista, cipreste em chama com 3
    massas.
  - Os de fundo ficam como estão (Tier C).
  - Topiária em formas compostas (05.03).

### 16.05 Repetição sem variação · global
- **Errado:** casas A iguais (03.08, 04.01), 3 salas iguais (10.02), 5 arcos iguais (09.05), nichos iguais (07.07),
  janelas iguais (06.07), parapeito igual por 230 (01.06), arrimo igual por 330 (03.05).
- **Direção:** a regra da AUDITORIA 2 (16.04): nunca a mesma peça em passo fixo por mais de 20 studs. Ritmo A-B com
  ênfase nos nós.

### 16.06 Emblema do crescente demais · global
- **Errado:** o crescente aparece na rosácea, no tímpano, no trono, no piso do salão, no caldeirão, nos estandartes e
  nos medalhões. A AUDITORIA 2 (16.02) pedia corte.
- **Onde:** `P/07_Piso.jpg`, `P/11_In_Porta.jpg`, `P/08_Trono_Fechado.jpg`, `P/06_Fachada_Patio.jpg`.
- **Direção:** só no tímpano da porta, nos estandartes e no trono (pequeno). Tirar do piso, do caldeirão e da
  rosácea.

### 16.07 Escala dos props não acompanhou o 2× · global
- **Errado:** o castelo, o salão e as salas dobraram, mas estátuas (06.03), lustres (07.09, 10.07), arco triunfal
  (07.03), folhas da porta (detalhe, 06.02) e estandartes ficaram na escala antiga.
- **Direção:** escala por espaço: no salão e nas salas, props ×1,5 a ×2. Avatar continua com 5: o que ele toca
  (bancos, degraus, corrimão) não muda.

### 16.08 Transições entre módulos · global
- **Errado:**
  - ponte × ilha (01.07);
  - castelo × terreno: a parede encosta direto na grama, sem rodapé, calçada ou dreno;
  - casas × chão: soco direto no plano liso (P1) ou na grama (P2), com floreira-caixa no lugar da calçada;
  - muralha × casas H6 e H7 (03.14);
  - alquimia × grama (11.06);
  - summon × ombro (12.03);
  - ponte gótica × laca DS (13.06).
- **Onde:** `P/06_Fachada_Base.jpg`, `P/03_H6_Lado.jpg`, `P/11_Rua.jpg`, `P/01_Ponte_Encontro.jpg`.
- **Direção:** um "rodapé de chão" comum: calçada de 2 de lajes em volta de todo prédio, com meio-fio para a grama.
  Entra no `sg_terrain` (recorte) com as lajes no módulo do prédio.

### 16.09 Pontos para conferir no Play (queda ou travamento) · global
- **Errado:** o QA de rotas passa, mas estes pontos não têm prova visual:
  - gramados rebaixados do pátio: murete de 1,3, com degrau só nas pontas; quem pula dentro precisa achar a saída;
  - canal do rio do Salão Sombrio: lâmina em −13,5 e fundo em −15, borda de cantaria lisa; confirmar que o jogador
    sobe de volta sem pular;
  - borda interna da caracol (R 3 a 4): piso de 0,84 por degrau, junto ao núcleo;
  - becos atrás da H6 e da H7, entre a casa e a muralha (03.14): risco de prender a câmera;
  - o vão sob a cabeceira da ponte do summon (`12_Ponte_Lado` ficou dentro de massa).
- **Código:** `sg_qa.py` (rotas e sondas).
- **Direção:** 5 sondas novas no QA (saída do gramado, saída do rio, câmera nos becos H6/H7, caracol a R 3,5,
  cabeceira do summon) e uma volta no Play.

---

## Resumo

### Contagem por setor

| Setor | Itens | [CRÍTICO] |
|---|---:|---:|
| 01 Ponte e entrada | 12 | 4 |
| 02 Praça e fonte | 8 | 1 |
| 03 Vila (exterior) | 16 | 6 |
| 04 Interiores das casas | 11 | 3 |
| 05 Pátio-jardim e muralha | 10 | 3 |
| 06 Castelo (exterior) | 13 | 3 |
| 07 Salão (interior) | 10 | 2 |
| 08 Trono e escada caracol | 6 | 1 |
| 09 Salão Sombrio | 14 | 4 |
| 10 Masmorra | 11 | 2 |
| 11 Alquimia | 8 | 0 |
| 12 Invocação | 5 | 0 |
| 13 Saída e mirante | 6 | 1 |
| 14 Terreno e silhueta | 5 | 2 |
| 15 Materiais, emissivo e luz | 7 | 3 |
| 16 Harmonia global | 9 | 3 |
| **Total** | **151** | **38** |

Alguns itens são remissões (16.x reúne os setores). Contam uma vez só no conserto.

### Os 15 piores

1. **Salão Sombrio quase preto** (09.01, 09.02, 15.01). Rocha a 13% de valor, 6 luzes, export cortando o Range em
   20. A área-hero nova é invisível no jogo.
2. **Export corta toda luz em Range 20** (15.01, `export_roblox.lights`). Escurece o salão, a cova e as salas de uma
   vez.
3. **Calçada do spawn e P1 inteiro em plano liso** (01.01, 02.01, `sg_terrain.tops`). A primeira imagem da ilha é um
   tapete lilás vazio.
4. **Abóbada de arame do salão** (07.01, `sg_hall.vault/ribs`). O maior plano do hero lê como estrutura de estufa.
5. **Abóbada de tenda das salas e salas iguais** (10.01, 10.02, `sg_dungeon.vault`, `room_kit`).
6. **Faixa baixa do castelo lisa: fachada, flancos e muralha por dentro** (06.01, 05.05, `sg_castle.wall_skin`,
   `muralha`).
7. **Todas as escadas em lajes contínuas** (16.03, `sg_lib.plan_stair`, `sg_cave.grand_stair`, `spiral_stairs`).
8. **Caminho nobre preto com fio Neon** (05.01, `sg_court.noble_path`).
9. **Vila esparsa e sem vida** (03.01, 16.02). Casas soltas num platô, sem quintal nem props.
10. **Interiores idênticos e de paredes lisas** (04.01, 04.02, `sg_village_int.furnish_a`, `linings`).
11. **Ruas com "faixa de rodovia"** (03.02, `sg_village.pave_strip`).
12. **Porta principal: folhas planas, guardas baixos, nártex de andaime** (06.02, 06.03, 06.04).
13. **Paleta monocromática no Roblox** (15.02, `sg_lib.SMATS`). Chão, muro e castelo no mesmo lilás.
14. **Falésia em paliçada e ilha em prato** (14.01, 14.02, `sg_terrain.rim_cliff`, `keel`).
15. **Rocha da cova em papel amassado e latas** (09.03, 09.04, `sg_cave.ceiling`, `basalt_organ`), com os
    arcos-anel soltos (09.05).

### Ordem de ataque por GANHO por hora

1. **Luz e valor (horas, ganho enorme):**
   - override de Range e Brightness no `export_sg` (15.01);
   - ambiente de subsolo no `CeuSombras` (09.01);
   - rocha da cova e cantaria em 2 valores (09.02);
   - paleta de chão × parede × remate (15.02);
   - água navy (15.04) e mármore fosco (15.05).

   Quase só números, e muda a ilha inteira no jogo.
2. **Cortes de emissivo (horas):** fio do pátio (05.01, só a parte do Neon), Neon das arquivoltas (06.05), rosácea
   (06.11), janelas inteiras (03.12, 11.01), círculo da alquimia (11.04), estrela do summon (12.01), setas e runas
   da masmorra (10.05, 10.06). Só remover ou trocar material.
3. **Funções compartilhadas (1 a 2 dias, dezenas de instâncias):**
   - degrau em `plan_stair` (16.03);
   - `pave_strip` em 3 ou 4 lajes (03.02);
   - chama do kit (15.06);
   - fechar a fresta das casas (03.13).
4. **Chão (1 dia):** P1 e EntryHigh pavimentados ou em gramado com borda (01.01, 02.01), grama em 3 tons com
   bordadura e touceiras agrupadas (03.03), rodapé de chão em volta dos prédios (16.08).
5. **Abóbadas (1 dia cada):** salão (07.01) e salas (10.01). Grande área de tela, geometria repetida por tramo.
6. **Faixa de 0 a 20 do castelo e da muralha (2 dias):** 06.01, 05.05, 06.02 a 06.04.
7. **Interiores por ofício (2 dias):** 04.01 a 04.04.
8. **Vida e props por zona (2 a 3 dias):** vila (03.01), becos (13.01), pátio (05.10), Salão Sombrio (09.13), salas
   com identidade (10.02).
9. **Rocha da cova e falésia (2 dias):** 09.03, 09.04, 09.05, 14.01, 14.02.
10. **Resto Tier B e C** na ordem do documento.

### Agrupamento por ARQUIVO (agentes em paralelo sem conflito)

Cada linha é um agente. Os arquivos não se cruzam. As dependências entre agentes estão indicadas no fim.

| Agente | Arquivos (só estes) | Itens |
|---|---|---|
| **L: luz no jogo** | `export_sg.py`, `roblox/CeuSombras.client.lua` | 15.01, 09.01 (parte do jogo), 10.11 |
| **P: paleta** | `sg_lib.py` (SMATS e `plan_stair`) | 15.02, 15.04, 15.05, 03.03 (variantes de grama), 16.03 (degrau), 01.02, 03.04 |
| **T: terreno** | `sg_terrain.py` | 01.01 (EntryHigh), 02.01 (chão do P1), 03.05, 02.06, 06.09, 14.01, 14.02, 14.03, 16.08 (recorte do rodapé), 01.11 (meio-fio) |
| **E: entrada** | `sg_entry.py` | 01.03 a 01.10 |
| **V: vila** | `sg_village.py` | 02.02 a 02.04, 03.02, 03.08 a 03.12, 03.16, 14.04 |
| **I: interiores** | `sg_village_int.py` | 03.13, 04.01 a 04.11 |
| **K: castelo** | `sg_castle.py` | 05.05 a 05.08, 06.01, 06.02, 06.04 a 06.07, 06.10 a 06.13 |
| **H: salão** | `sg_hall.py` | 06.06 (piso do salão), 07.01 a 07.10, 08.01 a 08.03, 08.05 |
| **C: Salão Sombrio** | `sg_cave.py` | 08.04, 08.06, 09.01 (material e luzes), 09.02 a 09.09, 09.11 a 09.14, 15.07 |
| **D: masmorra** | `sg_dungeon.py` | 10.01 a 10.10 |
| **J: pátio e mirante** | `sg_court.py` | 02.03 (estátua da fonte), 05.01 a 05.04, 05.09, 05.10, 06.03, 13.01, 13.04, 13.05 |
| **G: vegetação** | `sg_garden.py`, `sg_veg.py` | 03.03 (touceiras/bordadura), 03.06, 03.07, 05.03, 06.08, 13.03, 16.04 |
| **A: alquimia** | `sg_craft.py` | 11.01 a 11.08 |
| **S: invocação** | `sg_summon.py` | 12.01 a 12.05 |
| **X: saída** | `sg_exit.py` | 13.06 |
| **R: vestir** | `sg_props.py` | 02.05, 03.01 (quintais e props), 03.14, 03.15, 16.02 (vila e becos) |
| **W: água** | `sg_water.py` | 09.10, conferir 05.02 com os marcadores |
| **Q: QA** | `sg_qa.py` | 16.09 |

**Dependências e cuidados:**
- **P primeiro.** A paleta muda o valor de tudo, e os outros agentes julgam o "depois" com a cor nova. Ou P roda junto
  e todos refazem as folhas no fim.
- **L é independente.** Só o Play valida.
- **T × V × R no chão do P1:**
  - T emite o chão (lajes ou grama);
  - V não pavimenta fora de praça e ruas;
  - R só põe props.

  Combinar antes as zonas livres pela planta de props.
- **I × V na fresta (03.13):** fica com I (forro e piso). V não mexe no `socle`.
- **J × V na estátua da fonte (02.03):** `fountain_statue` chama `sg_court.hooded_figure`. J cria a figura nova e V
  só troca a chamada (pequeno, em sequência).
- **K × H na porta:** K fica com a porta e o nártex, H com o piso do salão.
- **C × L na luz da cova:** C cria as luzes `L_SGCave_*`, L ajusta o Range no export.
- `fm_lib.py` e `export_roblox.py` são compartilhados com o lobby e as ilhas 1 e 2. Nenhum agente edita: tudo por
  override no `sg_lib` e no `export_sg`.
- O orçamento continua em `studio_sg.BUDGET` / `export_sg.BUDGET_OWNER`. Os ganhos acima são de forma e material, não
  de polycount. Onde entra geometria (abóbadas, arcadas, props), cada agente mede a zona.
