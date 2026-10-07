# Referencias de producao - Seita da Forja Celeste

Pesquisa por categoria (workflow de 3 pesquisadores, 2026-09-19). Cada categoria separa: referencia historica / interpretacao cartoon / adaptacao para o jogo / erros comuns.
Itens marcados pelos pesquisadores como "conhecimento geral, nao verificado" ou "sem numero confiavel" NAO devem ser tratados como fato.


## Grupo: estilizacao-roblox

### Arquitetura oriental estilizada em jogos/animacao (Overwatch Lijiang, Genshin Liyue, LoL Ionia, Kung Fu Panda)

**Fontes**
- [Lijiang Tower - Overwatch, Philip Klevestav (ArtStation; veio no resultado da busca, nao aberto)](https://www.artstation.com/artwork/WKoRqJ) - portfolio de artista (ArtStation)
- [Lijiang Tower - Thiago Klafke (portfolio; veio no resultado da busca, nao aberto)](https://www.thiagoklafke.com/blog/portfolio/lijiang-tower/) - portfolio de artista
- [Making an Overwatch Fan Art Scene: Approach to Texturing (Jonathan Johnson) - aberto](https://80.lv/articles/overwatch-fan-art-environment-approach-to-texturing) - breakdown 80.lv
- [Liyue/Design - Genshin Impact Wiki (veio no resultado da busca, nao aberto)](https://genshin-impact.fandom.com/wiki/Liyue/Design) - wiki de jogo

**Referencia historica**
- Divisao de trabalho em Lijiang Tower (resultado da busca): Klevestav fez blockout e arquitetura dos 3 pontos; Klafke fez mercado noturno e cidade de fundo; Dion Rogers e Helder Pinto iluminacao e set dressing. Licao: a arquitetura foi resolvida primeiro em blockout de silhueta, detalhe depois.
- Liyue (resumo da busca): edificios multi-andar sobre pilares, cada andar separado por beiral ornamentado, telhado de curva suave tipo imperial, trelica de madeira, entalhes de animais/criaturas com dourado, motivo de dragao; Wangshu Inn inspirada no Templo Suspenso (Xuankong), Shanxi.
- Jade Palace (resumo da busca): leitura baseada em formas iconicas, cores distintas, telhados em camadas, escadaria ingreme e silhueta de topo de montanha. Numero '88.100 superficies' veio de wiki de fa: tratar como sem numero confiavel.
- Base real que todos exageram (conhecimento geral, NAO verificado nesta sessao): ordem tripartida plataforma / corpo de colunas / telhado; telhado de quatro aguas ou hip-and-gable; cantos levantados; cumeeira com chiwen nas pontas e fila de bestas na aresta do canto; cores por hierarquia (amarelo imperial > verde/jade > cinza).
- Proporcoes numericas de exagero (razao telhado x corpo, grossura de coluna) nao apareceram em nenhuma fonte aberta: sem numero confiavel. Os valores em 'adaptacao_jogo' sao proposta de trabalho, nao dado de fonte.

**Interpretacao cartoon**
- Telhado domina a silhueta: beiral projeta muito alem do corpo e a altura do telhado se aproxima ou iguala a do corpo de colunas; o corpo fica mais baixo e atarracado que o real (observacao geral de estilo, sem numero confiavel).
- Pecas lineares engrossadas: colunas, vigas, cumeeira e aresta de canto ficam bem mais grossas que o real para ler de longe e nao serrilhar; cumeeira vira um 'tubo' gordo com tampa.
- Curva do canto exagerada e continua: o levantar comeca mais cedo (nao so no ultimo vao) e termina em ponta clara; a linha do beiral vira um arco limpo, sem quebras.
- Contagem reduzida, tamanho aumentado: menos telhas, menos caibros, menos bracos de dougong, menos bestas de cumeeira, porem cada um maior e com chanfro largo. Dougong vira 2-3 camadas legiveis em vez de dezenas de pecas.
- Detalhe concentrado em faixas: linha do beiral (caibros + ponta de telha + dougong), cumeeira/chiwen, porta/placa de entrada e base sumeru. Planos grandes (parede, agua do telhado, piso) ficam calmos, so com gradiente.
- Chanfro/bevel largo em toda aresta (80.lv Johnson: bordas arredondadas e 'dano de aresta' estilizado), nada de aresta viva de 90 graus; tudo levemente torto/afunilado para parecer feito a mao.

**Adaptacao para o jogo**
- Escala para avatar de 5 studs (proposta, nao fonte): vao de porta ~8-9 studs de altura, coluna com diametro ~1,2-1,6 studs (grossa), beiral projetando ~5-7 studs alem da linha de colunas, base sumeru 2-3 studs.
- Modelar o kit em grade modular (Johnson usa grade fixa e paredes 400x400 cm com 50-100 cm de profundidade): definir modulo de vao (ex.: 12 ou 16 studs) e fazer beiral, viga, painel e balaustrada multiplos dele.
- Dougong em 3 graus = 3 malhas distintas reutilizadas (simples / medio / rico) + 1 conjunto de canto a 45 graus; cada uma como MeshPart unica instanciada, nunca reimportada por predio.
- Telha: nao modelar telha a telha na agua inteira; modelar faixas de telha-canal com perfil ondulado baixo + fileira de pontas redondas (wadang) so na borda do beiral, onde a camera ve.
- Canto levantado como peca propria (modulo de canto) que recebe a curva; os modulos retos de beiral ficam retos e baratos.
- Bestas de cumeeira: usar numero impar pequeno por hierarquia do predio (ex.: 3 em anexos, 5 no salao principal) com silhueta gorda; regra historica exata de contagem nao verificada nesta sessao.

**Erros comuns**
- Copiar proporcao real (telhado fino, colunas finas): some na camera de terceira pessoa do Roblox e parece maquete.
- Detalhe uniforme em tudo: sem areas de descanso o olho nao acha o foco e o custo de triangulos explode.
- Curva de canto so na ultima telha (canto 'dobrado') em vez de arco continuo.
- Dougong com dezenas de bracinhos finos: vira ruido e serrilhado; melhor 3 camadas grossas.
- Arestas vivas sem chanfro: nao pegam realce de luz e destroem o look cartoon premium.
- Misturar hierarquia de cor ao acaso (amarelo imperial em todo lugar): perde a leitura de importancia entre predios.

### Textura estilizada pintada a mao para ambientes (gradiente, realce de aresta, AO colorido, trim sheets, texel density, bake no Blender)

**Fontes**
- [Studying Hand-Painted Texturing Workflow for Stylized Art - aberto](https://80.lv/articles/studying-hand-painted-texturing-workflow-for-stylized-art) - breakdown 80.lv
- [Making an Overwatch Fan Art Scene: Approach to Texturing - aberto](https://80.lv/articles/overwatch-fan-art-environment-approach-to-texturing) - breakdown 80.lv
- [Building a Desert Scene with Modular Kit & Trim Sheets (veio no resultado da busca, nao aberto)](https://80.lv/articles/building-a-desert-scene-with-modular-kit-trim-sheets) - breakdown 80.lv
- [Roblox docs - Improve performance (orcamento de textura) - aberto](https://create.roblox.com/docs/performance-optimization/improve) - documentacao oficial Roblox

**Referencia historica**
- Ordem classica hand-painted (80.lv workflow): cor chapada de base -> pintar oclusao e sombras por cima -> gradientes considerando direcao da luz -> detalhes. AO assado do high poly entra como camada Multiply para revelar o relevo.
- Artista do artigo usa SO albedo: brilho, relevo e luz sao pintados no mapa de cor. Compativel com Roblox (ColorMap forte + Normal/Roughness simples).
- Fluxo Overwatch-like (Johnson): trabalhar em tons de cinza do grande para o pequeno (altura) -> cor -> roughness derivado do cinza -> ajustes de normal/AO. Formas grandes primeiro, micro-detalhe quase nenhum.
- Aresta estilizada: edge detect -> bevel -> slope blur com nuvens BORRADAS (para nao gerar ruido); dano de aresta por gradiente de flood-fill mesclado em Darken/Min.
- Trim sheet: varias faixas tileaveis e nao tileaveis lado a lado num unico bitmap; UVs saem do 0-1 de proposito e repetem ao longo da faixa (Johnson; definicao tambem no resumo da busca 80.lv).
- Busca 80.lv: gradiente sutil em todas as superficies para quebrar cor uniforme + passe de AO + realce suave de aresta que clareia a cor e abaixa o roughness.

**Interpretacao cartoon**
- Gradiente vertical em toda peca: mais escuro/saturado embaixo (contato com chao), mais claro/quente em cima; em coluna vermelha, base puxando para vinho, topo para laranja.
- Sombra/AO COLORIDA, nunca preto: multiplicar com tom frio ou complementar saturado (vermelho sombreia para roxo-vinho, jade para azul-petroleo, pedra para violeta acinzentado). Regra de estilo geral; sem numero confiavel de fonte.
- Realce de aresta pintado: linha clara de 2-4 px nas quinas viradas para cima, mais larga e quebrada nos cantos gastos; dourado recebe brilho quase branco-amarelado.
- Formas grandes e poucas: veio de madeira = 3-5 faixas largas, nao fibra; pedra = blocos com chanfro e 1-2 lascas, sem granulado fotografico.
- Roughness simples e em blocos (laca brilhante x pedra fosca x telha vitrificada semi-brilho); normal map so para chanfro e relevo grande assado.

**Adaptacao para o jogo**
- Bake no Blender (Cycles; conhecimento geral, nao verificado nesta sessao): assar Normal (tangente, OpenGL = padrao do Blender, que e o que o Roblox exige), AO e, se quiser, Pointiness/curvatura via Geometry node para mascara de aresta; usar cage/extrusion e margem de 8-16 px.
- Compor o ColorMap: base chapada x gradiente de posicao (Texture Coordinate Object Z em ColorRamp) x AO tingido em Multiply + mascara de curvatura em Screen para realce; assar tudo em Emit/Diffuse color para um unico PNG.
- Montar 2-3 trim sheets do kit: (1) madeira laqueada + vigas pintadas + faixas douradas, (2) pedra/base sumeru/piso/muro, (3) telha jade/imperial + cumeeira. Pecas unicas (chiwen, bestas, lanterna) em atlas proprio.
- Orcamento de textura conforme doc Roblox: 1024 custa 4x a memoria de 512; doc sugere 256 para imagens menores e 512 para objetos grandes salvo os que ocupam muita tela. Reservar 1024 para os trim sheets compartilhados; 2048+ so se necessario.
- Texel density: nenhuma fonte aberta deu numero; sem numero confiavel. Proposta de trabalho: fixar uma densidade unica para o kit (ex.: ~32-64 px por stud em pecas na altura do olho, metade disso no telhado) e conferir com checker map no Blender.
- Compartilhar o MESMO SurfaceAppearance entre pecas do mesmo trim sheet tambem ajuda instancing/draw calls (ver categoria Roblox).

**Erros comuns**
- Usar foto ou ruido procedural de alta frequencia: cintila no Roblox e quebra o look pintado.
- AO preto/cinza neutro: suja a cor; o premium vem da sombra tingida.
- Realce de aresta uniforme em todas as quinas (parece contorno de vetor): variar largura e concentrar nas quinas superiores.
- Densidade de texel diferente entre modulos vizinhos (coluna nitida ao lado de parede borrada).
- Normal map em formato DirectX (Y invertido): Roblox exige OpenGL tangent space.
- Pintar luz direcional forte no albedo e depois usar iluminacao dinamica com sombra: as duas luzes brigam. Manter no albedo so gradiente e AO suaves.

### Roblox ATUAL: limites de malha, SurfaceAppearance, fidelidades, instancing, streaming, iluminacao

**Fontes**
- [General specifications (Roblox docs, pagina c/ copyright 2026) - aberto](https://create.roblox.com/docs/art/modeling/specifications) - documentacao oficial Roblox
- [PBR textures / SurfaceAppearance (Roblox docs) - aberto](https://create.roblox.com/docs/art/modeling/surface-appearance) - documentacao oficial Roblox
- [4k Texture Rendering (DevForum Announcements, 30 jan 2026) - aberto](https://devforum.roblox.com/t/4k-texture-rendering/4316229) - anuncio DevForum
- [Emissive Masks are Now Live for Published Experiences (DevForum, 12 fev 2026; resultado da busca)](https://devforum.roblox.com/t/emissive-masks-are-now-live-for-published-experiences/4357705) - anuncio DevForum
- [Improve performance (Roblox docs) - aberto](https://create.roblox.com/docs/performance-optimization/improve) - documentacao oficial Roblox
- [Let There Be (Unified) Light! Unified Lighting is Fully Live (DevForum, 23 jul 2025; resultado da busca)](https://devforum.roblox.com/t/let-there-be-unified-light-unified-lighting-is-fully-live/3401512) - anuncio DevForum

**Referencia historica**
- Triangulos: doc oficial 'General specifications' (acessada 19/09/2026): malha individual nao pode passar de 20.000 triangulos. Topicos de DevForum citam ~21.000 no 3D Importer e 10.000 no batch import, mas sao posts de suporte (2023) e nao doc: tratar 20.000 como teto. Limite por ARQUIVO do importador: sem numero confiavel.
- Mapas do SurfaceAppearance (doc atual): ColorMap (com alpha opcional), NormalMap (somente tangent space OpenGL), RoughnessMap, MetalnessMap e EmissiveMaskContent (mascara em tons de cinza) com propriedades EmissiveTint e EmissiveStrength; SurfaceAppearance.Color tinge o ColorMap.
- Emissivo EXISTE: Studio Beta em out/2025 e liberado para experiencias publicadas em 12/02/2026 (DevForum), valido para SurfaceAppearance, MaterialVariant e TerrainDetail. Doc cita faixa de strength 0-40 como restricao para itens de Marketplace.
- AlphaMode (doc atual): Opaque (ignora alpha; marcado como beta na doc), Overlay (ColorMap sobre MeshPart.Color), Transparency (recorta/transparece pelo alpha), TintMask (mistura ColorMap tingido sobre nao tingido usando o alpha como mascara).
- Textura: anuncio de 30/01/2026: importacao ate 8K, renderizacao maxima 4096x4096, para MeshPart, SurfaceAppearance, Texture, Decal e MaterialVariant; o engine decide por dispositivo via Texture Streaming (carrega mips conforme memoria e importancia) e aparelhos fracos recebem versao reduzida.
- Iluminacao: desde 23/07/2025 (Unified Lighting) o seletor antigo Technology (Voxel/ShadowMap/Future/Compatibility) foi substituido por Lighting.LightingStyle: Realistic (equivale ao antigo Future) ou Soft; ShadowSoftness so aparece em Realistic. O engine escala a qualidade por dispositivo.

**Interpretacao cartoon**
- Emissivo por mascara resolve lanterna de palacio, brasas da forja, runas de espada e janelas acesas sem usar Neon nem peca separada: pintar a mascara em cinza no mesmo UV do ColorMap e ajustar EmissiveTint/Strength.
- TintMask permite UM conjunto de malha+textura de telha servir a telha jade e a telha imperial (e estandartes por faccao): alpha marca a area tingivel, SurfaceAppearance.Color muda a cor. Atencao: Color diferente = SurfaceAppearance diferente, o que separa os lotes de instancing (2 variantes e aceitavel).
- LightingStyle Realistic da sombra por luz local e especular, o que valoriza chanfro largo e laca/dourado; o look cartoon vem do albedo pintado + roughness em blocos, nao de desligar a luz.
- Como a resolucao efetiva e decidida por dispositivo (streaming de textura), o estilo precisa funcionar em mip baixo: formas grandes pintadas sobrevivem, micro-detalhe nao.

**Adaptacao para o jogo**
- Alvo por peca do kit: bem abaixo de 20.000 tris; pecas repetidas dezenas de vezes (caibro, telha, balaustre, dougong) devem ser baixas (centenas a poucos milhares; proposta de trabalho). Chiwen/bestas podem gastar mais pois sao poucas.
- Instancing (doc): malhas colapsam em um draw call quando tem o mesmo asset de malha e SurfaceAppearance identico (ou mesma textura; ou mesmo material se nao houver nenhum dos dois). Importar cada modulo UMA vez e duplicar no Studio; importar a cena inteira cria IDs diferentes para malhas iguais e quebra instancing.
- RenderFidelity: Automatic para quase tudo (permite LOD a distancia); Performance em pecas pequenas repetidas; Precise so em poucas pecas-heroi (doc avisa para evitar em muitas malhas).
- CollisionFidelity: Box em pecas pequenas ancoradas, Hull em pequenas/medias; evitar Precise em pecas grandes e complexas: criar colisao propria com Parts invisiveis (parede, piso, degraus, base). Desligar CanCollide/CanTouch/CanQuery em decoracao (telhas, caibros, dougong).
- Transparencia: evitar camadas sobrepostas semi-transparentes (overdraw). Trelica de janela: preferir geometria ou AlphaMode Transparency em um unico plano; folhagem de pinheiro/bambu em poucos cartoes.
- StreamingEnabled: doc recomenda para reduzir memoria e crashes, com StreamingMinRadius/TargetRadius menores para ser mais agressivo. Em lobby pequeno, agrupar cada predio em Model e testar raios; CastShadow off em pecas pequenas/distantes; limitar alcance, quantidade e Shadows das luzes das lanternas (sombras degradam abaixo de qualidade grafica 4).

**Erros comuns**
- Citar '1024 e o maximo de textura': desatualizado desde jan/2026 (render ate 4096), mas usar 4K em tudo estoura memoria: 1024 ja custa 4x de 512.
- Procurar Lighting.Technology = Future: a propriedade foi substituida por LightingStyle (Realistic) em jul/2025.
- Exportar o predio inteiro como um FBX: gera malhas duplicadas com IDs distintos, quebra instancing e pode bater no teto de 20k por malha.
- Um SurfaceAppearance diferente por peca (ou Color diferente em cada copia): cada variacao vira lote separado de draw call.
- CollisionFidelity Default/Precise em telhado cheio de telhas e caibros: custo de memoria/fisica alto sem ganho de gameplay.
- Normal map DirectX, ou esperar emissivo via alpha do ColorMap: o emissivo e um mapa proprio (EmissiveMaskContent).


## Grupo: forja-jardim-props

### Forja tradicional chinesa de espadas (Longquan): layout, fornalha, fole de caixa (fengxiang), bigorna, tempera, ferramentas, carvao, fornos com chamine

**Fontes**
- [Longquan Sword Forging Technique (Baidu Baike EN)](https://baike.baidu.com/en/item/Longquan%20Sword%20Forging%20Technique/667521) - enciclopedia (aberta)
- [Longquan Swords - China Today](http://www.chinatoday.com.cn/ctenglish/2018/cs/201802/t20180206_800116723.html) - revista (resultado de busca)
- [Oriental Box Bellows (China at Work / Craft of the Japanese Sword) - anvilfire](https://www.anvilfire.com/bookrev/kapp/oriental_box_bellows.htm) - site especializado de ferraria (resultado de busca)
- [Chinese Bellows, rectangular box and piston with feather valves - Science Museum Group](https://collection.sciencemuseumgroup.org.uk/objects/co61495/chinese-bellows-rectangular-box-and-piston-with-f) - museu (resultado de busca)

**Referencia historica**
- Processo Longquan (patrimonio imaterial nacional): 5 etapas nucleo = martelar/forjar, aplainar e limar, polir, incrustar, temperar; a tradicao completa lista 28 processos (fundir, forjar, esmerilhar etc).
- Forja: bloco de ferro aquecido na fornalha, dobrado e caldeado repetidamente com carburacao ate virar aco denso; contagem de dobras: sem numero confiavel.
- Tempera: lamina a cerca de 750-800 C mergulhada em agua; a temperatura da agua e o tempo decidem dureza x tenacidade. Logo a forja PRECISA de cocho/tanque de agua comprido ao lado da bigorna.
- Fole fengxiang: caixa retangular de madeira (paralelepipedo) com pistao interno empurrado/puxado por haste com cabo; dupla acao = sopra na ida e na volta; bordas do pistao vedadas com penas ou papel; valvulas de aba (flap) nas pontas e um duto lateral que leva o ar a um unico bico apontado para a base da fornalha. Medidas: sem numero confiavel.
- Polimento com pedra de amolar local ('pedra brilhante'), do grosso ao fino; incrustacao: sulcos gravados com agulha de aco e preenchidos com cobre vermelho (sete estrelas da Ursa Maior + dragao voador). Bainha/cabo em madeira huanghuali com ferragens de prata e cobre.
- Lenda fundadora: Ou Yezi (periodo Primavera e Outono) montou a forja junto a um lago no monte Qinxi, com 7 pocos dispostos como a Ursa Maior (resta 1). Em 1930 havia 11 oficinas produzindo 2000+ espadas/ano.
- Combustivel tradicional carvao vegetal; fornalha de oficina e baixa, de tijolo/barro, aberta na frente; fornos de fundicao com chamine alta: sem numero confiavel nas fontes abertas (conhecimento geral, nao verificado nesta pesquisa).

**Interpretacao cartoon**
- Ler a forja em 5 estacoes que contam a historia na ordem: fornalha+fole -> bigorna -> cocho de tempera -> bancada de lima/polimento -> mesa de incrustacao/montagem. Cada estacao com 1 prop heroi grande.
- Fole exagerado: caixa comprida de madeira laqueada vermelho-escura com cintas de bronze, cabo em T grande, bico de cobre; e o prop mais 'chines' da forja, deve ser visivel de longe.
- Fornalha com boca em arco brilhando (Neon/emissive laranja), coifa de tijolo e chamine grossa levemente afunilada e torta; fagulhas e fumaca como particulas.
- Os 7 pocos da Ursa Maior viram motivo do lobby: 7 discos/pocos de pedra no piso em forma de concha, com agua brilhando azul-jade.
- Bigorna superdimensionada sobre toco de tronco com cintas de ferro; marreta e tenaz encostadas com silhueta grossa.

**Adaptacao para o jogo**
- Escala (avatar 5 studs): fornalha 8-10 studs de largura, boca a 3 studs do chao; fole 6-7 x 2 x 2,5 studs; bigorna 3 studs de comprimento sobre toco de 2 studs; cocho de tempera 6 x 1,5 x 1,5 studs. Valores de projeto, nao historicos.
- Modular: fornalha (corpo + coifa + chamine em 2 segmentos repetiveis), fole, bigorna+toco, cocho, rack de tenazes/martelos, pilha de carvao (1 mesh de massa + 3-4 pedacos soltos), feixe de laminas brutas, barril de agua.
- Brilho: brasa e agua do cocho em material emissivo + PointLight quente; manter o resto em tons frios/escuros para o laranja dominar.
- Paleta: tijolo cinza-quente, madeira escura, ferro quase preto com highlight de borda, acentos cobre/bronze e jade da seita.
- Colisao simples em caixa para todos os props; nada de hull detalhado em tenazes/martelos.

**Erros comuns**
- Usar fole sanfonado europeu de couro em vez da caixa de pistao chinesa.
- Bigorna estilo londrino com chifre longo como unica opcao; em oficina chinesa tradicional o bloco e mais simples/retangular (sem numero nem fonte forte; tratar como direcao de arte).
- Esquecer o cocho de agua e a bancada de polimento - sem eles nao parece forja de ESPADA, parece ferreiro generico.
- Tratar katana/tempera com argila japonesa como se fosse jian de Longquan.
- Chamine fina e reta realista: some na silhueta; no cartoon ela precisa ser grossa.

### Anatomia da espada jian (guarda, pomo, borla, inscricoes) e monumentos/pedestais de espada

**Fontes**
- [Jian - Wikipedia](https://en.wikipedia.org/wiki/Jian) - enciclopedia com citacoes (aberta)
- [Longquan Sword Forging Technique (Baidu Baike EN)](https://baike.baidu.com/en/item/Longquan%20Sword%20Forging%20Technique/667521) - enciclopedia (aberta)
- [Longquan Sword (Baidu Baike EN)](https://baike.baidu.com/en/item/Longquan%20Sword/17532) - enciclopedia (resultado de busca)

**Referencia historica**
- Jian = espada reta de dois gumes. Uma mao: lamina 45-80 cm; peso medio 700-900 g para lamina de 70 cm. Duas maos: ate 1,6 m (rara). Jian de bronze do Exercito de Terracota: 81-94,8 cm.
- Lamina em 3 zonas: jianfeng (ponta, estocada e cortes rapidos), zhongren (meio, cortes e desvios), jiangen (raiz, defesa; as vezes com ricasso). Secao com nervura central (crista) e chanfros dos dois lados.
- Guarda curta com abas/lobos pequenos apontando para frente ou para tras (nao e cruzeta larga europeia). Pomo na ponta do cabo para equilibrio e para a mao nao escorregar; historicamente rebitado na espiga.
- Borla presa ao pomo: origem provavel como fiel/cordao de retencao, hoje decorativa.
- Construcao sanmei (3 chapas: nucleo duro entre duas chapas macias) ou wumei (5 chapas). Bronze nas epocas antigas, aco carbono temperado a partir do Han Ocidental.
- Decoracao Longquan: sete estrelas e dragao incrustados em cobre na lamina; bainha e cabo em huanghuali com ferragens de prata/cobre.
- Monumentos/pedestais de espada historicos: sem numero confiavel nem fonte aberta nesta pesquisa; tratar como invencao de direcao de arte apoiada na base sumeru do kit.

**Interpretacao cartoon**
- Proporcao exagerada: lamina mais larga (1,5-2x), crista central bem marcada, guarda com lobos grossos e pomo em anel ou flor bem legivel; borla longa e volumosa na cor da seita.
- Sete pontos de cobre/ouro ao longo da lamina como assinatura visual da Forja Celeste (pode ser emissivo sutil).
- Monumento: espada gigante cravada ponta para baixo em pedestal tipo sumeru (cintura estrangulada + petalas de lotus), com correntes ou fitas; placa de inscricao vertical na frente.
- Inscricao: 2-4 caracteres grandes em selo/relevo dourado na raiz da lamina ou na placa, nao texto miudo.

**Adaptacao para o jogo**
- Espada de suporte (prop): comprimento total 4-4,5 studs (1:1 exagerado com avatar de 5 studs). Monumento central: 25-40 studs de altura para ler do outro lado do lobby. Valores de projeto.
- Um unico mesh de jian com 3 variacoes de cor/ferragem via SurfaceAppearance para popular racks e paredes.
- Borla como mesh separado (pode animar/balancar com script simples ou constraint).
- Pedestal reutiliza o modulo de base sumeru do kit arquitetonico; so trocar a escala e o topo.
- Lamina com metalness/roughness baixo + highlight pintado na crista para ler em cartoon mesmo sem reflexo.

**Erros comuns**
- Lamina curva ou de um gume (isso e dao, nao jian).
- Guarda em cruz larga estilo europeu ou tsuba redonda japonesa.
- Borla na guarda em vez de no pomo.
- Lamina fina demais: some a media distancia no Roblox.
- Inscricao com caracteres inventados/ilegiveis em textura de baixa resolucao; melhor relevo grande e poucos glifos.

### Ponte-lua (Ponte do Cinturao de Jade), margens de lago em jardins chineses (pedra, rochas taihu), pequenas cascatas

**Fontes**
- [Moon bridge - Wikipedia](https://en.wikipedia.org/wiki/Moon_bridge) - enciclopedia (aberta)
- [Jade Belt Bridge - Wikipedia](https://en.wikipedia.org/wiki/Jade_Belt_Bridge) - enciclopedia (aberta)
- [Chinese garden - Wikipedia](https://en.wikipedia.org/wiki/Chinese_garden) - enciclopedia com citacoes (aberta)
- [Gongshi (scholar's rocks) - Wikipedia](https://en.wikipedia.org/wiki/Gongshi) - enciclopedia (aberta)

**Referencia historica**
- Ponte-lua: ponte de pedestres muito arqueada, arco arredondado unico; nasceu funcional (deixar barcas passarem em canais ocupando pouca margem). Em jardim, arco + reflexo na agua parada fecham um circulo = lua cheia. Rampas tao ingremes que algumas tem degraus tipo escada.
- Ponte do Cinturao de Jade (Palacio de Verao, Pequim): erguida em 1750 (Qianlong), marmore e pedra branca, arco unico alto e fino; vao dimensionado para o barco-dragao do imperador; guarda-corpos entalhados com grous e outros animais; a mais famosa das 6 pontes da margem oeste do lago Kunming. Medidas do vao/altura: sem numero confiavel.
- Materiais possiveis de ponte-lua: pedra, tijolo, madeira (inclusive arco tecido de vigas).
- Rochas: 4 criterios Tang para pedra de erudito/taihu = shou (magra/esguia), tou (aberta/vazada), lou (perfurada), zhou (enrugada). Taihu = calcario erodido pela agua do lago Tai; outras: Lingbi (Anhui, escura), Ying (Guangdong). Valorizam assimetria e forma 'desajeitada'.
- Montanha artificial (jiashan) simboliza virtude/estabilidade; auge no Ming; no Qing misturam rocha com terra para parecer natural. Uma unica rocha pode representar uma montanha.
- Agua e o centro do jardim; riachos sinuosos escondidos por rocha e vegetacao; pontes em zigue-zague (nove voltas) como mirantes. No Jardim do Administrador Humilde cerca de 1/5 da area e lago.
- Cascatas pequenas em jardim classico: sem numero confiavel; normalmente saem de dentro do jiashan (conhecimento geral, nao verificado aqui).

**Interpretacao cartoon**
- Arco quase semicircular perfeito para o reflexo fechar o circulo; aduelas (pedras do arco) grandes e legiveis, 1 pedra-chave destacada com emblema da seita.
- Guarda-corpo = mesma balaustrada do kit (pilarete com cabeca entalhada + painel); cabecas dos pilaretes exageradas (nuvem/grou/chama da forja).
- Margem: muro baixo de pedra irregular em blocos grandes com cantos arredondados, alternando com grupos de rocha taihu vertical como pontuacao a cada trecho.
- Taihu cartoon: massa vertical esguia, mais larga em cima que embaixo (instavel de proposito), 3-5 furos grandes atravessando, poucas rugas profundas - nao ruido fino.
- Cascata: 2-3 degraus de lamina d'agua saindo de um nicho escuro no jiashan, espuma branca estilizada na base.

**Adaptacao para o jogo**
- Ponte caminhavel: rampa real ingreme trava avatar; usar degraus baixos (altura <= 1 stud) ou rampa de colisao invisivel mais suave que o visual. Largura util 8-10 studs, vao 20-30 studs. Valores de projeto.
- Modulos: arco (metade espelhavel), tabuleiro com degraus, balaustrada do kit, 2 encontros de pedra. Colisao em caixas/cunhas separadas do mesh visual.
- Agua plana e calma abaixo da ponte para o reflexo/circulo funcionar (ou fake: meio-arco espelhado sob a agua translucida).
- Kit de margem: 3 segmentos de muro de pedra (reto, curva, canto) + 4-5 rochas taihu rotacionaveis + 2 pedras de passo. Rotacao e escala geram variedade.
- Cascata: mesh de lamina com textura rolando (script de offset) + ParticleEmitter de espuma; som em loop.

**Erros comuns**
- Ponte japonesa vermelha de madeira (taiko-bashi laqueada) no lugar da ponte de pedra branca chinesa.
- Arco achatado: o reflexo vira elipse e perde o motivo da lua.
- Taihu como pedregulho redondo macico - sem furos e sem verticalidade nao e taihu.
- Excesso de furos pequenos/ruido: vira queijo e custa triangulos; 3-5 vazados grandes bastam.
- Margem reta de concreto; jardim chines usa borda irregular de pedra com recuos e avancos.

### Pinheiro (Huangshan/penjing), bambu, bordo, ameixeira meihua: silhueta e simplificacao em massas

**Fontes**
- [Pinus hwangshanensis (Huangshan pine) - Wikipedia](https://en.wikipedia.org/wiki/Pinus_hwangshanensis) - enciclopedia (aberta)
- [Chinese garden - Wikipedia (plantas e simbolismo)](https://en.wikipedia.org/wiki/Chinese_garden) - enciclopedia (aberta)
- [Stylized Nature: Vegetation, Animation, Shaders - 80.lv](https://80.lv/articles/stylized-nature-vegetation-animation-shaders) - breakdown de arte de jogo (resultado de busca)
- [Setting Up Trees, Bushes, and Flowers For a Stylized 3D Environment - 80.lv](https://80.lv/articles/setting-up-trees-bushes-and-flowers-for-a-stylized-3d-environment) - breakdown de arte de jogo (resultado de busca)

**Referencia historica**
- Pinheiro de Huangshan: copa muito larga e de topo chato, galhos longos e horizontais; 15-25 m de altura; agulhas 2 por feixe, 5-8 cm; pinhas ovoides 4-6,5 cm; casca grossa, acinzentada, em placas escamosas; cresce em penhascos rochosos ingremes. Exemplar icone: Pinheiro que Da Boas-Vindas (Yingke Song).
- Pinheiro, bambu e ameixeira = 'Tres Amigos do Inverno' (longevidade, integridade/sabedoria, renascimento). Trio ideal para seita marcial.
- Jardins chineses preservam a forma natural e valorizam arvores retorcidas, de aparencia antiga e ananicadas (logica penjing).
- Bambu: colmos retos segmentados em touceira, folhagem concentrada no terco superior (conhecimento geral; sem numero confiavel).
- Meihua: floresce em galho nu e anguloso no fim do inverno, flor de 5 petalas rosa/branca; bordo: copa em camadas com folhas palmadas vermelho-alaranjadas (conhecimento geral; sem numero confiavel).

**Interpretacao cartoon**
- Pinheiro: tronco em S inclinado + 3 a 5 'nuvens' achatadas de folhagem (discos/lentes) em andares desencontrados, um galho longo estendido para o lado como braco de boas-vindas. Verde escuro azulado com topo mais claro.
- Bambu: touceira de 5-9 colmos cilindricos com aneis de no marcados, leve curvatura no topo, folhagem como 3-4 massas alongadas caidas; verde-jade claro.
- Meihua: galhos pretos angulosos em zigue-zague, quase sem folha, flores como aglomerados de bolinhas/petalas rosa - le como caligrafia.
- Bordo: 3-4 camadas horizontais de massa vermelho-laranja, tronco fino bifurcado; ponto de cor quente contra telhado jade.
- Regra geral: silhueta primeiro, 3 valores por massa (sombra, base, luz), nada de folha individual fora da borda.

**Adaptacao para o jogo**
- Tecnica citada nos breakdowns 80.lv: clumps de cartoes (malha de 3 quads cruzados com textura de folha) espalhados sobre um volume, com normais editadas apontando para fora (transferidas de uma esfera via Data Transfer no Blender) para sombreamento suave de massa.
- No Roblox: preferir massas solidas low-poly (blobs facetados/suavizados) + poucos cartoes de borda com alpha; lembrar que alpha so funciona via SurfaceAppearance (licao ja registrada no projeto).
- Escala de projeto: pinheiro heroi 35-50 studs, pinheiro penjing em jardineira 6-10 studs, bambu 25-35 studs, meihua/bordo 15-22 studs.
- 1 tronco + conjuntos de nuvens como MeshParts separados: reposicionar nuvens gera 3-4 variacoes sem novo asset.
- Colisao so no tronco (caixa/cilindro); folhagem CanCollide off e CastShadow avaliado caso a caso.

**Erros comuns**
- Pinheiro conico tipo arvore de natal - o pinheiro chines/huangshan e de topo chato e em andares.
- Bambu como bastoes lisos sem nos nem conicidade; ou folhagem distribuida do chao ao topo.
- Meihua confundida com sakura frondosa: meihua e esparsa, galho anguloso, flor direto no galho.
- Milhares de cartoes alpha sobrepostos: overdraw pesado no mobile e ruido visual.
- Normais de cartao nao editadas: cada plano acende diferente e a copa pisca.

### Lanterna de palacio (gongdeng hexagonal), lanterna vermelha, lanterna de pedra; estandartes de seita e militares; ding/braseiros de bronze; estantes de armas (bingqi jia); postes meihua

**Fontes**
- [Palace lantern - Wikipedia](https://en.wikipedia.org/wiki/Palace_lantern) - enciclopedia (aberta)
- [Ding (vessel) - Wikipedia](https://en.wikipedia.org/wiki/Ding_(vessel)) - enciclopedia com citacoes (aberta)
- [Mei Hua Zhuang (Plum Blossom Poles) - Black Belt Wiki](https://blackbeltwiki.com/mei-hua-zhuang) - site especializado de artes marciais (resultado de busca)
- [Meihua Zhuang - The Poles of Plum Blossom - Shaolin Temple Overseas](https://www.shaolinoverseas.com/articlesbyshifu/meihua-zhuang-the-poles-of-plum-blossom) - site especializado (resultado de busca)

**Referencia historica**
- Gongdeng: formas ortodoxas octogonal, hexagonal e quadrada; esqueleto de madeira nobre; faces de seda fina ou vidro pintadas (ex.: dragao e fenix auspiciosos); origem atribuida ao Han Oriental, auge Sui/Tang; no Qing era presente do imperador a duques e ministros. Dimensoes tipicas: sem numero confiavel.
- Lampada de bronze dourado em forma de serva (achada em 1968): 48 cm, 15,85 kg, manga funciona como duto de fumaca - referencia para luminaria de bronze de interior.
- Ding: tripe redondo (3 pernas) ou fangding retangular (4 pernas), 2 alcas verticais opostas na borda, as vezes tampa; decoracao taotie (mascara de dois olhos) no bojo e pernas, fundo de espirais 'trovao'. Houmuwu ding = maior bronze antigo conhecido (peso: sem numero confiavel nesta fonte).
- Hierarquia por contagem de ding: 9 imperador, 7 senhores feudais, 5 ministros, 3 ou 1 letrados; os Nove Ding lendarios = soberania sobre a China.
- Postes meihua: troncos cravados no chao, 50-150 cm de altura acima do solo; 5 postes em planta de flor de ameixeira (5 petalas); alunos comecam baixo e sobem; versao avancada tem varios 'floroes' de 5 postes afastados cerca de 6 pes (~1,8 m). Diametro: sem numero confiavel.
- Lanterna vermelha, lanterna de pedra, estandartes e estante de armas (bingqi jia): sem fonte aberta nesta pesquisa (teto de chamadas atingido); itens abaixo sao direcao de arte baseada em conhecimento geral, sem numero confiavel.

**Interpretacao cartoon**
- Gongdeng hexagonal em 3 andares legiveis: coroa (topo com 6 bracos curvos terminando em cabeca de dragao/nuvem, cada um com borla), corpo (6 paineis luminosos com moldura de madeira vermelho-escura/dourada), saia (pendente inferior + borla central grande).
- Lanterna vermelha: globo achatado com gomos verticais, aneis dourados em cima e embaixo, franja amarela; usar em fieiras nos beirais e portoes.
- Lanterna de pedra de jardim: base, fuste, caixa de luz vazada, telhadinho com cantos levantados - repete a linguagem do telhado do kit em miniatura.
- Ding/braseiro: tripe gordo, pernas tipo pata curva, 2 alcas altas, faixa taotie simplificada em relevo grande; brasa/chama emissiva dentro. Patio principal pode ter 1 ding gigante central ou 9 pequenos em fila como simbolo de soberania da seita.
- Estandarte: bandeira vertical estreita e longa em haste com travessa no topo, ponteira de lanca com borla, borda serrilhada/chama, 1 caractere ou emblema grande; cores da seita (jade + dourado + vermelho-forja).
- Estante de armas: cavalete de madeira com 2 travessas entalhadas em meia-lua, 5-7 armas de haste em pe (lanca, guandao, bastao) + fila de jian; pes em forma de nuvem. Postes meihua em 5, alturas escalonadas, topos gastos e claros.

**Adaptacao para o jogo**
- Escala de projeto (avatar 5 studs): gongdeng pendurada corpo 3-4 studs + borla 2; lanterna de pedra 6-7 studs; lanterna vermelha 2-2,5 studs de diametro; ding de patio 8-12 studs, braseiro pequeno 3-4; estandarte 14-20 studs; estante de armas 8 x 2 x 7 studs.
- Postes meihua jogaveis: topos a 1,5-4,5 studs (equivalente aos 50-150 cm), diametro 2-2,5 studs para o avatar pousar, espacamento 4-6 studs entre topos (alcance de pulo padrao); 5 em planta de flor, repetir floroes.
- Luz: paineis da lanterna em material Neon ou SurfaceAppearance clara + 1 PointLight quente por lanterna heroi; limitar luzes com sombra para performance, fieiras so com emissivo.
- Pano do estandarte como mesh com dobras modeladas (2 poses) ou animacao leve; face dupla - Roblox faz cull de backface, entao duplicar faces ou dar espessura.
- Um mesh de haste/arma generica reutilizado na estante e nos guardas; ding e braseiro compartilham textura trim de taotie.

**Erros comuns**
- Usar toro japones (ishidoro estilo Kasuga) como lanterna de pedra chinesa sem adaptar telhado/ornamento ao kit.
- Lanterna de palacio como simples cilindro de papel; a leitura vem da coroa com bracos e das borlas.
- Ding com 4 pernas e bojo redondo ou alcas laterais tipo panela; regra: redondo = 3 pernas, retangular = 4, alcas em pe na borda.
- Bandeira horizontal ocidental em mastro; estandarte chines de seita/militar e vertical com travessa e franjas.
- Postes meihua todos na mesma altura e em grade regular - perde a planta de flor e a progressao de treino; e postes finos demais para o avatar pousar.


## Grupo: arquitetura

### telhados wudian/xieshan: hierarquia, juzhe, beiral, canto levantado, telhado x coluna

**Fontes**
- [East Asian hip-and-gable roof (xieshan) - Wikipedia](https://en.wikipedia.org/wiki/East_Asian_hip-and-gable_roof) - enciclopedia (aberta)
- [Architectura Sinica - juzhe (verbete; resumo veio no resultado da busca, fetch deu 403)](https://architecturasinica.org/keyword/k000223) - dicionario academico de arquitetura chinesa
- [Hall of Supreme Harmony - Wikipedia](https://en.wikipedia.org/wiki/Hall_of_Supreme_Harmony) - enciclopedia (aberta)
- [Parameterizing the Curvilinear Roofs of Traditional Chinese Architecture (resultado de busca, nao aberto)](https://www.researchgate.net/publication/343266609_Parameterizing_the_Curvilinear_Roofs_of_Traditional_Chinese_Architecture) - artigo academico

**Referencia historica**
- Xieshan = 9 espigoes: 1 cumeeira principal horizontal + 4 espigoes verticais (descem pelas empenas) + 4 espigoes diagonais (nos cantos). E um telhado de 4 aguas com um triangulo de empena embutido em cada lateral. Wudian (4 aguas puro) = 5 espigoes: 1 cumeeira + 4 diagonais (contagem do wudian: conhecimento geral, nao verificado nesta sessao).
- Hierarquia (conhecimento geral consolidado, nao verificado por fonte aberta aqui): wudian beiral duplo > xieshan beiral duplo > wudian simples > xieshan simples > xuanshan > yingshan. Fonte aberta confirma apenas: xieshan e de uso oficial (palacios, templos, jardins), com variantes beiral simples e beiral duplo (chongyan).
- Juzhe (Yingzao Fashi) = metodo de posicionar as tercas para gerar a curva concava. Dois passos: juwu (define a altura total, do topo da terca do beiral ao topo da terca de cumeeira) e zhewu (rebaixa as tercas intermediarias). O perfil era desenhado em escala 1:10 numa parede (ding ceyang) antes da montagem. Fracoes exatas: sem numero confiavel nesta sessao (de memoria: altura ~1/3 do vao em saloes, ~1/4 em galerias; rebaixo 1/10 da altura na 1a terca e metade a cada terca seguinte - NAO verificado).
- A curva e resultado construtivo: segmentos retos de caibro entre tercas com inclinacao crescente para cima (mais ingreme na cumeeira, mais suave no beiral). Logo: modelar como polilinha de 4-6 segmentos, nao como arco de circulo.
- Canto levantado: a viga de canto inferior (laojiaoliang) sai em 45 graus sobre o dougong de canto; a viga de canto superior (zijiaoliang) assenta sobre ela e projeta mais alem, subindo; os caibros perto do canto abrem em leque e sobem progressivamente ate encostar na viga de canto. Estilo oficial do norte = levantamento contido; sul = ponta muito levantada. Proporcoes numericas: sem numero confiavel.
- Salao da Suprema Harmonia como teto de escala: 11 vaos de largura x 5 de profundidade, 65 x 37 m, ~30 m acima do patio, sobre 3 niveis de base de marmore. Relacao telhado x coluna: sem numero confiavel nesta sessao (observacao geral: em saloes Qing o telhado ocupa aprox. metade ou mais da altura da fachada).

**Interpretacao cartoon**
- Exagerar 3 coisas e so elas: (1) altura/volume do telhado em relacao ao corpo, (2) balanco do beiral, (3) levantamento da ponta do canto. Manter o resto sobrio para nao virar caricatura generica.
- Curva concava legivel a distancia: usar 4-5 segmentos com quebra bem marcada no terco inferior (beiral quase horizontal) e topo ingreme. Silhueta primeiro, telha depois.
- Canto levantado no estilo norte-imperial 'puxado': subir a ponta um pouco mais que o real, mas manter a linha do beiral reta nos 2/3 centrais e so curvar no ultimo vao - e isso que le como palacio e nao como templo do sul.
- Beiral duplo (chongyan) como marcador de hierarquia: salao principal da seita com beiral duplo, pavilhoes secundarios com xieshan simples, galerias com telhado de 2 aguas.

**Adaptacao para o jogo**
- Kit modular: modulo reto de agua de telhado (1 vao), modulo de canto (45 graus, bespoke), modulo de empena xieshan, cumeeira, espigao. 80.lv confirma pratica comum: canto feito cortando a peca reta, espelhando a metade e cobrindo a emenda com telhas individuais.
- Avatar 5 studs: beiral do terreo com face inferior a >= 10-12 studs para a camera de terceira pessoa nao entrar no telhado; balanco do beiral de 4-6 studs da sombra legivel.
- Telhas como normal/relevo em SurfaceAppearance sobre a agua do telhado + uma fileira real de telhas-canal apenas na borda do beiral e nos espigoes (onde a silhueta aparece).
- Colisao: uma caixa/cunha simples por agua de telhado; nao usar colisao precisa na malha curva.

**Erros comuns**
- Curva feita como arco convexo ou arco de circulo uniforme (parece tenda/pagode generico). A curva real e concava e concentrada embaixo.
- Levantar a linha inteira do beiral como 'sorriso' - no estilo oficial do norte so o canto sobe.
- Xieshan sem os 4 espigoes verticais da empena ou com empena triangular rente a parede (a empena fica recuada, sobre a agua lateral).
- Misturar ponta de canto 'rabo de andorinha' do sul/Fujian com pintura e telha imperial do norte.

### dougong: pecas, graus, conjunto de coluna x intercolunio x canto, pintura

**Fontes**
- [Dougong - Wikipedia](https://en.wikipedia.org/wiki/Dougong) - enciclopedia (aberta)
- [Architectura Sinica - tiaojin douke (pingshenke / jiaoke / zhutouke)](https://architecturasinica.org/keyword/k000249) - dicionario academico (resultado de busca)
- [Lateral hysteretic behavior of typical Dou-Gong in Ming-Qing dynasties - npj Heritage Science](https://www.nature.com/articles/s40494-026-02340-x) - artigo academico (resultado de busca)
- [Explosion diagram of Dou-Gong (diagrama explodido)](https://www.researchgate.net/figure/Explosion-diagram-of-Dou-Gong_fig2_369853271) - figura de artigo (resultado de busca)

**Referencia historica**
- Pecas base: dou = bloco de apoio (o grande na base do conjunto assenta na coluna/viga); gong = braco em forma de arco que apoia vigas ou novos bracos acima. Tudo encaixado por sambladura, sem cola nem prego (cavilhas de madeira entre camadas). Cada camada alarga a area de apoio.
- Classificacao Qing dos componentes de um conjunto: dou (blocos), gong (bracos), ang (bracos inclinados/bico), fang (vigas-tirante longitudinais que amarram os conjuntos) e heng (tercas). Sheng = bloco pequeno na ponta do braco; qiao = braco que projeta para fora perpendicular a fachada (definicoes de sheng/qiao: conhecimento geral, nao verificado aqui).
- Tres tipos por posicao (Qing): zhutouke (sobre a coluna), pingshenke (intercolunio, sobre a viga pingbanfang) e jiaoke (canto, sobre a coluna de canto). Pode haver ate 8 pingshenke entre duas colunas.
- Evolucao: ate Tang/Song conjuntos grandes e estruturais; do fim de Song em diante ganham carater decorativo; em Ming/Qing ficam menores e mais numerosos - e o visual 'cinto denso' da Cidade Proibida.
- Grau = numero de passos (tiao/cai) que o conjunto avanca para fora: 3-cai (1 passo), 5-cai (2), 7-cai (3), 9-cai (4). Modulo Qing = doukou (largura da boca do bloco). Correspondencias e medidas exatas: sem numero confiavel nesta sessao.
- Conjunto de canto: alem dos bracos nas duas direcoes ortogonais ha um braco/ang DIAGONAL a 45 graus que carrega a viga de canto (laojiaoliang); os bracos ortogonais de um lado atravessam e viram bracos do outro lado. Pintura: corpo azul e verde alternados entre conjuntos vizinhos, filete claro/dourado nas arestas, fundo (placa entre conjuntos) vermelho - esquema geral, sem fonte aberta nesta sessao.

**Interpretacao cartoon**
- Reduzir a contagem e aumentar o tamanho: 2-4 conjuntos por vao em vez de 6-8, cada um ~1,5-2x maior. Le melhor e custa menos triangulos.
- 3 graus do kit: G1 = 1 passo (bloco + 1 braco cruzado, para galerias/muros), G2 = 2 passos (pavilhoes), G3 = 3 passos com bico de ang apontado para baixo/fora (salao principal). O bico do ang e o detalhe que 'vende' dougong a distancia.
- Chanfro generoso em todos os blocos e a curva 'juansha' na ponta inferior dos bracos exagerada; filete dourado/creme pintado na aresta em vez de geometria.
- Alternancia azul/verde por conjunto da ritmo cromatico barato; para a seita da forja, trocar o filete por ouro-ambar quente mantendo azul/verde como massa.

**Adaptacao para o jogo**
- Um MeshPart por conjunto (nao por peca). Faces internas invisiveis removidas. Conjunto de canto e peca propria com o braco diagonal - nao tentar montar com dois conjuntos retos.
- Fileira de dougong + viga pingbanfang + placa de fundo vermelha como UM modulo por vao, para reduzir instancias.
- A distancia, o cinto de dougong fica na sombra do beiral: garantir contraste com filete claro, senao vira faixa escura.
- Sem colisao nos dougong (CanCollide off, CanQuery off).

**Erros comuns**
- Dougong so na coluna, sem conjuntos no intercolunio (vira estilo Tang/japones, nao Ming-Qing imperial).
- Canto resolvido com dois conjuntos retos se interpenetrando, sem braco diagonal.
- Bracos retos como prateleira, sem a curva inferior nem os blocos sheng nas pontas.
- Conjunto flutuando sem a viga pingbanfang embaixo e sem a terca/fang em cima.

### cumeeira e espigoes, chiwen, bestas de cumeeira, wadang/dishui, caibros e caibros voadores

**Fontes**
- [Imperial roof decoration - Wikipedia](https://en.wikipedia.org/wiki/Imperial_roof_decoration) - enciclopedia (aberta)
- [Chiwen - Wikipedia](https://en.wikipedia.org/wiki/Chiwen) - enciclopedia (aberta)
- [Traditional Chinese Roof: Types, Components, Functions and Ridge Beasts](https://www.lilysunchinatours.com/Ancient-Architecture/Traditional-Chinese-Roof.html) - site especializado/turismo (resultado de busca, nao aberto)

**Referencia historica**
- Fila de bestas no espigao diagonal: abre com um imortal montado em fenix/ave (na ponta, sobre o beiral), seguem as bestas miticas, fecha com um dragao imperial maior (cabeca de besta do espigao) atras.
- Contagem = hierarquia do edificio. Maximo: 9 bestas + 1 figura guardia extra (hangshi, a 10a), configuracao exclusiva do Salao da Suprema Harmonia. Edificios menores usam menos (na pratica numeros impares 3, 5, 7, 9 - os impares: conhecimento geral, nao verificado aqui).
- Bestas citadas pela fonte: touro que afasta o mal, xiezhi, peixe xiayu (chama vento e chuva), suanni (leao mitico), cavalo-marinho, cavalo celeste, leao, chiwen. Ordem canonica completa (dragao, fenix, leao, cavalo celeste, cavalo-marinho, suanni, xiayu, xiezhi, douniu, hangshi): de memoria, nao verificada aqui.
- Chiwen: ornamento nas DUAS pontas da cumeeira principal, corpo truncado tipo peixe-dragao com boca larga mordendo a cumeeira; protecao contra fogo. Evolucao: chiwei (Han, forma de asa/cauda) -> chiwen com feicoes de dragao em Song -> Ming/Qing mais ornado, corpo e cauda enrolados PARA DENTRO. Tamanho/peso do chiwen da Suprema Harmonia: sem numero confiavel.
- Cabo de espada cravado nas costas do chiwen: presente nos exemplares Ming/Qing; lenda popular diz que prende a criatura no telhado (atribuida ao imortal Xu Xun). A pagina aberta NAO cobre esse detalhe - tratar como conhecimento geral nao verificado. Para o tema da seita (espada + forja) e o gancho narrativo perfeito.
- Wadang = disco terminal da telha-capa (convexa) na borda do beiral; dishui = terminal triangular em gota da telha-canal (concava). Alternam 1:1 ao longo do beiral. Sob o beiral: caibros redondos (yanchuan) e, sobre eles, caibros voadores de secao quadrada (feichuan) que estendem e levantam a borda. Definicoes: conhecimento geral; sem numero confiavel de espacamento.

**Interpretacao cartoon**
- Bestas: reduzir para 3 (secundario) e 5 (salao principal), cada uma ~2x maior que o real, silhuetas bem distintas (imortal na ave na frente, dragao grande atras). Nunca usar 9+1: e exclusivo do trono do imperador e polui a silhueta.
- Chiwen grande (altura ~2-3x a da cumeeira), boca mordendo a cumeeira, cauda em espiral para dentro, e o cabo de espada MUITO visivel nas costas - pode ser o logotipo da seita (espada forjada cravada).
- Cumeeira principal grossa e alta, com faixa pintada em relevo; espigoes com 2 degraus: trecho alto (atras da besta grande) e trecho baixo (onde andam as bestas pequenas).
- Borda do beiral com wadang redondos grandes (disco com emblema da seita) e dishui em gota: uma fileira de geometria real, pois e o que fica na altura dos olhos.

**Adaptacao para o jogo**
- Bestas e chiwen como MeshParts separados e reutilizaveis; a fila de bestas pode ser 1 mesh unica por variante (3 e 5).
- Caibros: modulo por vao com caibros redondos + voadores quadrados ja fundidos; pontas pintadas (verde/azul com circulo claro) via textura.
- No canto, caibros em leque: peca bespoke junto com o modulo de canto do telhado.
- Telha jade (verde) para edificios secundarios e telha amarela/dourada so para o salao principal reforca hierarquia por cor (amarelo vidrado = reservado ao imperador segundo a fonte).

**Erros comuns**
- Bestas na cumeeira principal (elas ficam nos espigoes diagonais/verticais, perto da ponta).
- Chiwen virado para fora ou como dragao inteiro de corpo longo; o correto e compacto, virado para o centro, mordendo a cumeeira.
- Ordem invertida: dragao grande na ponta e imortal atras.
- Beiral sem camada dupla de caibros (so uma placa lisa) e sem wadang/dishui - perde toda a leitura de proximidade.

### base sumeru (xumizuo), balaustrada de marmore, danbi, piso de lajes

**Fontes**
- [Hall of Supreme Harmony - Wikipedia](https://en.wikipedia.org/wiki/Hall_of_Supreme_Harmony) - enciclopedia (aberta)
- [The Forbidden City - Baidu Baike (EN)](https://baike.baidu.com/en/item/The%20Forbidden%20City/986258) - enciclopedia (resultado de busca)
- [Places and buildings within the Forbidden City - Facts and Details](https://factsanddetails.com/china/cat15/sub94/entry-6465.html) - compilacao com citacoes (resultado de busca)

**Referencia historica**
- Terraco dos Tres Grandes Saloes: base sumeru de marmore branco em 3 niveis; borda de cada nivel com paineis de balaustrada, balaustres e cabecas de dragao. Numeros (resultado de busca): plataforma ~25.000 m2, 1.415 paineis vazados, 1.460 balaustres entalhados com dragoes/fenix em nuvens, 1.138 cabecas de dragao.
- As cabecas de dragao (chishou) sao gargulas funcionais: ha furos sob a pedra de soleira dos paineis e dentro das cabecas; em chuva forte todas jorram. Ficam sob cada balaustre, com uma maior em cada canto (a do canto maior: conhecimento geral).
- Ordem das molduras do xumizuo Qing, de baixo para cima (de memoria, Liang Sicheng/regras Qing - NAO verificado nesta sessao): guijiao (pe) -> xiafang (faixa inferior) -> xiaxiao (gola inferior, petalas de lotus para baixo) -> shuyao (cintura recuada, com pilaretes/nos de fita) -> shangxiao (gola superior, lotus para cima) -> shangfang (faixa superior). Proporcoes: sem numero confiavel.
- Balaustrada (nomes de memoria, nao verificados): wangzhu = balaustre/poste com cabeca entalhada (dragao/fenix em nuvem no nivel imperial); xunzhang = corrimao; jingping = 'vaso' que sustenta o corrimao no vao vazado; huaban/lanban = painel; baogushi = pedra-tambor em voluta que arremata o fim da balaustrada no pe da escada; diyu = soleira.
- Danbi/yulu = laje inclinada entalhada (dragoes em nuvens sobre ondas e montanhas) no eixo central da escadaria, ladeada por dois lances de degraus; ninguem pisa nela. Dimensoes da grande laje atras do Baohedian: sem numero confiavel nesta sessao.
- Piso: patio em tijolo cinza/lajes em fiadas; caminho imperial central em pedra clara levemente elevado; interior com 'tijolos dourados' (jinzhuan) escuros polidos. Medidas: sem numero confiavel.

**Interpretacao cartoon**
- Xumizuo com poucas molduras e bem gordas: pe, gola lotus, cintura funda, gola lotus, tampo. A cintura recuada com sombra forte e o que faz ler como 'sumeru' e nao como caixa.
- Cabecas de wangzhu grandes e simplificadas (botao de nuvem/chama de forja) - 1 balaustre a cada ~1 avatar de distancia; cabecas de dragao so nos cantos e sob alguns postes.
- Danbi como peca-heroi: relevo alto de dragao + espada/bigorna da seita, com leve brilho; escadas laterais para o jogador.
- Marmore nao branco puro: creme quente com AO azulada, para nao estourar na iluminacao do Roblox.

**Adaptacao para o jogo**
- Avatar 5 studs: corrimao a ~3-3,5 studs, degrau <= 1 stud de altura (ou rampa invisivel de colisao sobre degraus visuais) para o Humanoid subir sem travar.
- Modulos: trecho reto de base (1 vao), canto externo, canto interno, trecho com escada, balaustrada reta, poste, arremate baogushi, chishou. Balaustrada: painel+poste como 1 modulo.
- Danbi sem colisao andavel 'bonita': colisao em rampa lisa, relevo so visual (normal map + geometria baixa).
- Piso: grandes placas com textura de lajes em tiling (SurfaceAppearance), juntas no albedo/normal; caminho central como faixa de geometria separada 0,1-0,2 stud mais alta.

**Erros comuns**
- Base como paralelepipedo liso ou com molduras simetricas sem cintura recuada.
- Balaustrada de madeira vermelha estilo jardim sobre base imperial de marmore (mistura de registros).
- Cabecas de dragao apontando para cima ou usadas como enfeite no corrimao; elas saem horizontais da base, abaixo do poste.
- Escada central unica sem danbi e sem baogushi no arremate.

### portas e janelas geshan, trelicas, pregos de porta e pushou, menzan; pintura caihua (hexi/xuanzi) e queti

**Fontes**
- [Hexi Caihua - Wikipedia](https://en.wikipedia.org/wiki/Hexi_Caihua) - enciclopedia (aberta)
- [Caihua - Wikipedia](https://en.wikipedia.org/wiki/Caihua) - enciclopedia (resultado de busca)
- [Technical analysis of mid-Qing official-style architecture polychrome paintings in Chongjing Hall - J. Asian Architecture and Building Engineering](https://www.tandfonline.com/doi/full/10.1080/13467581.2026.2624879) - artigo academico (resultado de busca)
- [SCMP - Forbidden City red gates with golden door nails: rules on number and colour](https://www.scmp.com/news/people-culture/trending-china/article/3353579/china-forbidden-citys-red-gates-golden-door-nails-subject-rules-regarding-number-colour) - imprensa (resultado de busca)

**Referencia historica**
- Pregos de porta (mending) por regulamento do Ministerio das Obras Qing, por folha: 81 (9x9) = imperial; 49 (7x7) = principes, dourado sobre vermelho; 25 (5x5) = oficiais menores, bronze/ferro sobre porta verde ou preta. Impar = yang; 9 = maior impar, exclusivo do imperador.
- Hexi caihua = grau mais alto: muitos dragoes dourados sobre fundos azul e verde; usado nos edificios principais do patio externo e palacios altos do interno. Xuanzi = segundo grau (flor em redemoinho), amplo em palacios e residencias de altos oficiais. Terceiro grau Suzhou/Su-style para jardins (conhecimento geral).
- Composicao tripartida da viga: fangxin (centro: dragao/fenix dourado com borda de nuvem/folhagem), zhaotou (trecho intermediario) e gutou (ponta, junto a coluna). Proporcao classica 1/3-1/3-1/3 do comprimento: de memoria, nao verificada. No hexi as divisoes sao linhas quebradas em zigue-zague; no xuanzi o zhaotou leva as flores em redemoinho (de memoria).
- Regra cromatica geral (de memoria): azul e verde alternam entre viga superior e inferior e entre vaos vizinhos; ouro nas linhas e nos dragoes define o grau (mais ouro = mais alto). Colunas, portas e paredes em vermelho; tudo acima do capitel em frios azul/verde - contraste quente embaixo/frio em cima.
- Geshan = folha de porta-painel: parte superior em trelica (gexin), faixa estreita intermediaria (taohuanban) e almofada cega inferior (qunban). Trelica de maior grau = sanjiao liuwan linghua (losangos/flor de 6 petalas com 3 direcoes cruzadas); graus menores = grade quadrada, faixas retas. Proporcao trelica:almofada ~6:4 - de memoria, sem numero confiavel.
- Pushou = aldrava em mascara de besta com argola, par centrado na altura do peito; menzan = pinos decorativos (tipicamente 2 ou 4, hexagonais/florais) salientes no lintel acima da porta, que prendem a travessa do gonzo. Queti = misula entalhada no encontro viga-coluna, triangular alongada, pintada azul/verde com ouro. Todos: conhecimento geral, sem fonte aberta nesta sessao.

**Interpretacao cartoon**
- Pregos: NAO usar 9x9 literal em escala cartoon - usar 5x5 ou 7x7 com cabecas grandes e douradas; le como 'portao imperial' sem virar ruido. Se quiser a referencia de lore, 9x9 so no portao principal da seita.
- Caihua simplificado em 3 zonas chapadas: gutou (faixas verticais), zhaotou (1 motivo grande), fangxin (emblema da seita: espada/chama em ouro sobre azul). Linhas de ouro grossas; sem microdetalhe.
- Trelica grossa: barras 2-3x mais largas que o real, padrao linghua reduzido a 3-4 repeticoes por folha; fundo com papel/luz quente emissiva para o lobby a noite.
- Pushou oversized (cabeca de leao/besta de forja com argola) como ponto focal da porta; queti gordo com voluta unica.

**Adaptacao para o jogo**
- Trelica: geometria real so nas portas-heroi; no resto, plano com alpha. Licao do projeto: alpha confiavel so via Transparency/ColorMap com alpha em SurfaceAppearance - testar ordenacao de transparencia atras de vidro/luz.
- Caihua como trim sheet: uma textura em faixa com gutou-zhaotou-fangxin mapeada em vigas de comprimentos diferentes (esticar so o fangxin, manter pontas em escala).
- Pregos como geometria (hemisferios low-poly) numa unica mesh da folha; pushou mesh separada reutilizavel.
- Portas do lobby: folhas abertas fixas (sem colisao na passagem) com vao >= 8 studs de largura para fluxo de varios jogadores.

**Erros comuns**
- Numero par de pregos ou grade retangular arbitraria; portas imperiais sem menzan no lintel.
- Pintura de viga quente (vermelho/laranja) acima das colunas - o correto e azul/verde/ouro em cima, vermelho embaixo.
- Caihua continuo sem a divisao em tres zonas, ou dragoes em edificios secundarios (hierarquia: hexi so no salao principal, xuanzi no resto).
- Trelica japonesa (shoji quadriculado fino) no lugar de linghua/grade chinesa.

### grandes portoes (Portao do Meridiano, torres de portao, paifang) e placas bian'e

**Fontes**
- [Meridian Gate - Wikipedia](https://en.wikipedia.org/wiki/Meridian_Gate) - enciclopedia (resultado de busca)
- [Meridian Gate: The Entrance to the Forbidden City - Google Arts & Culture / The Palace Museum](https://artsandculture.google.com/story/meridian-gate-the-entrance-to-the-forbidden-city-the-palace-museum/NQUxZvrUFVtvAg?hl=en) - museu (Palace Museum; resultado de busca)
- [Meridian Gate, Wumen - TravelChinaGuide](https://www.travelchinaguide.com/attraction/beijing/forbidden/meridan_gate.htm) - site especializado (resultado de busca)
- [Creating Modules for Stylised Environments - 80.lv](https://80.lv/articles/creating-modules-for-stylised-environments) - breakdown de arte de jogo (resultado de busca)

**Referencia historica**
- Portao do Meridiano (Wumen): planta em U (corpo central + duas alas que avancam para o sul), ~38 m de altura total, 5 pavilhoes no topo = 'Torre das Cinco Fenix' (Wufenglou).
- Pavilhao central: 9 vaos de largura, beiral duplo, ~60,05 m x 25 m. Cada ala: galeria de 13 vaos de beiral simples ('torres asa de andorinha') ligando dois pavilhoes quadrados de telhado piramidal (cuanjian) de beiral duplo nas extremidades.
- Logica de torre de portao: embasamento macico de alvenaria vermelha com passagens em arco/tunel + plataforma com balaustrada + salao de madeira completo por cima (colunas, dougong, telhado). Numero de passagens do Wumen (3 frontais + 2 laterais ocultas): conhecimento geral, nao verificado aqui.
- Paifang/pailou: portico autoportante descrito por 'vaos-colunas-telhadinhos' (ex.: 3 vaos, 4 colunas, 7 lou). Vao central mais largo e alto; cada lou tem mini-dougong e mini-telhado proprios; colunas com pedras de abraco (baogushi/jiagan shi) na base; placa central com inscricao. Contagens tipicas: sem numero confiavel nesta sessao (busca nao retornou fonte).
- Bian'e: placa horizontal sobre a porta ou sob o beiral, com nome do edificio; em edificios imperiais de beiral duplo costuma ser VERTICAL (doubian, moldura em relevo com dragoes), pendurada inclinada para a frente entre os dois beirais. Fundo azul com caracteres dourados no padrao imperial; placas Qing da Cidade Proibida bilingues chines-manchu. Conhecimento geral, sem fonte aberta nesta sessao.
- Hierarquia de cor do conjunto: muro/embasamento vermelho, marmore branco na base e balaustrada, caihua azul-verde-ouro sob o beiral, telha amarela vidrada (reservada ao imperador) no topo.

**Interpretacao cartoon**
- Portao da seita = Wumen em miniatura: embasamento vermelho alto com 1 arco grande (+2 menores), U raso abracando a praca de spawn, 3 pavilhoes em vez de 5 (central beiral duplo + 2 quadrados piramidais nas pontas).
- Paifang de 3 vaos / 4 colunas como marco de entrada do caminho principal: telhadinhos exagerados, colunas grossas com pedra-tambor grande na base, placa central com o nome da seita.
- Bian'e vertical inclinada para a frente entre os beirais do salao principal, moldura de dragao/chama dourada, fundo azul profundo, caracteres dourados com leve emissive - ancora de leitura a distancia.
- Embasamento com talude (paredes levemente inclinadas para dentro) exagerado: da peso e 'fortaleza' sem detalhe extra.

**Adaptacao para o jogo**
- Tunel do portao: largura >= 12 studs e altura >= 14 studs para camera e multidao; iluminacao interna propria (PointLight quente) para nao virar buraco preto.
- Embasamento = Parts simples texturizadas (barato, colisao perfeita); so o pavilhao de cima usa o kit de MeshParts. Reaproveitar 100% do kit (coluna, dougong G2/G3, telhado, balaustrada).
- Paifang: 1 mesh para estrutura + telhadinhos reutilizando o modulo de beiral em escala reduzida; colisao so nas colunas.
- Texto da placa: SurfaceGui com fonte caligrafica ou textura propria; manter caracteres chineses genuinos e revisados (nao pseudo-hanzi).

**Erros comuns**
- Torii japones ou portao coreano no lugar de paifang (paifang tem telhadinhos com dougong e multiplos vaos).
- Pavilhao de portao sem embasamento macico, ou embasamento sem talude e sem balaustrada no topo.
- Placa horizontal pequena colada na parede num edificio de beiral duplo; o padrao imperial e vertical, inclinada, entre os beirais.
- Caracteres inventados/ilegiveis na placa; leitura tradicional e de cima para baixo (vertical) ou da direita para a esquerda (horizontal).
