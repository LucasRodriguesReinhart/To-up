# Ilha 1 — Vila da Folha (Naruto) · Anime Mining Simulator

Ilha 1 definitiva, construída no Blender 5.2 a partir das 11 referências aprovadas (`refs/`). Está pronta para o
3D Importer do Roblox: FBX por coleção, colisão em Parts, marcadores e um script de montagem.

> **Estado:** tudo gerado e verificado no Blender e nos QAs automáticos. **Nada foi importado nem salvo no place
> do Roblox.** A importação e o teste de Play ficam para quando você quiser (ver *Limitações*).

## Entregáveis

| O quê | Onde |
|---|---|
| Cena final | `ilha_naruto.blend` (coleções 00–15, `_SCALE_REFERENCE` incluída) |
| Renders finais 1920×1080 | `renders/final/CAM_*.jpg` (22 câmeras) |
| Prancha de contato | `renders/final/_contact_sheet.jpg` |
| Referência × render | `renders/final/_compare.jpg` |
| Export da ilha | `export/ILHA1_*.fbx` (10 FBX), `export/ilha_data.json`, `export/montar_ilha_naruto.lua` |
| Conexão com a Ilha 2 | `export/conexao_roblox.json` + [`CONEXAO_DRAGONBALL.md`](CONEXAO_DRAGONBALL.md) |
| 4 portões de compra (assets avulsos) | `export/portoes/<ShadowGarden\|DemonSlayer\|OnePiece\|OnePunchMan>/` |
| Relatórios do QA e do export | `renders/qa_final.txt`, `renders/export_final.txt` |
| Scripts | `build_ilha.py`, `export_ilha.py`, `export_ilha_lua.py`, `export_portoes.py`, `il_qa.py`, `run.sh` |
| Análise e processo | [`ANALISE_REFERENCIAS.md`](ANALISE_REFERENCIAS.md), [`RODADA2.md`](RODADA2.md), [`AGENT_BRIEF.md`](AGENT_BRIEF.md) |

Para reconstruir: `./run.sh build`. Para exportar: `blender -b ilha_naruto.blend --python export_ilha.py` e, por
portão, `--python export_portoes.py -- <chave>`. Para o QA: `./run.sh qa nav markers tech`.

## A ilha

Referencial de projeto: origem no centro do fosso, +Y é o norte (vila) e Z é a altura absoluta do Roblox. No mundo
do lobby, Roblox = (−x, z, 420 + y).

```
                 PAREDÃO (3 quedas, platô com 3 construções)
      SUMMON  ←  VILA (salão, 2 prédios redondos, loja, ramen, casas)  →  PONTE DE SAÍDA → PORTÃO DB → ÂNCORA
      (oeste)             T2 22,2 / T1 16,2                              (nordeste, 45°)
                   ANEL 10,2 ── FOSSO DE MINERAÇÃO 3,2 (r 60)
      riacho oeste                                     vale leste: bica, roda d'água, ponte em arco, queda SE
                    ENTRADA (portão, leões) ← ponte do lobby (WORLD_FROM_LOBBY)
```

- **Entrada (sul):** ponte de 24 alinhada à ponte do lobby, portão com telhado verde, 2 leões guardiões
  (`il_lion.py`, compartilhado com o portão DB), lanternas de poste a cada 16 e estandartes nos pilares.
- **Mineração (centro):** fosso limpo de r 60 com cerca, 4 torres de extração com polia e balde, rampas de 8 e
  escadas N/S. Tem um núcleo de cristal baixo (≤ fosso + 8) e 54 pontos de minério: 28 comuns, 16 incomuns, 8 épicos
  e 2 superlendários.
- **Vila (norte):** escadaria central com estandartes. O salão tem o símbolo da Folha, sem rostos de Hokage.
  - Prédios redondos gêmeos de telhado azul, 12 casas baixas (70% terracota, 2 verdes) e 3 construções no platô.
  - **4 interiores funcionais** com NPC e ponto de interação: salão, loja de armas, ramen e moinho (posto de
    venda com balcão alinhado à porta de 10). As casas comuns não têm porta, e não há porta falsa.
- **Summon (oeste):** torre das refs 08–12 com estrela facetada, 3 anéis que giram, constelação azul em 2 asas e
  praça com mosaico. `SUMMON_Interact` e `SUMMON_PlayerPosition` ficam no patamar diante do portal.
- **Água:** 3 quedas do paredão, canal do meio, sistema NE (canal no T2 e queda pela borda, longe da ponte), riacho
  do vale com bica, roda d'água girando, ponte em arco e queda SE. O riacho oeste desce pela borda O.
- **Saída (nordeste):** rua a 45° → ponte em arcos (96 × 18) → ilhota → **portão de compra Dragon Ball** (moon gate
  da ref 13, medalhão de 4 estrelas, esferas flutuando, leões) → patamar → `ISLAND_NEXT_ANCHOR`.
- **Vegetação composicional:** grupos por zona, cinturão na borda e copas nas saliências do penhasco; nada de
  scatter. Ficam livres os eixos, as portas, os canais, as 23 rotas e a linha de visão da chegada até a torre do
  summon. Bandeiras só na entrada, no salão, no summon e na saída.
- **Portões de compra (família):** DB na ilha e ShadowGarden, DemonSlayer, OnePiece e OnePunchMan como assets.
  - Todos têm o mesmo vão 16 × 18, soleira, pedestais com guardião temático, lanternas e emblemas flutuantes.
  - A barreira de energia tem núcleo tingido e cadeado. Cada moldura tem silhueta própria.

## Marcadores (82 no export, pasta `GAMEPLAY_MARKERS`)

`WORLD_FROM_LOBBY`, `WORLD_ENTRY_Naruto`, `PATH_ENTRY_CENTER` (+5 pontos do caminho), `GP_Zone_Pit`,
`ORE_COMMON_*` ×28, `ORE_UNCOMMON_*` ×16, `ORE_EPIC_*` ×8, `ORE_SUPERLEGENDARY_*` ×2, `SUMMON_Main`,
`SUMMON_Interact`, `SUMMON_PlayerPosition`, `NPC_*` e `PLAYER_INTERACT_*` (MainHall, WeaponShop, Ramen, Mill),
`ISLAND_EXIT_Naruto`, `GATE_DB`, `GATE_DB_INTERACT`, `GATE_DB_LOCKED`, `GATE_DB_EXIT`, `GATE_DB_OpenFX`,
`PURCHASE_UI_ANCHOR_DB` e `ISLAND_NEXT_ANCHOR`. Há também 12 pontos seguros de respawn (`SAFE_*`).

## Portões de compra: LOCKED / UNLOCKED

O script de montagem marca as peças com a tag `PortaoCompra`:

- `GATE_<k>_Barrier` (Neon, Transparency 0,2) e `GATE_<k>_Lock`, com os atributos `gate` e `gate_part`;
- `COL_Gate<k>Lock_001`, a colisão de bloqueio, que vai para dentro do Model atômico do portão.

Ele também cria o `ReplicatedStorage.PortoesCompra`:

```lua
require(game.ReplicatedStorage.PortoesCompra).Estado('DB', true)   -- desbloqueia (servidor = todos; LocalScript = só quem pagou)
```

O estado sobrevive ao streaming: peças que chegam depois recebem o estado. O ProximityPrompt vai em
`GATE_<k>_INTERACT` e o BillboardGui de preço em `PURCHASE_UI_ANCHOR_<k>`, dentro do vão. Os 4 portões avulsos
saem centrados, com o mesmo contrato (`montar_portao_<k>.lua` + FBX). O detalhe da conexão com a Ilha 2 e as
mudanças no jogo estão em [`CONEXAO_DRAGONBALL.md`](CONEXAO_DRAGONBALL.md).

## Métricas finais

**Navegação** (`il_qa.py`, walker com passo 2,3, queda 2,3, cabeça 6,5 e corpo 1,1), na cena final:

| Verificação | Resultado |
|---|---|
| 14 rotas da missão (entrada→mineração/summon/vila, mineração→summon/saída, vila→saída, saída→portão DB, loja→mineração, summon→saída, anel→ramen/moinho, fosso→rampa L→anel, volta no anel, ponte do lobby) | **14/14 OK** |
| 6 rotas internas (porta→balcão do salão, loja, ramen e moinho; ponte em arco; portão DB aberto→âncora) | **6/6 OK** |
| 23 rotas registradas pelos módulos (escadas laterais, caminhos das casas, contorno do núcleo, margem do riacho, praça→portal do summon, moinho…) | **23/23 OK** |
| 27 sondas de borda (fenda NE do T2, borda da âncora, pontes, rampas do fosso, patamar da entrada, moinho…) | **27/27 OK** |
| Largura (corpo r 1,7) | nenhum trecho < 3,4 |
| Marcadores obrigatórios | 0 faltando; minério 28/16/8/2 sem sobreposição |
| Técnico | 0 nomes genéricos, 0 duplicados, 0 sem material, 0 transformações pendentes, 0 faces degeneradas |

**Export da ilha** (orçamento para celular; todos os donos dentro do limite):

| | valor / limite |
|---|---|
| MeshParts | 472 / 660 |
| Triângulos | 326.409 / 470.000 |
| Materiais | 82 / 110 |
| Colisões (Parts COL) | 1.095 / 1.150 |
| MeshParts com sombra | 242 / 300 |
| Luzes ativas de dia | 11 / 36 (33 no total, as externas só à noite) |
| Peças móveis | 12: estrela e 3 anéis do summon, roda d'água, engrenagem, eixo e pilão do moinho, 4 esferas do DB |

**Triângulos e MeshParts por zona:**

| Zona | Triângulos (limite) | MeshParts (limite) |
|---|---|---|
| terreno | 97,5k (110k) | 88 (130) |
| vila + casas | 76,1k (100k) | 128 (150) |
| entrada | 24,8k (32k) | 28 (42) |
| summon | 23,7k (38k) | 25 (48) |
| mineração | 23,4k (48k) | 33 (70) |
| portão DB | 20,8k (26k) | 23 (34) |
| vegetação | 18,5k (45k) | 51 (60) |
| água | 18,2k (24k) | 34 (38) |
| saída | 13,9k (22k) | 26 (32) |
| VFX | 5,8k (12k) | 23 (28) |
| props | 3,5k (26k) | 13 (45) |

**Portões avulsos:**

| Portão | Triângulos | MeshParts |
|---|---|---|
| ShadowGarden | 10.088 | 24 |
| DemonSlayer | 10.920 | 25 |
| OnePiece | 13.352 | 27 |
| OnePunchMan | 7.692 | 23 |

**Streaming:** cada construção vira um Model atômico: salão, loja, prédios redondos, ramen, moinho, cada casa
(`VIL_House_*`), torre do summon, portão da entrada, portão DB e guarda da âncora. As ilhotas do céu ficam
persistentes.

## Processo (16 passes)

1. Análise das referências e medidas.
2. Planta travada (`il_layout.py`).
3. Blockout com gate de qualidade.
4. Navegação no blockout.
5. Rodada 1: 9 zonas em paralelo.
6. Integração.
7. Correções da integração.
8. Ambientação (vegetação, props, luzes).
9. Crítica independente (arte, level design e técnica).
10. Rodada 2B, onda 1 (terreno, rocha, água, mineração, saída + DB).
11. Integração da onda 1.
12. Rodada 2B, onda 2 (casas + moinho, vila, summon, entrada + leão, galeria).
13. Integração da onda 2.
14. Polimento (saliências, energia dos portões).
15. QA técnico e export final.
16. Renders finais e revisão 360° (Front/Left/Right/Back/BirdEye + 5 vistas das referências).

## Limitações e pendências

- **Não importado no Roblox.** O place não foi aberto para edição nem salvo. Faltam:
  - importar os 10 FBX no 3D Importer;
  - rodar `montar_ilha_naruto.lua` no command bar;
  - testar em Play.
  O bloco novo do script (a marcação da guarda da âncora) foi só revisado à mão. A checagem de compilação no
  Studio foi bloqueada pelo modo automático. O resto do script já tinha compilado no Studio numa rodada anterior.
- **O jogo precisa mudar** (detalhes em `CONEXAO_DRAGONBALL.md`):
  - o `IslandTravel` decide a área pela faixa de z, mas a saída agora vai para nordeste; precisa decidir por região;
  - a `Parede2` do `Core.Paredes` perde a função, porque o portão DB a substitui;
  - streaming: recomendo raio mínimo de 512–640 para a ilha inteira carregar a partir do centro.
- **Guarda da âncora:** é provisória. A Ilha 2 tem que apagar as peças com a tag `GuardaProximaIlha`.
- **Cores da prévia × Roblox:** a prévia usa Standard com emissão limitada. No Roblox os `*Glow` viram Neon, mais
  fortes, e a água sai como MeshPart translúcida, não Terrain water.
- **Pequenos pontos conhecidos:**
  - o piso visual da praça do summon fica 0,3 acima da colisão (o pé afunda 0,3);
  - o ramen ficou alto para a planta, por causa do pé-direito ≥ 12 exigido;
  - a trilha de lanternas da rua de saída tem só 1 lanterna no lado NO (uma lanterna ali cortava a rota natural);
  - os caminhos de lajota terminam em fachadas sem porta, onde há janelas com alpendre.
- **Kits do lobby:** o `hip_roof` e o `barrel` têm 2 folgas abaixo de 0,1 (friso a 0,035 e aro a 0,09). Não
  mexi para não alterar o export do lobby.
- **Portão DB:** com ele aberto, a passagem é o círculo do moon gate. Na altura do joelho são ~8 de largura nas
  bordas, por desenho.
- **Portões avulsos:** a soleira tem 22 e os plintos vão até ±18. A ilha de destino precisa de chão em volta.
- **Contagem técnica:** o QA conta ~18,6 mil arestas não-manifold. São primitivas com fundo aberto enterrado; não
  afetam MeshParts nem colisão, que é toda por Parts `COL_`.
