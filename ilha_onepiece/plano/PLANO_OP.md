# Plano: Ilha 5 ONE PIECE / WANO (área 5 "Grand Line", tema `mare`)

Data: 2026-10-07. Etapa: **M0 (auditoria) + M1 (blockout da ilha inteira)** do `PROMPT_USUARIO.md`. Nada fora de `ilha_onepiece\` foi editado; o Studio não foi usado (fatos do Studio vieram do lead e de `ilha_demonslayer\export\conexao_roblox.json`). Sem commit.

**Diagramas** (nesta pasta): `planta_op.png` (planta local: pisos, escadas, praça, MiningZone, 72 minérios, prédios por cor de telhado, rotas, castelo, árvore, navio, saída) e `mundo_op.png` (Roblox: Wano, Demon Slayer, Shadow Garden e o disco livre da área 6). Ambos saem de `python op_map.py`, que também imprime as conferências.

**Convenções** (as mesmas do `ds_layout`):
- 1 BU = 1 stud; Z absoluto = Y do Roblox.
- **Origem local:** centro da soleira do GRANDE TORII de entrada.
- **+Y** = eixo visual: ponte → torii → rua de chegada → praça → adro → castelo/árvore. **+X** = direita de quem chega (summon, porto, enseada, caveira, saída OPM). **−X** = bairro do canal, quarteirão oeste, terraço alto, pagode.
- Roblox = (x_mundo, z, −y_mundo). `W5 = T(âncora DS) · Rz(145°) · T(−WORLD_FROM_PREV)`.

---

## 0. Decisões em uma página

| # | Tema | Decisão |
|---|---|---|
| 1 | Encaixe | Nasce da âncora REAL da DS (`ISLAND_NEXT_ANCHOR_OnePiece` (−2054,391; 80,2; 1551,759), frente (−0,5736; 0; 0,8192), largura 18). Giro **145°**. **Ponte reta de 120** (80,2 → 84,2, 1,9°). Distância medida no export seco: **0,0000**. A DS não se move; o portão One Piece aprovado continua NA DS (não se cobra de novo). |
| 2 | Forma | 587 × 503 no topo (216k studs²). Pescoço estreito na entrada (torii no "nariz" da falésia, como na concept), lobo SO do bairro do canal, flanco oeste com o pináculo do pagode, fundo alto do castelo, **enseada do porto a leste aberta para SE** fechada pelo **promontório da caveira**, esporão da espada no canto NE do fundo. Não é disco: a enseada e o promontório dão a forma. |
| 3 | Narrativa | Ponte → **grande torii** → pátio (84,2) → escada → **rua de chegada comercial** (88,2) → escadaria larga → **PRAÇA** (92,2) → escada sob o **portão vermelho do castelo** → adro com bacia e **cachoeira do castelo** (98,2) → subida pelo flanco oeste da rocha → **pátio do castelo** (136,2) com varanda vermelha e a torre. Ao lado: summon (terraço leste 88,2) → porto (42,2) e **ponte vermelha de saída** → promontório → portão OPM. |
| 4 | Praça | Polígono 232 × 194 (42,5k studs² de paving), **MiningZone 152 × 120** (18.240 studs², contém o 112 × 150 da DS girado) em piso PLANO 92,2, centro local (0, 216). Margens livres ≥ 34 em volta. **72 `ORE_`** (2/10/22/38). Emblema de chão RENTE (+0,24, sem colisão). Nada no centro; estandartes só nos cantos (fora da zona + 8). |
| 5 | Castelo | Torre de 4 andares escalonados (56 × 46 na base, cumeeira ~215) num patio-rocha a **136,2** em proa sobre a praça; adro + portão vermelho no eixo; **terreo ACESSÍVEL** (porta aberta 6 × 9 → salão real 50 × 42, pé-direito 12, 3 luzes, mesmo caminho de volta); andares de cima cenográficos; varanda vermelha no 4º andar e guarda-corpo vermelho no mirante do pátio; yagura no canto SE. |
| 6 | Árvore | Tronco que **nasce de base de rocha com 5 raízes** no fundo-leste do pátio, sobe à direita da torre, curva por cima (topo 274, 58 acima da cumeeira) e termina à esquerda; raio 12 → 2,2 (afinamento progressivo), secção achatada, leve torção dirigida; 3 galhos; copa em 10 massas rosas + lobos + base verde com abertura sobre o castelo. É o ponto mais alto da ilha (304). |
| 7 | Summon | Terraço lateral leste a 88,2 (mesmo nível da rua de chegada: dá para ir da chegada ao summon **sem atravessar a praça**). Torre AMS aprovada **por alias** (estrela + anéis + torre + núcleo azul, código da Ilha 1, só pedra/tecido/madeira trocados para a paleta Wano). Topo 148 < castelo. 6 degraus da praça. |
| 8 | Porto | Cais a 42,2 (mar local 36): rua alta do porto (65,2) com 2 lances de 30 degraus, pier de madeira, palafita com pavilhão vermelho, 4 armazéns, 2 barcos. **Navio** 80 × 16 com convés **acessível pela prancha** (46,2), 2 mastros, velas apoiadas nas vergas, castelo de popa. Sem navegação. |
| 9 | Água | 3 quedas estruturais, cada uma com origem e término: **cachoeira do castelo** (nasce na rocha sob a varanda → bacia do adro, 34), **queda leste** (canal leste → enseada do porto, 56), **queda oeste** (bica no arrimo do terraço alto → canal oeste com 2 pontes vermelhas → roda d'água → mar, 52). Mar LOCAL turquesa feito no cliente só na área 5 (`WATER_Sea`, nível 36). No Blender só pedra + prévia. |
| 10 | Saída | Ponte vermelha de 88 sobre a enseada (rumo local 15°, para fora) → promontório (T1) → **portão One Punch Man da galeria** (`il_gate_opm`, mesma família do OP aprovado, `area_id` 6) → `ISLAND_NEXT_ANCHOR_OnePunchMan` na borda, com **guarda provisória** (término seguro; testado). |
| 11 | Orçamento | Teto ≤ 620k tris / ≤ 650 MeshParts estáticos / col ≤ 1300 / luzes de dia ≤ 36. Plano por dono: 617k / 614. Blockout: 71k tris, ~201 MeshParts, col 985 (519 depois da união do export), 7 luzes de dia. |
| 12 | Pipeline | Cópia do da DS com prefixo `op_` / `OP_`; `fm_lib` e `export_roblox` só leitura. `export_op` gera `ILHA5_*`, `ilha5_data.json`, `montar_ilha_onepiece.lua`, `workspace.ILHA_ONEPIECE`; fonte no Studio = `ServerStorage.IlhaOnePiece` (o nome que a DS já espera em `FONTE_PROXIMA`). |

---

## 1. Auditoria (M0)

### 1.1 Estado real
- **Config:** áreas 1 chakra, 2 ki, 3 sombra, 4 nichirin (DS), **5 mare "Grand Line" = esta ilha**, 6 serio "Cidade Z" (OPM). Não se cria mundo/progresso novo: Wano é a ambientação da área 5 existente.
- `workspace.Areas.Area5` hoje = construção genérica antiga (01_Relevo…, EntryPosition (0; 9,5; 2015), fora do mundo contínuo). Será substituída como nas ilhas 1–4 (o `IslandWorld` despacha por tema quando a fonte existe em `ServerStorage`); a antiga fica para rollback.
- **DS (export 9cc4bef4)** já tem o `GATE_OnePiece` aprovado (vende a área 5) 18 antes da âncora e `FONTE_PROXIMA = 'IlhaOnePiece'`: quando `ServerStorage.IlhaOnePiece` existir, a guarda provisória da ponta da DS sai sozinha. Nenhuma edição na DS é necessária.
- **OPM (área 6) não existe como ilha.** Wano termina com âncora documentada + guarda provisória + portão de compra da área 6 (padrão da DS com o portão OP).
- **Backup:** nada do projeto foi alterado nesta etapa (só arquivos novos em `ilha_onepiece\`). O backup do place é tarefa do M5 (lead), antes de importar.

### 1.2 O que REAPROVEITAR (sem editar)
| Peça | Uso em Wano |
|---|---|
| `fm_lib` (MB, col_box/ramp, light, camera, MATS, RBX_RULES, variantes, `FM_MAT_PREVIEW=roblox`), `fm_scene`, `fm_parts.Frame`, `fm_qa.walk` | Base de tudo, só leitura |
| `export_roblox` + `export_ilha_lua` | Export configurado por `export_op` (identidade, donos, tetos, luzes de interior, lock do portão, guarda da âncora) |
| `il_summon` (torre AMS) | Via `tower_mod()`/alias, como `ds_blockout`/`ds_summon` |
| `il_gate_opm.build_gate` + `il_gate_std` | Portão da área 6 (vão 16 × 18, deck 18, interação −7, saída +12, marcadores `GATE_OnePunchMan*`, `PURCHASE_UI_ANCHOR_OnePunchMan`, `COL_GateOnePunchManLock_001`). `AREA_ID["OnePunchMan"] = 6` bate com o Config. |
| `ds_layout` (só leitura) | Prévia da DS nas câmeras e cálculo de folgas |
| Contrato Roblox de `roblox/DemonSlayerIsland.lua` | Modelo do futuro `Core.OnePieceIsland` (seção 12) |

**Achado sobre o portão OPM:** `il_gate_opm` está na mesma galeria (`il_gates.MODS`) que o `il_gate_op` usado e aprovado na DS; não há registro explícito de aprovação só dele. Uso o asset da galeria sem redesenho e registro a pendência (seção 14).

### 1.3 Sistemas do jogo (só ligar, nada novo)
| Sistema | Contrato para Wano |
|---|---|
| Mineração | `SpawnMinerio` por zona: `MiningZone_OnePiece` (`sx` 152, `sy` 120, frente +Y, `floor` 92,2, céu aberto) → lista de células 8 × 8 girada; grade hex `PASSO_HEX` 7,5; `ORE_*` (72) + `GP_Block_*` (48 borda + 28 canto). Ponto válido: caixa 7 × 8 × 7 livre + raycast no piso (\|piso − 92,2\| < 0,5, normal > 0,85) — **conferido no QA (0 pontos fora)**. Raridades/HP/recompensas: tema `mare`, sem mudança. `OreMax` 80, alvo 70 simultâneos. |
| Summon | `Gacha_mare` vira motor invisível da torre (`SUMMON_Interact` a 7, `SUMMON_PlayerPosition` a 16), como na DS. Catálogo/custo/animação do tema `mare`. |
| Portões | Peça `NextAreaId = 6` + `PurchaseUI` + tag `PortaoCompra`; estado por jogador no `ILHAS_Cliente` (`GATES.OnePunchMan = 6`), sem teleporte. |
| Região / IslandTravel | `BoundsCenter/HalfSize` pela caixa do modelo; **`SafeMaxY` 150** (pátio do castelo 136,2); **`BoundsMinY` 28** (abaixo do mar local 36: quem cai na água é resgatado); `EntryPosition/Forward` do `WORLD_ENTRY_OnePiece`; `NextAnchor*` do `ISLAND_NEXT_ANCHOR_OnePunchMan`; `RotaPropria`. |
| AreaAtmosphere | Perfil `[5]` diurno (seção 11). Só área 5; não toca SG/DS. |
| Peças móveis / VFX | `VFX_OP_Wheel` (roda d'água) e `VFX_OPSUM_*` (anéis/estrela) com `IlhaMovel`; `FX_*` com `Dist` para `IlhaVFX`. |
| NightOnly / luzes | `NIGHT_ONLY` = `L_OPProp_`, `L_OPCap_Win_`; `LIGHT_KEEP` = `L_OPCas`, `L_OPSum`, portão; override de interior `L_OPCas_Hall_` (Range 18). |
| Montagem | Import pelo botão Import do ribbon → `montar_ilha_onepiece.lua` → `ServerStorage.IlhaOnePiece`; clone em runtime em `workspace.Areas.Area5` pelo `IslandWorld` (1 linha). O place não é salvo pelo agente. |

### 1.4 O que NÃO reaproveitar
| Não usar | No lugar |
|---|---|
| Layout DS (clareira longitudinal, forja, glicínia) | Capital em terraços em volta de castelo + árvore, porto lateral |
| Casas DS (madeira escura, noite) / Konoha (terracota) | Reboco claro, telha azul-escura por conjunto, alguns telhados verdes/vermelhos, vermelho e dourado seletivos |
| Mar de nuvens noturno (DS) | Mar turquesa diurno local (cliente, só área 5) |
| Arena redonda / anel de casas | Praça retangular-orgânica aberta para o porto a leste; casas por quarteirão, não em anel |
| Frutas, combate, chefes, navegação, dungeon, alquimia | Nada disso |

---

## 2. Leitura das referências

**ref_01 (concept aprovada, define a composição)** — câmera alta ao sul, no eixo:
- embaixo, ponte reta com guarda-corpo vermelho e tabuleiro escuro chegando a um **grande torii** na ponta de uma falésia, com lanternas e 2 nobori vermelhos;
- escada → rua curta com lojas → escadaria → **praça ampla** com emblema de chão e 4 estandartes brancos;
- ao fundo e no alto: **castelo** branco de telhados azul-escuros sobre um rochedo com **cachoeira central** e estandartes, um portão vermelho no pé; **árvore em arco** nascendo atrás-direita e passando por cima, copa rosa;
- esquerda: bairros em terraços, **ponte vermelha** sobre canal, **roda d'água**, **cachoeira para o mar**, pagode vermelho num pináculo;
- direita: casas, **porto** com cais de madeira e palafitas de guarda-corpo vermelho, **navio** com vela de caveira de chapéu de palha, **caveira com chifres** na rocha, ponte vermelha arqueada indo para ela; espada gigante e pináculos ao fundo.

**ref_02 (anime)** — câmera baixa na cidade: castelo sobre rocha com várias quedas e portão dourado na base; tronco nasce à direita/atrás, sobe, faz o arco por cima e termina à esquerda com pinheiros; pontes vermelhas arqueadas dos lados.

**O que preservo / adapto:**
| Elemento | Decisão |
|---|---|
| Castelo + árvore arqueada (marco) | Preservado como hero. Árvore com **copa rosa** (concept), arco à direita→cima→esquerda (anime). |
| Ponte + grande torii | Preservado no eixo; a ponte é a de chegada da DS (120). |
| Praça com emblema e estandartes | Preservada, dimensionada para 70 minérios; emblema rente; estandartes só nos cantos. |
| Capital em terraços | 84,2 / 88,2 / 92,2 / 98,2 / 100,2 / 136,2 + porto 42,2/65,2. |
| Canais, pontes vermelhas, roda d'água, quedas | 2 canais, 3 pontes vermelhas (2 no canal + a de saída), 1 roda, 3 quedas com função (não "cachoeira de borda" de enchimento). |
| Porto lateral + navio | Na enseada leste. Vela sem a caveira de chapéu de palha no blockout (iconografia a decidir no M3). |
| Caveira com chifres | Formação na ponta sul do promontório, rosto para a enseada/praça; o caminho da saída passa atrás dela. |
| Espada distante | Cravada no pináculo do esporão NE (só terreno), silhueta rígida, topo 216 < árvore. |
| Pagode | No pináculo oeste, cenográfico. |
| Pináculos/ilhotas do fundo | **Fora** (sem ilhotas soltas); o fundo é a rocha alta atrás do castelo + agulhas presas à ilha. |
| Summon | Adaptação (não está na concept): terraço lateral na transição para o porto. |
| Saída OPM | Adaptação: ponte vermelha da concept que vai para a caveira = ponte de saída. |

---

## 3. Encaixe no mundo

- `WORLD_FROM_PREV` local (0, −120, 80,2) → Roblox (−2054,391; 80,2; 1551,759) = âncora DS, frente (−0,5740; 0,8190) ~ (−0,5736; 0,8192). **Distância 0,0000** (export seco 49b609a4).
- **Folgas** (`op_map`): borda Wano ↔ borda DS **197** (≥ 180, mesma regra do plano DS); ↔ SG 991.
- **Saída:** `ISLAND_EXIT_OnePiece` local (206, 236) → Roblox (−2427,33; 88,2; 1725,22). `GATE_OnePunchMan` (−2530,70; 88,2; 1687,60). **`ISLAND_NEXT_ANCHOR_OnePunchMan` (−2553,25; 88,2; 1679,39)**, frente (−0,9397; 0; −0,3420), Orientation (0; 70; 0), largura 18, altura livre 22, piso 88,2. Rumo local 15° (para fora da enseada); componente radial (lobby → âncora) 0,60.
- **Espaço livre da área 6:** disco r 300 centrado 350 à frente da âncora (Roblox −2882; 1560) fica a 514 da DS, 1249 da SG e 50 de Wano → a ilha OPM deve nascer com ponte própria ≥ 60.
- **Mar e transição:** mar local turquesa (nível 36, quadrado 2200 em volta de Wano) só no cliente e só com o jogador na área 5. De Wano, a DS aparece saindo do mar (o topo da quilha DS é 53,6 > 36). Da DS, Wano flutua sobre as nuvens (quilha em estratos até −10). A troca céu noite → dia acontece na troca de região (meio da ponte), como SG → DS. Testar ida e volta no Play (risco 3).

---

## 4. Planta (ver `planta_op.png`)

### 4.1 Cotas
| Cota | Nome | O que fica nela |
|---|---|---|
| 36 | mar local | só visual (cliente) |
| 42,2 | **cais** | porto, pier, palafita, armazéns |
| 46,2 | convés do navio | acessível pela prancha (4 de subida em 11,6) |
| 65,2 | rua alta do porto | armazém H3, ligação das escadas |
| 80,2 | deck da âncora | ponte de chegada |
| 84,2 | **T0** pátio do torii | torii, 2 tōrō, 2 nobori |
| 88,2 | **T1** | rua de chegada, viela leste, bairro do canal (SO), **terraço do summon**, promontório da saída |
| 92,2 | **P** | **praça**, quarteirão oeste (2 margens do canal), quarteirão NE (santuário) |
| 98,2 | **CF** adro | bacia da cachoeira, portão vermelho |
| 100,2 | **W3** terraço alto | mansões de telhado verde |
| 117,2 | patamar da subida | |
| 136,2 | **CC** pátio do castelo | torre, varanda vermelha, yagura, base da árvore |
| ~215 / 274–305 | cumeeira da torre / topo do arco e da copa | |

### 4.2 Escadas (espelho ≤ 0,77, piso 1,8; guardas nos lados abertos)
| Nome | Pé (x, y, z) | Rumo | Largura | Degraus | Chega em |
|---|---|---|---|---|---|
| Chegada | (0, 34, 84,2) | N | 16 | 6 × 0,667 | T1 |
| Praca | (0, 109, 88,2) | N | 28 | 6 × 0,667 | Praça |
| Summon | (127, 216, 88,2) | O | 14 | 6 × 0,667 | Praça (lado leste) |
| Sudoeste | (−140, 109, 88,2) | N | 10 | 6 × 0,667 | Quarteirão oeste |
| OesteAlta | (−110, 288, 92,2) | N | 12 | 11 × 0,727 | Terraço alto |
| Adro | (0, 312,6, 92,2) | N | 30 | 8 × 0,75 | Adro (sob o portão vermelho) |
| CasteloA / B | (−71, 336 / 394) | N | 12 | 25 + 25 × 0,76 | Patamar 117,2 → pátio 136,2 |
| PortoA | (200,8, 140, 65,2) | O | 12 | 30 × 0,767 | Mirante do porto (T1) |
| PortoB | (160, 46, 42,2) | N | 12 | 30 × 0,767 | Rua alta do porto |

### 4.3 Setores
- **Entrada (y −120..44).** Ponte de 120 (tabuleiro escuro, guarda-corpo vermelho com remates dourados, 5 pares de pilares de pedra afinando até a quilha, 2 lanternas no meio) → **grande torii** (vão 18 × 22, escala 1,2, kasagi preto de pontas levantadas, placa dourada) em (0, 10) → pátio T0 ladeado por rochas com cerejeiras.
- **Rua de chegada (T1, x ±12, y 44..112).** 6 fachadas comerciais de alturas/recuos diferentes (C1–C7: lojas de 1–2 pisos, 1 esquina de 3 pisos com telhado vermelho = marco), noren índigo, alpendres; recanto de descanso com banco e cerejeira na viela do canal (y 80..93); fileiras de fundo (B1–B7). Viela leste (y 104..118) leva ao summon sem entrar na praça.
- **Praça (P).** Ver seção 5.
- **Quarteirão oeste (P).** Fileira que encara a praça (W1–W5: comércio, pavilhão aberto, 2 esquinas) e, do outro lado do **canal oeste**, casas (X1–X3) ligadas por **2 pontes vermelhas** (y 182 e 252); vielas entre os prédios (y 159 e 265).
- **Bairro do canal (T1, SO).** Casas baixas (S1–S5), **moinho** com a **roda d'água** no canal e a **queda oeste** na falésia.
- **Terraço alto oeste (W3).** Mansões de telhado verde (U1, U2), casas, pavilhão; o **pagode** de 5 andares fica no pináculo oeste (cenográfico, rocha até 158).
- **Quarteirão NE (P).** Santuário de telhado vermelho com torii pequeno, casas de telhado avermelhado (conjunto de cor), canal leste atrás.
- **Adro e castelo.** Portão vermelho (vão 36) sobre o topo da escada Adro, enquadrando a **bacia** e a **cachoeira**; 2 estandartes gigantes na face da rocha; colunas de rocha nos flancos; subida pelo flanco oeste (2 lances) → portão do pátio → pátio em proa com **guarda-corpo vermelho** (mirante) → **torre** (porta aberta, salão real) → base da árvore no fundo-leste.
- **Summon (T1).** Terraço x 116..206, y 150..264; torre em (170, 214) virada para a praça; laje clara, 2 tōrō, guarda-corpo vermelho nas bordas que dão para o porto.
- **Porto.** Rua alta (65,2) com armazém de 2 pisos, cais 42,2 com 2 armazéns, palafita com pavilhão vermelho sobre a água, pier de 90 com cabeços e defensas, **navio** atracado (proa para a saída da enseada), 2 barcos.
- **Saída.** Ponte vermelha (88, guarda-corpo vermelho com remates dourados, arco vermelho por baixo, 2 pilares de pedra na água) → promontório (laje, 2 lanternas, cerejeira) → portão OPM → âncora com guarda provisória. A caveira fica ao sul do caminho; a espada ao fundo.

### 4.4 Construções do blockout (40)
`BUILDINGS` em `op_layout`: famílias **loja, casa, esquina, pavilhão, mansão, santuário, armazém, moinho**; cada uma com gesto próprio (loja: treliça + noren + alpendre; esquina: pisos recuados com saia e varanda; santuário: frente de laca vermelha e estrado; armazém: reboco grosso e base escura; pavilhão: aberto). Cor do telhado **por conjunto**: rua de chegada azul (+1 esquina vermelha), oeste azul com esquinas verdes, terraço alto verde, NE vermelho, porto azul/vermelho. `op_map` confere: todas sobre o piso da cota certa, fora da MiningZone + 8, fora de escadas e pontes, sem sobreposição.

---

## 5. Praça de mineração

| Item | Valor |
|---|---|
| Paving (`PLAZA`) | x −116..116, y 120..314 (cantos chanfrados, abre a leste para o summon/porto e a norte para o adro) |
| **MiningZone_OnePiece** | x −76..76, y 156..276 → **152 × 120**, centro local (0, 216) / Roblox (−2247,11; 92,2; 1826,99), frente +Y |
| Margens livres | S 36 (chegada da escadaria), N 38 (pé da escada do adro), O 40 (frente do quarteirão oeste), L 40 (escada do summon) |
| `ORE_*` | 72 = SUPERLEGENDARY 2, EPIC 10, UNCOMMON 22, COMMON 38; grade hex em elipse; raridade pela profundidade (comum perto da chegada, super perto do castelo); 0 fora da zona, 0 sobrepostos |
| `GP_Block_*` | 48 "borda" (+3) + 28 "canto" (área útil em elipse) |
| Livre | Nada colidível de 92,5 a 104,2 dentro da zona (`PRACA_LIVRE` OK); piso plano (`PRACA_PISO` 0 pontos fora) |
| Emblema | anel + 8 pétalas + miolo, `Stone_OP_Inlay`, 0,24 acima do piso, sem colisão (no M2: rebaixo/junta, não relevo) |
| Estandartes | 4 mastros brancos com brasão índigo nos cantos, fora da zona + 8, com colisão de 1,4 |
| Unidades/pets | Margens de 34–40 + corredores entre as fileiras de minério (passo hex ≥ 10,4) |

---

## 6. Narrativa espacial

| Capítulo | Emoção | Densidade | O que tem |
|---|---|---|---|
| Ponte | Chegada, promessa | Baixa | Ponte vermelha, castelo e árvore já visíveis por cima do torii (visada OK do início da ponte) |
| Torii / pátio | Moldura | Baixa-média | Grande torii, tōrō, nobori, cerejeiras nos ombros de rocha |
| Rua de chegada | Vida, comércio | **Alta** | Fachadas próximas, alturas variadas, recanto; castelo no fim da rua |
| Praça | Revelação, jogo | **Muito baixa no centro**, média na borda | Piso amplo, emblema, estandartes; a cachoeira e o castelo emoldurados pelo portão vermelho |
| Castelo | Monumento | Alta (herói) | Subida, mirante vermelho, salão |
| Summon | Especial | Média | Torre AMS sobre o porto |
| Porto | Abertura, mar | Média | Navio, cais, palafita, caveira ao fundo |
| Saída | Próximo mundo | Baixa | Ponte vermelha, caveira, portão OPM |

---

## 7. Contrato de marcadores (dono: `op_core`)
- **Mundo:** `WORLD_FROM_PREV` (0, −120, 80,2; width 18, bridge_len 120); `WORLD_ENTRY_OnePiece` (0, 24, 84,4); `PATH_ENTRY_CENTER(_00..10)`; `ISLAND_EXIT_OnePiece` (206, 236, 88,2, heading 15); `ISLAND_NEXT_ANCHOR_OnePunchMan` (next_area 6, next_key OnePunchMan, clear_h 22, fwd/pos/orientation Roblox, guard).
- **Mineração:** `ORE_<RARIDADE>_<nn>` (72), `MiningZone_OnePiece`, `GP_Block_<nn>` (76).
- **Invocação:** `SUMMON_Main` (170, 214, 88,2, frente −X), `SUMMON_Interact` (d 7), `SUMMON_PlayerPosition` (d 16).
- **Portão OPM (`il_gate_std`):** `GATE_OnePunchMan` (+ `_LOCKED`, `_INTERACT`, `_EXIT`, `_OpenFX`), `PURCHASE_UI_ANCHOR_OnePunchMan`, `COL_GateOnePunchManLock_001`, `area_id` 6.
- **Guarda provisória:** `OP_Exit_AnchorGuard` + `COL_OPAnchorGuard_001` (`next_island_guard`), tag `GuardaProximaIlha` no montar.
- **Seguros (17):** `SAFE_Entrada, Ponte_Chegada, Rua_Chegada, Praca_S/N/O/L, Summon, Bairro_Canal, Oeste_Alem, Terraco_Alto, Adro, Castelo, Porto_Alto, Cais, NE, Promontorio`.
- **Áudio:** `AUDIO_Plaza` (wind 130), `Street` (wind 50 baixo), `CastleFall` (water 60), `FallE` (60), `FallW` (55), `Wheel` (30), `Harbor` (80), `Summon` (energy 36), `Castle` (wind 60). Sem trilha nova.
- **Água/efeitos:** `WATER_Sea` (client_only, area 5, nível 36, 2200), `WATER_Basin`, `WATER_CanalE`, `WATER_CanalW`, `FX_Fall_Castle_Lip/Base`, `FX_Fall_E_Lip/Base`, `FX_Fall_W_Lip/Base`, `FX_Weir_E/W`, `FX_Spring_W`, `FX_Petals_Tree` (1 emissor, Dist 320), `FX_Mist_CastleFall`.
- **Móveis:** `VFX_OP_Wheel` (pivô/eixo/rpm), `VFX_OPSUM_*`, `VFX_GATE_OnePunchMan_*`.

---

## 8. Kit e paleta

### 8.1 Kit (M2 cria `op_kit.py`; pequenas famílias)
Fundações de pedra (ishigaki com junta rebaixada) e socos; paredes de reboco claro entre pilares/vigas escuros; telhados irimoya/kirizuma/saias com **beiral com espessura, cumeeira, onigawara, cantos levantados**, telha em canais (azul, verde, vermelho); fachada comercial (treliça koshi, noren, alpendre, vitrine cenográfica com profundidade); janela (moldura + recuo + papel aceso ≥ 0,12 atrás); porta (aberta só onde há interior); varanda/guarda-corpo vermelho; lanterna de poste/parede/tōrō; estandarte; escada de pedra; ponte vermelha (tabuleiro contínuo, arco, encontro com patamar); prancha/cais/estacas; barril/caixa/cerâmica com boca e borda.

### 8.2 Paleta `OPMATS` (op_lib)
| Material | RGB | Uso |
|---|---|---|
| `Plaster_OP` / `_Warm` / `_Shop` | 234,228,212 / 226,210,182 / 214,196,164 | castelo, casas, lojas (POR CONJUNTO) |
| `Wood_OP_Dark` / `_Mid` / `_Hull` | 66,46,34 / 128,92,60 / 104,66,42 | estrutura, tábuas, casco |
| `Wood_OP_Lacquer` | 186,42,34 | **só** torii, pontes, varandas, portões, palafita |
| `Roof_OP_Blue` / `_Green` / `_Red` / `_Ridge` / `_Shingle` | 46,58,92 / 58,104,84 / 150,62,46 / 30,36,54 / 92,70,52 | telhados por conjunto |
| `Metal_OP_Gold` | 220,172,70 | shachihoko, remates, guarda da espada (seletivo) |
| `Stone_OP` / `_Path` / `_Plaza` / `_Inlay` / `_Dark` | 160,154,142 / 206,196,172 / 196,186,162 / 150,128,98 / 100,98,96 | pedra, caminhos, praça, emblema |
| `Cliff_OP` / `_Dark` / `_Moss` / `_Void` / `_Horn` | 132,134,140 / 94,98,108 / 90,128,70 / 38,40,48 / 58,56,62 | falésias claras (concept), quilha/caveira |
| `Grass_OP`, `Leaf_OP`, `Leaf_OP_Pine` | 108,156,74 / 66,122,62 / 44,94,62 | vegetação diurna |
| `Flower_OP_Blossom` / `_Light` | 240,150,198 / 250,196,224 | cerejeiras (acento) e copa da árvore |
| `Cloth_OP_White/Indigo/Red/Sail` | | estandartes, noren, nobori, velas |
| `Glass_OP_Lantern` (Neon), `Window_OP_Warm` | | luz SÓ dentro de armação |

Regra de valor (dia): praça/caminho claro-quente ≈ reboco > pedra > falésia cinza-clara > vegetação > madeira > telha azul (a mais escura). Validado em `FM_MAT_PREVIEW=roblox` (folha `FOLHA_previa_x_roblox_M1.jpg`): tudo distinguível.

---

## 9. Orçamento (≤ 620k tris / ≤ 650 MeshParts estáticos)

| Dono (prefixo) | Tris | MeshParts | Observação |
|---|---|---|---|
| terrain `OP_Ter_` | 100k | 75 | estratos/colunas, arrimos com junta só na faixa do jogador |
| entry `OP_Ent_` | 30k | 32 | ponte (tramo repetido), torii, pátio |
| capital `OP_Cap_` | 130k | 130 | ~36 construções por kit instanciado (~3,5k cada; fundos simples) |
| plaza `OP_Plz_` | 20k | 24 | paving com juntas, emblema, estandartes |
| castle `OP_Cas_` | 70k | 55 | torre Tier A até +25 e no salão, Tier B acima |
| tree `OP_Tree_` | 40k | 30 | tronco/raízes Tier A só até +20 do pátio; copa em massas |
| harbor `OP_Port_` | 35k | 40 | cais, pier, palafita, armazéns |
| ship `OP_Ship_` | 18k | 16 | casco, convés, mastros, velas |
| summon `OP_Sum_` | 34k | 40 | torre reaproveitada (~29k) + base Wano |
| exit `OP_Exit_` | 18k | 24 | ponte vermelha, promontório |
| gate_opm `GATE_` | 28k | 38 | asset da galeria |
| landmarks `OP_Lmk_` | 14k | 14 | caveira, espada, pagode (silhueta) |
| water `OP_Water_` | 10k | 16 | pedra dos canais/bacia |
| props `OP_Prop_` | 25k | 35 | lanternas, estandartes, barris, bancas |
| vegetation `OP_Veg_` | 45k | 45 | cerejeiras/pinheiros em conjuntos |
| **Total estático** | **617k** | **614** | VFX (reserva) 15k / 30 |

`ER.BUDGET`: static 620k/650, vfx 15k/30, materiais 110, shadow 260, **luzes de dia 36**, **col 1300**. Tetos por dono = tabela + 8% (`export_op.BUDGET_OWNER`); por zona em `studio_op.BUDGET`.
**Medido no M1:** 71,2k tris, ~201 MeshParts, 57 materiais, 7 luzes de dia (29 NightOnly), col 985 no Blender → 519 depois da união do export.
**FPS:** medir no Play (M5) na praça, no porto, no pátio do castelo e na cabeça da ponte olhando a DS (DS 599,6k + Wano visíveis juntas; risco 1).

---

## 10. Luz (dia) — perfil `[5]` do AreaAtmosphere (valores iniciais, ajustar no Play)
| Propriedade | Valor |
|---|---|
| ClockTime / GeographicLatitude | 13,5 / 30 (sol alto vindo de trás-esquerda de quem chega: fachada sul do castelo clara) |
| Brightness / ExposureCompensation | 2,6 / 0 |
| Ambient / OutdoorAmbient | (138,146,164) / (150,162,182) |
| EnvironmentDiffuse / Specular | 0,6 / 0,3 |
| Atmosphere | Density 0,26, Offset 0,15, Color (196,220,246), Decay (112,156,206), Glare 0,15, Haze 1,0 |
| Bloom | Intensity 0,35, Size 24, Threshold 1,6 (brancos do reboco não estouram) |
| ColorCorrection | Brightness 0,02, Contrast 0,06, Saturation 0,10, Tint (255,250,244) |
| SunRays | 0,04 / 0,12 |
| Céu | skybox diurno padrão do jogo (sem trilha nova); nuvens opcionais |

Hierarquia: sol > núcleo/estrela do summon > salão do castelo > janelas (NightOnly) > lanternas (NightOnly). Neon só dentro de armação. Sem névoa para esconder arquitetura.

---

## 11. Câmeras de QA (`op_layout.cams()` + `op_scene.extra_cams()`)
- **Referência:** `CAM_OP_Ref_01` (14, −170, 214) → (24, 300, 50), 18 mm = enquadramento da concept; `CAM_OP_Ref_02` (0, 196, 101,2) → (0, 420, 200), 22 mm = enquadramento da ref do anime (castelo + arco visto da praça).
- **Gerais:** Front, Back, Left, Right, BirdEye, Orbit_0..7 (360°).
- **Setores:** Entry, Plaza, Castle, Tree, Harbor, Summon, Exit, Skull.
- **Altura do jogador (olho +5,5):** Entry (na ponte), Street, Plaza, Castle (porta), Harbor, Summon, Exit; **Conexão:** OlhaDS, OlhaIlha.

---

## 12. Integração Roblox (M5, lead) — o que o Roblox vai ler
`Core.OnePieceIsland` = cópia do contrato de `DemonSlayerIsland.lua` com: `GATE_KEY 'OnePunchMan'`, `GATE_AREA 6`, `FONTE 'IlhaOnePiece'`, `NOME 'ILHA_ONEPIECE'`, `FONTE_PROXIMA 'IlhaOnePunchMan'`, `ZONA 'MiningZone_OnePiece'`, `PISO 92.2`, `SafeMaxY 150`, `BoundsMinY 28`, `OreMax 80`, invocação com `Gacha_mare`, portão (placa de preço da área 6), água pelos marcadores (bacia em polígono, 2 canais, 3 quedas, degraus, bica, roda), `WATER_Sea` num LocalScript tipo `CeuNatagumo` (mar turquesa só na área 5), sem masmorra/alquimia/trono. 1 linha no `IslandWorld`. A DS não precisa de patch (já espera `IlhaOnePiece`).

---

## 13. Gate do blockout (medido no M1)
| Critério | Resultado |
|---|---|
| Encaixe DS | **0,0000**, frente igual, largura 18, deck 80,2 |
| Rotas (andador: degrau 2,3, queda 2,3, altura 6,5, corpo 1,1) | **15/15 OK** + portão aberto → âncora OK + portão fechado bloqueia + **término seguro** (guarda fecha a âncora); largura ≥ 3,4 em todas |
| Sondas de borda | **28/28** |
| Praça livre / piso | OK / 0 pontos fora |
| Marcadores | 0 faltando; 215 marcadores |
| Técnico | 0 nomes genéricos, 0 duplicados, 0 sem material, 0 transform, 0 degeneradas |
| Marco | árvore 304,6 > castelo 216,4 > cidade 162; summon 148 < castelo; espada/caveira/pagode ≤ 216 |
| Visadas | castelo e árvore do início da ponte e do pátio do torii; castelo do topo da escadaria; cachoeira e estrela do centro da praça; estrela da rua de chegada; mastros do terraço do summon; portão OPM da cabeça da ponte: **10/10** |
| Câmera do jogador | nenhuma PlayerHeight com oclusão < 12 |

---

## 14. Ondas de produção (1 arquivo por agente; ninguém mexe no arquivo de outro)

`op_layout`, `op_lib` (só materiais novos, 1 linha cada), `op_col`, `op_core`, `op_qa`, `build_op`, `studio_op`, `export_op`, `op_scene` (só câmeras novas) são da integração.

**M2 — trecho de qualidade final, validado no Roblox ANTES de multiplicar o kit** (1 agente `op_kit.py` + 1 agente `op_m2_trecho.py`, serial):
1. `op_kit.py`: telhado (irimoya/kirizuma/saia com beiral grosso, cumeeira, onigawara, cantos), parede de reboco entre pilares, janela, porta, fachada comercial, lanterna de poste, piso de laje com junta rebaixada, escada de pedra, guarda-corpo vermelho — folha de close-ups.
2. Trecho: **rua de chegada C1/C2/C5/C6 + escadaria Praca + faixa sul da praça (y 109..170)** — fachada, telhado, lanterna, piso e transição rua → praça (inclui o emblema rebaixado de verdade).
3. Export só do trecho, import no Studio, Play com o avatar: escala, sem textura, bloom, z-fight, colisão. **Só depois o kit é multiplicado.**

**M3 — marcos** (paralelos): `op_castle.py` (torre 360°, salão, adro, portão, subida, varanda), `op_tree.py` (tronco/raízes/copa, casca só até +20 do pátio), `op_harbor.py` + `op_ship.py` (cais, pier, palafita, navio: casco, proa, popa, convés, mastros, velas apoiadas; iconografia da vela a decidir com a aprovada), `op_summon.py` (torre por alias + base Wano).
**M4 — expansão:** `op_terrain.py` (falésias em colunas claras, estratos, fundo/traseira, esporão, arrimos), `op_capital.py` (todas as famílias e instâncias), `op_plaza.py`, `op_water.py` (mede e corrige `FX_*/WATER_*`), `op_exit.py`, `op_landmarks.py` (caveira esculpida na rocha, espada, pagode), `op_veg.py`, `op_props.py`, `op_lights.py`, `op_vfx.py`. Auditoria por família (incluindo o que o usuário não citou).
**M5 — integração Roblox (lead):** backup do place, import, `Core.OnePieceIsland`, `IslandWorld`, `AreaAtmosphere[5]`, céu/mar local; testes: rotas, mineração (70 minérios, dano, quebra, recompensa, respawn), summon real, portão OPM bloqueado/comprado por jogador, travessia DS ↔ Wano, FPS.
**M6 — harmonia/otimização:** auditoria na altura do jogador (método AUDITORIA_DS), z-fight, flutuações, desempenho, limpeza, folhas finais.

Regras para todas as ondas: não modelar minérios (proxy `OP_Plz_OreProxy` só no blockout, removido no export); 3 voltas render → crítica → correção nos 2 modos; Blender `--factory-startup`; renders 960 × 540; sem commit e sem `taskkill`.

---

## 15. Riscos, adaptações e pendências
1. **Desempenho com a DS visível** (DS ~600k + Wano ~620k). Medir na cabeça da ponte; mitigação: Tier C na quilha/fundo/esporão, `RenderFidelity` Automatic, corte de VFX por `Dist`.
2. **Ilha arredondada** (587 × 503, razão 1,17). A forma vem da enseada, do promontório, do lobo SO e dos terraços; o M4 deve reforçar o contorno (falésias em colunas, reentrâncias) sem virar disco. **Trecho reto:** a margem do cais na enseada é reta (215) por ser cais construído — aceito; o resto da borda é orgânico.
3. **Mar local e transição DS ↔ Wano:** troca de céu e mar na região; testar ida e volta. Da DS, Wano flutua (quilha até −10).
4. **Portão OPM:** asset da galeria `il_gate_opm` sem aprovação explícita registrada (mesma galeria do OP aprovado). **Pendência para o usuário confirmar**; se reprovado, trocar só o `opm_gate()` do `op_core`.
5. **Caveira** ainda lê "caveira sobre pedestal" no blockout; o M4 deve fundir crânio, mandíbula e nuca à rocha (formação, não máscara).
6. **Traseira e laterais** da ilha estão em faces lisas de falésia no blockout (vistas Back/Left/Right): obrigatório no M4.
7. **Sem iconografia inventada:** vela do navio e brasão dos estandartes ficam neutros até o M3 escolher entre a iconografia aprovada (chapéu de palha do portão OP, brasão circular da concept).
8. **Colisões:** 985 no Blender (519 após a união do export) para o teto de 1300 — os módulos de detalhe devem colidir por volume simples.
9. **Porto longo** (cais 46 abaixo do summon, 2 lances de 30 degraus): aceitável porque o porto é visita opcional; as ações frequentes (praça ↔ summon ↔ saída) ficam a 6 degraus e ≤ 20 s.
10. **Adaptações registradas:** summon e saída OPM não estão na concept; ponte da concept que vai para a caveira = ponte de saída; pináculos/ilhotas do fundo trocados por agulhas presas à ilha; espada num esporão (não ilhota).
