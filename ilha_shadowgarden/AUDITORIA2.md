# AUDITORIA 2: passe de acabamento com tolerância zero (Ilha 3, Shadow Garden)

Data: 2026-09-29. Auditor: direção de arte. Nenhum arquivo de código foi editado.

**A pergunta de cada item:** o asset está realmente bom visto de perto? Ter melhorado não basta.

**Base:** as folhas por zona de `renders/auditoria2_antes/`, os JPGs individuais, as capturas do jogo e a leitura dos
módulos `sg_*.py`.

As capturas do Roblox são a fonte mais fiel. Nelas não aparece textura procedural: todo plano liso fica liso de verdade,
e o Neon engole a geometria em volta.

**Legenda de caminhos**

| Prefixo | Pasta |
|---|---|
| `J/` | `renders/auditoria2_jogo/` |
| `F/` | `renders/finesse_depois_jogo/` |
| `A/` | `renders/auditoria2_antes/` |

**Tiers:** A = hero, B = arquitetura, props e ruas, C = silhueta e fundo.

**[CRÍTICO]:** quebra em close-up na câmera normal do jogador (olho a ~5,2 studs, avatar de 5).

Cada item traz a função que gera o asset. As funções compartilhadas (`sg_emblem.*`, `sg_court.hooded_figure`,
`sg_court.iron_arch`, `sg_lib.plan_stair`) corrigem de uma vez dezenas de instâncias. Onde isso acontece, está indicado.

---

## 01 Entrada + praça

### 01.01 [CRÍTICO] Degraus da escadaria da entrada · Tier B
- **Errado:** cada degrau é uma laje-caixa de 18 de largura, lisa e sem junta. O focinho é uma caixa de 0,44 x 0,14
  quase no mesmo valor do degrau. No jogo o lance lê como rampa listrada, um bloco só. Não há espelho recuado, chanfro
  nem divisão em pedras (estrutura, bevel, close-up).
- **Onde:** `J/AU_Stair.jpg`, `F/PlayerHeight_Entry.jpg`, `A/entry/CAM_SG_PlayerHeight_Entry.jpg`.
- **Código:** `sg_entry.py: stair()` → `sg_lib.plan_stair` → `fm_parts.stairs`.
- **Direção:**
  - Cada degrau em 3 a 4 pedras com juntas desencontradas de degrau para degrau.
  - Focinho saliente 0,12 com chanfro de 0,06 e um valor mais claro que a pisada.
  - Espelho recuado e um valor mais escuro.
  - Primeiro e último degrau em cantaria mais larga, com arranque.
  - Mesmo polycount: são caixas, só que partidas e com bevel.

### 01.02 [CRÍTICO] Banzos e muretas inclinadas da escadaria · Tier B
- **Errado:** o banzo é um `yz_prism` liso de 1,4 com uma capa-viga branca de 1,75 × 0,45. É uma rampa de plástico
  sem fiada, sem plinto e sem pilarete de arranque. As duas cintas de obsidiana são fitas coladas (estrutura, material).
- **Onde:** `J/AU_Stair.jpg`, `F/PlayerHeight_Entry.jpg`.
- **Código:** `sg_entry.py: stair_wall()`.
- **Direção:**
  - Paramento em 3 fiadas de cantaria (altura alternada 1,2/0,9) com junta rebaixada.
  - Capa em peças de 2,5 studs com junta e pingadeira por baixo.
  - Plinto de 0,5 no pé.
  - Arranque em voluta ou dado moldurado no pé do lance.
  - Capa em Stone_SG_Trim um valor abaixo (ver 14.01).

### 01.03 [CRÍTICO] Parapeitos da ponte e do pátio baixo · Tier B
- **Errado:** o parapeito é uma viga contínua de 1,2 × 2,0 com uma viga-capa por cima. Muro liso sem balaústre, sem
  painel e sem fiada, repetido por 70 studs. É a cara exata de blockout (silhueta, estrutura).
- **Onde:** `A/entry/CAM_SGEnt_Back.jpg`, `A/entry/CAM_SGEnt_PlayerBridge.jpg`.
- **Código:** `sg_entry.py: parapet_run()`.
- **Direção:**
  - Parapeito gótico com base, faixa de arcadas cegas trilobadas em relevo raso (0,15) a cada ~2 studs e capa com
    pingadeira.
  - Ou balaústres em grupos de 5 entre pilaretes.
  - A face interna, vista pelo jogador, é a que precisa do desenho.

### 01.04 Pilaretes dos parapeitos · Tier B
- **Errado:** caixa de 1,6, capa-caixa, soco-caixa de obsidiana e cabeça de lanterna (ou pirâmide de 4 lados). São 3
  caixas empilhadas com remate primitivo (primitivas empilhadas).
- **Onde:** `A/entry/CAM_SGEnt_Back.jpg`, `J/AU_Stair.jpg`.
- **Código:** `sg_entry.py: _post()`.
- **Direção:** base moldurada (plinto + toro), fuste com quinas chanfradas de 0,15, capitel em 2 degraus e remate do
  kit comum (ver 12.12).

### 01.05 [CRÍTICO] "Cerca de luz" na ponte e no pátio baixo · Tier B
- **Errado:** são pedestais-lanterna a cada 5,6 na ponte, mais os pilaretes com lanterna, mais o par do pátio: 16+
  cubos amarelos em 70 studs, todos iguais. Distribuição uniforme, marca de arte de IA. Eles escondem a escada e os
  pórticos.
- **Onde:** `A/entry/CAM_SGEnt_PlayerBridge.jpg`, `A/entry/CAM_SGEnt_Front.jpg`, `A/_folha_entry.jpg`.
- **Código:** `sg_entry.py: parapets()` (`BRIDGE_LANTERNS`, `lit`), `_post(lamp=True)`.
- **Direção:** tirar os 3 pares intermediários da ponte. Lanterna só nos pilares da ponte e no par da cabeceira. Nos
  vãos, remate de pedra.

### 01.06 [CRÍTICO] Fustes dos pórticos A/B · Tier A (entrada)
- **Errado:** o fuste é uma caixa lisa s × s.
  - A "janela cega" são 2 caixas de 0,3 e 2 vigas de 0,24: palitos colados na face, sem recuo.
  - Os gabletes da coroa são triângulos planos de 0,57.
  - Os pináculos são caixa mais pirâmide de 4 lados.
  - De perto é um totem de blockout com 4 estandartes iguais (estrutura, detalhe colado).
- **Onde:** `A/entry/CAM_SGEnt_Back.jpg`, `F/PlayerHeight_Entry.jpg`, `J/AU_Stair.jpg`.
- **Código:** `sg_entry.py: pylon()`, `lancet()`.
- **Direção:**
  - Fuste com quinas chanfradas e colunelos de canto até o friso.
  - Janela cega como painel rebaixado 0,3 com arco ogival de espessura real e peitoril.
  - Faixa de fiadas no terço inferior.
  - Gabletes com espessura, cimalha e florão.
  - Pináculos do kit comum.

### 01.07 Lanterna baixa ao pé dos pórticos · Tier B
- **Errado:** caixa `Lantern_Glow` de 0,95 × 1,3 entre 4 montantes, chapéu de 4 lados e pedestal-caixa. É o cubo
  amarelo (ver 12.01).
- **Onde:** `A/entry/CAM_SGEnt_Back.jpg`, `A/entry/CAM_SGEnt_PlayerStairTop.jpg`.
- **Código:** `sg_entry.py: lantern()`.
- **Direção:** usar a lanterna nova do kit (12.01). O pedestal vira balaústre torneado curto.

### 01.08 Verga do pórtico B · Tier A
- **Errado:** barra de obsidiana lisa com filete violeta e a placa da ordem colada nas 2 faces. Sem moldura nem
  aduela. É mais uma placa com emblema no mesmo eixo do emblema monumental (repetição, ver 16.02).
- **Onde:** `F/PlayerHeight_Entry.jpg` (topo), `A/entry/CAM_SGEnt_PlayerBridge.jpg`.
- **Código:** `sg_entry.py: lintel_b()`.
- **Direção:** verga com perfil (cimalha + cavete + filete) e campo rebaixado. Trocar a placa por um fecho esculpido
  sem emblema.

### 01.09 Aduelas do arco da ponte de entrada · Tier C/B
- **Errado:** cada segmento é uma viga de 19,6 de largura. De lado, o intradorso lê em facetas escalonadas.
- **Onde:** `A/entry/CAM_SGEnt_SideE_Low.jpg`, `A/entry/CAM_SGEnt_SideW.jpg`.
- **Código:** `sg_entry.py: bridge()` (loop de `mb.beam(..., 19.6, band, ...)`).
- **Direção:** aduelas radiais individuais nas 2 faces (como `sg_dungeon.cave_mouth`) e o miolo do arco liso recuado.

### 01.10 [CRÍTICO] Piso da praça · Tier B
- **Errado:** disco de 64 lados liso com 8 setores escuros e "raios" em caixa de 0,55. No jogo é um plano liso lilás
  com fitas: nenhuma laje, nenhuma junta, nenhum bevel. É o maior plano que o jogador pisa na ilha (material, detalhe,
  close-up).
- **Onde:** `J/AU_PlazaFloor.jpg`, `J/AU_Lantern.jpg`, `F/PlayerHeight_Plaza.jpg`.
- **Código:** `sg_village.py: plaza()`.
- **Direção:**
  - Lajes em anéis concêntricos: peças de ~3 × 2 com junta de 0,1 rebaixada e bevel de 0,04.
  - 2 tons alternados por anel (variação dirigida, não sorteada).
  - Rosácea feita de peças, não de fita.
  - Borda de cantaria em segmentos de 3.

### 01.11 [CRÍTICO] "Fio da ordem" atravessando a praça · Tier B
- **Errado:** barra de obsidiana de 1,1 com risca violeta de 0,28. No jogo lê como trilho de trem preto (2 linhas
  escuras paralelas) cortando o piso (material, leitura).
- **Onde:** `J/AU_PlazaFloor.jpg` (canto inferior esquerdo), `F/PlayerHeight_Plaza.jpg` (base).
- **Código:** `sg_village.py: plaza()` (bloco "o FIO da ordem").
- **Direção:** tirar da praça, porque a fonte e a escada já dão o eixo. Se ficar, que seja uma fiada de lajes de
  mármore com juntas, sem contorno preto.

### 01.12 [CRÍTICO] Fonte da praça · Tier A (marco)
- **Errado:**
  - A bacia é um 12-gono com 12 pilastras-caixa de 0,75 e painéis escuros lisos.
  - Fuste e taças são cilindros n=8/12 com `r2` empilhados. A silhueta é uma pilha de primitivas, sem perfil de
    torno contínuo.
  - A água é um disco azul saturado liso.
  - Os 4 cubos-lanterna na borda competem com a estátua (silhueta, estrutura, material).
- **Onde:** `J/AU_Fountain.jpg`, `J/AU_PlazaFloor.jpg`, `A/village/CAM_SGVil_Fountain.jpg`.
- **Código:** `sg_village.py: plaza()` (bloco `mf`).
- **Direção:**
  - Um perfil de torno único (lathe, 16 lados, normais suaves) para pé, fuste, taça baixa, colar e taça alta, com
    bojo, lábio enrolado e bica.
  - Pilastras da bacia com base e capitel e painéis com moldura rebaixada.
  - Água em 2 níveis com anel de transbordo e cor menos saturada (ver 14.05).
  - Tirar as 4 lanternas (01.13).

### 01.13 Lanternas da borda da bacia · Tier B
- **Errado:** 4 `lantern_pedestal` s=0,6: cubos amarelos sobre caixas no parapeito da bacia. Ruído em volta do marco.
- **Onde:** `J/AU_Fountain.jpg`, `J/AU_PlazaFloor.jpg`.
- **Código:** `sg_village.py: plaza()` (loop `EM.lantern_pedestal` a 45/135/225/315).
- **Direção:** remover. Se quiser vida, 4 carrancas ou bicas d'água na parede da bacia.

### 01.14 [CRÍTICO] Estátua da fonte · Tier A
- **Errado:** é a mesma `hooded_figure` das guardas: cone, vigas e caixas (ver 03.01). No close da praça lê como
  chapéu de bruxa com saco.
- **Onde:** `A/village/CAM_SGVil_CU_Statue.jpg`, `J/AU_Fountain.jpg`.
- **Código:** `sg_village.py: fountain_statue()` → `sg_court.hooded_figure()`.
- **Direção:** corrigida junto com 03.01, porque é a mesma função.

### 01.15 [CRÍTICO] Bancos da praça · Tier B
- **Errado:** laje de 5 × 1,7 × 0,42 sobre 2 blocos de 0,9 × 1,3 mais uma travessa-caixa. É um bloco de blockout em
  primeiro plano (silhueta, bevel).
- **Onde:** `J/AU_Lantern.jpg` (primeiro plano), `J/AU_PlazaFloor.jpg`.
- **Código:** `sg_props.py: bench()`.
- **Direção:**
  - Assento com borda boleada (chanfro de 0,1 em cima, pingadeira embaixo).
  - Pés em console/voluta (perfil 2D extrudado de 8 pontos).
  - Assento levemente abaulado ou com junta no meio.
  - Opcional: encosto baixo com espaldar recortado.

### 01.16 [CRÍTICO] Postes da praça · Tier B
- **Errado:** o `lantern_post` é 3 caixas empilhadas com um cubo amarelo (ver 12.02 e 12.01).
- **Onde:** `J/AU_Lantern.jpg`, `F/PlayerHeight_Plaza.jpg`.
- **Código:** `sg_props.py: lamp()` → `sg_emblem.lantern_post`.
- **Direção:** vem de 12.01 e 12.02.

### 01.17 Eixo nobre na calçada alta e na praça · Tier B
- **Errado:** lajes de mármore em caixas uniformes (fiada de 3), borda de obsidiana, filete claro e fio no centro. São
  3 fitas paralelas, sem bevel e todas do mesmo comprimento.
- **Onde:** `A/entry/CAM_SGEnt_Back.jpg`, `A/CAM_SGCourt_PH_EntryHigh.jpg`.
- **Código:** `sg_court.py: noble_path()`.
- **Direção:** 2 comprimentos de laje alternados (2,4 / 3,6), bevel de 0,04 e junta de prata só a cada 8 fiadas.
  Remover o filete claro onde o piso em volta já contrasta.

### 01.18 Anéis de cantaria da praça · Tier B
- **Errado:** anéis de `Stone_SG_Trim` (valor 164): no jogo são faixas brancas de plástico em volta da fonte e na
  borda da praça.
- **Onde:** `J/AU_Lantern.jpg`, `J/AU_PlazaFloor.jpg`.
- **Código:** `sg_village.py: plaza()` (`ring_prism` com TRIM).
- **Direção:** segmentar em peças e baixar um valor (ver 14.01).

---

## 02 Vila

### 02.01 [CRÍTICO] Soco das casas · Tier B
- **Errado:** uma caixa de obsidiana de (W+0,7) × (D+0,7) × 1,4. A casa parece pousada numa bandeja preta lisa (ver a
  quina da loja e do torreão).
- **Onde:** `F/CU_VillageHouse.jpg`, `A/village/CAM_SGVil_Shop.jpg`.
- **Código:** `sg_village.py: house()` (primeiro `mb.box(... OBS ...)`).
- **Direção:** soco em 2 fiadas de pedra (Stone_SG_Block) com ressalto e pingadeira. Obsidiana só num filete fino de
  remate.

### 02.02 Térreo de pedra das casas · Tier B
- **Errado:** o corpo é uma caixa lisa, com os cunhais em caixas alternadas coladas nas quinas. Entre os cunhais a
  parede é lisa (material, detalhe).
- **Onde:** `A/village/CAM_SGVil_Shop.jpg`.
- **Código:** `sg_village.py: house()` (corpo `mat = STONE_H` e loop dos cunhais).
- **Direção:** fiadas em relevo raso (0,06) em 2 alturas alternadas, ou 3 a 4 blocos grandes por face. Cunhais com
  bevel de 0,06 e profundidade variando entre 0,15 e 0,25.

### 02.03 [CRÍTICO] Vidro das janelas das casas · Tier B
- **Errado:** o vidro é uma caixa de 0,3 inteira em `Window_Warm` (Neon). É um painel amarelo chapado, sem interior,
  cortina ou divisão de vidros. No close lê "tela acesa", e com 11 casas vira cartela de LED (material, emissive).
- **Onde:** `A/village/CAM_SGVil_CU_Window.jpg`, `F/CU_VillageHouse.jpg`, `A/village/CAM_SGVil_Shop.jpg`.
- **Código:** `sg_village.py: window()` (`f.box(... WIN)`).
- **Direção:**
  - Vidro recuado 0,15 em material âmbar médio não-emissivo.
  - Uma segunda peça emissiva menor atrás (ou só no terço inferior) para simular o cômodo iluminado.
  - Bandô ou cortina (caixa fina Cloth) em ~40% das janelas, escolhidas por fachada.
  - Pinázios de 0,06 formando grade 2 × 3 nas janelas "cross".

### 02.04 [CRÍTICO] Flores das floreiras (janela e chão) · Tier B
- **Errado:**
  - As flores são icosferas achatadas roxas e facetadas: gemas, não flores.
  - A folhagem é uma caixa verde de 0,3.
  - A floreira de chão é uma caixa de obsidiana com as mesmas gemas, na soleira de todas as casas (filler).
- **Onde:** `A/village/CAM_SGVil_CU_Window.jpg`, `A/village/CAM_SGVil_Shop.jpg`, `F/CU_VillageHouse.jpg`.
- **Código:** `sg_village.py: window()` (bloco `planter`) e `house_identity()` (floreiras de obsidiana).
- **Direção:**
  - Folhagem em 3 a 4 lobos baixos pendentes que transbordam a borda da caixa.
  - Flores em cachos de 3 discos pequenos com miolo claro.
  - Floreira com rebordo e pés.
  - Remover as floreiras de chão de metade das casas (as de fundo).

### 02.05 Fachada de loja · Tier B
- **Errado:**
  - A persiana é uma caixa navy com 4 ripas coladas por fora.
  - O toldo é uma caixa inclinada de 0,28 sem testeira nem recorte.
  - O balcão e a almofada são caixas de Trim branco.
- **Onde:** `A/village/CAM_SGVil_Shop.jpg`.
- **Código:** `sg_village.py: shopfront()`.
- **Direção:** persiana com ripas reais (sequência de caixas com 0,05 de folga e sombra entre elas), toldo com
  testeira recortada em ondas e mãos-francesas curvas, balcão com consolas.

### 02.06 [CRÍTICO] Lanterna de parede atravessando o montante do enxaimel · Tier B
- **Errado:** `_lantern_slots` põe a lanterna no meio do vão entre janelas. `timber_face` põe um montante justamente no
  meio de todo vão maior que 3,4. Resultado: o espelho de ferro e a haste ficam em cima da tábua (peça atravessando
  peça).
- **Onde:** `A/village/CAM_SGVil_CU_Gable.jpg` (lanterna central no montante).
- **Código:** `sg_village.py: wall_lantern()` + `_lantern_slots()` + `timber_face()` (`full.append(mid)`).
- **Direção:** deslocar o slot para o centro de um painel de reboco (entre montantes), ou não criar o montante do meio
  no vão que recebe lanterna.

### 02.07 Fiadas de ardósia dos telhados · Tier B
- **Errado:** as fiadas são caixas longas e contínuas, sem recorte de telha. O telhado lê como degraus lisos. A
  cumeeira comum é um cilindro n=8.
- **Onde:** `A/village/CAM_SGVil_CU_Roof.jpg`, `A/village/CAM_SGVil_CU_Gable.jpg`.
- **Código:** `sg_village.py: house()` (bloco "telhado ingreme").
- **Direção:**
  - Borda inferior de cada fiada com dentes (escama) a cada 1,2, feitos por vértices sem polígono extra por telha.
  - 2 alturas de fiada.
  - Cumeeira em peças com junta.

### 02.08 Encaixe das águas-furtadas · Tier B
- **Errado:** o corpo da água-furtada é uma caixa de reboco que atravessa a água principal sem rufo nem calha. Parece
  uma casinha enfiada (encaixe).
- **Onde:** `A/village/CAM_SGVil_CU_Roof.jpg`.
- **Código:** `sg_village.py: house()` (bloco `dormers`).
- **Direção:** rufo de ardósia (faixa de 0,3) na linha de encontro, bochechas triangulares com espessura e testeira na
  frente da cobertura.

### 02.09 Chaminés · Tier B
- **Errado:** fuste-caixa liso com cinta, capa e pote cilíndrico n=8. Sai do telhado sem rufo.
- **Onde:** `A/village/CAM_SGVil_CU_Roof.jpg`, `A/village/CAM_SGVil_Shop.jpg`.
- **Código:** `sg_village.py: house()` (bloco `chims`).
- **Direção:** fiadas em 2 alturas, capa com ressalto duplo, rufo na base e pote cerâmico com lábio (lathe de 5
  pontos).

### 02.10 [CRÍTICO] Torreão da casa · Tier B
- **Errado:**
  - O fuste é um prisma octogonal liso de ~12, sem cordão nem mísula.
  - As frestas levam molduras de caixa em Trim branco que saltam como adesivos claros.
  - A agulha é n=8 lisa.
- **Onde:** `F/CU_VillageHouse.jpg`, `A/village/CAM_SGVil_Turret.jpg`, `A/CAM_SG_CU_VillageHouse.jpg`.
- **Código:** `sg_village.py: house()` (bloco `turret`).
- **Direção:**
  - Cordão a cada andar.
  - Fiada de mísulas sob o beiral do cone.
  - Base em escarpa.
  - Molduras das frestas em pedra média (Stone_SG_Block), não Trim.
  - Agulha com escamas (dentes na borda) e lucarna pequena.

### 02.11 [CRÍTICO] Ruas secundárias (P1/P2) · Tier B
- **Errado:**
  - O calçamento é uma faixa lisa (prisma) com outra faixa lisa no centro.
  - O meio-fio são caixas de ~6 studs sem bevel.
  - No jogo lê asfalto: nenhuma pedra, junta ou desgaste na borda com a grama.
- **Onde:** `A/village/CAM_SGVil_PH_P2Craft.jpg`, `A/village/CAM_SGVil_PH_P1E.jpg`, `A/_folha_village.jpg`.
- **Código:** `sg_village.py: streets()`.
- **Direção:**
  - Fiadas transversais de paralelepípedo a cada 1,0, com relevo de 0,04 e junta escura (o prisma segue igual por
    baixo).
  - Meio-fio em peças de 2 com chanfro.
  - Na borda com a grama, uma faixa irregular de pedras soltas e tufos.

### 02.12 Transição do gramado P2 com a rua · Tier B/C
- **Errado:** o gramado é um plano liso com textura, cortado em linha reta pela rua. Não há terra nem transição.
- **Onde:** `A/village/CAM_SGVil_PH_P2Craft.jpg`, `A/_folha_village.jpg` (P2E_Back).
- **Código:** `sg_terrain.py: terraces()` (topo de grama do P2) e `sg_village.py: streets()`.
- **Direção:** faixa de terra batida de 0,6 junto ao meio-fio e pequenos grupos de tufos baixos em pontos escolhidos
  (esquinas, pé das casas).

### 02.13 [CRÍTICO] Escada P1 → P2 · Tier B
- **Errado:**
  - Degraus-caixa lisos.
  - Os banzos (stringers) do `fm_parts.stairs` fazem dentes de serra de caixas nas laterais.
  - As muretas de `vis_parapet` são caixas.
  - É o blockout do plano, intacto.
- **Onde:** `A/terrain/CAM_SGTer_PlayerHeight_P1Wall.jpg`, `A/village/CAM_SGVil_PH_Stair.jpg`, `J/AU_Fountain.jpg`
  (fundo).
- **Código:** `sg_village.py: streets()` (`SL.plan_stair(ms, "P1P2")`, `SL.vis_parapet`) → `fm_parts.stairs`.
- **Direção:** mesma receita de 01.01 e 01.02. Banzo contínuo inclinado com capa, no lugar dos dentes. É a escada de
  maior tráfego depois da entrada.

### 02.14 Arco de ferro do topo da escada P1P2 · Tier B
- **Errado:**
  - Postes são caixas de 0,56 com anéis-caixa e soco-caixa.
  - Os braços são vigas quadradas.
  - As lanternas são cubos de vidro de 0,62 com montantes.
  - Os trilhos curvos estão bons, mas os postes e as lanternas são primitivas.
- **Onde:** `A/village/CAM_SGVil_CU_Statue.jpg`, `A/CAM_SGCourt_PH_PlazaN.jpg`.
- **Código:** `sg_court.py: iron_arch()` (chamado por `sg_village.lamps()` e `sg_court.court()`).
- **Direção:** poste de ferro fundido (ver 12.02), volutas de ferro na nascença do arco, lanterna nova pendurada.
  Corrigir a função corrige os 2 arcos.

---

## 03 Castelo exterior

### 03.01 [CRÍTICO] Guardas/estátuas do pátio · Tier A
- **Errado:**
  - O corpo é um cilindro n=16 afunilado com 5 vigas retas coladas por fora como "pregas" (listras, não dobras).
  - A capa é outro cilindro.
  - O capuz é um cone n=12 com ponta aguda, chapéu de bruxa.
  - As mangas são vigas retangulares e as mãos são caixas.
  - No jogo é um boneco inflável ou saco com cone: sem ombros, cintura, cabeça sob o capuz nem peso (silhueta,
    proporção, estrutura, close-up).
- **Onde:** `J/AU_GuardSide.jpg`, `J/AU_GuardFront.jpg`, `F/CU_CastleWindow.jpg`, `F/CU_CastleDoor.jpg`,
  `A/CAM_SG_AU_GuardSide.jpg`, `A/CAM_SG_AU_GuardFront.jpg`.
- **Código:** `sg_court.py: hooded_figure()`, `statue()`.
- **Direção:**
  - Figura em UM volume por loft de 9 a 10 seções horizontais, com perfil que muda por altura:
    - barra larga e ondulada, com 6 a 7 pregas entrando no perfil da seção (a seção é uma estrela suave, não um
      círculo);
    - cintura;
    - ombros largos e quadrados;
    - pescoço;
    - capuz com volume de crânio (ponta caída para trás, não cone vertical);
    - borda do capuz grossa e dobrada, abertura funda e escura.
  - Braços saindo de dentro do manto, antebraços para a frente e mãos cruzadas sobre o pomo.
  - Proporção heroica: cabeça 1/7 da altura.
  - Normais suaves com arestas marcadas só nas dobras.
  - Mesmo polycount de hoje (~600 tris) bem distribuído.

### 03.02 [CRÍTICO] Espadas das estátuas · Tier A
- **Errado:**
  - A lâmina é um frustum com uma "aresta" em caixa.
  - A guarda é uma caixa de 1,0 × 0,24 × 0,2 com 2 caixas nas pontas.
  - O cabo é um cilindro n=8 e o pomo uma icosfera.
  - No Roblox os cantos arredondados leem balão/salsicha. É a mesma pedra do corpo, sem leitura de metal nem de
    arma (silhueta, espessura, material).
- **Onde:** `F/CU_CastleWindow.jpg`, `A/CAM_SG_CU_CastleWindow.jpg`, `J/AU_GuardSide.jpg`.
- **Código:** `sg_court.py: hooded_figure()` (bloco "espada ESCULPIDA").
- **Direção:**
  - Lâmina com a seção em losango do emblema (`sg_emblem._bar`): fio, sulco central e ponta afiada entrando no plinto.
  - Guarda em perfil 2D extrudado com quillons curvados para baixo e ponta em gota.
  - Cabo com 3 anéis de enrolamento.
  - Pomo facetado com colar.
  - Lâmina em pedra um valor mais escura que o manto (lê objeto na mão).

### 03.03 Pedestais das estátuas · Tier A
- **Errado:** dado violeta liso de 2,7 com a placa colada. As molduras são caixa mais frustum (aceitável), mas o dado
  é um bloco.
- **Onde:** `F/CU_CastleDoor.jpg`, `A/CAM_SGCourt_PH_Gate.jpg`.
- **Código:** `sg_court.py: statue()`.
- **Direção:** painel rebaixado (0,1) com moldura em cada face e a placa encaixada no painel. Cornija com cavete em
  vez de talude reto.

### 03.04 [CRÍTICO] Poste na frente da estátua · Tier B
- **Errado:** o poste norte (-8,4; 28,5) está a ~6 studs da estátua (-12,5; 33,5), justo na linha de visão de quem
  sobe para a porta. O poste corta a figura ao meio (composição, encaixe).
- **Onde:** `J/AU_GuardFront.jpg`, `F/PlayerHeight_Castle.jpg`, `A/CAM_SGCourt_PH_Gate.jpg`.
- **Código:** `sg_court.py` (`LAMPS`, `STATUES`) → `lamp()`.
- **Direção:** tirar o par norte (a luz violeta central já existe) ou movê-lo para fora do cone (x ±9,5; y ~23).

### 03.05 [CRÍTICO] Obeliscos do pátio · Tier A
- **Errado:**
  - O fuste é um cilindro de 4 lados com "filetes" rod n=4.
  - As runas são barras SG_VioletSoft_Glow que leem como letreiro ("Y L Y L", letras latinas em neon).
  - Placa colada na base e piramídion de prata n=4.
  - É mais um totem de primitivas com glow (detalhe colado, emissive).
- **Onde:** `F/CU_CastleWindow.jpg`, `A/CAM_SG_CU_CastleWindow.jpg`, `F/PlayerHeight_Castle.jpg`.
- **Código:** `sg_court.py: obelisk()`.
- **Direção:**
  - Runas ENTALHADAS: rebaixo de 0,08 com fundo violeta escuro não emissivo (ou emissão 0,3), glifos de 3 a 4 traços
    com curva, sem forma de letra latina.
  - Fuste com leve êntase.
  - Base em 3 molduras com perfil (toro + escócia).
  - Tirar a placa (ver 16.02).

### 03.06 Canteiros: sebes, flores e cipreste · Tier B
- **Errado:**
  - As sebes são vigas retas de seção quadrada.
  - As flores são icosferas achatadas (gemas).
  - Os pilaretes de canto são caixa mais pirâmide n=4.
  - O cipreste de 11,5 em primeiro plano é um cone escuro facetado que tapa a fachada.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_Forecourt.jpg` (cone escuro à direita), `A/CAM_SGCourt_PH_Cross.jpg`.
- **Código:** `sg_court.py: parterre()`, `hedge()` e `sg_veg.cypress()`.
- **Direção:**
  - Sebe com topo chanfrado ou boleado e bolas de topiária nos cantos em vez de pirâmides.
  - Flores em tufos (02.04).
  - Cipreste mais baixo (7 a 8) e mais lobado, ou trocado por topiária em espiral.

### 03.07 Muretas de transição do pátio · Tier B
- **Errado:** corpo-caixa, remate-caixa, pilares-caixa e pirâmide n=4. Primitivas empilhadas.
- **Código:** `sg_court.py: muret()`.
- **Onde:** `A/CAM_SGCourt_PH_Cross.jpg`.
- **Direção:** cantaria com capa moldurada e o remate do kit comum (12.12).

### 03.08 [CRÍTICO] Paredes da nave e das alas na altura do jogador · Tier A
- **Errado:**
  - No beco oeste, na fachada lateral e nas alas, são planos contínuos de 40 a 90 studs sem fiada, pilastra, cordão
    ou soco que o jogador leia.
  - No Blender o ruído da textura disfarça. No Roblox é plástico liso.
  - O castelo (hero) está menos acabado de perto que as casas (Tier B) (estrutura, material, close-up).
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_WestAlley.jpg`, `F/CU_CastleWindow.jpg`, `F/PlayerHeight_Castle.jpg`
  (flancos), `A/castle/CAM_SGCas_PlayerHeight_DungeonYard.jpg`.
- **Código:** `sg_castle.py: nave()` (`wall_run`, `SIDE_BANDS`), `wings()`.
- **Direção:**
  - Nos primeiros 8 studs (zona do olho): fiadas de cantaria em relevo raso (0,08), 2 alturas alternadas.
  - Soco com fiada de base e talude.
  - Cordão a +8.
  - Pilastras planas (saliência 0,4) no eixo de cada contraforte, até a cornija.
  - Acima de 20 studs pode continuar liso (Tier C de perto).

### 03.09 [CRÍTICO] Contrafortes e arcobotantes · Tier A
- **Errado:**
  - Os contrafortes são caixas empilhadas com uma "pingadeira" em caixa rodada.
  - Os arcobotantes são vigas retas de seção quadrada (1,1 × 1,3 e 0,9 × 0,9), em vez de arco.
  - No beco oeste são 5 blocos idênticos em linha.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_WestAlley.jpg`, `A/castle/CAM_SGCas_West.jpg`,
  `A/castle/CAM_SGCas_BackNE.jpg`.
- **Código:** `sg_castle.py: nave()` (loop `BUTT_Y`).
- **Direção:**
  - Cada ressalto com talude real (face inclinada de 45°) e pingadeira em perfil.
  - Arcobotante como perfil 2D extrudado: quarto de arco por baixo, extradorso reto por cima, espessura de 1,0 e
    chanfro.
  - Pináculo do kit comum no topo.

### 03.10 Pináculos (caixa + pirâmide n=4), cerca de 40 iguais · Tier A/C
- **Errado:** todos os pináculos da nave, fachada, pórtico, altar e pilaretes são caixa com `SL.spire(n=4)` e ponta
  de prata. Silhueta de "lápis". É a assinatura mais repetida do castelo (repetição, primitiva).
- **Onde:** `A/castle/CAM_SG_Castle.jpg`, `A/castle/CAM_SGCas_BackNE.jpg`, `A/castle/CAM_SGCas_PlayerHeight_Forecourt.jpg`.
- **Código:** `sg_castle.py: nave()`, `facade()`, `crown()` e `sg_lib.spire`.
- **Direção:**
  - Um kit de pináculo em 2 tamanhos: base quadrada com gablete nas 4 faces, agulha OCTOGONAL com 1 anel, 4 crochês
    (pequenas lascas) nas arestas e florão.
  - Substituir nas ~40 posições.
  - Custo baixo: é uma função.

### 03.11 [CRÍTICO] Muralha · Tier A
- **Errado:**
  - Caixa contínua com mísulas-caixa idênticas a cada 3,2 e ameias-caixa em uma de cada duas.
  - Lanterna-pedestal a cada ~12 no parapeito.
  - Face lisa entre talude e cornija.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_EastGap.jpg`, `A/castle/CAM_SGCas_PlayerHeight_Gate.jpg`,
  `J/AU_Stair.jpg` (fundo).
- **Código:** `sg_castle.py: muralha()`.
- **Direção:**
  - Paramento em fiadas no terço de baixo.
  - Mata-cães com arquinhos entre as mísulas.
  - Merlões em 2 larguras, com seteira e capa chanfrada.
  - Cortar as lanternas da muralha pela metade (12.04).

### 03.12 Verga do portão e grade levadiça · Tier A
- **Errado:** a verga é uma placa de obsidiana lisa com a "chave" trapezoidal violeta. A grade são 9 caixas de 0,36
  soltas embaixo da verga: dentes flutuando, sem malha nem trilho.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_Gate.jpg`, `A/CAM_SGCourt_PH_P2Axis.jpg`.
- **Código:** `sg_castle.py: muralha()` (bloco "torre-portaria" e "grade levadica").
- **Direção:** grade com malha (3 barras horizontais ligando os dentes) recolhida num sulco. Verga com arco abatido de
  aduelas e fecho.

### 03.13 Torres (portão, muralha, cortina, passagem leste) · Tier A/C
- **Errado:**
  - Os fustes são octógonos lisos com soco, faixa e parapeito.
  - As agulhas são n=8 lisas com um anel de prata.
  - De perto (pátio e passagem leste) não há fiada, cordão nem lucarna.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_EastGap.jpg`, `A/castle/CAM_SGCas_PlayerHeight_Gate.jpg`.
- **Código:** `sg_castle.py: shaft()`, `spire()`, `small_tower()`, `parapet_ring()`.
- **Direção:** fiadas no fuste até +10, cordão por andar, agulhas com escamas (recorte na borda de cada anel) e
  lucarna pequena nas torres do portão.

### 03.14 [CRÍTICO] Linhas de neon nas arestas da torre-coroa · Tier A
- **Errado:** `glow_edges` põe caixas finas SG_VioletSoft_Glow ao longo das quinas do fuste. É energia colada na
  arquitetura: placeholder com glow (emissive).
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_Terrace.jpg`, `A/castle/CAM_SGCas_BackNE.jpg`.
- **Código:** `sg_castle.py: glow_edges()` (chamado em `crown()`).
- **Direção:** remover. A magia da coroa fica só nas lancetas altas com vitral.

### 03.15 Pórtico da porta do castelo · Tier A
- **Errado:**
  - Colunelos são cilindros n=8 lisos, bases e capitéis são caixas.
  - As arquivoltas são painéis extrudados retos sem perfil de moldura.
  - Tímpano plano com placa.
  - De perto (4 m) lê como recortes de papelão escalonados.
- **Onde:** `F/PlayerHeight_Castle.jpg`, `A/castle/CAM_SGCas_PlayerHeight_Forecourt.jpg`, `A/CAM_SG_CU_CastleDoor.jpg`.
- **Código:** `sg_castle.py: facade()` (bloco "porche em degraus").
- **Direção:**
  - Colunelos com base ática e capitel em cesto (lathe de 6 pontos, n=12).
  - Arquivoltas com perfil (toro + cavete) por sweep ao longo da ogiva.
  - Tímpano rebaixado com moldura.

### 03.16 Telhados: crista, lucarnas, fiadas · Tier C/B
- **Errado:**
  - A crista da cumeeira é uma fileira de hastes com caixas rodadas a cada 4 (cruzinhas iguais).
  - As lucarnas são caixa mais telhadinho.
  - As fiadas são caixas contínuas.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_DungeonYard.jpg`, `A/castle/CAM_SGCas_BackNE.jpg`.
- **Código:** `sg_castle.py: nave_roof()`, `roofs()`.
- **Direção:** crista de ferro contínua (fita recortada com florões a cada 8). Lucarnas com bochechas, moldura e
  testeira.

### 03.17 Escadas Gate e EastP3 · Tier B
- **Errado:** `plan_stair` com stringers de caixas em dentes de serra nas laterais. Degraus lisos.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_EastGap.jpg`, `A/castle/CAM_SGCas_PlayerHeight_Gate.jpg`.
- **Código:** `sg_castle.py: stairs()` → `sg_lib.plan_stair` → `fm_parts.stairs`.
- **Direção:** receita de 01.01. Banzos contínuos com capa.

### 03.18 Encontro da faixa de obsidiana com a torrinha da fachada · Tier A
- **Errado:** a faixa de andar da fachada e a faixa da torrinha octogonal se encontram em quina viva, sem cunhal nem
  peça de transição. A faixa dobra em volta do fuste colada à moldura da janela vizinha (encaixe).
- **Onde:** `F/CU_CastleWindow.jpg`, `A/CAM_SG_CU_CastleWindow.jpg`.
- **Código:** `sg_castle.py: facade()` (`FAC_TURRETS`, `band(...)`) e `nave()` (faixas `WIN_SILL - 1.6`).
- **Direção:** a faixa da fachada morre num cunhal de cantaria antes da torrinha. A faixa da torrinha termina na
  mesma cota, com pingadeira.

---

## 04 Castelo interior (porta, casca da nave, foco do trono)

### 04.01 [CRÍTICO] Passagem da porta do castelo · Tier A
- **Errado:**
  - As ombreiras do vão de 16 × 18 são paredes lisas de 4 de espessura com um rodapé-caixa.
  - O intradorso é uma verga-caixa de obsidiana.
  - Não há porta, ferragem nem caixotão.
  - No jogo é um recorte com faixas roxas verticais, e a porta mais importante da ilha não tem folha (brief: "portas
    importantes: moldura + espessura + soleira + ligação + ferragem").
- **Onde:** `F/CU_CastleDoor.jpg`, `F/PlayerHeight_Castle.jpg`, `A/CAM_SG_CU_CastleDoor.jpg`.
- **Código:** `sg_castle.py: facade()` (bloco "PORTA (acabamento)").
- **Direção:**
  - 2 folhas de madeira abertas contra o intradorso: tábuas verticais, 3 ferragens em T, cravos, puxador em argola.
  - Ombreira com colunelo e dobradiças visíveis.
  - Intradorso com 3 caixotões rasos.
  - Soleira em 2 peças (já existe o focinho de prata; dividir em pedras).

### 04.02 [CRÍTICO] Trono de Shadow · Tier A
- **Errado:**
  - O assento é uma caixa de obsidiana.
  - Os braços são caixas com icosfera de prata na ponta.
  - O espaldar é um slab pentagonal com moldura em fita.
  - Os montantes são caixas com agulha n=4.
  - É o ponto focal do salão, e é blockout com glow atrás.
- **Onde:** `A/hall/CAM_SGHall_Throne.jpg`, `F/CU_CastleDoor.jpg` (fundo).
- **Código:** `sg_hall.py: throne()`.
- **Direção:**
  - Braços com voluta e garra na ponta (perfil 2D extrudado).
  - Pés em pata.
  - Espaldar com moldura escalonada em 2 camadas e crista em ogiva vazada (recorte).
  - Almofada com volume (lathe achatado ou caixa com bevel de 0,15).
  - Estrado com espelho moldurado.

### 04.03 Retábulo/altar: pilares e pináculos · Tier A
- **Errado:** pilares compostos em caixa com cilindros n=6/8 lisos. Pináculo em caixa mais `spire n=4` e bola de
  prata. Capitéis em caixa.
- **Onde:** `A/hall/CAM_SGHall_Throne.jpg`, `A/hall/CAM_SGHall_PlayerMid.jpg`.
- **Código:** `sg_hall.py: altar()`.
- **Direção:** capitel em cesto com ábaco chanfrado, colunelos com base, pináculo do kit comum (03.10).

### 04.04 [CRÍTICO] Nervuras e chaves da abóbada · Tier A
- **Errado:**
  - As nervuras são sweep de seção RETANGULAR (0,5 × 1,0 / 0,26 × 0,6).
  - As chaves são cilindros empilhados com o emblema virado para baixo.
  - Os panos têm textura de ruído.
  - No jogo são vigas-caixa cruzando o teto e um colar de discos pendurado no eixo.
- **Onde:** `F/CU_CastleDoor.jpg`, `F/PlayerHeight_MiningHall.jpg`, `A/hall/CAM_SGHall_Ceiling.jpg`.
- **Código:** `sg_hall.py: vault()`.
- **Direção:**
  - Perfil de nervura em pera/toro (6 a 8 pontos) no mesmo sweep.
  - Chaves com florão (rosa de 8 pétalas, lathe achatado) em vez de discos empilhados.
  - Emblema só na chave central.
  - Panos com linhas de fiada (sweep fino) em vez de ruído.

### 04.05 Lustres do salão · Tier A
- **Errado:**
  - Anel em tubo de 4 lados, braços em viga quadrada.
  - Velas em cilindro Lantern_Glow n=6 (bastão amarelo inteiro).
  - Pingente em cilindro invertido.
- **Onde:** `F/PlayerHeight_MiningHall.jpg`, `A/hall/CAM_SGHall_West.jpg`.
- **Código:** `sg_hall.py: chandelier()`.
- **Direção:** anel e braços em tubo n=8 com curva em S. Vela com prato, corpo creme não-emissivo e chama em gota
  Neon pequena (kit de vela, ver 12.09).

### 04.06 Estandartes do salão (4 nas pilastras + 2 no altar) · Tier B
- **Errado:** o mesmo pano rígido de fora (12.05). Somados ao emblema do trono, ao medalhão do piso, às chaves e aos
  vitrais com medalhão, o salão tem mais de 12 emblemas no mesmo quadro.
- **Onde:** `A/hall/CAM_SGHall_West.jpg`, `A/hall/CAM_SGHall_Throne.jpg`.
- **Código:** `sg_hall.py: banners()`, `altar()`.
- **Direção:** manter só os 2 do altar. Tirar os 4 das pilastras (ver 16.02).

---

## 05 Mining Hall: bordas do salão (sem minério)

### 05.01 [CRÍTICO] Nichos da arcada cega · Tier B
- **Errado:**
  - Mais de 16 nichos idênticos em linha, com o mesmo fundo violeta de textura de mármore em nuvem.
  - Uma candeia centrada em cada um.
  - O mesmo arco, o mesmo fecho.
  - Repetição mecânica sem hierarquia (repetição, procedural sem direção).
- **Onde:** `A/hall/CAM_SGHall_West.jpg`, `A/hall/CAM_SGHall_East.jpg`, `F/PlayerHeight_MiningHall.jpg`.
- **Código:** `sg_hall.py: niche()`, `walls()`, `ironwork()` (candeias).
- **Direção:**
  - Alternância dirigida de 2 nichos: A com mísula e candeia; B com prateleira de pedra e vaso de ferro.
  - Fundo em pedra lisa escura, sem ruído.
  - O nicho do eixo de cada vitral recebe moldura dupla.

### 05.02 Candeias dos nichos · Tier B
- **Errado:** caixa de ferro, cilindro de ferro e cilindro Lantern_Glow n=6. Vela-bastão amarela.
- **Onde:** `A/hall/CAM_SGHall_West.jpg`, `F/PlayerHeight_MiningHall.jpg`.
- **Código:** `sg_hall.py: ironwork()`.
- **Direção:** arandela com espelho de ferro recortado, braço curvo e o kit de vela (12.09).

### 05.03 Pilastras do salão · Tier B
- **Errado:** núcleo-caixa com 3 cilindros lisos (n=8/6), anel violeta-caixa e capitel-caixa. Sem base e sem capitel
  nos colunelos.
- **Onde:** `A/hall/CAM_SGHall_West.jpg`, `A/hall/CAM_SGHall_Diag.jpg`.
- **Código:** `sg_hall.py: walls()` (`pier`).
- **Direção:** colunelos com base (toro) e capitel (anel + ábaco). Capitel do núcleo com cavete.

### 05.04 Galeria alta · Tier B
- **Errado:**
  - Laje de obsidiana em caixa, sobre mísulas em caixa.
  - Balaústres em montantes-caixa de 0,2 e corrimão-caixa de prata.
  - Remates em pirâmide n=4.
- **Onde:** `A/hall/CAM_SGHall_West.jpg`, `F/PlayerHeight_MiningHall.jpg`.
- **Código:** `sg_hall.py: gallery()`.
- **Direção:** mísulas em perfil S (2D extrudado). Grade com barras redondas n=6 e roseta a cada 3. Corrimão com
  perfil boleado.

### 05.05 Paramento com textura de ruído · Tier B
- **Errado:** o fundo violeta dos nichos e o paramento usam textura de mármore em nuvem forte: procedural sem direção.
  No Roblox some, e o que resta é chapado.
- **Onde:** `A/hall/CAM_SGHall_West.jpg`, `A/hall/CAM_SGHall_Throne.jpg`.
- **Código:** `sg_hall.py` (`NI`, `CS`) + regras de textura do `fm_lib`.
- **Direção:** ver 14.02.

### 05.06 Piso do salão (bordas) · Tier B
- **Errado:** está correto de leitura (mármore, faixas de prata, borda de obsidiana). Único ponto: faixas retas de
  largura e espaçamento iguais em todo o perímetro.
- **Onde:** `A/hall/CAM_SGHall_Diag.jpg`.
- **Código:** `sg_hall.py: floor()`.
- **Direção:** manter. Opcional: tacos de prata só nos cruzamentos do eixo.

### 05.07 Círculos/pentagrama neon no piso (só no jogo) · fora do pipeline
- **Errado:** no jogo aparecem pentagramas e círculos magenta no piso da zona de minério. Não estão no Blender, então
  vêm do sistema de minério ou VFX. É um segundo sistema de símbolos, contra a regra do emblema único.
- **Onde:** `F/PlayerHeight_MiningHall.jpg`, `F/CU_CastleDoor.jpg`.
- **Código:** não gerado pelos `sg_*.py` (verificar o VFX de spawn de minério no Studio).
- **Direção:** decal de spawn com o crescente-lâmina ou um anel simples. Não se modela nada no salão.

---

## 06 Alquimia exterior

### 06.01 [CRÍTICO] Parede do pavilhão até 9,3 · Tier A
- **Errado:**
  - 24 faces planas lisas (`Stone_SGCraftDark`) só com o soco de obsidiana e o friso violeta.
  - As janelas começam em 9,3, então da altura do jogador o pavilhão é uma lata lisa.
  - No jogo cada face é um retângulo navy chapado.
- **Onde:** `J/AU_CraftBase.jpg`, `A/CAM_SG_AU_CraftBase.jpg`, `F/Craft.jpg`, `A/craft/CAM_SGCraft_S.jpg`.
- **Código:** `sg_craft.py: shell()`.
- **Direção:**
  - Embasamento em fiadas (2 alturas) até +4,5 com cordão.
  - Em cada face livre, arcada cega baixa (painel ogival rebaixado 0,2) ou respiro de porão com grade de ferro.
  - Quina de cada face com cunhal fino de 0,3 (quebra os 24 planos).
  - Mais barato que qualquer prop novo: são painéis por face.

### 06.02 [CRÍTICO] Empena do pórtico colada no domo · Tier A
- **Errado:**
  - A empena é um triângulo `pslab` de 1,4 de espessura, sem telhado de ligação atrás.
  - É um recorte de papelão encostado no domo.
  - A nervura de prata do domo a 180° nasce atrás dela (peça atravessando).
- **Onde:** `F/Craft.jpg`, `A/craft/CAM_SGCraft_W.jpg`, `A/craft/CAM_SG_Craft.jpg`, `J/AU_Flask.jpg` (lateral).
- **Código:** `sg_craft.py: portal()` (bloco "empena gotica", `GH`) e `dome()` (`RIB_A` contém 180).
- **Direção:**
  - O pórtico ganha telhado próprio de 2 águas (navy, com rincão) que morre no domo com rufo de prata.
  - A empena ganha moldura e cimalha em perfil.
  - Tirar 180 de `RIB_A`, ou terminar essa nervura na cumeeira do pórtico.

### 06.03 Maciço do pórtico · Tier A
- **Errado:** as ombreiras são blocos-caixa de parede (4,1 de largura) colados no cilindro. Pilastras de canto em
  caixa, soco em caixa. De 3/4 lê um caixote grudado na rotunda.
- **Onde:** `F/Craft.jpg`, `F/CU_CraftDoor.jpg`, `A/craft/CAM_SGCraft_PH_Door.jpg`.
- **Código:** `sg_craft.py: portal()`.
- **Direção:** pilastras com base e capitel no lugar das caixas de canto, flancos do pórtico chanfrados para casar com
  a curva, arquivolta externa em aduelas.

### 06.04 [CRÍTICO] Remates alquímicos dos contrafortes e do pórtico · Tier A
- **Errado:**
  - Esfera de vidro de 8 lados com cinta de latão no equador e agulha: balão com espeto.
  - No jogo o vidro PALE vira bola azul-marinho opaca e facetada, com uma cinta laranja grossa (a peça em primeiro
    plano de AU_Flask).
  - 9 unidades.
- **Onde:** `J/AU_Flask.jpg`, `A/CAM_SG_AU_Flask.jpg`, `A/craft/CAM_SGCraft_W.jpg`, `F/Craft.jpg`.
- **Código:** `sg_craft.py: finial()`.
- **Direção:**
  - Retorta estilizada por lathe n=12: pé de latão, bojo em pêra, gargalo que curva para o lado (peça separada em
    tubo) e 3 fitas de latão formando uma gaiola.
  - Bojo em material OPACO pintado (lilás-acinzentado claro com meia-lua de reflexo em Trim), sem depender de
    transparência.
  - Ou trocar por urna de pedra com tampa (mais simples e sólido).

### 06.05 Contrafortes do pavilhão · Tier B
- **Errado:** perfis `pside` lisos com topo inclinado e 2 pingadeiras-caixa. Sem fiada nem ressalto.
- **Onde:** `A/craft/CAM_SGCraft_S.jpg`, `A/craft/CAM_SGCraft_N.jpg`.
- **Código:** `sg_craft.py: shell()` (loop `BUTT_A`).
- **Direção:** 2 ressaltos com talude real e fiadas no primeiro lance.

### 06.06 Facetamento do domo e nervuras · Tier A
- **Errado:**
  - O domo tem 24 × 8 faces com sombreamento facetado visível (tabuleiro de luz).
  - As nervuras são sweep de seção retangular.
  - O lanternim é um octógono liso.
- **Onde:** `J/AU_Flask.jpg`, `F/Craft.jpg`, `A/craft/CAM_SGCraft_N.jpg`.
- **Código:** `sg_craft.py: dome()`, `dome_shell()`.
- **Direção:**
  - Normais suaves no domo (auto smooth ~40°).
  - Escamas de ardósia por anel, com recorte na borda inferior.
  - Nervuras com perfil redondo (6 pontos).
  - Lanternim com colunelos entre as fendas e cornija.

### 06.07 Emblema do frasco na empena · Tier A
- **Errado:** 3 `pslab` de prata de 0,18: um adesivo plano.
- **Onde:** `A/craft/CAM_SGCraft_W.jpg`, `F/Craft.jpg`.
- **Código:** `sg_craft.py: portal()` (bloco "emblema de prata: o frasco").
- **Direção:** medalhão de pedra com moldura e o frasco em relevo de 2 camadas (bojo lathe cortado ao meio).

### 06.08 Estandartes e postes de lanterna na porta · Tier B
- **Errado:** 2 estandartes rígidos mais 2 postes-cubo, repetição de 12.01, 12.02 e 12.05.
- **Onde:** `F/CU_CraftDoor.jpg`, `A/craft/CAM_SGCraft_PH_Door.jpg`.
- **Código:** `sg_craft.py: portal()`.
- **Direção:** herdam o kit novo. Considerar só as lanternas (o emblema já está no pórtico e dentro).

---

## 07 Alquimia: hero props

### 07.01 [CRÍTICO] Frasco gigante do topo · Tier A
- **Errado:**
  - O bojo é vidro ROSE de 18 lados com o líquido `SG_VioletDeep_Glow` até o equador.
  - No jogo o vidro some e sobra uma bolha magenta estourada sem contorno.
  - O gargalo é um cilindro reto.
  - As 4 garras são vigas retas de prata terminando em bola (garra de brinquedo).
  - Os anéis armilares são fitas finas que giram sem eixo nem pino visível: flutuam (silhueta, material, emissive,
    encaixe).
- **Onde:** `J/AU_Flask.jpg` (topo), `F/Craft.jpg`, `F/finesse_jogo_gerais.jpg` (Craft), `A/craft/CAM_SGCraft_W.jpg`.
- **Código:** `sg_craft.py: flask()`, `energy_rings()`.
- **Direção:**
  - Perfil desenhado (fundo achatado, bojo em pêra, ombro, gargalo afunilado com lábio virado).
  - Vidro em material opaco-claro pintado, com faixa de reflexo.
  - Líquido Neon fraco (≤0,6) só no terço inferior, com superfície em menisco.
  - Garras como estribos curvos (perfil 2D extrudado com rebite) abraçando o bojo.
  - Anéis armilares mais largos (0,9) presos por 2 pinos a um eixo vertical de prata que sai da rolha.
  - Continuam girando, mas com ponto de fixação.

### 07.02 [CRÍTICO] Câmaras de vidro externas: o "jarro cinza genérico" · Tier A
- **Errado:**
  - Cilindro de 16 lados com "vidro" PALE em cima, líquido embaixo, 2 aros e 4 montantes-caixa de 0,13.
  - No jogo o vidro vira cinza opaco: lata de tinta.
  - No Blender são faixas branco/rosa chapadas.
  - A tampa em lathe é a única parte boa.
- **Onde:** `J/AU_CraftBase.jpg`, `A/CAM_SG_AU_CraftBase.jpg`, `A/craft/CAM_SGCraft_S.jpg`, `A/craft/CAM_SGCraft_E.jpg`.
- **Código:** `sg_craft.py: lab_tanks()`.
- **Direção:**
  - Virar CALDEIRA/RETORTA DE COBRE: corpo metálico opaco (lathe com bojo e 2 cintas rebitadas).
  - VISOR redondo pequeno com moldura aparafusada, onde o líquido aparece (o visor é a única peça "de vidro", em cor
    sólida).
  - Pés de ferro.
  - O tubo para o contraforte continua.
  - Ou reduzir de 3 para 2 unidades.

### 07.03 Caldeirão · Tier A
- **Errado:**
  - A silhueta do bojo está boa. O resto não:
    - lábio em Metal_Gold saturado com especular estourado (lê plástico amarelo);
    - rebites em cilindros de latão salientes (pontos dourados);
    - pés em cone mais icosfera (salsicha com bola);
    - orelhas em caixa de 0,84 × 0,36 × 0,38.
- **Onde:** `F/CU_CraftTable.jpg`, `F/CU_Library.jpg`, `F/CraftInterior.jpg`, `A/CAM_SG_CU_Cauldron.jpg`.
- **Código:** `sg_craft.py: cauldron()`.
- **Direção:**
  - Pés em pata de ferro fundido (perfil 2D de 3 dedos extrudado, encostando no bojo).
  - Orelhas fundidas em perfil curvo (arco de tubo grosso).
  - Lábio em bronze envelhecido (14.04).
  - Rebites de ferro, menores, rentes.

### 07.04 [CRÍTICO] Brasa sob o caldeirão · Tier A
- **Errado:** um disco `SG_VioletSoft_Glow` liso. No jogo é uma poça violeta chapada embaixo do herói.
- **Onde:** `F/CraftInterior.jpg`, `F/CU_CraftTable.jpg`.
- **Código:** `sg_craft.py: cauldron()` ("brasa rasa").
- **Direção:** grelha de ferro (4 barras) sobre 6 a 8 pedaços de brasa escuros e facetados. Só as frestas entre eles
  em Neon baixo.

### 07.05 [CRÍTICO] Cristal do lustre e fio de energia · Tier A
- **Errado:** bipirâmide CRYS de 4 studs mais um rod VDEEP até a poção. No jogo é um cone magenta que domina o quadro
  inteiro da porta e esconde o lustre (emissive escondendo forma).
- **Onde:** `F/CU_CraftDoor.jpg`, `F/CraftInterior.jpg`, `F/CU_Library.jpg`.
- **Código:** `sg_craft.py: chandelier()` (grande cristal) e `cauldron()` (fio).
- **Direção:**
  - Cristal com ~2,2 de altura, facetas n=6 com topo cortado, cor lilás e emissão 0,8.
  - Fio mais fino, em 2 segmentos (o de cima escuro).
  - Ou trocar o fio por partícula de subida.

### 07.06 [CRÍTICO] Postes de lanterna do círculo mágico · Tier B
- **Errado:** 2 `lantern_post` s=0,8 com a cabeça na altura do olho, ladeando a passadeira entre a porta e o
  caldeirão. Do vão da porta tapam o herói (cubos amarelos gigantes em primeiro plano).
- **Onde:** `A/craft/CAM_SGCraft_In_Gallery.jpg`, `A/craft/CAM_SGCraft_In_ShelvesN.jpg`,
  `A/craft/CAM_SGCraft_In_ShelvesS.jpg`, `F/CU_CraftTable.jpg`.
- **Código:** `sg_craft.py: circle_lanterns()`.
- **Direção:** remover, ou trocar por candelabros de chão de ferro de 1,8 com 3 velas (kit 12.09), fora do cone da
  porta.

### 07.07 Glifos do círculo mágico · Tier A
- **Errado:** barras e losangos em caixa `SG_VioletDeep_Glow`. No jogo leem tracejado de estacionamento neon.
- **Onde:** `F/CU_CraftTable.jpg`, `F/CraftInterior.jpg`.
- **Código:** `sg_craft.py: magic_circle()`.
- **Direção:** glifos desenhados (perfis 2D com curva, 3 desenhos alternados) EMBUTIDOS no mármore, com emissão
  baixa. O anel de ouro continua como moldura.

### 07.08 [CRÍTICO] Frascos e potes das estantes no jogo · Tier B
- **Errado:**
  - No Blender o kit é bom.
  - No jogo o vidro (Glass_SGCraft, transparência 0,55) vira escuro opaco: frascos pretos.
  - Os acesos (`lit_v` = CRYS, `lit_a` = GLOW) viram bolhas magenta e bastões amarelos.
- **Onde:** `F/CU_Shelf.jpg`, `F/CraftInterior.jpg`.
- **Código:** `sg_craft.py: flask_at()`, `LIQ`, `place_flask()`.
- **Direção:** vidro em material OPACO claro de cor (verde-sálvia, âmbar, lilás) com gola escura. Líquido sem Neon.
  Só 1 a 2 frascos acesos na sala, com emissão baixa.

### 07.09 Alambique da bancada · Tier B
- **Errado:** o conjunto está bom. Detalhes: o fogareiro tem um disco GLOW chapado, e o tubo tem 6 lados com junção
  seca no coletor.
- **Onde:** `F/CU_CraftTable.jpg` (direita).
- **Código:** `sg_craft.py: bench()`.
- **Direção:** fogareiro com grelha e brasa (07.04 em pequeno). Colar de latão no encaixe do tubo.

---

## 08 Alquimia: interior e biblioteca

### 08.01 [CRÍTICO] Paredes internas lisas · Tier A
- **Errado:**
  - O 24-gono interno é liso, com textura de ruído.
  - Entre estantes, estandartes e janelas ficam planos vazios de ~9 studs.
  - No jogo são paredes navy chapadas atrás de tudo.
- **Onde:** `A/craft/CAM_SGCraft_In_Gallery.jpg`, `F/CraftInterior.jpg`, `A/craft/CAM_SGCraft_In_Up.jpg`.
- **Código:** `sg_craft.py: shell()` (`ring_band` da parede) e `interior()` (frisos).
- **Direção:**
  - Lambril de madeira até +3 (painéis emoldurados por face).
  - Pilastras de pedra nas juntas das faces, subindo até as mísulas das nervuras.
  - Reboco liso de cor média acima do lambril (sem ruído).

### 08.02 Fundo e profundidade das estantes · Tier B
- **Errado:** o fundo da estante tem a mesma madeira quente da frente. Os livros não recortam contra o fundo e tudo
  vira uma massa marrom.
- **Onde:** `F/CU_Shelf.jpg`, `A/CAM_SG_CU_Shelf.jpg`.
- **Código:** `sg_craft.py: bookcases()` (fundo `fprism ... 0.42, 8.6, WOOD`).
- **Direção:** fundo em madeira dois valores mais escura. Testeiras com filete de latão fino só no andar do meio.

### 08.03 Pergaminhos · Tier B
- **Errado:** cilindros n=7 em Cloth_Canvas quase brancos. No jogo são 5 bastões brancos saturando o canto.
- **Onde:** `F/CU_Shelf.jpg`.
- **Código:** `sg_craft.py: place_scrolls()`.
- **Direção:** tom pergaminho mais escuro e quente. Ponta com rolo de madeira (disco n=6) e fita vinho só em 1 ou 2.

### 08.04 Atril · Tier B
- **Errado:** fuste-caixa de 0,44 sobre base em lathe, tampo-caixa inclinado.
- **Onde:** `A/craft/CAM_SGCraft_In_Door.jpg`.
- **Código:** `sg_craft.py: lectern()`.
- **Direção:** coluna torneada (lathe de 6 pontos), tampo com borda e trave de apoio do livro, pés em cruz.

### 08.05 Baú e saco · Tier B
- **Errado:** baú de caixas, faixas de ferro em caixa e fechadura em caixa. O saco é uma icosfera com um cone.
- **Onde:** `F/CU_Library.jpg` (canto inferior esquerdo).
- **Código:** `sg_craft.py: chest()`.
- **Direção:** tampa abaulada (arco extrudado), cantoneiras, alças de argola. Saco com amarração e 2 dobras (lathe
  deformado).

### 08.06 Galeria das costas · Tier B
- **Errado:** mísulas triangulares planas (`pside`), balaústres-caixa de 0,16, corrimão em anel liso. Lê andaime.
- **Onde:** `A/craft/CAM_SGCraft_In_Gallery.jpg`, `F/CraftInterior.jpg`, `F/CU_CraftDoor.jpg`.
- **Código:** `sg_craft.py: gallery()`.
- **Direção:** mísulas em perfil S, balaústres redondos n=6 com anel a cada 3, corrimão boleado.

### 08.07 Nervuras e chave da abóbada interna · Tier B
- **Errado:** sweep de seção quadrada de 0,6 e chave em cilindro n=12.
- **Onde:** `A/craft/CAM_SGCraft_In_Up.jpg`.
- **Código:** `sg_craft.py: interior()`.
- **Direção:** perfil redondo e chave com florão (igual 04.04).

### 08.08 Lanterna das mesas · Tier B
- **Errado:** `lantern_head` s=0,46, um cubo amarelo pequeno.
- **Onde:** `F/CU_CraftTable.jpg`, `F/CraftInterior.jpg`.
- **Código:** `sg_craft.py: study_tables()` → `sg_emblem.lantern_head`.
- **Direção:** herda 12.01. Numa mesa, uma vela com castiçal basta.

### 08.09 Lustre (anel, velas, pingentes) · Tier B
- **Errado:** anel em tubo de 6 lados, velas em cilindro Plaster com chama em icosfera, pingentes em bipirâmide de 5
  lados. Aceitável, mas a vela é bastão (kit 12.09).
- **Onde:** `A/craft/CAM_SGCraft_In_Up.jpg`, `A/craft/CAM_SGCraft_In_Gallery.jpg`.
- **Código:** `sg_craft.py: chandelier()`.
- **Direção:** kit de vela. Anel com perfil n=8.

---

## 09 Dungeon

### 09.01 [CRÍTICO] Massa de rocha em estratos · Tier A
- **Errado:**
  - Cada bloco é a MESMA planta de 9 lados empilhada nas juntas, só mudando a escala: pilha de pneus/panquecas.
  - Não há fratura vertical nem blocos deslocados.
  - As bordas são arredondadas iguais em todas as camadas.
  - No jogo lê como bolo de camadas.
- **Onde:** `F/Dungeon.jpg`, `A/dungeon/CAM_SGDun_HouseNorth.jpg`, `A/dungeon/CAM_SGDun_HouseEast.jpg`,
  `A/dungeon/CAM_SGDun_HouseWest.jpg`.
- **Código:** `sg_dungeon.py: strata_rock()`, `house_shell()`.
- **Direção:**
  - Cortar cada camada em 2 a 3 prismas por diáclases VERTICAIS (planos com o mesmo rumo em toda a massa) e deslocar
    as partes (0,3 a 0,8).
  - Mudar a planta entre camadas duras (não só a escala).
  - Algumas camadas com lábio quebrado saliente.
  - Menos camadas finas e mais bancos grossos.
  - Mesmo convex hull, com mais pontos de corte.

### 09.02 [CRÍTICO] Ombreiras de cantaria da boca · Tier A
- **Errado:** fiadas de caixa em Stone_SG_Castle, claras, alternando recuo. No jogo são blocos de brinquedo bege/cinza
  sobre as aduelas violeta: contraste errado e arestas vivas.
- **Onde:** `F/CU_DunApproach.jpg`, `F/CU_DunMouth.jpg`, `F/Dungeon.jpg`.
- **Código:** `sg_dungeon.py: cave_mouth()` (bloco "1. ombreiras").
- **Direção:**
  - Cantaria no valor da rocha (um tom acima), bevel de 0,1.
  - Blocos com quina quebrada (1 vértice puxado) nas fiadas altas: ruína.
  - Líquen nas juntas superiores (faixa Grass fina no topo de 2 fiadas).

### 09.03 [CRÍTICO] Degraus partidos no revestimento do túnel · Tier A
- **Errado:** escadinhas regulares de caixas claras nas duas laterais do túnel: Lego, não ruína.
- **Onde:** `F/CU_DunMouth.jpg`, `F/CU_DunApproach.jpg`.
- **Código:** `sg_dungeon.py: mouth_lining()`.
- **Direção:** quebra irregular com blocos inclinados, 1 caído no piso e faces de fratura (convex hull de 8 pontos). O
  tom segue 09.02.

### 09.04 [CRÍTICO] Runas das ombreiras e dos marcos · Tier A
- **Errado:** os glifos entalhados leem como "X" e seta "↑" (sinalização de UI).
- **Onde:** `F/CU_DunApproach.jpg`, `F/Dungeon.jpg`, `A/dungeon/CAM_SGDun_Approach.jpg`.
- **Código:** `sg_dungeon.py: glyph()` (usado em `cave_mouth()` e `crystal_pedestal()`).
- **Direção:** glifos de 3 a 4 traços com curva, sem forma latina nem de seta. O mesmo alfabeto dos obeliscos (03.05).

### 09.05 Pilares dos estandartes · Tier A
- **Errado:** fiadas de caixa navy alternando largura, capitel em caixa e remate em pirâmide n=4.
- **Onde:** `F/Dungeon.jpg`, `A/dungeon/CAM_SGDun_Approach.jpg`.
- **Código:** `sg_dungeon.py: pillar()`.
- **Direção:** base moldurada, cintas de obsidiana mais finas com pingadeira, capitel com 4 mísulas e o remate do kit.

### 09.06 Entulho do pilar partido · Tier A
- **Errado:** 3 caixas rodadas e 2 lascas-caixa pousadas no piso: caixas caídas, não pedras quebradas.
- **Onde:** `A/dungeon/CAM_SGDun_Approach.jpg`, `A/dungeon/CAM_SGDun_Far.jpg`.
- **Código:** `sg_dungeon.py: rubble()`.
- **Direção:** usar as PEÇAS do pilar (capitel com a mesma moldura, fiada com face de fratura irregular) e uma aduela
  com o perfil do arco, todas com uma face quebrada (hull).

### 09.07 Marcos da aproximação · Tier B
- **Errado:** pilha de caixas (soco, fuste, cinta, capa) com pirâmide n=4.
- **Onde:** `F/CU_DunApproach.jpg` (direita), `F/Dungeon.jpg`.
- **Código:** `sg_dungeon.py: crystal_pedestal()`.
- **Direção:** fuste chanfrado, cinta de ferro com ARGOLA real onde a corrente entra, remate em bola ou pinha.

### 09.08 [CRÍTICO] Cristais do túnel e cristal da boca · Tier A
- **Errado:** bipirâmides n=4 CRYS. No jogo são lascas planas magenta (papel neon), espalhadas em pares simétricos.
- **Onde:** `F/CU_DunMouth.jpg`, `F/CU_DunApproach.jpg`, `A/dungeon/CAM_SGDun_Tunnel.jpg`.
- **Código:** `sg_dungeon.py: crystal()` (`TUN_CRYSTALS`, `VFX_SGDUN_MouthCrystal`).
- **Direção:** usar o `crystal_col()`/`cluster()` que já existe (coluna hexagonal com ponta e calo de rocha) em 3
  aglomerados assimétricos. Emissão só na ponta. Cor menos saturada.

### 09.09 Veios de energia · Tier A
- **Errado:** linhas Neon finas coladas na parede. Leem como raio 2D desenhado por cima.
- **Onde:** `F/CU_DunMouth.jpg`.
- **Código:** `sg_dungeon.py: tunnel_veins()`.
- **Direção:** veio como FENDA: rebaixo escuro de 0,3 com o fio Neon dentro (a borda da rocha faz sombra).

### 09.10 [CRÍTICO] Kit das salas R1, R2 e R3 · Tier A
- **Errado:**
  - Pilastras em caixa com colunelo n=8, colunas de canto em caixa, cornija em caixa, arcos cegos em painel.
  - As 3 salas são o MESMO kit, sem variação.
  - Abóbada com textura de ruído.
  - Piso em grade regular de 4 × 4.
- **Onde:** `A/dungeon/CAM_SGDun_R2.jpg`, `A/dungeon/CAM_SGDun_R3Back.jpg`, `A/dungeon/CAM_SGDun_R1Spawn.jpg`,
  `A/dungeon/CAM_SG_PlayerHeight_DungeonRoom.jpg`.
- **Código:** `sg_dungeon.py: room_walls()`, `room_kit()`, `pilaster()`, `corner_col()`, `blind_arch()`, `cornice()`,
  `tile_floor()`, `vault()`.
- **Direção:**
  - 1 variação dirigida por sala:
    - R1: portal e arcos altos;
    - R2: mísulas com grelhas de ferro e escoras de madeira de mina;
    - R3: altar e colunas duplas.
  - Pilastras com base e capitel.
  - Lajes em 2 tamanhos.
  - Nervuras em perfil redondo.

### 09.11 [CRÍTICO] Tochas das salas · Tier B
- **Errado:** mão-francesa em viga, copo cilíndrico n=6 e chama em CONE amarelo neon: cone de trânsito.
- **Onde:** `A/dungeon/CAM_SGDun_R2.jpg`, `A/dungeon/CAM_SGDun_R1Arrival.jpg`, `A/dungeon/CAM_SGDun_R2Link.jpg`.
- **Código:** `sg_dungeon.py: torch()`.
- **Direção:** cesto de ferro de 4 hastes curvas com trapo escuro e chama em gota de 2 tons (núcleo claro, borda
  laranja) (kit 12.09).

### 09.12 Moldura do portal das salas · Tier A
- **Errado:** anel com "ticks" em caixa, chave em caixa e pés em caixa.
- **Onde:** `A/dungeon/CAM_SGDun_R1Arrival.jpg`, `A/dungeon/CAM_SGDun_R3Exit.jpg`.
- **Código:** `sg_dungeon.py: portal_frame()`.
- **Direção:** anel de aduelas com runas gravadas (09.04), chave esculpida e pés em consola.

### 09.13 Runas do piso das salas · Tier A
- **Errado:** glifos Neon planos em anel no piso. É o segundo alfabeto (conflita com 09.04 e 03.05).
- **Onde:** `A/dungeon/CAM_SGDun_R3Exit.jpg`, `A/dungeon/CAM_SGDun_R1Arrival.jpg`.
- **Código:** `sg_dungeon.py: floor_runes()`.
- **Direção:** o mesmo alfabeto entalhado, com emissão baixa.

---

## 10 Summon

### 10.01 [CRÍTICO] Lanternas góticas dos pedestais · Tier A
- **Errado:** caixa Lantern_Glow de 0,9 × 2,0, 4 montantes-caixa de 0,28 e chapéu `spire n=4` de ardósia. Cubo
  amarelo com chapéu, na altura do olho de quem sobe a escada.
- **Onde:** `A/summon/CAM_SGSum_PlayerWalk.jpg`, `A/summon/CAM_SGSum_PlayerPad.jpg`, `F/Summon.jpg`.
- **Código:** `sg_summon.py: gothic_lantern()`.
- **Direção:** herda 12.01 (versão alta: camisa de vidro recuada, gaiola com arcos ogivais e chama).

### 10.02 [CRÍTICO] Segundo sistema de símbolos: estrelas · Tier A
- **Errado:**
  - Estrelas de 4 pontas de prata no pódio.
  - Estrela de 8 pontas no piso do jogador.
  - Estrela no nicho do portal e na janela da torre (Ilha 1).
  - Tudo contra a regra "um único símbolo da ordem; nada de estrela solta" (DECISOES/sg_emblem).
- **Onde:** `A/summon/CAM_SGSum_PlayerPad.jpg`, `A/summon/CAM_SGSum_PlayerWalk.jpg`, `F/Summon.jpg`.
- **Código:** `sg_summon.py: base()` (`K.star`), `floor_inlay()` (`K.star_pts`) e a torre importada de `il_summon`.
- **Direção:**
  - Pódio: rosetas geométricas neutras ou o crescente-lâmina pequeno.
  - Piso: rosácea de cantaria sem estrela.
  - A estrela fica SÓ no portal e na esfera, onde é a função gacha.

### 10.03 [CRÍTICO] Arco da ponte do summon · Tier B
- **Errado:** aduelas em caixa reta por segmento, formando escadinha no intradorso com frestas. Os pés do arco
  atravessam as colunas de basalto.
- **Onde:** `A/summon/CAM_SGSum_BridgeSide.jpg`.
- **Código:** `sg_summon.py: bridge()`.
- **Direção:** aduelas radiais (`obox3`, como `cave_mouth`), impostas de pedra onde o arco nasce e a rocha recortada
  em volta dos pés.

### 10.04 Balaustrada gótica da plataforma · Tier B
- **Errado:** colunelos-caixa de 0,32 a cada 1,15 e pilares em caixa com pirâmide. Repetição mecânica em 40 studs de
  arco.
- **Onde:** `A/summon/CAM_SGSum_PlayerWalk.jpg`, `F/Summon.jpg`.
- **Código:** `sg_summon.py: gothic_rail()`.
- **Direção:** balaústres torneados (lathe n=6) ou arcadas trilobadas em painel. Pilares com gablete (kit 12.12).

### 10.05 Pilastras do pódio · Tier B
- **Errado:** caixas de 1 × 1 lisas no contorno, sem base nem capitel.
- **Onde:** `A/summon/CAM_SGSum_PlayerPad.jpg`.
- **Código:** `sg_summon.py: base()` (loop `pil`).
- **Direção:** base e capitel em 2 degraus. Painel rebaixado entre pilastras.

### 10.06 Esfera armilar e estrela estourando no jogo · Tier A
- **Errado:** a estrela lilás em SG_SumStar_Glow 1,5 estoura em branco no Roblox (bloom) e apaga a gaiola.
- **Onde:** `F/Summon.jpg`, `F/finesse_jogo_gerais.jpg` (Summon).
- **Código:** `sg_summon.py` (`SG_SumStar_Glow`) e `il_summon.sphere`.
- **Direção:** emissão 0,8 a 1,0 e cor mais saturada (menos branca), para a gaiola de prata ler na frente.

### 10.07 Linha magenta vertical no pé da escada da torre (só no jogo) · verificar
- **Errado:** fio Neon vertical na frente do portal. Não existe no render do Blender.
- **Onde:** `F/Summon.jpg`.
- **Código:** não encontrado nos `sg_*.py` (provável Beam/VFX do sistema de invocação).
- **Direção:** verificar no Studio. Se for indicador de interação, trocar por brilho no piso.

---

## 11 Portões e pontes

### 11.01 [CRÍTICO] Pilares da cabeceira da saída · Tier A
- **Errado:**
  - Fuste-caixa de 3,1 com a mesma "janela cega de palitos" dos pórticos de entrada.
  - Coroa em caixa com pirâmide n=4.
  - Lanterna de braço em cubo de vidro.
- **Onde:** `A/exit/CAM_SGExit_PlayerHead.jpg`.
- **Código:** `sg_exit.py: head_pylon()`.
- **Direção:** a receita de 01.06. Lanterna de braço do kit 12.01.

### 11.02 Parapeito da ponte de saída e lanternas a cada 11 · Tier B
- **Errado:** viga lisa com capa e pedestal-lanterna a cada 11: muro liso com cubos.
- **Onde:** `A/exit/CAM_SGExit_PlayerHead.jpg`, `A/exit/CAM_SGExit_SideN.jpg`.
- **Código:** `sg_exit.py: sg_parapet()`, `parapets()`.
- **Direção:** a receita de 01.03. Lanternas só na cabeceira e no marco.

### 11.03 Guarda-corpo Demon Slayer · Tier B
- **Errado:** base-caixa, pilaretes-caixa vermelhos de 0,46, kasagi em viga reta sem pontas levantadas e capacete
  preto em pirâmide n=4.
- **Onde:** `A/exit/CAM_SGExit_PlayerMarco.jpg`, `A/exit/CAM_SGExit_Junction.jpg`.
- **Código:** `sg_exit.py: ds_rail()`.
- **Direção:** kasagi com pontas curvadas para cima (perfil 2D), giboshi (remate em cebola de bronze, lathe) nos
  pilares de canto e travessa com espiga.

### 11.04 Marco da transição (ds_post) · Tier B
- **Errado:** a lanterna de papel é um cilindro GLOW com 2 discos. O pilar octogonal está bom.
- **Onde:** `A/exit/CAM_SGExit_PlayerMarco.jpg`.
- **Código:** `sg_exit.py: ds_post()`.
- **Direção:** lanterna com 6 costelas verticais escuras e tampa/fundo em lathe.

### 11.05 Portão DS aprovado (fora da ilha, mas é a última imagem) · Tier A
- **Errado:** painel vermelho plano com linhas Neon e cadeado. Lê cartaz, e é a moldura final da ilha.
- **Onde:** `A/exit/CAM_SG_PlayerHeight_ExitGate.jpg`, `A/exit/CAM_SGExit_PlayerMarco.jpg`, `A/_folha_exit.jpg`.
- **Código:** `sg_core.py: ds_gate()` → `il_gate_ds.build_gate` (asset da galeria, aprovado).
- **Direção:** sinalizar ao dono do portão. Não mexer daqui.

### 11.06 Junta ponte/ilhota da saída · Tier B
- **Errado:** o tabuleiro encontra o piso da ilhota em junta reta. A borda de cantaria da ilhota é uma fileira de
  dentes-caixa (ameias baixas) idênticos.
- **Onde:** `A/exit/CAM_SGExit_Junction.jpg`.
- **Código:** `sg_exit.py: islet()`, `islet_rails()`, `deck()`.
- **Direção:** soleira de cantaria na junta. Borda com capa contínua e mísulas embaixo, em vez dos dentes.

### 11.07 Portão da muralha, arco do portão, pontes de entrada e do summon
- Remissões: 03.12 (verga e grade), 02.14 (arco de ferro: a mesma função no pé da escada Gate), 01.09 (aduelas da
  ponte de entrada), 10.03 (ponte do summon).

---

## 12 Props globais (kit compartilhado: corrigir aqui corrige a ilha)

### 12.01 [CRÍTICO] Lanterna da ordem: o "cubo amarelo emissivo" · Tier B (~90 instâncias)
- **Errado:**
  - O vidro é UMA caixa inteira de 1,05 × 1,05 × 1,74 em Lantern_Glow (Neon), com 4 montantes de 0,16.
  - Base e travessa em caixa, tampa em pirâmide n=4, zero bevel.
  - No jogo o Neon engole os montantes e sobra um cubo amarelo.
  - Altura de ~3,3 no poste (o brief pede 1,5 a 2,5).
  - Presente na entrada, praça, eixo, pátio, muralha, alquimia, dungeon, summon e saída.
- **Onde:** `J/AU_Lantern.jpg`, `J/AU_GuardFront.jpg`, `J/AU_Fountain.jpg`, `J/AU_Stair.jpg`,
  `F/PlayerHeight_Entry.jpg`, `F/CU_CraftDoor.jpg`, `A/entry/CAM_SGEnt_PlayerBridge.jpg`.
- **Código:** `sg_emblem.py: lantern_head()` e as cópias locais `sg_entry.lantern()`, `sg_summon.gothic_lantern()`,
  `sg_court.iron_arch()` (lanternas) e `sg_exit.head_pylon()` (lanterna do braço).
- **Direção:**
  - Lanterna HEXAGONAL (6 lados).
  - Montantes de 0,14 com chanfro na frente.
  - Vidro RECUADO 0,1 atrás dos montantes, em material âmbar escuro NÃO emissivo.
  - Dentro, uma vela pequena (prato + vela creme + chama em gota Neon de ~0,35): só a chama emite.
  - Travessa a 2/3 dividindo o vidro.
  - Base em prato moldurado (lathe de 4 pontos).
  - Tampa com beiral curvo (lathe de 5 pontos, n=6) e argola no topo.
  - Escala 0,7 da atual.
  - Polycount parecido: troca caixas por lathes de 6 lados.

### 12.02 [CRÍTICO] Poste de lanterna: 3 caixas empilhadas · Tier B
- **Errado:** soco-cubo de obsidiana de 1,4, fuste em caixa quadrada lisa de ferro (0,5 × ~6,5) e capitel em bloco
  dourado. No jogo é uma silhueta preta de vara com dado.
- **Onde:** `J/AU_Lantern.jpg`, `J/AU_GuardFront.jpg`, `F/PlayerHeight_Plaza.jpg`.
- **Código:** `sg_emblem.py: lantern_post()`.
- **Direção:**
  - Base em sino moldurado (lathe n=8: plinto, toro, escócia).
  - Fuste redondo ou octogonal afinando, com anel a 1/3 e colar.
  - Capitel com 4 consoles em S segurando o prato da lanterna.
  - Ferro um valor mais claro (14.08).

### 12.03 Lanterna de pedestal · Tier B
- **Errado:** 2 caixas de obsidiana, laje de prata e cabeça de lanterna, com ~5,4 de altura total: do tamanho do
  avatar.
- **Onde:** `J/AU_Fountain.jpg`, `F/PlayerHeight_Entry.jpg`, `A/entry/CAM_SGEnt_PlayerBridge.jpg`.
- **Código:** `sg_emblem.py: lantern_pedestal()`.
- **Direção:** pedestal em balaústre torneado curto ou dado moldurado, com a lanterna 12.01. Altura total ≤ 3,5 em
  parapeito.

### 12.04 [CRÍTICO] Quantidade e ritmo das lanternas · Tier B (harmonia)
- **Errado:** pares rígidos a cada 5,6 (ponte), 11 (saída), 12 (muralha) e 14 (eixo P2), mais pilaretes, praça, bacia
  e summon. Distribuição uniforme em fileiras: cerca de luz, e a escada e os pórticos somem atrás dos cubos.
- **Onde:** `A/entry/CAM_SGEnt_PlayerBridge.jpg`, `A/exit/CAM_SGExit_PlayerHead.jpg`, `A/_folha_entry.jpg`,
  `J/AU_Fountain.jpg`.
- **Código:**
  - `sg_entry.parapets()`
  - `sg_court.axis_north()` (`AXIS_LANTERN_Y`)
  - `sg_castle.muralha()`
  - `sg_exit.parapets()`
  - `sg_summon.order_dressing()`
  - `sg_village.plaza()`
- **Direção:**
  - Cortar ~40%.
  - Lanterna só em NÓS: começo e fim de ponte, portões, pé e topo de escada.
  - Nos intervalos, remate de pedra.

### 12.05 Estandarte da ordem · Tier B (~25 instâncias)
- **Errado:**
  - Pano pentagonal rígido de 0,22, plano, com ponta em V, verga reta e o emblema no mesmo lugar.
  - Idêntico na entrada (4), castelo (6), alquimia (4), salão (6), dungeon (1), saída (2), summon (2) e vila (2).
  - Sem caimento nem dobra: placa roxa.
- **Onde:** `F/PlayerHeight_Entry.jpg`, `A/castle/CAM_SGCas_PlayerHeight_Gate.jpg`, `A/entry/CAM_SGEnt_PlayerBridge.jpg`,
  `A/hall/CAM_SGHall_West.jpg`.
- **Código:** `sg_emblem.py: banner()`.
- **Direção:**
  - Seção do pano ondulada (6 pontos: 2 dobras verticais largas) extrudada para baixo.
  - Leve abaulado para a frente no terço de baixo.
  - Borlas pequenas nas pontas do V.
  - 2 larguras (estreito e largo) escolhidas por lugar.
  - Reduzir a quantidade (16.02).

### 12.06 [CRÍTICO] Banco · Tier B
- Ver 01.15 (`sg_props.py: bench()`).

### 12.07 Arco de ferro de transição · Tier B
- Ver 02.14 (`sg_court.py: iron_arch()`). Um conserto vale para os 2 arcos.

### 12.08 [CRÍTICO] Armas decorativas: espadas das estátuas · Tier A
- Ver 03.02 (`sg_court.py: hooded_figure()`). A espada do emblema (`sg_emblem._bar`) já tem o perfil certo e é a
  referência.

### 12.09 [CRÍTICO] Velas, tochas e candeias: bastões e cones Neon · Tier B
- **Errado:** vela = cilindro Lantern_Glow n=6 inteiro. Tocha = cone amarelo. Candeia = cilindro. Presentes no salão,
  na dungeon e nos 2 lustres da alquimia.
- **Onde:** `F/PlayerHeight_MiningHall.jpg`, `A/dungeon/CAM_SGDun_R2.jpg`, `A/craft/CAM_SGCraft_In_Up.jpg`.
- **Código:** `sg_hall.chandelier()`, `sg_hall.ironwork()`, `sg_dungeon.torch()`, `sg_dungeon.chandelier()`,
  `sg_craft.chandelier()`.
- **Direção:** UM kit de vela (prato de ferro, vela creme não-emissiva de 0,5 a 0,7, chama em gota Neon de 0,3) usado
  em todos. Tocha = cesto de ferro com chama de 2 tons.

### 12.10 Flores e floreiras em gema · Tier B
- Ver 02.04 e 03.06 (`sg_village.window()`, `sg_village.house_identity()`, `sg_court.parterre()`).

### 12.11 Placa com emblema · Tier B
- **Errado:** o disco de obsidiana com emblema está bem feito, mas aparece em pedestais, obeliscos, lintel do pórtico
  B, fecho da dungeon, tímpanos das salas, porta do castelo e caldeirão. É carimbo.
- **Onde:** `F/CU_CastleDoor.jpg`, `F/CU_DunApproach.jpg`.
- **Código:** `sg_emblem.py: plaque()` e seus chamadores.
- **Direção:** manter na porta do castelo, no caldeirão e no fecho da dungeon. Remover dos obeliscos, do lintel B, dos
  pedestais e dos tímpanos das salas.

### 12.12 Remate universal "pirâmide de 4 lados" · Tier B
- **Errado:** `SL.spire(n=4)` sobre caixa. É o remate de:
  - pilaretes (entrada e saída);
  - muretas e canteiros;
  - marcos e pilares da dungeon;
  - balaustrada do summon;
  - pináculos do castelo e do altar;
  - lanternas.
  Uma assinatura de kit procedural única em toda a ilha.
- **Onde:** `A/entry/CAM_SGEnt_Back.jpg`, `A/summon/CAM_SGSum_PlayerWalk.jpg`, `F/Dungeon.jpg`.
- **Código:** `sg_lib.spire` via `sg_entry._post`, `sg_exit.sg_post`, `sg_court.muret`/`parterre`,
  `sg_summon.gothic_rail`, `sg_dungeon.pillar`/`crystal_pedestal`.
- **Direção:** kit de 2 remates: bola com colar (lathe n=8) para cantaria baixa e pinha facetada ou pináculo com
  gablete para os altos. Proibir a pirâmide pura perto do jogador.

---

## 13 Terreno e background (Tier C, salvo indicação)

### 13.01 Penhasco em colunas hexagonais · Tier C
- **Errado:**
  - Centenas de colunas do mesmo diâmetro, em alturas sorteadas: repetição uniforme, sem massa grande que organize.
  - Textura mosqueada verde-violeta (camuflagem).
- **Onde:** `A/terrain/CAM_SGTer_CliffEast.jpg`, `A/terrain/CAM_SGTer_NorthEast.jpg`, `A/terrain/CAM_SG_Ref_Side.jpg`.
- **Código:** `sg_terrain.py: rim_cliff()`, `column()`, `under()`.
- **Direção:**
  - 3 escalas: 4 a 6 massas grandes (promontórios) com as colunas como detalhe.
  - 2 faixas de estrato horizontal contínuas que amarram a borda.
  - Textura sem mancha verde (14.02).

### 13.02 Cachoeiras · Tier C
- **Errado:** lâmina azul lisa com listras brancas paralelas retas e espuma em icosfera. Lê fita de cetim.
- **Onde:** `A/terrain/CAM_SGTer_CliffEast.jpg`, `A/terrain/CAM_SGTer_WaterWest.jpg`, `A/entry/CAM_SGEnt_SideW.jpg`.
- **Código:** `sg_water.py: Fall` (`build`, `_strip`), `sheet()`.
- **Direção:** 3 faixas de largura variável que se quebram nos degraus da rocha (a lâmina bate e espalha). Cor menos
  saturada. Véu de espuma no pé em 2 anéis.

### 13.03 Mar de nuvens · Tier C
- **Errado:** icosferas lilás achatadas e empilhadas: massinha.
- **Onde:** `A/terrain/CAM_SGTer_Under.jpg`, `A/terrain/CAM_SG_Back.jpg`.
- **Código:** `sg_scene.py: clouds()`.
- **Direção:** camadas horizontais de discos muito achatados sobrepostos, com borda superior mais clara e a de baixo
  mais escura.

### 13.04 Ilhotas flutuantes · Tier C
- **Errado:** rocha em icosfera, pinheiro em 3 cones de 7 lados empilhados sobre um cilindro, cachoeira em caixa.
  Primitivas empilhadas no céu de todas as vistas.
- **Onde:** `A/castle/CAM_SG_Ref_Main.jpg`, `F/Summon.jpg` (fundo), `A/_folha_terrain.jpg`.
- **Código:** `sg_scene.py: islets()`.
- **Direção:** usar `sg_veg.pine(..., lod=2)`, a rocha em 2 a 3 estratos (como a dungeon corrigida) e a cachoeira do
  13.02 em miniatura.

### 13.05 [CRÍTICO] Muros de arrimo P1→P2 e P2→P3 · Tier B
- **Errado:**
  - Fiadas de 1,9 com a mesma junta, blocos de 3 a 5,4: tijolo de Lego gigante.
  - Mísulas idênticas a cada 2,6.
  - Parapeito liso com pilaretes a cada 11.
  - É o fundo de toda a praça, em close de 10 studs.
- **Onde:** `J/AU_Lantern.jpg` (fundo), `A/terrain/CAM_SGTer_PlayerHeight_P1Wall.jpg`,
  `A/terrain/CAM_SGTer_PlayerHeight_P3Wall.jpg`.
- **Código:** `sg_terrain.py: masonry()`, `corbels()`, `parapet()`, `buttresses()`, `terrace_edges()`.
- **Direção:**
  - 2 alturas de fiada alternadas (1,4 / 2,2).
  - Blocos com bevel de 0,08 e face levemente abaulada (1 vértice central puxado).
  - Mísulas com arquinhos entre elas.
  - Capa do parapeito em peças com junta.
  - Contrafortes com talude.

### 13.06 [CRÍTICO] Parapeito das bordas (P3 oeste, borda do P1) · Tier B
- **Errado:** corpo em caixa lisa, capa branca e pilaretes-caixa. Blockout puro, onde o jogador encosta.
- **Onde:** `A/terrain/CAM_SGTer_PlayerHeight_P3West.jpg`, `A/terrain/CAM_SGTer_PlayerHeight_P1Edge.jpg`.
- **Código:** `sg_terrain.py: parapet()`.
- **Direção:** a receita de 01.03 e 13.05. Esta função sozinha cobre quilômetros de borda.

### 13.07 Base de basalto das bordas altas · Tier C
- **Errado:** colunas do mesmo raio (2,3 a 3,4) em fileira regular a cada 4,3.
- **Onde:** `A/terrain/CAM_SGTer_PlayerHeight_P3West.jpg`.
- **Código:** `sg_terrain.py: rock_base()`.
- **Direção:** agrupar em maciços de 3 a 5 colunas com vãos, e alternar o topo (grama ou rocha) por grupo, não por
  coluna.

### 13.08 Pinheiros e ciprestes perto das rotas · Tier C/B
- **Errado:** de perto as saias cônicas são facetadas, e o cipreste lê como cone escuro (03.06). Os grupos da borda
  estão OK.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_Forecourt.jpg`, `A/CAM_SGVeg_PH_P2.jpg`.
- **Código:** `sg_veg.py: pine()`, `cypress()`.
- **Direção:** saia inferior com mais lobos (LOD0) nas árvores a menos de 15 da rota. Cipreste com 4 fusos e topo
  torto.

### 13.09 Cristais da borda · Tier C
- **Errado:** lascas Neon pequenas espalhadas pela face inteira (densidade uniforme).
- **Onde:** `A/terrain/CAM_SGTer_CliffEast.jpg`, `A/terrain/CAM_SGTer_WaterNorth.jpg`.
- **Código:** `sg_terrain.py: rim_crystals()`.
- **Direção:** concentrar em 3 a 4 aglomerados (perto da dungeon, sob o summon e sob o castelo) e zerar o resto.

---

## 14 Materiais

### 14.01 [CRÍTICO] Stone_SG_Trim claro demais perto do jogador · Tier B
- **Errado:** o valor 164 (quase branco) está em estátuas, capas de parapeito, anéis da praça, molduras do torreão,
  cunhais e cantaria da dungeon. No Roblox, sem textura, lê cinza de blockout ou plástico branco.
- **Onde:** `J/AU_GuardSide.jpg`, `J/AU_Lantern.jpg`, `F/CU_VillageHouse.jpg`, `F/CU_DunMouth.jpg`.
- **Código:** `sg_lib.py: SMATS["Stone_SG_Trim"]` (congelado: pedir ao dono) e usos em todos os módulos.
- **Direção:** 128 a 136, levemente quente. Criar um Trim_Light só para peças altas e distantes.

### 14.02 [CRÍTICO] Textura procedural de ruído em pedra · Tier A/B
- **Errado:** manchas de nuvem e camuflagem em Stone_SG_Castle, Cliff_Rock_SG, fundo dos nichos do salão, abóbadas da
  dungeon e paredes da alquimia. É procedural sem direção. No Roblox desaparece, e os planos que ele disfarçava viram
  lisos.
- **Onde:** `A/castle/CAM_SGCas_PlayerHeight_WestAlley.jpg`, `A/hall/CAM_SGHall_West.jpg`,
  `A/terrain/CAM_SGTer_CliffEast.jpg` (Blender) × `F/CU_CastleWindow.jpg` (jogo).
- **Código:** `fm_lib` (TEX_RULES e texturas das pedras) e `sg_lib.SMATS`.
- **Direção:** dar a leitura de pedra por GEOMETRIA (fiadas, painéis, 03.08) e usar textura só em escala de bloco
  (juntas), ou nenhuma. Nunca contar com textura para esconder um plano.

### 14.03 [CRÍTICO] Vidro nos hero props · Tier A
- **Errado:** Glass_SGCraft* e Glass_SG_Rose no Roblox viram opacos escuros ou somem. Frasco gigante, remates, tanques
  e frascos das estantes dependem de transparência.
- **Onde:** `J/AU_Flask.jpg`, `J/AU_CraftBase.jpg`, `F/CU_Shelf.jpg`.
- **Código:** `sg_lib.py: _NEW_RULES` (Glass_SGCraft → Glass 0,55) e `sg_craft.py: NEW_MATS`.
- **Direção:** vidro PINTADO: material opaco de cor média-clara mais uma 2ª malha fina de reflexo (faixa curva em cor
  clara). Transparência só em vidro plano grande.

### 14.04 Metal_Gold saturado · Tier A/B
- **Errado:** amarelo-laranja saturado com especular estourado (lábio do caldeirão, molduras das lanternas, anéis). Lê
  brinquedo e briga com a paleta dessaturada.
- **Onde:** `F/CU_CraftTable.jpg`, `F/CU_Library.jpg`, `J/AU_CraftBase.jpg`.
- **Código:** `fm_lib.MATS["Metal_Gold"]` (usado em sg_craft, sg_emblem, sg_summon).
- **Direção:** bronze envelhecido: menos saturado, 20% mais escuro, rough 0,45.

### 14.05 Água da fonte · Tier B
- **Errado:** Water_SG azul saturado e emissivo: lâmina de plástico azul.
- **Onde:** `J/AU_Fountain.jpg`, `J/AU_PlazaFloor.jpg`.
- **Código:** `sg_lib.SMATS["Water_SG"]` e `sg_village.plaza()`.
- **Direção:** água da fonte em material próprio, escuro e esverdeado, sem emissão, com anel de espuma claro.

### 14.06 Window_Warm chapado · Tier B
- Ver 02.03. O mesmo vale para as lancetas do castelo e as janelas da alquimia: 100% emissivas, sem profundidade.

### 14.07 Parede da alquimia em material único · Tier A
- **Errado:** Stone_SGCraftDark cobre a rotunda inteira, por dentro e por fora, sem mudança de material por zona.
- **Onde:** `F/Craft.jpg`, `F/CraftInterior.jpg`.
- **Código:** `sg_craft.py: WALL`.
- **Direção:** embasamento em Stone_SG_Block, corpo no escuro atual, lambril interno em madeira e reboco acima (06.01,
  08.01).

### 14.08 Ferro quase preto · Tier B
- **Errado:** Metal_SG_BlackIron (40, 38, 46): postes, grades e braços viram silhuetas pretas sem volume à noite.
- **Onde:** `J/AU_Lantern.jpg`, `J/AU_GuardFront.jpg`.
- **Código:** `sg_lib.SMATS["Metal_SG_BlackIron"]`.
- **Direção:** um valor acima, com metal mais alto (reflexo do luar marca a forma).

### 14.09 Cor chapada das flores · Tier B
- **Errado:** Leaf_SGPropBloom é um roxo uniforme em todas as flores da ilha.
- **Onde:** `A/village/CAM_SGVil_CU_Window.jpg`.
- **Código:** `sg_court.py` / `sg_village.py` (`BLOOM`).
- **Direção:** 2 tons (flor e miolo), junto com 02.04.

---

## 15 Iluminação e emissive

### 15.01 [CRÍTICO] Caixas inteiras em Neon quente · Tier B
- **Errado:** lanternas, lanternas góticas, velas-cilindro, tochas-cone e janelas: o objeto inteiro emite, e a forma
  some no bloom. É a peça simples escondida por emissive.
- **Onde:** `J/AU_Lantern.jpg`, `J/AU_Fountain.jpg`, `F/CU_CraftDoor.jpg`.
- **Código:** `sg_emblem.lantern_head()`, `sg_summon.gothic_lantern()`, `sg_dungeon.torch()`, `sg_hall.ironwork()`,
  `sg_village.window()`.
- **Direção:** a regra é que SÓ A CHAMA emite, e o invólucro ilumina por luz real ou pelo reflexo (12.01, 12.09).

### 15.02 [CRÍTICO] Magenta estourando a alquimia · Tier A
- **Errado:** o líquido do frasco (VDEEP), o cristal do lustre (CRYS), as poções acesas e o fio de energia estouram no
  bloom do Roblox. A alquimia lê como boate magenta, e o caldeirão e o frasco perdem forma.
- **Onde:** `F/Craft.jpg`, `F/CraftInterior.jpg`, `F/CU_CraftDoor.jpg`, `F/CU_Shelf.jpg`.
- **Código:** `sg_craft.py` (`VDEEP`, `CRYS` em `flask()`, `chandelier()`, `cauldron()`, `LIQ`).
- **Direção:** um único foco violeta (a poção do caldeirão, emissão ≤1,0). Tudo o mais abaixo de 0,6 ou sem emissão.

### 15.03 Runas e glifos em Neon · Tier A
- **Errado:** obeliscos, círculo mágico, piso das salas da dungeon e ombreiras. Glifo emissivo lê letreiro, não
  gravação.
- **Onde:** `F/CU_CastleWindow.jpg`, `F/CU_CraftTable.jpg`, `A/dungeon/CAM_SGDun_R3Exit.jpg`.
- **Código:** `sg_court.obelisk()`, `sg_craft.magic_circle()`, `sg_dungeon.floor_runes()`.
- **Direção:** entalhe (rebaixo) com fundo de emissão ≤0,3.

### 15.04 Linhas de energia nas arestas da coroa · Tier A
- Ver 03.14 (`sg_castle.glow_edges()`).

### 15.05 Crescentes do emblema: ~50 pontos brilhando · Tier B
- **Errado:** todo emblema leva o crescente em SG_Rune_Glow ou VioletSoft. Com ~50 emblemas, o crescente vira confete
  violeta em todas as vistas.
- **Onde:** `F/PlayerHeight_Entry.jpg`, `F/PlayerHeight_Castle.jpg`, `A/hall/CAM_SGHall_West.jpg`.
- **Código:** `sg_emblem.py: _emblem_geo()` (`glow=MOON`).
- **Direção:** crescente emissivo SÓ no emblema monumental da fachada, no trono e no caldeirão. Nos estandartes e nas
  placas, crescente em Stone_SG_Violet sem emissão.

### 15.06 Estrela do summon estourada · Tier A
- Ver 10.06.

### 15.07 Brasa do caldeirão em disco · Tier A
- Ver 07.04.

---

## 16 Harmonia global

### 16.01 [CRÍTICO] Bevel sem linguagem · global
- **Errado:** a maioria das peças perto do jogador sai com `bevel=0.0`:
  - `lantern_head`, `lantern_post`;
  - `hooded_figure`, `obelisk`;
  - `iron_arch`, `gothic_lantern`;
  - pilastras do salão e degraus.
  Outras saem com 0,08 a 0,15 (casas, pórticos). No Roblox, aresta viva ao lado de aresta boleada lê kitbash.
- **Onde:** `J/AU_GuardFront.jpg` (lanterna viva ao lado de pedra chanfrada), `J/AU_Lantern.jpg`.
- **Código:** todos os módulos (parâmetro `bevel` de `mb.box` e `mb.cyl`).
- **Direção:** tabela única:

  | Peça | Bevel |
  |---|---|
  | Cantaria | 0,1 |
  | Móveis e props de 1 a 3 studs | 0,05 |
  | Metal fino | 0 |
  | Metal fundido | 0,03 |

  Aplicar nos helpers do kit (12.x) primeiro.

### 16.02 [CRÍTICO] Emblema repetido demais · global
- **Errado:** ~50 emblemas visíveis:
  - ~25 estandartes;
  - ~15 placas;
  - 2 medalhões de piso;
  - 6 chaves de abóbada;
  - fachada, trono, caldeirão (×2), tímpanos das salas.
  Da porta do castelo se contam mais de 10 no mesmo quadro. O símbolo deixa de ser marca e vira papel de parede,
  sinal clássico de arte de IA.
- **Onde:** `F/CU_CastleDoor.jpg`, `A/CAM_SGCourt_PH_Gate.jpg`, `F/PlayerHeight_Entry.jpg`.
- **Código:** chamadores de `sg_emblem.banner/plaque/emblem/emblem_flat` e `sg_hall.flat_emblem` (11 módulos).
- **Direção:** meta de no máximo 4 emblemas em qualquer quadro de jogador. Cortes sugeridos:
  - estandartes do salão nas pilastras;
  - placas dos obeliscos, dos pedestais e do lintel B;
  - chaves de abóbada, exceto a central;
  - tímpanos das salas da dungeon;
  - metade dos estandartes da entrada.

### 16.03 [CRÍTICO] Primitivas empilhadas como gramática · global
- **Errado:** caixa + caixa + pirâmide de 4 lados (+ bola de prata) é o desenho de postes, pilaretes, marcos, pilares,
  pináculos, muretas, obeliscos e lanternas. Mais de 15 props com a mesma frase.
- **Onde:** `A/entry/CAM_SGEnt_Back.jpg`, `F/Dungeon.jpg`, `A/summon/CAM_SGSum_PlayerWalk.jpg`.
- **Código:** `sg_lib.spire` + `mb.box` em sg_entry, sg_exit, sg_court, sg_summon, sg_dungeon, sg_castle.
- **Direção:** kit de 5 peças desenhadas (base moldurada, fuste chanfrado, capitel, remate bola e remate pináculo) em
  perfis de torno, usadas por todos (12.12).

### 16.04 Ritmo métrico · global
- **Errado:**
  - Lanternas a cada 5,6/11/12/14.
  - Mísulas a cada 2,6/3,2.
  - Ameias em cada 2.
  - Colunelos a cada 1,15.
  - Nichos iguais.
  Tudo em passo constante: distribuição uniforme sem hierarquia.
- **Onde:** `A/_folha_entry.jpg`, `A/castle/CAM_SGCas_PlayerHeight_EastGap.jpg`, `A/hall/CAM_SGHall_West.jpg`.
- **Código:** constantes de passo em sg_entry, sg_exit, sg_castle.muralha, sg_terrain.corbels, sg_summon.gothic_rail e
  sg_hall.walls.
- **Direção:** ritmo A-B-A (2 elementos alternados) e ênfase nos nós (portão, eixo, canto). Nunca a mesma peça em
  passo fixo por mais de 20 studs.

### 16.05 Hero menos acabado que o Tier B · global
- **Errado:** de perto as casas (enxaimel, janelas, beirais) têm mais estrutura que o castelo (paredes lisas,
  pórtico-caixa), a alquimia (lata lisa) e a dungeon (pneus e blocos). A hierarquia de acabamento está invertida.
- **Onde:** comparar `A/village/CAM_SGVil_CU_Gable.jpg` com `A/castle/CAM_SGCas_PlayerHeight_WestAlley.jpg` e
  `J/AU_CraftBase.jpg`.
- **Direção:** a ordem de correção deste documento (castelo, alquimia e dungeon nos setores 03 a 09) já ataca isso.
  Priorizar o que está a menos de 10 studs das rotas.

### 16.06 Saturação: neon violeta, neon amarelo e ouro saturado contra a paleta fria · global
- **Errado:** a paleta aprovada é pedra fria dessaturada com acento violeta. No jogo dominam amarelo Neon (lanternas),
  magenta (alquimia, dungeon) e laranja saturado (ouro).
- **Onde:** `F/finesse_jogo_gerais.jpg`.
- **Direção:** 15.01, 15.02 e 14.04 juntos.

### 16.07 Segundo e terceiro sistemas de símbolos · global
- **Errado:** estrelas (summon), pentagrama (VFX do salão), runas diferentes (obeliscos, dungeon e círculo mágico com
  3 alfabetos) e o frasco (alquimia).
- **Onde:** `A/summon/CAM_SGSum_PlayerPad.jpg`, `F/PlayerHeight_MiningHall.jpg`, `F/CU_CraftTable.jpg`.
- **Direção:**
  - Um alfabeto de runas só.
  - Estrela só na função gacha.
  - Frasco só na fachada da alquimia.
  - Pentagrama fora.

### 16.08 Filler · global
- **Errado:**
  - Bolinhas de prata em icosfera no topo de tudo (`mb.ico(..., SILVER, 1)` em pilaretes, trono, arcos e pináculos).
  - Flores-gema.
  - Floreiras de chão em toda casa.
  - Dentes de grade soltos.
  - "Ticks" de moldura de portal.
  Detalhe sem função, espalhado por igual.
- **Onde:** `A/hall/CAM_SGHall_Throne.jpg`, `A/village/CAM_SGVil_Shop.jpg`.
- **Direção:** tirar antes de acrescentar. Cada remate tem que ser uma peça do kit ou nada.

### 16.09 Escala · global
- **Errado:**
  - Lanterna no poste com ~3,3 de altura; lanterna de pedestal com ~5,4 (tamanho do avatar).
  - Postes do círculo da alquimia com a cabeça a 5.
  - Pedestal-lanterna mais alto que o parapeito que o sustenta.
  Contra a régua do brief (lanterna de 1,5 a 2,5).
- **Onde:** `J/AU_GuardFront.jpg`, `F/CU_CraftTable.jpg`, `A/entry/CAM_SGEnt_PlayerBridge.jpg`.
- **Direção:** escala 0,7 no kit de lanterna (12.01) e pedestais ≤ 3,5.

---

## Resumo

### Contagem por setor

| Setor | Itens | [CRÍTICO] |
|---|---:|---:|
| 01 Entrada + praça | 18 | 11 |
| 02 Vila | 14 | 7 |
| 03 Castelo exterior | 18 | 8 |
| 04 Castelo interior | 6 | 3 |
| 05 Mining Hall (bordas) | 7 | 1 |
| 06 Alquimia exterior | 8 | 3 |
| 07 Alquimia hero props | 9 | 6 |
| 08 Alquimia interior/biblioteca | 9 | 1 |
| 09 Dungeon | 13 | 7 |
| 10 Summon | 7 | 3 |
| 11 Portões/pontes | 7 (+1 remissão) | 1 |
| 12 Props globais | 12 | 6 |
| 13 Terreno/background | 9 | 2 |
| 14 Materiais | 9 | 3 |
| 15 Iluminação/emissive | 7 | 2 |
| 16 Harmonia global | 9 | 3 |
| **Total** | **162** | **67** |

Alguns itens são remissões entre setores (o mesmo asset visto em outra zona). Contam uma vez só no conserto.

As 5 funções compartilhadas cobrem sozinhas cerca de 40% dos críticos:

| Função | Cobre |
|---|---|
| `sg_emblem.lantern_head` e `lantern_post` | ~90 lanternas e ~20 postes |
| `sg_court.hooded_figure` | 2 guardas e a estátua da fonte |
| `sg_emblem.banner` | ~25 estandartes |
| `sg_lib.plan_stair` → `fm_parts.stairs` | todas as escadas do plano |
| `sg_terrain.parapet` e `masonry` | todas as bordas e arrimos |

### Os 10 piores

1. **Guardas/estátuas do pátio e da fonte, com as espadas** (`sg_court.hooded_figure`, `statue`). Cone de bruxa,
   vigas coladas como pregas, mãos-caixa, espada de caixa e salsicha. É o boneco inflável citado, repetido em 3
   lugares.
2. **Lanterna da ordem, o cubo amarelo** (`sg_emblem.lantern_head`, e `lantern_post` com 3 caixas empilhadas). Cerca
   de 90 instâncias. O Neon inteiro engole a forma, a escala é de avatar e o ritmo forma cerca de luz.
3. **Frasco gigante e remates alquímicos** (`sg_craft.flask`, `energy_rings`, `finial`). No jogo: bolha magenta sem
   vidro, garras de viga com bola, anéis sem fixação, bolas de 8 lados com cinta.
4. **Câmaras de vidro externas, o jarro cinza** (`sg_craft.lab_tanks`). No jogo, lata cinza opaca com faixas.
5. **Exterior da alquimia** (`sg_craft.shell`, `portal`, `dome`). Parede de 24 planos lisos até 9,3, empena de
   papelão colada no domo com a nervura atravessando, pórtico-caixa, domo facetado.
6. **Paredes, contrafortes, pináculos e muralha do castelo na altura do jogador** (`sg_castle.nave`, `muralha`,
   `SL.spire`). Planos lisos no Roblox, arcobotante de viga quadrada, ~40 pináculos-lápis iguais. O hero está menos
   acabado que as casas.
7. **Escadas e parapeitos do plano** (`sg_entry.stair`, `stair_wall`, `parapet_run`, `sg_lib.plan_stair`,
   `sg_terrain.parapet`). Degraus-laje sem pedra, banzos-rampa lisos, muretas-viga. É a escada e a muralha de
   blockout em todo trajeto.
8. **Fonte e piso da praça** (`sg_village.plaza`, `sg_props.bench`). Taças de cilindros empilhados, água azul
   plástica, piso liso com fitas e "trilho" preto, bancos de laje sobre blocos.
9. **Massa de rocha e ruína da dungeon** (`sg_dungeon.strata_rock`, `cave_mouth`, `mouth_lining`, `rubble`, `glyph`).
   Pilha de pneus, cantaria de blocos de brinquedo em tom errado, runas "X" e "↑", entulho de caixas.
10. **Emissive escondendo forma na alquimia** (`sg_craft.chandelier`, `circle_lanterns`, `cauldron` (brasa),
    `magic_circle`, frascos acesos). Cristal magenta de 4 studs dominando o herói, dois postes-cubo na frente do
    caldeirão, poça violeta embaixo, glifos de estacionamento.

### Ordem de ataque sugerida (maior ganho por hora)

1. **Kit compartilhado primeiro:** lanterna e poste (12.01/12.02), remates (12.12), kit de vela (12.09), estandarte
   (12.05), `hooded_figure` e espada (03.01/03.02), escada e parapeito (01.01/01.03, 13.05/13.06). Poucas funções
   mudam dezenas de instâncias.
2. **Cortes que só removem:**
   - emblemas (16.02) e lanternas (12.04);
   - `glow_edges` (03.14);
   - postes do círculo da alquimia (07.06) e poste na frente da estátua (03.04);
   - fio da praça (01.11);
   - floreiras de chão (02.04).

   É o ganho imediato, sem modelagem.
3. **Depois, os heróis por setor, na ordem deste documento:** alquimia (06/07), castelo (03/04), dungeon (09), praça
   e entrada (01).
