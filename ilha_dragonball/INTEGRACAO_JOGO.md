# Ilha 2 (Dragon Ball) — produção e integração no jogo

Status em 2026-09-25 (noite): a ilha foi modelada, revisada, exportada, importada no Roblox Studio, integrada e **testada em Play**.
O place não foi salvo nem publicado pelo agente. Salvar ou não fica com você.

Vídeo dentro do jogo: [renders/final/ilha2_ingame_2026-09-25.mp4](renders/final/ilha2_ingame_2026-09-25.mp4).
Renders finais e prancha concept × render: [renders/final/](renders/final/) (`_compare.jpg`, `_grid.jpg`).

## Como a ilha foi feita (Blender, headless)
- **Planta travada:** [db_layout.py](db_layout.py). A ilha encaixa na `ISLAND_NEXT_ANCHOR` da Ilha 1 com giro de 135°. Tem 360° de leitura:
  - Capsule (herói) ao norte;
  - vila tech entre o Capsule e a arena;
  - summon a oeste;
  - arena de mineração no centro;
  - saída a leste (portão Shadow Garden);
  - entrada ao sul, vinda da Ilha 1.
- **Colisão andável congelada:** [db_col.py](db_col.py). Pisos, escadas, rampas e guardas invisíveis, todos em Parts simples.
- **Módulos por zona** (prefixo = dono no export):
  - `db_terrain*` (DB_Ter_);
  - `db_mining` (DB_Mine_);
  - `db_entrance` (DB_Ent_);
  - `db_capsule*` (DB_Cap_);
  - `db_village*` (DB_Hub_);
  - `db_towers` (DB_Twr_);
  - `db_summon` (DB_Sum_);
  - `db_water` (DB_Water_);
  - `db_exit` (DB_Exit_);
  - `db_veg*` / `db_props` / `db_lights` (vestir).
- **Pipeline:** blockout aprovado internamente, depois 3 ondas de agentes (construir → crítico independente → corrigir). No fim, uma revisão da ilha inteira com 3 críticos (fidelidade à concept, experiência do jogador, art pass) e correções por zona.
- **QA** ([db_qa.py](db_qa.py)): andador sobre as COL_ com degrau 2,3, queda 2,3, corpo 1,1 e teto 6,5. Resultado final:

| Verificação | Resultado |
|---|---|
| Rotas da missão | 13/13 |
| Rota com o portão aberto | 1/1 |
| Rotas internas das zonas | 30/30 |
| Sondas de borda | 41/41 |
| Largura mínima 3,4 | ok |
| Marcadores obrigatórios | todos |

- **Revisão visual:**
  - [db_review_cam.py](db_review_cam.py) faz caminhadas em 3ª pessoa sobre as rotas, com câmera tipo Roblox;
  - [db_sheet.py](db_sheet.py) monta as pranchas concept × render.
- **Export** ([export_db.py](export_db.py), modo estrito): `1d00de62`.

| Item | Quantidade |
|---|---|
| FBX | 11 |
| MeshParts | 551 |
| Triângulos | 446.816 (limite 480 mil) |
| Colisões | 1.517 |
| Marcadores | 169 |
| Luzes de dia | 33 |

## Como ficou montado no Roblox
```
export/ILHA2_*_1d00de.fbx  --3D Importer-->  workspace.ILHA_DRAGONBALL
   --montar_ilha_dragonball.lua + roblox/pos_montagem_dragonball.lua-->  ServerStorage.IlhaDragonBall (FONTE)
   --clone em runtime-->  workspace.Areas.Area2.ILHA_DRAGONBALL   (Core.DragonBallIsland.build, chamado pelo IslandWorld)
```
- **Importação:** 551/551 MeshParts. Dois nomes de peças do portão foram truncados pelo importador ("…") e renomeados antes de montar. Alinhamento: giro de 180° corrigido, escala 1,000.
- **`Core.DragonBallIsland`** (novo, [roblox/DragonBallIsland.lua](roblox/DragonBallIsland.lua)) segue o mesmo contrato do `Core.NarutoIsland`.
  - Atributos: EntryPosition/EntryForward, SafePosition, SafeMaxY, BoundsCenter/BoundsHalfSize, RotaPropria, GachaPosition e NextAnchor*.
  - Minério: zona `MiningZone_DragonBall` + 75 bloqueios `GP_Block_*` (rochas, pod, acessos, anel junto ao muro).
  - Pontos de minério: 52 marcadores ORE_* válidos + 136 da grade hexagonal. No Play nasceram 70 minérios dentro da bacia (raio máximo 57, vizinho mínimo 7,4).
  - Invocação: a máquina `Gacha_ki` vira o motor invisível da torre. O prompt "Invocar" fica no portal.
  - Portão Shadow Garden: peça `NextAreaId=4` + placa de preço + disco de viagem na âncora.
  - VFX: névoa no pé das quedas, borrifo nos degraus e no poço NW, energia do summon e faíscas do portão.
- **`IslandWorld`:** 1 linha nova antes do Vale Capsule. **Rollback:** renomeie `ServerStorage.IlhaDragonBall` e a área 2 antiga (`DragonBallArea` / `CapsuleIsland`, intocadas) volta.
- **`IslandTravel`** foi substituído pela versão por regiões ([roblox/IslandTravel_regioes.lua](roblox/IslandTravel_regioes.lua)).
  - Motivo: a Ilha 2 fica fora das faixas de Z do mundo em linha reta.
  - Cada área pode declarar BoundsCenter/BoundsHalfSize. Há histerese onde as caixas se tocam, e o jogador olha para `EntryForward` ao chegar.
  - A regra antiga do lobby foi mantida.
- **`ILHAS_Cliente`** (novo LocalScript, [roblox/ILHAS_Cliente.client.lua](roblox/ILHAS_Cliente.client.lua)) substitui o `ILHA_NARUTO_Cliente`, que ficou desligado.
  - Estado de todos os portões de compra por jogador (DB, ShadowGarden, …).
  - Culling dos VFX e pulsos.
- **`Core.NarutoIsland`:** com `ServerStorage.IlhaDragonBall` presente, tira da ponta da Ilha 1:
  - a guarda provisória (EXIT_AnchorGuard + COL);
  - o disco `ViagemProximaArea`.
  
  A ponte da Ilha 2 encosta ali com **distância 0,000** entre `ISLAND_NEXT_ANCHOR` e `WORLD_FROM_PREV`.
- **`ILHA_DRAGONBALL_Servidor`**, gerado pelo montar, ficou desligado, como o da Ilha 1.
- **Backups:** `ServerStorage.BeforeIlhaDragonBall_20260925` guarda IslandWorld, IslandTravel, NarutoIsland e ILHA_NARUTO_Cliente de antes.

## Testes em Play (perfil sem salvar: DebugV31 `semSalvar` / `perfilNovo`)
- **8/8 rotas da missão andando de verdade** (Humanoid:MoveTo sobre a colisão), 0 recuperações do IslandTravel:
  - Ilha 1 (ponta) → entrada DB;
  - entrada → arena;
  - entrada → Capsule (até o salão);
  - arena → summon;
  - arena → Capsule;
  - arena → portão SG;
  - Capsule → portão SG;
  - summon → portão SG.
  
  A área muda para 2 ao pisar na ponte.
- **Mineração:** golpes tiram HP, o minério quebra, entra `ki_comum` na mochila e ele renasce.
- **Invocação:** o prompt "Invocar" fica a 3,8 do jogador. O giro `single` entregou o pet Kuririn (tema ki).
- **Portão Shadow Garden** (perfil novo):
  - fechado: barreira pulsando, colisão ligada, placa de preço e prompt "Desbloquear";
  - compra sem a área 3: **"Compre Monte Natagumo antes"** (ver pendências);
  - compra com a área 3: abre na hora (barreira some, colisão desliga, prompt "Viajar").
- **Output limpo** em todas as sessões: nenhum erro nem aviso da ilha.

## Pendências / decisões suas
1. **Ordem das áreas × portão Shadow Garden.**
   - A missão manda a saída da Ilha 2 para o **Shadow Garden**, que no `Config` é a **área 4**. A área 3 é o Monte Natagumo (Demon Slayer).
   - O `Progresso.comprarArea` exige a área anterior, então quem vem da Ilha 2 recebe "Compre Monte Natagumo antes".
   - Não mexi na ordem das áreas nem na regra de compra. É decisão de economia e de progresso: reordenar o `Config` ou liberar a exceção.
2. **Nome da área 2:** no `Config` ela continua "Planeta Namekusei". A ilha nova é Dragon Ball / Capsule. Troque o nome se quiser que a UI acompanhe.
3. `Corredores.Area2_Area3` (passarela antiga que saía da área 2 velha) continua no workspace. Não atrapalha a ilha nova, porque fica longe.
4. **Salvar o place:** tudo acima está no Studio aberto e não foi salvo pelo agente.

## Reimportar depois de mudar a ilha no Blender
1. `./run.sh build`, depois `./run.sh qa` (tudo verde) e por fim `blender -b ilha_dragonball.blend --python export_db.py`.
2. Importar os FBX pelo botão Import do ribbon. Com o Studio coberto por outra janela, dá para fazer sem o mouse com `tools/import_ribbon.ps1`: traz o Studio para a frente, clica, preenche o diálogo e confirma o preview.
3. Mover os `ILHA2_*` importados para `workspace.ILHA_DRAGONBALL`.
4. Rodar o `export/montar_ilha_dragonball.lua` e, se ele acusar nomes faltando, conferir nomes truncados com "…".
5. Rodar `roblox/pos_montagem_dragonball.lua`, que move a ilha para `ServerStorage.IlhaDragonBall` e guarda a anterior.
