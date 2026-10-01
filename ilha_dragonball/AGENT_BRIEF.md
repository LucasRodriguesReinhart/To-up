# Brief comum — produção da Ilha 2 (Dragon Ball)

Você é um dos agentes da produção. O **blockout já foi aprovado** (planta, níveis, rotas). Seu trabalho é transformar
UMA zona do blockout em arte final jogável, sem mudar a planta.

Pasta do projeto: `C:\Users\lucas\OneDrive\Desktop\To up\ilha_dragonball` (abaixo: `ilha_dragonball/`).
Pipeline reaproveitado (só leitura):
- lobby: `C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\forja_mineradora` (fm_lib, fm_parts, kits);
- Ilha 1 Naruto: `C:\Users\lucas\OneDrive\Desktop\To up\ilha_naruto` (il_lib, kits de portão/summon, andador de QA).

## 0. A regra que manda
**NARUTO DEFINE O PIPELINE, NÃO O LAYOUT.** Esta ilha não pode parecer um reskin da Ilha 1:
- nada de telhado japonês por toda parte;
- nada de vila Konoha;
- nada de fosso redondo com anel uniforme;
- nada de paredão contínuo.

A identidade DRAGON BALL vem da arquitetura Capsule (domos brancos, faixas azuis, vidro azul, portas arredondadas,
antenas, torres com prato no topo), do relevo de arenito (mesas, pilares, agulhas, cânion), da paleta quente e de
poucos acentos marciais (telhado laranja, lanterna, vermelho). **Sem Shenlong, sem personagens, sem esculturas, sem
logo espalhado, sem 30 Dragon Balls, sem placa com texto grande** (a UI do jogo comunica).

## 1. Leia antes de começar
- A concept APROVADA: `ilha_dragonball/refs/concept_db_aprovado.png` e os recortes `refs/ref_*.jpg` (`ref_main_view`,
  `ref_view_front/side/top/back`, `ref_summon`, `ref_village`, `ref_capsule`, `ref_environment`, `ref_next_gate`).
  Abra com Read. É ART DIRECTION + LAYOUT: siga a intenção, corrija o que só funciona na perspectiva da imagem.
- `db_layout.py`: a planta TRAVADA (níveis, contornos, lotes, escadas, pontes, mesas, torres, água, saída).
  Todas as posições vêm daqui. Nunca escreva coordenada "no olho" que contradiga a planta.
- `renders/_mapa_planta.png`: a planta vista de cima (gerada pelo `python db_map.py`).
- `db_blockout.py`: a versão blockout da sua zona (posições, colisões dos volumes e marcadores que ela já cria).
- `db_lib.py`:
  - paleta `DMATS` (Sand_DB, Cliff_Rock_DB/_Dark/_Top/_Dusk, Grass_DB, Dirt_DB, Stone_Paving_DB, Stone_DB_Block,
    Stone_DB_Dusk, Plaster_DB_White, Plaster_DB_Navy, Roof_DB_Blue, Roof_DB_Orange, Metal_DB_Steel, Metal_DB_Dark,
    Glass_DB_Blue, DB_Cyan_Glow, DB_Ball_Glow, DB_Star_Red, Water_DB);
  - helpers `ring_band`, `dome`, `blob_poly`, `octo_col`, `rim_r`, `vis_stairs`, `vis_fence`, `vis_parapet`, `dummy`.
- `db_col.py`: **a colisão de tudo que é andável já existe e é congelada** (ver seção 3). Leia `stair_list()`: a sua
  escada visual tem que casar com ela.
- A biblioteca do lobby:
  - `fm_lib.py`: classe `MB` com box, box2, beam, cyl, rod, ico, rock, prism, sweep, tube, quad, tri, gable_roof;
    `col_box`, `col_ramp`, `light`, `camera`;
  - `fm_parts.py`: stairs, fence, stone_parapet, lantern, palm, pave_poly, pave_ring, masonry_wall, arch,
    rock_column, cliff_band, peak, frustum, plank_floor, crate, barrel, Frame;
  - os kits `fm_arch_kit.py`, `fm_veg_kit.py`, `fm_water_kit.py`, `fm_props_kit.py`, `fm_portal_kit.py`.
  Reaproveite; não reescreva o que já existe.

## 2. Arquivos
- Você só **cria e edita** `ilha_dragonball/db_<sua_zona>.py`, mais helpers opcionais `db_<sua_zona>_*.py`, e os seus
  renders em `ilha_dragonball/_studio/<sua_zona>/`.
- **Não edite:**
  - `db_layout.py`, `db_lib.py`, `db_col.py`, `db_core.py`, `db_blockout.py`, `db_scene.py`, `build_db.py`,
    `studio_db.py`, `db_qa.py`, `db_map.py`, `run.sh`;
  - os módulos de outros agentes;
  - nada em `ilha_naruto/` ou `lobby_area/`.
  Se precisar mudar a planta ou um arquivo compartilhado, NÃO mude: descreva o pedido em `requests` no relatório.
- Não apague arquivos que não são seus. Não faça `git commit`/`push`.

## 3. Colisão: quem faz o quê
- O `db_col` (sempre, congelado) já cria a colisão de:
  - todo PISO: arena, promenade, chão, praça, vila, terraço do Capsule, summon, prateleira da saída, pontes, ilhota,
    satélites;
  - todas as ESCADAS e RAMPAS da planta (como rampas);
  - as GUARDAS invisíveis: borda da ilha, borda da arena, bordas de terraço com queda > 2,3, laterais das pontes;
  - as colunas das mesas/rochas, o pod central e o portão Shadow Garden.
- O seu módulo desenha o VISUAL disso sem colisão:
  - escadas com `db_lib.vis_stairs` (= `fm_parts.stairs(..., col=False)`), com os mesmos pé/rumo/largura/espelho/piso
    do `db_col.stair_list()`;
  - guarda-corpos com `vis_fence`/`vis_parapet` (col=False) nas mesmas linhas das guardas invisíveis.
- O seu módulo cria colisão SÓ dos próprios volumes: paredes de prédio (com vão na porta), torres, props grandes.
  - Use `col_box`/`col_box2`/`octo_col`, caixas simples, NADA de colisão por malha.
  - A área começa com `DB_` + zona, p.ex. `col_box("DB_CapWall", ...)`.
- O topo do seu visual tem que bater com as cotas (`L.GROUND` 24,2, `L.ARENA` 20,2, `L.HUB` 28,2, `L.SUM` 30,2,
  `L.CAP` 34,2, `L.EXIT_Z` 28,2, `L.DECK` 16,2). Visual acima do piso de colisão = flutua; abaixo = afunda. Não crie
  piso duplicado.

## 4. Contrato do módulo
- `build()` sem argumentos cria tudo da zona.
- Nomes: `DB_<Zona>_<Coisa>`, únicos e descritivos. Nada de `Cube`, `Cylinder`, `.001`. O prefixo define o dono no
  export do Roblox:
  - `DB_Ter_` terreno, `DB_Mine_` mineração, `DB_Ent_` entrada, `DB_Cap_` Capsule;
  - `DB_Hub_` vila, `DB_Twr_` torres, `DB_Sum_` summon, `DB_Water_` água, `DB_Exit_` saída;
  - `DB_Veg_` vegetação, `DB_Prop_` props, `DB_Sky_` fundo.
- Coleções:
  - `02_TERRAIN`, `03_MINING_ZONE`, `04_CAPSULE_LANDMARK`, `05_TECH_VILLAGE`, `06_SUMMON`, `07_WATER`,
    `08_NEXT_ISLAND`, `09_PROPS`, `10_VEGETATION`;
  - luzes em `11_LIGHTING` (o `fm_lib.light` já põe lá);
  - o segundo argumento de `MB(nome, colecao)` é o nome da coleção.
- Peças que se movem (anéis, orbes, turbinas, radar giratório, bandeiras):
  - objeto separado com nome `VFX_DB<ZONA>_<Coisa>` (p.ex. `VFX_DBTWR_Radar`) na coleção `12_VFX_HELPERS`;
  - propriedades customizadas `pivot` = (x, y, z) mundo, `axis` = (x, y, z) e `rpm` (ou `bob` para flutuar);
  - aparecem no render; o export as envia como peças móveis.
- Luzes: `fm_lib.light(nome, "POINT", loc, energia, cor, raio)` com nome `L_DB<Zona>_<Coisa>`. Poucas: respeite o teto
  de luzes de dia.
- Marcadores obrigatórios: `db_lib.mk(nome, loc, rot, tamanho, tipo, props=...)` com exatamente os nomes do seu brief.
- Câmeras de revisão: dicionário `CAMS = {"CAM_DB<Zona>_<Vista>": (loc, alvo, lente)}` no topo do módulo.
  - Inclua frente, trás, os 2 lados e ALTURA DO JOGADOR (olho 5,2 acima do piso, lente 20–24).
  - Revisão 360°, não só bird-eye.
- Rotas/sondas extras das peças novas: `EXTRA_ROUTES = {nome: (pontos_xy, z_inicial)}` e
  `EXTRA_PROBES = [(nome, x, y, z_piso, dx, dy)]` no módulo (o `db_qa` roda).
- Determinístico (sementes fixas), sem `bpy.ops`, build da zona abaixo de 20 s.

## 5. Escala e jogabilidade (Roblox)
- 1 BU = 1 stud, Z para cima. O jogador tem 5,2 de altura (os bonecos cinza `SCALE_Dummy_*` aparecem nos renders).
- Prédio entrável:
  - portas com vão ≥ 7 × 10 e pé-direito interno ≥ 14 (o usuário já reclamou de interior apertado);
  - interior de verdade: piso, paredes, teto, porta (vão aberto), circulação, espaço de câmera, lugar do NPC/balcão e
    colisão coerente (paredes com vão, não bloco maciço).
- Prédio **não entrável** NÃO tem porta nenhuma, nem falsa: use janelas redondas, painéis, varandas altas, antenas.
  **Nada de fachada falsa** (porta → parede).
- Escadas: espelho ≤ 0,8, piso ≥ 1,6, largura ≥ 6. O andador do QA sobe no máximo 2,3 e cai no máximo 2,3.
- As rotas do `db_qa.py` têm que continuar todas OK (ROTAS 13/13, ROTAS_ABERTAS 1/1, SONDAS todas). Nada seu pode
  bloquear um caminho.
- **NÃO MODELE MINÉRIO, NEM CRISTAL QUE PAREÇA MINÉRIO.** Os minérios são do jogo (o SpawnMinerio gera nos `ORE_*`).
  Nada de pedra solta na área de minério da arena além das `ARENA_ROCKS` da planta.

## 6. Materiais
- Use a paleta `DMATS` (db_lib) e os existentes (`Metal_Gold`, `Wood_Lacquer_Red`, `Wood_Dark`, `Lantern_Glow`,
  `Window_Warm`, `DB_Energy_Glow`, `Summon_*`, `Water`, `Water_Fall`, `Foam`, `Leaf_*`, `Bark`, `Cloth_*`...).
- Material novo:
  - registre com `fm_lib.MATS.setdefault(nome, (fm_lib.S(r,g,b), rough, metal, emissao, cor_emissao, 0.0))`;
  - o nome começa pelo prefixo de família do lobby (`Stone_`, `Plaster_`, `Metal_`, `Roof_`, `Wood_`, `Cliff_Rock_`,
    `Grass_`, `Sand_`, `Leaf_`, `Cloth_`, `Glass_DB`) e traz a sua zona, p.ex. `Metal_DBCapChrome`;
  - emissivo tem `Glow` no nome e vira Neon no Roblox;
  - respeite o teto de materiais novos da zona.
- Neon só em energia/brilho (anéis de energia, núcleos, luzes de sinalização, janelas acesas raras).

## 7. Orçamento (o `studio_db.py` mede e avisa)

| zona | tris | MeshParts est. | mat. novos | colisões próprias | luzes de dia |
|---|---|---|---|---|---|
| terrain | 95k | 120 | 6 | 60 | 0 |
| mining | 35k | 45 | 4 | 60 | 2 |
| entrance | 35k | 45 | 5 | 60 | 3 |
| capsule | 60k | 80 | 7 | 170 | 6 |
| village | 55k | 85 | 6 | 150 | 4 |
| towers | 35k | 55 | 5 | 90 | 3 |
| summon | 40k | 50 | 5 | 80 | 4 |
| water | 20k | 30 | 3 | 20 | 0 |
| exit | 25k | 35 | 4 | 60 | 2 |
| dressing | 50k | 90 | 6 | 90 | 12 |

Detalhe onde o jogador olha:
- `MB(..., detail="hero")` só em marco; `"near"` no resto; `"far"` em massa grande ou fundo;
- nada de geometria microscópica (< 0,2 stud) nem chanfro em peça pequena comum;
- instancie por função: a mesma peça gerada várias vezes vira 1 MeshPart por (objeto, material) no export, então
  agrupe peças repetidas no mesmo objeto `MB`.

## 8. Estilo
- Cartoon estilizado da concept: formas robustas e arredondadas, silhuetas claras, cores saturadas mas quentes,
  chanfro visível nas peças-herói, contraste claro/escuro nas rochas (estratos).
- **Rocha:** massa primária + secundária + quebra pequena, NUNCA "rocha rocha rocha" repetida.
- **Autocrítica:**
  - isso parece um conjunto de modelos aleatórios?
  - alguma fachada é falsa?
  - quebra por trás (360°)?
  - o jogador entende a função sem texto?
  - parece Naruto com outra cor?
  Se a resposta for ruim, corrija.

## 9. Ciclo de teste (obrigatório; no mínimo 3 voltas: render → crítica → correção)
```
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "C:/Users/lucas/OneDrive/Desktop/To up/ilha_dragonball/studio_db.py" -- <zona> "C:/Users/lucas/OneDrive/Desktop/To up/ilha_dragonball/_studio/<zona>" [--cams CAM_A,CAM_B] [--res 960x540]
```
- O estúdio monta a ilha com a SUA zona em detalhe e o resto em blockout. Ele imprime as métricas
  (`STUDIO tris=... MeshParts~... colisoes=...`), os marcadores, as rotas e os renders JPG.
- Abra os JPG com Read e compare com a concept. Filtre a saída com
  `| grep -E "STUDIO|ROTAS|SONDAS|FAIL|Error|Traceback|line "`.
- Há outros agentes rodando Blender ao mesmo tempo:
  - use `--res 960x540` e renderize só as câmeras que precisa;
  - se o render falhar por GPU/memória, espere ~20 s e tente de novo.
- Termine SÓ quando os 4 itens estiverem OK:
  - rotas todas OK;
  - marcadores obrigatórios OK;
  - orçamento OK;
  - técnico limpo (sem nome ruim, sem prefixo fora do padrão, sem material vazio, 0 faces degeneradas).

## 10. Proibido
- Ferramentas do Roblox Studio (`mcp__Roblox_Studio__*`), Blender ao vivo (`mcp__blender__*`), computer-use, navegador.
  O Blender é SÓ pela linha de comando em segundo plano (`-b`).
- `git commit`/`push`, instalar pacotes, abrir servidores, mexer nos .blend de outras pastas.

## 11. Relatório final
Responda com o objeto estruturado pedido (schema), contendo:
- arquivos criados;
- o que foi construído;
- as linhas `STUDIO` e `ROTAS`/`SONDAS` do último studio;
- os renders finais (caminhos);
- os problemas que ficaram, sem esconder nada;
- os pedidos de mudança em arquivos compartilhados.
