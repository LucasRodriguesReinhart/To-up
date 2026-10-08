# Lobby WOLFBERG - Vila da Forja: direcao de projeto (2026-10-08)

Referencia unica: `ref/wolfberg_referencia_usuario.jpg` (vila medieval de forja, ensolarada, estilo Roblox).
Pedido do usuario (08/10, com 6 capturas da V4 da Vila Medieval): organizacao ruim, visual pobre, coisas sem
sentido (bancos na frente dos portais, ranking dentro de casa), VFX de atmosfera que nao combina com a era medieval,
loja de mochilas mal feita por fora e por dentro, paisagem de fundo pobre. "Trabalhe como engenheiro, arquiteto e
designer de interiores."

## 1. Diagnostico da V4 (o que nao pode voltar)
| Problema visto nas capturas | Causa | Decisao |
|---|---|---|
| Ranking (2 paineis de 25 studs) atravessando uma casa | palco do ranking encostado no quarteirao, sem edificio proprio | Mural dos Campeoes: loggia de pedra propria, a oeste da praca, aberta para ela |
| Bancos espalhados na frente dos portais e no meio da praca | props soltos sem regra de posicao | mobiliario so encostado em bordas (muros, fachadas, canteiros); nada no raio de 12 studs de um portal |
| Praca de lajes gigantes palidas, vazia | material sem textura; nada que de escala | paralelepipedo pequeno (textura 6 studs/tile), fonte, barracas, carroca, canteiros, postes |
| Loja: interior escuro, NPC em cima de uma viga, prateleiras com potinhos | interior improvisado | loja projetada (balcao, mochilas expostas em ganchos/manequins/prateleiras, vitrine, luz pela janela) |
| Canal cortando o eixo, ponte no meio do caminho, roda d'agua | planta copiada do hub do Anime Expeditions | sem canal: vila de UM nivel, UMA praca, UM eixo |
| Fundo: piramides cinzas, pinheiros-cone | pano de fundo de blockout | cordilheira com cristas e neve em 2 planos, colinas com campos e bosques, lago em volta |
| Atmosfera generica e clara demais | perfil de luz neutro, VFX de portal/ "sci-fi" | sol quente de fim de manha, neblina leve e quente, fumaca das chamines, fogo nas fornalhas, lanternas, estandartes |

## 2. Partido
- **Um eixo (X = 0), uma praca.** Norte: Forja do Ignis (marco). Sul: cerca + placa de boas-vindas, rua sul, portao e
  ponte reta ate a Ilha 1. Quem nasce (spawn em (0, 32), olhando -Z) ve EXATAMENTE a composicao da referencia: placa e
  cerca atras, praca a frente, forja com as duas fornalhas acesas ao fundo, montanhas por cima dos telhados.
- **Leste da praca:** Loja de Mochilas (predio proprio com vitrine, porta para a praca, interior projetado).
- **Oeste da praca:** Mural dos Campeoes (GlobalTop100 em loggia de pedra com telhado de madeira).
- **Sudoeste:** rua curta ate o Caminho dos Mundos (os 6 portais aprovados em semicirculo, terraco de pedra, poste
  de setas, lanternas, estandartes; sem bancos).
- **Sul:** rua com casas dos dois lados, larguinho do poco, portao de duas torres, ponte de pedra reta.
- **Tudo a <= 10 s a pe do spawn**: Ignis 78 studs, loja 70, campeoes 50, portais ~150 (9 s), ponte 110.
- Volumes de referencia: casas de 2-3 andares (12-16 de fachada), forja 52 x 40 com beiral a 36 (o golem tem 24 de
  altura; vao central livre ate 33), chamines a 70.

## 3. Programa e contratos (nada muda no codigo do jogo)
| Funcao | Onde | Contrato |
|---|---|---|
| Spawn | (0, 7, 32) olhando -Z | `LobbyLayout.Spawn`, `Mystical Spawn Point.SpawnLobby` |
| Correio | (-10, 7, 37) | `workspace.MailBox`, prompt "Enviar Feedback" |
| Ignis | Root (-0.9, 7, -60.7) +Z, envoltoria livre | `workspace.NPCs.Ignis`, belly/hot_billet/LetreiroIgnis, marcadores NPC_/INTERACT_/PLAYER_INTERACT_Ignis |
| Loja | predio x 54..80, z -22..4; NPC (72, -9) olha -X; jogador (62, -9) | `npc vendedor `, `LojaPrompt`, `LojaMochilas.PadLoja`, `LobbyLayout.Shop/ShopFacing` |
| Ranking | origem (-58, 7.6, -9) olhando +X | `LOBBY_FORJA.GlobalTop100` (PivotTo pela montagem), atributo Top100Origin |
| Portais | COURT_C (-134, 62), r 56, Naruto ao sul ... OPM ao norte | `Santuario.Portal1..6` com Disco/AreaId (montagem) |
| Saida | portao (0, 142), ponte x 0 de z 148 a 222, pousa em (0, 6, 222) | `ISLE_LINK` Ilha 1 (piso 6), marcadores LOBBY_GATE_Ilha1 / ISLE_LINK_Area1 |
| Raiz | Model `LOBBY_FORJA`, `LobbyRevision`, `GAMEPLAY_MARKERS`, `LOBBY_FORJA_Servidor` (rede de quedas) | export_wb.py (copia configurada do export_vm; export_roblox so leitura) |

## 4. Kit (wb_kit.py) - tudo com textura colorida (SurfaceAppearance, alpha 1), nada liso
- **Forja do Ignis:** terreo de pedra (cantaria clara com quinas escuras), andar enxaimel ocre com vigas escuras,
  telhado de telha vermelho-terra com 2 aguas-furtadas, 2 chamines de pedra com fumaca, 2 fornalhas de pedra em arco
  abertas para a praca (fogo, brasa, luz), vao central com colunas de pedra e vigas grossas, letreiro de madeira
  "FORJA DE WOLFBERG" com bigorna pintada, bancada de ferramentas, barris de tempera, pilha de lenha, carvao, lingotes.
- **Casas enxaimel:** base de pedra, reboco creme/ocre com vigas (montantes, travessas, X e diagonais), andar em
  balanco sobre misulas, janelas com caixilho e floreiras, portas em arco com ferragens, telhado ingreme com cumeeira,
  aguas-furtadas, chamines; placas penduradas (taverna, padaria, albergue, estabulo). 2-3 andares, 6 variacoes.
- **Loja de Mochilas (interior projetado):** vitrine em bay-window com 3 mochilas, toldo listrado, placa com mochila;
  dentro: piso de tabuas, tapete, balcao em L com livro-caixa e balanca, parede de fundo com 3 prateleiras de
  mochilas (8 cores), parede lateral com ganchos e 2 manequins de madeira com mochila, bau aberto, rolos de couro,
  lampiao e candelabro, janela lateral com luz do dia, escada para o mezanino (so cenografia).
- **Mural dos Campeoes:** muro de pedra 62 x 31, loggia com 4 colunas de pedra e telhado de madeira, palco de 2
  degraus, 2 braseiros, estandartes "CAMPEOES" vermelhos e azuis, escudos de madeira.
- **Praca:** paralelepipedo (textura cobble 6 studs/tile) com meio-fio, canteiros de grama e flores, fonte octogonal
  de pedra com 2 taças e agua, 3 barracas de mercado com toldo listrado (vermelho, azul, verde) e mercadorias, carroca
  com barris, barris e caixotes encostados nas fachadas, postes de ferro com lanterna, cerca de madeira com placa de
  boas-vindas de 2 faces, poste de direcoes, correio.
- **Caminho dos Mundos:** disco de paralelepipedo, terraco de cantaria com 2 degraus, postes com lanternas entre os
  portais, 6 estandartes com a cor de cada mundo, poste "CAMINHO DOS MUNDOS" com 6 setas.
- **Portao e ponte:** 2 torres de pedra com telhado conico, arco com portas de madeira abertas, ponte de pedra com 3
  arcos, guarda-corpo de madeira e lanternas.
- **Paisagem:** plato de grama com margem rochosa, lago em volta, margem distante com colinas de campos (faixas
  lavradas), bosques de pinheiro e carvalho, 2 planos de montanhas com cristas e neve, nuvens (Terrain.Clouds).

## 5. Atmosfera e VFX (era medieval)
- Sol quente de fim de manha (ClockTime ~10.8), sombras suaves, `OutdoorAmbient` quente, `Atmosphere` leve e quente
  (Density 0.3, Color creme-azulado, Haze 1.2), bloom baixo, `ColorCorrection` levemente quente e saturada.
- Particulas: fumaca pesada das 2 chamines da forja, fumaca fina em 5 chamines de casas, fogo + brasas nas 2
  fornalhas (com PointLight laranja e tremor), respingo da fonte, folhas caindo dos carvalhos, poeira na luz da
  forja. Lanternas NightOnly (vermelho-amarelo). Nada de neon, laser, holograma ou listras de aviso fora dos portais.

## 6. Entregas (cada uma mostrada ao usuario ANTES de seguir)
1. Planta esquematica + amostra (praca + forja + loja + taverna + cerca/placa + fonte + barracas) na camera da ref.
2. Kit completo + vila inteira em Blender (renders nas cameras de QA + aereas) + QA das rotas.
3. Export (`export_wb.py`) + import na copia AMS_Lobby_Champions_Avaliacao + montagem + Play + capturas.
Regras: nunca salvar o place; nao editar `forja_mineradora/`, as ilhas, nem `vila_medieval/`; avisar as sessoes
antes do Studio; subagentes sem Studio/computer-use.

## 7. Licoes do video de referencia do usuario (08/10, `ref/video/_contato.jpg`: lobby de ruinas com atmosfera verde)
O que faz aquele lobby parecer "bom" e o que vira regra aqui (traduzido para o tema medieval, sem copiar o tema):
- **Atmosfera unica e forte**: neblina, degrade de cor e bloom afinados num SO clima. Aqui: fim de manha dourado,
  neblina quente leve, raios de sol, bloom so no fogo/lanternas (wb_lights.LOBBY_PROFILE).
- **Escala dramatica ao fundo**: ossos/arcos gigantes enquadram o hub. Aqui: cordilheira mais perto e mais alta,
  penhascos de rocha na borda do plato, pinheiros gigantes, chamines altas da forja, fumaca.
- **Linguagem de piso**: lajes grandes com juntas e musgo, aneis concentricos no centro, linhas que levam as estacoes.
  Aqui: EIXO principal em lajeado claro de pedras grandes (textura wb_flag) com borda escura, medalhao circular no
  centro da praca (anel de bronze + bigorna), "tapetes" circulares de bronze diante de cada estacao.
- **Estacoes sinalizadas**: cada funcao tem placa flutuante com icone e um anel no chao onde o jogador para. Aqui:
  BillboardGui "LOJA DE MOCHILAS / CAMPEOES / CAMINHO DOS MUNDOS / CORREIO" (montar, marcadores LETREIRO_*) + o
  LetreiroIgnis que o jogo ja tem + anel de bronze no PLAYER_INTERACT de cada estacao.
- **Props agrupados nas estacoes** (caixotes, barris, ferramentas) e nunca soltos no meio do caminho.
- **Relevo**: plataformas com degraus e rampas. Aqui: palco do Mural (+0,6), terraco dos portais (+1,2), soleira da
  loja (+0,4), ponte descendo ate a ilha; o chao diante do Ignis segue plano na cota 7 (contrato).
