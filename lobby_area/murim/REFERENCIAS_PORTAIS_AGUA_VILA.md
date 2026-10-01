# Referencias: portais, agua cartoon e vila (2026-09-19)


## agua

### Agua do Blox Fruits (o que da pra confirmar e como replicar)

**Fontes**
- [How is Blox Fruits water system done? - Roblox DevForum](https://devforum.roblox.com/t/how-is-blox-fruits-water-system-done/3489808) - devforum
- [How was Blox Fruits water made so big? - Roblox DevForum](https://devforum.roblox.com/t/how-was-blox-fruits-water-made-so-big/3421998) - devforum
- [Water - Blox Fruits Wiki (Fandom)](https://blox-fruits.fandom.com/wiki/Water) - wiki
- [Material that matches Terrain Water? - Roblox DevForum](https://devforum.roblox.com/t/material-that-matches-terrain-water/2180823) - devforum

**Achados**
- Nao existe fonte oficial dizendo os valores exatos da agua do Blox Fruits. O que aparece no DevForum e reconstrucao da comunidade, entao qualquer numero especifico citado por ai e chute. Nao copiar numero inventado.
- A wiki do jogo registra que a textura da agua foi trocada no update 17.3, ou seja, a aparencia do mar nao e a Terrain water crua padrao e sim algo ajustado/estilizado ao longo do tempo.
- O padrao mais citado no DevForum para mares enormes tipo Blox Fruits: Terrain water de verdade so perto do jogador (para natacao e colisao funcionarem) e, longe, um bloco/plano azul gigante que apenas finge ser oceano. Isso existe porque encher milhares de studs de terrain water pesa e estoura o voxel.
- Quando o dev tenta casar esse bloco distante com a terrain water, o relato e que da pra acertar so em angulo baixo: a terrain water muda de cor conforme o angulo de visao e o reflexo, entao o bloco nunca bate perfeito em visao de cima.
- A sugestao tecnica dada para esse bloco de imitacao e usar PBR convertido em MaterialVariant, com metalness cheia e sem roughness map, para aproximar o comportamento reflexivo da agua.
- Outra linha descrita na mesma thread: superficie de agua como mesh deformada por bones (altura animada) e uma terrain water invisivel embaixo so para o estado Swimming, ou natacao 100% custom (desabilita o estado Swimming, trava o Y com BodyPosition/raycast e alterna animacoes SwimIdle/Swim).
- Leitura util para o lobby: o que o usuario chama de 'agua do Blox Fruits' e a impressao visual - turquesa/ciano saturado, translucido perto da margem, com brilho forte de ceu - nao um preset tecnico. Da pra chegar la com Terrain water bem tunada mais margem tratada.

**Como aplicar**
- O Lago de Jade e pequeno e decorativo: usar Terrain water de verdade, sem o truque do bloco distante. O truque so vale para oceano gigante.
- Mirar em turquesa/jade saturado para casar com a paleta do lobby (jade + ouro + vermelho imperial), nao em azul-marinho realista. A agua vira o contraponto frio do vermelho.
- Calibrar por captura de tela dentro do Roblox em Play (como ja foi feito com as tintas do Gate 1), nao no viewport do Studio: a agua so mostra a aparencia final em playtest.
- Se em algum momento quiser um espelho de agua fora do terrain (ex: bacia elevada, fonte), usar MeshPart com SurfaceAppearance imitando agua em vez de tentar casar com terrain water - a tentativa de casar e frustrada pelo angulo.

**Erros comuns**
- Copiar um 'valor oficial do Blox Fruits' que ninguem publicou; o resultado sai errado e sem como auditar.
- Fazer lago gigante de terrain water achando que fica igual ao mar do jogo - fica pesado e continua parecendo piscina.
- Comparar o resultado no viewport do Studio e concluir que ficou chapado, quando na verdade a agua nao renderiza completa fora do playtest.
- Deixar a agua azul-marinho realista: quebra o registro cartoon premium do resto do lobby.

### Roblox Terrain water: propriedades, faixas e limitacoes

**Fontes**
- [Terrain - Roblox Creator Docs (API)](https://create.roblox.com/docs/reference/engine/classes/Terrain) - doc_oficial
- [creator-docs parts/terrain.md (secao de agua)](https://github.com/Roblox/creator-docs/blob/main/content/en-us/parts/terrain.md) - doc_oficial
- [New water properties (anuncio) - Roblox DevForum](https://devforum.roblox.com/t/new-water-properties/20309) - devforum
- [How do you make different color water in different areas? - Roblox DevForum](https://devforum.roblox.com/t/how-do-you-make-different-color-water-in-different-areas/1920986) - devforum

**Achados**
- As cinco propriedades ficam no objeto Terrain do Workspace e sao de ambiente (capability Environment): WaterColor (Color3), WaterTransparency, WaterReflectance, WaterWaveSize, WaterWaveSpeed.
- Faixas documentadas: WaterTransparency de 1 (totalmente limpa/transparente) a 0 (opaca); WaterReflectance de 1 (reflexo alto) a 0 (nenhum); WaterWaveSize de 1 (ondas grandes) a 0 (sem onda); WaterWaveSpeed de 100 (turbulenta) a 0 (parada).
- LIMITACAO PRINCIPAL: WaterColor ajusta o tom de TODA a agua do lugar. Nao existe agua de cor diferente por area nativamente - so trocando por script.
- Workarounds documentados para cor por regiao: (a) sobrepor uma Part semitransparente colorida sobre a agua, com a terrain water setada para preto (0,0,0) para o resultado ficar limpo; (b) script que tweena WaterColor (e junto iluminacao e som) conforme a regiao do jogador - abordagem usada por jogos como The Wild West.
- WaterWaveSize e travada em 1 no maximo; devs ja pediram teto de 5 ou 10 e nao foi atendido. Ou seja, onda alta de verdade nao sai da terrain water.
- As propriedades de agua so aparecem corretas em playtest. Para ver no editor, subir 'Editor Quality Level' nas Studio Settings para o maximo. Existe inclusive relato de bug de agua renderizando sempre plana independente do nivel de qualidade.
- Extremos ja usados de forma estilizada pela comunidade: WaterTransparency 0 gera um efeito quase neon (agua opaca chapada de cor), e cor totalmente fora do natural (agua vermelha tematica) funciona - a propriedade aceita qualquer Color3.
- Reflectance alta puxa a cor do ceu/Lighting para dentro da agua: a aparencia final depende tanto do Lighting (Atmosphere, ClockTime, ambiente) quanto do WaterColor.

**Como aplicar**
- Ajustar apenas no Terrain do Workspace e testar em Play, com Editor Quality no maximo, para nao calibrar no escuro.
- Ponto de partida cartoon turquesa para o Lago de Jade: WaterColor em turquesa/jade claro saturado, WaterTransparency baixo-medio (agua mais leitosa, nao vidro), WaterReflectance media para pegar brilho do ceu sem virar espelho realista, WaterWaveSize baixo (0.1-0.2) e WaterWaveSpeed baixo (agua de jardim e calma, nao mar) - varrer esses valores em play e escolher pelo print.
- Como o lobby tem um unico corpo de agua, a limitacao de WaterColor global nao atrapalha: uma cor serve o lobby inteiro.
- Se depois quiser contraste raso/fundo, usar o workaround (a): terrain water como base e Parts finas semitransparentes mais claras nas bordas rasas.
- Registrar os valores finais no script de build do lobby (mesma pratica dos atlas do Gate 1) para o lago nao voltar ao default em rebuild.

**Erros comuns**
- Achar que da pra ter lago verde e mar azul no mesmo lugar sem script - nao da.
- Subir WaterWaveSize/Speed em lago pequeno: ondas grandes num espelho de agua de jardim ficam ridiculas (critica literal feita a uma agua estilizada no DevForum).
- Confiar no viewport do Studio para julgar cor e reflexo.
- Setar Reflectance perto de 1 e depois culpar o WaterColor quando a agua fica so espelho de ceu.
- Esquecer que a Part de imitacao precisa da terrain water em preto para o truque de sobreposicao ficar limpo.

### Agua cartoon estilizada: o que impede de parecer uma placa azul

**Fontes**
- [My take on shaders: Stylized water shader - Harry Alisavakis](https://halisavakis.com/my-take-on-shaders-stylized-water-shader/) - artigo_tecnico
- [Shoreline Shader Breakdown - Cyanilux](https://www.cyanilux.com/tutorials/shoreline-shader-breakdown/) - artigo_tecnico
- [Cartoon Water Shader in UE4 - 80.lv](https://80.lv/articles/cartoon-water-shader-in-ue4) - artigo_tecnico
- [[FEEDBACK] Stylized Animated Water - Roblox DevForum](https://devforum.roblox.com/t/feedback-stylized-animated-water/2580001) - devforum

**Achados**
- O que mais vende agua estilizada e a PROFUNDIDADE: usar a diferenca de profundidade em tres niveis - linha da margem, faixa intermediaria e fundo escuro. Isso da as transicoes de cor e o controle do tom por profundidade.
- Agua cartoon usa 2 ou 3 faixas de cor chapadas (raso ciano claro / meio azul-turquesa / fundo indigo escuro) em vez de gradiente continuo realista. E a leitura em bandas que da o look de desenho.
- Espuma na margem e o segundo item mais importante: aparece onde a agua intersecta a geometria (depth fade como mascara) e onde a onda quebra. Pode ser banda pintada a mao ou anel procedural com ruido rolando.
- Truque concreto de linhas de espuma animadas: aplicar seno sobre a diferenca de profundidade com o tempo, gerando linhas brancas que correm em direcao a margem; uma 'swash wave' secundaria simula a espuma subindo e descendo na areia.
- Ruido tipo Voronoi animado/distorcido gera as manchas organicas de espuma; uma segunda amostra de Voronoi adiciona bolhinhas internas.
- Ondulacao pode vir so de normal maps: dois normal maps mapeados em world space e misturados, com UVs deslocadas - sem tessellation, sem height map, sem deslocar vertice. O shader do Alisavakis roda em um quad plano.
- Areia molhada: uma faixa mais escura e translucida no terreno junto da agua, que vende a interacao agua/terra mesmo com a agua parada.
- No caso Roblox concreto de agua estilizada aprovada pela comunidade: skinned mesh deformada por funcao gaussiana para as ondas, normal e roughness feitos no Substance Designer, textura de splatter pintada com pincel no Photoshop, deslocamento de textura animado pelos mesmos valores da gaussiana e transparencia leve.
- Criticas recorrentes nessa mesma thread: onda grande demais para o tamanho do corpo d'agua, transparencia fraca demais e particulas sem fade-out. Escala e fade sao onde as pessoas erram.

**Como aplicar**
- Prioridade para o Lago de Jade, nesta ordem: (1) faixa de espuma/raso na margem, (2) duas ou tres bandas de cor por profundidade, (3) ondulacao sutil, (4) reflexo controlado. Sem (1) e (2) qualquer agua vira placa azul.
- Espuma sem shader custom no Roblox: anel de MeshParts finos (ou Decals/Textures brancas com SurfaceAppearance Transparency) acompanhando a borda do lago, pintado no atlas junto com o resto do kit - mesmo pipeline de bake ja usado no Gate 1.
- Bandas de profundidade sem shader: modelar o fundo do lago em degraus (borda rasa larga, centro fundo) e pintar o fundo em duas ou tres tintas jade - a propria terrain water faz o resto, porque o tom lido depende do que esta embaixo.
- Pedra molhada em vez de areia molhada: faixa de pedra clara com tom mais escuro e saturado na borda d'agua, assada na textura do kit - vende a transicao mesmo com a agua imovel.
- Movimento barato: WaterWaveSpeed baixo mais nenufares/petalas com leve animacao e um ou dois Beams de brilho na superficie, em vez de tentar onda de verdade.
- Reflexo: manter medio e deixar o ceu e as lanternas douradas fazerem o brilho - o contraste quente/frio e o que faz a agua parecer volume.
- Cuidar da escala: lago de jardim com avatar de 5 studs pede ondulacao minima; onda grande e o erro apontado diretamente no feedback do DevForum.

**Erros comuns**
- Agua opaca de cor unica chapada sem variacao na margem: e literalmente uma placa azul.
- Espuma como linha branca dura e estatica, sem ruido nem movimento - le como contorno de erro, nao como espuma.
- Gradiente realista continuo em cena cartoon: some com a leitura em bandas e briga com o resto do kit pintado.
- Fundo do lago plano: sem variacao de profundidade nao ha o que ler como raso/fundo.
- Exagerar reflexo e onda achando que e 'mais bonito' - vira mar realista dentro de um jardim chines estilizado.
- Particulas de respingo sem fade-out, que somem de golpe e denunciam o efeito.


## portais

### Portais de teleporte em jogos do Roblox de grande publico

**Fontes**
- [Portals - Blox Fruits Wiki (Fandom)](https://blox-fruits.fandom.com/wiki/Portals) - wiki do jogo
- [Portals - Blox Fruits Wiki (espelho)](https://bloxfruitswiki.org/wiki/portals/) - wiki do jogo
- [Portal (fruta) - Blox Fruits Wiki](https://blox-fruits.fandom.com/wiki/Portal) - wiki do jogo
- [Portal Teleportation Warp Travel Point Zone - Creator Store](https://create.roblox.com/store/asset/91062503899633/Portal-Teleportation-Warp-Travel-Point-Zone) - asset oficial Roblox

**Achados**
- No Blox Fruits (Third Sea) os portais sao descritos literalmente como COLUNAS TRANSPARENTES, nao como arcos: um cilindro/pilar de energia semitransparente que o jogador atravessa. Leitura simples, silhueta vertical, sem moldura pesada.
- Sao SEIS portais no Third Sea: tres no Castle on the Sea, um no Mansion, um no Tiki Outpost, um em Hydra Island. Coincide exatamente com os 6 portais do Santuario - da para copiar o padrao de hub central com varias saidas juntas.
- Portais tem TRAVA por progressao: se o jogador nao derrotou rip_indra True Form (Mansion/Hydra) ou o Tyrant of the Skies (Tiki Outpost), aparece a mensagem 'You cannot access this portal yet'. Ou seja: estado bloqueado e estado liberado sao parte do design visual e de feedback.
- A wiki registra que o Update 24 adicionou 'teleporting visuals' e o Update 26 REVERTEU para o visual antigo - sinal de que efeito de teleporte exagerado incomoda em hub de uso repetido. Preferir efeito curto e discreto na travessia.
- Os portais 'parecem estar sempre em areas com teto por cima' - ficam abrigados sob estrutura, nao soltos ao ar livre. Isso reforca por que um Santuario coberto com nichos e a solucao certa.
- A fruta Portal (Legendary, Natural, 1.900.000$ ou 2.000 Robux) usa a mecanica [C] World Warp para teleportar para quase qualquer ilha - confirma que 'portal' no vocabulario do publico-alvo significa viagem rapida entre ilhas, nao dungeon.
- Assets prontos de portal na Creator Store se chamam justamente 'Portal / Teleportation / Warp / Travel Point / Zone' - vocabulario util para nomear as pecas e para pesquisar mais referencias dentro do Studio.

**Como aplicar**
- Cada um dos 6 nichos ganha uma COLUNA DE ENERGIA vertical (cilindro de ~4.5 x 9 studs, largura maior que o avatar de 5 studs para passagem confortavel) em vez de so um disco chapado no fundo do nicho. Mantem a silhueta que o publico de Blox Fruits ja reconhece.
- Cor por destino: cada portal recebe uma cor propria (jade, vermelho imperial, dourado, roxo, azul-gelo, verde-agua) mantendo a paleta do lobby. A cor e a leitura primaria a distancia; o icone e o texto so a curta distancia.
- Placa de pedra clara acima de cada nicho com o nome da area em relevo dourado, mais um icone simples no chao na frente do portal. Isso substitui o texto flutuante e combina com a arquitetura.
- Modelar DOIS estados por portal: FECHADO (coluna quase transparente, cinza-azulada, sem particulas, pedra sem brilho) e ATIVO (coluna saturada, particulas subindo, luz no chao). Mesmo que hoje todos fiquem ativos, o kit ja nasce preparado para travas de progressao.
- Manter os 6 portais juntos e visiveis de um so ponto, como o Castle on the Sea: o jogador entra no Santuario e ve todas as opcoes de uma vez, sem precisar andar.

**Erros comuns**
- Exagerar no efeito de travessia: o proprio Blox Fruits adicionou e depois REMOVEU visual de teleporte. Em hub usado dezenas de vezes por sessao, efeito longo vira irritacao. Maximo ~0.3s de flash.
- Fazer o vao do portal estreito demais: o avatar tem 5 studs, entao vao menor que ~6 studs de altura util e ~4 de largura faz o jogador travar na quina.
- Deixar todos os 6 portais com a mesma cor: o jogador perde a referencia de memoria muscular ('o portal verde e o do treino') e passa a depender de ler texto.
- Portal solto no meio do patio sem estrutura em volta: as referencias mostram portal sempre abrigado, o que ancora a escala e evita a sensacao de adesivo colado no chao.

### Portais magicos em fantasia (concept art e jogos estilizados)

**Fontes**
- [Fantasy Portal Concept Art (colecao de referencias)](https://www.pinterest.com/ideas/fantasy-portal-concept-art/957239429752/) - colecao de referencia visual
- [Stylized Magic Stone Portal with Runes - CGTrader](https://www.cgtrader.com/3d-models/character/fantasy-character/stylized-magic-stone-portal-with-runes) - modelo 3D estilizado
- [Magic portal - concept design steps (DeviantArt)](https://ellixus.deviantart.com/art/Magic-portal-concept-design-steps-734331160) - estudo de concept art
- [Animated pixel art magical portal in a runic stone archway](https://www.dreamstime.com/animated-pixel-art-magical-portal-swirling-purple-dark-blue-energy-vortex-runic-stone-archway-perfect-game-assets-image437027306) - referencia de asset de jogo

**Achados**
- A anatomia recorrente e sempre a mesma tripla: MOLDURA de pedra (arco ou arco quebrado) + RUNAS brilhantes gravadas na pedra + VORTICE de energia no vao. Tirar qualquer uma das tres e o portal deixa de ler como portal.
- As runas quase nunca sao espalhadas: elas correm EM ESPIRAL em direcao ao vao ou ficam alinhadas na borda interna do arco, guiando o olho para o centro. Runas aleatorias na superficie externa nao funcionam.
- Cristais e pedras FLUTUANDO em volta do arco sao o truque mais barato para dizer 'isto e magico e esta ligado' - especialmente pedras destacadas da moldura, como se a gravidade tivesse sido quebrada ali.
- Variacoes de familia bem documentadas: portal com runas na borda, portal QUEBRADO com bordas rachadas e irregulares (leitura de caos/perigo), e o 'energy gate' que dispensa moldura solida e usa so linhas de energia girando.
- Luz colorida etérea banhando a pedra (o exemplo classico e teal sobre pedra desgastada) faz o material da moldura receber a cor do vortice - esse bounce de cor e o que amarra moldura e energia numa coisa so.
- Portal ATIVO vs FECHADO se separa por: runas acesas vs runas apagadas/entalhadas sem brilho; vao com vortice vs vao vazio mostrando o cenario atras; particulas subindo vs nenhuma; luz projetada no chao vs sombra normal.
- Leitura a distancia vem da SILHUETA e do BRILHO, nunca do detalhe: em concept art o portal e reconhecivel como um anel/arco luminoso mesmo reduzido a poucos pixels.
- A base do portal quase sempre tem um elemento proprio (degrau, plataforma circular, pedras enterradas no chao) que separa o portal do piso comum e marca 'aqui voce para e entra'.

**Como aplicar**
- Aplicar a tripla no vocabulario do lobby: moldura = moon gate de pedra clara quente com telha vermelha; runas = caracteres/selos dourados gravados na borda interna do anel; vortice = disco de jade ou da cor do destino.
- Trocar 'runas magicas genericas' por SELOS DE SEITA entalhados em espiral no anel - mesma funcao visual, mas coerente com China imperial + Murim, sem virar portal nordico.
- Adicionar 2 a 4 fragmentos de jade flutuando lentamente em volta de cada portal (pequenos MeshParts com posicao animada). E o sinal mais barato de 'ativo' e funciona a distancia.
- Base obrigatoria: um disco de pedra de ~6 studs no chao na frente de cada portal, meio stud acima do piso, com o icone da area. Serve de marca de passo e ancora o modelo no terreno.
- Reaproveitar a mesma moldura para os 6 portais e variar SO a cor do vortice, a cor da luz e o selo - economiza modelagem e cria familia visual clara.

**Erros comuns**
- Encher a moldura de detalhe fino que some a 20 studs de distancia; o orcamento de detalhe tem que ir para a silhueta e a borda iluminada.
- Runas espalhadas sem direcao: perde o efeito de funil que puxa o olho para o vao.
- Portal ativo sem nenhuma luz no chao: sem a mancha de luz projetada, o portal parece um adesivo e nao uma fonte de energia.
- Misturar linguagens (runas nordicas, cristais roxos genericos) num lobby chines - quebra o tema todo; a magia precisa falar o idioma da arquitetura.

### Como fazer o vortice/superficie do portal no Roblox tecnicamente

**Fontes**
- [Animated Particles with the Particle Flipbooks Beta - Roblox DevForum](https://devforum.roblox.com/t/animated-particles-with-the-particle-flipbooks-beta/1718023) - anuncio oficial Roblox
- [Beams - Roblox Creator Documentation](https://create.roblox.com/docs/effects/beams) - documentacao oficial
- [How to recreate this portal effect? - Roblox DevForum (Building Support)](https://devforum.roblox.com/t/how-to-recreate-this-portal-effect/2878663) - forum de desenvolvedores
- [Are surfaceguis good/performant for textures? - Roblox DevForum](https://devforum.roblox.com/t/are-surfaceguis-goodperformant-for-textures/2276029) - forum de desenvolvedores

**Achados**
- FLIPBOOK de particula e o caminho oficial para textura animada: layouts 2x2 (4 quadros), 4x4 (16) e 8x8 (64), com a textura SEMPRE em 1024x1024 - entao cada quadro fica 512, 256 ou 128 px. Propriedades: FlipbookFramerate (faixa min/max em fps), FlipbookMode (Loop, OneShot, PingPong, Random) e FlipbookStartRandom.
- CUSTO REAL do flipbook: a resolucao 1024x1024 e obrigatoria, e desenvolvedores reclamam no proprio anuncio que todo emissor animado vira 'memory hog'. Um flipbook 4x4 de 1024 por portal, x6 portais com texturas diferentes, e caro. Compartilhar UMA textura entre os 6 e variar so a cor do emissor.
- Truque util do FlipbookStartRandom: com framerate ZERO ele vira gerador de 64 variacoes estaticas de uma unica textura 8x8 - otimo para petalas, faiscas e poeira do jardim sem custo de animacao.
- BEAM e a opcao barata para energia animada: Texture com TextureSpeed (rola a textura sozinha, sem script), TextureMode (Wrap, Static, Stretch), TextureLength, Width0/Width1 em studs, Curve por Bezier cubica (CurveSize0/CurveSize1), LightEmission e LightInfluence para o brilho, Transparency e Segments para suavidade. Um beam animado nao precisa de script por frame.
- A doc de Beams avisa explicitamente para TESTAR em varios niveis de qualidade grafica, porque o resultado muda conforme o device do jogador - vale para tudo que e efeito no lobby.
- Para textura animada em superficie plana, o consenso do DevForum e SurfaceGui + ImageLabel trocando ImageRectOffset/ImageRectSize sobre um UNICO atlas: uma imagem, uma requisicao, mais eficiente que varios ImageLabels ou trocar a propriedade Image.
- Vantagem extra do SurfaceGui com atlas: voce sobe UM atlas e recorta, enquanto Decal/Texture obriga a subir cada imagem separada - exatamente o pipeline de atlas que o lobby ja usa.
- Para profundidade real no vao (ver 'o outro lado'), a tecnica citada no forum e SurfaceGui contendo um ViewportFrame com Camera e os modelos dentro, sincronizando a camera do viewport com a do jogador via LocalScript; o forum descreve isso como de impacto minimo em performance, mas exige script de camera e nao combina com um vortice abstrato.
- O thread nao traz valores concretos de propriedades para malhas, neon ou particulas - so a tecnica de viewport. Ou seja: nao existe receita oficial pronta, a combinacao precisa ser calibrada no Studio.

**Como aplicar**
- Receita recomendada por portal, do mais barato ao mais caro: (1) MeshPart disco com SurfaceAppearance da cor do destino, (2) SurfaceGui com ImageLabel rolando um atlas de espiral compartilhado pelos 6, (3) um Beam curvo em anel com TextureSpeed para o brilho da borda, (4) UM ParticleEmitter pequeno subindo, (5) PointLight da cor do portal. Nada disso precisa de script por frame.
- Fazer UM unico atlas 1024x1024 de vortice em escala de cinza e colorir por portal via ImageColor3/Color do emissor - evita 6 texturas de 1024 na memoria.
- Usar Neon com moderacao: so no anel interno e nos selos, nunca no disco inteiro, senao o portal estoura o bloom e some o desenho da espiral.
- Evitar ViewportFrame neste caso: o portal do lobby e magico/abstrato, nao um buraco para outro comodo; o custo de script de camera nao se paga.
- Guardar FlipbookStartRandom com framerate 0 para as PETALAS do jardim - um emissor, 64 variacoes de petala, custo de animacao zero.
- Testar o lobby com qualidade grafica baixa antes de fechar, como a propria doc de Beams recomenda.

**Erros comuns**
- Subir 6 flipbooks 1024x1024 diferentes (um por destino): custo de memoria desnecessario quando a cor pode ser propriedade.
- Achar que flipbook aceita qualquer resolucao: nao aceita, tem que ser 1024x1024 e grade 2x2, 4x4 ou 8x8.
- Usar varios Decals/Textures separados em vez de um atlas recortado com ImageRectOffset - mais uploads, mais requisicoes, menos performance.
- Animar textura por script rodando a cada frame quando TextureSpeed do Beam ou o flipbook ja fazem isso nativamente.
- Nao testar em qualidade grafica baixa e descobrir depois que o portal some ou vira um borrao branco no celular.
- ParticleEmitter com Rate alto em 6 portais simultaneos num hub onde todo mundo passa - somar emissores e o jeito mais facil de derrubar o FPS do lobby.

### Portais em arquitetura chinesa/oriental que viram portal magico

**Fontes**
- [Moon gate - Wikipedia](https://en.wikipedia.org/wiki/Moon_gate) - enciclopedia
- [Paifang - Wikipedia](https://en.wikipedia.org/wiki/Paifang) - enciclopedia
- [China's Auspicious Moon Gates - Qi Journal](https://www.qi-journal.com/index.php/fengshui-articles/traditional-fengshui/3519-china-s-auspicious-moon-gates) - artigo sobre jardins chineses
- [An Ultimate Guide of Chinese Archways (Paifang) - Roaming China](https://roamingchina.com/an-ultimate-guide-of-chinese-archways/) - guia de arquitetura

**Achados**
- O moon gate (yueliangmen, 月亮門) e uma abertura CIRCULAR em muro de jardim usada como passagem de pedestres; pode ser tambem oval ou octogonal. E, literalmente, um portal ja pronto: o anel e a moldura magica sem precisar inventar nada.
- Diametro tipico citado: 4 a 8 pes (cerca de 1,2 a 2,4 m), com 6 a 8 pes funcionando bem em jardim residencial. Convertendo para a escala do Roblox com avatar de 5 studs, isso equivale a um vao de aproximadamente 7 a 9 studs de diametro - generoso e passavel.
- Detalhe de ouro para o kit: alguns moon gates tem TELHADO INCLINADO por cima representando a meia-lua do verao chines, e as PONTAS DAS TELHAS levam ornamentos talismanicos. Ou seja, telha + amuleto na ponta ja e canonico, nao e invencao.
- Simbolismo direto: o circulo representa o ceu (contra a terra quadrada), perfeicao, harmonia, reuniao e boa sorte - encaixa perfeitamente com 'portal que te leva a outro mundo' sem forcar a barra.
- Origem documentada no tratado Yuanye (1631), de Ji Cheng, que descreve a funcao do moon gate de ENQUADRAR VISTAS e fazer transicao entre espacos. Isso e exatamente o uso de um portal de teleporte: enquadrar o destino.
- Moon gates podem ser embutidos no muro OU ficar isolados/ligados a um muro baixo (variante de Bermuda). A versao isolada e a que melhor serve de portal solto dentro do Santuario.
- Materiais historicos: tijolo, pedra, madeira ou metal - pedra clara e tijolo sao os mais compativeis com a paleta quente do lobby.
- Paifang vs pailou: PAIFANG nao tem torre, dougong nem telhado; PAILOU tem telhado e por isso e mais imponente. Para portais menores dentro do Santuario, a versao sem telhado e mais leve e nao compete com o Grande Portao.
- Estrutura do paifang: base, pilares (retangulares ou quadrados, as vezes com cantos chanfrados), vigas horizontais, PLACA com caligrafia, telhado e dougong. O numero de pilares e vaos define a hierarquia - o topo era o pailou de cinco vaos, seis pilares e onze empenas.
- Materiais e cor do paifang: madeira pintada de VERMELHO sobre bases de pedra; ou pedra/tijolo que pode ser pintado ou decorado com telhas coloridas; ou pedra branca lisa, sem telha e sem cor, so com entalhe elaborado (usado em locais religiosos). Essas tres variantes dao tres niveis de pompa para escalonar os 6 portais.
- Escala real para calibrar: o arco de Seattle tem 14 m de altura; o de Lima tem 8 m de altura por 13 de largura; o Friendship Archway de Washington tem 14,50 m por 23 m. Isso mostra que paifang e ARQUITETURA DE ESCALA GRANDE - encolher demais descaracteriza.

**Como aplicar**
- Adotar o MOON GATE como moldura padrao dos 6 portais: anel de pedra clara quente, vao de 7 a 9 studs de diametro, anel com ~1 a 1.5 stud de espessura, base assentada num degrau de pedra. Um unico mesh reaproveitado seis vezes.
- Coroar cada moon gate com uma pequena aba de telha vermelha inclinada e um ornamento talismanico dourado na ponta de cada telha - detalhe historicamente correto que ja entrega o sabor cartoon premium.
- Colocar a PLACA com caligrafia (nome da area) acima do anel, exatamente onde o paifang coloca a sua - e o lugar canonico e o jogador aprende a procurar ali.
- Usar a hierarquia de material do paifang para diferenciar portais: pedra branca entalhada sem cor para areas 'sagradas', madeira vermelha sobre base de pedra para as comuns, pedra com telha colorida para as de destaque.
- Manter os portais do Santuario SEM telhado de torre (linguagem paifang, nao pailou) para que o Grande Portao continue sendo a estrutura mais imponente do lobby.
- Variar as formas para nao ficar repetitivo: alem do circulo, usar as variantes ja documentadas oval e octogonal em um ou dois portais - continua dentro do repertorio chines.
- Usar a logica do Yuanye: o moon gate serve para ENQUADRAR uma vista. Alinhar cada portal de forma que, quando ativo, o vortice colorido seja o que o jogador ve enquadrado - o anel vira a moldura de um quadro.

**Erros comuns**
- Fazer um paifang em miniatura: as referencias reais estao entre 8 e 14,5 m de altura; miniaturizar gera aquele efeito de brinquedo de jardim e mata a leitura de monumento. Para portal pequeno, use moon gate, nao paifang.
- Confundir paifang com pailou e colocar telhado de multiplos niveis em todos os 6 portais - fica pesado, repetitivo e rouba a cena do Grande Portao.
- Vao do moon gate na escala errada: o diametro real de 1,2 a 2,4 m NAO deve ser convertido literalmente, porque o avatar do Roblox tem 5 studs; converter direto produz um portal em que o jogador nao passa.
- Pintar tudo de vermelho: a propria tradicao tem a variante de pedra branca lisa so com entalhe, util para criar contraste e evitar monotonia cromatica.
- Esquecer o ornamento na ponta da telha - e um detalhe pequeno, historicamente correto e altamente legivel na silhueta cartoon.
- Deixar o moon gate embutido num muro quando o desejado e um portal isolado: a variante freestanding existe e e a correta para o Santuario.


## vila-flores

### rua/beco de vila chinesa tradicional: props de rua

**Fontes**
- [Along the River During the Qingming Festival (Wikipedia) - inventario da cena urbana Song](https://en.wikipedia.org/wiki/Along_the_River_During_the_Qingming_Festival) - enciclopedia
- [Along the River during the Qingming Festival - China Online Museum](https://www.comuseum.com/painting/famous-chinese-paintings/along-the-river-during-the-qingming-festival/) - museu/arte
- [Chinese Lanterns: History, Meaning, Types & Festival Traditions (StudyCLI)](https://studycli.org/chinese-culture/chinese-lanterns/) - cultura
- [Chinese Lanterns: History, Types (TravelChinaGuide)](https://www.travelchinaguide.com/essential/holidays/lantern/) - cultura
- [Making a Stylized Japanese Village in UE4 & ZBrush (80 Level)](https://80.lv/articles/making-a-stylized-japanese-village-in-ue4-zbrush) - breakdown de arte

**Achados**
- O rolo Qingming Shanghe Tu e a melhor lista de props ja feita de uma rua chinesa: as contagens citadas sao 814 pessoas, 28 barcos, 60 animais, 30 edificios, 20 veiculos, 8 cadeiras de liteira e 170 arvores. Rua viva = gente + carga + arvore, nao so casa.
- Comercio de rua no rolo: lojas grandes com fachada aberta, barracas soltas no meio da rua e vendedores ambulantes. Casas de cha, barracas de comida, restaurantes e tavernas/lojas de vinho sao os tipos mais repetidos.
- Mercadorias citadas por tipo de loja no rolo: vinho, graos, usados, panelas, arcos e flechas, lanternas, instrumentos musicais, ouro e prata, adornos, tecidos tingidos, pinturas, remedios, agulhas, incenso e papel ritual. Cada uma vira uma banca com silhueta propria.
- Transporte como prop de rua: carrocas de roda, burros e mulas de carga, carros puxados e cadeiras de liteira. Uma carroca parada com caixotes ja conta historia melhor que dez vasos iguais.
- Lanterna vermelha pendurada e o item assinatura: aparece em mercados, templos e ao longo de ruas inteiras, e e simbolo de prosperidade do negocio. Penduradas em fila, em festival ocupam a rua toda.
- Existe variacao de lanterna alem da esferica: ha lanterna de sombras, com camada interna de recortes/papel pintado que gira com o calor. Da para usar como versao 'especial' em pontos de interesse.
- Roupa lavada e secando e cena real de vila: a lavagem era feita na beira do rio, em grupo, batendo a roupa na pedra - logo pedra de lavar, bacia e varal perto da agua sao props corretos, nao decoracao aleatoria.
- Breakdowns de vila estilizada (caso japones do 80 Level) mostram o mesmo metodo: poucos modulos de casa + muitos props pequenos repetidos com rotacao/escala variada e que a densidade de tralha e o que faz a rua parecer habitada.

**Como aplicar**
- Montar um sub-kit 'rua viva' com 10 a 12 props: lanterna vermelha (2 tamanhos), varal com panos, barril, cesto de bambu (cheio e vazio), jarro de agua grande, banco de pedra, poco, pilha de telhas, corda enrolada, placa/estandarte vertical de loja, carroca de mao com caixotes.
- Usar as mercadorias do rolo como tema de cada banca do lobby: uma de cha, uma de remedio/ervas, uma de ferragem (encaixa na Forja Celeste), uma de lanternas. Muda so o prop que esta em cima, o balcao e o mesmo mesh.
- Pendurar lanternas em linha de corda entre dois postes/beirais ao longo da Via Imperial; guardar a lanterna 'especial' (maior, com padrao) para o Grande Portao e o Santuario dos Portais.
- Colocar poco + jarros + pedra de lavar perto do Lago de Jade, e varal com panos no beco da Casa do Intendente. Props agrupados por funcao leem como vila; espalhados leem como cenario falso.
- Carroca com caixotes encostada numa parede serve de bloqueio visual barato e quebra a linha reta da rua sem construir geometria nova.
- Reaproveitar o atlas ja assado do kit: os props novos entram no mesmo atlas para nao criar mais SurfaceAppearance por objeto.

**Erros comuns**
- Espalhar o mesmo vaso repetido em distancia regular; vira padrao visivel e mata a leitura de vila.
- So por lanterna e achar que virou China. Sem carga, roupa, cesto e sujeira de trabalho, a rua continua vazia.
- Prop grande demais para avatar de 5 studs: barril e cesto devem bater na cintura, lanterna pendurada acima da cabeca, senao vira obstaculo.
- Colocar objeto de trabalho (varal, poco, carroca) em lugar cerimonial, tipo o eixo do Grande Portao. Tralha domestica fica nos becos e nas laterais.
- Criar material novo por prop; quebra o pipeline de atlas e pesa no Roblox.

### jardim chines classico: composicao e elementos obrigatorios

**Fontes**
- [Chinese garden (Wikipedia)](https://en.wikipedia.org/wiki/Chinese_garden) - enciclopedia
- [Elements of the Chinese Garden - Espace pour la vie (Jardim Botanico de Montreal)](https://espacepourlavie.ca/en/elements-chinese-garden) - instituicao/jardim
- [What are we talking about when we talk about plants in classical Chinese gardens? - China Daily](https://www.chinadaily.com.cn/a/201901/23/WS5ca3195aa3104842260b3fbd.html) - jornalismo cultural
- [Astor Court, Metropolitan Museum of Art (Wikipedia) - patio chines reconstruido](https://en.wikipedia.org/wiki/Astor_Court_(Metropolitan_Museum_of_Art)) - museu

**Achados**
- Os cinco elementos do jardim classico sao arquitetura, rochas, agua, plantas e caligrafia. Faltando rocha ou agua, nao le como jardim chines.
- Arquitetura de jardim tem tipos definidos: pavilhao (ting), corredor coberto (lang) que quase nunca e reto e zigueza acompanhando o terreno, portao-lua circular e ponte em zigue-zague (ponte das nove curvas) que obriga varios pontos de vista.
- Rocha: as pedras de escolar do Lago Tai sao o foco; valem pela forma contorcida e cheia de furos, que expressa a agua (yin) erodindo a pedra (yang). Rocha de jardim e escultura, nao entulho.
- Agua: lago central simboliza infinito, a superficie plana funciona como espelho e amplia o espaco; riachos serpenteiam e as vezes somem atras da vegetacao. Pavilhao de lotus e plataforma sobre a agua sao padrao.
- Plantas simbolicas com papel definido: pinheiro, bambu e ameixeira sao os Tres Amigos do Inverno (longevidade, sabedoria, renascimento); orquidea = nobreza; lotus = pureza; peonia = opulencia e refinamento (rainha das flores, primavera); crisantemo = outono; salgueiro = amizade.
- Outros elementos construidos: muros brancos usados como fundo puro para as plantas, janelas ornamentais hexagonais/octogonais/em forma de vaso, e o calcamento tratado como parte da composicao.
- Principios de composicao: cenario emprestado (jiejing), que enquadra montanha ou arvore de fora para o jardim parecer maior; vistas escondidas e ocultacao, que impedem ver tudo de uma vez; caminhos sinuosos que entregam descobertas em sequencia.

**Como aplicar**
- Garantir os cinco elementos no jardim do lobby: uma rocha grande de jade/cinza como foco, a agua do Lago de Jade, tres grupos de plantas, um pavilhao ou corredor coberto pequeno e uma placa/estela com caligrafia dourada.
- Trocar qualquer caminho reto do jardim por caminho sinuoso, e usar ponte em zigue-zague ou o portao-lua como quadro: o jogador anda e a vista muda, em vez de ver tudo do spawn.
- Usar muro branco/pedra clara como fundo atras dos canteiros de peonia; a flor so 'estoura' se tiver parede lisa atras. Abrir uma janela ornamental (circulo ou vaso) nesse muro enquadrando a Espada Ancestral.
- Plantar por simbolo e nao por acaso: pinheiro+bambu+ameixeira juntos num canto (Tres Amigos), peonia perto do salao nobre, lotus so na agua, crisantemo na borda do caminho, salgueiro pendendo sobre o lago.
- Esconder o final do caminho atras de rocha ou bambu para criar a 'vista escondida'; isso vale mais que adicionar mais props.
- Uma rocha boa vale cinco medias: modelar 2 ou 3 rochas com furos e silhueta torta e reusar com rotacao, em vez de espalhar pedras redondas.

**Erros comuns**
- Jardim simetrico e geometrico: isso e jardim frances, nao chines. O classico chines evita eixo e reta no jardim.
- Pedras arredondadas e iguais no lugar de rocha escultural furada; perde todo o carater.
- Lago sem nada refletindo nem nada pendendo sobre ele: a agua serve de espelho, precisa de silhueta na margem (salgueiro, pavilhao, ponte) para ter funcao.
- Misturar tudo com tudo: cada especie deve ter seu lugar e sua estacao, plantio aleatorio le como parque generico.
- Encher o jardim de arquitetura: os predios entram em menor quantidade, para enquadrar a cena natural, nao para dominar.

### flores para jardim estilizado cartoon: forma, cor e plantio

**Fontes**
- [Texture Atlases - Creating Foliage Texture and Meshes (Roblox DevForum, staff)](https://devforum.roblox.com/t/texture-atlases-creating-foliage-texture-and-meshes/3171224) - documentacao oficial Roblox
- [Low Poly Foliage (Polycount)](https://polycount.com/discussion/169096/low-poly-foliage) - forum de artistas
- [Creating Visual Interest in Low Poly Artworks (80 Level)](https://80.lv/articles/creating-visual-interest-in-low-poly-artworks) - breakdown de arte
- [Petal Power: simbolismo das flores na cultura chinesa (Shen Yun)](https://www.shenyunperformingarts.org/blog/view/article/e/MfFhDWG0M1s/category/blogger/flower-symbolism-in-traditional-chinese-culture.html) - cultura

**Achados**
- O material oficial do Roblox sobre folhagem manda empacotar petalas e folhas num unico atlas, com retangulos invisiveis em volta de cada elemento para nao sobrepor UV, e densidade de texel consistente para a flor nao ficar com escala errada.
- Transparencia custa mais que triangulo no Roblox: a recomendacao e cortar o espaco transparente morto do card antes de reduzir poligono. O exemplo citado tirou 60% dos triangulos (240 para 144) so recortando vazio, sem perda visual.
- DoubleSided so deve ser ligado quando o jogador realmente ve os dois lados; ligar em tudo dobra o custo a toa.
- Evitar sobreposicao excessiva de cards na mesma linha de visao da camera (overdraw); usar ferramenta de distribuicao controlada (tipo Brushtool) em vez de empilhar tufos no mesmo ponto.
- Regra pratica de folhagem low poly do Polycount: menos folha na textura e mais folha na malha. Aglomerado pintado na textura vira bloco solido quando o mipmap reduz.
- O 80 Level sobre low poly aponta que o que 'vende' o ambiente sao os detalhes vivos: borboletas, poeira brilhante, folhagem balancando e folhas caindo; se o objeto tem peso, vale animar ou dar shader de vento.
- Flores estilizadas prontas de mercado convergem no mesmo receituario: silhueta limpa, sombreamento suave por rampa de cor sem costura de textura, cor vibrante - o que casa com pipeline toon/cel.
- Papel simbolico e sazonal ja define a paleta: peonia (primavera, rosa/magenta/vermelho, rainha das flores), lotus (branco/rosa, so na agua, pureza), crisantemo (outono, amarelo/dourado/bronze), ameixeira (inverno/fim de inverno, branco e rosa palido sobre galho escuro).

**Como aplicar**
- Fazer 4 flores no kit, cada uma com 2 variantes de escala: peonia (bola de 5 a 7 petalas largas), lotus (flor aberta + botao fechado + folha circular flutuante), crisantemo (esfera de petalas finas radiais) e ramo de ameixeira (galho escuro com pontos de flor).
- Modelar petala em geometria, nao em alpha, sempre que possivel: no Roblox isso evita o custo de transparencia e conversa com o pipeline de atlas assado que o lobby ja usa. Alpha so no que for realmente folha fina.
- Assar as 4 flores no mesmo atlas do kit do jardim, com folga reservada no atlas para flores futuras sem reUV.
- Paleta travada em 4 acordes ligados ao lobby: magenta/rosa quente da peonia contra vermelho imperial, branco-rosa do lotus na agua de jade, amarelo-dourado do crisantemo conversando com o ouro, e branco frio da ameixeira como ponto de respiro.
- Plantio em grupos impares e com hierarquia: cada canteiro com 1 tufo grande, 2 medios e 3 a 5 pequenos, todos com rotacao aleatoria em Y e escala variando de 0.85 a 1.2; nunca linha regular nem uma flor solta no meio do gramado.
- Uma especie dominante por canteiro (70%) com 20% de uma segunda e 10% de grama alta; isso da leitura clara de 'canteiro de peonias' em vez de salada de cores.
- Lotus so na agua parada e perto da margem ou da ponte-lua, em ilhas de 3 a 6 folhas com 1 ou 2 flores; folha flutuante quebra a superficie espelhada do lago.
- Adicionar 1 ou 2 efeitos vivos baratos: petalas caindo perto da ameixeira e vagalumes/poeira dourada no jardim a noite.

**Erros comuns**
- Espalhar flores unitarias e equidistantes pelo gramado; le como grama com pontinhos, nao como jardim.
- Usar muitas cores de flor no mesmo canteiro; perde o simbolo e vira ruido.
- Abusar de card com alpha: no Roblox e o custo mais caro da folhagem e o mipmap engole o detalhe de longe.
- Ligar DoubleSided e empilhar cards no mesmo ponto, gerando overdraw sem ganho visual.
- Densidade de texel diferente entre flor e resto do kit; a flor aparece borrada ou nitida demais ao lado dos props ja assados.
- Peonia e crisantemo com o mesmo tamanho e mesma silhueta: se de longe as duas viram a mesma bola, nao valeu modelar duas.

### transicao gramado -> caminho em jogos estilizados

**Fontes**
- [Tips for Painting Fallen Leaves, Grass, Dirt, Pebbles and Other Ground Matter (Draw Paint Academy)](https://drawpaintacademy.com/ground/) - fundamento de arte
- [How to Draw Ground, Grass and Rocks (Envato Tuts+)](https://design.tutsplus.com/tutorials/how-to-draw-ground-grass-and-rocks--cms-26827) - tutorial
- [8 Great Patterns for a Pebble Mosaic (This Old House)](https://www.thisoldhouse.com/masonry/21017470/8-great-patterns-for-a-pebble-mosaic) - referencia construtiva
- [Grass Generator - gerar grama no topo de partes (Roblox DevForum)](https://devforum.roblox.com/t/grass-generator-easily-generate-grass-on-top-of-parts/2746519) - ferramenta Roblox

**Achados**
- A tecnica base para esconder costura e usar aglomerados que transbordam a borda: tufos, arbustos e pedrinhas que atravessam a linha entre caminho e grama, em vez de uma borda limpa.
- Transicao boa e gradual, por pontilhado/dispersao: a densidade de um material vai caindo enquanto a do outro sobe, com pedrinhas e ervas daninhas no meio do caminho.
- Detalhe fino na borda - folhas caidas e detritos espalhados - aumenta a coesao entre os dois materiais e e o que tira o aspecto de adesivo.
- Caminho de pedra chines usa seixo de rio assentado de pe no cimento formando padrao (dragoes, flores, geometria), com contraste de preto, branco e cinza para o desenho aparecer, e pedra de borda definindo o limite do calcamento.
- Caminhos de jardim chines sao sinuosos e o padrao em espiral funciona bem em trecho curvo porque reforca a direcao da curva.
- No Roblox ha plugin que gera grama no topo de partes e e explicitamente usado para criar caminhos - ou seja, o caminho pode ser definido pela ausencia/menor densidade de grama, nao por uma textura chapada.

**Como aplicar**
- Construir a borda em tres faixas: 1) pedra de borda do calcamento, 2) faixa de 0.5 a 1 stud de terra batida/musgo com pedrinhas, 3) tufos de grama alta que invadem o calcamento em pontos irregulares. Nunca deixar linha reta e limpa.
- Dispor os tufos de invasao com espacamento irregular e em grupos, deixando trechos de caminho totalmente limpos - o contraste entre trecho limpo e trecho invadido e o que parece natural.
- Assar o padrao de seixo (preto/branco/cinza) no atlas do piso, com variacao de 2 a 3 tiles para nao repetir; guardar um tile com padrao de flor ou moeda para as rotatorias e entradas de pavilhao.
- Fazer o caminho do jardim curvo e usar o padrao em espiral/losango nas curvas; deixar o calcamento reto e formal so na Via Imperial e no eixo do Grande Portao.
- Quebrar a cor chapada do gramado com 3 camadas: mancha de verde mais escuro/oliva no fundo, decals ou meshes baixos de musgo e folhas caidas, e tufos de grama alta em grupos. Gramado de uma cor so e o que mais denuncia build de Roblox.
- Acumular folhas caidas e petalas onde faria sentido fisico: no canto de muro, sob a ameixeira e na juncao do caminho com o degrau.

**Erros comuns**
- Borda dura entre gramado e caminho, com o caminho parecendo adesivo colado por cima.
- Distribuir tufos de borda com espacamento regular ao longo de todo o caminho; vira cerca viva, nao invasao natural.
- Gramado com uma unica cor saturada e sem variacao de tom nem detritos.
- Repetir um unico tile de seixo em toda a area; o padrao vira listra visivel de longe.
- Exagerar na tralha da borda ao ponto de o jogador nao ler para onde ir - o caminho precisa continuar legivel como caminho.
- Usar terra batida em area cerimonial de pedra polida; a transicao suja pertence ao jardim e aos becos, nao ao eixo imperial.
