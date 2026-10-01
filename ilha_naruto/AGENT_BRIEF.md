# Brief comum — produção da Ilha 1 (Naruto / Vila da Folha)

Você é um dos agentes da produção. O **blockout já foi aprovado** (planta, níveis, rotas). Seu trabalho é
transformar UMA zona do blockout em arte final jogável, sem mudar a planta.

Pasta do projeto: `C:\Users\lucas\OneDrive\Desktop\To up\ilha_naruto` (abaixo: `ilha_naruto/`).
Pipeline reaproveitado do lobby (só leitura): `C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\forja_mineradora`.

## 1. Leia antes de começar
- `ilha_naruto/ANALISE_REFERENCIAS.md`: a análise das referências.
- As referências da sua zona em `ilha_naruto/refs/*.jpg`, abertas com a ferramenta Read (ela mostra a imagem).
  As `ref_14..18` são a ilha inteira de 5 ângulos, as `ref_08..12` a torre de summon e a `ref_13` o portão Dragon Ball.
- `ilha_naruto/il_layout.py`: a planta travada. Leve dela todas as posições, níveis e raios, e nunca escreva
  coordenadas "no olho" que contradigam a planta.
- `ilha_naruto/il_blockout.py`: a versão blockout da sua zona (posições exatas, colisões e marcadores que ela já cria).
- `ilha_naruto/il_lib.py` (paleta `KMATS`, helpers de polígono/colisão), `il_col.py`, `il_core.py` e `il_gate_std.py`.
- A biblioteca do lobby: `fm_lib.py` (classe `MB`: box, box2, beam, cyl, rod, ico, rock, prism, sweep, tube, quad, tri,
  gable_roof; `col_box`, `col_ramp`, `light`, `camera`), `fm_parts.py` (stairs, fence, stone_parapet, lantern,
  pave_poly, pave_ring, masonry_wall, arch, timber_wall, window_glow, rock_column, cliff_band, peak, plank_floor,
  crystal_cluster, crate, barrel, mine_cart, rails, Frame) e os kits `fm_arch_kit.py`, `fm_arch_house.py`,
  `fm_veg_kit.py`, `fm_water_kit.py`, `fm_props_kit.py` e `fm_portal_kit.py` (chochin, toro, rope_twist, chain,
  katana, ring, loft...). Reaproveite; não reescreva o que já existe.

## 2. Arquivos
- Você só **cria e edita** `ilha_naruto/il_<sua_zona>.py`, mais helpers opcionais `il_<sua_zona>_*.py`, e os seus
  renders em `ilha_naruto/_studio/<sua_zona>/`.
- **Não edite:** `il_layout.py`, `il_lib.py`, `il_col.py`, `il_core.py`, `il_blockout.py`, `il_scene.py`,
  `build_ilha.py`, `studio.py`, `il_qa.py`, `il_gate_std.py`, `il_gates.py`, os módulos de outros agentes, nem nada em
  `lobby_area/`. Se precisar mudar a planta ou um arquivo compartilhado, NÃO mude: descreva o pedido em `requests`
  no relatório final.
- Não apague arquivos que não são seus. Não faça `git commit`/`push`.

## 3. Contrato do módulo
- `build()` sem argumentos cria tudo da zona. Os portões da galeria usam `build_gate(gx, gy, gz, yaw)`; veja o seu
  brief.
- Nomes: `<PREFIXO>_<Coisa>` únicos e descritivos. O prefixo define o dono no export do Roblox:
  `TER_` terreno, `MINE_` mineração, `ENT_` entrada, `VIL_` vila/casas, `SUM_` summon, `WATER_` água, `EXIT_` saída,
  `GATE_<k>_` portões, `VEG_` vegetação, `PROP_` props. Nada de `Cube`, `Cylinder`, `.001`.
- Coleção: a da sua zona (`02_TERRAIN`, `03_MINING`, `04_VILLAGE`, `05_SUMMON`, `06_WATER`, `07_NEXT_ISLAND`,
  `08_PURCHASE_GATES`, `09_PROPS`, `10_VEGETATION`). O segundo argumento de `MB(nome, colecao)` é o nome da coleção.
- Peças que se movem (anéis do summon, roda d'água, bandeiras que tremulam, orbes flutuantes):
  - objeto separado com nome `VFX_<ZONA>_<Coisa>` na coleção `12_VFX_HELPERS`;
  - propriedades customizadas `pivot` = (x, y, z) mundo, `axis` = (x, y, z) e `rpm` (ou `bob` para flutuar);
  - elas aparecem no render; o export as envia como peças móveis.
- Colisão: toda superfície pisável e toda parede sólida precisa de colisão `COL_`, feita com
  `col_box`/`col_box2`/`col_ramp` ou `fm_parts.stairs`/`fence`/`stone_parapet`, que já criam a sua. O nome da área
  de colisão começa com o nome da sua zona (ex.: `col_box("SummonTower", ...)`). Caixas simples, NÃO colisão por
  malha.
- A colisão do chão da ilha inteira (fosso, anel, T1, T2, paredão) e a parede invisível da borda já vêm prontas do
  `il_core`. O topo do seu visual tem que bater com essas cotas (`L.G`, `L.RING`, `L.PIT`, `L.T1`, `L.T2`...).
  Não crie chão duplicado.
- Luzes: `fm_lib.light(nome, "POINT", loc, energia, cor, raio)` com nome `L_<Zona>_<Coisa>`. Poucas: respeite o teto
  de luzes de dia da sua zona.
- Marcadores obrigatórios: crie com `il_lib.mk(nome, loc, rot, tamanho, tipo, props=...)`, com exatamente os nomes
  do seu brief.
- Câmeras próprias de revisão: dicionário `CAMS = {"CAM_<Zona>_<Vista>": (loc, alvo, lente)}` no topo do módulo.
  Inclua pelo menos frente, trás, os dois lados e a altura do jogador (revisão 360°).
- Determinístico (sementes fixas), sem `bpy.ops`, build da zona abaixo de 20 s.

## 4. Escala e jogabilidade (Roblox)
- 1 BU = 1 stud, Z para cima. O jogador tem 5,2 de altura (os bonecos cinza `SCALE_Dummy_*` aparecem nos renders).
- Portas de prédio entrável: vão ≥ 7 de largura × 10 de altura. Pé-direito interno ≥ 14. O usuário já reclamou de
  interior apertado, em que o jogador não via nada; aqui o espaço tem que sobrar para a câmera.
- Escadas: espelho ≤ 0,8, piso ≥ 1,6, largura ≥ 6. O andador do QA sobe no máximo 2,3 e cai no máximo 2,3.
- As 14 rotas de navegação do `il_qa.py` têm que continuar 14/14 OK. Nada seu pode bloquear um caminho.
- Prédio **entrável** tem interior de verdade: piso, paredes, teto, porta aberta (vão), circulação, espaço de
  câmera, lugar do NPC e balcão quando for o caso, com colisão coerente (paredes com vão, não um bloco maciço).
- Prédio **não entrável** NÃO tem porta nenhuma, nem falsa. Use janelas, varandas altas, caixas d'água, etc.

## 5. Materiais
- Use a paleta existente: `il_lib.KMATS` (Grass_Konoha, Dirt_Pit, Stone_Paving_Warm, Stone_Wall_Light/Dark,
  Cliff_Rock_Tan/_Dark/_Top, Roof_Terracotta, Roof_Blue, Roof_Green, Plaster_Cream, Wood_Lacquer_Red, Metal_Gold,
  Summon_*, Cloth_Royal_Blue, DB_Energy_Glow, Sea_Water) e os de `fm_lib.MATS` (Wood_Dark, Wood_Plank, Wood_Light,
  Metal_Dark, Metal_Iron, Stone_Dark, Lantern_Glow, Window_Warm, Crystal_Blue, Crystal_Purple, Water, Water_Fall,
  Foam, Leaf_*, Bark, Cloth_Red, Rope, P_DB_*, P_Shadow_*, P_DS_*, P_OP_*, P_OPM_*...).
- Material novo:
  - registre no topo do módulo com `fm_lib.MATS.setdefault(nome, (cor_linear, rough, metal, emissao, cor_emissao, 0.0))`,
    com a cor em `fm_lib.S(r, g, b)` (sRGB 0–255);
  - o nome começa pelo prefixo de família do lobby (`Stone_`, `Wood_`, `Roof_`, `Plaster_`, `Metal_`, `Cloth_`,
    `Grass_`, `Dirt_`, `Cliff_Rock_`, `Leaf_`, `Crystal_`) e traz a sua zona, p.ex. `Metal_SumBronze`, `Stone_EntLion`;
  - emissivo tem `Glow` no nome e vira Neon no Roblox;
  - respeite o teto de materiais novos da zona.
- Neon só em energia/brilho (lanternas, cristais, barreiras, estrelas). Janela comum = `Window_Warm`.

## 6. Orçamento (o `studio.py` mede e avisa)

| zona | tris | MeshParts estimadas | materiais novos | colisões | luzes de dia |
|---|---|---|---|---|---|
| terrain | 100k | 120 | 6 | 420 | 0 |
| mining | 45k | 65 | 5 | 130 | 4 |
| entrance | 30k | 40 | 4 | 70 | 4 |
| village | 55k | 80 | 6 | 160 | 6 |
| houses | 45k | 70 | 5 | 130 | 4 |
| summon | 35k | 45 | 6 | 70 | 4 |
| water | 22k | 35 | 4 | 50 | 0 |
| exit | 20k | 30 | 4 | 70 | 2 |
| gate_db | 24k | 32 | 6 | 30 | 3 |
| gates (4 portões) | 100k (25k cada) | 140 | 12 | 120 | 0 |

Detalhe onde o jogador olha. Use `MB(..., detail="hero")` só em marco, `"near"` no resto e `"far"` em massa grande ou
fundo. Nada de geometria microscópica (< 0,2 stud) nem chanfro em peça pequena comum. Instancie por função: a mesma
peça gerada várias vezes vira 1 MeshPart por (objeto, material) no export, então agrupe peças repetidas no mesmo
objeto `MB`.

## 7. Estilo
- Cartoon estilizado das referências: formas robustas e legíveis, silhuetas claras, beirais largos, cores saturadas
  mas quentes, chanfros visíveis nas peças-herói, contraste claro/escuro nas pedras.
- **Proibido:**
  - rostos dos Hokages ou esculturas de personagens;
  - bandeiras como enfeite (só nos pontos do seu brief);
  - placa 3D com preço ou texto "COMPRAR";
  - vegetação espalhada (quem cuida da vegetação é o agente de dressing; você só deixa espaço).
- Autocrítica: "isso parece um conjunto de modelos aleatórios?"; "alguma fachada é falsa?"; "quebra por trás?"; "o
  jogador entende a função sem texto?". Se a resposta for ruim, corrija.

## 8. Ciclo de teste (obrigatório; no mínimo 3 voltas: render → crítica → correção)
```
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "C:/Users/lucas/OneDrive/Desktop/To up/ilha_naruto/studio.py" -- <zona> "C:/Users/lucas/OneDrive/Desktop/To up/ilha_naruto/_studio/<zona>" [--cams CAM_A,CAM_B] [--res 960x540]
```
- O estúdio monta a ilha com a SUA zona em detalhe e o resto em blockout. Ele imprime:
  - as métricas (`STUDIO tris=... MeshParts~... colisoes=...`);
  - os marcadores obrigatórios;
  - as 14 rotas;
  - os renders JPG na pasta de saída (câmeras da zona + o seu `CAMS`).
- Abra os JPG com Read e compare com as referências. Rode no bash do Git; filtre a saída com `| grep -E "STUDIO|ROTAS|FAIL|Error|Traceback|line "`.
- O `ilha_naruto/` tem outros 8 agentes rodando Blender ao mesmo tempo: use `--res 960x540`, renderize só as câmeras
  que precisa e, se o render falhar por GPU, espere ~20 s e tente de novo.
- Termine SÓ quando os 4 itens estiverem OK:
  - 14/14 rotas;
  - marcadores obrigatórios OK;
  - orçamento OK;
  - técnico limpo (sem nome ruim, sem material vazio, 0 faces degeneradas).

## 9. Proibido
- Ferramentas do Roblox Studio (`mcp__Roblox_Studio__*`), do Blender ao vivo (`mcp__blender__*`), computer-use, Chrome
  e navegador. O Blender é SÓ pela linha de comando em segundo plano (`-b`).
- `git commit`/`push`, instalar pacotes, abrir servidores, mexer nos .blend do lobby.

## 10. Relatório final
Responda com o objeto estruturado pedido (schema), contendo:
- os arquivos criados;
- o que foi construído;
- as métricas do último `studio` (colando as linhas `STUDIO` e `ROTAS`);
- os renders finais (caminhos);
- os problemas que ficaram, sem esconder nada;
- os pedidos de mudança em arquivos compartilhados.
