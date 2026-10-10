# Ilha 5 One Piece / Wano V2: import no Studio (export 20f29090)

Gerado em 2026-10-10 por `./run.sh export`, depois da reconstrução V2 que respondeu à reprovação do usuário (`feedback_20261010/FEEDBACK_USUARIO.md`, U1–U16 e G1–G7).

**Resultado:**
- EXPORT OK;
- CONEXAO `WORLD_FROM_PREV` × âncora da Ilha 4: **0,0000**;
- `./run.sh qa` verde: rotas 15/15, sondas 31/31, `PRACA_LIVRE`/`PISO` OK, gate visual VERDE (chão alcançável sem colisão 4,5 studs², corpo dentro 0, frestas 0).

O passo a passo completo (backup, scripts, patches e Play) continua em `../roblox/LEIA_M5.md`.

## Antes de importar
- **Apague o import anterior** (export `37998c7c`) de `workspace.ILHA_ONEPIECE` e tire do caminho o `ServerStorage.IlhaOnePiece` antigo (backup). O montar confere o `EXPORT_ID`, e os nomes das malhas mudaram.
- **Não há mais `ILHA5_09_PROPS`.** Os props V1 foram reprovados (U7/U15/U16); postes, lanternas e poços novos estão dentro da capital, da praça e da entrada.

## FBX (13, todos com o sufixo `_20f290`)

| # | FBX | Conteúdo |
|---|---|---|
| 1 | `ILHA5_02_TERRAIN` | Falésias de Wano V2, pele na cota da colisão, socalcos NE, picos, rochedo do castelo |
| 2 | `ILHA5_03_PLAZA` | Praça de mineração com lajes, medalhão, meio-fio e guarda-corpo |
| 3 | `ILHA5_18_ENTRY` | Ponte de chegada, viaduto, grande torii, pátio |
| 4 | `ILHA5_05_CAPITAL` | 101 lotes do kit V2 em 12 quadras, ruas, santuário NE, 4 interiores |
| 5 | `ILHA5_04_CASTLE` | Castelo V3 e árvore arqueada |
| 6 | `ILHA5_06_SUMMON` | Convés pirata e torre AMS intacta |
| 7 | `ILHA5_07_WATER` | Canais rebaixados, pontes em arco, roda d'água |
| 8 | `ILHA5_16_HARBOR` | Porto vivo e navio atracado |
| 9 | `ILHA5_10_VEGETATION` | Cerejeiras, kuromatsu, árvores largas, karikomi |
| 10 | `ILHA5_17_LANDMARKS` | Caveira e espada (o pagode saiu) |
| 11 | `ILHA5_08_NEXT_ISLAND` | Ponte de saída e guarda provisória |
| 12 | `ILHA5_08_PURCHASE_GATES` | Portão One Punch Man (inalterado) |
| 13 | `ILHA5_12_VFX_HELPERS` | 15 peças móveis: barcos que balançam, tambor e lingada do guindaste, junco, roda, anéis e estrela do summon |

## Totais

| Item | Valor |
|---|---|
| MeshParts | 514 |
| Tris | 651.244 (639k estáticos + ~12k móveis) |
| Materiais | 77 |
| Colisões | 1.234 depois da união |
| Marcadores | 230 |
| Luzes | 56: 12 ativas de dia e 44 `NightOnly` |
| MeshParts com sombra | 260 |
| Peças móveis | 15 |

## Depois do import
1. Mova os grupos importados para `workspace.ILHA_ONEPIECE`.
2. Rode `montar_ilha_onepiece.lua` (`EXPORT_ID = 20f29090`).
3. Rode `../roblox/pos_montagem_onepiece.lua`.
4. **Scripts:**
   - `AreaAtmosphere`: troque **só a linha `[5]`** pela de `../roblox/AreaAtmosphere_area5.lua` (perfil rosa-lilás da ref_03). O resto do arquivo pertence a outras sessões.
   - `CeuWano`: atualize as constantes `BLOOM`, `RAIOS` e `NUVENS`.

**Pétalas:** são 13 emissores `FX_Petals_*` por grupo de cerejeiras, mais 1 na praça. O `FX_Petals_Tree` continua como marcador, mas mudo: a árvore monumental agora é pinheiro.
