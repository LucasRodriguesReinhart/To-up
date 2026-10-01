# Revisão aplicada no Roblox Studio — 9/9/2026

Projeto: Anime Mining Simulator, place 101959830085647.

## Entrega

- Mineração: seleção pelas peças visíveis do minério; aproximação até a superfície da hitbox; alcance compartilhado entre cliente e servidor; bloqueio de golpes através de paredes e fora de alcance. Rochas quebradas deixam de interceptar o clique e recuperam a transparência original ao reaparecer.
- Golpe: movimento apenas do braço direito, pegada fixa e impacto em 0,28 s. A animação de locomoção própria do jogo permanece. Animate e tracks pessoais do avatar são desativados para impedir mistura.
- Pets: tela de invocação com fundo índigo, título à esquerda, máquina 3D ao centro, quatro destaques à direita, chances e botões x1/x10 na base. Sorteio e preços continuam vindo do servidor.
- Vila da Folha: relevo esculpido mais visível, estratos adicionais, margens com seixos e plantas, santuário, varanda e objetos de mineração.
- Dragon Ball (área 2): praça em arenito, Capsule Corp, casa de treino, Torre Karin, mirante Kami, esfera do dragão, palmeiras, água, quedas, pontes e mina.
- Shadow Garden (área 4): castelo com torres, estátua, luas, ilhas flutuantes, vegetação roxa, quedas, pontes e iluminação noturna local, restaurada ao sair.
- Lobby: oficinas de madeira nas laterais, bancos, jardins, lanternas suspensas e fogo ambiente com brilho controlado.
- Materiais Plastic/Studs e árvores originais reaproveitados.

## Verificação

- Clique real e aproximação automática em minério dourado: dano confirmado pelo servidor em cinco direções, incluindo diagonal.
- Solicitações de golpe longe do minério e através de uma parede: rejeitadas.
- Avatar: Animate desativado, zero tracks pessoais ativos; golpe com corpo e pegada estáveis.
- Pathfinding: dez trajetos internos nas ilhas novas e três acessos adicionais com resultado Success.
- Portal da área 2: ativação real com E e chegada à área 3 confirmadas.
- UI de invocação e cenários inspecionados em Play. Nenhuma compra de gacha realizada nos testes.
- Inicialização final: seis áreas, 284 rochas e nenhum erro no console nessa execução.

## Cópias e estado

Estes arquivos são cópias dos scripts finais presentes no Studio. Não são um projeto Rojo completo; dependem dos modelos, KeyframeSequences, Config e GUIs existentes no jogo.
SummonLayout.json registra os principais ajustes de layout feitos diretamente nas instâncias.
As máquinas de gacha Ki e Sombra foram redimensionadas para 68% e reposicionadas nos terraços, com pads em (-66, 6.5, 454) e (-66, 6.5, 1014).
O cenário final também está reconstruído no modo Edit. As alterações não foram publicadas.

Backup anterior às alterações: ServerStorage.RevisionWorldPets_1788982774.

