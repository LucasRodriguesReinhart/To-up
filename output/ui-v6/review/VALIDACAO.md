# UI V6 — Anime Mining Simulator

## Implementação
- Escala de 65% a 115%, em passos de 5%, com preferências independentes para PC e celular. Padrões: 85% e 80%. Salva no perfil existente.
- Ajuste da tipografia que ignorava a redução da interface; refinamento de cabeçalhos, bordas, barras, botões, fundo e raridades, mantendo a organização.
- Personagens com pose articulada e movimentos pequenos; sem balanço do modelo inteiro. Respeita a opção de reduzir movimentos.
- Forja portátil exige o passe 1983332510, com validação no servidor. Venda gratuita permanece disponível junto do NPC Ignis. O passe portátil não concede venda automática.
- Nove passes reais configurados; imagens oficiais via rbxthumb e preços consultados no Roblox. Pet equip +3, hat equip +3, inventário +50/+300/+1000 cumulativos.
- Aviso de chegada compacto, com duração de cinco segundos, escondido ao abrir menus.

## Verificação
- 20 arquivos compilam e correspondem às fontes locais.
- 18 verificações de lógica passaram: validação da escala, limite e campos permitidos, acesso à forja, tentativa de burlar o contexto do NPC, bônus de slots/inventário e sorte.
- Ícones: nove de nove carregados no cliente. Preços: nove consultas respondidas pelo Roblox.
- PC: HUD, inventário, loja, configurações, forja bloqueada, diário, missões e invocação.
- Celular horizontal: iPhone 17 Pro e Samsung Galaxy A06; escala de 65%, 80% e 115% revisada no iPhone. Capturas Samsung em 80%.
- Caminho real até Ignis testado: viagem gratuita, aproximação e abertura por interação; botão de venda disponível no NPC.
- Raiz e pés do preview permaneceram fixos em uma amostragem de 2,1 segundos; cabeça e mãos tiveram movimento articulado.
- Sessão final sem ferramentas de teste: inventário aberto pela tecla H, escala PC 85% restaurada e console sem erros.
- Script e gancho temporários de teste removidos. Backup: ServerStorage.BeforeUIV6_1789676670.

## Limites e decisões
- Não foram feitas compras reais, vendas de minérios nem consumo de unidades durante os testes.
- Lucky mantém ×1,25. Lucky+ usa provisoriamente ×1,50, pois os passes não tinham descrição; juntos resultam em ×1,875. A pergunta sobre o balanceamento ainda aguardava resposta ao preparar esta entrega.
- A comparação visual não afirma equivalência de qualidade ou cópia exata: mantém os modelos, conteúdo e organização do Anime Mining Simulator.
- As capturas da forja bloqueada usam a simulação local de não possuir o passe; o bloqueio também foi testado independentemente no servidor.
- A imagem externa de referência é exibida pelo endereço original no HTML e exige internet. Não foi incorporada como asset do jogo.

## Referências
- Anime Expeditions: https://allthings.how/anime-expeditions-summer-siege-how-to-get-the-new-units-and-fishing-rods/
- Roblox MarketplaceService: https://create.roblox.com/docs/reference/engine/classes/MarketplaceService
- Roblox assets e miniaturas: https://create.roblox.com/docs/projects/assets
