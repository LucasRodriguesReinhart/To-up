# Lobby "Vila Medieval": especificação aprovada (2026-10-08)

O usuário aprovou o desenho em 3 partes no chat (planta, forja e estilo, conexões e ordem) e pediu: "prossiga sem interrupções".

## Objetivo
Substituir o lobby atual (`LOBBY_FORJA`, Vila-Forja noturna, 794 × 594) por um lobby novo:
- com o estilo da imagem `ref/ref_01_estilo_vila.jpg`: vila medieval de fantasia ensolarada, rua de paralelepípedo, casas enxaimel com telha laranja sobre base de pedra, grama, árvores, carroça;
- com o layout de hub do Anime Expeditions (`ref/ref_02_layout_anime_expeditions.jpg`): spawn central em terraço com escadaria, praça com medalhão, eixos claros e um prédio por função.

A primeira experiência deve ser agradável e o ciclo do jogo legível: chegar, picareta (forja), vender, mochila, portais e ilhas, voltar.

## Decisões do usuário
- O layout é o do Anime Expeditions, no estilo da imagem.
- **Não há castelo.** O marco é a **forja do Ignis**, porque o tema do jogo é mineração.
- Caminho: o lobby é feito do zero no pipeline Blender das ilhas.
- Planta: `ref/planta_aprovada_v1.png`.

## Planta (cerca de 370 × 330 studs, em volta da origem do place)
- **Spawn:** terraço com escadaria descendo para a praça, de frente para a forja. O `LobbyLayout.Spawn` atual é (0, 9,5, 94).
- **Praça central:** paralelepípedo e medalhão no piso (picareta + bigorna), rebaixado e sem colisão.
- **Eixo norte:** rua com casas enxaimel, ponte de pedra sobre o canal e, no fim, a forja do Ignis.
- **Leste:** loja de mochilas com vitrine. Mantém o funcionamento atual: `npc vendedor ` (com espaço no fim), `LojaPrompt` e `PadLoja` como marca.
- **Oeste:** ranking Top 100 (pódios do `GlobalTop100`) e, pela rua, o pátio dos portais, com os 6 portais aprovados em semicírculo (`Santuario.Portal1..6` com Disco AreaId; o `Main` liga).
- **Sudeste:** portão e ponte para a Ilha 1. Mantém a travessia a pé e as paredes de custo de hoje. A conexão real com a Vila da Folha fica em Roblox z 222, piso 6 (ver `fm_terrain_isles`).
- **Correio:** junto ao spawn, com o prompt "Enviar Feedback".
- **Em volta:** colinas, pinheiros e árvores de copa; montanhas ao fundo.
- **Distância:** qualquer função a no máximo cerca de 15 s a pé do spawn.

## Forja do Ignis (marco)
- **Posição:** o ponto do Ignis fica EXATAMENTE onde está hoje.
  - Root em (−0,9; 7; −60,7), olhando +Z, piso Y = 7, bigorna a +5 em Z.
  - É o contrato do golem novo da sessão "Ignis 3D": Model `workspace.NPCs.Ignis`, BasePart `belly` (prompt do `Main`, distância 22), `hot_billet`, `LetreiroIgnis`, atributos `IgnisTalkingUntil`/`IgnisLookAt`/`ForgeImpactTime` e `ReplicatedStorage.LOBBY_FORJA_VFX.IgnisImpact`.
  - Marcadores `INTERACT_Ignis`/`NPC_Ignis`/`PLAYER_INTERACT_Ignis`, como hoje.
- **Forma:** base de pedra em blocos arredondados, andar enxaimel e telha laranja.
  - Chaminé de pedra alta, com fumaça e brasa, visível do spawn por cima das casas.
  - Frente da oficina aberta com vigas grossas: da praça vê-se o Ignis na bigorna.
  - Roda d'água na lateral, puxada pelo canal, movendo um martelo-pilão.
- **Props:** suportes de picaretas à venda, sacos de carvão, lingotes, tenazes e placa com a bigorna. Nada que pareça minério de mineração.

## Kit da vila
- **Casas enxaimel:** térreo de pedra arredondada; reboco creme com vigas escuras (X, diagonais); andar superior em balanço; telhado íngreme de telha laranja com águas-furtadas e chaminés; varandas, floreiras e placas penduradas.
  - 2 a 3 andares, com variações para nenhuma rua repetir a mesma casa.
  - Só forja e loja têm interior; as outras casas são fachadas fechadas, mas completas, em 360°.
- **Rua:** paralelepípedo arredondado em geometria, meio-fio, borda de grama com tufos e flores, muretas, carroça e roda, barris, caixotes e postes de ferro com lanterna (NightOnly).
- **Vegetação:** pinheiros estilizados, árvores de copa redonda, sebes, colinas e montanhas.
- **Cor (Roblox, sem textura):** telha terracota (~200, 110, 60); reboco creme (~235, 225, 200; nunca branco puro, por causa do bloom do dia); madeira marrom escura; pedra cinza-azulada; paralelepípedo bege-cinza; grama verde saturada.
- **Luz:** dia, sol quente, sombra suave; perfil do lobby no `AreaAtmosphere`.

## Contratos e scripts
- Posições do jogo: só os números do `ServerScriptService.Core.LobbyLayout` (Spawn, Shop, ShopFacing, Ignis, PortalIsland).
- Os prompts e sistemas de hoje continuam: `Main`, `IslandTravel`, `LobbyServices` (`LobbyRevision`), `TravessiaCorredores`, `Paredes`, `PortoesDeIlha`, `Top100`, `IgnisIntroService`, `BackpackFullRoute`.
  - Antes de trocar, cada um é lido para achar a dependência do `LOBBY_FORJA` (nomes de filhos, marcadores).
  - A dependência é preservada: o modelo novo terá os mesmos nomes onde o código procura.
- **Nenhum sistema novo.**

## Produção (pipeline das ilhas, em `lobby_area/vila_medieval/`)
- **V0:** blockout do hub inteiro + QA de rotas pelo andador (spawn→forja, loja, portais, saída Ilha 1, ranking, correio) + folhas comparando com a ref.
- **V1:** trecho de qualidade final (rua praça → ponte do canal, 2 casas, paralelepípedo, poste, mureta), validado na CÓPIA do Studio antes de multiplicar o kit.
- **V2:** forja; depois loja, ranking, pátio dos portais (portais aprovados via `fm_pv3`, só leitura) e casas.
- **V3:** vegetação, props, luz e efeitos (fumaça, brasa, roda).
- **V4:** integração, export, import na cópia, Play (rotas, prompts, portais, travessia, FPS).
- **V5:** auditoria na altura do jogador e finesse.

## Segurança
- **Só a cópia:** trabalhar apenas em `AMS_Lobby_Champions_Avaliacao.rbxl`, com backup do `LOBBY_FORJA` dentro dela (ServerStorage). O place oficial só depois do OK do usuário.
- **Arquivos:** nunca salvar o place. Não editar `lobby_area/forja_mineradora/` (`fm_lib.py`, `export_roblox.py` e afins são compartilhados e só leitura), as ilhas nem a pasta do Ignis golem.
- **Agentes:** subagentes sem Studio, Blender MCP, computer-use ou browser; Blender sempre com `--factory-startup`.
- **Studio compartilhado:** avisar as outras sessões por SendMessage antes de importar ou dar Play no place oficial. A cópia é um Studio separado.
