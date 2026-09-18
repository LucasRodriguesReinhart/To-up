# Referências visuais e medidas — UI V3

Pesquisa em 17/09/2026. As três imagens fornecidas e as três capturas V2 foram reabertas com view_image. Capturas web de Anime Expeditions e Anime Vanguards foram abertas e inspecionadas no navegador. Nenhuma alteração de fonte ou Studio nesta pesquisa.

**Conclusão:** a V2 repetiu cores, mas alterou as proporções. Sua ficha e seu palco ficaram largos, os banners estreitos, os cabeçalhos repetidos e os personagens viraram bustos ampliados. As referências mostram corpos, poses, diferentes tipos de botão e maior densidade de informação em regiões menores.

## Método

Retângulos anotados pela borda visível, tolerância aproximada de 2–4 px. Formato `x,y,w,h`; origem no canto superior esquerdo do arquivo. Percentuais calculados exatamente por x/W,y/H,w/W,h/H; casas decimais não significam precisão subpixel. Contornos de modelos e glifos são estimativas separadas. Não se conhecem os UDim/Insets/FontFace internos.

Dimensões confirmadas dos arquivos: Diário1920×1065; Inventário1920×1080; Invocação1920×943. As três capturas V2 medem1143×643. Diário/Inventário incluem barras do sistema; Invocação tem outra proporção. Para comparação, priorizar medidas dentro do painel. Não tratar percentuais verticais de arquivos com proporções diferentes como equivalentes.

## Inventário — anexo do usuário

[Original](</C:/Users/lucas/AppData/Local/Temp/codex-clipboard-e36ba5e6-27e5-433b-9616-a99de4d9dabf.png>) · [V2](</C:/Users/lucas/OneDrive/Desktop/To up/output/ui-v2/screenshots/inventory.png>)

| Região | Pixels x,y,w,h | Percentuais x,y,w,h |
|---|---|---|
| Cabeçalho | `0, 24, 1920, 111` | `0.00, 2.22, 100.00, 10.28` |
| Busca | `48, 161, 395, 54` | `2.50, 14.91, 20.57, 5.00` |
| Grid visível | `49, 231, 509, 677` | `2.55, 21.39, 26.51, 62.69` |
| Card | `50, 232, 122, 121` | `2.60, 21.48, 6.35, 11.20` |
| Ficha | `1551, 180, 312, 429` | `80.78, 16.67, 16.25, 39.72` |
| Rodapé coleção | `48, 909, 510, 113` | `2.50, 84.17, 26.56, 10.46` |
| Equipe | `632, 899, 655, 107` | `32.92, 83.24, 34.11, 9.91` |
| Ações circulares | `774, 175, 375, 72` | `40.31, 16.20, 19.53, 6.67` |

Quatro colunas, cards quase quadrados122×121, intervalo horizontal~4px. Busca e dois botões de ícone estão numa única linha. Cinco linhas completas de cards aparecem antes do rodapé de coleção. O número real de itens determina preenchimento; não fabricar itens para reproduzir densidade.

A ficha ocupa16,25%W. Comandos rápidos aparecem como quatro círculos sobre o modelo; comandos de manutenção ficam à direita como texto+ícone, fora da ficha. A referência não usa barras retangulares iguais para todas as ações.

O modelo tem cabeça, torso, braços, arma e pernas, em pose, com oclusão entre volumes, aura atrás e chão/reflexo. Isso comprova aparência tridimensional, não a API usada. Corpo/arma ocupam aproximadamente20–22%W e46–49%H, deixando fundo ao redor. A V2 mostra busto frontal cortado no tórax, suave e ampliado.

| Diferença | Referência | V2 | Consequência |
|---|---|---|---|
| Grid |509/1920=26,51%W|~416/1143=36,40%W|Coleção proporcionalmente1,37× mais larga. Reduzir na composição AV.|
| Ficha |312/1920=16,25%W|~306/1143=26,77%W|Ficha proporcionalmente1,65× mais larga. Separar ações da tabela.|
| Abas |Largura próxima do rótulo|Duas abas enormes ocupando toda linha|Dimensionar pelo conteúdo; não inventar categorias.|
| Personagem |Corpo/pose/chão|Busto frontal ampliado|Câmera de corpo inteiro, sem ampliar thumbnail.|
| Controles |Círculos, texto+ícone e botão coletivo|Barras lilás semelhantes|Preservar diferenças de forma e posição.|

## Invocação — anexo do usuário

[Original](</C:/Users/lucas/AppData/Local/Temp/codex-clipboard-07cb71e3-ed9a-44fb-84fd-96877dc66c4b.png>) · [V2](</C:/Users/lucas/OneDrive/Desktop/To up/output/ui-v2/screenshots/summon.png>)

| Região | Pixels x,y,w,h | Percentuais x,y,w,h |
|---|---|---|
| Rail | `87, 229, 393, 532` | `4.53, 24.28, 20.47, 56.42` |
| Banner | `87, 229, 393, 123` | `4.53, 24.28, 20.47, 13.04` |
| Faixa título | `576, 190, 650, 90` | `30.00, 20.15, 33.85, 9.54` |
| Cena | `532, 285, 856, 458` | `27.71, 30.22, 44.58, 48.57` |
| x1 | `762, 637, 224, 57` | `39.69, 67.55, 11.67, 6.04` |
| x10 | `993, 637, 222, 57` | `51.72, 67.55, 11.56, 6.04` |
| Chances | `561, 650, 194, 42` | `29.22, 68.93, 10.10, 4.45` |
| Pity | `551, 701, 405, 28` | `28.70, 74.34, 21.09, 2.97` |
| Ofertas | `1438, 252, 338, 518` | `74.90, 26.72, 17.60, 54.93` |

Banners largos/baixos:393/123=3,195. Rail/cena=393/856=45,91%. V2: banners~172/72=2,389; rail/cena~172/801=21,47%. A V2 estreitou pela metade a relação lateral/centro e forçou títulos sobre thumbnails pequenas.

Cena central:856×458, razão1,869. V2:~801×448, razão1,788. O problema maior é ocupar44,58%→70,08% da largura da captura e ampliar os bustos. Na referência, centro e laterais têm poses distintas; tronco/braços permanecem visíveis. Na V2, cabelo/rosto enormes chegam ao rodapé, com imagem suave diante de texto nítido.

x1/x10 na referência:~224×57, cada um26,17% da largura da cena; intervalo7px. V2:~272×43, cada um33,96% da cena. A V2 tornou os botões mais largos e proporcionalmente baixos. Chances/Info na referência têm42px de altura versus57px dos principais. Não uniformizar todos.

Pity de referência:405×28, altura6,11% da cena. V2:~382×17, altura3,79%. A V2 empilha custo, preço e frase de garantia enquanto afina o próprio progresso. Reunir preço+moeda nos botões e números nas barras.

Alvos derivados: banners com razão3,0–3,3; principais25–27% da cena e11–13% de sua altura; pity5–6%. Manter torso e braços dos três modelos. Se a coluna lateral do AMS tiver catálogo em vez de ofertas, dimensioná-la explicitamente; não ocupar sua largura ampliando personagens. Não inventar produtos indisponíveis.

## Diário — anexo do usuário

[Original](</C:/Users/lucas/AppData/Local/Temp/codex-clipboard-10c8569d-2b17-41b5-927d-9b4d2e3f0ca8.png>) · [V2](</C:/Users/lucas/OneDrive/Desktop/To up/output/ui-v2/screenshots/daily.png>)

| Região | Pixels x,y,w,h | Percentuais x,y,w,h |
|---|---|---|
| Modal | `430, 230, 1060, 606` | `22.40, 21.60, 55.21, 56.90` |
| Categorias | `126, 311, 324, 451` | `6.56, 29.20, 16.88, 42.35` |
| Faixa título | `461, 255, 371, 59` | `24.01, 23.94, 19.32, 5.54` |
| Grid visível | `460, 345, 990, 488` | `23.96, 32.39, 51.56, 45.82` |
| Card | `460, 345, 240, 230` | `23.96, 32.39, 12.50, 21.60` |
| Faixa estado | `461, 533, 238, 41` | `24.01, 50.05, 12.40, 3.85` |
| ClaimAll | `1001, 261, 145, 47` | `52.14, 24.51, 7.55, 4.41` |

Preto com contorno laranja fino, separado por preto. Faixa do título ocupa35% da largura do modal, perto do texto; claim pequeno separado. Categorias ilustradas ficam fora do painel principal. Card tem razão1,043, estado ocupa17,83% da sua altura. Nome/quantidade pequenos no topo e item cercado por espaço preto.

A V2 duplica título, subtítulo, abas, outro título e regra. O grid começa194px abaixo do topo do modal:194/536=36,19%. Na referência começa115px:115/606=18,98%. Referência mostra duas linhas completas+início da terceira; V2 mostra cerca de1,5 linha. O card V2 já tem proporção próxima; aumentá-lo piora esse problema.

Próxima versão: título único, grid começando entre18–21% da altura total, quatro colunas desktop, faixa de estado18–20% do card. Arte deve representar recompensa: hats não são mochila; pet não é uma estrela sem identificação. Prêmio aleatório exige símbolo próprio ou identificação explícita, sem prometer personagem específico.

## Anime Expeditions — capturas web realmente vistas

| Fonte | Observação |
|---|---|
|[Inventário LDPlayer](https://www.ldplayer.net/blog/anime-expeditions-tier-list.html) · [imagem](https://files.ldrescdn.com/rms/ldplayer/process/img/263728ebb7ba4bbca038993195c4a8881784379410.png?x-oss-process=image%2Fresize%2Cw_960%2Fformat%2Cwebp)|Janela preta/dourada compacta; busca na linha do título;5colunas×4linhas visíveis;~60% largura interna em grid,~33% ficha com personagem do peito às pernas e3atributos na base; coluna estreita de ícones e ações coletivas embaixo. É diferente do inventário fullscreen AV.|
|[Summon update1.0](https://www.lolga.com/de/news/anime-expeditions-update-10-warriors-saga-new-units-east-town-code-combat-guide) · [imagem](https://www.lolga.com/uploads/images/news/New-Units-Details-Six-Warriors-Arrive.png)|Faixa ciano curta;3abas superiores; ofertas/serviços à esquerda;3modelos com torso/cintura e poses. Pity empilhado à esquerda inferior, moeda à direita. Preço+ícone nos2botões verdes. Captura recortada ao menu não mede ocupação da tela.|
|[HUD LDPlayer](https://www.ldplayer.net/blog/roblox-anime-expeditions-codes.html) · [imagem](https://files.ldrescdn.com/rms/ldplayer/process/img/24be372e7c7a4217877012d9ce7a7f5e1784378831.png?x-oss-process=image%2Fresize%2Cw_960%2Fformat%2Cwebp)|Esquerda2colunas de quadrados ícone+rótulo, Store/Events largos nas pontas; direita1coluna. Carteira imediatamente acima de6slots centralizados; XP fino abaixo. Centro e chão visíveis. Não há faixa com8palavras pequenas no rodapé.|

Fontes de terceiros, não execução dos builds atuais. A página do inventário está atualizada em setembro/2026 mas usa captura/texto de julho; HUD também vem de artigo de julho. LOLGA é comercial e foi usado somente para observar sua captura, sem validar ofertas.

## Anime Vanguards — confirmação externa

- [HUD Twinfinite, setembro/2024](https://twinfinite.net/guides/anime-vanguards-trade-value-list/) · [imagem vista](https://twinfinite.net/wp-content/uploads/2024/09/anime-vanguards-trade-value-list.jpg?fit=1200%2C675): em1200×675, bloco esquerdo~155×330(12,9%W×48,9%H); quadrados~74×78 em2colunas; direita1coluna; carteira/equipe central inferior~35%W. Confirma organização lateral histórica, não build atual.
- [Summon update5, abril/2025](https://www.sportskeeda.com/roblox-news/anime-vanguards-update-5-patch-notes) · [imagem vista](https://staticg.sportskeeda.com/editor/2025/04/31166-17446972918636-1920.jpg): rail+palco+ofertas,3modelos com torso/pernas; principais violeta, pity acima. Posição e cor históricas diferem: priorizar o anexo do usuário.
- Busca de inventário também retornou [montagem comercial histórica](https://cdn-offer-photos.zeusx.com/40dbbb8a-5729-49dd-b570-122ce034b9c6.jpg), aberta e excluída das métricas porque junta várias telas. Duas imagens AllThingsHow eram ilustração/cenário e foram excluídas. O screenshot do usuário é a fonte canônica do inventário AV neste documento.

## Tipografia, bordas e controles

**Família não identificada.** Não presumir Fredoka porque a V2 a usa. Comparar uma candidata com as mesmas palavras: `Summon x1`, `Day 7`, `Units`, `Unequip All`, números e nomes longos. Observar desenho e contraformas dos glifos, peso e espessura do contorno.

Caixa varia por função: tabs AV são maiúsculas pequenas; nomes/título de banner usam iniciais maiúsculas; botões summon usam caixa mista; CLAIMED é maiúsculo grande. A V2 aplicou maiúsculas em excesso. Na imagem Summon, título do banner tem~1,8–2× a altura dos glifos do CTA; nomes~1,2×; auxiliares~0,7×. São relações visuais estimadas, não TextSize recuperado.

Contorno protagonista~2–3px no anexo original, menor nos metadados; preto rente à letra, sem sombra esfumaçada larga. Molduras grid/ficha~1–2px; banners selecionados~3–4px. Não substituir combinação de borda escura+linha colorida por stroke grosso universal. Não confundir tamanho de forma visível com área de toque.

Há controles realmente diferentes: botões principais coloridos, chances/info menores, círculos de ícone AV, coluna de ícones AE, comandos sem caixa. A fileira uniforme de retângulos lilás da V2 não reproduz esse sistema. No mobile, aumentar alvo interativo ou rearranjar regiões; não encolher toda a composição.

## Critérios para o próximo desenho

1. Escolher AV ou AE por tela. Não combinar grid largo AE, palco fullscreen AV e ficha larga V2 na mesma largura.
2. Conferir retângulos/proporções antes de brilho/texturas. Usar viewport com mesma proporção para comparação.
3. Modelo com corpo e pose; thumbnail pequena continua retrato, palco não. Faces nítidas e margem de cabelo/ombros/braços.
4. Uma linha de busca/filtros desktop; ações da equipe no rodapé do grid; equipe central inferior.
5. Daily com um título e2linhas completas no desktop equivalente; não ampliar cards para compensar cabeçalho repetido.
6. HUD com navegação lateral de ícones, carteira sobre equipe e centro livre. Usar recursos e categorias reais do AMS.
7. Cor é local: AV inventário violeta, Daily preto/laranja, Summon escuro/violeta; AE inventário preto/dourado, Summon ciano. Não misturar todos os cabeçalhos numa mesma tela.

As recomendações históricas de navy sóbrio, modais obrigatoriamente pequenos e raridade apenas em faixa foram superadas pelo pedido de semelhança. Inverter para brilho/ampliação em tudo também não resolve: as proporções, o corpo dos modelos e os diferentes controles fazem parte da referência.
