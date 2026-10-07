# AMS: miniaturas de minério e hat na coleta

Pedido: ao quebrar um minério, mostrar vários minérios e o hat sorteado no chão; após 5 segundos, os drops vão ao jogador e entram no inventário. Revisão de 07/10: hats em 3D real, sem imagem ou nome flutuante, com tamanho constante no mundo; minérios maiores e contornados.

## Scripts instalados no lugar 101959830085647

| Arquivo | Caminho no Studio |
| --- | --- |
| `Mineracao.lua` | `ServerScriptService.Core.Mineracao` |
| `Main.lua` | `ServerScriptService.Core.Main` |
| `MineracaoVisual.client.lua` | `StarterPlayer.StarterPlayerScripts.MineracaoVisual` |
| `AMS_UI.client.lua` | `StarterPlayer.StarterPlayerScripts.AMS_UI` |

`ReplicatedStorage.MiningDropVisuals` contém 18 cópias leves dos modelos de minério de `ServerStorage.Modelos`, sem colisão e sem os componentes grandes usados só nas rochas. O cliente clona de 2 a 4 peças por quebra, maiores e com `Highlight` de contorno. A mochila recebe a mesma quantidade, respeitando o espaço livre.

`ReplicatedStorage.MiningDropHats` contém 80 modelos 3D dos acessórios usados pelo próprio AMS. Eles foram importados no Studio com [InstallHatDropVisuals.lua](InstallHatDropVisuals.lua). Cada drop clona o `MeshPart` correspondente em escala fixa no mundo, sem `BillboardGui`, PNG ou nome. O asset `ki_86070099711035` (Goku SSJ4) não foi aprovado para este lugar; seu drop usa provisoriamente uma silhueta 3D escurecida do SSJ5. O item entregue no inventário continua sendo o SSJ4.

O servidor reserva o espaço dos minérios e hats pendentes, aguarda 5 segundos e só então entrega a recompensa. A primeira garantia de hat por conta/área, chance, nível, missões, telemetria e autoequipamento continuam ligados ao prêmio real. Drops pendentes são concluídos antes de descarregar ou salvar o perfil na saída. Se outra fonte encher a mochila durante a espera, o drop permanece pendente até haver espaço.

Backups anteriores às edições: `ServerStorage.Backup_MiningDrops_20261007` e `ServerStorage.Backup_MiningDropsAntes3D_20261007`. O lugar foi salvo no Roblox Studio; isso é Save to Roblox, não publicação da versão jogável.

## Validação feita

- Play local carregou os módulos e a UI sem erro de inicialização.
- Uma quebra comum controlada mostrou mochila `0` e duas peças com contorno após 1 segundo; depois de 5,6 segundos mostrou mochila `2`.
- O visual do hat no cliente foi confirmado como `MeshPart` 3D, com tamanho de 1,3 studs e sem `BillboardGui`.
- Feedback “+N minério” e som de coleta acontecem em `dropColetado`, junto à entrada no inventário.
- Save to Roblox confirmado pelo log `Saved new changes in "Anime Mining Simulator" to Roblox.`

O DataStore estava indisponível na sessão Play local, então persistência após reentrada e teste multiplayer não foram confirmados. O caso de mochila cheia foi revisado no código, mas não reproduzido nessa sessão porque o perfil de teste tinha mochila infinita.
