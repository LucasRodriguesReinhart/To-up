# Referências adicionais fornecidas pelo usuário

Fontes: três screenshots anexados e `08c79851-dcb9-4c1d-a99b-fefbf11f7863/pasted-text.txt`. Análise visual direta, separada por imagem. Não houve edição de fontes nesta subtarefa.

Os screenshots permitem avaliar composição, cor, profundidade, textos, enquadramento e estados visíveis. Não permitem concluir duração de transições, sons, hover, fluidez ou qualidade de animações. Qualquer proposta de motion abaixo depende de implementação e teste próprios.

## 1. Diário — arquivo terminado em `10c8569d-2b17-41b5-927d-9b4d2e3f0ca8.png`

O painel principal usa preto sólido com uma moldura laranja, distinguindo-se do cenário azul escurecido. O título laranja, os números dos dias e a borda externa formam uma única família de cor; o corpo permanece neutro. Cards laterais combinam uma ilustração escurecida, título curto e personagem/item recortado à direita. Isso dá identidade a cada evento sem depender de caixas de texto longas.

O grid comunica três estados por meios diferentes: texto `CLAIMED` + faixa clara/verde; cadeado grande + rodapé cinza para bloqueado; moldura especial no marco do dia 7. A ordem temporal permanece estável, inclusive com o início da próxima linha aparecendo na borda inferior, sugerindo scroll.

Princípios aplicáveis: dias em posições estáveis; destaque real do dia atual; prêmio grande e nome/quantidade secundários; concluído com check e texto; bloqueado com motivo curto. Para Anime Mining Simulator, um prêmio de mineração pode ter um recorte de cristal e faixa de recompensa dourada, enquanto a navegação do diário continua ciano.

Riscos a evitar: o cadeado tapa boa parte do prêmio, a repetição de `CLAIM` parece acionável mesmo em itens bloqueados, e os muitos botões do HUD seguem visíveis atrás do modal. Não copiar o botão fechar triangular nem alertas vermelhos em todas as categorias. Na nossa versão, deixar o prêmio identificável e usar `Amanhã` / `Em 2 dias` como estado de bloqueio.

## 2. Unidades — arquivo terminado em `e36ba5e6-27e5-433b-9616-a99de4d9dabf.png`

A composição separa três responsabilidades: coleção à esquerda, apresentação grande da unidade no centro e ficha de atributos à direita. O personagem ocupa uma área muito maior que seu card; isso dá importância ao item selecionado. A família violeta conecta o fundo, a aba ativa e a aura do personagem, enquanto a ficha permanece escura para leitura.

Os cards têm rostos grandes, nível no canto superior, check verde de equipamento, cadeado e marcador `NEW`; esses sinais independem da borda de raridade. Os atributos da ficha têm valor forte à direita e identificador à esquerda. A capacidade e o desequipar permanecem no rodapé da coleção. A equipe atual aparece separada, em uma fileira estável.

Princípios aplicáveis: aumentar o retrato para preencher a área de arte; reservar espaço opaco para nome/nível; distinguir selecionado de equipado; manter capacidade e ações de equipe no rodapé. A prévia principal pode sugerir um pequeno palco escuro com recorte de cristal e cor de raridade atrás da silhueta. Uma fonte de corpo simples pode coexistir com um título mais expressivo.

Riscos a evitar: fundo violeta claro em tela inteira reduz o contraste do modelo e compete com a ficha; há muitos comandos laterais sem agrupamento; vários cards pequenos têm nome e custo sobrepostos ao rosto. Não copiar o inventário de tela cheia: o usuário priorizou gameplay visível. Nossa seleção/detalhes precisa funcionar em uma janela compacta e virar detalhe expansível em portrait.

## 3. Invocação — arquivo terminado em `07cb71e3-ed9a-44fb-84fd-96877dc66c4b.png`

A imagem dos personagens é a informação dominante. Os recortes atravessam a composição e um personagem aparece maior que os demais, comunicando a unidade de destaque. A faixa violeta facetada do título cria uma silhueta própria. Os botões de invocar estão juntos na base da imagem, diretamente acima das barras de pity. Isso conecta ação e progresso sem obrigar a procurar informações em cantos diferentes.

A seleção de banners usa cards ilustrados à esquerda; moedas ficam em uma linha acima; chance, informação e pity são visualmente diferentes da ação de compra. O centro escuro permite texto branco e personagens coloridos. A imagem vai até a borda e possui profundidade, em vez de parecer uma thumbnail solta.

Princípios aplicáveis: uma imagem dominante por banner; preview maior da unidade em destaque; fundo temático subordinado; custo/moeda e chances ao lado das ações x1/x10; pity agrupado embaixo dessas ações. Usar nossa identidade de cristal e mineração em pequenos recortes da faixa e do palco.

Riscos a evitar: a loja de Robux ocupa toda a lateral e compete com o banner; a mistura de verde, amarelo, ciano, magenta e violeta nos CTAs elimina prioridades; ilustrações cruzam os botões e os nomes. Não transportar esse excesso para nosso jogo. Preservar uma ação principal ciano, secundárias escuras e monetização em área própria.

## Cinco decisões para a UI atual

| Decisão | Motivo extraído das referências | Aplicação concreta |
|---|---|---|
| 1. Cabeçalho com uma assinatura visual curta | Faixas laranja/violeta identificam rapidamente a tela | Faixa ou canto facetado de cristal no header, cobrindo apenas a zona do título; corpo navy/grafite. Ciano é a identidade, cor da página é apoio. Não aplicar textura/gradiente a toda superfície. |
| 2. CTA realmente dominante | Invocar/Resgatar se destacam por contraste e posição, não apenas pelo texto | `T.button` deve separar primary/secondary: primary com preenchimento ciano mais presente e texto ink; secondary em bg2/bg3; disabled neutro. Reservar ouro ao dinheiro/recompensa. |
| 3. Arte integrada ao card e ao palco | Rostos e recortes grandes dão valor aos itens | No card, arte ocupa aproximadamente os dois terços superiores, com recorte que preserva rosto. No detalhe/banner, fundo temático escurecido + personagem maior + área limpa sob o nome. Sem glow em todos os itens. |
| 4. Três estados independentes | Referências usam check, cadeado e moldura, evitando depender só de cor | Raridade = faixa/borda + nome; equipado = check e palavra; selecionado = borda interna clara ou marcador ciano. Bloqueado = cadeado pequeno + razão, sem tapar toda a imagem. |
| 5. Informação utilitária em posições estáveis | Capacidade/ações na base da coleção e pity sob invocação reduzem busca | Capacidade, slots e ações de equipe fixos no painel; preços e pity imediatamente junto de x1/x10; detalhes podem rolar sem mover os comandos importantes. Em mobile, converter organização, não encolher tudo. |

Essas decisões mudam o peso da arte e dos componentes sem abandonar a arquitetura atual. O resultado não precisa reproduzir o roxo dominante, o X triangular, a loja lateral ou os mesmos símbolos das referências.

## Revisão estática do Theme atual

Snapshot revisado: SHA256 `84C02F3BBCF9716573F38FEED9C1D5C74944E32CC57158E08902F76F92ACF3D9`. Linhas abaixo se referem à versão lida; root está trabalhando no mesmo arquivo.

### Visual

- `T.button` (~503–528) preserva legibilidade, mas o preenchimento colorido usa `tone:Lerp(P.bg0,.56)`, tornando primário próximo de secundário. Aumentar o contraste de hierarquia exige uma variante explícita, não clarear todos os botões. Com os tokens atuais, ciano misturado a bg0 em .56 tem contraste aproximado 5.46:1 com P.text. Mistura em .18 cai para 2.21:1 com P.text, mas sobe para 8.22:1 com P.ink. Portanto mudar simultaneamente preenchimento e texto do primary.
- `T.chip` (~674–692) mede texto com FredokaOne apesar de exibir BuilderSans. Trocar a fonte de medição pelo token correto evita folgas/encolhimento injustificados. Chips `solid` dourados usam texto branco; branco sobre gold puro tem contraste aproximado 1.60:1. Para badges claros, texto ink é mais legível.
- `T.tile` (~346–357) e `T.rarityFrame` (~749–758) já limitam a cor de raridade à faixa e a seleção à borda. São uma base limpa; não precisam voltar a glow integral. O card precisa ganhar valor principalmente com enquadramento da arte e hierarquia de nome/atributos.
- `T.rarityFrame` mudou o retorno de `r` para `st,r`. Os callers encontrados no pacote ignoram o retorno, então não há falha ativa demonstrada; preservar o retorno antigo evita surpresa a outros consumidores futuros.
- `T.shadow` (~295) cria um irmão estático: posicionamento/size/AnchorPoint posteriores do painel não sincronizam automaticamente a sombra. Na shell atual há reposicionamento específico durante resize; conferir novos headers/previews que alterem esses valores depois de criar a sombra.

### Movimento reduzido e custo

- `T.tween` (~137) agora encurta as novas animações para .001 quando motion está desligado; `bindInteraction`, `pop`, `enter`, `toggle`, `iconButton` e `rarityFrame` já estão mais consistentes que a versão anterior.
- `T.shine`, `T.breathe`, `T.sparkles` e a prévia 2D animada verificam `motionEnabled()` só na criação. Tweens infinitos já existentes continuam se o atributo mudar enquanto o componente permanecer vivo. Registrar cancelamento por mudança de preferência ou usar um gerenciador central; não acrescentar um Heartbeat por componente.
- A prévia 3D (~928–936) cria `RenderStepped` e verifica somente `v.Parent`; não interrompe rotação ao mudar ReducedMotion e continua se um ancestral ficar invisível. Acrescentar guarda de preferência/visibilidade no ciclo ou desconectar quando oculta. A conexão já é destruída corretamente ao destruir o ViewportFrame.
- `T.countTo` (~394–403) usa TweenService diretamente e mantém animação mesmo em reduced motion. É menos crítico que rotação/partículas, mas pode fixar valor final quando reduzido e cancelar tween anterior do mesmo label para evitar disputa de números.
- `T.roundButton` (~537) ainda faz escalas próprias 1.1/.9; os usos atuais encontrados não chamam esse helper. Se permanecer público, migrar para bindInteraction; não reintroduzi-lo nos novos menus.

## QA visual orientado pelas referências

Conferir desktop e portrait com estes critérios: primeiro olhar encontra título/arte/ação nessa ordem; imagem principal não cobre custo nem CTA; rostos são identificáveis no menor card; selected/equipped/locked continuam distinguíveis sem cor; texto em botões claros usa ink; cadeado não apaga a recompensa; nenhum header facetado invade botão fechar; todos os painéis mantêm a mesma família de superfície. Testar movimento reduzido com um preview/reveal já aberto e novamente ao reabrir, distinguindo os dois casos.
