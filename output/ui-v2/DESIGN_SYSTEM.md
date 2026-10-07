# Anime Mining Simulator — sistema de interface

Estado em 17/09/2026: nova direção aplicada ao Theme/shell e em integração nos conteúdos; **estado em validação**. Este documento não aprova o acabamento nem substitui QA em Play. O inventário contido em duas colunas e a paleta sóbria da proposta anterior deixaram de ser o destino visual do projeto.

## Direção artística implementada

As três imagens de Anime Vanguards anexadas são o benchmark de composição, densidade, hierarquia e presença de personagens. A expectativa é uma aproximação visual mais forte, com identidade anime reconhecível, sem reproduzir literalmente marca, textos ou dados da referência.

- Diário: base preta e assinatura laranja, categorias ilustradas, grade contrastada, recompensa imediata em destaque e estados resgatado/disponível/bloqueado legíveis por texto e símbolo.
- Inventário: campo violeta, retratos grandes nos cards, personagem selecionado dominante no centro, estatísticas/ações à direita. Desktop passa a usar a tela inteira, com grade densa à esquerda; a adaptação estreita preserva acesso aos mesmos controles.
- Invocação: palco e banners com personagens integrados, composição em camadas, títulos pesados, raridade e garantia visíveis, CTAs com volume e contraste.

Theme atual usa Fredoka para display/title/label/number, Gotham Heavy para heavy e Builder Sans para corpo. Contorno é automático nos papéis de destaque e explicitamente removido no corpo, legendas e parágrafos quando necessário. Fundos violetas, raridade forte, bordas marcadas, faces com gradiente/brilho e lábio inferior dão volume aos botões. Navegação permanece única na base, com cards coloridos por categoria.

Valores atuais de Theme.P: fundo #0A0716, superfície #120C22, elevada #1E1436, violeta #A74AFF, ciano #2EDAFF, ouro #FFD32B, verde #28EB4F e laranja #FF9017. Esses valores descrevem o código desta integração. T.F.display é Fredoka. As capturas reais finais estão em `screenshots/inventory.png`, `screenshots/summon.png` e `screenshots/daily.png`; escopo de verificação e limites em `QA_RESULTS.md`.

## Fonte única e componentes

ReplicatedStorage.ExpeditionUI.Theme continua sendo a fonte única de cores (T.P, compatibilidade T.C), fontes (T.F), raridades, espaçamentos, raios, motion, assets e componentes. **Não existe um módulo novo Tokens.** As variáveis locais UITokens em scripts de mundo são aliases de require(ExpeditionUI.Theme).

- button mantém Face.Caption, Disabled e ToneColor; setEnabled, setTone e bindInteraction coordenam estados e input.
- progress mantém Fill/Tint; setProgress permanece compatível.
- preview usa Config.PetArte para busto/corpo, PreviewModelos.Pets no fallback, ExpeditionPreviews.Pickaxes para picaretas e Config.HatAssets para hats.
- dropdown usa TooltipLayer para lista sem recorte, fechamento externo e rolagem; emptyState/loading tratam ausência e carregamento.
- Efeitos contínuos respeitam ReducedMotion e ExpeditionEffectsEnabled, com cancelamento e remoção de conexões ao destruir componentes.

## Arquitetura e ownership

| Arquivo | Responsabilidade | Fronteira preservada |
|---|---|---|
| ExpeditionClient.lua | ScreenGui, HUD, navegação, popups, resize, snapshot, invoke e invocação | Ownership página/popup, input e remotes |
| Theme.lua | Aparência, assets e componentes | APIs públicas; require seguro também no servidor |
| Inventory.lua | Coleção por UID, filtros, seleção, detalhe, equipamento e consumo | UID diferente de ID de catálogo; proteção local e confirmação |
| Menus.lua | Loja, áreas, invocação/chances, forja, missões, diário/index e settings/códigos | Dados reais, disponibilidade e ações do servidor |
| Notify.lua | Toasts, feed agregado, banners e reveals | Filas limitadas; arbitragem com modais/viagens |
| AutoMinerar.lua | Seleção/aproximação e Hold | Gameplay suspenso durante UI; mesmo pedido de golpe |
| IslandTransition.lua | Overlay de viagem e bloqueio transitório | AreaTransition autoritativo; sem porcentagem fictícia |
| MineracaoVisual.lua | Impacto, números e fragmentos locais | Tempo do golpe, eventos, limites e cleanup |
| AreaBuilder.lua | Interfaces dos minérios | Nomes/HP/hitbox/spawn; apresentação apenas |
| PetsSeguidores.lua | Placas dos seguidores | Movimento/postura e nomes filtrados |

O servidor mantém moedas, inventários, equipamento, XP, pity, drops, desbloqueios, missões, diário, códigos, boosts e compras. A UI apresenta snapshots e envia ações, sem inventar recompensas ou modificar regras.

## Estado e camadas

PlayerGui.ExpeditionUI.Canvas abriga HUD, ModalLayer, Notifications, PopupLayer.Dialogs e TooltipLayer. Window.Body continua host de página. OpenPage, PopupOpen e BottomReserved pertencem ao **ScreenGui ExpeditionUI**. RevealOpen, TravelTransition, AreaTransition, CurrentAreaId e preferências pertencem ao **Player**.

Página/popup/reveal/viagem ou TextBox em foco suspendem seleção e movimento automático de mineração. Fechar UI não deve reativar alvo antigo; preferência Hold permanece local.

Popups retêm builder/closure. Resize reconstrói na dimensão disponível e restaura texto, cursor, foco e rolagem por nome de componente, sem disparar onClose. Seleção e revisão de alimentação/fusão ficam na closure do inventário. Conteúdo extenso rola sem encolher CTAs. Resultados recalculam colunas/largura usando o espaço real do builder.

Favoritos, proteção de consumo, filtros, ordenação e preferências são de sessão. A UI diz “nesta sessão”; não há persistência adicional. Equipados, favoritos e protegidos ficam fora dos candidatos, com revalidação antes do remote.

## Validação necessária

Baseline técnico: exportação LIVE before (62 scripts). Versões antigas de output/revision não são fonte de instalação. O pacote reconstruído contém dez scripts em src.

Após a nova direção visual: compilar os dez scripts; revisar screenshots desktop/telefone/landscape curto; testar navegação, cancelamento, seleção e rotação com popup aberto; verificar Hold suspenso, desbloqueio/viagem, venda, chances/pity e feedback. Consumo deve usar fixture segura e verificar proteção/IDs. Imagens exigem ImageLabel.IsLoaded em Play. IDs Robux 0 continuam indisponíveis, sem compra real validável até configuração.
