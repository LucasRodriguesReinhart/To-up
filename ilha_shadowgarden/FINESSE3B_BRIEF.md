# Onda FINESSE 3B (2026-10-06): pátio, jardim, alquimia, invocação, saída e água

Vale tudo do `FINESSE3_BRIEF.md` (regras, critério "bom de perto na altura do jogador, no Roblox sem textura",
ambiente Linux com bpy em venv, comandos de studio/build/QA/folha). Leia-o primeiro, inclusive a seção
**Fechamento da onda**: ela lista as pendências que a onda anterior deixou para vocês. A lista de problemas
continua sendo a `AUDITORIA3.md`.

## Agentes (arquivos que NÃO se cruzam)

| Agente | Arquivos (só estes) | Itens da AUDITORIA3 + pendências do fechamento |
|---|---|---|
| **J** pátio e mirante | `sg_court.py` | 02.03, 05.01, 05.02 (bordas e forma dos espelhos), 05.03, 05.04, 05.09, 05.10, 06.03, 13.01, 13.04, 13.05; figura da fonte, figura dos guardas, `statue()` duplicada, fio Neon |
| **G** vegetação | `sg_garden.py`, `sg_veg.py` | 03.03 (touceiras e bordadura), 03.06, 03.07, 05.03 (se a sebe/topiária for de G), 06.08, 13.03, 16.04; floreiras vazias da vila; touceiras dos parapeitos; vegetação cobrindo a arcada do castelo |
| **A** alquimia | `sg_craft.py` | 11.01 a 11.08; MeshParts da zona craft já estão ESTOURADAS (75/74): resolver |
| **S** invocação, saída e água | `sg_summon.py`, `sg_exit.py`, `sg_water.py` | 12.01 a 12.05, 13.02, 13.06, 09.10, conferir 05.02 com os marcadores `WATER_*` |

Depois desta onda (não é seu trabalho): **R** props e vida nas ruas (`sg_props.py`).

**Fronteiras:**
- J × G: J faz caminhos, gramados rebaixados, muretes, espelhos d'água, bancos, estátuas e mirante; G faz tudo que é planta (sebes, topiárias, árvores, grama, flores, trepadeiras). Se uma topiária/sebe for gerada em `sg_court`, ela é de J; combine pelo código, sem editar o arquivo do outro.
- J × V (já concluído): a figura da fonte entra pela função `sg_village.fountain_figure(mb, F, s, z0)`. Crie a figura em `sg_court` (ex.: `fountain_figure(...)`) com a mesma assinatura; escreva em `requests` a linha exata que o `sg_village.py` deve passar a chamar (a coordenação faz a troca). Referencial F com +Y local = frente; s = 0,88; ~6,4 de altura; pé num disco de raio 1,02, 0,46 acima da lâmina d'água da taça de cima; tom claro; ≤ 2k tris.
- J × K (já concluído): os guardas do castelo chamam `CT.hooded_figure(mb, F, 1.5, 5.0, CAPL, kind="guard")` (~11 de altura). Refaça a figura mantendo a assinatura; com escala 1,5 as seções precisam de mais lados. Tire `statue()` dos pontos `STATUES` (±21; 34,5).
- S × W: o `sg_water` só faz pedra de bica e confere marcadores; a água em si é do Roblox. Não mova marcadores `WATER_*`.

## Orçamento: a ilha está no teto
Build atual: **869.129 tris** (teto 870.000). Sobram ~870 tris para a ilha inteira. Por isso:
- **Nenhum agente pode aumentar os tris da própria zona/módulo** em relação ao início desta onda. Geometria nova sai de outro lugar do SEU arquivo.
- Valores do início da onda (studio, `--all-detail`):

| Zona | Tris | MeshParts | Materiais novos | Colisões | Luzes |
|---|---|---|---|---|---|
| dressing (J + G + R + luzes) | 84.643 / 88.000 | 91 / 107 | 2 / 9 | 144 / 160 | 16 / 18 |
| craft | 82.214 / 84.000 | **75 / 74** | 11 / 11 | 74 / 75 | 4 / 4 |
| summon | 30.730 / 31.000 | 43 / 44 | 4 / 5 | 23 / 42 | 3 / 3 |
| exit | 23.984 / 26.000 | 34 / 34 | 0 / 4 | 2 / 45 | 2 / 3 |
| water | 2.332 / 3.000 | 9 / 10 | 0 / 3 | 0 / 10 | 0 / 0 |

- J e G dividem a zona dressing: meçam os tris SÓ do próprio módulo (objetos `SG_Court*`/do `sg_court` para J; `SG_Veg_*`/`SG_Gar*` para G) antes de começar e não passem desse valor.

## Ritmo da máquina
São 4 agentes ao mesmo tempo numa máquina de 4 núcleos e 16 GB. Renderize **no máximo 2 câmeras por rodada**
e nunca rode 2 studios seus ao mesmo tempo. Se o render morrer por memória, espere e tente de novo.

Não faça `git commit` nem `git push`. Relatório final no formato do `FINESSE3_BRIEF.md`.

## Fechamento das ondas 3B e 3C (2026-10-06)

Onda 3B (J, G, A, S) e onda 3C (R, props e vida nas ruas) concluídas e aprovadas pelas folhas no modo Roblox.
Build completo OK com **862.692 tris** (teto 870k), 2203 objetos, 1679 colisões, 61 luzes.
QA: ROTAS 27/27, ROTAS_ABERTAS 3/3, ROTAS_MODULOS 52/52 (6 rotas novas do R), SONDAS 29/29, SALAO_LIVRE,
DUNGEON_LIMPA, CAVE_LIVRE e TECH OK.

| Zona | Tris início → fim | Observação |
|---|---|---|
| craft | 82.214 → 76.392 | MeshParts 75 → 58 (estava estourada) |
| summon | 30.730 → 30.664 | |
| exit | 23.984 → 23.556 | 3/3 luzes |
| water | 2.332 → 2.254 | 10/10 MeshParts |
| dressing (J + G + R + luzes) | 84.643 → 85.378 | 105/107 MeshParts, 153/160 colisões, **18/18 luzes** |

Correções da coordenação nesta onda: colisão das ruas do P2 recortada na face do pórtico da alquimia;
canteiros só no H1, H4 e H7 e floreiras só no H3 e H7; fonte da vila ligada à `sg_court.fountain_figure`.

### Pendências
- **Decisão do usuário:** teto de luzes da zona cave 6 → 8 (cristais 09.14 e luz da queda d'água 09.10).
- **Decisão do usuário:** baixar um tom o Neon do painel do portão Demon Slayer (asset aprovado `il_gate_ds`/`sg_core`).
- **G:** `sg_garden` ler zonas de props (ex.: `sg_props.PROP_ZONES`) para as touceiras ao pé das casas não atravessarem lenha e barris; trepadeira nas pérgulas do mirante e das pontas do pátio.
- **J:** a forma da água dos espelhos continua retangular (água do Roblox); caminho do mirante reto (lajes do `sg_village`, planta travada).
- **Folga:** a zona dressing está sem luzes e quase sem MeshParts; craft com colisões 75/75; hall, cave, castle, dungeon e village no teto de tris.
- **Conferir no Play:** braseiro da H6 e lanterna do pórtico do beco (NightOnly); abertura dos portões das muretas da H1 e H3 (~3,8); fresta de luz na base das casas; vão do portão da muralha (06.13); escuridão do salão.
