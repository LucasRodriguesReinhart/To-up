# Revisão V4 — feedback de 17/09/2026

Implementação instalada no place 101959830085647, experiência Anime Mining Simulator.
Salvamento confirmado no Output do Studio: `Saved new changes in "Anime Mining Simulator" to Roblox.` às 14:28:37 da sessão. Salvar não equivale a publicar uma nova versão para os jogadores.

## Mudanças
- HUD: moedas no alto à esquerda, mochila logo abaixo, força à direita, mineração contínua como ícone junto da equipe, engrenagem no canto inferior esquerdo. Invocar e atalho G removidos do HUD.
- Celular horizontal: menu em duas fileiras de três ícones acima do joystick, força fora do botão de pular, inventário com personagem e detalhes simultâneos. Ações principais de alimentar/equipar medidas em 44,25 px no teste com escala 0,75.
- Fontes LuckiestGuy/FredokaOne/GothamBold, contornos, botões com brilho/facetas, barras com acabamento comum. Layout do diário preservado.
- Inventário e hats: ações coloridas e visíveis, prévia 3D com movimento de repouso, redução de movimento respeitada. Modelos surgem após um pequeno intervalo para evitar o primeiro frame desmontado.
- Alimentar/fundir: seis seletores cumulativos até Mítico; limpar seleção ao trocar de limite; equipados, favoritos e protegidos excluídos; revisão obrigatória antes da chamada ao servidor.
- Loja do HUD mostra passes e ofertas. Picaretas/mochilas usam a tela Equipamentos; o atalho de viagem aponta para o local da loja com Ignis.
- Invocações: entrada pelos gachas, abertura de estrela antes dos resultados; resultado continua determinado pelo servidor.
- Viagem: imagem e nome da ilha; identificação central desaparece cinco segundos após chegar. Removido aviso redundante de viagem concluída.
- Missões refeitas com seleção de ilha, progresso, recompensa e estados de resgate. Avisos/coleta, banner de conquista e revelação rara revisados.

## Verificação executada
- Os sete scripts alterados compilaram após a instalação final.
- Capturas reais em Play de HUD, inventário, hats, filtros, alimentação, lojas, missões, diário, configurações, áreas, notificações e revelação.
- Inventário e invocação também inspecionados em layout horizontal compacto durante a revisão.
- iPhone 11 e iPhone 17 Pro em horizontal; TouchEnabled verdadeiro, LandscapeSensor. Na checagem do iPhone 17 Pro, viewport 749×361 e interseção força/botão de pular falsa.
- Clique em Até Mítico selecionou uma cópia mítica disponível (+1,2K XP); Até Comum voltou a zero. Os três equipados não entraram na lista. Não houve confirmação de consumo.
- Callback da estrela retornou `QAStarComplete=true` e `RevealOpen=false`.
- Movimento do modelo central medido entre frames; abertura da revelação verificada visualmente após acomodação do rig.
- Atlas final 119470718103729 autorizado para a experiência e validado com IsLoaded=true, reserva oculta e captura visual.
- Último console de Play continha somente mensagens de inicialização, sem erro dos scripts da UI.
- Fixture UIV4_QA removida, Play encerrado e simulador devolvido ao viewport padrão.
- Backup de sete fontes originais em ServerStorage.BeforeUIV4_Feedback_20260917 e na pasta before.

## Limites e pendências
- Ícones oficiais dos passes/boosts: aguardando o envio informado pelo usuário. IDs comerciais já não configurados continuam como Em breve; não foram inventados IDs nem feitas compras.
- Não houve consumo real de inventário, compra, resgate econômico, teste multijogador ou aprovação estética do usuário.
- Os nomes muito longos de itens continuam abreviados nos cards pequenos; detalhes e rolagem permanecem disponíveis.
- A prévia é uma sequência de capturas estáticas de teste, sem áudio. Não é uma gravação das animações nem uma nova apresentação integral das 28 etapas do questionário.

## Arquivos
- `src`: sete fontes finais e Config de referência (Config não alterado).
- `assets/ui-icons-refined.png`: atlas final; ferramenta embutida imagegen, prompt em assets/PROMPT.txt.
- `preview`: capturas reais. O arquivo Areas.png foi capturado antes de mudar o texto do atalho Equipamentos para Equipamentos · Ignis e direcioná-lo à viagem; o restante do layout é o mesmo.
