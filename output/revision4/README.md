# Ilhas restantes — revisão 4

Aplicado no Roblox Studio em Anime Mining Simulator (place 101959830085647).

- Área 3 / Monte Natagumo: casarão em dois níveis, dojo, torii, bambus, glicínias, teias, espadas Nichirin, rio, cascatas e ambiente ao entardecer.
- Área 5 / Grand Line: porto com navio e velas, cais acessível, armazém, farol, tesouro, palmeiras e água tropical.
- Área 6 / Cidade Z: avenidas e faixas de pedestre, prédios, Associação dos Heróis, monumento, grua de construção e canais.
- Todas usam o padrão de Plastic/Studs e árvores originais, praça de mineração, terraços, pontes, cercas, placas e lanternas.
- Os gachas originais foram redimensionados e posicionados nos terraços. A operação é idempotente e integrada ao gerador.
- Mantidos IDs das áreas, temas, HP, recompensas e regras de desbloqueio. Cada uma das três ilhas passou a usar 24 posições de minério planejadas, no padrão das ilhas criadas antes.
- A área final retorna ao lobby; os outros portais usam a verificação de desbloqueio do servidor existente.

Verificação em Play: 21 rotas principais e acesso aos 72 minérios com Pathfinding Success; abertura real dos três gachas com E; viagens 3→4 e 5→6; retorno 6→lobby; iluminação do lobby restaurada; nenhuma compra realizada; execução final sem erros de console.

O cenário final também está construído no modo Edit. A câmera foi deixada em Grand Line.
Cópias dos scripts nesta pasta; dependem dos modelos, GUIs e demais scripts existentes no jogo.
Backup anterior: ServerStorage.BeforeRemainingIslands_1789006688.
As alterações foram aplicadas no Studio e não foram publicadas.

