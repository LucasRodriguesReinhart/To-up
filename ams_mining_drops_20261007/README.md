# AMS: miniaturas de minério e hat na coleta

Pedido: ao quebrar um minério, mostrar o minério e o hat sorteado no chão; após 5 segundos, os drops vão ao jogador e entram no inventário, como na coleta visual do Unboxing.

## Scripts instalados no lugar 101959830085647

| Arquivo | Caminho no Studio |
| --- | --- |
| `Mineracao.lua` | `ServerScriptService.Core.Mineracao` |
| `Main.lua` | `ServerScriptService.Core.Main` |
| `MineracaoVisual.client.lua` | `StarterPlayer.StarterPlayerScripts.MineracaoVisual` |
| `AMS_UI.client.lua` | `StarterPlayer.StarterPlayerScripts.AMS_UI` |

`ReplicatedStorage.MiningDropVisuals` contém 18 cópias leves dos modelos de minério de `ServerStorage.Modelos`, sem colisão e sem os componentes grandes usados só nas rochas. O cliente clona esses modelos localmente para o dono do drop. O hat usa a miniatura do asset sorteado, uma esfera de raridade e o nome do item.

O servidor reserva o espaço dos minérios e hats pendentes, aguarda 5 segundos e só então entrega a recompensa. A primeira garantia de hat por conta/área, chance, nível, missões, telemetria e autoequipamento continuam ligados ao prêmio real. Drops pendentes são concluídos antes de descarregar ou salvar o perfil na saída. Se outra fonte encher a mochila durante a espera, o drop permanece pendente até haver espaço.

Backup anterior à edição: `ServerStorage.Backup_MiningDrops_20261007` (quatro scripts). O lugar foi salvo no Roblox Studio; isso é Save to Roblox, não publicação da versão jogável.

## Validação feita

- Play local carregou os módulos e a UI sem erro de inicialização.
- Uma quebra controlada mostrou mochila `0` e miniatura visível após 1 segundo; depois de 5,6 segundos mostrou mochila `1`.
- Hat recebido no fluxo de mineração após a garantia de início; miniatura do asset carregou no cliente.
- Feedback “+1 minério” e som de coleta foram movidos para `dropColetado`, junto à entrada no inventário.
- Save to Roblox confirmado pelo log `Saved new changes in "Anime Mining Simulator" to Roblox.`

O DataStore estava indisponível na sessão Play local, então persistência após reentrada e teste multiplayer não foram confirmados. O caso de mochila cheia foi revisado no código, mas não reproduzido nessa sessão porque o perfil de teste tinha mochila infinita.
