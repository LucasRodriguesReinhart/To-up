Status: REVERTIDO a pedido do usuário. A estrutura anterior foi restaurada no Studio a partir de ServerStorage.BeforeGuiEditable_1789069773. Os arquivos desta pasta permanecem somente como histórico da migração desfeita.

Registro original: as interfaces foram migradas diretamente para o Roblox Studio conectado (Anime Mining Simulator, placeId 101959830085647).

COMO EDITAR AS INTERFACES
Todas as telas e os modelos visuais usados pelo jogo ficam em StarterGui.

MinaHUD > ResponsiveHUD
  Moedas: valor e ícone de dinheiro.
  Mochila: retrato, nome, capacidade e barra.
  MenuLateral: botões Loja, Pets, Inventário, Áreas, Config. e Som.
  Hotbar: picareta.
  AreaAtual, Boost, Avisos: notificações e bônus.
  PainelInventario: abas, grade, detalhes e botões.
  PainelGamepasses: loja do botão Loja.
  PainelIgnis e PainelMochilas: interfaces das interações existentes.
  PainelConfiguracoes: preferências.

MinaHUD > Templates
  LinhaLista, ItemInventario, LinhaAtributo, Aviso, InventarioVazio.
  IconesItens: desenhos dos itens; ImagemItem: miniatura do catálogo.
  Edite o modelo para alterar todos os itens gerados.

SummonGui > Root > Conteudo
  Layout da invocação de pets.
SummonGui > Templates
  CardTemplate, BarraTemplate e EstrelaTemplate.

IslandTransition > Fundo
  Fundo e título da transição entre ilhas.

InterfacesMundo > Templates
  VidaMinerio, VidaChefe, VoltarLobby, TituloArea, PlacaIlha e brasões.
InterfacesMundo > PlacasExistentes
  Placas do lobby, portais, NPC e gachas.
  O atributo CaminhoOriginal identifica cada placa.
  Esses modelos ficam desativados aqui; o servidor os copia para as peças.
  AtivarNoMundo controla a visibilidade das placas existentes.

Edite fora do Play para manter as alterações.
Use Visible para visualizar um painel fechado e volte a false ao terminar.
Mantenha os nomes dos objetos referenciados pelos controladores.
Posição, tamanho, fonte, imagens, cantos, bordas e cores-base ficam nos objetos.
Textos de saldo, nomes de itens, raridades, preenchimentos e estados são atualizados pelo jogo.
Cores de estado específicas também podem ser editadas nos atributos dos botões/barras.
O atributo EscalaAutomatica de MinaHUD controla a adaptação da tela.
Roblox CoreGui (menu do Roblox, chat e controles nativos) é administrado pelo Roblox.

Verificação realizada
- HUD carregado com moeda, mochila, retrato e hotbar.
- Inventário de hats e pets, seleção e detalhes, abas, loja de gamepasses e configurações.
- Invocação aberta sem realizar sorteios; cartões, chances e estrelas carregados.
- Alternância de música e painel de picaretas.
- Alterações temporárias de posição, tamanho de fonte e cor feitas em StarterGui persistiram em Play.
- Alteração temporária do template de vida apareceu nos minérios.
- 152 barras de vida (146 minérios e 6 chefes), 64 placas/brasões nas ilhas e 21 placas estáticas.
- Renascimento manteve uma única instância de cada tela e os controladores ativos.
- Sem erros no console das duas sessões de teste.
- Alterações temporárias de teste restauradas; Studio devolvido ao modo Edit.
- Backup anterior no Studio: ServerStorage.BeforeGuiEditable_1789069773.

Os arquivos Lua desta pasta são cópias dos controladores e construtores atualizados.
Os objetos visuais editáveis estão no StarterGui do projeto aberto.
