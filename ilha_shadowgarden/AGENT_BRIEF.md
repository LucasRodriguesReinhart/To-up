# Brief comum: produção da Ilha 3 (Shadow Garden)

Você é um dos agentes da produção. O **blockout já passou no portão de qualidade**: planta, níveis, rotas (14/14),
sondas (14/14), salão livre e dungeon limpa. Seu trabalho é transformar UMA zona do blockout em arte final jogável,
**sem mudar a planta**.

Pasta do projeto: `C:\Users\lucas\OneDrive\Desktop\To up\ilha_shadowgarden` (abaixo, `ilha_shadowgarden/`).

Pipeline reaproveitado (só leitura):
- lobby: `C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\forja_mineradora` (`fm_lib`, `fm_parts`, kits);
- Ilha 1: `C:\Users\lucas\OneDrive\Desktop\To up\ilha_naruto` (`il_lib`, kits de portão e summon, andador de QA);
- Ilha 2: `C:\Users\lucas\OneDrive\Desktop\To up\ilha_dragonball` (`db_*`). **Pipeline, não layout nem estilo.**

## 0. A regra que manda
A direção de arte é **ELEGÂNCIA ESCURA**. Tudo o que foge dela é erro.

**Paleta e luz**
- Pedra escura fria (azul-ardósia), navy, madeira escura, ardósia e prata.
- Noite ao luar: luz fria vinda de noroeste, céu navy/roxo.
- Interiores e janelas QUENTES (âmbar), pontuais.

**Roxo dessaturado é só ACENTO de função**
- Só nestes pontos: portal da dungeon, invocação, craft, rosácea do castelo e barreira do portão.
- Nada de roxo espalhado.

**Hierarquia visual (do mais forte ao mais fraco)**
1. castelo;
2. Mining Hall;
3. entrada;
4. dungeon;
5. craft;
6. saída;
7. vila.

A vila é **só ambientação**: poucas casas de qualidade, com espaço negativo.

**Evitar o "visual de IA"**
- Nada de prop de enchimento.
- Nada de estandarte, cristal, vela, partícula ou lanterna sem motivo.
- Nada de "vazio preenchido automaticamente".
- Cada peça tem que ter função: ou de leitura (marca o caminho, emoldura a vista), ou de jogo.

**Ordem de trabalho:** primeiro faz funcionar, depois faz ficar bonito, depois **tira o que ficou exagerado**.

## 1. Leia antes de começar
- **Concept APROVADA:** `ilha_shadowgarden/refs/concept_sg_aprovado.png`, mais os recortes `refs/ref_*.jpg`: `ref_main_view`, `ref_view_front/side/back/top`, `ref_castle`, `ref_mining_hall`, `ref_craft`, `ref_dungeon`, `ref_dungeon_ext`, `ref_village`, `ref_entry`, `ref_summon`, `ref_exit`.
  - Abra com Read.
  - É DIREÇÃO DE ARTE e INTENÇÃO de layout.
  - A leitura e as correções já decididas estão em `ilha_shadowgarden/REFERENCIA.md` (leia).
- **`sg_layout.py`: a planta TRAVADA.** Níveis, contornos dos patamares, escadas, pontes, castelo, salão, torres, craft, dungeon, casas, ruas, cachoeiras, colunas de basalto e pinheiros.
  - Todas as posições vêm daqui.
  - Nunca escreva coordenada "no olho" que contradiga a planta.
- `renders/_mapa_planta.png`: a planta vista de cima (gerada por `python sg_map.py`).
- **Renders do blockout:** `renders/blockout_v1/*.jpg`.
- `sg_blockout.py`: a versão blockout da sua zona (posições, volumes, colisões próprias e luzes).
- **`sg_lib.py`:**
  - paleta `SMATS`: `Cliff_Rock_SG/_Dark/_Top`, `Grass_SG`, `Dirt_SG`, `Stone_Paving_SG`, `Stone_SG_Block`, `Stone_SG_Castle`, `Stone_SG_Trim`, `Stone_SG_Floor`, `Roof_SG_Slate`, `Roof_SG_Navy`, `Wood_SG_Dark`, `Plaster_SG`, `Metal_SG_Iron`, `Metal_SG_Silver`, `Cloth_SG_Navy`, `Cloth_SG_Violet`, `Glass_SG_Rose`, `Leaf_SG_Pine`, `Water_SG`, `SG_Violet_Glow`, `SG_Moon_Glow`;
  - helpers: `dome`, `spire`, `blob_poly`, `ngon_col`, `octo_col`, `box_walls_col`, `plan_stair`, `vis_stairs`, `vis_parapet`, `vis_fence`, `dummy`, `ray_poly`.
- **`sg_col.py`: a colisão de tudo que é andável já existe e está congelada** (ver seção 3).
- **Biblioteca do lobby** (reaproveite; não reescreva o que já existe):
  - `fm_lib.py`: classe `MB` com `box`, `box2`, `beam`, `cyl`, `rod`, `ico`, `rock`, `prism`, `sweep`, `tube`, `quad`, `tri` e `gable_roof`; mais `col_box`, `col_box2`, `col_ramp`, `light` e `camera`;
  - `fm_parts.py`: `stairs`, `fence`, `stone_parapet`, `lantern`, `pave_poly`, `pave_ring`, `masonry_wall`, `arch`, `rock_column`, `cliff_band`, `frustum`, `Frame`;
  - os kits `fm_arch_kit.py`, `fm_veg_kit.py`, `fm_water_kit.py`, `fm_props_kit.py` e `fm_portal_kit.py`.

## 2. Arquivos
- Você só **cria e edita** `ilha_shadowgarden/sg_<sua_zona>.py`, helpers opcionais `sg_<sua_zona>_*.py` e os seus renders em `ilha_shadowgarden/_studio/<sua_zona>/`.
- **Não edite:**
  - `sg_layout.py`, `sg_lib.py`, `sg_col.py`, `sg_core.py`, `sg_blockout.py`, `sg_scene.py`, `build_sg.py`, `studio_sg.py`, `sg_qa.py`, `sg_map.py`, `run.sh`;
  - os módulos de outros agentes;
  - nada em `ilha_naruto/`, `ilha_dragonball/` ou `lobby_area/`.
- Precisa mudar a planta ou um arquivo compartilhado? NÃO mude. Descreva o pedido em `requests` no relatório.
- Não apague arquivos que não são seus. Não faça `git commit` nem `git push`.

## 3. Colisão: quem faz o quê
- **O `sg_col` + `sg_core` (sempre, congelados) já criam a colisão de:**
  - todo PISO dos patamares: `P1` 36,2, `P2` 44,2, `P3` 52,2, `Summon` 40,2, pátio baixo `DECK` 28,2 e calçada alta;
  - todas as ESCADAS da planta (rampas);
  - as 3 pontes, a ilhota do portão Demon Slayer e a bacia da fonte;
  - as GUARDAS invisíveis de toda borda com queda maior que 2,3 (menos topo de escada e cabeceira de ponte);
  - o portão Demon Slayer;
  - **TODOS os marcadores de gameplay** (`ORE_*`, `SUMMON_*`, `CRAFT_*`, `DUNGEON_*`, `DUN_*`, `AUDIO_*`, `FX_*`, `WORLD_*`, `ISLAND_*`, `GATE_*`). **Você não cria marcador de gameplay.** Você constrói EM VOLTA deles.
- **O seu módulo desenha o VISUAL disso, sem colisão:**
  - escadas com `sg_lib.plan_stair(mb, "<nome>")`, que casa exato com a colisão;
  - guarda-corpos com `vis_parapet`/`vis_fence` (`col=False`) nas bordas.
- **O seu módulo cria colisão SÓ dos próprios volumes:** paredes de prédio (com vão na porta), torres, muralha e props grandes.
  - Use `col_box`, `col_box2`, `octo_col`, `ngon_col` ou `box_walls_col`: caixas simples, NADA de colisão por malha.
  - O nome da área começa com `SG_` mais a zona, p.ex. `col_box("SG_CasWall", ...)`.
- **O topo do seu visual tem que bater com as cotas.** Visual acima do piso de colisão = flutua; abaixo = afunda. Não crie piso duplicado andável.

## 4. Contrato do módulo
- `build()` sem argumentos cria tudo da zona. Ele SUBSTITUI a função da zona no `sg_blockout` (inclusive as colisões próprias e as luzes que ela criava: refaça o que continuar valendo).
- **Nomes:** `SG_<Zona>_<Coisa>`, únicos e descritivos. Nada de `Cube`, `Cylinder` ou `.001`.
- **O prefixo define o dono no export do Roblox:**
  - `SG_Ter_` terreno, `SG_Ent_` entrada, `SG_Vil_` vila, `SG_Cas_` castelo, `SG_Hall_` Mining Hall;
  - `SG_Sum_` summon, `SG_Craft_` craft, `SG_Dun_` dungeon, `SG_Water_` água, `SG_Exit_` saída;
  - `SG_Veg_` vegetação, `SG_Prop_` props, `SG_Sky_` fundo.
- **Coleções:**
  - `02_TERRAIN`, `03_MINING_HALL`, `04_CASTLE`, `05_VILLAGE`, `06_SUMMON`, `07_WATER`, `08_NEXT_ISLAND`, `09_PROPS`, `10_VEGETATION`, `16_CRAFT`, `17_DUNGEON`, `18_ENTRY`;
  - luzes em `11_LIGHTING` (o `fm_lib.light` já põe lá).
- **Peças que se movem:** objeto separado com nome `VFX_SG<ZONA>_<Coisa>` na coleção `12_VFX_HELPERS`, com as propriedades `pivot` = (x, y, z) mundo, `axis` = (x, y, z) e `rpm` (ou `bob`). Poucas, e só com função.
- **Luzes:** `fm_lib.light(nome, "POINT", loc, energia, cor, raio)` com nome `L_SG<Zona>_<Coisa>`.
  - Respeite o teto de luzes da zona.
  - Quente em janela, lanterna e interior; fria (luar) só onde a lua não chega.
- **Câmeras de revisão:** dicionário `CAMS = {"CAM_SG<Zona>_<Vista>": (loc, alvo, lente)}` no topo do módulo.
  - Inclua frente, trás, os 2 lados e ALTURA DO JOGADOR (olho 5,2 acima do piso, lente 20–24).
  - Revisão 360°.
- **Rotas e sondas extras das peças novas:** `EXTRA_ROUTES = {nome: (pontos_xy, z_inicial)}` e `EXTRA_PROBES = [(nome, x, y, z_piso, dx, dy)]` no módulo. O `sg_qa` roda.
- **Determinístico** (sementes fixas), sem `bpy.ops`, com o build da zona abaixo de 20 s.

## 5. Escala e jogabilidade (Roblox)
- 1 BU = 1 stud, Z para cima. O jogador tem 5,2 de altura; os bonecos cinza `SCALE_Dummy_*` aparecem nos renders.
- **Prédio entrável (castelo/salão, craft, portaria da dungeon, salas):**
  - portas com vão de pelo menos 7 × 10;
  - pé-direito interno de pelo menos 14;
  - interior de verdade: piso, paredes, teto, circulação, espaço de câmera e colisão coerente.
- **Prédio NÃO entrável (casas da vila, alas do castelo):** SEM porta nenhuma, nem falsa. Use janelas quentes, varandas, empenas, chaminés, lojas com persiana fechada. **Nada de fachada falsa** (porta que dá em parede).
- **Escadas:** espelho de no máximo 0,8, piso de pelo menos 1,6, largura de pelo menos 6. O andador do QA sobe no máximo 2,3 e cai no máximo 2,3.
- **As rotas do `sg_qa.py` têm que continuar todas OK:** ROTAS 14/14, ROTAS_ABERTAS 1/1, SONDAS 14/14, `SALAO_LIVRE` OK e `DUNGEON_LIMPA` OK. Nada seu pode bloquear um caminho.
- **NÃO MODELE MINÉRIO, NEM CRISTAL OU PEDRA FLUTUANTE QUE PAREÇA MINÉRIO.** Os minérios são do jogo: o `SpawnMinerio` gera nos `ORE_*` do salão, e a dungeon usa os `DUN_ORE_*`.
  - Dentro de `MINE_RECT` (a zona de minério do salão), **nada colidível** entre o piso+0,3 e o piso+12.
  - Nada de objeto solto no chão da zona.

## 6. Materiais
- Use a paleta `SMATS` (`sg_lib`) e as existentes: `Lantern_Glow`, `Window_Warm`, `Water_Fall`, `Foam`, `Leaf_*`, `Bark`, `Cloth_*`, `Metal_Gold` (pouco).
- **Material novo:**
  - registre com `fm_lib.MATS.setdefault(nome, (fm_lib.S(r,g,b), rough, metal, emissao, cor_emissao, 0.0))`;
  - o nome começa pelo prefixo de família do lobby (`Stone_`, `Plaster_`, `Metal_`, `Roof_`, `Wood_`, `Cliff_Rock_`, `Grass_`, `Leaf_`, `Cloth_`, `Glass_SG`) e traz a zona, p.ex. `Stone_SGCasCarved`;
  - brilho: prefixo `SG_` e `Glow` no nome (vira Neon);
  - respeite o teto de materiais novos da zona.
- **Neon só em energia de função:** portal, invocação, caldeirão, rosácea e janelas raras.

## 7. Orçamento (o `studio_sg.py` mede e avisa)

| zona | tris | MeshParts est. | mat. novos | colisões próprias | luzes |
|---|---|---|---|---|---|
| terrain | 90k | 110 | 6 | 80 | 0 |
| entry | 30k | 40 | 3 | 40 | 4 |
| village | 60k | 90 | 5 | 80 | 5 |
| castle | 90k | 110 | 6 | 140 | 4 |
| hall | 30k | 40 | 3 | 30 | 6 |
| summon | 35k | 45 | 4 | 40 | 3 |
| craft | 30k | 40 | 4 | 60 | 3 |
| dungeon | 40k | 55 | 4 | 120 | 6 |
| water | 15k | 25 | 2 | 10 | 0 |
| exit | 20k | 30 | 3 | 40 | 2 |
| dressing | 40k | 80 | 4 | 100 | 6 |

**Detalhe onde o jogador olha:**
- `MB(..., detail="hero")` só em marco; `"near"` no resto; `"far"` em massa grande ou fundo;
- nada de geometria microscópica (menor que 0,2 stud), nem chanfro em peça pequena comum;
- instancie por função: a mesma peça repetida vai no MESMO objeto `MB`. O export faz 1 MeshPart por (objeto, material).

## 8. Estilo
- **Estilizado/cartoon da concept:** formas robustas, silhuetas góticas claras (agulhas, arcos ogivais, contrafortes, rosácea), chanfro visível nas peças-herói e contraste claro/escuro (luar raspando a pedra).
- **Rocha:** basalto em COLUNAS (prismas hexagonais) e estratos. Massa primária + secundária + quebra pequena, NUNCA "rocha rocha rocha" repetida.
- **Autocrítica:**
  - Isso parece um conjunto de modelos aleatórios?
  - Alguma fachada é falsa?
  - Quebra por trás (360°)?
  - O jogador entende a função sem texto?
  - Tem roxo ou enfeite onde não tem função?
  - Parece Naruto ou Dragon Ball com outra cor?

  Se a resposta for ruim, corrija.

## 9. Ciclo de teste (obrigatório; no mínimo 3 voltas: render → crítica → correção)
```
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "C:/Users/lucas/OneDrive/Desktop/To up/ilha_shadowgarden/studio_sg.py" -- <zona> "C:/Users/lucas/OneDrive/Desktop/To up/ilha_shadowgarden/_studio/<zona>" [--cams CAM_A,CAM_B] [--res 960x540]
```
- **O que o estúdio faz:**
  - monta a ilha com a SUA zona em detalhe e o resto em blockout;
  - imprime as métricas (`STUDIO tris=... MeshParts~... colisoes=...`), os marcadores, as rotas, `SALAO_LIVRE`, `DUNGEON_LIMPA` e os renders JPG.
- **Como revisar:** abra os JPG com Read e compare com a concept. Filtre a saída com `| grep -E "STUDIO|ROTAS|SONDAS|SALAO|DUNGEON|FAIL|Error|Traceback|line "`.
- **Há outros agentes rodando Blender ao mesmo tempo:**
  - use `--res 960x540` e renderize só as câmeras que precisa;
  - se falhar por GPU/memória, espere ~20 s e tente de novo.
- **Termine SÓ quando os 4 itens estiverem OK:**
  - rotas e sondas OK;
  - marcadores obrigatórios OK;
  - orçamento OK;
  - técnico limpo: sem nome ruim, sem prefixo fora do padrão, sem material vazio, 0 faces degeneradas.

## 10. Proibido
- **Ferramentas:** Roblox Studio (`mcp__Roblox_Studio__*`), Blender ao vivo (`mcp__blender__*`), computer-use e navegador. O Blender é SÓ pela linha de comando em segundo plano (`-b`).
- **Git e ambiente:** `git commit`/`push`, instalar pacotes, abrir servidores e mexer nos `.blend` de outras pastas.

## 11. Relatório final
Responda com o objeto estruturado pedido (schema), contendo:
- arquivos criados;
- o que foi construído;
- as linhas `STUDIO`, `ROTAS`/`SONDAS` e `SALAO`/`DUNGEON` do último estúdio;
- os renders finais (caminhos);
- os problemas que ficaram, sem esconder nada;
- os pedidos de mudança em arquivos compartilhados.
