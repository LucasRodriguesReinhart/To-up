# Plano de validação — Áudio V3

Data: 17/09/2026. Plano específico para o projeto e sua auditoria anterior. Este arquivo define testes; não declara resultados executados. Não modificar progressão/saldo real para simular áudio. Usar harness local e tabelas de perfil descartáveis; para persistência, usar store falso ou namespace de QA separado.

## Evidências necessárias

Cada execução registra versão/hashes dos scripts, modo Edit/Play, cliente(s), seed aleatória, cenário, duração, configuração dos volumes e métricas. Capturar logs estruturados sem dados privados e, quando possível, áudio/vídeo. Um evento marcado 'played' por código não confirma que o arquivo carregou, que era audível ou que soava adequado.

Campos por evento: eventName, cycleId, sourceUserId de teste, assetId, layer, slot, priority, scheduledAt, markerAt, playRequestedAt, endedAt, IsLoaded, PlaybackSpeed, volume base, ganho final, material, local/remote, motivo de descarte. Relógio de timeline: workspace:GetServerTimeNow; tempo de CPU local: os.clock. Não subtrair um do outro.

## T01 — Inventário e bootstrap

1. Iniciar cliente sem clicar. Contar grupos por nome e caminho; não pode haver duplicatas.
2. Verificar cada Sound.SoundGroup; Parent sozinho não satisfaz roteamento.
3. Require SomJogo no servidor pelo caminho AreaBuilder → Theme: não deve iniciar playback, criar pool de cliente ou duplicar grupos por corrida.
4. Respawn e reabertura de UI não podem duplicar conexões, pools ou loops.
5. Conferir ausência de scripts QA persistentes em StarterPlayer/ServerScriptService após o teste.

Critério: uma hierarquia de mix intencional; quantidade de slots/loops volta ao orçamento inicial. Sons padrão de avatar devem ser listados como exceção ou explicitamente roteados, sem apagá-los incidentalmente.

## T02 — Assets, direitos, preload e autoplay

- Manifesto por ID: função, origem verificável, autor/biblioteca, permissão/licença disponível, duração, canais, estado de moderação e acesso pela experiência. Comentários 'PSE/APM' e nomes do Toolbox não bastam como prova.
- Deduplicar IDs para preload. Capturar callback final de AssetFetchStatus; depois validar IsLoaded e TimeLength no cliente. Não tratar sucesso de pcall como sucesso dos assets.
- Testar falha com ID de fixture inválido ou loader falso, sem alterar catálogo publicado. Jogo continua; camada omite ou usa fallback aprovado. Não deixar Loaded:Wait sem limite bloquear input.
- Confirmar que o primeiro click/hit após entrar não depende de download tardio. Música só começa quando a preferência carregada permite; Master/Music=0 não podem produzir um frame inicial audível.
- Depois de fechar/reabrir sessão, arquivos ainda carregam e permissões continuam válidas. Upload/moderação concluídos não substituem este teste.
- Preview autorizado de asset não é evidência de reprodução no lugar publicado. Deixar cada resultado claramente identificado como Edit, cliente de Studio ou experiência publicada.

Critério: todos os IDs do catálogo final classificados como sucesso, omitidos intencionalmente ou pendentes; nenhum ID silencioso desconhecido mascarado por fallback.

## T03 — Timeline e marcadores de mineração

Baseline: início recebido do servidor em `starts`; MiningGeometry.ImpactTime e MiningAnimations.CONTATO são 0,28s; TRAIL_INICIO=0,15s. LocomocaoBigAxe amostra a pose procedural a partir de MiningSwingStart.

1. Instrumentar ciclo e marcadores sem alterar dano. Comparar tSwing com starts+0,15 e tHit com starts+0,28, ou com os tempos centralizados finais.
2. Para AnimationTrack real, exigir GetMarkerReachedSignal ligado uma vez e verificar o asset contém os markers esperados. Para a trajetória procedural atual, exigir emissão semântica pelo avanço da própria timeline; documentar que não é um AnimationTrack nativo.
3. Um ciclo deve gerar no máximo um hit principal, mesmo com previsão+confirmação. Confirmar que fallback tardio usa cycleId/timestamp correspondente e não apenas uma janela global por minerador.
4. Gravar delta visual/VFX/play request. Meta inicial: desvio de disparo dentro de um frame na máquina de teste; qualquer discrepância auditiva deve ser calibrada ao ataque do sample. Log de Play mede solicitação, não latência de hardware.
5. Cancelar antes do swing e entre swing/impacto: desequipar, morrer, teleportar, destruir/ocultar alvo. Não pode haver whoosh/impacto órfão ou camada atrasada do ciclo anterior.
6. Testar latência simulada de 0/100/250ms e jitter; chegada atrasada não pode disparar retrospectivamente uma sequência inteira de sons no mesmo frame.
7. Verificar ferramentas de todas as famílias, inclusive mundo >=3, e câmera próxima/afastada. Mudar som não pode alterar a postura ou tempo de dano.

Critério: uma identidade de ciclo atravessa intenção, marker, confirmação e cancelamento. Dano, alcance e intervalos permanecem governados pelo gameplay anterior.

## T04 — Repetição e velocidades

Executar 100 hits com seed fixa por material e sequência adicional com seed diferente. Registrar sample e pitch de cada camada; exigir ausência de repetição imediata onde houver >1 take e variedade conforme catálogo. Não há exigência de que 100 sorteios tenham contagens exatamente iguais.

Repetir em velocidade base, upgrades máximos existentes e Auto Mine por vários minutos. Ajustar apenas fixture de áudio para cenário acima da cadência do gameplay; não mudar o intervalo real nem conceder upgrade ao perfil real. Conferir redução de camadas/cadência se implementada. Pitch não cresce indefinidamente com velocidade.

Audicionar protótipos A/B no mesmo ganho percebido: 10, 50 e 100 golpes. Registrar transiente, materialidade, aspereza, fadiga e distinção hit/break. Comparação matemática não aprova conforto. O último golpe não pode sobrepor dois transientes plenos desnecessários de hit+break.

## T05 — Pool, budget e cleanup

1. Disparar 100 eventos mais rápido que o intervalo mínimo, depois esperar a maior duração e o watchdog. Contagem de instâncias e conexões volta ao baseline.
2. Saturar por camadas: 10 eventos com três camadas equivalem a 30 vozes potenciais. Conferir budget global e por categoria, incluindo delays de camadas.
3. Reservas locais: saturar com outros jogadores/ambiente e então clicar/minerar localmente. Evento local importante mantém prioridade.
4. Reusar um slot antes de callback antigo: o token antigo não pode parar/liberar novo som. Testar Ended, Stop, cancelamento de cena, asset falho e duração maior que o normal.
5. Verificar cancelamento de todos os atrasos agendados no teardown. Nenhum callback revive Sound após desligar o controller.
6. Registrar active/peak/reused/stolen/dropped/aggregated/loadFailures. Instâncias criadas por hit após pool aquecido devem ser zero, salvo expansão limitada explicitamente documentada.

Critério: máximo observado <= orçamento configurado; zero crescimento cumulativo e nenhuma perda sistemática de feedback prioritário. Orçamento de projeto não deve ser apresentado como limite oficial Roblox.

## T06 — Coleta e economia

- Injetar 30 pickups no mesmo frame, 100 em sequência e pausas acima/abaixo do reset. Exigir agregação, sequência musical limitada e nenhuma cauda de fila atrasada por segundos.
- Testar vendas sintéticas +100, +10.000, +1.000.000 e +10.000.000 com **mesma quantidade**. Tiers precisam responder ao valor; valores de fronteira classificam previsivelmente. NaN/inf/negativo/zero precisam de comportamento seguro.
- Vendas manuais e Auto Sell confirmadas percorrem o mesmo evento estruturado, sem interpretar número de texto formatado. Evitar vender duas vezes, tocar venda sem sucesso ou combinar toast+coinBurst+sting em três celebrações plenas redundantes.
- Falha de compra, inventário cheio e mochila vazia não tocam confirmação positiva. Upgrade máximo distinto só quando o dado real indica máximo; equip e unequip devem refletir o resultado.
- Não gastar Robux, resgatar códigos/daily reais, criar compras ou editar saldo real para essa verificação. Harness de retornos de UI não chama remotos de compra.

## T07 — Preferências persistentes

Usar profile fixtures com campos ausentes, schema antigo, valores válidos 0/0,5/1, NaN/inf, strings e limites fora de faixa. Defaults e clamp devem ser determinísticos e serializáveis. Testar remote com whitelist, tamanho limitado, tipos restritos e rate limit; entrada de preferências nunca altera saldo, inventário ou flags de compra.

Executar save/load através de adapter/store falso e novo objeto de sessão; comparar somente os campos de áudio. Não alegar persistência de produção baseada em atributo local ou mock. Se houver namespace de QA real isolado, documentar o nome e limpar apenas a chave de teste autorizada.

Master=0 silencia todas as categorias gerenciadas. Music=0 não bloqueia SFX; SFX=0 não bloqueia Music. Testar sliders enquanto ducking e crossfade estão ativos; release não deve desfazer mute ou preferência recente. Confirmar também SomMineracaoEnabled/legado, se preservado, silencia coleta e camadas de reward da quebra prometidas pela UI.

## T08 — Raridades e abertura

Disparar Common, Uncommon, Rare, Epic, Legendary, Mythic e Secret via harness, em ordem randomizada, com volumes comparáveis. Pedir identificação sem tela; anotar confusões e ajustar timbre, motivo, envelope, antecipação e finalização. Mythic não pode continuar alias acústico de Legendary se o requisito de distinção for mantido.

Validar activation/build/reveal sincronizados aos eventos da animação de abertura, skip, fechamento, auto-opening e batch de resultados. Som raro depende do resultado confirmado e não da animação antecipada. Desativar som durante antecipação cancela/reduz o restante conforme a preferência. Vários Secret no harness não devem empilhar stings ilimitados nem deixar música ducked para sempre.

## T09 — Mundo, música e multiplayer

Percorrer lobby, Ignis/forja e todos os portais/áreas. Medir distância da câmera/listener: junto, RollOffMinDistance, metade e após RollOffMaxDistance. A pequena forja não atravessa o mapa; fontes ausentes/removidas não deixam loop órfão. Batida de martelo deve corresponder ao contato e faíscas; não usar timer independente aproximado se a animação expõe o instante.

Cruzar A→B→A rapidamente durante crossfade, teleportar longe, respawn e ativar mute no meio. Máximo de loops/canais previsto e faixa final correta. Avaliar emendas dos loops por escuta; pausar/faça Volume=0 não comprova ausência de clique.

Dois clientes reais de Studio para rede: A minera e B ouve perto; B se afasta e rotaciona câmera; cada um tem preferências diferentes. UI e recompensa de A não tocam em B. Sons remotos seguem distância/limites do receptor. Verificar explicitamente se B deve ouvir break, pois antes só recebia hit. Em seguida simular densidade de 15 mineradores no harness; isso complementa, mas não substitui, o teste com dois clientes.

Critério: sons locais identificáveis sob carga; não criar RemoteEvents por camada, replicar preferências desnecessariamente a todos nem reproduzir UI globalmente.

## T10 — Mix e encerramento

Escutar sem música, com música, volume baixo, fones e speaker pequeno. Testar pico simultâneo de mineração+break+coleta+venda+UI+ambiente. Usar captura e medição quando disponível; Volume<1 e limitador presente não provam ausência de clipping. Manter registro separado de medição e julgamento auditivo.

Ao terminar: parar Play, remover fixtures/conexões temporárias, conferir diffs e backup, verificar persistência no lugar pretendido e emitir tabela de resultados **passou / falhou / não executado / depende de audição humana**. Nenhum teste perceptual, multiplayer real ou persistência pode ser marcado como passou só porque existe um roteiro para ele.
