# Auditoria de áudio anterior à reformulação

Data: 17/09/2026. Escopo: 63 scripts exportados em `before/`, inventário de edição `audit/edit_inventory.json` e snapshot de runtime `audit/runtime_audio_before.json`. Análise de código e dados, sem audição. Não se infere qualidade, clipping, conforto ou licença a partir de nomes, volumes ou IDs.

## Inventário e alcance

O inventário de edição registra 158 scripts: 14 em ReplicatedStorage, 36 em ServerScriptService, 12 em StarterPlayer, 1 em Workspace e 95 em ServerStorage. Os 63 fora de ServerStorage foram exportados e pesquisados integralmente. Os 95 de ServerStorage foram vistos somente como metadados; não se afirma ausência de referências sonoras em seu conteúdo. Estar em ServerStorage não executa um Script automaticamente; ModuleScripts também exigem require explícito.

- **Edição:** 19 Sounds, dos quais 16 fora de ServerStorage e 3 guardados em fontes/backup. Um grupo, `SoundService.MusicaGrupo`, volume 0,35.
- **Runtime capturado:** 32 Sounds e 12 SoundGroups. Todos os 32 Sounds do snapshot indicavam `loaded=true`. Somente `SoundService.Theme_0` indicava `playing=true`, Volume 0,23. Isso não comprova os assets criados posteriormente por eventos de SomJogo, que não existiam nesse instante.
- **Rotas de áudio de gameplay/UI:** `ReplicatedStorage.SomJogo`, `MineracaoVisual`, `ExpeditionClient`, `ExpeditionUI.Theme` e `Notify`; `AutoMinerar` usa o wrapper UI para toggle. `AreaAtmosphere` gerencia música separadamente.
- Não há Sound de forja, portal, água, lava, NPC ou cristal no inventário de edição; nenhum emissor ambiente é criado pelos 63 scripts exportados. `AmbienteLobby`, `AmbienteFolha`, `SakuraEffects` e `IgnisForjando` fazem animação/VFX, mas não criam áudio.

## Sounds existentes em edição

| Objeto | Asset ID | Volume | Situação observada |
|---|---:|---:|---|
| SoundService.OST | 112898538778548 | 0,28 | Loop legado; AreaAtmosphere o interrompe |
| ReplicatedStorage.Sons.Quebra | 9118585250 | 0,55 | Template sem uso direto encontrado nos 63 scripts |
| ReplicatedStorage.Sons.Golpe | 9116651255 | 0,45 | ID reutilizado como metal_1 no catálogo |
| ReplicatedStorage.Sons.GolpeAlt | 9116652339 | 0,45 | ID reutilizado como metal_2 |
| ReplicatedStorage.Sons.Detrito | 9118690959 | 0,35 | Template e ID rock_debris sem evento ativo encontrado |
| ReplicatedStorage.Sons.Premio | 93529351909119 | 0,60 | Mesmo ID de Compra; catálogo usa diretamente |
| ReplicatedStorage.Sons.Compra | 93529351909119 | 0,45 | Mesmo ID de Premio; catálogo usa diretamente |
| ReplicatedStorage.Sons.Erro | 9116652038 | 0,30 | ID reutilizado pelo evento ui_erro |
| ReplicatedStorage.Sons.Ovo | 9118770617 | 0,50 | ID reutilizado como sand em invocar_inicio |
| ReplicatedStorage.Sons.Moeda | 4608067546 | 0,50 | ID reutilizado em coleta, venda e UI |
| AreaMusicAssets.Hidden Lotus Pond | 82061470648013 | 0,50 | Template; AreaAtmosphere usa ID literal |
| AreaMusicAssets.Space Atmosphere | 1845421369 | 0,50 | Idem |
| AreaMusicAssets.Mysterious Forest | 9048681794 | 0,50 | Idem |
| AreaMusicAssets.The Forgotten Crypt | 131334832939011 | 0,50 | Idem |
| AreaMusicAssets.Pirate King | 1835322563 | 0,50 | Idem |
| AreaMusicAssets.Home Bound | 1845676363 | 0,50 | Idem |

Os 16 objetos fora de ServerStorage possuem 15 IDs únicos. Os nomes são os encontrados no projeto, não confirmação de autoria ou tema musical. Os templates não são clonados/referenciados pelo caminho `Sons`/`AreaMusicAssets` nos scripts exportados; alguns IDs continuam essenciais por estarem duplicados em tabelas de código.

### Fontes e backup em ServerStorage

| Objeto | ID | Volume | Observação |
|---|---:|---:|---|
| ToolboxAnimationSources.Toolbox_Pickaxe_FIN.Pickaxe.Pickaxe.Workspace.Coin | 3302699870 | 0,50 | Fonte de Toolbox guardada; não ativo no snapshot |
| ToolboxAnimationSources.Toolbox_PickaxeSwing.Rig.Pick-Axe.Handle.Sound | 12135982 | 0 | URL HTTP legado; silencioso por propriedade |
| BeforeIslandFinish_1789008574.OST | 112898538778548 | 0,28 | Cópia do OST, mesmo grupo/loop |

Nenhum desses objetos deve ser classificado como áudio ativo só por existir no inventário. Nenhum arquivo/objeto foi removido por esta auditoria.

## Catálogo dinâmico anterior

`SomJogo.lua:13–37` contém 18 IDs: 17 aparecem em eventos e `rock_debris` está declarado sem uso. Onze IDs adicionais em relação aos templates são 9118598279, 9118598469, 9118617342, 9125869797, 9118612665, 9120972321, 9120972444, 9120972323, 9040476898, 1840076509 e 9047103106. O número de objetos Sound antes da execução não representa o número de samples usados dinamicamente.

Sete IDs do catálogo coincidem com os oito IDs únicos em `ReplicatedStorage.Sons`; os onze restantes são exclusivos do catálogo. O ID legado de Quebra, 9118585250, não participa do catálogo. Junto com as sete músicas, há 26 IDs de conteúdo no catálogo/templates fora de ServerStorage, contando também o detrito declarado sem uso. Há mais dois IDs apenas nas fontes Toolbox.

Os comentários atribuem parte dos IDs a Pro Sound Effects/APM, mas isso não verifica licença, permissões nem correspondência do conteúdo. O snapshot confirma carregamento apenas dos templates/músicas presentes naquele momento. Exigir manifesto de proveniência e verificação individual dos 11 IDs exclusivos do catálogo.

### Eventos e conexões

São 38 eventos configurados. As famílias via wrappers não estão sem uso só porque o nome literal não aparece fora de SomJogo.

| Família/eventos | Conexão encontrada | Situação |
|---|---|---|
| hit, hit_pesado, whoosh | MineracaoVisual:253,255,288 | Ativos; pedra+metal, grave em ferramentas mundo >=3 |
| break_comum/incomum/raro/epico/lendario/chefe | Som.quebra ← MineracaoVisual:300 | Ativos por variante; comum tem 2 samples, variantes maiores reutilizam conjunto |
| coleta | Som.coleta ← MineracaoVisual:301 | Após quebra, delay 0,08s; não é evento de chegada física de item |
| venda_pequena/media/grande/jackpot | Som.venda ← ExpeditionClient:248 | Somente venda manual pelo retorno do remoto |
| upgrade | ExpeditionClient:260 | Compra de picareta ou mochila |
| level_up | ExpeditionClient:264 | AlimentarPet/FundirHat quando resposta diz levelUp |
| area_nova | ExpeditionClient:256 | ComprarArea confirmado |
| drop_comum/raro/epico/lendario/secreto | Som.drop ← MineracaoVisual:304 e ExpeditionClient:512 | Hat e reveal gacha |
| invocar_inicio | ExpeditionClient:560 | Abertura gacha |
| portal_saida, portal_chegada | ExpeditionClient:445,1111 | Transição; sem loop espacial do portal |
| ui_click/tab/toggle/erro | Theme, Inventory, AutoMinerar, ExpeditionClient | Botões, abas, ajustes e falhas |
| ui_abrir/fechar | ExpeditionClient:426,372; Theme:572 | Abertura/fechamento de menu |
| ui_compra/equipar | ExpeditionClient:264,266,270 | Confirmações de ações |
| ui_notify/popup/reward_banner/coin_tick | Notify e ExpeditionClient | Notificações, popup, recompensa e animação de moedas |
| ui_hover | SomJogo:148 | Configurado, mas nenhum chamador estático encontrado |

Ausências funcionais: material de minério não muda o hit; não há crack por HP, critical hit específico, max-upgrade, unequip, forge craft/idle ou assinatura distinta Mythic. Não foi encontrado sistema de críticos no Mineracao atual; não se recomenda inventar mecânica só para fornecer som. `mitico` usa `drop_lendario`, e `incomum` usa `drop_comum`. Achievements/boosts não têm família específica; missões/daily/códigos compartilham reward_banner. A existência desses eventos genéricos não é defeito automático, mas não cumpre todas as distinções solicitadas.

## Problemas confirmados e riscos de implementação

1. **Limite de vozes não mede vozes.** `SomJogo:197–213` conta uma reprodução do evento e libera após 0,6s fixos. Cada evento pode criar até quatro camadas; não há limite global de Sounds. Durações reais frequentemente superam 0,6s.
2. **Criação constante.** Toda camada cria Sound; 3D também cria Attachment. Cleanup por Debris em 4s. Há cleanup, portanto não afirmar vazamento infinito, mas há churn de instâncias e ausência de pool.
3. **Corte previsível no erro.** ID 9116652038 dura 3,270229s no snapshot. ui_erro usa PlaybackSpeed 0,70–0,75: reprodução nominal dura 4,36–4,67s; Debris encerra aos 4s. É risco de truncamento por código, sem julgamento auditivo.
4. **Repetição descontrolada.** Seleção uniforme independente não evita repetir o sample. Hit tem apenas dois takes de pedra e dois de metal; não há baralho/round robin. Metal possui intervalo de pitch 1,35–1,60; UI usa até 2,60. Esses números não provam fadiga, mas precisam de A/B e escuta prolongada.
5. **Venda ignora valor.** `S.venda(ganho,itens):242–249` nunca usa ganho; faixas são somente 12, 50 e 120 itens. Valores muito diferentes com mesma quantidade geram o mesmo evento. O comentário sobre valor da ilha não corresponde à implementação.
6. **Auto Sell sem evento estruturado.** `IgnisService:48–50` envia `tipo='area'` com texto formatado. O consumidor mostra toast; não chama Som.venda com ganho/itens. Portanto não compartilha o mesmo feedback de venda manual.
7. **Mute incompleto.** SomMineracaoEnabled muda apenas GrupoMining, embora Menus:513 prometa incluir coleta. Coleta e partes de quebra estão em Rewards e continuam. Não existem Master/Music/SFX numéricos nem persistência de preferências; Menus:526 só grava atributo local.
8. **Grupos duplicados no snapshot.** GrupoSFX, GrupoUI, GrupoMining, GrupoAmbience e GrupoRewards aparecem duas vezes cada, totalizando 10; AreaMusic e MusicaGrupo completam 12. Caminho do require server confirmado: AreaBuilder:37 → Theme:448 → SomJogo top-level. Também há require client. O código pode criar grupos nos dois contextos antes de replicação; o snapshot prova duplicação, mas não registra a ordem exata da corrida.
9. **Música com dois controles.** SomJogo limita MusicaGrupo a 0,32, porém AreaAtmosphere toca em AreaMusic volume 1. O comentário 'música nunca compete' não controla as faixas reais. OST é parado e Theme_0 usa o mesmo ID, sem duplicação audível no snapshot.
10. **Não há preload de SFX.** A ocorrência de PreloadAsync em ExpeditionClient:1178 é para imagens. SomJogo toca imediatamente sem checar IsLoaded ou callback de asset.
11. **Timeline de mineração duplicada.** Server usa ImpactTime=.28; cliente agenda `task.delay` até starts+CONTATO=.28 e whoosh em starts+.15. LocomocaoBigAxe amostra pose pela mesma hora do servidor. Não há AnimationTrack/GetMarkerReachedSignal nesta cadeia procedural. A intenção de sincronização existe, mas o agendamento do som depende de delays separados.
12. **Deduplicação aproximada.** MineracaoVisual:266 ignora confirmação se houve previsão do minerador nos últimos 0,45s, sem ID do golpe. Confirmações tardias ou golpes rápidos precisam de teste de duplicação/perda por ciclo.
13. **Swing cancelado pode soar.** O callback whoosh não revalida MiningSwingStart, ferramenta, personagem ou alcance; o callback de hit previsto faz algumas dessas verificações.
14. **Rede e prioridade parcial.** Server dispara AnimarPicareta a todos no início e contato; cliente corta além de 90 studs, usa 70 studs de rolloff e reduz ganho dos demais para 0,55/0,5. Há culling/gain local, mas não priorização global nem simplificação de camadas por distância.
15. **Quebra de outro jogador não tem mesma rota.** FeedbackMina de quebra é FireClient para quem quebrou; vizinhos recebem confirmação de hit, mas não a família Som.quebra por essa rota. Deve ser decisão explícita no novo mix.
16. **Nenhum estado auditivo da forja.** IgnisForjando:48 em diante anima batida e emite faíscas a cada ciclo, sem evento ou Sound no frame de contato.

## Música e duplicatas

AreaAtmosphere cria sete loops Theme_0–6; cada um recebe fade de 1,8s, e faixas antigas são pausadas após o fade. Cancela tweens antigos. É uma transição já implementada a preservar/testar, sem afirmar qualidade do loop ou adequação musical. Todas as sete músicas carregaram no snapshot; somente lobby estava tocando. Duração: Lobby 96,03s; Folha 233,32s; Namek 163,13s; Natagumo 205,01s; Shadow 194,52s; GrandLine 146,24s; CidadeZ 63,61s.

Duplicatas são: Premio/Compra compartilham 93529351909119; OST/backup/Theme_0 compartilham 112898538778548; cada template AreaMusicAssets compartilha ID com seu Theme de runtime. Running/Climbing compartilham o arquivo padrão Roblox de passos. Duplicar ID não significa tocar simultaneamente ou desperdiçar um download; os grupos duplicados são questão de instâncias distinta.

Os nove sons do avatar são criados pelo controlador padrão Roblox e não por SomJogo: Climbing, Died, GettingUp, Swimming, Jumping, Landing, Splash, FreeFalling, Running. Não aparecem roteados nos grupos personalizados. FreeFalling estava em Volume 0; os outros em 0,65, todos sem tocar no snapshot. Não atribuir esses estados a defeito de mix sem ação/escuta correspondente.

## Decisões preserváveis e estado desta auditoria

Preservar contratos Som.tocar/coleta/drop/quebra/venda ou fornecer adaptação, confirmações servidor de economia, geometria de contato, timestamps da pose, VFX existentes e pausa/fade de música. Os backups não são candidatos a apagar para 'limpar áudio'. A retirada de templates legados exige comprovar referências fora dos 63 scripts e manter backup.

Esta auditoria não removeu nem substituiu sons. A reformulação ocorre em paralelo e deve informar sua lista final separadamente. Não há aprovação perceptual de 100 hits, 100 pickups, fones, alto-falantes, teste cego ou clipping neste documento.
