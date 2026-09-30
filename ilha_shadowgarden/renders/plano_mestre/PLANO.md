# Plano mestre: reforma grande da Ilha 3 Shadow Garden (v4)

Data: 2026-09-30. Etapa de PLANEJAMENTO: nenhum `sg_*.py`, `export_sg.py` ou `studio_sg.py` foi editado.

Diagramas nesta pasta:
- `mundo.png`: o mundo visto de cima, antes e depois;
- `planta_ilha.png`: a planta nova, com rotas e zonas;
- `corte_castelo.png`: corte no eixo, do castelo às salas da masmorra.

Os números saem de `scripts/geo.py` e `scripts/final.py`, uma cópia dos cálculos. O agente da planta pode reaproveitar as constantes.

Convenções:
- **Coordenadas locais** seguem a regra do `sg_layout`: +Y vai para o castelo, +X para leste, Z é a cota absoluta (igual ao Y do Roblox).
- **Coordenadas do Roblox** vêm como (X, Y, Z).
- **Bboxes "sem ilhotas"** usam o contorno do topo do penhasco de cada ilha: `ISLAND_RIM` do `db_layout` e `SHELF_RIM` do `il_layout`, mais as pontes e as ilhotas dos portões.

---

## 0. Decisões em uma página

| # | Pedido | Decisão |
|---|---|---|
| 1 | Castelo pequeno, portas fora de proporção | Castelo **2× em planta e 1,8× em altura**. Salão com 184 × 196 × 84 de interior. Porta principal com **vão de 28 × 34, tímpano até 46 e folhas do tamanho do vão**. Portão da muralha com 24 × 32. |
| 2 | Entrada da dungeon pelo trono | O trono **desliza 27,5 de lado para dentro de um bolso na parede leste** do presbitério e revela um arco de 12 × 18 atrás dele. Esse arco leva a uma **escada caracol**: raio interno 14, degrau útil de 10,5, 60 degraus de 0,8 em 2 voltas, descendo de 54,6 a 6,6. A escada termina na galeria do **Salão Sombrio**, que fica embaixo do castelo: 180 × 248, piso −12, pé-direito de até 58. O portal da masmorra fica no fundo sul desse salão. |
| 2b | Entrada antiga da dungeon | A portaria-caverna do pátio leste **sai**. No lugar entra o **Jardim-Mirante do Luar**. |
| 3 | Salas 3× maiores; bug do selo | R1 passa a **84 × 84** e R2/R3 a **104 × 104**: 3× a área, com pé-direito de 44. As salas ficam **sob o Salão Sombrio**, com piso em −72. O selo e o "portal da próxima sala" ficam **dentro do plano do vão** e são orientados pelo marcador. A barreira de saída por toque é trocada por prompt. |
| 4 | Casas maiores e visitáveis | **7 casas** (eram 11) em 3 tipos: A 32 × 24 com 2 andares, B taverna 38 × 28 e C 24 × 18 térrea. Todas com **vão de porta de 8 × 11 aberto**, interior mobiliado, lareira e escada para o andar de cima quando há. |
| 5 | Ilhas se encostam; portão DS aponta para o lobby | A ilha gira de **67° para 100°** e a ponte de chegada vai de **34 para 232**, com uma curva de 33°. A folga até a Ilha 2 sobe de 130 para **301**; até a bbox dos picos do lobby, de 42 para **261**. A saída vai para a **ponta noroeste** e o rumo da área 4 fica a **3° do radial** (lobby → fora). |
| 6 | Jardim "maquete"; grama "spammada" | Pátio-jardim novo de 200 × 73, com hierarquia de alturas, 2 árvores-marco, 2 espelhos d'água e grama só em bordas e manchas. Grama de **78k para 35k tris**. |

**Tetos novos propostos** (detalhe na seção 5):
- **Superfície:** ≤ 700k tris e ≤ 720 MeshParts. É o que se renderiza junto, menos que os 745k de hoje.
- **Subsolo:** ≤ 160k tris e ≤ 130 MeshParts, visíveis só embaixo da terra.
- **Total estático:** 860k tris e 870 MeshParts. **Precisa da sua aprovação**, porque passa do limite de 800 MeshParts.

---

## 1. Mundo

### 1.1 Situação atual (medida com o `ilha*_data.json` dos exports e os contornos dos layouts)

| Par | Folga hoje (sem ilhotas) |
|---|---|
| Borda da Ilha 3 ↔ borda da Ilha 2 | **130** (vila da Ilha 3 "colada" no cânion) |
| Borda da Ilha 3 ↔ ilhota do portão da Ilha 2 | 29 |
| Borda da Ilha 3 ↔ bbox dos picos do lobby | **42** |
| Portão DS | Em (−694, 44, 349), rumo (0,39; 0; −0,92): aponta para **dentro** da bbox dos picos |

### 1.2 Encaixe novo
A âncora não se move: `ISLAND_NEXT_ANCHOR_ShadowGarden` = (−579,227; 28,2; 650,727).

**Ponte de chegada: 232 no total.**
- 92 em arco de raio 160, virando 33°: sai no rumo da Ilha 2, (−0,9205; 0; −0,3907), e termina no rumo da ilha nova, (−0,985; 0; 0,174).
- Depois, 140 em reta.

**Matriz de encaixe:** `W3 = T(âncora) · Rz(100°) · T(−WORLD_FROM_PREV)`.
- O `WORLD_FROM_PREV` local passa a (−25,81; −561,14), a ponta da ponte. O deck continua em 28,2.
- A polilinha local da ponte está em `final.py`.
- **Conferido:** o `WORLD_FROM_PREV` levado ao mundo cai exatamente em (−579,23; 650,73).

**Ilha nova:** o contorno do topo vai de x −1522 a −804 e de z 511 a 927. O centro fica em (−1163, 719). A área em planta é **2,4×** a de hoje (222k contra 93k studs²).

| Par (sem ilhotas) | Folga nova | Meta |
|---|---|---|
| Borda da Ilha 3 ↔ borda da Ilha 2 | **301** | ≥ 180 |
| Borda da Ilha 3 ↔ ilhota ou ponte da Ilha 2 | 224 / 258 | ≥ 180 |
| Praça da vila ↔ borda da Ilha 2 | 412 | ninguém "colado" |
| Borda da Ilha 3 ↔ Ilha 1 | 666 | ≥ 250 |
| Borda da Ilha 3 ↔ bbox dos picos do lobby | **261** | ≥ 250 |
| Borda da Ilha 3 ↔ montanhas próximas | 742 | – |
| Ponte de chegada ↔ picos | 221 | Não depende do giro: o trecho junto à âncora fixa já está a 221. |

### 1.3 Saída e área 4

| Item | Valor |
|---|---|
| `ISLAND_EXIT_ShadowGarden` | Local (−116, 342, P3 52,2), na ponta noroeste atrás do castelo. Roblox (−1453,0; 52,2; 896,4). |
| Ponte de saída | 64, rumo local de 120° |
| Portão Demon Slayer | Roblox (−1511,2; 52,2; 945,2): o mesmo asset, na ilhota R 22. |
| **`ISLAND_NEXT_ANCHOR_DemonSlayer`** | **(−1532,7; 52,2; 963,2)**, frente **(−0,7660; 0; 0,6428)**, `heading_deg` −140. Deck em **52,2**: a área 4 começa na cota do P3. |
| Direção | A 3° do radial lobby → âncora: aponta para fora do mundo. |
| Espaço para a área 4 | Um disco de raio 300 centrado 350 à frente da âncora fica a mais de 1.000 da Ilha 2, a mais de 1.400 da Ilha 1 e a mais de 1.000 do lobby. As áreas 5 e 6 continuam no mesmo rumo, em céu aberto. |

### 1.4 Efeitos colaterais do mundo
- **Mar:** o `FAR_GROUND` da Ilha 1 (mar em −111) cobre só x de −1024 a 1024. A ilha nova vai até x −1522.
  - Solução: um mar escuro próprio da área 3, criado pelo `CeuSombras` no cliente.
  - Tamanho 2048 × 2048, centrado na ilha, em **−111,5**: meio stud abaixo, para não brigar com o da Ilha 1 onde os dois se sobrepõem.
- **Região da área 3:** o `BoundsCenter` e o `BoundsHalfSize` do `JardimSombrasIsland` têm de cobrir a ilha nova e o subsolo.
  - Y de −80 até 380; a detecção de área usa isso.
- **`VOID_CATCH`:** hoje está em −40 e cortaria as salas.
  - Passa para **−100**, com 800 × 480 centrado na ilha, entre o piso das salas (−76) e o mar (−111).

---

## 2. Planta nova da ilha (ver `planta_ilha.png`)

### 2.1 Tamanho, patamares e rotas
- **Ilha:** cerca de 360 × 720 no local (x ±186, y de −334 a 386). As cotas não mudam: DECK 28,2, P1 36,2, SUM 40,2, P2 44,2 e P3 52,2.

| Faixa (y local) | O que tem |
|---|---|
| −334 a −262 | Pátio baixo (DECK) com o pórtico A, escada Entry de 20 de largura, calçada alta (P1) com o pórtico B, spawn em (0, −268). |
| −300 a −150 (P1) | Praça R 32 com a fonte R 9 (água feita no Roblox), vila baixa (4 casas), rua oeste até a invocação. |
| −150 a −23 (P2) | Escada P1P2 de 18 de largura, vila alta (3 casas), rua do P2 em y −86, alquimia em (112, −86), mirante leste na antiga saída. |
| −23 a −13 | Muralha: 10 de espessura, altura P3+24, portão de 24 × 32 entre 2 torres R 12. A passagem leste fica em x 150. |
| −13 a 60 (P3) | Pátio-jardim de 200 × 73. |
| 60 a 344 (P3) | Castelo 2×. |
| 60 a 380 (P3) | Becos oeste e leste: o oeste é a rota da saída; no leste fica o Jardim-Mirante. Terraço norte e cabeceira da saída na ponta noroeste. |

**Escadas** (espelho ≤ 0,8 e piso ≥ 1,7):

| Nome | Pé | Largura | Degraus |
|---|---|---|---|
| Entry | (0, −310) | 20 | 10 × 1,8 |
| P1P2 | (0, −150) | 18 | 10 × 1,8 |
| Gate | (0, −40) | 20 | 10 × 1,7 |
| EastP3 | (150, −40) | 14 | 10 × 1,7 |
| Summon | (−184, −222) para oeste | 12 | 5 × 1,7 |

Escadas novas, fora do chão:
- degraus do presbitério: 3 × 0,8;
- escada caracol;
- escadaria do Salão Sombrio: 24 × 0,775 em 2 lances de 12, largura 16.

**Rotas para o QA:**

| Rota | Caminho | Distância | Tempo (16 studs/s) |
|---|---|---|---|
| Principal | Chegada → praça → P1P2 → portão → pátio → porta | 340 | 21 s |
| | Porta → trono | 224 | 14 s |
| | Trono → caracol → galeria → escadaria → portal | ~300 | 19 s |
| Secundária | Praça → invocação | | |
| Secundária | Rua do P2 → alquimia | | |
| Secundária | EastP3 → Jardim-Mirante | | |
| Secundária | Pátio → beco oeste → terraço norte → saída | | |
| Secundária | Galeria → passarelas laterais (6,6) → ponte suspensa | | |

### 2.2 Castelo 2×

| Elemento | Hoje | Novo |
|---|---|---|
| Nave (interior) | 96 × 99 × 48 | **184 × 196 × 84** (x ±92, y 66..262, teto P3+84 = 136,2), parede 5 |
| Organização da nave | Salão único, pilastras rasas | **Nave central de 128** + 2 **naves laterais de 24**, andáveis, com capelas e nichos. Arcada de 8 tramos de 22,5 com pilares 4 × 6 em x ±66, fora da MiningZone. |
| Casca externa | ~110 × 106 | 208 × 214 com contrafortes; cumeeira ~228 |
| Fachada | 136 (torre a torre), corpo central 44 | **280**, corpo central **88** |
| Torres da fachada | R 10 em x ±58, topo 142 | **R 20 em (±120, 72), topo 214, agulha 279** |
| Torre-coroa | R 16, topo 196, agulha 232 | **Base 76 × 82** (x ±38, y 262..344) com o presbitério e o poço da escada; fuste octogonal R 30; **topo 311, agulha 376** |
| Porta principal | Vão 16 × 18 | **Vão livre de 28 × 34** com verga reta. **Tímpano ogival até 46** com o emblema. **Arquivoltas de 4 ordens** de 2,5 (moldura externa 48 × 58). Nártex de 16 de fundo. **2 folhas de 14 × 34** de madeira escura com ferragens, abertas 100° e encostadas no nártex. Altura/largura do vão 1,2; com o tímpano, 1,64 (proporção gótica). |
| Portão da muralha | 16 × 18, torres R 7 | **24 × 32** ogival, grade levadiça recolhida (dentes à vista), folhas 12 × 26 abertas, torres R 12 com topo P3+44 |
| Muralha | P3+12 | P3+24, 10 de espessura, passeio com ameias |
| Janelas da nave | 6 × 21, 4 por lado | 10 × 34, 8 por lado (1 por tramo) |
| Alas oeste e leste | Não entráveis | **Saem**: a nave 2× ocupa o lugar e os becos viram rota e jardim |
| Pátio | 92 × 43 | 200 × 73 |

**Mining Hall e minérios**
- **MiningZone:** x ±52, y 80..216, ou seja, **104 × 136**. Centrada na nave central, com 12 livres até os pilares.
  - Marcador: Roblox (−1282,1; 52,2; 748,4), `sx` 104, `sy` 136, `ceil` 136,2.
- **Corredor da porta:** `MINE_DOOR_LANE` = (0, 66..96, meia-largura 8).
- **`ORE_*`:** 80 pontos (2 super, 10 épicos, 24 incomuns, 44 comuns), com a mesma lógica de grade hexagonal centrada.
- **No jogo:** pela curva medida (76 × 78 deu 51, 90 × 89 deu 61), a zona nova daria cerca de 100. **Meta: 90 simultâneos.** Se passar, limitar no `JardimSombrasIsland` (pedido R6).

**Presbitério e trono**

Presbitério:
- **Planta:** y 267..300, 40 de largura, na base da torre-coroa. Piso **P3+2,4 = 54,6**, com 3 degraus a partir da nave.
- **Arco triunfal:** 40 × 60.
- **Rosácea:** R 14, acima do arco.

**Trono novo:**
- 14 × 11 × 20 (1,25× o de hoje), no mesmo desenho de cátedra;
- fica em (0, 294), encostado no **muro do retábulo** (y 300..306).

**Mecanismo:**
- No muro do retábulo, atrás do trono, abre-se o **arco secreto** de 12 × 18.
- Ao ser tocado, **o trono desliza 27,5 para leste** (+X local), em 3 s, para dentro de um **bolso de 14 × 13 × 22** cavado na parede leste do presbitério (x 20,5..35, y 288..300). Por isso a base da torre-coroa tem 76 de largura.
- O que se move: o trono inteiro com o soco, objeto `SG_Hall_ThroneMov`, e a colisão dele. Nada mais se mexe.
- Com o trono recolhido, o arco fica livre e leva ao patamar de topo da escada caracol, em 54,6.

**Escada caracol**
- **Poço:** centro (0, 322), dentro da torre-coroa. Raio interno 14 e parede de 4 (externo 18). Núcleo R 3.
- **Degraus:** de R 3 a R 13,5, o que dá **10,5 de degrau e ~10 livres** com o corrimão. Cabem 2 ou 3 avatares lado a lado.
- **Descida:** 60 degraus de 0,8 a 12° cada, **2 voltas**, de **54,6 a 6,6** (−48).
- **Piso na linha de passo** (R 8,5): 1,78. No R 4, 0,84 (íngreme, mas o Humanoid anda).
- **Pé-direito entre voltas:** 24.
- **Colisão:** rampa helicoidal em 30 cunhas de 24°. O andador do QA desce e sobe.
- **Sentido:** horário na descida. O patamar de baixo sai pelo sul, direto na galeria.
- **Visual dividido em z 44:**
  - acima de 44, a casca da torre é do `sg_castle`;
  - abaixo, a "Torre do Poço" é do `sg_cave`: cilindro de cantaria com arcos abertos, e a última volta fica à vista de dentro do salão.

**Salão Sombrio** ("Cova da Ordem", a bat-caverna; módulo novo `sg_cave.py`, prefixo `SG_Cave_`)

**Volume**
- Interior x ±90, y 88..336 (**180 × 248**), embaixo da nave e do presbitério.
- Piso principal **−12** (água em −14/−18); galeria de chegada **6,6**.
- Abóbada irregular de rocha **até 46**: pé-direito de até 58, com 6 de laje sob o piso do castelo (52,2).

**Circulação**
- **Galeria** (y 290..336, x ±60): balcão de ferro em volta do pé da Torre do Poço.
- **Escadaria** no eixo: 2 lances de 12 × 0,775, patamar de 6, largura 16. Desce de y 290 até o piso em y ~241.
- **Passarelas de ferro** a 6,6 nas paredes leste e oeste, até y 150, ligadas por uma **ponte suspensa** em y 200. Os 4 **estandartes rasgados** da ordem pendem dela.

**Elementos**
- **Água escura:** rio subterrâneo de y 196 a 220, com ponte de pedra no eixo (largura 16).
  - Uma queda d'água sai de uma fenda nordeste.
  - Os dois são água do Roblox, com os marcadores `WATER_CavePool` e `WATER_CaveFall`.
- **Pedra bruta:** colunas de basalto hexagonais (a assinatura da ilha) nas paredes. As estalagmites ficam só junto das paredes, fora das rotas.
- **Estalactites:** ~50 instâncias no teto, Tier C.
- **Cristais:** violeta, **engastados** nas paredes e no teto, acima de piso+12, só em volta do portal. Nunca soltos no chão, para não parecer minério.
- **Forja/oficina secreta:** plataforma oeste (x −88..−50, y 140..220, +1,6) com fornalha e chaminé para a rocha, bigorna, bancada, cabides de armas e baú. É a única luz quente.
- **Sala do Mapa:** plataforma leste (x 50..88, y 140..220) com a mesa do mapa (maquete da ilha), armários de relíquias e cabides de armaduras.

**Portal e UI**
- **Portal da masmorra** no fundo sul: `DUNGEON_Hall` em (0, 104), estrado −10,4 com 2 degraus.
- Anel e vórtice de Ø 26, emoldurados por um arco natural de basalto.
- **UI de horário:** `DUNGEON_UI`, placa em z 22 sobre o arco, virada para o norte.

**Luzes (6):** portal (violeta), forja (quente), sala do mapa (quente), 2 frias de cristal e a lanterna da galeria.

**Salas da masmorra 3×**

**Layout**
- Fila no eixo local Y, sob o Salão Sombrio:
  - **R1:** x ±42, y 6..90 (84 × 84);
  - **R2:** x ±52, y 92..196 (104 × 104);
  - **R3:** x ±52, y 198..302.
- **Piso −72, teto −28** (44). Paredes de 2.
- **Vãos de ligação:** 28 × 22 em y 91 e y 197.
- **Nicho de portal:** 28 × 22 no muro norte da R3 (y 302..304).

**Proporção**
- Área: 3,06× na R1 e 3,0× na R2/R3.
- Altura: 1,5×, porque 44 com vão de 104 lê bem como abóbada.

**Minérios** (23 por arena, eram 17):
- centro;
- 6 pontos a R 16;
- 10 a R 30 (0/30/60/120/150/180/210/240/300/330°);
- 6 a R 42 (0/40/140/180/220/320°).
- Os ângulos de 90° e 270° ficam livres: é o eixo dos vãos.
- `DUN_SPAWN_CLEAR` sobe de 10 para 14.

**`DUN_KEEP_OUT`** = (−56, 2, −76, 56, 306, −26).

**Entrada e retorno**
- O portal teleporta para a R1, logo embaixo dele.
- `DUNGEON_Return` fica no Salão Sombrio, na frente do portal.

**Correção do bug "barreira que teleporta está para fora"**
- **Causa medida no código e nos marcadores:**
  - o `MasmorraSaida` é criado com `CFrame.new(pos)`, alinhado aos eixos do MUNDO e com `Size` (2, 13, 12);
  - a ilha está girada 67° + 180°, então os 12 de largura ficam ~23° do **eixo** da sala em vez do plano da parede;
  - a 4 da parede leste da R3, a folha avança 5,9 ao longo do eixo e atravessa a parede de 2 até a face externa.
- **O `MasmorraSelo`** usa `lookAt` e está orientado certo. Mas o jogador vê o selo e o portal de saída juntos e os dois leem como "o portal da próxima sala".
- **O `GIRO` fixo** (−90° no mundo) também gira os jogadores para o lado errado no teleporte.
- **Plano:**
  - todo objeto de jogo nasce com o CFrame do marcador (atributos `fwd_x`/`fwd_z`);
  - o "portal da próxima sala" é um marcador próprio **no plano médio da parede, dentro do vão** (`DUN_NEXT_*`, w 27 × h 21 × t 1);
  - a saída vira ProximityPrompt, sem barreira de toque (seção 3).

**Vila: 7 casas visitáveis**

| Casa | Tipo | Lote (x, y) | Tamanho | Frente | Patamar | Papel |
|---|---|---|---|---|---|---|
| H1 | B taverna | (−92, −262) | 38 × 28 | Norte (rua da invocação) | P1 | Estalagem da Lua Negra |
| H2 | A | (−100, −180) | 32 × 24 | Sul | P1 | Ferreiro |
| H3 | A | (96, −262) | 32 × 24 | Norte | P1 | Boticário |
| H4 | C | (104, −180) | 24 × 18 | Sul | P1 | Tecelã |
| H5 | A | (−66, −114) | 32 × 24 | Norte (rua do P2) | P2 | Cartógrafo |
| H6 | C | (−122, −58) | 24 × 18 | Sul | P2 | Guarda da ordem |
| H7 | A | (−62, −56) | 32 × 24 | Sul | P2 | Casa do mestre de armas |

**Lotes e fachadas**
- Lote = casa + 8 de lado e 7 de frente e fundo, com jardim dirigido.
- Fachadas em meia-enxaimel, no mesmo kit refeito do overhaul 02, com escala 1,5×.
- Beirais em ~14 (C) e ~27 (A e B); cumeeiras ~22 (C) e ~38 (A e B). Das ruas, dão impacto.

**Porta:** todas com **vão livre de 8 × 11**, soleira de 0,4 e folha aberta presa na parede de dentro. Nenhuma porta falsa.

**Programas de interior**

- **A (2 andares, 30 × 22 livres):**
  - térreo com pé-direito de 12;
  - sala com lareira de pedra na empena;
  - mesa de 4 lugares e bancos, aparador com louça e a bancada do ofício da casa;
  - escada em U com 2 lances de 8 degraus de 0,81 × 1,7 e 5 de largura, no canto do fundo (bloco de 11 × 20);
  - andar de cima com 12 até o frechal e forro aberto até as tesouras: 2 quartos (cama, baú, guarda-roupa), guarda-corpo no vão da escada e sacada de janela.
- **B taverna (36 × 26 livres):**
  - salão de pé-direito 14 com mezanino em U de 6 de largura em 3 lados;
  - balcão, 6 mesas, barris, lareira monumental e lustre de ferro;
  - escada reta de 6 de largura com 18 degraus de 0,8 ao longo da parede lateral;
  - no mezanino, 3 quartos pequenos.
- **C térrea (22 × 16 livres):**
  - 12 até o frechal, forro aberto até a cumeeira;
  - lareira, cama em alcova, mesa, fogão e prateleiras;
  - sem sótão acessível e sem escada de mão falsa.

**Técnica**
- **Pé-direito:** de 12 nas casas. O brief pede 14 para prédio entrável; proponho a exceção para casas, porque a câmera cabe e com 14 a escada não cabe.
- **Colisão:** paredes em caixas com o vão da porta, lajes e escadas em rampa; mesa, balcão e cama colidíveis; objetos pequenos sem colisão.
- **Luz:** real (lareira) só em H1, H2, H5 e H7. Nas outras, brilho Neon na grelha da lareira e janelas quentes.
- **Objetos:** o interior de cada casa vai num objeto próprio, `SG_Vil_Int_H<n>`, para o corte por distância no cliente.

**Alquimia, invocação, fonte e saída**
- **Alquimia:** o módulo não muda; só se reposiciona em (112, −86), com a porta a oeste para a rua do P2. Roblox (−1071,1; 44,2; 597,5).
- **Invocação:** plataforma R 24 em (−208, −222) e torre em (−216, −222), virada para +X. Ponte de 12 a partir da rua da praça. Roblox (−880,2; 40,2; 896,9).
- **Fonte:** bacia R 9 no centro da praça R 32. A água é feita no Roblox, pelo marcador que o agente de água definir.
- **Saída:** beco oeste (P3, ≥ 25 livres fora da torre da fachada) → terraço norte → cabeceira em (−116, 342) → ponte de 64 a 120° → ilhota R 22 com o portão DS.

**O que sai e o que entra**
- **Sai:**
  - portaria-caverna da dungeon (`SG_Dun_Cave_*`, `SG_Dun_Approach_*`, `SG_Dun_House_Portal`: ~28k tris e 37 MeshParts);
  - alas do castelo;
  - ponte de saída leste e ilhota antiga;
  - 4 das 11 casas;
  - ilhotas do céu (outro agente);
  - água modelada no Blender (outro agente).
- **Entra no lugar da portaria** (P3 leste, ~(130, 170)): **Jardim-Mirante do Luar**.
  - Terraço com balaustrada de pedra na borda e banco em êxedra.
  - 1 árvore velha inclinada (a árvore-marco da lua) e 3 pinheiros.
  - 1 lanterna no nó do caminho.
  - A massa de rocha em estratos fica reduzida à falésia da borda, como moldura.
  - Vista para leste: a Ilha 2 ao longe, já separada.
- **Na antiga saída leste (P2):** mirante leste pequeno, com parapeito e banco.

**Pátio-jardim (fim da "maquete")**

**Causas de ler como maquete:** tudo na mesma altura, espaçamento uniforme, sebes de brinquedo, grama igual em toda parte e nada com escala maior que o jogador.

**Plano**
- **Eixo processional:** 20 de lajes, do portão à porta.
- **Canteiros:** 2 **gramados rebaixados 1,2**, com murete de cantaria e degraus nas pontas.
- **Espelhos d'água:** 2 retangulares de 20 × 32, que refletem a fachada (marcadores de água).
- **Árvores-marco:** **2** (teixo ou cipreste escuro de 30–36 de altura). É a escala que falta.
- **Caminhos:** saibro nas bordas, com desgaste.
- **Musgo:** no pé dos muros.
- **Sebes:** só nas quinas.
- **Plantio:** flores em manchas irregulares junto das árvores e dos degraus.
- **Estátuas:** 2 da ordem, no pé da escada da porta.
- **Lanternas:** só nos nós.

**Grama** (78k → 35k):
- tufos só a 1,5–3 das bordas, caminhos e muros, e em manchas junto das árvores;
- o gramado aberto é chão liso de `Grass_SG`;
- nada de tufos a mais de 120 das rotas.

---

## 3. Marcadores

Posições Roblox calculadas com o encaixe novo. A frente é o vetor `fwd` que o export grava (`fwd_x`, `fwd_z`).

### 3.1 Que mudam de lugar (mesmo nome)

| Marcador | Local (x, y, z) | Roblox | Observação |
|---|---|---|---|
| `WORLD_FROM_PREV` | (−25,8; −561,1; 28,2) | (−579,2; 28,2; 650,7) | Igual no mundo; muda só no local |
| `WORLD_ENTRY_ShadowGarden` | (0, −268, 36,4) | (−872,4; 36,4; 676,2) | frente (−0,985; 0; 0,174) |
| `PATH_ENTRY_CENTER(_nn)` | eixo | – | Waypoints novos até (0, 96, P3) |
| `ISLAND_EXIT_ShadowGarden` | (−116, 342, 52,2) | (−1453,0; 52,2; 896,4) | Cota P3 |
| `ISLAND_NEXT_ANCHOR_DemonSlayer` | – | **(−1532,7; 52,2; 963,2)** | frente (−0,766; 0; 0,643), deck 52,2 |
| `GATE_DemonSlayer*` | – | (−1511,2; 52,2; 945,2) | Mesmo asset |
| `MiningZone_ShadowGarden` | (0, 148, 52,2) | (−1282,1; 52,2; 748,4) | `sx` 104, `sy` 136, `ceil` 136,2 |
| `ORE_*` (80), `GP_Block_*` | Salão | – | Grade nova; anel "borda" nas faces da MiningZone |
| `SUMMON_*` | (−216, −222, 40,2) | (−880,2; 40,2; 896,9) | |
| `CRAFT_*`, `NPC_Craft` | (112, −86, 44,2) | (−1071,1; 44,2; 597,5) | |
| `DUNGEON_Entrance` | (0, 114, −10,4) | (−1248,6; −10,4; 742,5) | Prompt "Entrar" (≤ 14 do portal) |
| `DUNGEON_UI` | (0, 103, 22) | (−1237,8; 22; 740,6) | Placa sobre o arco do portal, virada para o norte |
| `DUNGEON_Return` | (0, 134, −11,8) | (−1268,3; −11,8; 746,0) | Volta ao Salão Sombrio |
| `DUNGEON_Spawn` (R1) | (0, 18, −71,8) | (−1154,0; −71,8; 725,9) | frente +Y local = (−0,985; 0; 0,174) |
| `DUN_ROOM_R1/R2/R3` | (0, 48 / 144 / 250, −72) | (−1183,6 / −1278,1 / −1382,5; −72; 731,1 / 747,8 / 766,2) | `sx`/`sy` 84 ou 104, `floor` −72, `ceil` −28 |
| `DUN_SPAWN_R2`, `DUN_SPAWN_R3` | (0, 102 / 208, −71,8) | (−1236,8 / −1341,2; −71,8; 740,5 / 758,9) | frente +Y local |
| `DUN_LINK_R1R2`, `DUN_LINK_R2R3` | (0, 91 / 197, −72) | (−1225,9 / −1330,3; −72; 738,6 / 757,0) | `w` 28, `h` 22, `t` 2; **frente = eixo das salas** |
| `DUN_EXIT_R1` | (−30, 10, −72) | (−1141,0; −72; 754,0) | Prompt "Sair" |
| `DUNGEON_ExitPortal` | = `DUN_EXIT_R3` | – | Mantido como alias; sem barreira de toque |
| `DUN_ORE_<sala>_<RAR>_<nn>` | 23 por arena | – | Anéis de 16, 30 e 42 |
| `AUDIO_DungeonPortal`, `AUDIO_DungeonRooms`, `AUDIO_HallAmbience` | Portal do salão / salas / nave nova | – | |
| `SAFE_*` | – | – | Lista nova em `export_sg.safe_candidates` (inclui `SAFE_Cova` e `SAFE_Terraco_N`) |

### 3.2 Novos

| Marcador | Local (x, y, z) | Roblox | Representa |
|---|---|---|---|
| `THRONE_Rest` | (0, 294, 54,6) | (−1425,9; 54,6; 773,8) | Pivô do trono em repouso; frente = nave (0,985; 0; −0,174) |
| `THRONE_Park` | (27,5; 294; 54,6) | (−1430,6; 54,6; 746,7) | Pivô do trono recolhido no bolso |
| `THRONE_Interact` | (0, 284, 54,6) | (−1416,0; 54,6; 772,1) | Prompt "Tocar o trono", na frente do soco |
| `THRONE_OpenZone` | caixa x ±9, y 280..312, z +14 | – | Onde o trono não pode fechar se houver jogador |
| `THRONE_Stair_Top` | (0, 308, 54,6) | (−1439,6; 54,6; 776,2) | Patamar de topo, dentro do arco; prompt de baixo "Abrir passagem" |
| `THRONE_Stair_Bottom` | (0, 300, 6,6) | (−1431,7; 6,6; 774,9) | Saída da escada na galeria (QA e spawn seguro) |
| `THRONE_Return` | (0, 276, 54,6) | (−1408,1; 54,6; 770,7) | Destino do atalho "Subir" (opcional) |
| `CAVE_Zone` | centro (0, 212, −12), `sx` 180, `sy` 248, `h` 60 | (−1345,1; −12; 759,6) | Reverb Cave e corte do subsolo no cliente |
| `CAVE_Stair_Up` | (14, 128, −12) | (−1264,8; −12; 731,2) | Prompt "Subir ao salão" → `THRONE_Return` (opcional) |
| **`DUNGEON_Hall`** | (0, 104, −10,4) | (−1238,7; −10,4; 740,8) | **Portal da masmorra no Salão Sombrio**; frente = norte (−0,985; 0; 0,174) |
| `DUNGEON_Portal` | = `DUNGEON_Hall` | – | Alias: o `JardimSombrasIsland` põe as partículas nele |
| `DUN_NEXT_R2` | (0, 197, −72) | (−1330,3; −72; 757,0) | Portal da próxima sala **no plano médio do vão R2R3**: `w` 27, `h` 21, `t` 1, frente = eixo |
| `DUN_NEXT_R3` | (0, 303, −72) | (−1434,7; −72; 775,4) | Idem, no **nicho** do muro norte da R3 |
| `DUN_EXIT_R3` | (−44, 204, −72) | (−1329,6; −72; 801,5) | Prompt "Sair" da R3, no muro oeste; frente +X local |
| `WATER_CavePool`, `WATER_CaveFall`, `WATER_Court_L/R`, `WATER_Fountain` | – | – | Para o agente de água (os nomes finais são dele) |
| `AUDIO_Cave`, `AUDIO_Forge` | – | – | Família wind/fire |

### 3.3 O que o `DungeonService` precisa (lista para você)
1. **`cfMarcador(nome)`:** `CFrame.lookAt(pos, pos + Vector3.new(fwd_x, 0, fwd_z))`.
   - Todo objeto criado (selo, portais, âncoras de prompt) e todo teleporte usam esse CFrame.
   - **Sai o `GIRO` fixo:** `teleportar(p, cf)` recebe um CFrame.
2. **Selo e portal da próxima sala, um objeto por arena:**
   - `DUN_NEXT_<salaFisica>`: `Part` `Size(w, h, t)`, `CFrame = cfMarcador * CFrame.new(0, h/2, 0)`;
   - **fechado** durante a sala: colidível, escuro, `Transparency` 0,55;
   - **aberto** quando a sala limpa: `CanCollide` desligado, `CanTouch` ligado, brilho;
   - `Touched` de um participante:
     - se `corrida.transicao`, chama `iniciarSala(sala + 1)` na hora (só uma vez: confere corrida, sala e transição);
     - quem tocou vai para `DUN_SPAWN` da sala nova;
     - os outros seguem a regra de hoje (teleporte do grupo) quando a sala nova começa;
   - o `task.delay(TRANSICAO)` continua como garantia. Sugestão: **TRANSICAO 4 → 8 s**, para dar tempo de andar até o portal.
   - Sai o `criarSelo` baseado em `DUN_LINK_R2R3` com `lookAt` entre salas. O `DUN_LINK_*` continua sendo o vão físico (geometria).
3. **Saídas só por prompt:** `DUN_EXIT_R1` e `DUN_EXIT_R3` ("Sair", hold 0,6).
   - **Sai a peça `MasmorraSaida` com `Touched`** (a barreira que ficava para fora).
   - As espirais `SG_Dun_R3_ExitSpiral*` passam a ser o visual do `DUN_NEXT_R3`: acendem em transição.
4. **Entrada:** `DUNGEON_Entrance` fica no Salão Sombrio. O `S.entrar` não muda: continua exigindo ≤ 14 do marcador.
5. **Config (`AlquimiaConfig.Masmorra`):** `SELO` = {27, 21, 1}; `TEMPO_SALA` 150 → **180** (salas 3×: sugestão, você decide); `TRANSICAO` 8.
6. **Mensagem da UI:** a faixa da `AlquimiaUI` diz "torre ao lado do castelo". Passa a dizer "desça pelo trono do castelo".
7. **Streaming:** antes de cada teleporte para uma sala, chamar `player:RequestStreamAroundAsync(pos)`. As salas ficam a ~60 do portal, mas o modelo do subsolo pode estar recolhido no cliente.

### 3.4 O que o script do trono precisa (`TronoService`, ModuleScript novo em `Core`, ligado pelo `SistemasShadowGarden`)
1. **Peças móveis:**
   - todas as `BasePart` com nome `^SG_Hall_ThroneMov` e a colisão `COL_SGHallThroneMov_*`;
   - o export as põe num `Model` próprio, sem a tag `IlhaMovel` (prefixo diferente de `VFX_`);
   - a translação é `THRONE_Park − THRONE_Rest`, 27,5 ao longo de +X local.
2. **Estado no servidor, igual para todos:**
   - atributo `TronoAberto` no modelo da área;
   - tween de 3 s (Quad InOut) das peças por CFrame;
   - `CanCollide` desligado durante o movimento e ligado no repouso;
   - som de pedra arrastando e um tremor leve de câmera no cliente, a até 40.
3. **Abrir:**
   - prompt em `THRONE_Interact` ("Tocar o trono", hold 0,5, distância 10);
   - prompt em `THRONE_Stair_Top` para quem sobe ("Abrir passagem");
   - aberto automaticamente enquanto `MasmorraEstado.Estado` ∈ {COUNTDOWN, ENTRY_OPEN}.
4. **Fechar:**
   - 20 s depois da última abertura, só se não houver nenhum `HumanoidRootPart` em `THRONE_OpenZone` (verificação a cada 1 s);
   - se houver, adia.
   - Nunca fecha com alguém no caminho: se alguém entrar durante o tween de fechar, inverte o tween.
5. **Atalho "Subir" (opcional):** prompt em `CAVE_Stair_Up` teleporta para `THRONE_Return` e abre o trono, para ninguém ficar preso.

### 3.5 Outros scripts do Roblox
- **`JardimSombrasIsland`:**
  - `BoundsCenter`/`HalfSize` novos, cobrindo o subsolo;
  - **`OreMax` ~90** no salão;
  - alias do `DUNGEON_Portal` para as partículas;
  - `PASSO_HEX` igual.
- **`CeuSombras`:**
  1. mar escuro próprio em −111,5;
  2. reverb Cave dentro de `CAVE_Zone`;
  3. **corte do subsolo:** o modelo `SUBSOLO` (Salão Sombrio + salas) fica fora do workspace do cliente enquanto `HRP.Y > 46` e o jogador está a mais de 40 do eixo do poço. Ele volta ao entrar no arco ou no teleporte;
  4. **interiores das casas:** `SG_Vil_Int_*` somem a mais de 90.
- **`DragonBallIsland`:** não muda (a âncora é a mesma). Conferir se o `PortoesDeIlha` não tem posição fixa da saída antiga da área 3.

---

## 4. Orçamento

**Estado hoje** (export 58cdd0bf):
- 745k de 750k tris estáticos;
- 766 de 800 MeshParts;
- 105 de 130 materiais;
- 30 de 42 luzes;
- 749 colisões;
- FPS: 60 no geral, 56 na vila.

**Estimativa** (a grama cai para ~35k; ilhotas e água do Blender saem):

| Camada | Zona (dono) | Hoje (tris / MeshParts) | Proposto (tris / MeshParts) | Como |
|---|---|---|---|---|
| Superfície | terrain | 48k / 92 | **72k / 115** | Ilha 2,4×; basalto em módulos maiores; penhasco inferior e quilha em Tier C; ilhotas fora (−3k) |
| | entry | 34k / 32 | 40k / 38 | Ponte de 232 com tramo repetido (1 objeto MB por função) e um pilar-marco no meio |
| | village | 90k / 94 | **100k / 108** | 7 casas, ~11,5k cada, interior incluído (exterior 7k + interior 4,5k); mobília instanciada; fachadas laterais e de fundo simplificadas |
| | castle | 145k / 100 | **170k / 125** | Escala não custa triângulo. O silhar e o detalhe só na faixa do jogador (piso a +24) e nos portais; acima, fiadas grandes (Tier B/C). Sem alas (−21k). |
| | hall | 64k / 46 | 80k / 58 | Arcada de 16 pilares, naves laterais, abóbada maior e trono novo |
| | craft | 81k / 60 | 84k / 62 | Não muda (outro agente) |
| | summon | 29k / 44 | 29k / 44 | Só muda de lugar |
| | exit | 24k / 31 | 26k / 34 | Cabeceira noroeste |
| | gate_ds | 10k / 17 | 10k / 17 | – |
| | water | 5,5k / 22 | 3k / 10 | Quedas e fonte vão para o Roblox |
| | vegetation | 97k / 75 | **58k / 62** | Grama 82k → 35k; jardim do pátio novo +6k |
| | props | 20k / 42 | 22k / 45 | – |
| | **Total superfície** | 745k / 766 | **~691k / ~718** | |
| Subsolo | **cave** (novo) | – | **70k / 60** | Rocha em massas (Tier C); estalactites instanciadas; detalhe só na galeria, portal, forja e mapa |
| | dungeon | 91k / 89 | **78k / 64** | Sai a portaria (−28k / −37). Salas 3× com o mesmo número de elementos em tramos maiores (+15k). |
| | **Total subsolo** | – | **~148k / ~124** | |
| | vfx | 6k / 22 | 14k / 32 | Trono móvel |
| | **Total estático** | 745k / 766 | **~839k / ~842** | |

**Tetos propostos** para o `ER.BUDGET` e o `studio_sg.BUDGET`:

| Item | Hoje | Proposto |
|---|---|---|
| `static_tris` | 750k | **860k** (superfície ≤ 700k, subsolo ≤ 160k) |
| `static_meshes` | 800 | **870** (superfície ≤ 720, subsolo ≤ 130) |
| `total_tris` / `total_meshes` | 768k / 850 | 880k / 910 |
| `materials` | 130 | 130 (estimado 116: cave +6, casas +4, castelo +1) |
| `shadow_meshes` | 320 | 320 (subsolo sem sombra, fora as massas grandes) |
| `day_lights` | 42 | **48** (estimado 44: cave 6, casas 4) |
| `col` | 1800 | 1800 (estimado ~1.050: rampa helicoidal 30, casas ~150, cave ~200) |

- **Condição dos tetos novos:** o corte do subsolo e dos interiores no cliente (seção 3.5). Com ele, o que se renderiza na superfície fica em ≤ 700k e ≤ 720, **abaixo de hoje**.
- **Meta:** ≥ 58 FPS na vila (hoje 56, e a grama cai 47k) e 60 no resto. Medir com o mesmo protocolo de `_audit/PERF_BASELINE.md`.
- **Se 800 MeshParts for inegociável:**
  - fundir materiais por objeto: cave 60 → 45, castle 125 → 110, village 108 → 95, terrain 115 → 105;
  - no fim fica em ~790, com mais atlas de material e menos variação.

---

## 5. Ordem de construção (ondas; nunca dois agentes no mesmo arquivo)

**Pré-requisito:** os agentes que estão agora em `sg_emblem`, `sg_craft`, `sg_hall`, `sg_court`, `sg_water`, `sg_entry`, `sg_scene` e `sg_core` terminam e as mudanças deles entram primeiro.

**Onda 0: planta e contratos** (1 agente, serial; é o dono da integração)
- **Arquivos:**
  - `sg_layout.py` v4: todas as constantes deste plano, `world_matrix` com o giro de 100 e o `WORLD_FROM_PREV` novo, a polilinha da ponte e `DUN_*`, `CAVE_*`, `THRONE_*`, `STAIR_*` e `KEEP_OUT`;
  - `sg_col.py`: pisos, escadas, guardas, rampa helicoidal, galeria, escadaria e pontes da cova;
  - `sg_core.py`: todos os marcadores da seção 3;
  - `sg_blockout.py`: volumes 2×, cova e salas;
  - `sg_map.py`;
  - `sg_qa.py`: rotas novas e os testes `CAVE_LIVRE` e `ESCADA_CARACOL`, com o andador descendo e subindo os 60 degraus;
  - `studio_sg.py`: zona `cave` e `BUDGET` novo;
  - `export_sg.py`: dono `cave` (`SG_Cave_`), coleção `19_CAVE`, modelo `SUBSOLO`, `VOID_CATCH` em −100, `SAFE_*` e `BUDGET` novos.
- **QA:**
  - `ROTAS`, `SONDAS`, `SALAO_LIVRE` (MiningZone nova), `DUNGEON_LIMPA` (salas novas), `CAVE_LIVRE` e `ESCADA_CARACOL` OK;
  - export em modo seco imprimindo `CONEXAO`, com `WORLD_FROM_PREV` = âncora exata;
  - 6 renders do blockout (geral, fachada, praça, trono, cova e sala R2).
- **Portão do usuário:** você aprova o blockout antes da Onda 1. É barato corrigir aqui.

**Onda 1: módulos grandes** (7 agentes em paralelo, cada um no seu arquivo)

| Agente | Arquivos | Escopo | Fronteira com os outros |
|---|---|---|---|
| 1a | `sg_castle.py` | Casca 2×, porta e portão novos, muralha, torres, torre-coroa com o bolso do trono e o poço acima de z 44 | O poço abaixo de 44 é do 1c; o interior é do 1b |
| 1b | `sg_hall.py` | Interior 2×, arcadas, naves laterais, presbitério, arco secreto, `SG_Hall_ThroneMov` como objeto separado | O trono é o único objeto móvel da zona |
| 1c | `sg_cave.py` (novo) | Salão Sombrio completo, Torre do Poço abaixo de 44, galeria, escadaria, passarelas, forja, mapa, portal | Não toca nas salas (1d) |
| 1d | `sg_dungeon.py` | Tira a portaria; salas 3×, vãos com o nicho dos portais `DUN_NEXT` e saídas | – |
| 1e | `sg_village.py` + `sg_village_int.py` (novo) | 7 casas: exterior e interior | Praça e ruas ficam neste agente |
| 1f | `sg_terrain.py` | Ilha nova, quilha rochosa até −108 contendo a cova e as salas (seção do subsolo ≥ 120 × 320 em z −80), falésias e rocha do Jardim-Mirante | – |
| 1g | `sg_entry.py` + `sg_exit.py` | Ponte curva de 232 com pórticos; saída noroeste, cabeceira e ilhota | – |

**QA de cada agente da Onda 1:**
- `studio_sg <zona>` com `ROTAS`, `SONDAS`, `SALAO_LIVRE`, `DUNGEON_LIMPA`, `CAVE_LIVRE`, `BUDGET` da zona e técnico com 0 degeneradas;
- 3 voltas de render, crítica e correção, nos dois modos (prévia e `FM_MAT_PREVIEW=roblox`).
- **O 1b renderiza o trono nas 2 poses:** repouso e recolhido.

**Onda 2: ambientação e reposicionamento** (paralela, depois da Onda 1)
- `sg_garden.py` + `sg_court.py` (1 agente): pátio-jardim novo, grama 35k, Jardim-Mirante.
- `sg_summon.py`, `sg_craft.py` e `sg_water.py`: só reposicionar e ajustar a base. O `sg_craft` fica com o agente da alquimia, se ainda estiver ativo.
- `sg_props.py`, `sg_lights.py` e `sg_veg.py` (1 agente): lanternas nos nós, luzes da cova e das casas, pinheiros.
- **QA:** por zona, como na Onda 1.

**Onda 3: integração** (1 agente, serial)
- `sg_scene` / `build_sg` completo.
- `sg_qa` inteiro, `BUDGET` global, técnico.
- 360° nos 2 modos, folhas de antes e depois (`tools_sheet.py`).
- Export com `SG_BUDGET=strict`.

**Onda 4: Roblox** (só quando você liberar o Studio)
- Importar e montar.
- Scripts: `DungeonService`, `TronoService`, `CeuSombras`, `JardimSombrasIsland`, `AlquimiaConfig`, `AlquimiaUI`.
- **Testes no Play:**
  - chegada pela ponte;
  - trono abrindo e fechando com jogador no caminho;
  - descida e subida da caracol;
  - entrada no portal;
  - salas 1 → 2 pelo portal `DUN_NEXT` e pelo tempo;
  - saídas por prompt;
  - volta ao Salão Sombrio;
  - saída noroeste até a ilhota;
  - FPS na vila, no salão e na cova.
- **O place não é salvo pelo agente.**

---

## 6. Riscos, suposições e dúvidas

**Suposições** (sigo com elas):
1. **"Dobrar"** = 2× em planta e 1,8× em altura: agulha da torre-coroa em 376. Com 2× também na altura, ela vai a ~412 e a massa pesa mais sobre a vila.
2. **Casas** com pé-direito de 12, exceção ao "≥ 14 para prédio entrável". Com 14, a escada em U não cabe.
3. **Número de minérios:** o jogo decide pela zona. A meta é ~90 simultâneos no salão, com teto `OreMax` se passar.
4. **A área 4 começa na cota 52,2** (P3). Ela ainda não existe, então não quebra nada.
5. **O trono é compartilhado** (servidor): um jogador abre para todos, e o trono fica aberto durante COUNTDOWN e ENTRY_OPEN.

**Riscos:**
1. **Tamanho:** a ilha fica **2,4× maior em área**.
   - Caminhadas mais longas: spawn → porta 21 s (hoje ~13 s); spawn → portal da masmorra ~55 s.
   - Se incomodar, a alternativa B é castelo 1,6× e ilha ~1,7×.
2. **Teto de MeshParts acima de 800:** depende do corte do subsolo no cliente para manter o FPS.
   - **É a decisão que mais preciso de você.**
3. **Mar:** fora do `FAR_GROUND` da Ilha 1. Sem o mar próprio da área 3, aparece o vazio a oeste de x −1024.
4. **Trono no servidor e física:** peça ancorada movida por CFrame não empurra o jogador. Com a colisão desligada no tween e a zona de segurança, o risco fica em "atravessar o trono por 3 s", não em prender alguém.
5. **Conflito de arquivos:** a Onda 0 mexe em `sg_core`, `sg_layout` e outros onde há agentes agora. Ela precisa esperar.

---

## Arquivos
- `renders/plano_mestre/PLANO.md` (este)
- `renders/plano_mestre/mundo.png`
- `renders/plano_mestre/planta_ilha.png`
- `renders/plano_mestre/corte_castelo.png`
- `renders/plano_mestre/scripts/`: `geo.py` (constantes e encaixe), `final.py` (números), `solve3.py` (busca do giro e da ponte), `draw_*.py` (diagramas)
