# Menus V2 — dependências, implementação e revisão

Módulo de origem: `before/ReplicatedStorage/ExpeditionUI/Menus.lua`.
Implementação: `src/ReplicatedStorage/ExpeditionUI/Menus.lua`.
Nenhuma escrita em Studio foi realizada pelo responsável deste módulo. Compilação Luau, inspeção renderizada e teste funcional integrado devem ocorrer no fluxo de QA do agente principal.

## Contrato preservado

Exports mantidos: `store`, `areas`, `rates`, `summon`, `forge`, `progress`, `settings`, `daily`, `render`.

Dependências: `Theme`, `Config`, `MonetizacaoConfig`, `Players.LocalPlayer`; os módulos continuam sendo obtidos das mesmas localizações. Não há dependência externa dos caminhos dos Frames antigos identificada neste módulo; sua construção é interna e o controlador chama os exports.

| Tela | Estado usado | Ações / integração |
|---|---|---|
| Picaretas | `picareta`, `picaretasCompradas`, `moeda`, `ctx.storeTab` | `ComprarPicareta`, `EquiparPicareta`, `ctx.confirm`, `ctx.nextPickaxe` |
| Mochilas | `mochilaTier`, `moeda` | `ComprarMochila` com confirmação; mochila adquirida representa tier já alcançado |
| Passes / produtos | `passes`, `compras`, catálogo `Mon` | `ComprarRobux`; ID zero permanece indisponível / Em breve; Starter permanece visível com estado Adquirido após compra |
| Ilhas | `areas`, `moeda`, `CurrentAreaId` | `ctx.nextArea`, `ctx.buyArea`, `ctx.travel("area", id)`, atalhos Loja/Forja |
| Invocar | `bannerArea`, `luckyMult`, `pity`, `giroGratis`, `index.pets`, `summonBusy` | `ctx.nearBanner`, `ctx.startSummon`, `ctx.travel("gacha", id, true)`, `ctx.onSummonProgress`, `Config.chancesGacha` |
| Último resultado | `lastSummonResults`, `showLastSummon` | Botão condicional que reapresenta os resultados pelo controlador |
| Forja | `mochila`, `carregado`, `capacidade`, `multMoedas`, `passes.AutoSell` | `Vender`; composição pelo `Config.infoMinerio`, acesso permanece validado pelo servidor |
| Missões | `missoes`, `questArea`, `areas` | `ResgatarMissao`, individual/coletivo; feedback só para respostas bem-sucedidas |
| Diário | `daily.dia`, `daily.disponivel`, `Config.DAILY` | `ResgatarDaily`; recompensa descrita pelo catálogo; removidos valores artificiais de coinBurst |
| Coleção | `index.pets`, `index.hats`, `Config.Pets`, `Config.Hats` | Busca local, categorias, paginação; nenhum remote novo |
| Configurações | atributos listados abaixo | `SetAttribute` local, `ResgatarCodigo` via ctx.invoke; rascunho do código no contexto |

Atributos existentes preservados: `MusicEnabled`, `SomMineracaoEnabled`, `SomInterfaceEnabled`, `LobbyVFXEnabled`, `ExpeditionBlurEnabled`. Expõe `ExpeditionEffectsEnabled` existente e o contrato novo `ReducedMotion`. Preferências são descritas como sessão atual, sem alegar persistência que não existe.

APIs novas acordadas com o controlador: `T.dropdown(parent,name,x,y,w,h,items,current,onPick,opts)` e `T.emptyState(parent,name,title,description,x,y,w,h,actionLabel,onAction)`. APIs antigas permanecem em uso para compatibilidade.

## Problemas estruturais corrigidos

- Loja: hero ocupava toda altura e comprimia catálogo em cards com texto/CTA ao lado de 116 px de arte. Agora a melhoria imediata ocupa cabeçalho compacto; catálogo usa linhas largas com compra/equipamento e dados legíveis. Em largura menor que 620, arte/nome e ação/preço ficam em linhas distintas.
- Passes: removeu banner promocional, brilho recorrente e hierarquia cromática excessiva. Produtos seguem mesma grade, conteúdo, duração, propriedade e estado de compra.
- Ilhas: texto deixou de disputar espaço com imagem de fundo inteira; thumb separado, nome/estado/requisito/preço/CTA têm regiões próprias.
- Invocação: a revisão de fidelidade substitui o hero baixo por palco dominante, rail de banners temáticos, três personagens e rótulos sobre a composição; x1/x10 e duas barras de garantia ficam integrados à base. A coleção completa abre em popup. Chances usam distribuição real com sorte aplicada. Giro grátis continua sendo descontado do x10.
- Forja: resumo da venda e capacidade são prioritários; lista mostra composição e atalhos ao próximo passo. Layout estreito empilha conteúdo. Total usa multiplicador real; valores na lista são base.
- Missões: lateral larga e tabs só numéricas foram substituídas por seletor com nome das ilhas; textos longos recebem duas linhas, recompensa/CTA são separados no mobile. Claim All contabiliza apenas sucessos reais.
- Diário: removidas alturas calculadas que comprimiam reward cards abaixo do conteúdo e um personagem ilustrativo não relacionado à recompensa. Ciclo rolável, estado e regra explícitos; não inventa moedas ganhas.
- Coleção: mantém totais e contagem por ilha, acrescenta grid de descobertas, categorias/busca/paginação. No máximo 18 previews por página; itens desconhecidos recebem cadeado.
- Configurações: conteúdo passou a ser integralmente rolável; códigos não ficam mais em y610 fora do body estreito. Controle de movimento reduzido, efeitos, atalhos e estado vazio do código.

## Revisão estática concluída

1. Revisados offsets e transições de layout em larguras 400, 700 e 1132, incluindo body largo com alturas 400 e 220. Abaixo de 380 de altura, menus não-Summon têm scroll externo com conteúdo legível de 620. Summon usa composição mínima de 530 de altura no desktop ou 636 na variante estreita; em viewports menores, o conjunto permanece acessível via scroll. CTAs usam pelo menos 52 unidades virtuais; x1/x10 usam 60. A renderização em dispositivo continua necessária para verificar tipografia e touch reais.
2. Mantidos todos os exports antigos. Nenhum remote de gameplay/dados novo. Nenhuma escrita em catálogo, saldo ou inventário.
3. `action` mantém guarda por operação em `ctx.menuPending`; não depende da sobrevivência do botão durante redraw. Reativa o botão após falha e renova estado caso o botão seja reconstruído durante a requisição.
4. Código vazio/desabilitado aceita reativação após digitar; aplica trim antes de enviar e preserva rascunho. Erro de resgate não gera recompensa falsa.
5. Nenhum Heartbeat, RenderStepped, shine, breathe, rays ou emitter adicionado. Previews deste módulo são estáticos; conexões locais pertencem aos controles e são destruídas junto deles.
6. Index limita quantidade de previews; busca atualiza apenas conteúdo, preservando foco no TextBox. Resultado vazio oferece limpar busca.
7. BuyArea permanece sequencial; compra monetizada ID zero bloqueada; Summon exige ilha liberada, proximidade e saldo. A validação definitiva continua no servidor.
8. Revisão crítica reduziu espaços negativos no mobile, eliminou duplicidade de informação promocional e preservou áreas clicáveis separadas. Fechar, foco global, restrição de duas janelas, manutenção de scroll no redraw e efeitos do Theme são responsabilidades do controlador/Theme.

## Primeira revisão artística — substituída após nova orientação do usuário

- Direção: composições anime com recortes de personagens, arte das ilhas, facetas inclinadas e fundo tonal. Os benchmarks orientam a qualidade; não houve cópia literal de layout.
- Summon: 2 personagens em largura menor que 620 e 3 no desktop; usa `Config.PetArte` do banner atual, sem revelar um secreto não descoberto. O grid continua completo e usa `T.tile` com raridade. Não acrescenta loop de animação.
- Diário: ícone principal aumentado de 54 para 92; recompensas compostas têm ícones secundários correspondentes ao catálogo. A cor considera a maior raridade efetiva da recompensa; o estado resgatado reduz contraste. Nenhum personagem específico é mostrado como promessa de um pet aleatório.
- Loja: melhoria imediata com placa angular discreta; produtos têm ícone maior e composição tonal. Ilhas usam a arte como thumbnail com faixa temática; textos e ações ficam abaixo.
- Coleção: `T.tile` acompanha a linguagem de raridade do Theme; itens desconhecidos continuam ocultos.
- Superfícies compostas aplicam uma região de leitura escura sobre a arte. Confirmação final de contraste, corte dos assets e encaixe de texto depende da inspeção renderizada do agente principal.

## Revisão de fidelidade estrutural — 17/09/2026

As imagens locais Daily e Summon fornecidas pelo usuário foram abertas e inspecionadas diretamente com `view_image`. A rejeição da primeira revisão motivou mudanças de composição, além das mudanças de Theme coordenadas pelo agente principal.

- Summon: rail vertical com thumbnails reais das seis ilhas e títulos/estados; no retrato, faixa horizontal rolável. O palco ocupa a maior parte da janela com fundo da ilha, três bustos grandes, rótulos de nome/raridade sobre os personagens, título expressivo, x1/x10 verdes de 60 de altura e duas barras de pity. Personagens secretos desconhecidos continuam ocultos.
- As chances detalhadas e o catálogo completo são popups independentes acessíveis por CHANCES e UNIDADES. Último resultado e viagem mantêm seus caminhos. Não há catálogo de sete cards idênticos ocupando a tela inicial.
- Diário: fundo quase preto, faixa e contorno laranja, quatro colunas no desktop, recompensa grande inclinada, DIA flutuante sobre a borda e faixa de estado/claim ocupando a base. O botão do dia e o botão do cabeçalho compartilham a guarda de requisição. Dias futuros usam cadeado; dias resgatados têm faixa clara e texto de sucesso.
- Nenhuma regra de recompensa, preço, saldo, chance ou produto foi alterada. Não foi criada oferta/cronômetro artificial; o relógio do diário continua baseado na liberação diária existente.
- Nenhuma escrita em Studio pelo responsável deste módulo. Compilação e inspeção integrada continuam sob responsabilidade do agente principal.

## QA integrado ainda necessário

- Compilar módulo e executar todos os exports com Theme novo no Studio.
- Inspecionar todas as telas em desktop/compacto/retrato: nomes longos, textos, alvos de toque, padding e scroll até o final.
- Equipar picareta adquirida; falha por saldo; confirmar/cancelar compra; não realizar compra Robux real para validar aparência.
- Viajar e abrir forja, vender mochila vazia/cheia respeitando acesso real; comparar valor de composição/total ao retorno do servidor.
- Invocar perto/longe/bloqueado; x1 gratuito, x10, progresso, cancelamento externo e último resultado.
- Missão incompleta/completa/resgatada, resgate coletivo parcial; diário disponível/indisponível e código inválido/válido sob o procedimento de teste do projeto.
- Coleção conhecida/desconhecida, busca vazia/sem correspondência e navegação entre páginas.
- Persistência durante a sessão e restauração do estado ao navegar são verificações separadas da renderização.
