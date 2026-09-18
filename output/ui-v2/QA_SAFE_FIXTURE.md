# QA funcional com perfil temporário não persistível

Análise do código copiado em `before/`, sem modificar Studio. `qa/SafeFixture.lua` é um helper de teste para avaliar somente no Server Play; não pertence ao pacote `src` e não deve ser instalado no Edit nem publicado.

**Estado nesta execução:** a leitura de `require(PlayerData)` no tool Server foi recusada com `current thread cannot require PlayerData` por capacidades `LoadUnownedAsset (and 3)`, conforme retorno recebido pelo agente principal. A fixture não foi instalada nem executada. Não usar cópia de fonte, `loadstring`, escrita em `ModuleScript.Source` ou execução indireta para contornar esse limite. O helper local fica como referência técnica para uma futura sessão que tenha acesso autorizado ao módulo.

O QA atual segue somente navegação, interações não consumptivas e equipar/desequipar pelos remotes comuns da UI, restaurando a seleção original. Mineração com recompensa, venda, compras, gacha, resgate de missões/diário e mutações de economia **não são considerados testados** nesta execução por este plano.

## Conclusão

É possível testar mineração, venda por moeda interna, upgrades, equipagem, gacha, missões e diário sem salvar alterações da fixture. A arquitetura já oferece `PlayerData.carregarVazio()` e duas guardas de persistência. A proteção principal da fixture é `perfil.__semSalvar = true`, acompanhada de `perfil.__dev = true` e `perfil.__devSalvar = false`; uma segunda barreira envolve `PlayerData.salvar` apenas para o jogador de QA até encerrar Play.

Não usar `PlayerData.carregar(player)` para criar a fixture: ele já chama `UpdateAsync` na chave real `u_<UserId>` para registrar trava de sessão. Não usar `snapshot()` como backup: petsInv, hatsInv, mochila, missões, index e outras tabelas são retornadas por referência.

## APIs e salvamentos encontrados

| API / hook | Comportamento |
|---|---|
| `PlayerData.get(player)` | Referência mutável do perfil no cache; não há setter/export do cache. |
| `PlayerData.carregarVazio()` | Cria e normaliza perfil novo em memória; não consulta Store. |
| `novoPet(perfil,id,nivel)` / `novoHat(...)` | Cria UID, inventário e index no perfil recebido. |
| `snapshot(perfil)` | Modelo de leitura para UI; não é cópia profunda. |
| `sincronizar(player)` | Envia AtualizarDados, publica PetsEquipados/PetsApelidos/IntervaloGolpe, leaderstats e WalkSpeed. Sem gravação. |
| `salvar(player,liberar)` | Retorna false imediatamente se `__semSalvar` ou `__dev and not __devSalvar`; depois faria UpdateAsync. |
| `descarregar(player)` | Chama salvar(player,true) e remove cache. Não chamar durante QA. |
| `Main.PlayerRemoving` | Histograma/telemetria, descarregar e limpar cooldown gacha. |
| `Main.BindToClose` | salvar(player,true) para todos. |
| `Main` autosave | salvar a cada 120 s. |
| `Retencao.resgatarDaily` | Agenda salvar com task.spawn após entregar o diário. Guarda cobre a chamada. |
| `Produtos` | Rejeita perfil `__semSalvar`; recibos podem chamar salvar. Pagamentos e recibos ficam fora deste QA. |
| `DebugV31` | `semSalvar`, `modoTeste`, `perfilNovo`, `moedas`, `areas`, `hats`, `golpear`, `vender`, compras, `gacha`, `daily`, `missao`, `estado`. Não faz backup; preferir fixture com rollback. |

`DevTest` está ligado para UserId 638377833, marca `__devSalvar=false`, entrega tudo e recarrega moedas a 1e15 a cada segundo. Desabilitar **a instância Script no Server Play** antes de testar saldo/progressão; alterar apenas o atributo `Desligado` depois do início não interrompe seu loop, pois ele só lê o atributo no topo. A fixture faz `DevTest.Disabled=true` no runtime e mantém assim até Stop Play.

`Telemetria` chama AnalyticsService também no Studio. A fixture intercepta `evento`, `marco` e `economia` apenas para seu jogador, conserva marcos no perfil temporário e registra as ocorrências em `F.events`, sem emitir esses eventos de QA à API.

## Protocolo previsto para uma sessão com acesso autorizado (não executado)

1. Confirmar `Server Play`, um jogador e UI hidratada. Não executar no Edit. Ler estado antes de começar; uma sessão que já estava em Play pode ter feito gravação legítima anterior, que a fixture não pretende desfazer.
2. Usar `qa/SafeFixture.lua` somente se a sessão tiver acesso autorizado ao módulo PlayerData, sem contornar a restrição identificada acima. Chamar `begin(player)` uma única vez e manter a referência retornada pelo ambiente de testes.
3. Chamar `assertSaveBlocked()`. O resultado deve ter `semSalvar=true`, `dev=true`, `devSalvar=false`, com bloqueio confirmado sem chamar a implementação original de salvar.
4. Preparar cada fase com `reset("nome")`, depois usar a UI Client real e verificar servidor com `status()`. Para estado especial, `profile()` permite mudar somente o perfil de fixture; `sync()` reapresenta o snapshot.
5. Ao terminar, fechar janelas/cancelar x10 no Client, chamar `restore()` no Server, exigir `restored=true` e `persistenceStillBlocked=true`; encerrar Play imediatamente. Guardas e hooks continuam ativos durante PlayerRemoving/BindToClose e desaparecem no Stop Play. Não restaurar autorização para salvar dentro da sessão.

API do helper de referência: `begin(player)`, `assertSaveBlocked()`, `reset(phase)`, `profile()`, `sync()`, `status()`, `restore()`. As fases estão na matriz abaixo. Não há tentativa de carregamento ou execução alternativa neste documento.

## Matriz de teste e evidência esperada

| Fase | Preparação | Ação real Client | Assert servidor |
|---|---|---|---|
| `empty` | Perfil novo, inventários/mochila vazios | Abrir inventário/loja/forja/missões, comprar sem saldo | Estado vazio útil; `ok=false` onde aplicável; saldo/inventário intactos. |
| `mining` | Picareta e mochila iniciais, ilha1 liberada | Viajar à ilha1, selecionar minério, golpear, abrir menu durante aproximação | HP diminui por dano servidor; quebra aumenta mochila/minerados; novo menu cessa novos pedidos; slots/dinheiro não mudam indevidamente. |
| `economy` | 3 minérios comuns e saldo calculado para picareta2+mochila2+1000 | Viajar ao Ignis de verdade, vender, comprar/equipar picareta2 e mochila2, cancelar outra compra | Ganho esperado = floor(soma valor*qtd*Economia.multMoedas); mochila vazia; custos debitados uma vez; `picareta`, `picaretasCompradas`, `mochilaTier` e capacidade atualizados. |
| `inventory` | 3 pets e 3 hats reais do catálogo, nível1, UIDs retornados | Selecionar, equipar/desequipar, melhores, pesquisar; confirmar postura/pets atrás | Arrays equipados contêm UIDs existentes, tamanho <= slots; dano muda; atributos e modelo equipados acompanham; pesquisa não muda perfil. |
| `gacha` | 12 vezes custo da área1 e giros0 | Ir à máquina real, x1 gratuito, depois x10 | Primeiro giros+1 sem débito e raridade mínima; depois10 giros/+10pets e débito10*custo, respeitando0.6s; retorno `Calma ai` não conta como giro. |
| `quests` | Primeira missão da área1 em meta e não resgatada | Abrir e resgatar; tentar novamente | Moeda aumenta exatamente premio; r=true; segundo pedido não duplica. Preparação é fixture, não prova que progressão foi conquistada. |
| `areas` | Apenas área1, saldo exato custo área2 | Desbloquear área2, viajar e voltar | Saldo0, áreas[2]=true, servidor publica CurrentAreaId; transição termina, nova compra rejeita duplicação. |
| Diário opcional | `empty`, daily.ultimo0 | Resgatar uma vez e repetir | dia avança, ultimo=hoje, prêmio uma vez, salvar bloqueado. |
| Mochila cheia | `mining`, completar mochila via profile()+sync() | Tentar golpe, clicar vender | Mensagem clara e ausência de quebra/recompensa indevida, fluxo de venda íntegro. |

Não usar `IgnisService.vender(player,true)` para testar a venda manual, pois `auto=true` ignora a exigência de lobby. Não simular atributos de local para passar validação; utilizar `UITravel`/caminhada normal. Não substituir sorteio, remotes ou validações de distância para afirmar que o fluxo passou.

## Limites da evidência

- Testes com fixture validam comportamento e contratos em Play, não persistência em produção.
- Chamadas diretas `R.<RemoteFunction>.OnServerInvoke(player,...)` ou serviços equivalentes validam lógica do servidor e atualização de dados; somente cliques/teclas na UI validam navegação, loading, cancelamento e feedback.
- Tool/mesh e postura devem ser observados depois que PicaretaTool atualizar o equipamento, não apenas pelo campo `perfil.picareta`.
- Mudanças nas rochas e nos modelos são locais ao runtime Play; Stop Play restaura mundo Edit. O rollback do helper restaura o perfil original (campos persistíveis) com cópia profunda e mantém as guardas de não salvar.
- A fixture foi escrita e revisada estaticamente; não foi instalada ou executada nesta subtarefa.
