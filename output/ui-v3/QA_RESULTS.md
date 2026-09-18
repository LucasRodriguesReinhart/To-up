# Verificação UI V3 — 17/09/2026

## Implementação

- Theme: botões planos, abas, hierarquia de fontes e componentes compartilhados; API preservada.
- Inventory: grade/palco/ficha; modelos completos; filtros em popup; ações desktop abertas; detalhe mobile com rolagem e ações fixas.
- Menus: invocação em três colunas e diário com um único cabeçalho; moeda e saldo visíveis; ajustes responsivos em viagens e abas de loja.
- ExpeditionClient: HUD lateral, equipe/recursos centralizados, escala mínima 1, cabeçalhos e composição de janelas.
- Notify e IslandTransition: fontes fixas com reflow, revelação em colunas no formato horizontal e conteúdo rolável quando necessário.
- AutoMinerar: texto e posição do controle adaptados; algoritmo de mineração preservado.

## Evidência em Play

- Modelos 3D Muzan, Madara, Kakashi e Itachi renderizados com rosto/roupa. Boros conferido apesar dos bounds importados anormais. A câmera usa limites do corpo, sem ampliar bustos ou ocultar roupa pelos bounds.
- Desktop 1919×1080 e notebook 1365×768; portrait 400×776 e formato horizontal 843×390 em simulação de resolução; tablet iPad 1022×767. A área útil desconta o inset do Roblox. Capturas HD retornadas pelo conector medem 1143×643 e representam a viewport HD.
- Inventário: seleção de UID, abrir filtros, alternar catálogo/itens, detalhe mobile e retorno; equipamento retirado, reposto e ordenado com Melhores. Equipe final: Muzan e dois Tomioka, igual à inicial.
- Viagem normal até o banner: área 1, transição encerrada, invocação habilitada quando próximo. Custos e pity provenientes do estado real.
- Loja, viagens, missões, ajustes, itens, invocação e diário: checagem de texto no desktop e portrait. Cortes encontrados em abas da loja, título de viagens e botões de inventário do tablet foram corrigidos; repetição das telas afetadas sem overflow.
- Revelação visual testada em portrait e paisagem, com CTA de 52px. Fixtures somente de UI, sem conceder itens. Banner aguardou o inventário, apareceu após fechar, pausou durante invocação, retomou e encerrou; callbacks de banner observados exatamente uma vez por aviso.
- Dez fontes compiladas. Console das sessões finais sem erros de UI; saída apenas dos serviços de dados, áreas e mineração.
- Ao encerrar o último Play, o módulo anterior `Core.IslandTravel:67` registrou `PersistentPerPlayer player isn't in datamodel` no evento de saída do jogador. O aviso ocorreu no encerramento, fora dos módulos de UI; a viagem durante Play foi concluída. Esse módulo de servidor não foi alterado nesta revisão visual.
- Perfil conferido após testes: HUD com 54.4B moedas, mochila 550/67.5K, quatro unidades existentes e equipe original restaurada.
- Scripts temporários V3ViewportProbe e UIV3VisualQA removidos. Play e simulador encerrados ao final.
- Persistência confirmada pela saída nativa do Studio às 06:34:23.917: `Saved new changes in "Anime Mining Simulator" to Roblox.` Dez fontes comparadas com o Studio por tamanho e Adler-32 normalizados, todas idênticas e compiladas; backup com dez fontes inertes confirmado.

## Limites

Não foram feitas compras, giros de gacha, fusões ou resgates consumindo o perfil para validar estética. Não foi realizado teste multiplayer, medição de FPS nem teste em aparelho físico. A revisão preserva os remotes, configurações econômicas e integração de áudio; estes limites não equivalem a uma certificação completa do backend.

As capturas mostram os itens reais da conta. Não foram fabricadas unidades para preencher a grade. A aprovação estética final pertence ao usuário; a revisão registra diferenças concretas em relação à versão rejeitada e às referências.
