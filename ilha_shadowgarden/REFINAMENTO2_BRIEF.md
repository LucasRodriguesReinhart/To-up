# Refinamento definitivo (nova referência, 2026-09-28)

Referências novas em `refs/v2/` (9 imagens + recortes). Leitura: a imagem da caverna (`ref2_dungeon_cave.png`) é a
referência da ENTRADA DA DUNGEON. As regras do `AGENT_BRIEF.md` e do `REFINAMENTO_BRIEF.md` continuam valendo
(emblema único `sg_emblem`, paleta com função, rotas 14/14, salão livre, dungeon limpa).

## Diagnóstico (contra a referência v2)
- Macro layout já bate com a referência; o problema é a apresentação de cada zona.
- Castelo: massa num só valor, coroa baixa; falta o grande portal ogival violeta aceso na fachada, estandartes
  ladeando e muitas janelas quentes.
- Iluminação chapada: falta o RITMO de lanternas quentes (calçada, muralhas, pontes, praça).
- Cores: falta azul-noite profundo e roxo saturado no céu, na água e na rocha; sem cristais/veios violeta na borda.
- Dungeon: ainda é "casa com fachada"; a referência é BOCA DE CAVERNA na rocha, túnel até o vórtice, ponte de
  aproximação com estandartes e cristais em pedestais, correntes, cachoeiras dos lados.
- Alquimia: pavilhão pequeno (interior 21 studs), caldeirão no chão; a referência é salão nobre com estrado, círculo
  mágico, estantes acesas, lustre de cristal, galeria superior, mesas de estudo.
- Estandartes apagados: a referência tem estandartes longos, escuros, debrum DOURADO e símbolo aceso.
- Skybox/VFX: no Roblox a área usa o céu de dia escurecido; falta lua grande, estrelas, bloom, cristais pulsando.
- Chegada nua: na referência a calçada de entrada é o corredor cerimonial mais forte do mapa.

## Princípios a adaptar
1. Catedral de agulhas: coroa mais alta/densa, portal ogival violeta aceso na fachada, estandartes, janelas quentes
   no corpo e violeta no alto.
2. Ritmo de lanternas (Neon; poucas luzes reais) na ponte de chegada, calçada, eixo, muralhas, praça, ponte de saída.
3. Paleta: roxo profundo, preto, azul-noite, pedra fria, DOURADO (Metal_Gold) nas lanternas e debruns, violeta na magia.
4. Borda viva: cristais violeta (Neon `SG_Crystal_Glow`) nos penhascos e ilhotas, veios na rocha, cachoeiras
   azul-violeta, ilhotas com quedas próprias.
5. Dungeon como caverna (boca na rocha em x 80..126, y 74..116, pode fundir com os montes do terreno; marcadores e
   rotas iguais; caixa DUN_KEEP_OUT intocada).
6. Alquimia como salão nobre: `CRAFT_R` 13 -> 16 (ajustar STREETS: fim da rua em (72,-60); início da rua da saída em
   (104,-36)), estrado do caldeirão com degraus <= 0,8, galeria superior, estantes acesas, lustre de cristal.
7. Praça com marco: estátua encapuçada de manto longo com lâmina na fonte (genérica), lanternas em volta.
8. Roblox: Sky noturno próprio da área (lua grande, estrelas) trocado por LocalScript em `ShadowGardenMood`, bloom no
   perfil do AreaAtmosphere, tag `IlhaPulso` + `Cor0` nos cristais, brilho nos estandartes.
9. Experiência primeiro: cotas, larguras e rotas iguais; nada em rota.

## Mudanças compartilhadas a fazer ANTES da onda (integração)
- `sg_layout.py`: CRAFT_R = 16; STREETS ajustadas; `DUNGEON_CAVE_MASS = (80, 74, 126, 116)`.
- `sg_emblem.py`: `banner(..., trim="Metal_Gold")` e helpers `lantern()` / `lantern_post()` (moldura dourada,
  vidro Lantern_Glow, pedestal de obsidiana) para o ritmo de lanternas em todas as zonas.
- `sg_lib.py`: `SG_Crystal_Glow`; Water_SG mais azul-violeta.
- `sg_scene.py`: lua maior (r ~220 a 1500), estrelas no world shader, céu mais roxo.
- Orçamento total: 560k tris / 800 MeshParts / 42 luzes; por zona: castle 150k/180, dungeon 80k/100, craft 50k/60,
  terrain 120k/150, entry 40k/55, village 70k/100, dressing 90k/150 (studio_sg.BUDGET e export_sg.BUDGET_OWNER).

## Ondas
- Onda A (paralela): castelo v2; dungeon-caverna; alquimia v2; exterior v2 (dressing + village + entry + polimento leve
  do summon: lanternas/estandartes na borda da plataforma); borda (terrain cristais/veios + islets/clouds do
  sg_scene + water).
- Onda B: build completa, renders das mesmas câmeras (renders/integ_v1 = antes), crítica contra `refs/v2`, correções.
- Onda C (Roblox): importar os 14 FBX, montar, `JardimSombrasIsland` + IslandWorld, Sky/bloom/VFX, Play (rotas,
  mineração no salão, invocação, craft, masmorra, multiplayer), desempenho vs PERF_BASELINE, vídeo, docs.
