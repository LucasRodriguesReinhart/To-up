# Linha de base de desempenho (antes da Shadow Garden) — 2026-09-28

Play no Studio, cliente, 1 jogador, perfil sem salvar. O jogador foi teleportado a cada ponto e medido depois de 6 s.
O FPS medido tem ruído: o Studio fica em segundo plano e é limitado pelo Windows. Use-o só como comparação relativa.
A memória é o total do processo do Studio, que inclui o datamodel de edição.

| Ponto | FPS | Memória | Instâncias | Parts | MeshParts | Luzes | Emissores | Render CPU |
|---|---|---|---|---|---|---|---|---|
| lobby | 57 | 4118 MB | 87.563 | 12.727 | 3.429 | 213 | 705 | 16,4 ms |
| Ilha 1 Naruto | 46 | 4134 MB | 87.662 | 12.742 | 3.508 | 214 | 705 | 5,8 ms |
| Ilha 2 Dragon Ball | 15* | 4141 MB | 87.741 | 12.804 | 3.508 | 218 | 707 | 2,4 ms |
| área 4 atual (Shadow Garden antiga, genérica) | 15* | 4176 MB | 102.634 | 24.189 | 3.496 | 195 | 694 | 2,7 ms |

\* Studio em segundo plano durante a medição (o render CPU baixo mostra que não era o jogo que limitava).

**Referência para a nova ilha:**
- ao chegar na área 4, a antiga soma cerca de 15 mil instâncias e 11,4 mil Parts;
- a nova Shadow Garden não deve passar disso sem justificativa;
- alvo: no máximo cerca de 700 MeshParts e 1.800 colisões simples, como a Ilha 2.
