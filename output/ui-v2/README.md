# Anime Mining Simulator — UI V2

A direção final aproxima a composição das três referências de Anime Vanguards: inventário violeta com grade, personagem dominante e ficha; invocação com banners ilustrados à esquerda, palco de três personagens, ações x1/x10 e pity na base; diário preto/laranja com prêmios grandes e faixas de resgate. Tipografia Fredoka com contorno, botões com profundidade e cores fortes de raridade unificam as telas. Regras, remotes e dados de gameplay foram preservados.

Prévia desktop: [Inventário](</C:/Users/lucas/OneDrive/Desktop/To up/output/ui-v2/screenshots/inventory.png>) · [Diário](</C:/Users/lucas/OneDrive/Desktop/To up/output/ui-v2/screenshots/daily.png>) · [Invocação](</C:/Users/lucas/OneDrive/Desktop/To up/output/ui-v2/screenshots/summon.png>).

**Fontes canônicas da UI:** `output/ui-v2/src/`. Os dez caminhos abaixo correspondem às posições dos scripts no Explorer do Studio:

```text
ReplicatedStorage/ExpeditionUI/Theme.lua
ReplicatedStorage/ExpeditionUI/Inventory.lua
ReplicatedStorage/ExpeditionUI/Menus.lua
ReplicatedStorage/ExpeditionUI/Notify.lua
StarterPlayer/StarterPlayerScripts/ExpeditionClient.lua
StarterPlayer/StarterPlayerScripts/AutoMinerar.lua
StarterPlayer/StarterPlayerScripts/IslandTransition.lua
StarterPlayer/StarterPlayerScripts/MineracaoVisual.lua
StarterPlayer/StarterPlayerScripts/PetsSeguidores.lua
ServerScriptService/Core/AreaBuilder.lua
```

`before/` contém **62 fontes anteriores** para comparação e recuperação seletiva. O backup equivalente no Studio é `ServerStorage.BeforeUIV2_20260917_Expedition`. Não é um instalador nem uma versão final.

**Dependência obrigatória: áudio V3.** A UI final já incorpora a integração de áudio. Exige `ReplicatedStorage.AudioCatalog` e `ReplicatedStorage.AudioPreferences`, disponíveis em `output/audio-v3/src/ReplicatedStorage/`, junto da infraestrutura atualizada descrita no [relatório de áudio](</C:/Users/lucas/OneDrive/Desktop/To up/output/audio-v3/RELATORIO_FINAL.md>). Não reinstale a UI sem áudio, nem copie `SomJogo` isoladamente. Para arquivos compartilhados, use as fontes sincronizadas em `ui-v2/src/`; `audio-v3/merged-ui-final/` registra o merge. Restaurar versões antigas de Menus, ExpeditionClient, MineracaoVisual ou IslandTransition pode apagar essa integração. Este pacote não executa sobrescrita automática.

Para testar no Studio com a integração completa:

1. Inicie **Play**. Use **H** para Unidades, **J** para Itens e **G** para Invocar; abra Loja, Ilhas, Missões, Diário/Coleção, Forja e Configurações pela navegação.
2. Confira busca/filtros, seleção/equipamento, estados vazios/bloqueados e rolagem. Em Invocar, use **Viajar**, depois confira proximidade, chances, unidades e pity. Compras, resgates e consumo precisam de perfil de teste apropriado.
3. Repita no emulador em desktop, retrato, paisagem e tablet; revise alvos de toque, popups após resize, volume e movimento reduzido. Pare **Play** ao terminar; os scripts de `qa/` não fazem parte da entrega de produção.

**Estado da entrega:** integrado e salvo no Roblox, confirmado pelo Output do Studio às 00:56:06.333 de 17/09/2026. Studio deixado em Edit, sem scripts temporários de QA. Veja [QA_RESULTS.md](</C:/Users/lucas/OneDrive/Desktop/To up/output/ui-v2/QA_RESULTS.md>) para evidências e limites: capturas não comprovam teste econômico completo, toque físico ou aprovação auditiva. A cópia adicional .rbxl não foi gerada; este diretório contém fontes e backups, não o place completo. Publicação pública não foi realizada.
