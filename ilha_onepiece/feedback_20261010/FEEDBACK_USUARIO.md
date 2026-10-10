# Ilha 5 Wano: feedback do usuário depois de jogar (10/10/2026)

O usuário jogou a versão implementada (export 37998c7c) e **reprovou o conjunto**.

Material de apoio nesta pasta:
- 15 capturas, de `01_` a `15_`;
- 3 vídeos em `C:\Users\lucas\Videos\Roblox\Roblox-2026-10-10T01_0*.mp4`;
- folhas de contato dos vídeos em `frames/`.

## Texto do usuário (literal)
> a ilha de wanno na esta de meu agrado, os modelos da casas estao feios, mal projetados e vila e caminho mal projetados, o mesmo se aplica ao modelo do palcio dcentral e a arvore e as arvores menores tambem, lugares com vãos, ponte dentro da calçada, pequenas estruturas mal modeladsas, lugares com chao mas que caimos para dentro do modelo, area de navegaçlão fraca, so os barcos porem sem dinamica, sem aquela sensaçao de estar em um abiente de embarcaçao de verdade, o moelo de invocaçao sem tema nenhum de one piece, o pequeno vilarejo ao lado da invocaçoes com modelos mal feitos , mal organixados feitos somente para ocupar espaço com ammontanha de tras dando para cair dentro dela, as estruturas estao sem vida por dentro estrutura em uma montanha sem necessidade e feia caminhos do chao mal feito e deixe atmosfera da ilha igual a da ultima foto de referencia de awano ceu meio rosado flores e as arvores soltando particulas de flores de cerejeras postes de luzes feiose xecesso de bandeiras sem necessidade

## Itens (numerados para rastrear)
| # | Item | Evidência |
|---|---|---|
| U1 | **Casas feias e mal projetadas.** O kit inteiro (`op_kit.house`, presets C1…ESQ, famílias B/C) está reprovado, inclusive o trecho M2. | 01, 02, 09 |
| U2 | **Vila e caminhos mal projetados.** Ruas, lajes e quintais de terra formam uma malha sem desenho e o chão é mal feito. | 02, 11, vídeo 3 |
| U3 | **Palácio (castelo) feio.** | 03, 14 |
| U4 | **Árvore monumental feia**, assim como as árvores menores (copas facetadas genéricas, cerejeiras em blocos). | 03, 04 |
| U5 | **Vãos** (frestas e buracos). | vídeos |
| U6 | **Ponte dentro da calçada:** a ponte do canal está apoiada sobre o piso, não vence o canal entre margens. | 05 |
| U7 | **Pequenas estruturas mal modeladas** (poço, postes, etc.). | 06, 13 |
| U8 | **Chão aparente onde se cai para dentro do modelo**, ou seja, superfícies visuais sem colisão (montanha atrás do vilarejo NE, entre outros). | vídeos 2 e 3 |
| U9 | **Porto fraco:** "só os barcos, porém sem dinâmica, sem a sensação de estar num ambiente de embarcação de verdade". | 07, vídeo 2 |
| U10 | **Summon sem tema One Piece.** | 08 |
| U11 | **Vilarejo ao lado do Summon (NE/santuário):** modelos mal feitos e mal organizados, feitos só para ocupar espaço, e a montanha de trás deixa cair dentro dela. | 09 |
| U12 | **Estruturas sem vida por dentro.** | vídeos |
| U13 | **Estrutura numa montanha sem necessidade e feia** (provável: o pagode no pilar, e talvez o yagura sobre o muro do porto). | 10, 07 |
| U14 | **Atmosfera igual à última referência** (`ref/ref_03_atmosfera_wano_anime.jpg`, cópia `12_`): céu meio rosado, flores e árvores soltando partículas de pétalas de cerejeira. | 12 |
| U15 | **Postes de luz feios.** | 13 |
| U16 | **Excesso de bandeiras sem necessidade.** | 14, 08 |

## Leitura do lead
- **Causa da reprovação:** o resultado ainda lê como "procedural de blocos". As casas são caixas com telhado aplicado e as árvores são esferas facetadas. Os caminhos são retângulos de laje sobre grama, com quintais de terra recortados.
- **Ref_03 (Flower Capital do anime):** uma avenida larga e reta leva ao castelo sobre o rochedo-árvore, com quarteirões densos de telhados escalonados coloridos (azul, verde-água, vermelho, roxo). Os telhados se sobrepõem em camadas e o céu é rosa-lilás com pétalas no ar.
- **O que preservar:** os sistemas e contratos que funcionaram no Play — âncora, encaixe, praça de mineração, 70 minérios, Summon (núcleo AMS), portão OPM, scripts `OnePieceIsland`/`CeuWano`, 60 fps.

## Rodada 2: resposta do usuário ao gate V2-1 (10/10)
> modelos das arvores de decoraçao bem fracas faltam amor em sua composiçao precis amelhorar elas, as cas melhoraram, porem os modelos estao vindo dentro um do outro, as pontes e laternam mehloram, e o caminho esta bom, porem o predio principal seu conceito ainda esta pouco fraco, paredes lisas sem presença, suas montanhanhas trabem precisamde um acabamento melhor, a arvbore grande melhorou abstante porem suas folhas precisam melhorar e voce nao chegou a mexer no porto ainda

| # | Item | Estado |
|---|---|---|
| G1 | Árvores de decoração fracas, sem cuidado na composição | refazer (cerejeira, pinheiro, larga, moita) |
| G2 | Casas melhoraram, mas os modelos entram um dentro do outro | APROVADAS com correção de interpenetração |
| G3 | Pontes e lanternas melhoraram; caminho está bom | APROVADO |
| G4 | Castelo: conceito ainda fraco, paredes lisas sem presença | refazer as paredes e a presença do castelo |
| G5 | Montanhas precisam de acabamento melhor | terreno V2-3 |
| G6 | Árvore grande melhorou bastante, mas as folhas precisam melhorar | refazer as almofadas de folhagem |
| G7 | "não chegou a mexer no porto" | o porto V2 existia, mas as imagens não tinham sido enviadas; agora foram |
