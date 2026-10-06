# Plano: Ilha 4 DEMON SLAYER (Monte Natagumo, área 4)

Data: 2026-10-06. Etapa: fases 01 (auditoria) e 02 (referências) do `PROMPT_USUARIO.md`, mais o plano. Nenhum arquivo do projeto foi editado. Nada foi construído ainda.

**Diagramas** (nesta pasta):
- `mundo.png`: o mundo visto de cima, como no Top do Blender (X do Roblox para a direita, Z para baixo), mais o zoom do encaixe;
- `planta_ds.png`: a planta local, com patamares, rotas, zonas, minérios, água, glicínias e câmeras;
- `corte_ds.png`: o corte longitudinal desdobrado ao longo do percurso, da âncora da Shadow Garden até a âncora One Piece, com vertical exagerado 2,5×.

**Números:** saem de `scripts/ds_geo.py`, que tem as constantes e o encaixe e é a proposta do `ds_layout.py`. `scripts/ds_final.py` imprime os números, `scripts/ds_cams.py` tem as câmeras e `scripts/draw_*.py` gera os diagramas. Eles rodam com Python + matplotlib, importando só para leitura as plantas das Ilhas 1, 2 e 3.

**Convenções** (as mesmas do `sg_layout`):
- 1 BU = 1 stud.
- Z é absoluto e igual ao Y do Roblox.
- **Origem local:** centro da soleira do torii de entrada.
- **Eixos locais:**
  - **+Y** é o eixo do percurso: entrada → clareira → forja → saída;
  - **+X** é a direita de quem chega: bambuzal, summon e roda d'água;
  - **−X** é a esquerda: vila e saída noroeste.
- **Roblox** = (x_mundo, z, −y_mundo).

---

## 0. Decisões em uma página

| # | Tema | Decisão |
|---|---|---|
| 1 | Encaixe | A ilha nasce da âncora real da SG, com **ponte reta de 100** no rumo da âncora. Giro **130°**: o local +Y vai para (−0,766; 0; 0,643). A borda fica a **188** da borda da SG e a ≥ 1.100 do resto. A SG não se move. |
| 2 | Forma | Ilha **longitudinal**, de 602 × 374 no topo (razão 1,61). Tem um **gargalo** na entrada (~130 de largura), um bojo lateral só onde fica o summon e um **nariz** a noroeste, na saída. Terraços em 6 cotas. Nada radial. |
| 3 | Percurso | Ponte → torii → pátio T0 54,2 → trilha + escada → T1 60,2. Ali o jogador escolhe a vila (esquerda, sobe a T2 66,2) ou a **clareira** (em frente). Depois vem a subida em 2 lances com um patamar a 70,2, o **terraço da forja a 80,2** e o caminho de saída atrás da forja. Fecha com o torii de saída, a ponte de 56, a cabeceira de pedra, o portão One Piece e a âncora. |
| 4 | Clareira | Natural, de 176 × 280 (~40k studs²), sem forma circular. **MiningZone de 112 × 150** em piso plano a 60,2. **72 marcadores `ORE_`** (2/10/22/38), entre as Ilhas 1 e 2 (54) e a 3 (80). Meta no jogo: **70 simultâneos** (`OreMax` 80). |
| 5 | Forja | Herói no topo: salão da fornalha de 44 × 32, com a boca acesa **no eixo** e virada para a clareira. **Torre-chaminé de 140,2**, o ponto mais alto da ilha. Oficina-residência a oeste; ala leste e **roda d'água** a leste, movida por um aqueduto que vem da nascente. Ferraria **artesanal de katana**: madeira, reboco e telha. Não é cópia da Forja do Ignis do lobby, que é industrial, rebitada e cheia de tubos. |
| 6 | Summon | Platô lateral a leste a 70,2, a **13 degraus** da clareira. Torre AMS **sem redesenho** (estrela + anéis + torre + núcleo, a família da Ilha 1, como a SG fez). Muda só a base, os materiais e o entorno, com madeira escura, pedra escura e 2 glicínias. O topo fica em ~115, abaixo da chaminé. |
| 7 | Torii | **Só 2**: entrada e saída. A vila tem portão de postes com lanternas, não torii. |
| 8 | Glicínia | **Só 4 acentos**: pérgola no topo do bambuzal, jardim da casa principal e 2 árvores no platô do summon. |
| 9 | Água | Uma única história de água: nascente → aqueduto de madeira → roda d'água → canal → **1 cascata** (forja → lagoa, 20 de altura) → lagoa → canal sob a pontezinha do summon → **1 sangradouro** pela ravina leste. Fora isso, nenhuma cachoeira e nenhuma ilhota. A água é feita no Roblox, por marcadores. |
| 10 | Saída | Ponte **real** de 56 a 80,2 → cabeceira de pedra (30 × 30, funcional) → portão One Piece aprovado (`il_gate_op`) → `ISLAND_NEXT_ANCHOR_OnePiece` na borda de fora, apontando para céu aberto (15° do radial lobby → fora). |
| 11 | Orçamento | **≤ 600k tris e ≤ 650 MeshParts** estáticos: proposta de 582k / 629, mais a reserva de VFX de 15k / 30. Fica menor que a Ilha 3 (847k / 809). |
| 12 | Pipeline | Cópia do da Ilha 3 com prefixo `ds_`: layout / lib / col / core / blockout / scene / qa / build / studio / export. Usa `fm_lib` e `export_roblox` **sem editar**. No Roblox, `Core.DemonSlayerIsland` segue o mesmo contrato do `JardimSombrasIsland`. |

---

## 1. Auditoria do projeto (fase 01)

### 1.1 O que REAPROVEITAR

**Pipeline**, igual ao da Ilha 3 e trocando `sg_` por `ds_`:

| Peça da Ilha 3 | Papel | Na Ilha 4 |
|---|---|---|
| `sg_layout.py` | Planta travada: cotas, polígonos, escadas, `world_matrix` = T(âncora)·Rz(yaw)·T(−PREV), `to_roblox`, `ore_points` | `ds_layout.py` a partir de `plano/scripts/ds_geo.py`. Ponte reta, sem o arco da SG. |
| `sg_lib.py` | Coleções `00_REFERENCE…18_*`, paleta da ilha em `fm_lib.MATS`, helpers de escada e guarda só visuais | `ds_lib.py` com as coleções da seção 9.1 e a paleta `DSMATS` (seção 10) |
| `sg_col.py` | Colisão andável congelada: pisos em faixas, escadas em rampa, guardas de borda, pontes | `ds_col.py`: pisos de T0 a T4, 7 escadas, 2 pontes, cabeceira, guardas. **A clareira tem piso PLANO** (o raycast do jogo exige \|piso − 60,2\| < 0,5 e normal > 0,85). |
| `sg_core.py` | Todos os marcadores, mais o portão aprovado da próxima área | `ds_core.py`: marcadores da seção 7 mais `il_gate_op.build_gate`, sem redesenho e com `area_id` 5 |
| `sg_blockout.py` | Volumes por zona com material simples | `ds_blockout.py`: só o que a seção 27 do prompt pede |
| `sg_scene.py` | Render, mar, lua, vizinhos de prévia, câmeras | `ds_scene.py`: câmeras de `ds_cams.py`, vizinhos SG / Ilha 2 / lobby como prévia, mar de nuvens |
| `sg_qa.py` + `fm_qa` | Andador (degrau 2,3, queda 2,3, altura 6,5, corpo 1,1), sondas, salão livre, técnico, marcadores | `ds_qa.py`: as 10 rotas da seção 4.4, `CLAREIRA_LIVRE` (nada colidível até piso+12 na MiningZone), sondas de borda, técnico e marcadores |
| `build_sg.py` | `ZONE_MODULES` (detalhe ou blockout por zona) | `build_ds.py` com as mesmas regras |
| `studio_sg.py` | Estúdio por zona: câmeras, rotas, `BUDGET`, `--all-detail` | `studio_ds.py`, com o `BUDGET` da seção 8 |
| `export_sg.py` | Leva ao mundo e roda `export_roblox.main()` com identidade, donos, tetos, `INTERIOR_LIGHTS`, `atomic`, `safe_candidates`, `collisions` (lock do portão) e `extra_lua` (`export_ilha_lua`) | `export_ds.py`: `ILHA4_<col>_<ID6>.fbx`, `ilha4_data.json`, `montar_ilha_demonslayer.lua`, `workspace.ILHA_DEMONSLAYER` e `ILHA_DEMONSLAYER_Servidor`, que fica desligado. O assert do lock vale para `COL_GateOnePieceLock_`. |
| `tools_sheet.py` | Folhas de antes e depois | Usado direto, sem cópia |
| `FM_MAT_PREVIEW=roblox` | Prévia com as cores reais do Roblox, sem textura | Obrigatório em todo QA visual |

**Base compartilhada.** `lobby_area/forja_mineradora/fm_lib.py` e `export_roblox.py` são **somente leitura**. O que a Ilha 4 usa deles:
- `MB`, `col_box`, `light`, `camera`, `add_variants` e `MATS`;
- `RBX_RULES` / `RBX_CAL` pela palavra-chave do nome do material (Wood, Plaster, Roof, Stone, Metal, Glass, Leaf, Grass);
- regras do export: ≤ 18k tris por malha, fatiamento em células de 128, `FOLD`, `VARIANT_MIN_TRIS`;
- orçamento estrito (`FM_BUDGET=strict`).

**Assets aprovados (sem redesenho):**

| Asset | Onde | Uso |
|---|---|---|
| Portão One Piece (`ilha_naruto/il_gate_op.build_gate`) | Cabeceira de saída | Padrão `il_gate_std`: vão 16 × 18, deck 18, interação a −7, saída a +12, marcadores `GATE_OnePiece*` e `PURCHASE_UI_ANCHOR_OnePiece`. `AREA_ID["OnePiece"] = 5` já bate. |
| Torre de invocação AMS (`ilha_naruto/il_summon.py` + `il_summon_kit.py`) | Platô do summon | Pelo esquema da SG (`sg_summon.tower_mod` / `fm_lib.MAT_ALIAS` só durante a torre): **estrela + 3 anéis + torre + núcleo**. Pódio próprio, porque a base de 40 × 19,6 não cabe. |
| Glicínia do portal DS do lobby (`fm_pv3_demonslayer`: tronco-líder em S, copa em guarda-chuva, cascatas cônicas em 3 tons) | 4 acentos | Mesma técnica, para a glicínia ter a família do jogo |
| Portão Demon Slayer (`il_gate_ds`) | Já está na ilhota da SG | Não se toca. É o portão de **entrada** da Ilha 4: a ponte nasce 28 depois dele. |

**Escala e convenções que valem:**
- avatar de ~5;
- espelho ≤ 0,8 e piso ≥ 1,7;
- porta com vão de 8 × 11 nas casas entráveis;
- guarda-corpo de 4;
- pé-direito ≥ 12 dentro das casas;
- tabuleiro de 18 nas âncoras;
- regra do z-fight (Onda 1 da SG): nenhuma face visível coplanar ou a < 0,12 de outra; janela acesa ≥ 0,12 atrás do vidro e da parede;
- Tier A, B e C;
- bevel único via `mb.box(..., bevel)`;
- o ladrilhado vem da **geometria**, com junta rebaixada, porque o Roblox não tem textura de detalhe.

**Sistemas do jogo** (só ligar, nada novo):

| Sistema | Contrato |
|---|---|
| Mineração | `SpawnMinerio` por zona: `MiningZone_*` (`sx`, `sy`, frente) + células 8 × 8, grade hexagonal `PASSO_HEX` 7,5 + `ORE_*` + bloqueios circulares `GP_Block_*`. Ponto válido: caixa 7 × 8 × 7 livre e raycast no piso. Raridade e minério vêm do tema `nichirin`. |
| Gacha | `Gacha_nichirin` vira o motor invisível da torre (`SUMMON_Interact` / `SUMMON_PlayerPosition`) |
| Portão de compra | Peça `NextAreaId` + `PurchaseUI` + tag `PortaoCompra`. Estado por jogador no `ILHAS_Cliente`, sem teleporte depois de liberado. |
| Região | Atributos `BoundsCenter`, `BoundsHalfSize`, `BoundsMinY`, `EntryPosition`, `EntryForward`, `SafePosition`, `SafeMaxY`, `RotaPropria`, `NextAnchor*`. `IslandTravel` por regiões e `IslandVisibility` por vizinhança. |
| Peças móveis | `VFX_*` com tag `IlhaMovel` (roda d'água e anéis do summon); `IlhaVFX` com `Dist` para o corte de partículas |
| Luzes | `NIGHT_ONLY` e `LIGHT_KEEP` do export, mais o override de interior por prefixo, como `INTERIOR_LIGHTS` na SG |
| Atmosfera | `AreaAtmosphere`, já com patch na SG, por tema. Mais um LocalScript de céu como o `CeuSombras`: mar de nuvens e névoa só na área 4. |
| Montagem | Import pelo botão Import do ribbon, `montar_*.lua`, fonte em `ServerStorage.IlhaDemonSlayer`, clone em runtime em `workspace.Areas.Area4` pelo `IslandWorld` (1 linha). O antigo procedural `01_Relevo`/`02_Arquitetura` fica para rollback. |
| Guarda da âncora | `SG_Exit_AnchorGuard` + `COL_SGAnchorGuard_*` saem quando a fonte `IlhaDemonSlayer` existe. É 1 linha no `JardimSombrasIsland`, como o `NarutoIsland` fez para a Ilha 2. |

### 1.2 O que NÃO reaproveitar (identidade própria)

| Não usar | Por quê | No lugar |
|---|---|---|
| Layout e composição da SG (praça + muralha + castelo no eixo, salão interno de mineração) | É a SG | Território longitudinal, mineração **a céu aberto** numa clareira natural |
| Basalto hexagonal, gótico, violeta e prata (SG) | Assinatura da SG | Penhasco de **estratos horizontais** cinza-azulados, com musgo e blocos irregulares |
| Arena circular, poço, rampas radiais (Ilhas 1 e 2) | Proibido (circular) | Clareira alongada, sem centro marcado |
| Casas de Konoha (`il_houses`: 4 águas, terracota, reboco, prédios redondos azuis) | Seria "Naruto com glicínia" | Minka / machiya da era Taishō: **irimoya** de telha **escura**, **madeira escura aparente** sobre reboco claro, *engawa*, *shoji* com treliça, soco *ishigaki* em talude |
| Forja do Ignis do lobby (`fm_forge*`: alto-forno redondo, chapas rebitadas, tubos, coifa de ferro) | É o lobby | Ferraria de katana: fornalha de tijolo refratário e pedra escura, foles de caixa (*fuigo*), bigorna baixa, cocho de têmpera, estantes de lâminas. A torre é quadrada, de alvenaria e reboco, com telhado de telha e chaminé de pedra. A roda d'água move um **martelo-pilão de madeira**. Sem tubo e sem rebite. |
| Ilhotas no céu (`SG_Sky_Islets`, ilhotas da Ilha 2) | O usuário proíbe | Profundidade só com `Atmosphere`, névoa e mar de nuvens (cliente) |
| Cachoeiras na borda | Proibidas como enchimento | Uma cascata interna funcional e um sangradouro |

---

## 2. Leitura das referências (fase 02)

As 5 vistas são do **mesmo mapa**. A orientação de cada uma sai da posição relativa entre entrada, vila, clareira, forja e summon.

| Ref | Câmera estimada | O que se vê |
|---|---|---|
| ref_01 | Sul, alta, no eixo (`CAM_DS_Ref_01`) | Ponte e torii de entrada embaixo, no centro; vila à esquerda numa rua curva; clareira no meio; forja no alto ao fundo, com duas escadas; summon num platô alto à direita; torii + ponte a leste; bambu + glicínia à frente-direita |
| ref_02 | Sudeste (`CAM_DS_Ref_02`) | Summon à direita, perto; forja ao fundo à direita; vila ao fundo à esquerda; entrada embaixo à esquerda, com glicínia NO torii; um 3º torii com ponte a oeste |
| ref_03 | Norte, atrás da forja (`CAM_DS_Ref_03`) | Forja em primeiro plano, com a roda d'água à esquerda (= leste); torii de entrada lá no fundo; vila à direita (= oeste); **torii + ponte junto da forja, a oeste** |
| ref_04 | Sul-sudoeste, alta e aberta (`CAM_DS_Ref_04`) | Igual à ref_01, com 2 pontes na frente (SO e L) |
| ref_05 | Sudoeste, baixa (`CAM_DS_Ref_05`) | Torii de entrada perto, à direita; vila à esquerda; forja ao fundo à esquerda; summon ao fundo à direita; torii + ponte a leste |

**Leitura espacial coerente** (o que as 5 concordam):
- **Forja** no **nível mais alto**, ao **norte**, numa plataforma de arrimo acima da clareira, com escadas descendo para ela:
  - salão com a boca da fornalha acesa, virada para a clareira;
  - torre-chaminé quadrada, alta, com fumaça;
  - roda d'água na ponta **leste**;
  - casa de 2 andares com estandartes vermelhos a **oeste**.
- **Clareira** no centro: terra batida com manchas de grama, pedras e um poço pequeno na borda.
- **Vila** a **oeste**, numa rua que sobe da entrada até perto da forja, com casas dos dois lados e lanternas.
- **Summon** a **leste/nordeste**, num platô mais alto que a clareira e mais baixo que a forja, com escadaria virada para a clareira, um pavilhão pequeno de madeira escura ao lado e glicínia em volta. Torre escura afilada, **núcleo azul**, **anel dourado**, **estrela dourada**.
- **Entrada** ao **sul**: ponte de madeira → torii vermelho com telhado escuro → pátio de lajes → caminho que se divide entre vila (esquerda) e bambuzal/glicínia (direita).
- **Bambuzal** no **sudeste**, ladeando o caminho da direita.
- **Penhasco** de blocos verticais, cinza-azulados, com musgo e trepadeiras.
- **Noite azul**, lanternas quentes, névoa embaixo.

**Onde divergem e como resolvo:**

| Divergência | Resolução |
|---|---|
| Ilha quase **circular** e clareira **quase redonda** (todas) | **Alongo pelo percurso**. A entrada vira um **gargalo** (y 0–130), a clareira vira um **retângulo orgânico de 176 × 280** no eixo, a subida ganha um capítulo próprio (y 377–437), a forja fica em y 434–524 e a saída num **nariz** a noroeste (y 594). O topo fica com 602 × 374. Mantém a intenção de cada vista: vila à esquerda, summon à direita, forja ao fundo e no alto, entrada embaixo. |
| 2 a 4 torii/pontes, cada vista com uma combinação (leste, oeste, SO) | **Só 2**: entrada (sul) e saída (**noroeste, atrás da forja**, como a ref_03 mostra). O torii leste do summon (refs 01, 02, 04 e 05) vira o **mirante do platô do summon**, com balaustrada e glicínia, sem torii e sem ponte. Isso também cumpre "saída depois da forja" (seção 5 do prompt). |
| Na ref_03 a boca da fornalha olha para o lado oposto à clareira | Fica com a maioria (4 de 5): **a boca olha para a clareira e para a entrada**, no eixo |
| Glicínia farta (torii de entrada, pérgola do bambuzal, summon) | 4 acentos. **Sem glicínia no torii** de entrada. |
| Duas escadas simétricas da clareira para a forja | **Assimétricas**: a subida principal tem 2 lances com patamar e é **deslocada a leste do eixo**; a escada oeste sai da vila alta |
| Cerca em volta da clareira inteira | Cerca baixa **só em setores**: borda do penhasco sul, junto da vila e no pé da subida |
| Vila de 10 a 12 casas | **6 construções** de tipos diferentes + poço coberto + oratório pequeno |
| Lanternas a cada poucos studs | Lanternas **nos nós** e a cada ~28 no caminho principal: `NightOnly` |
| Torre do summon das imagens (treliça afilada) | É a mesma **identidade** (estrela + anéis + torre + núcleo). Usamos a **torre AMS aprovada** com materiais DS, sem desenhar uma torre nova. |
| Ilhotas de rocha no fundo | Fora (proibidas). Profundidade por névoa e mar de nuvens. |

---

## 3. Encaixe no mundo

### 3.1 Dados de partida (Studio e `sg_layout` batem)
- **`ISLAND_NEXT_ANCHOR_DemonSlayer`:** (−1534,49; 52,20; 962,44), frente (−0,766; 0; 0,643), largura 18. Orientation (0; 130; 0).
- **Portão DS aprovado:** (−1513,04; 52,2; 944,45). Fica 28 antes da âncora, na ilhota R 22 da SG.

### 3.2 Matriz
`W4 = T(âncora) · Rz(130°) · T(−WORLD_FROM_PREV)`, com `WORLD_FROM_PREV` local = (0, −100).

| Eixo local | Roblox |
|---|---|
| +Y | (−0,7660; 0; 0,6428) = frente da âncora |
| +X | (−0,6428; 0; −0,7660) |

**Conferido:** `WORLD_FROM_PREV` levado ao mundo cai exatamente em (−1534,49; 962,44).

### 3.3 Posição e folgas
- **Topo:** x de −2101 a −1597 e z de 996 a 1491 no Roblox. Centro em (−1849; 1244). Área de 153k studs².

| Par (sem ilhotas) | Folga | Meta |
|---|---|---|
| Borda da Ilha 4 ↔ borda da SG | **188** | ≥ 180 (a mesma regra do plano da SG) |
| Borda da Ilha 4 ↔ ilhota do portão DS | 98 | É a ponte de chegada |
| Borda da Ilha 4 ↔ Ilha 2 | 1.102 | – |
| Borda da Ilha 4 ↔ Ilha 1 | 1.535 | – |
| Borda da Ilha 4 ↔ bbox dos picos do lobby | 1.139 | ≥ 250 |
| Ponte e cabeceira de saída ↔ SG | ≥ 790 | – |

**O ponto mais próximo da SG é a cabeça da ponte.** A folga depende só do comprimento da ponte: com 72 dava 160; com 100 dá 188. Por isso a ponte tem 100.

**Mar:**
- A Ilha 4 fica fora do `FAR_GROUND` da Ilha 1, que vai de x −1024 a 1024.
- Ela também cai dentro do retângulo do mar escuro do `CeuSombras` (2048², em −111,5), que só existe com o jogador na área 3.
- **Decisão:** mar de **nuvens próprio** da área 4 no cliente, em **−60**, só com o jogador na área 4. Fica acima do mar da SG: vista daqui, a quilha da SG (até −108) "sai das nuvens".

### 3.4 Chegada da Shadow Garden
**Ponte de chegada**, de 100, reta:
- tabuleiro de 52,2 a 54,2: rampa de 1,1°, sem degrau;
- 18 de estrutura e 14 livres entre guardas;
- madeira escura.

| Trecho | O que tem |
|---|---|
| 0–10 | Encontro na âncora: soleira de pedra escura que casa com a pedra da SG. É o único material da SG que entra. |
| 50 | Patamar de descanso com 2 postes-lanterna. É a transição: o violeta frio fica para trás, e névoa e bambu aparecem à frente. |
| 90–100 | Último vão, já com musgo e samambaia nos pilares |

**Torii de entrada:**
- fica em (0, 8), com vão livre de 12 × 14 e altura de ~16;
- laca vermelha escura, *kasagi* com telha escura;
- 2 *tōrō* de pedra.

Da ponte, a **torre-chaminé (140,2)** aparece por cima do torii e da vila. Ver a visada em `corte_ds.png`.

### 3.5 Saída para One Piece

**Caminho:** caminho de saída atrás da forja → **torii de saída** em (−94, 586) → `ISLAND_EXIT_DemonSlayer` → **ponte de saída real de 56** a 80,2, no rumo local 105° (15° à esquerda do eixo) → **cabeceira de pedra** de 30 × 30 sobre um pilar de rocha → portão One Piece a 12 do fim da ponte → âncora na borda de fora da cabeceira.

| Marcador | Local | Roblox |
|---|---|---|
| `ISLAND_EXIT_DemonSlayer` | (−95, 594; 80,2) | (−2005,06; 80,2; 1481,31) |
| `GATE_OnePiece` (`il_gate_op`, `area_id` 5) | (−112,6; 659,7; 80,2) | (−2044,07; 80,2; 1537,01) |

**`ISLAND_NEXT_ANCHOR_OnePiece`:**

| Campo | Valor |
|---|---|
| **Position** | **(−2054,39; 80,20; 1551,76)** |
| **ForwardVector** | **(−0,5736; 0; 0,8192)** |
| **Orientation** | **(0; 145; 0)** (LookVector = (−sin 145°; 0; −cos 145°)) |
| **Width** | **18** (tabuleiro) |
| **Height** | Tabuleiro em **Y 80,2** (a área 5 começa nessa cota); `NextAnchorClearHeight` **22** |
| `heading_deg` | −125 (atan2(−z, x)) |
| `next_area` / `next_key` | 5 / OnePiece |

- **Guarda provisória:** `DS_Exit_AnchorGuard` + `COL_DSAnchorGuard_*`. A integração da One Piece remove.
- **Direção:** a 15° do radial lobby → âncora, apontando para fora.
- **Espaço livre para a área 5:** um disco de raio 300, centrado 350 à frente da âncora em (−2255; 1838), fica a:
  - 926 da SG;
  - 1.706 da Ilha 2;
  - 2.161 da Ilha 1;
  - 1.851 dos picos do lobby;
  - 132 da Ilha 4: a One Piece nasce com ponte própria.

---

## 4. Planta (ver `planta_ds.png`)

### 4.1 Tamanho e cotas

**Topo:** 602 (eixo) × 374. Com as pontes, o percurso da âncora SG até a âncora OP tem 942.

| Cota | Nome | O que fica nela |
|---|---|---|
| 52,2 | DECK | Âncora e ponte de chegada |
| 54,2 | **T0 Entrada** | Pátio do torii (x −26..28, y 0..40), lajes, 2 *tōrō*, 1 árvore-marco |
| 60,2 | **T1** | Trilha alta (y 56–130), vila baixa, **clareira**, lagoa |
| 66,2 | **T2** | Vila alta (y 226–362), com arrimo de 6 para a clareira |
| 70,2 | **T3** | Platô do summon e patamar do meio da subida |
| 80,2 | **T4** | Terraço da forja, pátio do carvão, caminho de saída, ponte de saída e âncora OP |
| ~140 | – | Topo da torre-chaminé, o ponto mais alto |
| −34 | – | Fundo da quilha (Tier C). Mar de nuvens em −60. |

**Escadas** (espelho ≤ 0,8 e piso ≥ 1,75; todas com guarda nos lados abertos):

| Nome | Pé (x, y, z) | Rumo | Largura | Degraus | Chega em |
|---|---|---|---|---|---|
| Trilha | (−12, 40, 54,2) | N | 12 | 8 × 0,75 | T1 em y 54,4 |
| VilaAlta | (−84, 216, 60,2) | N | 10 | 8 × 0,75 | T2 |
| VilaClareira | (−44, 284, 60,2) | O | 8 | 8 × 0,75 | T2 (atalho vila alta ↔ clareira) |
| Summon | (128, 300, 60,2) | L | 12 | 13 × 0,77 | T3 em x 150,8 |
| SubidaA | (16, 377, 60,2) | N | 16 | 13 × 0,77 | Patamar T3 (−14..46, 400..414) |
| SubidaB | (30, 414, 70,2) | N | 14 | 13 × 0,77 | T4 em y 437,4 |
| OesteForja | (−66, 342, 66,2) | N | 10 | 18 × 0,78 | T4 em y 373,5 (pátio do carvão) |

**Rampa do bambuzal:** de T0 (20, 28) a T1 (66, 132), ~115 de comprimento e 6 de desnível. Inclinação de 5,2%, sem degrau.

### 4.2 Capítulos e zonas

**Entrada** (y −100..56). Ponte, torii, pátio T0.
- **Duas saídas do pátio:**
  - **Trilha** (escada de 8, em frente-esquerda);
  - **Bambuzal** (rampa à direita).
- **Transição:**
  - **materiais:** soleira de pedra escura da SG → madeira escura → lajes de pedra quente;
  - **vegetação:** nada roxo; bambu, cedro e samambaia;
  - **lanternas:** na ponte e nos *tōrō*.

**Trilha** (T1, y 56–130, x −44..14). Gargalo entre o penhasco oeste e o bambuzal.
- No topo da escada Trilha (y 54) o jogador fica **no nível da clareira** e a vê em frente, a 70 de distância, aberta e iluminada pela lua.
- No mesmo quadro aparecem:
  - à esquerda, os telhados da vila;
  - ao fundo, no alto, a forja com a boca acesa;
  - à direita, a estrela do summon por cima das copas.

  É a sequência de 5 passos da seção 31 do prompt.
- **Portão da vila:** 2 postes-lanterna altos + marco de pedra em (−38, 116). Não é torii.

**Vila** (T1 → T2, x −160..−40, y 100–362). Rua que sobe da trilha até a escada OesteForja: 6 construções e o poço.

| Id | Tipo | Centro (x, y) | Planta | Cota | Leitura |
|---|---|---|---|---|---|
| V1 | Pavilhão / casa de chá (*chaya*), aberto | (−62, 128) | 14 × 10 | T1 | 1º edifício depois do torii: bancos, cortina *noren*, lanterna. Segurança, "você chegou". |
| V2 | Residência (*minka*) térrea | (−112, 150) | 22 × 16 | T1 | Telhado irimoya baixo, *engawa*, horta |
| V3 | Oficina pequena (afiador / carpinteiro) | (−100, 198) | 18 × 14 | T1 | Frente aberta, rebolo, estantes de tábuas. Conversa com a forja. |
| V4 | Armazém (*kura*) de 2 pisos | (−134, 252) | 14 × 12 | T2 | Reboco branco grosso, soco de pedra alto, porta de ferro. A massa branca que marca a vila de longe. |
| V5 | Residência de 2 pisos | (−118, 294) | 22 × 16 | T2 | Sacada de madeira para a clareira |
| V6 | **Casa principal** (casa do mestre-ferreiro) | (−116, 340) | 30 × 20 | T2 | Portão próprio, jardim pequeno com **1 glicínia em treliça** (acento), *engawa* em L. Fica ao pé da escada OesteForja: a vila "pertence" à forja. |
| – | Poço coberto + oratório (*hokora*) | (−30, 196) | – | T1 | Na borda oeste da clareira, fora da MiningZone |

- **Interiores:** só V1 (aberto) e V6 (térreo visitável) têm interior real. As outras têm **janela com moldura, rebaixo, *shoji* e luz por trás** e porta com recuo e soleira, sem vão aberto. Fica dentro do orçamento menor.

**Clareira** (T1). Contorno natural de 176 × 280 (x −46..130, y 126..406), **40,5k studs²**.

**`MiningZone_DemonSlayer`:**
- retângulo nos eixos locais, de **112 × 150** (x −11..101, y 180..330), no piso 60,2;
- centro local (45, 255), Roblox (−1835,36; 60,2; 1156,16);
- frente = +Y local;
- céu aberto, sem teto.

**Margens livres:**

| Lado | Folga | Para quê |
|---|---|---|
| Sul (y 126–180) | ~50 | **Antecampo de chegada**: trilha e bambuzal chegam aqui |
| Oeste | 30 | Rua de circulação até a vila e o poço |
| Leste | 24 | Canal, pontezinha e escada do summon |
| Norte (y 330–377) | 47 | Pé da subida e lagoa |

**`ORE_*`:** 72 pontos em grade hexagonal de passo 14, com os cantos recortados por uma elipse para a mancha ler orgânica.
- **Raridade pela profundidade:** comum no sul (entrada), super no norte (pé da subida, diante da forja).
- Plano: `SUPERLEGENDARY` 2, `EPIC` 10, `UNCOMMON` 22, `COMMON` 38.

**`GP_Block_*`:**
- anel "borda" a +3 do retângulo (o builder tira o tamanho da zona dele);
- 4 grupos de **recorte de canto**, que deixam a área útil com forma de elipse e não de retângulo;
- corredores livres no antecampo (chegadas da trilha e do bambuzal) e no pé da subida.

**Comparação com as outras ilhas:**

| Ilha | Marcadores | No jogo |
|---|---|---|
| Ilha 1 | 54 | 70 |
| Ilha 2 | 54 + 136 da grade | 70 |
| Ilha 3 | 80 | 51 a 61, com `OreMax` 90 |
| **Ilha 4** | **72** + a grade de 7,5 na zona | `min(SPAWN.minerios 70; pontos − 2)` = **70**; `OreMax` **80** |

**Chão da clareira:**
- a colisão é **plana**;
- o visual tem ondulação de ≤ 0,3, sem colisão, com terra, manchas de grama, fragmentos de pedra e raízes saindo das árvores da borda;
- **nada colidível até piso + 12 dentro da zona.**

**Borda da clareira:**
- 3 árvores largas (oeste, sudeste, nordeste), fora da zona + 8;
- pedras só nas bordas;
- cerca baixa em 3 setores;
- vazio no meio: é **intencional**.

**Subida** (y 377–437). SubidaA → **patamar de 70,2**, que funciona como mirante sobre a clareira (pinheiro torto, *tōrō* e banco) → SubidaB.
- Fica em degraus de pedra cortados no arrimo, com muro de *ishigaki* em talude dos dois lados.
- A subida fica **a leste do eixo** (x 16–30). Assim a boca da fornalha (x 0) segue visível da clareira por cima do patamar.

**Forja (herói)**, no terraço T4 80,2 (x −152..130, y 372..540).

| Parte | Planta (x, y local) | Alturas acima de T4 | Conteúdo |
|---|---|---|---|
| Pátio de trabalho | −60..84 × 436..468 | – | Bigorna de pedra + bigorna de ferro, cocho de têmpera, 2 **estantes de lâminas** (espadas modeladas: lâmina com *shinogi* e ponta *kissaki*, *tsuba*, empunhadura com *ito*, pomo / *kashira*), rebolo, cestos de carvão, cerca baixa na borda com vão nas escadas |
| **Salão da fornalha** | −22..22 × 470..502 | Beiral 13, cumeeira 24 (104,2) | Soco de pedra escura de 3, enxaimel de madeira escura + reboco, **boca da fornalha de 10 × 9** em arco de pedra refratária no meio da fachada sul, com brasas e calor (a luz principal). Lá dentro: forno (*hodo*), fole de caixa (*fuigo*), bigorna. Telhado irimoya com **lanternim de fumaça** (*koshi-yane*) na cumeeira. |
| **Torre-chaminé** | 30..44 × 486..500 | Corpo até +44, telhado-chapéu +44..+52, chaminé de pedra até **+60 (140,2)** | Alvenaria até +16, reboco com enxaimel em cima, janelas estreitas quentes. Fumaça controlada saindo da chaminé. É o marco visível de tudo. |
| Oficina-residência | −68..−36 × 476..500 | 2 pisos, beiral 12, cumeeira 20 | Casa do mestre: sacada, **2 *noren* vermelhos** (o acento vermelho fora dos torii) |
| Ala leste | 52..74 × 474..496 | Beiral 9, cumeeira 16 | Polimento e armazém; eixo da roda entrando na parede |
| **Roda d'água** | Centro (92, 488), Ø 20 × 4 | Eixo a +11 | Alimentada por cima pelo **aqueduto de madeira** sobre cavaletes, vindo da nascente (100, 552, z 104). Move o martelo-pilão. Gira (`VFX_DS_Wheel`, tag `IlhaMovel`). |
| Pátio do carvão | Lobo oeste (x −150..−40, y 372..440) | – | Sacos e pilhas de lenha, carvoeira de pedra. Recebe a escada OesteForja. |
| Fundo | y 520..600 | Tier C | Rochas da montanha + 3 árvores grandes + nascente. É a moldura da silhueta. |

**Summon**, no platô lateral leste T3 70,2 (x 150..206, y 264..336).
- **Plataforma:** raio útil de ~24, com centro em (176, 300).
- **Torre AMS** em (184, 300), virada para −X (oeste: clareira e entrada).
  - `SUMMON_Interact` fica a 7 da torre e `SUMMON_PlayerPosition` a 16.
- **Pódio próprio:** madeira escura + pedra escura, com ferragens de ferro envelhecido.
- **Luz:** núcleo azul + estrela e anéis dourados. É a identidade do AMS; os acentos violeta ficam só em filetes.
- **Entorno:**
  - 2 glicínias (acentos);
  - mirante na borda leste com balaustrada baixa: é o lugar do torii leste das refs;
  - 4 lanternas de pedestal;
  - abrigo pequeno de madeira escura, como o das refs.
- **Acesso:** clareira → pontezinha sobre o canal (124, 300) → escada Summon.

**Saída** (T4): pátio do carvão → caminho de saída pelo oeste, atrás da oficina (y 452 → 590) → torii de saída → ponte de 56 → cabeceira → portão OP → âncora.
- **Densidade baixa:** cedros, 3 lanternas, vista aberta para o vazio.
- No fim do caminho, o portão One Piece com a energia azul-água é a "promessa do próximo mundo".

### 4.3 Água (a única, com função)
- **Nascente na rocha** (100, 552, 104).
- **Aqueduto de madeira** (100, 548) → (94, 500).
- **Roda d'água.**
- **Canal de pedra** pela borda leste do terraço até (118, 432).
- **Cascata** de 20: de T4 para a **lagoa** (110, 392, raio 14) no canto nordeste da clareira. Marcador `FX_Fall_1`.
- **Canal** pela margem leste da clareira, sob a **pontezinha** do summon.
- **Sangradouro** pela ravina leste em (154, 230). Marcador `FX_Fall_2`, fino.
- **No Blender:** só a pedra estanque e os marcadores.
- **No Roblox:** a água, como na SG (painéis com textura rolando e névoa).

### 4.4 Rotas (o andador do QA percorre as 10 sobre a colisão)

| Rota (seção 30 do prompt) | Caminho | Planta | Tempo (16 studs/s) |
|---|---|---|---|
| SHADOW_GATE → ENTRY | Portão DS → ponte de 100 → torii → pátio | 148 | 9 s |
| ENTRY → VILLAGE | Pátio → escada Trilha → portão da vila → rua baixa → VilaAlta → rua alta | 271 | 17 s |
| ENTRY → CLEARING | Pátio → Trilha → antecampo | 192 | 12 s |
| ENTRY → CLEARING (alternativa) | Pátio → rampa do bambuzal → antecampo sudeste | 166 | 10 s |
| CLEARING → FORGE | Pé da subida → SubidaA → patamar → SubidaB → pátio → boca | 234 | 15 s |
| CLEARING → SUMMON | Margem leste → pontezinha → escada Summon → plataforma | 141 | 9 s |
| CLEARING → ONE_PIECE_GATE | Subida → pátio → pátio do carvão → caminho de saída → torii → ponte | 473 | 30 s |
| FORGE → ONE_PIECE_GATE | Pátio → caminho de saída → torii → ponte → portão | 254 | 16 s |
| SUMMON → CLEARING | Volta | 137 | 9 s |
| VILLAGE → FORGE (secundária) | Rua alta → OesteForja → pátio do carvão → pátio | 196 | 12 s |

Nenhuma rota pede salto, *parkour* ou passagem escondida. Todos os nós têm lanterna e uma visada para o próximo destino.

---

## 5. Narrativa espacial por capítulo (densidade visual de propósito)

| Capítulo | Emoção | Densidade | O que tem | O que NÃO tem |
|---|---|---|---|---|
| Ponte / entrada | Silenciosa, misteriosa | **Baixa** | Ponte, torii, 2 *tōrō*, névoa, bambu, 1 árvore-marco | Casas, glicínia, placas |
| Trilha | Revelação | Baixa → média | Escada, arrimo, samambaia, portão de postes | Props soltos |
| Vila | Habitável, tradicional, segura | **Média-alta** (a mais "cheia" depois da forja) | 6 construções, varais, barris, vasos, hortas, janelas quentes, 1 glicínia | Lojas, NPCs com função, letreiros |
| Clareira | Espaço de jogo | **Muito baixa no centro**, média na borda | Terra, grama em manchas, pedras de borda, 3 árvores, poço, cerca em setores | Qualquer coisa colidível no meio; cristais; pedreira |
| Subida | Esforço, expectativa | Baixa-média | Escada de pedra, arrimo, pinheiro do patamar, *tōrō* | – |
| Forja | Calor, força, ofício | **Alta (herói)** | Fornalha, torre, fumaça, roda, aqueduto, pátio de trabalho, lâminas, carvão | Tubos industriais, rebites, minério |
| Summon | Místico, especial | Média | Torre AMS, pódio de madeira escura, 2 glicínias, 4 lanternas | Mais estrelas, cristais soltos |
| Saída | Promessa | **Baixa** | Cedros, 3 lanternas, torii, ponte, portão OP | Enchimento |

---

## 6. Lista de marcadores (contrato da Ilha 4)

O dono é o `ds_core.py`, que roda sempre. Os módulos de zona desenham em volta e nunca criam marcador. O export grava `fwd_x`/`fwd_z` e leva tudo ao mundo.

### Mundo
- **`WORLD_FROM_PREV`**:
  - local (0, −100, 52,2), Roblox (−1534,49; 52,2; 962,44);
  - frente = +Y local;
  - `width` 18, `deck_z` 52,2;
  - `prev` = `ISLAND_NEXT_ANCHOR_DemonSlayer` (Ilha 3);
  - `bridge_len` 100.
- **`WORLD_ENTRY_DemonSlayer`**: (0, 22, 54,4), Roblox (−1627,95; 54,4; 1040,86), frente +Y.
- **`PATH_ENTRY_CENTER(_nn)`**: waypoints pátio → Trilha → antecampo → centro da clareira → pé da subida → pátio da forja.
- **`ISLAND_EXIT_DemonSlayer`**: (−95, 594, 80,2), `heading_deg` local 105, `width` 18.
- **`ISLAND_NEXT_ANCHOR_OnePiece`**: os dados da seção 3.5, mais:
  - `next_area` 5, `next_key` OnePiece;
  - `clear_h` 22;
  - `fwd_roblox` "-0.5736,0.0000,0.8192";
  - `guard` = `DS_Exit_AnchorGuard`.

### Mineração
- **`ORE_<RARIDADE>_<nn>`**: 72 pontos (seção 4.2), cada um com `rarity` e `radius` (2,6 / 3,0 / 3,4 / 4,4).
- **`MiningZone_DemonSlayer`**:
  - (45, 255, 60,2);
  - `kind` mining, `floor` 60,2, `sx` 112, `sy` 150;
  - **sem `ceil`** (céu aberto). O script usa `piso + 28` como antes.
- **`GP_Block_<nn>`**: anel "borda", recorte de cantos, corredores do antecampo e do pé da subida, cada um com `radius` e `kind`.

### Invocação
- **`SUMMON_Main`**: (184, 300, 70,2), frente −X local, Roblox (−1959,18; 70,2; 1078,61).
- **`SUMMON_Interact`**: (177, 300, 70,2).
- **`SUMMON_PlayerPosition`**: (168, 300, 70,2).

### Portão de compra (pelo `il_gate_std.markers`, dentro do `il_gate_op.build_gate`)
- `GATE_OnePiece`, `GATE_OnePiece_LOCKED`, `GATE_OnePiece_INTERACT`, `GATE_OnePiece_EXIT`, `GATE_OnePiece_OpenFX`;
- `PURCHASE_UI_ANCHOR_OnePiece`;
- `COL_GateOnePieceLock_001`;
- `area_id` 5.

### Pontos seguros (`SAFE_*`)
`Entrada`, `Ponte_Chegada`, `Trilha`, `Vila_Baixa`, `Vila_Alta`, `Clareira_S`, `Clareira_N`, `Summon`, `Patamar`, `Forja_Patio`, `Patio_Carvao`, `Saida`, `Cabeceira`.

### Áudio (`AUDIO_*`, com família e alcance)

| Marcador | Família | Alcance |
|---|---|---|
| `AUDIO_Forge` | fire | 40 |
| `AUDIO_Waterwheel` | water | 30 |
| `AUDIO_Cascade` | water | 50 |
| `AUDIO_Pond` | water | 30 |
| `AUDIO_Bamboo` | wind | 50 |
| `AUDIO_Summon` | energy | 36 |
| `AUDIO_Clearing` | wind | 120 |
| `AUDIO_Village` | wind | 60, baixo |

### Efeitos e água (`FX_*` / `WATER_*`)
- `FX_Fall_1_Lip` / `_Step` / `_Base`: a cascata;
- `FX_Fall_2_Lip` / `_Base`: o sangradouro;
- `FX_Forge_Smoke`: topo da chaminé, `Dist` 400;
- `FX_Forge_Embers`: boca da fornalha, `Dist` 120;
- `FX_Mist_Bamboo` e `FX_Mist_Ravine`: névoa baixa;
- `WATER_Pond`;
- `WATER_Flume`, `WATER_Tailrace`, `WATER_Channel`: com `waypoints` e `widths`, no idioma do `sg_water`.

### Peças móveis
- `VFX_DS_Wheel`: roda d'água, com pivô e eixo;
- `VFX_DSSUM_*`: anéis e estrela da torre;
- `VFX_GATE_OnePiece_*`: do asset do portão.

---

## 7. Orçamento (≤ 600k tris e ≤ 650 MeshParts estáticos)

Referência da Ilha 3: 847k / 809, com teto de 860k / 870 e FPS de 56 a 60.

| Dono (prefixo) | Zona | Tris | MeshParts | Como |
|---|---|---|---|---|
| terrain (`DS_Ter_`) | Massa, penhascos, arrimos, chão, clareira | 95k | 110 | Estratos em módulos grandes; quilha Tier C; o detalhe (*ishigaki*, lajes com junta rebaixada) só na faixa do jogador |
| entry (`DS_Ent_`) | Ponte de 100, torii, pátio, *tōrō* | 32k | 34 | Tramo de ponte repetido, um objeto por função |
| village (`DS_Vil_`) | 6 construções + poço + rua | 110k | 105 | Kit modular instanciado. ~15k por casa (V6 ~22k, V1 ~8k). Fundos simplificados. |
| forge (`DS_Frg_`) | Forja inteira, roda, aqueduto, pátio | 120k | 95 | Herói Tier A até +20 e na boca; torre Tier B acima de +20 |
| summon (`DS_Sum_`) | Torre AMS + pódio + entorno | 32k | 40 | Torre reaproveitada (~29k na SG) + pódio |
| exit (`DS_Exit_`) | Caminho, torii, ponte de 56, cabeceira, guarda | 24k | 30 | Mesmo tramo da ponte de chegada |
| gate_op (`GATE_`) | Portão One Piece aprovado | 28k | 38 | Sem mexer |
| water (`DS_Water_`) | Canais, lagoa, bicas (pedra) | 6k | 12 | A água é do Roblox |
| props (`DS_Prop_`) | Lanternas (kit), cercas, barris, estantes, espadas | 35k | 55 | Kit instanciado, poucas variantes |
| vegetation (`DS_Veg_`) | Árvores largas, cedros, bambu em touceiras, arbustos, grama em manchas, 4 glicínias | 70k | 70 | Touceiras como objeto; grama só em bordas e manchas (≤ 20k) |
| **Total estático** | | **582k** | **629** | |
| vfx (`VFX_`) | Roda, anéis, partes do portão | Reserva de 15k | Reserva de 30 | – |

**`ER.BUDGET` proposto:**

| Item | Valor |
|---|---|
| `static_tris` / `static_meshes` | **600k / 650** |
| `vfx_tris` / `vfx_meshes` | 15k / 30 |
| `total` | 615k / 680 |
| `materials` | 110 |
| `shadow_meshes` | 260 |
| `day_lights` | 36 |
| `col` | 1.300 |

Tetos por dono no `export_ds.BUDGET_OWNER`: a tabela acima + 8% de folga, como na SG.

**FPS:**
- meta de **≥ 58** na vila e na forja e 60 no resto, medido com o protocolo de `ilha_shadowgarden/_audit/PERF_BASELINE.md`;
- **medir também na cabeça da ponte olhando para a SG**: as duas ilhas ficam visíveis juntas pelo `IslandVisibility`.

---

## 8. Kit arquitetônico a criar (`ds_kit.py`, Onda 1)

**Peças-base** (perfis com espessura, bevel único de 0,08 a 0,12, Tier A):
- **fundações *ishigaki***: talude de 8°, pedras com junta rebaixada e capa de pedra;
- **soco de pedra** reto;
- **paredes *shinkabe***: reboco **recuado** entre pilares e vigas de madeira escura aparente, com rodapé de tábuas (*koshi-ita*);
- **parede *kura***: reboco grosso com cantos arredondados e faixa preta de base (*namako* simplificado, em relevo);
- **pilares** (*hashira*) de seção quadrada chanfrada; **vigas** (*nuki*, *nageshi*) que passam dos pilares;
- **misulas** e **consolos** dos beirais (*hijiki*, simplificado);
- **telhados irimoya** e kirizuma:
  - telha em canais de relevo;
  - **beirais de 3 a 4 com espessura** (tabeira + caibros à mostra);
  - **cumeeira** com telha de cumeeira e ponteiras *onigawara*;
  - empena *irimoya* com tabeira e ventilação;
  - **cantos** com leve levantamento.

  Sem plano atravessando: cada interseção tem a sua peça (água-furtada, rincão).
- **janelas:** moldura + rebaixo + treliça *koshi* ou *shoji* + vidro / papel recuado ≥ 0,12 + luz por trás. Em 3 tipos: alta, baixa e de *kura*, com porta de ferro;
- **portas:** de correr, com trilho, soleira de pedra, folha com quadros, recuo e ferragem; *noren* opcional;
- **varanda *engawa***: assoalho de tábuas, pilaretes, degrau de pedra (*kutsunugi-ishi*);
- **escadas:**
  - de madeira, para as casas;
  - de pedra, com focinho chanfrado e espelho escuro recuado: o mesmo idioma que a SG aprovou;
- **guarda-corpo** de madeira com corrimão; **cerca baixa** de bambu ou ripas, com mourões.

**Lanternas** (seção 22: armação, vidro / papel, chapéu, base, suporte, fixação):
- **de poste:** pilar de madeira, braço, caixa de papel com armação e chapéu de telha;
- **de parede:** suporte de ferro e caixa pequena;
- **de pedestal (*tōrō*):** base, fuste, câmara com aberturas recuadas, chapéu de pedra e *hōju* no topo.

Em todas, a luz fica **dentro** da câmara: nada de cubo amarelo.

**Variações dirigidas:**
- V1 a V6 combinam 2 telhados, 3 janelas, 2 portas, *engawa* com ou sem, 1 ou 2 pisos e a altura do soco pelo terreno;
- a cor do reboco varia ±6% **por casa**, nunca de forma aleatória por peça;
- **um gesto próprio** por casa:
  - V1: aberta;
  - V3: frente da oficina;
  - V4: torre branca;
  - V5: sacada;
  - V6: portão e jardim.

**Forja** (kit próprio): fornalha de tijolo refratário, bigorna, fole de caixa, cocho, estante de lâminas, **espada** (lâmina com *shinogi*, ponta *kissaki*, *habaki*, *tsuba*, empunhadura com *ito* em losango, *kashira*), roda d'água (raios, aros, pás), aqueduto em cavaletes, martelo-pilão.

---

## 9. Paleta (`DSMATS`, nomes com a palavra-chave do `RBX_RULES`)

| Material | RGB base | Uso | Valor |
|---|---|---|---|
| `Wood_DS_Dark` | (58, 40, 30) | Estrutura aparente, pilares, vigas, beirais | Escuro |
| `Wood_DS_Mid` | (104, 72, 48) | Tábuas, *engawa*, pontes, cercas | Médio |
| `Wood_DS_Lacquer` | (150, 38, 30) | **Só** torii e *noren* da forja | Acento |
| `Plaster_DS` | (228, 216, 192) | Reboco claro e quente | **Claro** |
| `Plaster_DS_Kura` | (238, 234, 224) | Armazém branco | Mais claro |
| `Roof_DS_Tile` | (52, 58, 72) | Telha escura azul-ardósia | Escuro |
| `Roof_DS_Ridge` | (38, 42, 54) | Cumeeira e *onigawara* | Mais escuro |
| `Stone_DS` | (124, 120, 112) | *Ishigaki*, socos, escadas | Médio |
| `Stone_DS_Path` | (156, 146, 128) | Lajes dos caminhos (quentes, as mais claras do chão) | Claro |
| `Stone_DS_Dark` | (72, 70, 70) | Base da forja, fornalha, pódio do summon | Escuro |
| `Cliff_DS` | (86, 92, 104) | Penhasco em estratos, cinza-azulado | Médio-escuro |
| `Metal_DS_Iron` | (64, 62, 60), metal 0,5 | Ferro envelhecido: ferragens, bigorna, aros | Escuro |
| `Metal_DS_Rust` | (112, 66, 42) | Acento de ferrugem | Médio |
| `Glass_DS_Lantern` (Glow) | (255, 192, 118) | Papel / vidro de lanterna aceso, dentro da armação | Quente |
| `Window_DS_Warm` (Glow) | (255, 204, 140) | *Shoji* aceso, recuado | Quente |
| `Bamboo_DS` / `Bamboo_DS_Dry` | (118, 150, 72) / (170, 160, 104) | Bambuzal e cercas | Médio |
| `Leaf_DS_Broad` / `Leaf_DS_Cedar` / `Leaf_DS_Shrub` | (46, 84, 48) / (34, 66, 46) / (66, 104, 56) | Copas e arbustos | Médio-escuro |
| `Grass_DS` | (84, 118, 62) | Manchas de grama | Médio |
| `Dirt_DS` / `Dirt_DS_Dark` | (132, 106, 76) / (98, 80, 60) | Chão da clareira (lê os minérios por contraste) | Médio |
| `Wisteria_DS` / `_Light` | (150, 110, 205) / (186, 156, 230) | **Só** nos 4 acentos | Acento |
| `Fire_DS_Glow` / `Ember_DS_Glow` | (255, 122, 40) / (255, 84, 24) | Boca da fornalha, brasas | Quente |
| Summon | Estrela e anéis `Metal_Gold` + `Crystal_SumAmber/Yellow` (da Ilha 1), núcleo `Crystal_SumPortal` azul (da Ilha 1), filete violeta escuro | – | Identidade do AMS |

**Regra de valor:**
- o chão do caminho (claro e quente) fica acima da parede de reboco (claro), da madeira (escura) e do telhado (mais escuro);
- o penhasco é médio-frio;
- a vegetação é médio-escura, com 3 tons.

Valida com `FM_MAT_PREVIEW=roblox`: tudo distinguível sem luz dramática.

**Neon:** médio ou escuro, só onde tem função (fogo, lanterna, janela, núcleo).

---

## 10. Iluminação: noite legível

- **Lua fria**, vinda de trás-esquerda de quem chega (sudoeste local). Ilumina as fachadas que o jogador vê e recorta a forja contra o céu.
- **Valores iniciais por tema no `AreaAtmosphere`**, ajustados no Play:

| Propriedade | Valor |
|---|---|
| Ambient | (118, 128, 156) |
| OutdoorAmbient | (138, 152, 184) |
| Brightness | 1,6 |
| ExposureCompensation | +0,2 |
| Atmosphere | Density 0,30, Color (150, 170, 205), Decay (60, 72, 105), Haze 1,8, Glare 0 |
| Bloom | 0,3 / limiar 1,4 |
| ColorCorrection | saturação −0,05, tint (232, 236, 255) |

- **Hierarquia das luzes quentes:**
  1. boca da fornalha: a mais forte, laranja, ~Range 28 com override de interior;
  2. janelas da forja e da torre;
  3. summon: núcleo azul + 2 lanternas;
  4. janelas das casas (1 luz por casa, dentro);
  5. lanternas de caminho (`NightOnly`, `L_DSProp_Lamp_*`);
  6. *tōrō*.
- **Contagem:** ~16 luzes de dia (≤ 36) + ~24 `NightOnly`.
- **Sem "preto + neon":** o piso, os caminhos, as casas, a forja, os minérios, as saídas e o summon precisam ler só com o ambiente.
- **Névoa:** baixa, no bambuzal e na ravina (`FX_Mist_*`), mais o mar de nuvens.

---

## 11. Câmeras de QA (referencial local; `ds_cams.py`)

| Câmera | Local (x, y, z) | Alvo | Lente |
|---|---|---|---|
| `CAM_DS_Entry` | (8, −45, 62) | (−4, 90, 66) | 22 |
| `CAM_DS_Front` | (40, −260, 220) | (20, 300, 70) | 28 |
| `CAM_DS_Left` | (−460, 300, 230) | (20, 300, 70) | 30 |
| `CAM_DS_Right` | (520, 280, 230) | (20, 300, 70) | 30 |
| `CAM_DS_Back` | (−20, 900, 260) | (20, 280, 70) | 30 |
| `CAM_DS_BirdEye` | (25, 300, 1100) | (25, 302, 60) | 32 |
| `CAM_DS_Clearing` | (24, 404, 80,2) (do patamar) | (40, 200, 60,2) | 24 |
| `CAM_DS_Village` | (−20, 150, 100) | (−110, 260, 68) | 26 |
| `CAM_DS_Forge` | (30, 300, 96) | (10, 480, 102) | 26 |
| `CAM_DS_Summon` | (70, 230, 84) | (180, 300, 92) | 28 |
| `CAM_DS_OnePieceGate` | (−110, 548, 92) | (−112,6; 659,7; 90) | 24 |
| `CAM_DS_PlayerHeight_Entry` | (0, −40, 58,9) (na ponte) | (0, 120, 64) | 22 |
| `CAM_DS_PlayerHeight_Clearing` | (−20, 140, 65,7) | (50, 280, 63) | 22 |
| `CAM_DS_PlayerHeight_Village` | (−44, 130, 65,7) | (−84, 210, 66) | 22 |
| `CAM_DS_PlayerHeight_Forge` | (16, 360, 65,7) (pé da subida) | (10, 480, 96) | 22 |
| `CAM_DS_PlayerHeight_Summon` | (112, 300, 65,7) | (184, 300, 82) | 22 |
| `CAM_DS_PlayerHeight_OnePieceGate` | (−100,2; 613,3; 85,7) (na ponte) | (−112,6; 659,7; 89,2) | 24 |
| `CAM_DS_Ref_01` | (30, −300, 380) | (25, 280, 62) | 28 |
| `CAM_DS_Ref_02` | (330, −160, 300) | (20, 280, 62) | 30 |
| `CAM_DS_Ref_03` | (−30, 820, 320) | (20, 260, 62) | 28 |
| `CAM_DS_Ref_04` | (−90, −260, 430) | (30, 270, 60) | 26 |
| `CAM_DS_Ref_05` | (−200, −150, 200) | (40, 220, 70) | 30 |

As `Ref` servem para comparar lado a lado com `ref/ref_0n.jpg`, no QA de coerência entre vistas.

**Diferença esperada e aceita:** a ilha é **mais longa** que nas imagens.

---

## 12. Ordem de construção em ondas (1 arquivo por agente; ninguém mexe no arquivo de outro)

**Onda 0: planta, contratos e blockout** (1 agente, serial; é o dono da integração)
- **Arquivos:**
  - `ds_layout.py` (de `ds_geo.py`);
  - `ds_lib.py` (coleções, `DSMATS`, prefixos);
  - `ds_col.py`;
  - `ds_core.py` (marcadores + `il_gate_op`);
  - `ds_blockout.py`;
  - `ds_scene.py` (câmeras, mar de nuvens, lua, vizinhos de prévia);
  - `ds_qa.py`;
  - `build_ds.py`;
  - `studio_ds.py` (`BUDGET`);
  - `export_ds.py` (identidade, donos, tetos, `INTERIOR_LIGHTS` com `L_DSFrg`, `atomic`, `safe_candidates`, lock `COL_GateOnePieceLock_`).
- **Blockout só com** a massa da ilha, a entrada, a vila (volumes com telhado), a clareira, a forja (volumes + torre), o platô do summon (pode já ser a torre AMS) e a saída para One Piece. Materiais simples.
- **QA:**
  - 10 rotas OK;
  - `CLAREIRA_LIVRE`;
  - sondas;
  - técnico;
  - export seco imprimindo `CONEXAO` com `WORLD_FROM_PREV` = âncora (distância 0,000);
  - renders das 22 câmeras nos 2 modos e folha lado a lado com as 5 referências.

**GATE DO BLOCKOUT** (seção 28 do prompt). O lead revisa com critério medido. **Se falhar, a Onda 0b refaz o blockout.**

| Item da seção 28 | Critério verificável |
|---|---|
| Fluxo claro | 10 rotas OK no andador. Em cada `PlayerHeight` o próximo destino aparece (luz ou silhueta) sem virar a câmera mais de 60°. |
| Composição não circular | Razão topo ≥ 1,5 (plano: 1,61). Clareira com razão ≥ 1,4 (280/176). `CAM_DS_BirdEye` não lê "disco". |
| Clareira grande o suficiente | MiningZone ≥ 112 × 150, ≥ 70 pontos válidos (marcadores + grade), nada colidível até +12 |
| Forja como landmark | Torre ≥ 20 acima de qualquer outra coisa. Silhueta acima do horizonte em `PlayerHeight_Entry` e `_Clearing`. Boca visível do antecampo. |
| Summon integrado | Visível da trilha e da clareira, topo abaixo da chaminé, 1 escada + 1 ponte |
| Entrada SG coerente | Ponte encostando na âncora: largura 18, deck 52,2, 0,000 |
| Saída OP coerente | Ponte real + cabeceira + portão + âncora na borda, rumo para fora |
| Câmera do jogador funciona | Nenhuma `PlayerHeight` com oclusão por beiral, galho ou guarda |
| Não parece quadrado | Nenhum trecho reto de borda > 60. Topo com gargalo e nariz. |
| Conta uma história | Os 6 capítulos com densidade diferente (seção 5) nos renders |

**Onda 1** (paralela, depois do gate):

| Agente | Arquivo | Escopo |
|---|---|---|
| 1a | `ds_terrain.py` | Massa, estratos, quilha, arrimos, chão (lajes, terra, grama em manchas), clareira, ravina. Fases 05 e 03. |
| 1b | `ds_kit.py` | Kit arquitetônico + lanternas + cercas (seção 8), com folha de close-up de cada peça. Fase 06. |
| 1c | `ds_entry.py` + `ds_exit.py` | Pontes, 2 torii, *tōrō*, cabeceira, guarda da âncora. Posiciona o `il_gate_op` (sem redesenho). Fase 09. |
| 1d | `ds_summon.py` | Torre AMS via alias (como o `sg_summon`), pódio DS, mirante, 2 glicínias. Fase 08. |

**Onda 2** (paralela; precisa do `ds_kit` pronto):

| Agente | Arquivo | Escopo |
|---|---|---|
| 2a | `ds_village.py` | V1 a V6, poço, oratório, rua, interiores de V1 e V6. Fase 10. |
| 2b | `ds_forge.py` | Herói (seção 4.2) + espadas + roda e aqueduto. Fases 07 e 10. |
| 2c | `ds_water.py` | Pedra de canais, lagoa, bicas. Mede e corrige `FX_*` e `WATER_*`. |

**Onda 3** (paralela):

| Agente | Arquivo | Escopo |
|---|---|---|
| 3a | `ds_veg.py` | Árvores, bambu, cedros, grama, as 4 glicínias de mesma família. Fase 12. |
| 3b | `ds_props.py` | Props da vila, da clareira (borda) e da forja. Fase 11. |
| 3c | `ds_lights.py` + `ds_vfx.py` | Luzes e VFX (fumaça, brasas, névoa, roda). Fases 14 e 15. |

**Onda 4: integração** (1 agente, serial)
- `build_ds` completo, `ds_qa` inteiro e `BUDGET` global estrito;
- passe de material (fase 13) nos 2 modos;
- 360°, folhas de antes e depois, z-fight (`zf_detect` adaptado);
- export.

**Onda 5: Roblox** (só quando o Studio for liberado). Fases 16, 17 e 18.
- Import e montagem;
- `Core.DemonSlayerIsland` (o contrato do `JardimSombrasIsland`, com `GATE_KEY` OnePiece, `GATE_AREA` 5, `SafeMaxY` 100, `OreMax` 80, sem masmorra e sem alquimia);
- 1 linha no `IslandWorld`;
- guarda da SG removida no `JardimSombrasIsland`;
- `CeuNatagumo` (cliente: mar de nuvens e névoa);
- valores do tema no `AreaAtmosphere`;
- **testes no Play:**
  - 10 rotas;
  - mineração (70 minérios);
  - gacha;
  - portão OP (compra, sem teleporte);
  - encaixe 0,000;
  - FPS na vila, na forja e na cabeça da ponte olhando a SG.
- **O place não é salvo pelo agente.**

**Onda 6: auditoria de altura do jogador + polimento** (fases 19 e 20). Mesmo método da `AUDITORIA3` da SG: lista por arquivo, depois o passe de finesse.

**Regras para todas as ondas:**
- `fm_lib` e `export_roblox` são só leitura;
- não modelar minérios (proxy só no blockout, `DS_Clr_OreProxy`, removido no export);
- 3 voltas de render → crítica → correção, nos 2 modos;
- sem commit e sem `taskkill`.

---

## 13. Riscos e suposições (decididos; sigo com eles)

**Suposições:**
1. **A área 4 continua sendo o "Monte Natagumo"** (tema `nichirin`), com o gacha, os minérios e o preço que já existem. A ilha substitui só o procedural antigo de `Area4`, que fica para rollback.
2. **A área 5 é One Piece** (tema `mare`). O `il_gate_std.AREA_ID["OnePiece"] = 5` já bate e não precisa de override.
3. **A One Piece começa na cota 80,2.** Ela ainda não existe, então nada quebra.
4. **Ponte de chegada de 100**, para a folga de 188 até a SG. A alternativa, uma ponte curva com giro, não traz ganho.
5. **Interiores só em V1 e V6.** As outras casas leem por janela recuada e iluminada, porque o orçamento é menor.

**Riscos:**
1. **Ilha 3 e Ilha 4 visíveis juntas.** O `IslandVisibility` mostra as vizinhas, e a SG tem 847k. Sem o subsolo, que fica escondido, a superfície da SG soma ~700k; junto com a Ilha 4 dá ~1,3M.
   - **Medir na cabeça da ponte.**
   - **Mitigação:** Tier C agressivo na quilha e no fundo, `RenderFidelity` Automatic e corte de VFX e partículas por `Dist`.
   - Se o FPS cair, a ilha de trás fica só com a SKYLINE.
2. **Semelhança com a Forja do Ignis**, que também tem chaminé e roda d'água. As regras da seção 1.2 são obrigatórias para o agente 2b, e a revisão compara os dois lado a lado.
3. **Semelhança com a Konoha (Ilha 1).** O telhado escuro irimoya, a madeira aparente e a ausência de terracota e de prédio redondo são obrigatórios.
4. **MiningZone retangular, borda orgânica:** o script só conhece retângulos. O recorte vem dos `GP_Block` de canto. Se sobrar ponto feio no canto, aumento os blocos, sem tocar no sistema.
5. **Lua:** o azimute no Roblox sai do `ClockTime` e da `GeographicLatitude` por tema. A direção da seção 10 é um alvo, ajustado no Play.
6. **Mar:** a Ilha 4 fica fora do `FAR_GROUND` da Ilha 1 e dentro do retângulo do mar do `CeuSombras`. O mar de nuvens próprio (−60, área 4) precisa ser testado na transição SG → DS, para não piscar.
7. **Região:** as caixas da SG e da Ilha 4 se tocam na ponte. A histerese do `IslandTravel` decide. Testar ida e volta.
8. **`SafeMaxY`:** a forja fica em 80,2, então o valor é **100**. A SG usa 60 e não serve aqui.
9. **Proximidade da área 5:** o disco da área 5 fica a 132 da Ilha 4. A ilha One Piece deve nascer com uma ponte de ≥ 100 a partir da âncora.
