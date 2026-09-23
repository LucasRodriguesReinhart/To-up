# Lobby Vila-Forja — Anime Mining Simulator

Arquivo final: `lobby_forja_mineradora.blend` (Blender 5.2). Renders: `renders/` (18 câmeras em 1920×1080 + prancha `_PRANCHA_todas_cameras.jpg`). Exportação para o Roblox: `export/`.

O lobby inteiro é gerado por script. Para reconstruir do zero (cerca de 55 s):

```
blender -b --factory-startup --python build.py
blender -b lobby_forja_mineradora.blend --python fm_qa.py -- nav tech
blender -b lobby_forja_mineradora.blend --python render.py -- renders --res 1920x1080
blender -b lobby_forja_mineradora.blend --python export_roblox.py
```

## Escala e eixos
- **1 BU = 1 stud**, Z para cima, dummy R15 de 5,2 studs em `_SCALE_REFERENCE` (spawn, praça, porta, mina, portal).
- Níveis: spawn z0 · vale z4 · ledge dos portais z14 · terraço dos portais z30. Konoha fica na direção **+Y do Blender**, que é a direção das ilhas em sequência.
- Exportação: Roblox = (x, z, −y) do Blender. É o mesmo mapeamento do FBX `-Z forward / Y up`, e o `montar_lobby_forja.lua` usa esse mesmo mapeamento para as colisões, os marcadores e as luzes.

## Planta (o que cada área faz)
| Área | Função |
|---|---|
| Spawn (0,−104) | Chegada de frente para a avenida. A escadaria sobe até a praça e daí se veem a forja, a chaminé e os 6 portais. |
| Praça (r25) | Circulação central. Liga a forja, a mina, a loja, a estrada oeste e a ponte leste. |
| **Forja do Ignis** | Salão com enxaimel, lareira aberta na fachada (Ignis entre o fogo e a bigorna) e torre-chaminé de alvenaria com fornalha dentro. Ala esquerda: recebimento de minério (portão do trilho, tremonha, calha até a fornalha) e loft de armazenamento com varanda e quadro de líderes. Ala direita: casa dos foles, acionados pelo eixo alto que vem da roda d'água, com o balcão de venda na frente. |
| Mina (SW) | Portal de madeira, túnel escorado a cada 5 studs que faz curva, câmara de cristais e duas galerias interditadas. |
| Trilhos | Mina → balança de vagonetes (telheiro) → portão oeste da forja → tremonha → calha → fornalha. |
| Água | Nascentes NO/NE e cachoeira central → canal do ledge → vertedouro → tanque → rio → roda d'água → queda no penhasco sul. |
| Roda d'água | Eixo baixo → roda de coroa e pinhão (casa da roda, que também aciona o martinete da oficina) → eixo alto (z15,5) sobre a passagem → foles da forja. |
| Portais | 6 portais no terraço, do mais fácil ao mais difícil, da esquerda para a direita. Cada um tem acesso próprio: patamar → lance 1 → ponte sobre o canal → lance 2 → pad. As placas de dificuldade (1–6) usam pontos luminosos, sem texto. |
| Konoha | Torii → Passo da Folha (cânion com torii, lanternas e sakura) → ponte suspensa sobre a garganta → Grande Portão de Konoha → mirante. |

Portais, cada um com arquitetura própria:
- **Naruto:** torii vermelho com kasagi curvo, lanternas de pedra, nobori e sakura.
- **Dragon Ball:** anel dourado com dragão enrolado, base em cápsula branca e 7 esferas em pedestais. A frente fica livre.
- **Shadow Garden:** arco ogival escuro com pináculos, lua crescente, correntes e grade.
- **Demon Slayer:** pórtico-santuário com telhado de telhas, máscara oni, katanas cruzadas, shimenawa, braseiros e glicínias.
- **One Piece:** timão gigante, cais de madeira, âncora, baú, mastro com vela e palmeiras.
- **One Punch Man:** moldura de concreto com neon, torres com janelas, punho no topo e totens.

## Construções entráveis (sem fachada falsa)
Todas estas têm porta real, piso, paredes, teto, interior mobiliado e colisão com vão de porta: salão da forja, sala da fornalha, as duas alas, o loft, a loja (balcão, NPC e prateleiras), a casa da roda (engrenagens, martinete e bancada) e as 5 cabanas de mineiros (cama, mesa, prateleira e lanterna).

A estação de carga e o galpão de cristais são **abertos** de propósito, então não sugerem portas que não existem.

## Marcadores de gameplay (`15_GAMEPLAY_MARKERS`)
`NPC_Ignis`, `INTERACT_Ignis`, `PLAYER_INTERACT_Ignis`, `NPC_Balcao`/`INTERACT_`/`PLAYER_INTERACT_Balcao`, `NPC_Shop`/`INTERACT_`/`PLAYER_INTERACT_Shop`, `PORTAL_<Naruto|DragonBall|ShadowGarden|DemonSlayer|OnePiece|OnePunchMan>`, `WORLD_EXIT_Naruto`, `WORLD_ENTRY_Naruto`, `MINE_Entrance`, `MINE_Interior_Zone`, `RAIL_*`, `DOOR_*`, `LEADERBOARD_Balcony` e `VFX_*` (fumaça, faíscas, fogo, rotação da roda, martinete, espirais e cachoeiras).

## QA automático (`fm_qa.py`)
- **Navegação:** um "jogador" percorre as rotas sobre as colisões `COL_`, com degrau ≤ 2,3, sem queda, altura livre ≥ 6,5 e corpo de raio 1,1 livre. **18/18 rotas OK:** spawn→Ignis, spawn→mina (até dentro do túnel), Ignis→loja, Ignis→casa da roda, Ignis→cada um dos 6 portais, ledge→Naruto, Naruto→Konoha (até o portão), margem leste, spawn→salão, salão→fornalha, praça→varanda/loft, praça→balcão, portão do trilho→tremonha.
- **Técnico:** 0 nomes genéricos, 0 malhas sem material, 0 escalas não aplicadas ou negativas, 0 malhas acima de 120k tris. Restam 62 faces minúsculas degeneradas, sem efeito visual.

## Métricas
| | |
|---|---|
| Objetos na cena | 932 (malhas nomeadas por área, colisões, marcadores, luzes, câmeras) |
| Triângulos (Blender) | ~656k (inclui nuvens, fumaça e vale distante, que não são exportados) |
| Exportado para o Roblox | 459 malhas / ~642k tris, 1 material por malha, ≤ 18k tris por malha |
| Colisões `COL_` | 675 caixas e rampas (Parts invisíveis) |
| Marcadores | 48 |
| Luzes | 96 (PointLight/SpotLight sem sombra, exceto as principais) |
| Materiais | 61, com biblioteca enxuta e variantes por portal |

## Estrutura do arquivo
Coleções: `00_REFERENCE` (18 câmeras `CAM_*`) · `01_BLOCKOUT` (vazia na versão final) · `02_TERRAIN` · `03_FORGE` · `04_MINE` · `05_WATER_SYSTEM` · `06_PORTALS` · `07_BUILDINGS` · `08_PROPS` · `09_VEGETATION` · `10_RAILS` · `11_LIGHTING` · `12_VFX_HELPERS` · `13_COLLISION` (subcoleções `COL_<área>`) · `14_EXPORT` · `15_GAMEPLAY_MARKERS` · `_SCALE_REFERENCE`.

Scripts:
- `fm_layout.py`: planta travada; todas as cotas saem daqui.
- `fm_lib.py`: construtor de malha, materiais, colisões, marcadores.
- `fm_parts.py`: módulos (escada, cerca, lanterna, penhasco facetado, pico, trilho, árvores, arco, enxaimel, alvenaria).
- Um script por área: `fm_terrain`, `fm_forge`, `fm_mine`, `fm_water`, `fm_buildings`, `fm_portals`, `fm_konoha`, `fm_props`, `fm_veg`.
- `fm_scene.py`: céu, sol, câmeras e escala.
- `fm_qa.py`, `render.py`, `export_roblox.py`.

## Integração com o Roblox (`export/`)
1. No Studio, importe `LOBBY_02_TERRAIN.fbx` … `LOBBY_10_RAILS.fbx` com o 3D Importer, mantendo as posições, para dentro de `workspace.LOBBY_FORJA`.
2. Rode `montar_lobby_forja.lua` na Command Bar. Ele:
   - aplica cor e material pelo sufixo do nome (`__Stone_Light`, …), com `RICO=false` estilizado e `RICO=true` texturizado;
   - deixa os visuais `CanCollide=false`;
   - cria as 675 colisões invisíveis, os 48 marcadores (com atributos) e as 96 luzes.
   
   `ROOT_OFFSET` desloca o lobby inteiro.
3. Para ligar o jogo:
   - Ignis no `NPC_Ignis`, com o prompt em `INTERACT_Ignis` (alcance 18);
   - teleporte ou continuidade: `PORTAL_*`, e `WORLD_EXIT_Naruto`/`WORLD_ENTRY_Naruto` alinhados com a entrada da Área 1;
   - `ParticleEmitter` nos `VFX_*`;
   - girar `WATER_Waterwheel` em torno de X e as espirais dos portais.

Recomendado: `StreamingEnabled` ligado.

## Limitações reais
- **Não importei nem testei dentro do Roblox Studio.** O FBX, o JSON e o Luau estão prontos, mas o mapeamento de eixos (x, z, −y) e a escala do importador precisam ser conferidos numa primeira importação. Se o lobby aparecer espelhado, basta trocar a matriz `T` em `export_roblox.py` e reexportar.
- As cores têm variação por face e ruído **só no render do Blender**. No Roblox cada malha recebe cor sólida + Material; texturas pintadas ou assadas ficaram fora deste passe.
- Os VFX (fumaça, fogo, faíscas, rotação da roda e das espirais, martinete) existem como marcadores e placeholders. Os efeitos animados precisam ser montados no Roblox.
- O Ignis é um proxy em blocos (1,35×) que marca posição e escala. O rig real entra no `NPC_Ignis`. O quadro de líderes é um painel sem conteúdo.
- ~642k triângulos exportados é pesado para o Roblox (o lobby anterior tinha 294k). Os maiores são os pinheiros (66k), as montanhas próximas (47k) e o muro dos portais (35k). Candidatos a LOD ou simplificação se o desempenho em celular pedir.
- Os picos de fundo são volumes facetados simples, feitos para leitura de silhueta, não para inspeção de perto.
