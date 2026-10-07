# ============================================================
# ANIME MINING SIMULATOR (AMS)
# ILHA 4 — DEMON SLAYER
# MASTER PRODUCTION PROMPT PARA CLAUDE
# BLENDER + ROBLOX STUDIO
# ============================================================

## MISSÃO

Sua missão é construir e integrar a ilha DEMON SLAYER do Anime Mining Simulator utilizando como referência principal as imagens aprovadas fornecidas junto com este prompt.

Você deve atuar simultaneamente como:

- Lead Environment Artist
- Senior Level Designer
- Senior 3D Environment Modeler
- Senior Technical Artist
- Roblox World Builder
- Lighting Artist
- Material Artist
- VFX Artist
- Optimization Artist
- QA visual e funcional

O usuário irá avaliar APENAS o resultado final.

Trabalhe de forma autônoma.

Não peça aprovação para microdecisões.

Não pare depois da primeira versão aceitável.

Não entregue apenas plano, relatório ou conceito.

Você deve executar o trabalho real nas ferramentas disponíveis.

Use, quando realmente útil:

- Blender
- Blender Python
- bpy
- bmesh
- Geometry Nodes
- scripts
- terminal
- MCP
- Roblox Studio
- Play Test
- profiling
- screenshots
- ferramentas auxiliares realmente disponíveis

Não invente ferramentas inexistentes.

# ============================================================
# 1. AUDITE O PROJETO EXISTENTE ANTES DE CONSTRUIR
# ============================================================

Antes de modelar, analise o estado real do projeto.

Estude:

- Lobby
- Naruto
- Dragon Ball
- Shadow Garden
- escala
- bridges
- island anchors
- purchase gates
- sistema de mineração
- sistema de Summon
- materiais
- conventions de assets
- collisions
- iluminação
- VFX
- export pipeline Blender → Roblox
- organização de arquivos
- scripts
- otimizações já realizadas

NÃO reconstrua sistemas maduros.

Reutilize:

PIPELINE
+
ESCALA
+
CONVENÇÕES
+
SISTEMAS.

Mas NÃO reutilize:

LAYOUT
+
COMPOSIÇÃO
+
ARQUITETURA
+
GEOGRAFIA.

Demon Slayer precisa possuir identidade própria.

# ============================================================
# 2. REFERÊNCIAS VISUAIS APROVADAS
# ============================================================

As imagens fornecidas junto deste prompt representam VISTAS DIFERENTES DO MESMO MAPA.

Trate todas elas como:

ART DIRECTION
+
SPATIAL INTENT
+
QUALITY TARGET.

Não trate cada imagem como uma ilha diferente.

Reconstrua UMA ÚNICA cena 3D coerente que explique o maior número possível de elementos vistos nos diferentes ângulos.

Quando as imagens divergirem:

1. preserve a intenção geral;
2. preserve a composição aprovada;
3. resolva a geometria de forma coerente;
4. priorize gameplay;
5. preserve a identidade visual.

As imagens NÃO são plantas arquitetônicas exatas.

Não copie erros impossíveis de perspectiva.

# ============================================================
# 3. DIREÇÃO FUNDAMENTAL
# ============================================================

NÃO quero:

- uma ilha circular;
- uma arena circular perfeita;
- Naruto com wisteria;
- Shadow Garden japonês;
- uma mina temática de Demon Slayer;
- uma pedreira;
- um mapa de mineração visualmente industrial;
- sub-ilhas usadas apenas para preencher o céu;
- cachoeiras usadas apenas como filler;
- torii a cada poucos studs;
- glicínia em toda superfície;
- construções espalhadas sem lógica;
- mapa simétrico demais;
- mapa com cara de concept art genérica.

Quero:

# UM TERRITÓRIO DE DEMON SLAYER NO QUAL O JOGADOR TAMBÉM MINERA.

A mineração é GAMEPLAY.

Ela NÃO define a estética do mapa.

# ============================================================
# 4. IDENTIDADE VISUAL
# ============================================================

A direção deve combinar:

- vila japonesa montanhosa
- influência da era Taishō
- caminhos estreitos e naturais
- casas tradicionais simples
- madeira escura
- reboco claro
- telhados japoneses escuros
- lanternas quentes
- bamboo
- wisteria usada seletivamente
- névoa
- noite azulada
- floresta montanhosa
- grandes árvores stylized
- stone retaining walls
- pontes pequenas
- atmosfera inspirada em ambientes de Demon Slayer / Project Slayers

A ilha deve transmitir:

MISTÉRIO
+
TRADIÇÃO
+
PERIGO
+
BELEZA
+
ISOLAMENTO
+
PROGRESSÃO.

Não dependa de símbolos gigantes para comunicar Demon Slayer.

A identidade deve vir principalmente de:

- arquitetura
- atmosfera
- composição
- iluminação
- vegetação
- geografia
- paleta

# ============================================================
# 5. MAPA QUE CONTA UMA HISTÓRIA
# ============================================================

A ilha não pode parecer:

“plataforma + sistemas”.

Ela deve parecer uma pequena jornada.

Fluxo principal:

SHADOW GARDEN
↓
PONTE DE TRANSIÇÃO
↓
ENTRADA DEMON SLAYER
↓
TRILHA / VILA MONTANHOSA
↓
GRANDE CLAREIRA DE GAMEPLAY
↓
SUBIDA
↓
FORJA / LANDMARK PRINCIPAL
↓
CAMINHO DE CONTINUAÇÃO
↓
GATE / PONTE PARA ONE PIECE

Com o Summon como rota lateral claramente reconhecível.

O jogador deve sentir que está:

# ATRAVESSANDO E SUBINDO UM TERRITÓRIO.

Não chegando numa arena isolada.

# ============================================================
# 6. GEOGRAFIA
# ============================================================

A ilha deve possuir forma:

- irregular
- longitudinal
- quebrada por terraços
- orientada pelo caminho principal

Evite geometria radial/circular.

Use:

- cliffs controlados
- terraces
- pequenos desníveis
- retaining walls
- escadas
- paths
- pequenos bridges
- pequenas quedas de terreno

NÃO crie dezenas de ilhas secundárias.

NÃO crie cachoeiras em toda borda.

Se houver água, use com função compositiva real.

O fundo deve possuir profundidade atmosférica sem parecer que o cenário está cheio de objetos colocados apenas para preencher vazio.

# ============================================================
# 7. ÁREA CENTRAL DE MINERAÇÃO
# ============================================================

A mineração acontece numa:

# GRANDE CLAREIRA NATURAL.

Não numa mina.

Não numa pedreira.

Não numa quarry industrial.

Não numa arena perfeitamente circular.

Essa clareira precisa ser:

- grande
- aberta
- limpa
- legível
- multiplayer-friendly
- fácil de entender
- adequada ao sistema existente de spawn de minérios

Pode possuir:

- terra
- pedra
- patches de grama
- algumas irregularidades
- poucas pedras nas bordas
- raízes
- cercas baixas em setores pontuais

O espaço principal precisa permanecer livre.

# ============================================================
# 8. REGRA ABSOLUTA — NÃO MODELE MINÉRIOS
# ============================================================

OS MINÉRIOS JÁ EXISTEM NO JOGO.

NÃO:

- modele minério
- crie novos ores
- crie crystals decorativos confundíveis com minério
- substitua modelos
- redesenhe ores
- crie MiningSystem2
- altere raridades sem necessidade

Sua responsabilidade é:

# PREPARAR O AMBIENTE PARA RECEBER O SISTEMA EXISTENTE.

Durante o blockout, se precisar:

use proxies extremamente simples e claramente temporários.

Remova todos antes da entrega.

# ============================================================
# 9. VILA
# ============================================================

A vila deve ser pequena e orgânica.

Não quero uma cidade inteira.

Use poucas construções bem trabalhadas.

Tipos possíveis:

- residência tradicional
- pequeno workshop
- storage
- pavilhão
- casa principal
- pequenas estruturas de apoio

A vila serve principalmente para:

- worldbuilding
- ambientação
- circulação
- contar a história do lugar

NÃO invente:

- quests
- upgrades
- lojas funcionais
- skill tree
- sistemas não solicitados

# ============================================================
# 10. KIT ARQUITETÔNICO
# ============================================================

Crie um kit modular de qualidade:

- foundations
- wall sections
- timber beams
- windows
- doors
- roof pieces
- roof ridges
- eaves
- porches
- stairs
- railings
- support posts
- stone bases

Depois crie variações dirigidas.

Não use:

CUBE
+
ROOF
+
WINDOW

como versão final.

As casas precisam compartilhar linguagem visual sem parecer clones.

# ============================================================
# 11. FORJA — HERO LANDMARK
# ============================================================

No nível superior da ilha deve existir uma grande FORJA.

Ela é o principal landmark ambiental.

Sua função principal é worldbuilding.

Ela deve comunicar:

- espada
- fogo
- metal
- Nichirin-inspired craftsmanship
- tradição
- trabalho artesanal
- poder

Pode possuir:

- grande furnace
- chimney
- anvil
- weapon racks
- workbenches
- heated metal
- storage
- wooden structure
- dark stone
- smoke controlado

Mas NÃO transforme toda a ilha num mapa de mineração.

A forja é um ponto narrativo e visual.

# ============================================================
# 12. SUMMON
# ============================================================

O Summon precisa preservar a identidade já aprovada do Anime Mining Simulator.

O núcleo visual deve continuar reconhecível:

STAR
+
RINGS
+
TOWER
+
ENERGY CORE.

NÃO redesenhe o sistema como uma máquina completamente diferente.

Adapte apenas:

- base
- plataforma
- materiais
- ornamentos
- entorno

Para Demon Slayer use:

- dark wood
- dark stone
- metal
- detalhes discretos de wisteria
- iluminação quente
- acentos violetas controlados

O Summon deve ficar em um platô lateral e ser visível, mas não competir com a Forja.

# ============================================================
# 13. ENTRADA VINDO DE SHADOW GARDEN
# ============================================================

Audite a âncora real da ilha anterior.

Construa Demon Slayer a partir dela.

NÃO mova Shadow Garden.

A entrada deve usar:

- bridge
- gate
- pequena mudança de materiais
- vegetation transition
- lanternas
- leitura clara de “novo mundo”

Evite transição abrupta.

# ============================================================
# 14. SAÍDA PARA ONE PIECE
# ============================================================

A próxima ilha é ONE PIECE.

Prepare:

DEMON SLAYER
↓
CAMINHO FINAL
↓
BRIDGE
↓
PURCHASE GATE
↓
NEXT ISLAND ANCHOR
↓
ONE PIECE.

A ponte deve existir de verdade.

Não coloque gate na borda sem continuação física.

Documente:

- Position
- Orientation
- Width
- Height
- ForwardVector

# ============================================================
# 15. WISTERIA
# ============================================================

Wisteria é ACCENT.

Use em poucos lugares:

- perto do Summon
- pequeno jardim
- framing de landmark
- entrada especial
- pequenas transições

NÃO use em:

- cada casa
- cada árvore
- cada parede
- toda borda
- todo cliff

A identidade de Demon Slayer NÃO depende de pintar o mapa de roxo.

# ============================================================
# 16. VEGETAÇÃO
# ============================================================

Use:

- broad stylized trees
- bamboo
- shrubs
- small grasses
- poucas árvores especiais

A vegetação deve parecer parte do ambiente e não scatter automático.

Cada cluster precisa ter intenção.

NÃO use árvores para preencher qualquer vazio.

# ============================================================
# 17. ILUMINAÇÃO
# ============================================================

Objetivo:

# NOITE LEGÍVEL.

Use:

MOONLIGHT FRIO
+
WINDOWS QUENTES
+
LANTERNAS QUENTES.

O jogador precisa enxergar:

- piso
- caminhos
- casas
- forge
- minérios oficiais
- exits
- summon

Não faça:

preto + neon.

Não use bloom para esconder geometria ruim.

# ============================================================
# 18. CRAFTSMANSHIP DESDE O PRIMEIRO ASSET
# ============================================================

Esta ilha NÃO deve receber um craftsmanship pass apenas no final.

Cada asset importante deve nascer seguindo:

SILHUETA
↓
PROPORÇÃO
↓
ESTRUTURA
↓
ENCAIXE
↓
ESPESSURA
↓
BEVEL
↓
MATERIAL
↓
DETALHE
↓
ILUMINAÇÃO.

Se um asset ainda parecer primitive + material:

REFINE.

# ============================================================
# 19. ANTI-VIBE-CODER / ANTI-AI
# ============================================================

Considere NÃO FINAL qualquer elemento que pareça:

- cubo colorido
- cilindro com detalhe
- esfera com emissive
- primitives empilhadas
- objeto inflável
- detalhe simplesmente colado
- peça sem espessura
- asset procedural não revisado
- ornamentação aleatória
- modelo feito apenas para funcionar num render distante

Não quero:

“o script conseguiu gerar a forma”.

Quero:

# “UM ARTISTA DECIDIU COMO ESSA FORMA DEVERIA SER CONSTRUÍDA.”

# ============================================================
# 20. TELHADOS
# ============================================================

A arquitetura japonesa depende muito dos telhados.

Revise:

- thickness
- ridge
- eaves
- corners
- overhang
- structural supports
- wall transitions
- intersections

Não deixe planos atravessando.

# ============================================================
# 21. PORTAS E JANELAS
# ============================================================

PORTAS:

frame
+
recess
+
thickness
+
threshold
+
hardware cues quando apropriado.

JANELAS:

frame
+
recess
+
panel/glass
+
interior light.

Não use planos emissivos colados.

# ============================================================
# 22. LANTERNAS
# ============================================================

Crie um kit de lanternas de qualidade.

Precisam possuir:

- frame
- glass
- top
- base
- support
- mounting

Não use cubos amarelos emissivos.

Faça variações:

- post
- wall
- pedestal

# ============================================================
# 23. ARMAS / ESPADAS DECORATIVAS
# ============================================================

Se usar armas:

modele corretamente.

Uma espada precisa ter:

- blade
- point
- guard
- grip
- pommel

Não faça lâmina “salsicha”.

Não use tubo/cilindro como versão final.

# ============================================================
# 24. SÍMBOLOS
# ============================================================

Emblemas importantes devem ser:

- curves limpas
- clean meshes
- thickness consistente
- bevel coerente

Não monte símbolos com Parts mal sobrepostas.

# ============================================================
# 25. CHÃO / CLAREIRA
# ============================================================

A clareira precisa parecer ambiente final sem ficar poluída.

Use:

- subtle ground variation
- dirt
- patches de grass
- stone fragments
- edge transitions
- pequenas irregularidades

Não espalhe props para preencher vazio.

O espaço vazio da área de gameplay é INTENCIONAL.

# ============================================================
# 26. STORYTELLING AMBIENTAL
# ============================================================

Cada parte do percurso deve contar um capítulo.

ENTRADA:
silenciosa, simples, misteriosa.

VILA:
habitável, tradicional, segura.

CLAREIRA:
grande espaço de gameplay.

FORJA:
calor, força, trabalho artesanal.

SUMMON:
místico e especial.

SAÍDA:
promessa do próximo mundo.

Não deixe todas as áreas com a mesma densidade visual.

# ============================================================
# 27. BLOCKOUT FIRST
# ============================================================

Antes de detalhar, construa SOMENTE:

- island mass
- entry
- village
- central clearing
- forge
- summon platform
- One Piece exit

Use materiais simples.

SEM:

- props detalhados
- vegetation pesada
- VFX final
- excesso de iluminação

# ============================================================
# 28. GATE DE QUALIDADE DO BLOCKOUT
# ============================================================

NÃO avance enquanto:

[ ] mapa não possuir fluxo claro
[ ] composição ainda parecer circular
[ ] clareira não estiver grande o suficiente
[ ] Forge não funcionar como landmark
[ ] Summon não estiver integrado
[ ] entrada Shadow Garden não estiver coerente
[ ] saída One Piece não estiver coerente
[ ] player camera não funcionar
[ ] mapa parecer simplesmente quadrado
[ ] mapa não contar uma história espacial

Se falhar:

REFaça O BLOCKOUT.

# ============================================================
# 29. CÂMERAS DE QA
# ============================================================

Crie:

CAM_DS_Entry
CAM_DS_Front
CAM_DS_Left
CAM_DS_Right
CAM_DS_Back
CAM_DS_BirdEye
CAM_DS_Clearing
CAM_DS_Village
CAM_DS_Forge
CAM_DS_Summon
CAM_DS_OnePieceGate

E versões:

PlayerHeight.

As câmeras das referências devem ser usadas como guia para validar coerência entre vistas.

# ============================================================
# 30. TESTES DE NAVEGAÇÃO
# ============================================================

Teste:

SHADOW_GATE → ENTRY
ENTRY → CLEARING
ENTRY → VILLAGE
CLEARING → FORGE
CLEARING → SUMMON
CLEARING → ONE_PIECE_GATE
FORGE → ONE_PIECE_GATE
SUMMON → CLEARING

Nenhuma rota deve depender de:

- salto estranho
- parkour
- passagem escondida
- placa gigante

# ============================================================
# 31. PLAYER-FIRST
# ============================================================

Na entrada o jogador deve:

1. entender onde está;
2. perceber o espaço de mineração;
3. reconhecer o landmark;
4. notar o Summon;
5. perceber que o mapa continua.

Não dependa de texto gigante.

Use:

- caminho
- luz
- terreno
- arquitetura
- framing
- elevação
- landmarks

para ensinar o mapa.

# ============================================================
# 32. MATERIAL PASS
# ============================================================

Principais materiais:

- plaster
- dark wood
- roof tile
- stone
- aged iron
- lantern glass
- bamboo
- vegetation

Mesmo sem luz dramática, eles precisam ser distinguíveis.

Não deixe tudo plástico.

# ============================================================
# 33. ROBLOX STYLE
# ============================================================

Continue:

- stylized
- cartoon
- mid-poly
- Roblox-friendly

NÃO faça hiper-realismo.

NÃO use detalhe fotográfico para compensar modelagem ruim.

# ============================================================
# 34. PERFORMANCE
# ============================================================

Planeje performance desde o início.

Controle:

- trees
- houses
- rocks
- materials
- lights
- transparent surfaces
- particles

Use:

instancing
+
modular kits
+
simplified collisions
+
VFX distance culling quando aplicável.

# ============================================================
# 35. QA CLOSE-UP / PLAYER HEIGHT
# ============================================================

No final, ande pelo mapa como jogador.

Inspecione:

- entrada
- lanternas
- casas
- telhados
- stairs
- forge
- doors
- windows
- summon
- gates
- bridges
- props

Se algum asset parecer:

primitive + material,

REFINE.

# ============================================================
# 36. GLOBAL HARMONY
# ============================================================

Depois do detalhe, volte para a vista geral.

Confirme:

- nenhum setor está excessivamente detalhado
- nenhum está vazio demais
- Forge domina sem exagero
- Summon é importante mas secundário
- vegetation enquadra
- clareira permanece livre
- iluminação possui hierarquia
- materiais pertencem ao mesmo jogo
- a ilha não parece montagem de assets independentes

# ============================================================
# 37. PROIBIÇÕES IMPORTANTES
# ============================================================

NÃO:

- modelar minérios
- criar sistema novo de minério
- criar island layout circular
- copiar Naruto
- copiar Dragon Ball
- copiar Shadow Garden
- espalhar wisteria
- espalhar torii
- criar dezenas de cachoeiras
- criar sub-ilhas filler
- transformar o lugar em mina/pedreira
- perder identidade do Summon AMS
- usar VFX para esconder modelagem
- deixar primitives visíveis como asset final
- inventar quests/upgrades/shops
- refazer sistemas maduros por conveniência

# ============================================================
# 38. FASES OBRIGATÓRIAS
# ============================================================

PHASE 01 — Project Audit
PHASE 02 — Reference Analysis
PHASE 03 — Blockout
PHASE 04 — Navigation
PHASE 05 — Terrain Composition
PHASE 06 — Village Kit
PHASE 07 — Forge Hero Asset
PHASE 08 — Summon Integration
PHASE 09 — One Piece Exit
PHASE 10 — Architectural Craftsmanship
PHASE 11 — Props
PHASE 12 — Vegetation
PHASE 13 — Materials
PHASE 14 — Lighting
PHASE 15 — VFX
PHASE 16 — Roblox Integration
PHASE 17 — Mining Integration
PHASE 18 — Performance
PHASE 19 — Player-height QA
PHASE 20 — Final Polish

# ============================================================
# 39. AUTOCRÍTICA OBRIGATÓRIA
# ============================================================

Pergunte regularmente:

“Isso parece Demon Slayer ou apenas Japão?”

“Isso parece um mapa realmente projetado ou uma coleção de assets?”

“A mineração está definindo demais a estética?”

“A ilha está ficando circular?”

“Estou usando cachoeiras/sub-ilhas apenas para preencher?”

“Estou usando wisteria demais?”

“O Summon continua parecendo AMS?”

“Existe asset com cara de vibe coder?”

“Algum objeto parece primitive disfarçada?”

“Estou aumentando qualidade ou apenas complexidade?”

“Este objeto sobreviveria a close-up?”

Se a resposta indicar problema:

CORRIJA.

# ============================================================
# 40. DEFINITION OF DONE
# ============================================================

Demon Slayer NÃO está pronta até:

[ ] conexão Shadow Garden funcionar
[ ] composição não ser circular
[ ] mapa contar progressão visual
[ ] clareira ser grande e funcional
[ ] nenhum minério novo ser modelado
[ ] vila possuir identidade
[ ] Forge atingir qualidade Hero
[ ] Summon preservar identidade AMS
[ ] One Piece bridge/gate estar preparado
[ ] arquitetura resistir a close-up
[ ] telhados estarem bem resolvidos
[ ] lanternas não serem cubos emissivos
[ ] vegetation estar controlada
[ ] nenhuma waterfall existir apenas por filler
[ ] não existirem sub-ilhas inúteis
[ ] materials estarem coerentes
[ ] iluminação estar legível
[ ] VFX estarem controlados
[ ] navegação funcionar
[ ] performance ser aceitável
[ ] player-height QA passar
[ ] mapa não parecer feito por IA/vibe coding

# ============================================================
# 41. REGRA FINAL
# ============================================================

NÃO BUSQUE QUALIDADE ADICIONANDO QUANTIDADE.

Não entregue:

“uma ilha cheia de coisas”.

Entregue:

# UM LUGAR QUE PARECE TER SIDO PROJETADO.

O mapa precisa possuir:

- intenção
- narrativa espacial
- identidade
- composição
- gameplay
- craftsmanship
- harmonia

Se houver conflito entre:

CONCEPT BONITA

e

JOGO BOM,

priorize o jogo e encontre uma solução igualmente bonita.

COMECE PELA AUDITORIA E PELO BLOCKOUT.

NÃO COMECE PELOS DETALHES.

NÃO MODELE MINÉRIOS.

NÃO ME PEÇA APROVAÇÃO INTERMEDIÁRIA.

EU VOU AVALIAR APENAS O RESULTADO FINAL.
