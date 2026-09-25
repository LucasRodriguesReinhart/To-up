# Onda 2 — prompts das zonas (village, towers, water, exit)

Rascunho usado pelo script de workflow da onda 2. Vale o `AGENT_BRIEF.md` para todas as zonas.

## village → db_village.py (prefixo DB_Hub_, coleção 05_TECH_VILLAGE)
Vila tech, poucas construções de alta qualidade (QUALIDADE > QUANTIDADE). Refs: `refs/ref_village.jpg`
(barracas asiáticas de madeira com telhado laranja, lanternas em postes, domo Capsule, passarela de vidro, palmeiras)
e `ref_main_view`.

**Lotes da vila** (`L.HUB_LOTS`, piso HUB 28,2):
- **capsule_house_A** (−58,100) r11: casa-cápsula.
  - Domo branco sobre tambor, faixa azul, janelas redondas, antena, pequeno anexo.
  - NÃO entrável: sem porta nenhuma.
- **capsule_house_B** (62,98) r10: outra família de forma, não repetir a A. Por exemplo:
  - cápsula deitada (cilindro com pontas em domo);
  - ou dois domos ligados, com teto azul.
  - NÃO entrável.
- **martial_market** (−86,128) r13: mercado marcial ABERTO (pavilhão/barracas).
  - Postes vermelhos, telhado laranja em beiral asiático, lanternas, balcão.
  - Marcadores NPC_Market e PLAYER_INTERACT_Market.
- **workshop** (34,116) r11: oficina tech entrável.
  - Frente de garagem ABERTA em arco arredondado (vão ≥ 7×10).
  - Interior real: bancada, ferramentas, veículo cápsula estacionado, luz interna.
  - Marcadores NPC_Workshop e PLAYER_INTERACT_Workshop.
  - Colisão das paredes com o vão.

**Pods e dojo:**
- 4 pods (`L.PODS`): casas-cápsula pequenas, sem porta, janelas redondas, antena.
- Dojo (`L.GROUND_LOTS` "dojo", (120,−14) r14, piso GROUND 24,2): pavilhão marcial aberto.
  - Piso de madeira elevado com 2 degraus, telhado laranja/vermelho, bonecos de treino, gongo.
  - Colisão dos postes e do piso elevado (degraus ≤ 0,8).

**Corredores livres** (nada de construção nem prop grande neles):
- faixa y 76..88 da vila entre x −100 e 100 (rota CAPSULE→SHADOW_GATE);
- frente das 3 escadas da vila;
- escadaria do Capsule (x ±12, y 118..132).

## towers → db_towers.py (prefixo DB_Twr_, coleção 05_TECH_VILLAGE)
Torres que dão a silhueta (concept: torres brancas finas com topo de disco/cúpula de vidro).
**Não fazer todas iguais.**

**Torres** (`L.TOWER_SITES`):
- **comm** (−104,150): mastro de comunicação alto (~52), anéis azuis, pratos/antenas, luz no topo.
- **lookout** (100,140): mirante com topo "disco voador" envidraçado (~40), como na concept.
- **energy** (74,118): estação de energia (~30): bobinas, orbe ciano, anel girando.
  - Peça móvel `VFX_DBTWR_EnergyRing`, com rpm.

**Satélites andáveis** (`pad_sw` (−148,−98) e `pad_se` (140,−76)):
- plataformas redondas sobre pilar de rocha pendente, com a ponte curta `L.SAT_BRIDGES`;
- guarda-corpos visuais nas linhas das guardas do db_col;
- um farol/mirante pequeno na ponta de fora e um banco ou luneta.

**Passarelas e heliponto:**
- 2 passarelas de vidro (Glass_DB_Blue com costelas brancas) em pilares:
  - do porto do anexo oeste do Capsule (−48,180, z = CAP+10) até a torre comm;
  - do anexo leste (48,176) até o lookout;
  - anel de acoplamento no lado da torre.
- Heliponto Capsule (`L.GROUND_LOTS` "landing_pad" (−140,58) r12):
  - pad com marcações, luzes de pouso;
  - uma aeronave cápsula estacionada (casco arredondado + asas curtas), só visual, com colisão em caixa.

**Colisões:** fuste das torres (octo_col), aeronave e bases.

**VFX:**
- radar girando (`VFX_DBTWR_Radar`);
- anel de energia;
- orbe com bob.

## water → db_water.py (prefixo DB_Water_, coleção 07_WATER)
Água com moderação (poucas quedas, canais coerentes).
- **Poços SW e SE:**
  - `L.POOL_SW` (−82,−88) r8 e `L.POOL_SE` (80,−84) r7;
  - lâmina em GROUND−0,8, borda de pedra/rocha;
  - canal de 4,8 até `L.FALL_SW` / `L.FALL_SE` (a mesma faixa do `db_col.water_polys`).
- **Quedas pela borda:**
  - começam no lábio (o terreno deixa um entalhe de 7) e descem pelo penhasco até as nuvens (~−60);
  - espuma no lábio (fm_water_kit.cascade / fall_path / ribbon).
- **Poço NW** (`L.POOL_NW` (−108,96) r10, lâmina HUB−0,8, na vila):
  - cascata da mesa NW a partir de `L.CASCADE_NW_TOP` (−132,110,70), descendo em 2–3 degraus pelas saliências até o poço (ref_environment);
  - espuma e rochas em volta.
- Materiais: `Water_DB`, `Water_Fall`, `Foam`.
- Sem colisão nova (o db_col já tem o leito).

## exit → db_exit.py (prefixo DB_Exit_, coleção 08_NEXT_ISLAND)
DRAGON BALL → TRILHA → ARCO → PONTE → PORTÃO DE COMPRA SHADOW GARDEN (asset aprovado, já no db_core) → ÂNCORA.
- **Escada e prateleira:**
  - escada visual db_col "Exit";
  - prateleira da saída (`L.EXIT_PATH` hw 9 + `L.HUB_EXIT_LINK` hw 7, topo EXIT_Z 28,2) com calçamento;
  - muros laterais do GROUND até EXIT_Z e parapeitos nas linhas das guardas do db_col.
- **ARCO NATURAL** de rocha sobre a trilha em `L.EXIT_ARCH`:
  - vão ≥ 18 de largura × 22 de altura;
  - pernas fora da faixa da trilha, massa de arenito com estratos: um marco;
  - colisão das pernas (octo_col).
- **Transição Shadow Garden** (começa depois do arco, discreta):
  - pedra mais escura (Stone_DB_Dusk, Cliff_Rock_DB_Dusk);
  - acentos roxos (lanternas pequenas P_Shadow_Glow);
  - vegetação menos quente (1–2 árvores secas);
  - no máximo 2 luzes.
  - NÃO transformar Dragon Ball em Shadow Garden.
- **Ponte de saída:**
  - `L.EXIT_START`, rumo `L.EXIT_DEG`, 64 de comprimento, 18 de largura, tabuleiro EXIT_Z;
  - pilares até as nuvens e parapeitos;
  - o estilo muda aos poucos para pedra escura perto da ilhota.
- **Ilhota do portão** (`L.islet_center()` r22):
  - massa de rocha pendente e calçamento em volta do portão;
  - **o portão NÃO é seu**: não modificar nem duplicar `GATE_ShadowGarden*`;
  - plataforma da âncora com a guarda provisória `DB_Exit_AnchorGuard` (2 pilones + corrente), mantendo nome e prop `next_island_guard`.
- **Colisões:** o piso e as guardas já estão no db_col; as pernas do arco e os pilones são seus.
