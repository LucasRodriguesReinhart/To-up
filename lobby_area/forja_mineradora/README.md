# Lobby Vila-Forja — Anime Mining Simulator

- **Arquivo final:** `lobby_forja_mineradora.blend` (Blender 5.2).
- **Renders:** `renders/` tem as 18 câmeras em 1920×1080, mais a prancha `_PRANCHA_todas_cameras.jpg`.
- **Concepts de referência:** `refs/concept_1..7.jpg`.
- **Roblox:** tudo em `export/`, gerado por `export_all.py`.

## Reconstruir / validar / exportar
```
blender -b --factory-startup --python build.py                               # ~25 s; FM_OUT=<caminho> muda o .blend de saida
blender -b lobby_forja_mineradora.blend --python fm_qa.py -- nav tech         # 18 rotas + auditoria tecnica
blender -b lobby_forja_mineradora.blend --python render.py -- <pasta_absoluta> --res 1920x1080
blender -b lobby_forja_mineradora.blend --python export_all.py               # estatico + VFX no MESMO passe (EXPORT_ID)
```
O `export_all.py` roda em modo **estrito**: se algum orçamento estourar, ele não grava nada. Com `FM_BUDGET=warn` ele grava assim mesmo e imprime o relatório.

## Escala e eixos
- **1 BU = 1 stud**, Z para cima.
- Níveis: spawn z0 · vale z4 · ledge z14 · terraço dos portais z30.
- Konoha fica em **+Y** do Blender.
- Roblox = (x, z, −y), validado no Studio: sem espelhamento, a mina fica à esquerda-frente do spawn e o rio à direita.
- Dummy R15 de 5,2 studs em `_SCALE_REFERENCE`.

## Planta (congelada desde a aprovação do usuário)
| Área | Função |
|---|---|
| Spawn → avenida → praça | O spawn olha de frente para a forja, a chaminé e os 6 portais. |
| **Forja do Ignis** | Fábrica artesanal com salão e boca de fornalha retangular com fogo em degradê. O Ignis fica entre o fogo e a bigorna, que está na altura da cintura. |
| Forja — torre | **Alto-forno** baixo e largo sobre a casa da fornalha, com coroa incandescente. |
| Forja — tubulação | Coifa e fumeiro da lareira até a torre, e tubos grossos com registros. |
| Forja — ala esquerda | Recebimento de minério: portão do trilho, guindaste, elevador de canecas e calha até a fornalha. Tem loft com varanda. |
| Forja — ala direita | Casa dos foles, com fole gigante acionado pelo eixo da roda d'água. Tem balcão de venda. |
| Mina (SW) | Portal de madeira e túnel escorado e iluminado que leva a uma câmara de cristais, com galerias interditadas. |
| Trilhos | Mina → balança de vagonetes → portão da forja → tremonha → fornalha. |
| Água | Nascentes em contrafortes → cachoeiras → canal do ledge → vertedouro e calha da roda → tanque → rio com corredeiras → queda no penhasco sul. |
| Roda d'água (de peito) | Eixo baixo → coroa e pinhão → eixo alto → foles. O martinete da oficina é acionado por cames. |
| Portais (v3) | 6 portais no terraço, do mais fácil ao mais difícil. **Naruto:** anel de arenito entre postes de laca com a bandana da Folha. **Dragon Ball:** Esfera do Dragão gigante com a esfera de 4 estrelas no topo e base Capsule Corp. **Shadow Garden:** arco gótico com a lua crescente. **Demon Slayer:** tsuba gigante com katanas cruzadas e glicínia. **One Piece:** leme com a caveira. **One Punch Man:** muro com o buraco do soco. Cada escada tem dressing na paleta do próprio portal, e cada portal tem espiral com cor própria. |
| Konoha | Torii → cânion → ponte suspensa → Grande Portão (`WORLD_EXIT_Naruto`) → mirante (`WORLD_ENTRY_Naruto`). |
| Moldura | Montanhas de skyline quebrado e rosto de guardião esculpido; vegetação em aglomerados com 6 espécies. |

**Entráveis**, todos com porta real, interior e colisão coerente:
- salão da forja, sala da fornalha, alas e loft;
- loja;
- casa da roda;
- 5 cabanas, cada uma com silhueta própria e portas de 5,4 a 5,6 studs.

A estação de carga e o galpão são **abertos** de propósito.

## Pipeline de produção
**Portais v3** (aprovados em separado em 2026-09-24):
- Um módulo por portal: `fm_pv3_naruto.py`, `fm_pv3_dragonball.py`, `fm_pv3_shadowgarden.py`, `fm_pv3_demonslayer.py` e `fm_pv3_onepunchman.py`. Cada um tem `build(rng)` e `stairs(mb, px, rng)`, que monta o dressing do lance 2.
- O One Piece continua em `fm_portals.onepiece`.
- `fm_pv3.load()` precisa rodar antes do `make_materials` e também no export. O `build.py` e o `export_roblox.py` já fazem isso, porque cada módulo registra ali os próprios materiais, a cor da luz e a textura da espiral.
- Estúdio de avaliação de um portal isolado sobre o terreno real, com métricas, contrato e rota: `blender -b --factory-startup --python portal_studio.py -- <Key|all> <pasta_absoluta> [--save] [--cams A_Hero,G_Far,H_Stairs,I_Climb]`.
- `portal_sheet.py` monta a prancha.

Cada área tem módulos próprios:
- `fm_forge*`, `fm_portal*` / `fm_konoha`, `fm_buildings` / `fm_arch_*`
- `fm_terrain*`, `fm_veg*`, `fm_props*` / `fm_mine`, `fm_water*`, `fm_scene*`

A biblioteca e os materiais ficam em `fm_lib.py`: variantes tonais por peça (que chegam ao Roblox), detalhe perto/longe, UVs e texturas geradas (`fm_mat_textures.py`). A planta travada fica em `fm_layout.py`.

O acabamento foi feito em duas rodadas com agentes paralelos, cada um dono dos seus arquivos. A rodada 2 foi guiada por 5 críticos independentes: direção de arte, hero assets, ambientação, inspeção 360° como jogador e prontidão para Roblox.

## QA (versão final)
- **Navegação:** 18/18 rotas OK sobre as colisões `COL_`, verificando degrau, queda, altura livre e corpo livre. As rotas: spawn→Ignis, spawn→mina (dentro do túnel), loja, casa da roda, os 6 portais, ledge→Naruto, Naruto→Konoha (até o portão), margem leste, spawn→salão, salão→fornalha, praça→varanda, praça→balcão e portão do trilho→tremonha.
- **Técnico:** 0 nomes genéricos, 0 malhas sem material, 0 escalas não aplicadas e 11 faces degeneradas minúsculas.

## Métricas do export (EXPORT_ID atual no `montar_lobby_forja.lua`)
| | valor | teto |
|---|---|---|
| MeshParts estáticas | 730 | 750 |
| Triângulos estáticos | 474k | 624k |
| Peças móveis (`LOBBY_VFX_MOVING`) | 23 malhas / 8,5k tris | 30 / 16k |
| Materiais | 134 | 134 |
| MeshParts com sombra | 323 | 350 |
| Colisões (Parts invisíveis) | 813 | 820 |
| Marcadores | 62 | – |
| Luzes | 86 (45 de dia, 41 só à noite) | 45 de dia |

As cotas por dono foram redistribuídas sem mexer nos tetos globais de MeshParts e triângulos. Na rodada 2, arquitetura e terreno ganharam a folga de forja, portais e vegetação. Com os portais v3, os portais ficaram com 148 MeshParts e 90k triângulos.

O teto de materiais subiu de 120 para 134, porque no Roblox cada material é só cor e `Enum.Material`, e o custo real está nas MeshParts, que têm teto próprio. O remapeamento do teto segue três regras:
- só troca cores de **mesmo matiz**, então lilás não vira prata e laca não vira telha;
- nunca encadeia trocas;
- nunca mexe em `Ember_Glow`/`Fire_Glow_`, que o VFX acha pelo nome, nem nos 3 tons das glicínias.

## Integração no Roblox Studio
Este export foi gerado com `FM_ROOT_OFFSET="4000, 0, 0"` para não sobrepor o `LOBBY_MURIM`, que está na origem. Para trocar de lugar, basta editar `ROOT_OFFSET` no topo do `montar` e rodar de novo; o script é idempotente.

Só a importação dos FBX exige a interface do Studio. O resto (`montar`, VFX e LocalScript) roda pelo MCP do Studio (`execute_luau`) com um servidor local: `python -m http.server 8771` na pasta `export/`, e depois `loadstring(HttpService:GetAsync(...))()`.

1. Rode `export_all.py` e importe no 3D Importer **todos** os `LOBBY_*_<ID6>.fbx` do mesmo passe para `workspace.LOBBY_FORJA`, com as texturas embutidas. Espere as texturas processarem: as peças ficam brancas por alguns minutos.
2. Rode `export/montar_lobby_forja.lua` na Command Bar. Ele:
   - confere a importação e **alinha** cada MeshPart;
   - aplica cor/material por variante, sombra e fidelidade;
   - cria colisões, marcadores, luzes (as NightOnly ficam desligadas), chão distante e rede de quedas (`VOID_CATCH`).
   
   Opções no topo do script: `ROOT_OFFSET`, `RICO`, `LISO`, `APLICAR_LIGHTING`.
3. Importe `LOBBY_VFX_MOVING_<ID6>.fbx` do mesmo passe e rode `export/vfx_lobby_forja.lua`, que cria fogo, fumaça, faíscas, cachoeiras, espirais, roda, martinete, foles e o carrinho de mina.
4. Coloque `export/vfx_lobby_forja_client.lua` como LocalScript em StarterPlayerScripts.

O próprio `montar` recomenda `StreamingEnabled` com TargetRadius 1024 e MinRadius 128.

Para ligar o jogo:
- **Ignis:** rig em `NPC_Ignis` com a tag `FORJA_Ignis`; o KeyframeMarker `Golpe` dispara as faíscas.
- **Portais:** gatilho em `PORTAL_*`.
- **Konoha:** `WORLD_EXIT_Naruto` / `WORLD_ENTRY_Naruto`, alinhados com a entrada da Área 1.

## Limitações reais
- **Prévia no place:** a prévia antiga com EditableMesh (`workspace.LOBBY_FORJA_PREVIEW`) foi apagada em 2026-09-24. O place não foi salvo por nenhum agente.
- **Não testado no Studio:** os FBX finais não foram importados pelo 3D Importer real, porque ele exige a interface. O `montar` confere e realinha a importação, mas a primeira importação precisa de uma olhada humana.
- **VFX:** as partículas, os Beams e as animações foram escritos e compilam, mas não foram vistos rodando no Studio. Taxas e cores podem pedir ajuste fino.
- **One Punch Man:** o disco de trás (`PORTAL_OnePunchMan_SwirlBack`) recebe a textura mas não gira; só aparece por trás do muro.
- **Engrenagens da forja:** as engrenagens de parede da ala direita foram fundidas na malha da ala e ficam paradas.
- **Proxies:** o Ignis continua um proxy em blocos e o quadro de líderes está vazio.
- **Render vs Roblox:** o render do Blender usa AgX + névoa de compositor, e o Roblox usa o próprio Lighting e Atmosphere. O perfil recomendado está no `montar` (`APLICAR_LIGHTING`) e nas notas de validação.
