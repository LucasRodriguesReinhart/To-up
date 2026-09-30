# Onda 0: base da planta v4 (2026-09-30)

## Build e QA
`build_sg` roda de ponta a ponta em 17 s.

**Zonas em detalhe:** entrada, invocação, alquimia e saída. São os módulos da v3, rodando pelo `sg_relocate` e só mudados de lugar. A saída gira 120° para o noroeste e sobe 8 de cota.

**Zonas em blockout v4:**
- terreno;
- vila (a praça e a fonte da v3 foram realocadas);
- castelo;
- salão com o trono móvel;
- salão sombrio (zona nova `cave`);
- masmorra;
- água (só a pedra das bicas);
- ambientação.

**QA** (`qa_onda0.txt`, `ilha_shadowgarden.blend`): 71 OK, 0 FAIL.

| Teste | Resultado |
|---|---|
| ROTAS | 27/27 |
| ROTAS_ABERTAS | 3/3 (portão DS, e trono aberto → caracol → salão sombrio → portal, na descida e na subida) |
| ROTAS_MODULOS | 9/9 |
| SONDAS | 29/29 |
| SALAO_LIVRE | OK |
| DUNGEON_LIMPA | OK |
| CAVE_LIVRE (novo) | OK |
| Marcadores | 0 faltando |
| Técnico | 0 degeneradas |

- **Rotas novas:**
  - âncora da Ilha 2 → ponte curva de 234 → entrada;
  - spawn → porta → trono;
  - trono aberto → escada caracol (60 degraus, 2 voltas) → galeria → escadaria → ponte do rio → estrado do portal, e o caminho inverso;
  - salas R1 → R2 → R3;
  - passarelas e ponte suspensa;
  - 7 casas (porta → dentro) e as 5 de 2 andares (escada → andar de cima);
  - saída noroeste e jardim-mirante.
- **Sonda nova:** `TRONO_FECHADO_tapa_o_arco`, que confirma que o trono em repouso fecha a passagem.

## Totais (export de teste 6e214e20, feito em pasta temporária, sem mexer em `export/`)
| | Blockout | Teto |
|---|---|---|
| Tris estáticos | 226.336 | 860.000 |
| MeshParts estáticas | 350 | 870 |
| Materiais | 68 | 130 |
| Luzes de dia | 35 | 48 |
| COL | 911 | 1.800 |

- **Por dono (tris / MeshParts):** castle 2,4k/12, cave 13,5k/30, craft 80,4k/59, dungeon 1,0k/8, entry 34,8k/38, exit 24,0k/30, gate_ds 9,7k/17, hall 1,5k/8, summon 28,9k/44, terrain 4,4k/11, village 17,0k/57, vfx 5,5k/25.
- As zonas em blockout ficam muito abaixo dos tetos; a onda 1 é que ocupa o orçamento.

## Encaixe conferido no export
- **`WORLD_FROM_PREV`:** (−579,227; 28,2; 650,727), igual à âncora da Ilha 2. A frente da ponte é (−0,920; 0; −0,391), igual ao rumo da Ilha 2.
- **`ISLAND_NEXT_ANCHOR_DemonSlayer`:** (−1534,5; 52,2; 962,4), frente (−0,766; 0; 0,643).
- **Distâncias** (contorno sem ilhotas):

| Até | Distância |
|---|---|
| Caixa da Ilha 2 | 219 (entre bordas, 301) |
| Ilha 1 | 604 |
| bbox dos picos do lobby | 271 |

## Marcadores
- `marcadores_onda0.md`: por sistema (trono, DungeonService, salão sombrio, água, mundo, mineração, invocação/alquimia, áudio), com posição Roblox, frente e atributos.
- `marcadores_onda0.json`: os 281, com os vetores x/y e todas as props.

## Mudanças em relação ao PLANO.md (medidas finais da onda 0)
- **Abóbada do salão sombrio:** até 41, não 46. Fica abaixo do fundo da laje do P3 (42,2) e o pé-direito continua em 53.
- **Ponte de chegada:** 234, e não 232, com 2 studs retos na âncora para sair tangente ao rumo da Ilha 2.
- **Praça (R 26 com fonte R 7), invocação (R 22) e entrada:** com as MESMAS medidas da v3, só transladadas, para os módulos antigos rodarem sem mudança.
- **Casas:** escada reta ao longo do fundo, com 6 de largura e piso de 1,6. O pé-direito é 12, e 14 no salão da taverna.
- **`FX_Fall_*`:** a tabela é estimada pela planta. O `sg_water` mede e corrige quando rodar na v4.
- **`VOID_CATCH`:** fica em −100, com 800 × 560.

## Arquivos da onda 0
- **Editados:** `sg_layout`, `sg_col`, `sg_core`, `sg_blockout`, `sg_qa`, `sg_map`, `sg_scene` (câmeras e silhuetas dos vizinhos só na prévia), `studio_sg`, `export_sg` e `build_sg`.
- **Novos:**
  - `sg_layout_v3.py`: cópia congelada da planta v3;
  - `sg_relocate.py`: roda os módulos da v3 no referencial deles e transforma o resultado.
- **Nenhum código de detalhe foi apagado:** `sg_castle`, `sg_hall`, `sg_dungeon`, `sg_village` (exceto `plaza`), `sg_terrain`, `sg_water`, `sg_court`, `sg_veg`, `sg_garden`, `sg_props` e `sg_lights` só deixaram de ser chamados, pelo `build_sg.ZONE_MODULES`.
- **Na onda 1**, o módulo refeito na v4 entra em `ZONE_MODULES` e, quando for o caso, sai de `LEGACY`.
