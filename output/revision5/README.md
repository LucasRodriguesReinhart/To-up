# Revisão das seis ilhas — 10/09/2026

Aplicada ao projeto aberto no Roblox Studio, Anime Mining Simulator, place 101959830085647.

## Organização e circulação

As áreas agora são destinos separados por pelo menos 1.600 studs, acessados pelos teleportes existentes. Foram removidos os corredores e as barreiras de progressão que conectavam fisicamente os mapas.

Cada ilha tem grupos próprios de relevo, arquitetura, circulação, vegetação, detalhes e água/VFX. O piso das rotas principais é contínuo, com uma via central de 22 studs, travessias de 18 e pontes de 16. Os 146 depósitos e os seis chefes mantêm os valores de progressão; os depósitos foram redistribuídos para liberar a aproximação. A invocação fica junto da chegada e o retorno ao lobby possui identificação própria.

O relevo conserva Plastic/Studs e as árvores originais do jogo. Foram adicionadas falésias estratificadas, fragmentos e fissuras, jardins, flores, lanternas, coberturas com telhas, chaminés, bancos, carga de mineração, entradas de minas e detalhes específicos de cada tema.

## Direção visual e fontes consultadas

As referências orientam a adaptação ao estilo do jogo; os mapas são composições próprias, sem promessa de reprodução exata dos cenários do anime.

| Ilha | Elementos usados | Referências |
|---|---|---|
| Vila da Folha | Telhados vermelhos, comércio, torii, monumento esculpido, vegetação e água | [Vila temática licenciada NARUTO](https://www.nijigennomori.com/en/naruto_shinobizato/), [NARUTO STORM — imagens do jogo](https://store.playstation.com/en-hk/product/HP0700-CUSA06133_00-ASIANARUTOUNST00) |
| Planeta Namekusei | Copa azul das Ajisa, água e atmosfera esverdeadas, habitações arredondadas e Capsule Corp. | [Ecossistema de Namek — Dragon Ball oficial](https://en.dragon-ball-official.com/news/01_1917.html), [Locais do manga e Kakarot](https://en.dragon-ball-official.com/news/01_536.html) |
| Monte Natagumo | Árvores altas com a folhagem original, bambus, teias, abrigo japonês, bruma e iluminação de entardecer | [Episódio 15 — Kimetsu oficial](https://kimetsu.com/anime/story/detail/?ep=15&series=risshi) |
| Jardim das Sombras | Catedral, arcadas, ruínas, eclipse e luz violeta | Imagem enviada pelo usuário; [The Eminence in Shadow — site oficial](https://shadow-garden.jp/) para o contexto visual da série |
| Grand Line | Cais, canais, fachadas claras, coberturas coloridas, embarcação e farol | [Water Seven — ONE PIECE oficial](https://one-piece.com/story/water_seven/index.html), [Water Seven em Odyssey — Bandai Namco](https://www.bandainamcoent.com/news/one-piece-odyssey-water-seven-full-story) |
| Cidade Z | Avenidas, travessias, edifícios residenciais, associação de heróis, obras e vapor | [Episódio 6 — One-Punch Man oficial](https://onepunchman-anime.net/news/archives/468), [Z-City — referência complementar](https://onepunchman.fandom.com/wiki/Z-City) |

## Som e ambiente

São músicas de ambiente do Creator Store, escolhidas para combinar com as áreas, e não as trilhas oficiais dos animes. Todas carregaram no cliente de teste, com duração não nula. O controlador faz transição de volume entre áreas e respeita o botão Som e a preferência de música nas configurações.

| Ilha | Música | Origem | Duração carregada |
|---|---|---|---|
| Vila da Folha | [Hidden Lotus Pond](https://create.roblox.com/store/asset/82061470648013) | DistrokidOfficial | 233,32 s |
| Namekusei | [Space Atmosphere](https://create.roblox.com/store/asset/1845421369) | APMOfficial | 163,13 s |
| Natagumo | [Mysterious Forest](https://create.roblox.com/store/asset/9048681794) | APMOfficial | 205,01 s |
| Jardim das Sombras | [The Forgotten Crypt](https://create.roblox.com/store/asset/131334832939011) | DistrokidOfficial | 194,52 s |
| Grand Line | [Pirate King](https://create.roblox.com/store/asset/1835322563) | APMOfficial | 146,24 s |
| Cidade Z | [Home Bound](https://create.roblox.com/store/asset/1845676363) | APMOfficial | 63,61 s |

Cada área possui iluminação e atmosfera locais. Correntezas, superfícies de água, névoa, partículas, bandeiras e pequenos pássaros são animados no cliente. Partículas e luzes distantes deixam de ser atualizadas/ativadas. O controle de efeitos do HUD também se aplica às ilhas.

## Teleporte e contenção

O servidor mantém a área autorizada de cada jogador. Limites físicos fecham laterais, fundo, frente e teto; a recuperação do servidor cobre quedas, excesso de altura e posições externas. O jogador retorna ao último ponto seguro validado. Trocar de área cancela o alvo de mineração anterior.

O destino usa PersistentPerPlayer e é solicitado antes de liberar o personagem no teleporte; a área anterior deixa de ser persistente. A transição visual acompanha esse carregamento. Modelos distantes são ocultados localmente. Implementação baseada na [documentação de streaming da Roblox](https://github.com/Roblox/creator-docs/blob/main/content/en-us/workspace/streaming/techniques.md) e em [Model:AddPersistentPlayer](https://create.roblox.com/docs/reference/engine/classes/Model/PrimaryPart).

## Verificação

- 146 depósitos acessíveis, verificados de três posições de aproximação: 438 verificações.
- 54 rotas principais e laterais calculadas com AgentCanJump=false.
- 24 tentativas de saída, quatro por ilha, recuperadas pelo servidor.
- Travessia real da chegada à ponte e à margem a WalkSpeed 18, sem saltar.
- Carregamento das seis músicas; botão Som testado; mudo preservado ao trocar de área.
- Prompt real de invocação e portal da Vila da Folha para Namekusei testados.
- Carregamento antecipado confirmado em nova sessão; apenas a ilha atual visível. Personagem liberado após o teleporte.
- Retorno físico da Cidade Z ao lobby confirmado, com troca da música e restauração do ambiente.

Os resultados detalhados estão em validation.json. Scripts em qa/ são apenas instrumentos de teste e não foram deixados ativos no projeto. A pasta before/ contém as fontes anteriores. A cópia de segurança do cenário está em ServerStorage.BeforeIslandFinish_1789008574. Estes arquivos são cópias de código; o cenário completo está no projeto aberto do Studio.
