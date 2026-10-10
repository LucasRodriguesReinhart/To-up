# Plano V2: Ilha 5 One Piece / Wano (refazimento depois da reprovação de 10/10)

**Data:** 2026-10-10.

**Entradas:**
- `feedback_20261010/FEEDBACK_USUARIO.md` (U1–U16), as 15 capturas e os 3 vídeos;
- a auditoria medida `feedback_20261010/aud/AUDITORIA_V2.md` e as folhas dela;
- `ref/ref_03_atmosfera_wano_anime.jpg` (NOVA: guia de atmosfera e de leitura da cidade), `ref_02` (castelo + árvore) e `ref_01` (composição aprovada).

**Base:** este plano substitui as seções 4.3/4.4, 8, 10 e 14 do `PLANO_OP.md` no que conflitar. Âncora, cotas principais, praça e contratos continuam valendo.

**Nada foi editado** além deste arquivo e de `feedback_20261010/aud/`. Nenhum `op_*.py` e nenhum `.blend` oficial foram tocados.

---

## 0. Decisões em uma página

| # | Tema | Decisão V2 |
|---|---|---|
| 1 | Causa da reprovação | Lê "procedural de blocos": caixas com telhado aplicado, árvores-esfera, laje sobre grama, casas soltas. Além disso, há **11.671 studs² de chão aparente sem colisão alcançável** (medido). V2 = **cidade densa tipo ref_03 + colisão nascida do visual + gate de qualidade de perto antes de espalhar**. |
| 2 | O que fica | Âncora e encaixe 0,0000; ponte de chegada; torii; cotas T0/T1/P/CF/W3/CC/porto; **praça de mineração** (`PLAZA`, `MINE_RECT` 152 × 120, **72 `ORE_`**, 76 `GP_Block`, piso plano 92,2, 70 minérios); **Summon** em (170, 214) e os marcadores dele; **saída** (ponte 88, promontório, portão OPM, âncora + guarda); `roblox/OnePieceIsland.lua` (contrato); `CeuWano`; export/montar; 60 fps. |
| 3 | Cidade (U1/U2/U12) | **Avenida de chegada** larga e reta no eixo, até a escadaria da praça (o eixo continua pela faixa central da praça → Adro → portão vermelho → cachoeira → castelo). **Quarteirões densos** de casas geminadas (machiya em fileira), com fachadas contínuas e telhados escalonados que se sobrepõem (hisashi + telhado principal + 3º piso). Cor por quadra: **azul-cobalto, verde-água, vermelho, roxo**. Ruas com meio-fio, sarjeta e pedra assentada; **zero laje solta sobre grama**. São **5 interiores vivos** e o resto é vitrine rasa com profundidade. |
| 4 | Vilarejo NE (U11) | **ELIMINAR as 9 casas soltas.** O NE vira o **Santuário do Porto**: haiden refeito, sando com lanternas, bosque de cerejeiras com pétalas e **1 fileira contínua de lojas** fechando a praça a nordeste. A **montanha de trás** vira **socalcos de pedra (ishigaki) com pinheiros**, com colisão fechada até o topo visual. Topos alcançáveis colidem; os outros ficam acima de 8,5 da guarda. |
| 5 | Castelo e árvore (U3/U4) | **Castelo:** 5 andares de telhados escalonados com frontões chidori e kara-hafu, beiral grosso com caibros, janelas em faixas pretas, varanda vermelha, remates dourados e base de ishigaki em talude. **Árvore** (ref_02/ref_03): tronco GROSSO (raio 14 → 5) que **abraça** o castelo, com copas de **pinheiro em nuvem** (pads achatados em camadas). Árvores menores refeitas: cerejeira de copa em cachos e pinheiro de pads. Nenhuma esfera facetada. |
| 6 | Porto (U9) | **2 navios** (o grande acessível + 1 junco de Wano fundeado), **5 barcos**. Movimento só pela tag `IlhaMovel` (`bob`/`rpm`): barcos balançando, **carga sendo içada** por guindaste de madeira (tambor em `rpm`, fardo em `bob`), cais vivo com redes, armazém aberto e carga. Água: `AguaCorrente` do `CeuWano`. |
| 7 | Summon (U10) | **Recomendado: opção A, "Convés do Summon".** O terraço vira o convés de um navio pirata: tabuado, amurada, proa com carranca, timão, 2 mastros com Jolly Roger (iconografia aprovada do portão OP), baús, barris, mesa de mapa e rosa-dos-ventos no piso. A torre AMS fica **intacta**: estrela dourada, anéis, corpo e núcleo azul. |
| 8 | Remoções (U13/U16) | **Sai o pagode do pináculo** (`OP_Lmk_Pagoda`) e **sai o H3 do topo da muralha do porto**. Bandeiras: de ~20 para **≤ 10**, só onde contam história. |
| 9 | Postes e miúdos (U7/U15) | Nova família de luz: tōrō de pedra (kasuga), andon de poste baixo e chochin de beiral. Sai o poste em T. Também saem refeitos: poço, bancas, pontes do canal (arco de verdade, U6) e tábuas da ponte de saída sem frestas (U5). |
| 10 | Atmosfera (U14) | Perfil `[5]` rosa-lilás da ref_03 (seção 7): Atmosphere rosa com Haze alto, ColorShift quente-rosado e nuvens rosadas. São **10 emissores de pétalas por grupo de cerejeiras** (receita no marcador, sistema existente). |
| 11 | Colisão (U5/U8) | Nova regra: **toda superfície visual que o jogador alcança colide a ≤ 0,5**. Rocha fechada até o topo, guarda de **8,5** nos lábios (pulo de 7,2), canais com leito colidível, telhados com colisão, sem extrapolar o polígono. **O gate de QA usa o mesmo raio da auditoria.** |
| 12 | Processo | V2-0 planta e colisão → **V2-1 GATE de qualidade de perto** (quadra-modelo, poste, rua, cerejeira, pinheiro, ponte em arco; aprovado pelo usuário em imagens próximas antes de espalhar) → V2-2 marcos → V2-3 expansão → V2-4 Roblox → V2-5 harmonia. |
| 13 | Orçamento | ≤ 640k tris, ≤ 650 MeshParts, col ≤ 1.300, luzes de dia ≤ 36. Plano por dono: **632k / 566 + VFX 6k / 30 / col ~1.180 / 12 luzes de dia** (seção 10). |

---

## 1. O que a auditoria mediu (resumo; detalhes em `aud/AUDITORIA_V2.md`)

**U8, cair para dentro do modelo.** São 11.671 studs² de chão ou rocha visual alcançável sem colisão, mais 2.138 de telhado e 2.734 de copa. As causas:
- **R1:** a colisão nasce dos 12 polígonos da planta, não do visual. `ROCKS`, pele da borda, canais, bacia e arrimos não colidem.
- **R2:** a guarda tem 3,2 e o pulo tem 7,2.
- **R3:** canais e bacia não têm fundo; a água não colide.
- **R4:** as faixas "union" do `op_col.strips` geram **piso 92,2 dentro da rocha NE** (x 190..226, y 290..337) e piso sob as muralhas do cais.
- **R5:** a colisão das casas é uma caixa 7 a 10 abaixo do telhado.

**Piores zonas:**

| Zona | Área (studs²) | Coordenadas (local) |
|---|---|---|
| Borda oeste | 1.665 | x −230..−179 |
| Canal oeste | 1.620 | x −179..−170, y 50..299 |
| Canal leste + bacia | 1.422 | y 335..347 |
| Borda sul | 1.249 | — |
| Topos de muralha do cais | 603 | — |
| **Montanha NE** | 369 + 216 | (192..231, 290..337) e BackE/CastleFootE |
| Rochedo do castelo | 663 | — |

**U5, vãos.** A colisão do piso é contínua (só há 10 vãos ≥ 0,6, quase todos em telhado ou mureta). As **frestas visuais** são:
- tábuas da cabeça da ponte de saída (212..221, 232..249), 0,2–0,6, com o cais visível 46 abaixo;
- **junta T1/praça em y 117–119**, de x −113 a +59, 0,2–0,8;
- trincas da pele × falésia em toda a borda, de 0,4 a 3,8;
- rua alta do porto, até 3,8;
- topo da OesteAlta, até 3,6.

**U6, ponte do canal.**
- Vão do canal: 7,0. Água a só 0,6 do piso.
- Tabuleiro de 14,4 com flecha de 0,13, 3,6–3,8 deitados em cada calçada.
- **A capa do canal (93,05–93,15) fica ACIMA do tabuleiro (92,8–92,9) e atravessa as tábuas.**
- A colisão é plana a 92,2.
- Causa: o `canal_bridge` desenhou para "capa 92,5", o `op_water` entregou 93,1, e a planta pôs a ponte plana na cota da praça.

---

## 2. Contratos que NÃO mudam (checklist de cada onda)

- **Encaixe:** `WORLD_FROM_PREV` (0, −120, 80,2), `WORLD_YAW_DEG` 145. Distância à âncora da DS 0,0000; ponte de chegada de 120, largura 18.
- **Mineração:**
  - `PLAZA`, `P_BASE` (forma externa), `MINE_RECT` (−76..76, 156..276);
  - piso PLANO 92,2 na zona (raycast `|piso − 92,2| < 0,5`, normal > 0,85);
  - `ORE_*` 72 (2/10/22/38), `GP_Block_*` 76, `MiningZone_OnePiece`;
  - nada colidível de 92,5 a 104,2 dentro da zona.
- **Summon:** `SUMMON_Main` (170, 214, 88,2, frente −X), `SUMMON_Interact` (d 7), `SUMMON_PlayerPosition` (d 16), `Gacha_mare`, `VFX_OPSUM_*`. A torre é o alias aprovado e **não muda**.
- **Saída:** `ISLAND_EXIT_OnePiece` (206, 236), ponte de 88 com rumo de 15°, `GATE_OnePunchMan*`, `PURCHASE_UI_ANCHOR_OnePunchMan`, `COL_GateOnePunchManLock_001`, `ISLAND_NEXT_ANCHOR_OnePunchMan` + guarda (`next_island_guard`).
- **Roblox:**
  - `Core.OnePieceIsland` (`FONTE 'IlhaOnePiece'`, `NOME 'ILHA_ONEPIECE'`, `ZONA`, `PISO 92.2`, `SafeMaxY 150`, `BoundsMinY 28`);
  - marcadores `WATER_*`, `FX_*`, `AUDIO_*` e `SAFE_*`;
  - `CeuWano` (`MOOD 'GrandLine'`) e linha do `IslandWorld`.
  - Os novos `FX_Petals_*` usam a receita já aceita pelo `OnePieceIsland.emissor()`.
- **Mudanças de planta permitidas na V2-0**, documentadas e só da integração:
  - canal oeste e canal leste rebaixados;
  - ponte do canal em arco;
  - NE refeito;
  - `BUILDINGS`/`STREETS` trocados por `BLOCKS`/`STREETS_V2`;
  - `SAFE_NE` movido se o NE mudar;
  - `ROCKS` com colisão.

---

## 3. CIDADE (U1, U2, U11, U12)

### 3.1 Leitura alvo (ref_03)
Uma **avenida larga e reta** com o castelo no fim, dos dois lados **paredões contínuos de fachada**. Por trás, um **tapete de telhados** escalonados que se sobrepõem em 2–3 camadas, com cores por quarteirão. Cerejeiras em cachos nos vazios. Nada de casa solta no gramado.

### 3.2 Malha (planta V2, dono `op_layout`)

| Setor | Forma V2 | Cor do telhado |
|---|---|---|
| **Avenida de chegada** (T1, y 38..108) | Leito de pedra assentada de 18 (x −9..9). **Calçadas de 4** com meio-fio de 0,3 × 0,5 e sarjeta de 0,8 (−0,15). Fachadas contínuas em x ±15. Quadras **AvO** (x −15..−62) e **AvL** (x 15..62) de 4–6 lotes cada, com frentes de 8–14, 2–3 pisos. 1 esquina-marco de 3 pisos por lado. A viela do canal (y 86) e a viela leste (y 111) cortam as quadras como **passagens cobertas** (portal de madeira), sem abrir buraco na fachada. | AvO cobalto / AvL cobalto + 1 vermelho na esquina |
| **Eixo** | A escadaria Praca (28) e uma faixa central da praça em pedra de outro tom e assentamento (x ±15, **RENTE**, sem relevo, zona livre) levam ao Adro (30) e ao portão vermelho. Lê como "a avenida continua até o castelo" sem tocar no spawn. | — |
| **Fachada oeste da praça** (P, x −160..−118, y 125..300) | **3 quadras contínuas** (as antigas W1–W5 viram 1 paredão com recuos de 1–2 e 1 viela em y 212 com o recanto). Fundos para o cais do canal. | **Verde-água** |
| **Além do canal** (W2b, x −216..−184) | 1 fileira contínua de casas de frente para o canal, varandas sobre a água. | Verde-água + 1 cobalto |
| **Bairro do canal** (T1 SO) | 2 quadras densas ao longo da viela do canal; o moinho fica com a roda d'água. | Roxo / cobalto |
| **Rua alta do porto** (T1 leste, x 40..120, y 42..106) | 2 quadras (lojas de carga e armazéns de 2 pisos) com fachada para a viela leste. | **Vermelho** |
| **NE** (P, x 110..231, y 262..340) | Ver 3.4. | Roxo (lojas) + vermelho-laca (santuário) |
| **Terraço alto W3** | 2 mansões refeitas com muro de jardim e jardim de pinheiros; as casas soltas saem. | Verde |

**Regras de quadra:**
- Lotes geminados com parede-meia (sem frestas entre casas).
- Altura de cumeeira variando ±2–4 de lote para lote.
- Em 1 de cada 3 lotes, hisashi contínuo no térreo + 2º piso recuado.
- 1 lote em 4 com 3º piso e telhado irimoya virado para a rua (é o que dá o "escalonado" da ref_03).
- Fundos simples (Tier B) onde ninguém chega.
- **O quintal de terra deixa de existir:** pátio interno de pedra ou jardim delimitado por pedras de borda.

### 3.3 Ruas e chão (U2)
- **Piso:** pedra assentada em fiadas (laje de 3 × 1,5 com junta rebaixada de 0,08). Meio-fio de pedra (0,3) e sarjeta (0,8) nas vias com calçada. Praça e vielas sem meio-fio, com borda de pedra.
- **Grama:** só em jardins com moldura (pedra de borda de 0,25). Nada de laje retangular solta sobre grama (captura 11).
- **Transições:** degrau ou rampa de pedra entre cotas, com banzo. A junta T1/praça de y 117 vira uma **soleira contínua** que tampa as frestas medidas.

### 3.4 NE: decisão
- **Eliminar** N2, N3, N5–N10 (casas soltas sem função).
- **Fazer:**
  - **fileira contínua de 5 lojas** (x 118..200, y 266..290) fechando o canto NE da praça, com a frente para o sul;
  - **sando** de pedra com 6 tōrō, do canto da praça até o **haiden refeito** (aberto, com interior);
  - honden atrás;
  - **bosque de 8 cerejeiras** em 2 grupos (pétalas);
  - lago pequeno ligado ao canal leste.
- **Montanha de trás** (NERocksW/E, BackE, CastleFootE):
  - vira **socalcos de pedra** em 2–3 degraus de 6–8, com pinheiros nos patamares;
  - o patamar 1 (100) é **jardim alcançável com colisão** (mirante), e os de cima ficam ≥ 8,5 acima de qualquer topo alcançável;
  - **colisão maciça até o topo visual** (sem piso dentro da rocha).

### 3.5 Interiores com vida (U12): 5 e não mais

| # | Onde | O que tem |
|---|---|---|
| 1 | Casa de chá (oeste, refeita) | Já existe |
| 2 | Loja de tecidos (AvO) | Rolos nas prateleiras, balcão, noren |
| 3 | Casa de lámen / izakaya (AvL) | Balcão com panelas, bancos, mesas baixas, chochin |
| 4 | Armazém aberto do cais | Carga, redes, balança de mercador |
| 5 | Haiden do santuário NE | — |

- **Requisitos de cada interior:** piso, forro, paredes, 1 luz de dia (≤ 5 no total), colisão das paredes, vão de porta ≥ 5 e saída pelo mesmo lugar.
- **Demais lojas:** vitrine rasa de 1,5–3 de profundidade atrás da treliça ou do noren, com mercadoria visível de dia. Dá vida sem interior falso.

---

## 4. CASTELO E ÁRVORE (U3, U4)

### 4.1 Castelo (dono `op_castle`, cota CC 136,2 mantida)
- **Silhueta (ref_02/ref_03):** 5 andares que encolhem.
  - 1º e 3º com **chidori-hafu** (frontão triangular) nas 4 faces.
  - 2º com **kara-hafu** curvo na frente.
  - Telhado do topo irimoya com **shachihoko dourado**.
  - Telhas em canais com **beiral grosso de 1,2** (caibros visíveis por baixo, cantos levantados).
- **Paredes:** reboco off-white (225–232), com faixa de madeira escura na base de cada andar e **janelas em faixas** (grade preta recuada 0,3).
- **Detalhe:** varanda vermelha no 4º andar (já aprovada) e remates dourados só nas cumeeiras.
- **Base:** ishigaki em **talude de 15°** (pedras desencontradas) sobre o rochedo. O **portão dourado** no pé da rocha (ref_02) vira o portão do pátio.
- **Rochedo:** as cachoeiras da ref_02 ficam como estão (a do castelo com bacia), com colisão fechada.
- **Interior:** o salão acessível continua e ganha vida (tatami, biombos, 2 armaduras de exposição, 3 luzes).
- **Orçamento:** 85k tris, Tier A até +25 do pátio.

### 4.2 Árvore monumental (dono `op_tree`)
- **Tronco:**
  - Nasce **atrás à direita** do castelo, numa base de raízes que abraça a rocha (raízes com colisão).
  - Raio de **14 → 5**, secção achatada e torção dirigida.
  - Sobe, contorna o castelo por trás e passa por cima em arco, formando **quase um anel** em volta do topo (ref_02). Termina à esquerda.
  - Mantém folga ≥ 4 de todo volume do castelo.
- **Casca:** 2 tons + manchas de musgo em geometria separada (sem cor de vértice: lição do Murim).
- **Copa:** **pinheiro em nuvem** (ref_02/ref_03).
  - De 7 a 9 grupos de **pads achatados** em camadas (3–5 discos com bevel suave, face de baixo mais escura), nas pontas dos galhos.
  - Céu aberto entre os grupos.
  - Verde (`Leaf_OP_Pine`) com borda mais clara. Rosa só nas cerejeiras da cidade.
- **Colisão:** raízes e tronco até +20. **Copa sem colisão**, mas toda fora de alcance (≥ 8,5 acima de qualquer topo alcançável).
- **Orçamento:** 40k tris.

### 4.3 Árvores menores (dono `op_veg`)
- **Cerejeira:**
  - Tronco com 2–3 forquilhas.
  - Copa em **cachos** de 5–9 blobs (icosfera de nível 2 com ruído, base achatada).
  - 2 rosas (`Flower_OP_Blossom` e `Light`) + fundo `Deep`.
  - **Sombreamento suave, sem facetas grandes.**
- **Pinheiro (matsu):** tronco em S, galhos horizontais e pads em nuvem (o mesmo módulo da árvore monumental).
- **Arbustos:** karikomi (podados) em 2 tons.
- **Distribuição:** em **grupos com função** (pátio, jardim, sando, beira de canal). Nunca dentro do leito da rua.

---

## 5. PORTO (U9): "ambiente de embarcação de verdade"

**Sem sistema novo:** o movimento vem da tag `IlhaMovel` existente, criada pelo montar para os `VFX_*`.
- `bob`: senoide com 1,6 rad/s e fase por `p.X`.
- `rate`: dente de serra.
- `rpm`: giro sobre `pivot`/`axis`.

| Peça | Dono | Movimento |
|---|---|---|
| **Navio grande** (refeito: casco curvo de cavernas, castelo de proa e de popa, 2 mastros, velas ENFUNADAS presas às vergas, Jolly Roger aprovado) | `op_ship` | **Estático**, porque o convés é acessível pela prancha e a colisão não pode mexer |
| **Junco de Wano** (bezaisen: casco alto, 1 vela quadrada branca com faixas, fundeado na enseada a ~60 do cais) | `op_ship` | `VFX_OP_Junk` com `bob` 0,4 |
| **5 barcos** (2 sampans no pier, 1 yakatabune, 1 barco de pesca com rede, 1 bote fundeado) | `op_harbor` | `VFX_OP_Boat_1..4` com `bob` 0,25–0,5 (o 5º é estático, puxado na rampa) |
| **Guindaste de madeira** (pórtico + lança + tambor) no cais, com **fardo içado** | `op_harbor` | Tambor `VFX_OP_Crane_Drum` com `rpm` 5; fardo `VFX_OP_Crane_Load` com `bob` 2,0 (senoide, sobe e desce) |
| 2º guindaste parado com rede de carga pendurada | `op_harbor` | — |
| **Cais vivo** (carga empilhada, redes nos varais, caixas de peixe, balança, cabos nos cabeços, escada de pedra até a água, rampa de barco) | `op_harbor` / `op_props` | — |
| **Armazém aberto** (interior 4) com porta de correr aberta e carga | `op_harbor` | — |
| **Água** (o mar local já rola a textura) | `CeuWano` | Rolagem do `AguaCorrente` mais forte perto do cais (atributo `Velocidade` no marcador `WATER_Sea`, que já existe); espuma rente nas estacas em geometria estática |

- **Sai** o H3 do topo da muralha (U13).
- **Peças móveis:** 13 no total, contando as 9 que já existem.

---

## 6. SUMMON (U10): tema One Piece sem perder o núcleo AMS

**Regra:** a torre aprovada fica intacta (estrela dourada, anéis, corpo, núcleo azul, portas com estrela). Muda só a base e o entorno, que hoje é o terraço genérico do `op_summon`.

| Opção | O que é | Prós | Contras |
|---|---|---|---|
| **A, Convés do Summon (RECOMENDADA)** | O terraço vira **convés de navio pirata**: tabuado em elipse, amurada de madeira com corrimão, **proa** apontando para a praça (oeste) com **carranca** genérica dourada (onda/sol, sem personagem), **2 mastros** laterais com velas recolhidas e **Jolly Roger** do chapéu de palha (iconografia já aprovada no portão OP e na vela do navio), cordame dos mastros até a amurada, **timão** a 9 da torre (fora do raio de interação de 7), **baús** de tesouro, barris, **mesa com mapa** e **rosa-dos-ventos** embutida RENTE no piso | Lê "One Piece" de longe e de perto; usa a iconografia aprovada; não toca na torre | Mais 4–5k tris e ~6 colisões |
| B, Cais do tesouro | Base de pedra de cais com âncora gigante encostada, correntes, baús e mapas | Mais barato | Menos legível como One Piece |
| C, Rosa-dos-ventos / Log Pose | Piso com rosa-dos-ventos grande, globo-bússola em pedestal, mapas | Elegante | Abstrato; o usuário pediu tema, não símbolo |

- **Recomendação:** **A**, com a rosa-dos-ventos da C no piso do convés.
- **As 2 flâmulas atuais da torre** (azul com brasão) saem: entram as Jolly Roger dos mastros. Isso também é U16.
- **Colisão:** amurada como guarda de 4, os mastros, o timão e os baús.

---

## 7. ATMOSFERA (U14): céu rosa-lilás e pétalas

### 7.1 Perfil `[5]` (`AreaAtmosphere`, linha `[5]`; o resto do arquivo não muda)

O ClockTime e a latitude **ficam**: a direção do sol já foi validada no Play e deixa a fachada sul do castelo clara. A ref_03 é luz suave e rosada, não outra hora do dia.

| Propriedade | Hoje | V2 (inicial; ajustar no Play) |
|---|---|---|
| ClockTime / GeographicLatitude | 9,05 / 10 | 9,05 / 10 |
| Brightness / Exposure | 2,4 / −0,05 | **2,2 / 0,0** |
| Ambient / OutdoorAmbient | (138, 146, 164) / (150, 162, 182) | **(150, 136, 168) / (178, 156, 196)** |
| ColorShift_Top | (255, 242, 224) | **(255, 222, 234)** |
| EnvironmentDiffuse / Specular | 0,5 / 0,3 | 0,5 / 0,25 |
| Atmosphere Density / Offset | 0,24 / 0,12 | **0,30 / 0,20** |
| Atmosphere Color / Decay | (190, 216, 246) / (104, 150, 206) | **(238, 198, 228) / (168, 136, 204)** |
| Atmosphere Glare / Haze | 0,12 / 0,8 | **0,30 / 1,7** |
| ColorCorrection Tint | (255, 250, 244) | **(255, 238, 246)** |
| ColorCorrection Saturation / Contrast / Brightness | 0,10 / 0,08 / 0 | **0,14 / 0,05 / 0,0** |

### 7.2 `CeuWano`

| Item | V2 |
|---|---|
| Nuvens | Cover **0,55**, Density **0,6**, Color **(255, 226, 240)** |
| Bloom | 0,40 / 24 / limiar 1,5 (o reboco off-white não estoura; conferir no Play) |
| SunRays | 0,06 / 0,14 |
| Mar | Mantém a cor (48, 176, 196); com o tint ela fica levemente lilás |
| Skybox | Sem skybox novo nesta fase: o rosa vem de Atmosphere + Haze + nuvens. Um skybox lilás próprio exige upload (permissão "Click to share access" + ~90 s, risco de moderação; memória do projeto) e fica como **opcional** se o Play não chegar na ref_03. |

### 7.3 Pétalas
- **Marcadores:** são **10 `FX_Petals_<grupo>`** (`op_vfx`), 1 por grupo de cerejeiras.
  - 2 na avenida, 2 na borda da praça, 1 no oeste, 2 no santuário NE, 1 no pátio do torii, 1 no W3 e 1 no porto.
- **Receita no marcador** (o `OnePieceIsland.emissor()` já lê):
  - `rate` 2,5, `vida` 10, `vel` 1,0, `tam` 0,32;
  - `cor` 255,186,212 → 246,150,186;
  - forma `Box` do tamanho do grupo, `Dist` 200.
- **Orçamento:** com `Dist` 200, ficam ativos ≤ 4 emissores perto do jogador, ou seja ≤ 10 partículas/s e ~100 vivas. Teto de 25/s somando tudo.
- O `FX_Petals_Tree` atual (árvore monumental) **sai**: a copa vira pinheiro.
- **Textura:** a de pétala exige upload (mesmo risco do skybox). Sem ela, usa a padrão tingida (como hoje).

---

## 8. Remoções e miúdos (U7, U13, U15, U16)

**U13:**
- **Sai** o `OP_Lmk_Pagoda` (dono `op_landmarks`). O pináculo oeste vira agulha de rocha com pinheiro no topo, mais baixa: topo de 158 → ~130.
- **Sai** o H3 do topo da muralha (`op_harbor`). A muralha fica limpa com a escada PortoA; o "escritório do porto" desce para o cais (1 piso, integrado ao armazém aberto).

**U15, postes (dono `op_kit` + chamadores):**
- **tōrō de pedra kasuga** (base, haste, caixa de fogo com janelas recortadas, chapéu com cantos levantados, hōju) na praça, no sando e no pátio;
- **andon de poste baixo** (4,5, caixa de papel em kumiko) ao longo das ruas, a cada 18–24;
- **chochin de beiral** nas lojas.
- Sai o poste em T com 2 lanternas.
- Luzes só NightOnly, como hoje.

**U16, bandeiras (≤ 10):**

| Fica | Quantidade |
|---|---|
| Estandartes na face da rocha do castelo (ref_01) | 2 |
| Nobori no pátio do torii | 2 |
| Nobori no torii do santuário | 2 |
| Jolly Roger do convés do summon | 2 |
| Vela/flâmula do navio | 1–2 |

**Saem:**
- 4 estandartes dos cantos da praça + 2 da escadaria M2 (`op_m2_trecho`);
- `BANNERS_E` (`op_plaza`);
- estandartes do `op_props`;
- 2 nobori da ponte (`op_entry.bridge_banners`);
- 2 flâmulas da torre do summon.

`L.BANNERS` fica vazio. Os `COL_OP_PropBanner` saem junto.

**U7, miúdos:**
- **Poço:** bocal de pedra em anel com tampa de madeira, sarilho com eixo, corda e balde, telhadinho com pilares encaixados. Hoje é um cilindro cinza com telhado flutuando.
- **Bancas:** tampo, pernas, travessas e mercadoria apoiada.
- **Pontes do canal (U6):**
  - Canal rebaixado: água a **89,6**, leito colidível a **88,6**.
  - Capa de 0,9 acima do piso **só fora das pontes**.
  - Ponte em **arco**: sobe 1,4 no meio; encontros de pedra fora do vão; 2 degraus de 0,7 por lado.
  - Colisão em 2 rampas + topo.
- **Ponte de saída:** tábuas sem fresta, junta ≤ 0,05 ou tabuleiro contínuo com friso escuro.

---

## 9. COLISÃO V2 (U5, U8): regra e gate (dono: integração, `op_col` + `op_qa`)

1. **Colisão nasce do visual alcançável.** Os 12 polígonos continuam valendo para a praça e as rotas, mas toda superfície visual com normal ≥ 0,7 alcançável (≤ 6 de um piso, ≤ pulo 7,2 acima) colide a ≤ 0,5 abaixo. Isso inclui a pele da borda até o lábio, os topos de rocha baixos, a capa dos canais, os topos de arrimo e mureta e a amurada do navio.
2. **Faixas sem extrapolar:** o `strips` passa a usar o modo `inter` nas arestas diagonais (ou recorta pelo polígono). Acaba o piso dentro da rocha NE e sob as muralhas.
3. **Rocha fechada:** cada massa de `ROCKS` ganha colisão maciça até o topo visual (≤ 6 caixas/cunhas por massa). Topo alcançável = piso com colisão. Topo não alcançável = ≥ 8,5 acima de tudo o que é alcançável.
4. **Guarda nos lábios** (onde a queda leva ao vazio ou ao mar): **8,5 de altura** (pulo de 7,2 + 1,3), no lábio verdadeiro da falésia, não na borda do polígono.
5. **Canais e bacia:** leito colidível 1,0 abaixo da água, degraus de saída nas pontas. Sem buraco até o vazio.
6. **Telhados:** cada água de telhado principal ganha 1 Ramp e a cumeeira 1 Block, em todo telhado a ≤ 7,2 de algo alcançável. Na prática, quase todos na cidade densa: ~150 colisões.
7. **Pé afundando:** ≤ 0,3 entre o piso visual e a colisão (pontes, pátio do castelo, pedras do summon).
8. **Gate `op_qa visual`** (acréscimo pontual no `op_qa`): os raios da auditoria (`audit_rays` + `analyze` + `u5`) rodam a cada build. Para passar:

| Critério | Limite |
|---|---|
| Chão ou rocha alcançável sem colisão | **≤ 20 studs²** (cantos) |
| Telhado alcançável sem colisão | **0** |
| Corpo dentro do modelo | **0** |
| Fresta visual ≥ 0,6 na faixa do jogador | **0** |
| Vão de colisão ≥ 0,6 | **0** |
| Copa | Liberada, mas copa a ≤ 7,2 de um topo alcançável é aviso |

9. **No Studio (lead, V2-4):** conferir o `CharacterJumpHeight` real do jogo. Se não for 7,2, a guarda passa a ser pulo + 1,3 e o gate é rodado de novo.

---

## 10. Orçamento V2

| Dono | Tris | MeshParts | Observação |
|---|---|---|---|
| terrain `OP_Ter_` | 80k | 60 | Bordas, socalcos NE, pináculo sem pagode |
| entry `OP_Ent_` | 26k | 26 | Menos 2 nobori |
| capital `OP_Cap_` | 175k | 150 | **Quadras em fileira**: telhado contínuo por quadra (custo por lote cai), 5 interiores |
| plaza `OP_Plz_` | 22k | 22 | Faixa do eixo rente, sem estandartes |
| castle `OP_Cas_` | 85k | 55 | 5 andares, frontões |
| tree `OP_Tree_` | 40k | 24 | Tronco grosso + pads |
| harbor `OP_Port_` | 42k | 46 | Guindastes, 5 barcos, armazém aberto |
| ship `OP_Ship_` | 30k | 26 | Navio refeito + junco |
| summon `OP_Sum_` | 34k | 30 | Torre ~29k + convés |
| exit / gate_opm | 9k / 7k | 10 / 15 | Tábuas sem fresta |
| landmarks `OP_Lmk_` | 6k | 10 | Sem pagode |
| water `OP_Water_` | 9k | 12 | Canais rebaixados, pontes em arco |
| props `OP_Prop_` | 22k | 30 | Tōrō, andon, poço, bancas, carga |
| vegetation `OP_Veg_` | 45k | 50 | Cerejeiras em cacho, pinheiros de pads |
| **Total estático** | **632k** | **566** | Teto 640k / 650 |
| VFX (`IlhaMovel` + FX) | 6k | 30 | 13 peças móveis |

| Métrica | Hoje | V2 | Teto |
|---|---|---|---|
| Colisões | 743 | ~1.180 (+150 telhados, +120 rochas, +40 canais/bacia, +60 pele/borda, +60 convés/porto, −~25 bandeiras/postes) | 1.300 |
| Luzes de dia | 8 | 12 (5 interiores + salão 3 + summon + portão) | 36 |
| Partículas | — | ≤ 25/s | — |
| Sombra | 260 | ≤ 260 | 260 (já no teto: a quadra contínua reduz MeshParts com sombra) |

---

## 11. Ondas de produção V2 (1 arquivo por agente; ninguém mexe no arquivo de outro)

**Regras de todas as ondas:**
- Blender `--factory-startup`.
- Renders 960 × 540, nos 2 modos (Blender e `FM_MAT_PREVIEW=roblox`).
- 3 voltas de render → crítica ("sobrevive a close na altura do jogador?") → correção.
- Não modelar minérios; não inventar sistemas.
- Proibido: MCP, computer-use, commit e taskkill.

**V2-0, planta e colisão (integração, serial):**
- `op_layout`: `BLOCKS`, `STREETS_V2`, NE novo, canais rebaixados, ponte em arco, `ROCKS` com flag de colisão, `L.BANNERS` vazio.
- `op_col`: seção 9, itens 1–7.
- `op_qa`: gate `visual` (seção 9.8; os scripts da auditoria viram módulo).
- `op_lib`: materiais novos, 1 linha cada (`Roof_OP_Cobalt` 60,90,168; `Roof_OP_Teal` 62,148,138; `Roof_OP_Violet` 104,84,152; `Roof_OP_RedV2` 172,62,52; `Stone_OP_Curb`; `Stone_OP_Gutter`; `Leaf_OP_PinePad` / `Leaf_OP_PineUnder`). Valor conferido na prévia Roblox.
- `op_map`: planta V2.
- **Saída:** blockout V2 com QA de rotas 15/15, gate `visual` verde no blockout e `planta_v2.png`.

**V2-1, GATE DE QUALIDADE DE PERTO (serial, ANTES de espalhar; lição da memória: mostrar a casa-modelo de perto antes de espalhar).** Peças:
- `op_kit` (agente do kit):
  - **quadra-modelo** de 5 lotes geminados com telhados escalonados nas 4 cores;
  - **tōrō, andon e chochin de beiral**;
  - **meio-fio, sarjeta e piso assentado**;
  - **ponte em arco**;
  - **poço**.
- `op_veg` (agente da vegetação): **cerejeira-modelo** e **pinheiro de pads** (o mesmo pad serve à árvore monumental).
- **Trecho:** 1 quadra AvO + metade do leito da avenida + 1 cerejeira + 2 andon.

**Folha do gate:**
- 6 closes na altura do jogador (olho +5,5), a 3–8 da fachada;
- 2 vistas de cima a 30–40, como a câmera do jogo;
- comparação lado a lado com a ref_03 e com as capturas 01/02/04/06/13.

**Aprovação do usuário com essas imagens de perto.** Depois, export do trecho (`OP_EXPORT_ONLY`) + Play pelo lead (escala, cor no Roblox, colisão de telhado, z-fight). **Só então** a V2-3 multiplica.

**V2-2, marcos (paralelo, depois do V2-1 aprovado):**
- `op_castle`: 5 andares, frontões, ishigaki, salão com vida.
- `op_tree`: tronco que abraça, pads.
- `op_summon`: convés A, sem tocar no alias da torre.
- `op_harbor` + `op_ship` (o mesmo agente, 2 arquivos em série): navio, junco, barcos `VFX_*`, guindastes, armazém aberto, H3 fora.

**V2-3, expansão (paralelo, cada um no seu arquivo):**
- `op_capital`: todas as quadras, NE novo, 5 interiores.
- `op_terrain`: bordas que fecham as frestas, socalcos NE, pináculo sem pagode, pele até o lábio.
- `op_water`: canais rebaixados, capa fora das pontes, leito colidível.
- `op_props`: tōrō, andon, bancas, carga, redes; sem estandartes.
- `op_landmarks`: sem pagode; caveira e espada mantidas.
- `op_plaza`: faixa do eixo rente; sem `BANNERS_E`.
- `op_entry`: sem nobori da ponte; postes novos.
- `op_exit`: tábuas sem fresta.
- `op_veg`: espalhar por grupos.
- `op_vfx`: `FX_Petals_*` (10), `VFX_OP_Boat_*`, `Junk`, `Crane_*`.
- `op_lights`: 5 interiores, NightOnly.
- `op_m2_trecho`: o trecho M2 é **absorvido pela quadra-modelo**; o `op_m2_trecho` vira chamador do kit V2 ou é aposentado (decisão no V2-0).

**V2-4, Roblox (lead):**
- backup do place;
- linha `[5]` do `AreaAtmosphere`, `CeuWano` (nuvens e bloom);
- import (o montar novo confere o `EXPORT_ID`);
- `pos_montagem`.

**Testes do V2-4:**

| Teste | Critério |
|---|---|
| **Teste de queda** | Andar e pular toda a borda, canais, NE, telhados, cais e pátio do castelo |
| Rotas | 15/15 |
| Mineração | 70 minérios (aparecer, dano, quebra, recompensa, respawn) |
| Summon | Summon real |
| Portão OPM | Bloqueado e comprado por jogador |
| Travessia | DS ↔ Wano |
| FPS | 60 na praça, no porto, no pátio e na cabeça da ponte olhando a DS |
| Partículas | Contagem viva |

**V2-5, harmonia e otimização:** auditoria na altura do jogador (método AUDITORIA_DS), z-fight, desempenho, limpeza e folhas finais com as mesmas câmeras das capturas do usuário.

---

## 12. Riscos

1. **Cidade densa × desempenho.** Mitigação:
   - quadra = poucas MeshParts (telhado contínuo e fachada por quadra);
   - fundos Tier B;
   - `RenderFidelity` Automatic;
   - sombra só nas fachadas que a câmera vê.
   - Medir o FPS já no trecho do V2-1.
2. **Colisão de telhado e rocha estoura o teto de 1.300.** Mitigação: telhados por quadra (1 Ramp por água contínua, não por lote); rochas em ≤ 6 volumes.
3. **Guarda de 8,5 "parede invisível".** Mitigação: pôr a guarda no lábio real (a pele vira piso) para o jogador andar até a beirada visual. Conferir o `CharacterJumpHeight` real.
4. **Cor das telhas no Roblox.** Cobalto, verde-água e roxo podem empastar no bloom ou no tint rosado. A amostra no Roblox vai no V2-1.
5. **Atmosfera rosa.** Haze 1,7 pode lavar o fundo e tingir a DS vista de Wano. Ajuste no Play. O perfil `[5]` só vale na área 5 (SG e DS intactos).
6. **Textura de pétala / skybox.** Upload exige liberação de permissão e pode cair em moderação silenciosa (memória). Fallback: textura padrão tingida + Atmosphere.
7. **Navio acessível não balança** (colisão estática). Só os barcos não acessíveis e o junco usam `bob`.
8. **NE e marcadores.** O `SAFE_NE` e o `AUDIO_*` do NE mudam de lugar: atualizar no `op_core` (integração) e conferir no `OnePieceIsland`.
9. **Canal rebaixado.** `WATER_CanalW`/`CanalE`, `FX_Weir_*` e a roda d'água mudam de cota. O `op_water` mede e o `op_core._water_measured` regrava (fluxo já existente).
10. **Prazo.** O gate V2-1 pode precisar de 2 rodadas com o usuário: é o ponto de controle que faltou na V1 (o M2 validou só um trecho de rua, não a quadra nem a árvore).
