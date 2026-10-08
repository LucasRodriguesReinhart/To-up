# AMS: miniaturas de minério e hat na coleta

Pedido: ao quebrar um minério, mostrar vários minérios e o hat sorteado no chão; após 5 segundos, os drops vão ao jogador e entram no inventário. Revisões de 07/10: hats em 3D real, sem imagem ou nome flutuante, com tamanho constante no mundo; minérios maiores e contornados. Último ajuste solicitado: coletar ao passar sobre cada minério/hat e colorir o contorno conforme sua raridade.

## Scripts instalados no lugar 101959830085647

| Arquivo | Caminho no Studio |
| --- | --- |
| `Mineracao.lua` | `ServerScriptService.Core.Mineracao` |
| `Main.lua` | `ServerScriptService.Core.Main` |
| `Recompensas.lua` | `ServerScriptService.Core.Recompensas` |
| `MineracaoVisual.client.lua` | `StarterPlayer.StarterPlayerScripts.MineracaoVisual` |
| `AMS_UI.client.lua` | `StarterPlayer.StarterPlayerScripts.AMS_UI` |

`ReplicatedStorage.MiningDropVisuals` contém 18 cópias leves dos modelos de minério de `ServerStorage.Modelos`, sem colisão e sem os componentes grandes usados só nas rochas. O cliente clona de 2 a 4 peças por quebra, maiores e com `Highlight` de contorno. A mochila recebe a mesma quantidade, respeitando o espaço livre.

`ReplicatedStorage.MiningDropHats` contém 80 modelos 3D dos acessórios usados pelo próprio AMS. Eles foram importados no Studio com [InstallHatDropVisuals.lua](InstallHatDropVisuals.lua). Cada drop clona o `MeshPart` correspondente em escala fixa no mundo, sem `BillboardGui`, PNG ou nome. O asset `ki_86070099711035` (Goku SSJ4) não foi aprovado para este lugar; seu drop usa provisoriamente uma silhueta 3D escurecida do SSJ5. O item entregue no inventário continua sendo o SSJ4.

O servidor reserva o espaço dos minérios e hats pendentes e verifica contato a cada 0,1 segundo nas mesmas posições enviadas ao cliente. Cada miniatura e hat é consumido uma única vez, independentemente dos outros itens. A coleta usa raio horizontal de 1,65 studs e tolerância de altura do personagem; somente o dono recebe o drop, sem remoto de coleta. Ao completar 5 segundos, entrega os itens restantes automaticamente.

A primeira garantia de hat por conta/área, chance, nível, missões, telemetria e autoequipamento continuam ligados ao prêmio real. Uma quebra aumenta `minerados` uma vez, mesmo quando suas miniaturas são coletadas em momentos diferentes. `Recompensas.darHat` ganhou um callback opcional para registrar o UID antes dos efeitos da entrega; isso impede repetir um hat se algum efeito posterior falhar. Consultas de gamepass e entrega concorrente são protegidas, e a saída aguarda entregas em andamento antes de salvar. Se outra fonte encher um inventário durante a espera, só os itens sem espaço permanecem pendentes e visíveis.

Os contornos são compartilhados por raridade, com no máximo sete `Highlight` para todos esses drops locais. Minérios `epica`/`lendaria` usam as cores de `epico`/`lendario`; a cor do hat é a raridade real sorteada.

| Raridade | Contorno |
| --- | --- |
| Comum | Cinza claro |
| Incomum | Verde |
| Raro | Azul |
| Épico | Roxo |
| Lendário | Dourado |
| Mítico | Rosa |
| Secreto | Ciano |

Backups anteriores às edições: `ServerStorage.Backup_MiningDrops_20261007`, `ServerStorage.Backup_MiningDropsAntes3D_20261007` e `ServerStorage.Backup_MiningDropsContatoRaridade_20261007`. O lugar foi salvo no Roblox Studio; isso é Save to Roblox, não publicação da versão jogável.

## Validação feita

- Play local carregou os módulos e a UI sem erro de inicialização.
- Coleta automática: mochila `0` e duas miniaturas após 1 segundo; entrega em 5,017 segundos, mochila `2` e zero miniaturas restantes.
- Contato com minério: mochila `2 → 4` em 0,318 segundo; após mais de 5 segundos continuou `4`, sem segunda entrega.
- Contato com hat: em 0,351 segundo, hats `0 → 1` e minérios continuaram `4`, com as duas miniaturas no chão. Em 5,013 segundos os minérios foram para `6`; hats continuaram `1`.
- Sete pares temporários confirmaram todos os RGB de raridade ao mesmo tempo, sem recolorir drops anteriores. A captura no Play mostrou os contornos nos modelos 3D. A plataforma e os pares de teste existiam só no Play.
- O visual do hat no cliente foi confirmado como `MeshPart` 3D, com tamanho de 1,3 studs e sem `BillboardGui`.
- Feedback “+N minério” e som de coleta acontecem em `dropColetado`, junto à entrada no inventário. Coleta exclusiva de hat preserva seu feedback próprio e não exibe `+0 minério`.
- Save to Roblox confirmado pelo log `Saved new changes in "Anime Mining Simulator" to Roblox.`

O DataStore estava indisponível na sessão Play local, então persistência após reentrada e teste multiplayer não foram confirmados. O caso de mochila cheia foi revisado no código, mas não reproduzido nessa sessão porque o perfil de teste tinha mochila infinita.
