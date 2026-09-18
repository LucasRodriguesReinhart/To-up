# Anime Mining Simulator — reformulação de áudio V3
Data: 17/09/2026 · Place 101959830085647

## Estado da entrega
O sistema foi implementado no Studio e passou pelos testes automatizados de reprodução, variação, limites, limpeza, marcadores procedurais e transição musical. A última execução técnica está em [FINAL_QA_UI_SESSION.json](qa/FINAL_QA_UI_SESSION.json).

**Salvamento no Roblox confirmado:** a tarefa que operou a UI nativa do Studio registrou às 00:56:06.333 a mensagem de alterações salvas em Anime Mining Simulator após Ctrl+S. A evidência nativa foi lida e está em [SAVE_CONFIRMED.json](../ui-v2/qa/SAVE_CONFIRMED.json). Isso confirma salvar o place, sem publicação pública. Uma cópia local completa `.rbxl` não foi gerada neste fechamento; fontes, manifestos e backups locais estão disponíveis nesta pasta.

**A aceitação auditiva permanece pendente.** Não houve escuta crítica real em fones/alto-falantes, teste cego de reconhecimento, medição do mix final de saída ou aprovação de fadiga após 100 golpes. Reprodução automatizada e análise de waveform não demonstram satisfação, conforto ou ausência de clipping perceptível. Portanto esta entrega não recebe o rótulo de sound design perceptualmente aprovado.

As alterações da tarefa paralela de UI foram incorporadas por merge específico de áudio, preservando a interface que estava sendo reconstruída. A conferência final em Edit confirmou as 19 fontes iguais aos arquivos entregues, todas compilando, backup presente e nenhum dos três scripts temporários de QA instalado. [VERIFICACAO_FINAL.json](VERIFICACAO_FINAL.json) registra fontes, hashes e estado do salvamento.

## Auditoria anterior
Foram exportados e examinados os 63 scripts fora de ServerStorage. O inventário também registra 95 scripts armazenados em ServerStorage, examinados apenas por metadados. Em edição havia 19 Sounds, incluindo três fontes/backups inativos. O snapshot inicial de Play continha 32 Sounds e 12 SoundGroups.

Problemas confirmados:
- Um Sound novo por camada e Attachment novo por emissão 3D. O limite anterior contava eventos, não camadas simultâneas.
- Contadores expiravam em 0,6 segundo, independentemente da duração real. O cleanup de quatro segundos podia cortar o antigo erro, cuja reprodução desacelerada ultrapassava esse tempo.
- Dois takes de pedra sem prevenção de repetição imediata.
- Venda calculava intensidade pela quantidade de itens, ignorando o valor recebido. Auto Sell não compartilhava essa resposta.
- Mythic compartilhava a assinatura de Legendary; Uncommon compartilhava Common.
- Música controlada por um grupo separado; cinco grupos de efeitos apareciam duplicados entre servidor e cliente.
- Mute de mineração não abrangia a coleta prometida pela interface.
- Sem preload do banco de efeitos; sem presença sonora espacial para portais/forja/água.
- Swing e hit eram agendados por delays independentes da amostragem da pose; deduplicação usava uma janela geral de 0,45 segundo.

Duplicatas identificadas: Premio/Compra compartilhavam 93529351909119; OST/backup/Theme_0 compartilhavam 112898538778548; templates das áreas repetiam IDs da música dinâmica. Compartilhar ID não significa reprodução simultânea.

**Removidos da reprodução ativa:** controlador musical paralelo, criação de Sound por hit, contador antigo por evento, erro longo, prêmio/moeda de proveniência pouco clara, prêmio por partícula visual de moeda e sons de portal disparados antes da transição confirmada. Os templates legados e backups foram preservados; o OST legado foi explicitamente interrompido. Detritos antes declarados sem uso agora participam da quebra.

A relação completa de objetos, IDs e achados está em [AUDIT.md](AUDIT.md).

## Identidade e referências
Direção: pedra compacta, metal curto, movimento de ar discreto e cristal tonal para progressão. A importância vem de ritmo, timbre, camadas e intervalos; não de aumentar tudo de volume. Mineração cotidiana recebe menos densidade que uma quebra; progressão e raridade ocupam o primeiro plano brevemente.

Foram estudadas fontes primárias de Roblox Beyond the Dark, Diablo IV, Audiokinetic/Wwise e a descrição técnica da apresentação de Overwatch na GDC. Princípios aplicados: separação de ambiente e fontes físicas, variação controlada, orçamento de vozes, hierarquia e identificação pelo som. Não foram extraídos sons dessas referências.

Os arranjos/motivos dos eventos são novos para o sistema, usando samples disponíveis na biblioteca Roblox. **Não são gravações exclusivas produzidas do zero.** Nenhum áudio foi extraído de anime. As sete músicas existentes foram mantidas; não foi composta uma trilha nova. Origem, carregamento e parâmetros finais constam em [ASSET_FINAL.md](ASSET_FINAL.md) e [ASSET_MANIFEST_FINAL.json](ASSET_MANIFEST_FINAL.json). Pesquisa e links primários: [RESEARCH.md](RESEARCH.md).

## Novo sistema
Há 31 IDs únicos carregados no cliente: 24 efeitos/ambiências e sete músicas.
- Pedra: cinco samples.
- Metal: dois; impacto grave: um.
- Quebra: dois ataques; detritos: um.
- Swing: três takes.
- Click: dois; cristal tonal: um; vidro: um; moedas: dois.
- Loops: fogo, vento, água e energia.

Os samples reutilizados foram selecionados para as mesmas funções. Foram adicionados takes para ampliar a variação, substituídos os sons monetários/tonais de origem menos clara e reorganizado todo o despacho em `AudioCatalog` + `SomJogo`. A seleção técnica não representa aprovação auditiva.

Uma análise de waveform detectou o ataque de um sample de moeda perto de 349 ms, usando o primeiro cruzamento de 8% do pico; o trecho inicial estava abaixo desse limiar, sem prova de silêncio absoluto. O recorte anterior de 140–200 ms podia terminar antes do ataque. Seu início passou a 344 ms. Whooshes recebem entradas de 16/56/65 ms; o cristal tonal, 200 ms; o vidro, 108 ms. Ganhos por sample compensam diferenças de nível. `PlaybackRegion` limita a janela no próprio engine; a liberação do pool também possui watchdog. As durações do catálogo são tetos: o fim do arquivo e o pitch podem encurtá-las, especialmente nas notas agudas.

## Mineração
**Swing:** três variantes, microvariação de pitch, duração curta e ganho abaixo do impacto. O modo automático reduz ganho e densidade.

**Hit:** cinco takes de pedra sem repetição consecutiva, combinados com metal discreto. Famílias reutilizáveis stone/metal/crystal/magic/lava selecionam a materialidade conforme área/tipo disponível. Ferramentas avançadas podem receber corpo grave; isso é omitido no automático. Pitch varia aproximadamente ±3,5% nas texturas; volume varia ±4%. Motivos tonais não recebem desafinação aleatória.

**HP baixo:** crack discreto quando HP cai abaixo de 28%, com intervalo mínimo de 0,30 s. A quebra possui ataque próprio, detritos suaves e acento tonal nas variantes maiores. Há seis configurações de quebra, do comum ao chefe, compartilhando dois takes de ataque. Não são seis arquivos gravados distintos.

**Sincronia:** o projeto usa animação procedural. `MiningSwing.Advance` publica SwingStart/Hit/SwingEnd no mesmo tempo amostrado pela pose; `MineracaoVisual` usa o evento Hit para áudio, VFX, reação da rocha e câmera. O timestamp inicial identifica o golpe e evita duplicação entre previsão e confirmação do servidor. Cancelamento encerra trail e resolve somente impactos já confirmados. Foi adicionado um adaptador `GetMarkerReachedSignal` para AnimationTracks futuros, mas o fluxo atual não usa um track nativo e esse adaptador não foi validado com asset animado real.

**Coleta:** agrupamento em 65 ms, sequência limitada de cinco notas (0, 2, 4, 7, 12 semitons), reset após pausa. Um lote de 100 solicitações no mesmo instante produziu um feedback. O inventário atual recebe minério diretamente; não foi inventado um sistema de drops físicos.

Não existe crítico de gameplay identificado no código atual: `critical_hit` está disponível no catálogo, sem criar uma mecânica falsa. `ore_drop` também fica disponível para uma futura aparição física de minério.

## Economia e progressão
A venda usa o ganho monetário confirmado pelo servidor:

| Faixa | Valor recebido | Desenho |
|---|---:|---|
| Pequena | abaixo de 1.000 | confirmação + moeda |
| Média | 1.000 a 9.999 | segundo toque de moedas |
| Grande | 10.000 a 999.999 | resolução cristalina |
| Enorme | 1.000.000 a 9.999.999 | acento agudo adicional |
| Jackpot | 10.000.000 ou mais | corpo grave e resolução mais rica |

Venda manual e Auto Sell compartilham essa escala. A animação visual de moedas não dispara um som para cada partícula.

Compras usam retorno confirmado; upgrade máximo tem motivo próprio. Level Up, área nova, missão, achievement e boost possuem eventos distintos. Reequipar/desequipar recebe respostas complementares. Não foram alterados preços, taxas de drop, saldo ou poder das ferramentas para justificar áudio.

Preferências numéricas de Master/Music/SFX/UI/Ambience e três toggles passam por whitelist, rejeição de NaN/infinito, clamp e schema compartilhado. O servidor recebe patches limitados por taxa e grava no perfil já existente, pelo autosave normal. A interface informa o estado de perfil/sessão e pendências. **Não foi realizado teste de persistência após sair e entrar com alteração deliberada do perfil real.**

A revisão final retirou o som duplicado da substituição física da Tool: a confirmação de equipamento agora pertence ao retorno da ação da UI. Também retirou a reaplicação dos atributos pelo servidor a cada patch de volume, que podia sobrescrever um ajuste local mais recente. Preferências são aplicadas na carga inicial e reconhecidas pelo cliente sem retroceder cliques pendentes.

## Recompensas e raridade
Common, Uncommon, Rare, Epic, Legendary, Mythic e Secret possuem arranjos próprios:
- Common: uma nota curta; Uncommon acrescenta resposta.
- Rare: intervalo aberto; Epic: figura de três notas.
- Legendary: resolução de quatro notas.
- Mythic: registro e sequência diferentes de Legendary.
- Secret: antecipação de ar, corpo e assinatura de quatro notas, com maior redução temporária da música.

Abertura de lote gacha toca um reveal inicial e uma assinatura da maior raridade do lote, evitando dez stings simultâneos. Reabrir ou reorganizar o popup não repete o prêmio. Notificações genéricas são suprimidas perto de recompensas importantes.

O teste técnico reproduziu as sete raridades. A identificação cega das raridades e a qualidade de sua diferenciação permanecem pendentes de escuta.

Daily e códigos agora devolvem um resumo da recompensa efetivamente entregue. O cliente escolhe uma celebração principal por raridade, boost ou moeda; snapshots e feedbacks auxiliares dessa transação preservam o visual sem repetir a celebração. Se o pet pedido cair para raridade inferior pela regra já existente, o som segue a raridade entregue. Inventário cheio não recebe um sting de item que não foi concedido.

## Interface
Família coesa de click seco, tab/toggle menores, open/close complementares, compra/confirm, cancel neutro e erro curto. Equip inclui movimento e metal; unequip é menor. O erro anterior longo foi substituído por dois clicks discretos.

Hover permanece definido, mas não foi imposto a todos os botões: não há necessidade de transformar passagem do cursor em som constante. A UI foi integrada à reconstrução paralela sem restaurar versões antigas de Menus/ExpeditionClient. Os controles de áudio usam passos de 5%, valores visíveis, restauração de padrão e área rolável. Na inspeção da tarefa de UI, o telefone emulado apresentou viewport de 401×776: scroll 342×586, canvas 1788, controles +/−/reset de 44,2 px físicos e nenhum overflow de texto. A paisagem 749×361 manteve conteúdo rolável. Isso não equivale a um teste em telefone físico ou a 390×844 exatos.

## Mundo e áudio espacial
`AudioWorld` usa os objetos reais e acompanha objetos adicionados/removidos:
- Portais Portal1–6 do Santuário: energia localizada, raio de 36 studs.
- PortalDeProgressao: raio de 34.
- Ignis/hot_billet: fogo, raio de 38.
- ForgeChimney: fogo, raio de 42.
- Superfície que contém FluxoCachoeira: água, raio de 52.
- Martelo de Ignis: evento emitido no contato com as faíscas, raio de 40; sem RemoteEvent novo por batida.
- Base regional: vento baixo; energia discreta na região sombria.

São quatro vozes ambientes persistentes: uma base regional e até três fontes físicas próximas. A seleção é feita a cada 0,25 s, com fade. Emissores móveis têm posição atualizada a cada dois segundos. Portais compartilham a família energética; não se afirma que cada um ganhou uma gravação temática exclusiva.

Efeitos posicionais usam Attachments e `InverseTapered`. Hits locais: mínimo 8, máximo 64 studs. Remotos: mínimo 5, máximo 44, uma única camada e 36% do ganho de origem. Fontes fora do alcance são descartadas antes da reprodução. UI e recompensas pessoais permanecem não posicionais/locais. Passos e demais sons do avatar passam pelo grupo de gameplay, com alcance de 38 studs.

Não foram adicionados sons a lava/máquinas/cristais de cenário sem um objeto/função correspondente identificado. Forge Success está disponível; o jogo atual não recebeu uma mecânica nova de crafting só para cobrir esse evento.

## Música, SoundGroups e mixagem
As sete faixas existentes foram preservadas, com dois slots reutilizados para transição. A faixa anterior continua enquanto a nova ainda não carregou. Transições rápidas terminam com apenas uma faixa tocando. Não se afirma que as emendas musicais foram aprovadas por audição.

```text
MASTER
├── MUSIC
├── AMBIENCE
└── SFX
    ├── SFX_GAMEPLAY
    │   └── SFX_MINING
    ├── SFX_REWARDS
    ├── SFX_WORLD
    └── SFX_UI
```

Os grupos são criados exclusivamente no cliente. O grupo musical legado permanece inativo, separado dessa árvore.

Padrões: Master 80%, Music 60%, SFX 85%, UI 65%, Ambience 55%; os ganhos são multiplicativos. Recompensas e mundo recebem submixes de 90% e 75%. Música usa volumes de faixa próximos de 0,20–0,23, com redução temporária durante grandes recompensas. O mute não é sobrescrito pelo retorno do ducking.

Equalização suave reduz agudos de mineração/UI e abre espaço na música. Compressor Master: threshold -7 dB, ratio 3:1, attack 10 ms, release 120 ms, sem makeup. **Esse compressor não é um limiter true-peak, nem prova de ausência de clipping.** Foram examinados níveis dos samples, não medida a saída final completa do jogo.

## Performance, rede e limpeza
- Pool fixo de 24 Sounds e 24 Attachments para one-shots; nenhum Sound novo por hit.
- O limite de 24 cobre apenas os one-shots geridos por SomJogo. Música, ambiente, cache silencioso e sons padrão do avatar ficam fora desse número.
- Limites por bus: Mining 10, Rewards 8, UI 3, World 4; limite total de 24 e máximo de quatro vozes remotas.
- Dois slots musicais, quatro ambientes e cache silencioso dos 31 assets.
- Fila limitada a 48 camadas; eventos atrasados são descartados em vez de reproduzidos fora do tempo.
- Roubo somente de voz de menor prioridade, priorizando ação local.
- Coletas agregadas; eventos com cooldown; histórico diagnóstico limitado a 160 entradas.
- Retirada por duração/estado, fade de cauda e teardown explícito.
- Preload em três trabalhadores com lotes pequenos; asset indisponível não provoca hit atrasado.
- Reutilização dos remotes de mineração/economia existentes; timestamp do golpe adicionado à confirmação. Um novo RemoteFunction atende apenas preferências.
- Servidor não cria mixer nem reproduz SFX locais por require indireto.

## Testes executados
| Verificação | Resultado observado | Alcance da evidência |
|---|---|---|
| Assets atuais | 31/31 carregados; zero falhas | Cliente Studio desta sessão |
| 100 hits | 5 takes; 0 repetições consecutivas; pool permaneceu 24 | Eventos de áudio sintetizados no harness |
| Duração da rodada de hits | 14,84 s para 100 solicitações | Não representa mineração real sustentada na velocidade máxima |
| Pickups sequenciais | 100 feedbacks para 100 solicitações espaçadas | Reprodução/contagem técnica |
| Pickup burst | 100 solicitações agrupadas em 1 feedback | Sem fila longa após o lote |
| Caos | pico 20/24; 73 substituições; 2.351 descartes controlados | Mistura sintética com 15 solicitações remotas por ciclo |
| Cleanup | zero vozes transientes e zero camadas pendentes após espera | Sem vazamento no período ensaiado |
| Marcadores | SwingStart, Hit, SwingEnd e Cancelled emitidos uma vez | Fixture procedural; não transação real contra minério |
| Música | uma faixa ativa após transições rápidas | Controle de slots/fades |
| Preferências | schema, boolean false, clamp, NaN/inf e whitelist aprovados | Validação pura; sem novo login |
| Mute/culling | aprovados na rodada de polish | Master/mineração/coleta e fonte remota distante |
| A/B técnico | três famílias reproduzidas, 10 hits cada | Nenhum vencedor auditivo declarado |
| Raridades/vendas | sete raridades e cinco tiers exercitados | Identificação perceptual não validada |
| Regressão Daily/códigos | 13 fixtures aprovadas; estado de gameplay antes/depois igual | Luau CLI 0.738 com dependências simuladas, sem perfil real |
| Preferências atrasadas | ACK antigo não sobrescreve ajuste novo; whitelist preservada | Fixture local, não rede real |
| Smoke após últimos patches | 31 assets, 9 grupos, 24 slots; UI carregada; 0 ativos/0 fila após StopEffects | [FINAL_SMOKE_UI_SESSION.json](qa/FINAL_SMOKE_UI_SESSION.json); console de gameplay sem erros nessa execução |

Os últimos testes isolados estão em [LOCAL_FIXTURE_QA.json](final-fixes/LOCAL_FIXTURE_QA.json). Incluem Daily 2/5/7, múltiplos hats, fallback de raridade, inventário cheio, código monetário/hat/pet, código inválido e resgate duplicado, além de preservação de boosts de compra e drops da mineração. Não foram feitas transações ou escritas no DataStore real por esses fixtures.

O smoke final aguarda o RemoteFunction criado depois da construção do mundo. Ele verifica orçamento de fila durante sons concorrentes da UI e testa `StopEffects` como limpeza explícita. Duas versões preliminares desse harness presumiam endpoint imediato e fila global vazia no startup; essas premissas foram corrigidas. O teste prolongado anterior continua sendo a evidência de retirada automática das vozes após o cenário de carga.

No encerramento do QA, um comando de automação tentou orientação `Sensor`, recusada pela API do emulador. Esse erro não veio dos scripts de gameplay; a simulação foi encerrada e o Studio ficou em Edit. O teste não é apresentado como validação de sensor ou de dispositivo físico.

A primeira execução de refinamento acusou 121 vozes no teste de 100 pickups e três no burst porque o contador global incluía as duas camadas do martelo de Ignis. O diagnóstico passou a contar por evento; a repetição final confirmou 100 e um. O relatório intermediário foi preservado em `qa/automated-refinement-interference.json` para rastreabilidade.

Não foi realizado teste real com múltiplos clientes. A saturação de solicitações remotas verifica os limites do mixer, não latência/rede de uma sessão multiplayer. Também não foram efetuadas compras, grants, vendas ou alterações de saldo para os testes: o perfil conectado era persistente.

## Limitações e aceitação restante
1. Escuta crítica de 100 hits/100 pickups e Auto Mine prolongado, com música ligada/desligada, em fones e speaker pequeno.
2. Teste cego de Hit/Break/Sell/Level Up/Legendary/Mythic/Secret e comparação A/B com intensidade percebida equivalente.
3. Mineração integrada real nas velocidades extremas, especialmente cancelamento/troca de alvo sob latência e último hit seguido de quebra.
4. Sessão multiplayer real com vários jogadores próximos.
5. Medição/escuta de clipping, mascaramento e transições de loop; remove test auditivo de cada camada.
6. Persistência após reconexão, respawn com controles e inspeção dos emissores em todas as regiões.
7. Confirmar carregamento/permissões também no cliente publicado, fora do Studio.

Esses pontos não foram marcados como aprovados. O harness reproduz cenários e registra funcionamento, mas não substitui a avaliação sonora solicitada.

## Fontes, instalação e recuperação
Fontes próprias/alteradas ficam em `src/`. A versão final de Menus/ExpeditionClient deve ser a sincronizada com a tarefa de UI; `merged-ui-final/` preserva o patch de integração e sua validação. Os scripts de teste ficam em `qa/` como ferramentas de revisão e devem permanecer fora de StarterPlayerScripts na entrega.

Backup de fontes no Studio: `ServerStorage.BeforeAudioV3_20260917`, com caminhos e classes originais. Exportação anterior: `before/`. **Restaurar integralmente Menus, ExpeditionClient, MineracaoVisual ou IslandTransition do backup também reverteria alterações da tarefa de UI.** Nesses arquivos, a recuperação deve ser por merge dos trechos de áudio. Não existe rollback automático aplicado.

Foram preservados contratos externos, remotes de gameplay, postura/animação, geometria de contato, VFX, recompensas e economia. A implementação exige os novos módulos AudioCatalog e AudioPreferences junto das fontes atualizadas; copiar SomJogo isoladamente não constitui instalação completa.
