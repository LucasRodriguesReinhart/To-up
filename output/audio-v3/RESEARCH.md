# Pesquisa de áudio — Anime Mining Simulator

Consulta em 17/09/2026. Este documento é pesquisa e proposta de parâmetros iniciais; não comprova execução no Studio, audição crítica, disponibilidade de assets ou aprovação dos testes perceptuais.

## Referências estudadas e aplicação

- **Roblox / Beyond the Dark:** o estudo oficial combina base ambiente 2D com fontes localizadas 3D, camadas reutilizáveis e grupos hierárquicos com ducking. Aplicação: vento discreto como base; forja, cristais e portais têm presença local e abrem espaço no fundo quando se aproximam. Ajustes de compressor precisam ser feitos para os samples reais, não copiados cegamente. [Estudo oficial](https://create.roblox.com/docs/resources/beyond-the-dark/sound-design).
- **Diablo IV / Blizzard:** a equipe descreve microvariações, limites de instâncias e prioridades dinâmicas para preservar clareza, além de separar quebra principal e detalhes de detritos. Aplicação: metal + pedra para impacto, quebra com identidade própria, limitar detritos e remover camadas secundárias no caos. O próprio relato salienta que cobrir um evento não significa reproduzir todas as suas instâncias. [Relato do Sound Supervisor](https://news.blizzard.com/en-us/article/23731236/diablo-iv-quarterly-updateoctober-2021).
- **Audiokinetic / Wwise 101:** o exemplo de quebra de gemas usa conjuntos distintos de ataque e cauda em seleção aleatória. Aplicação: 5 impactos coerentes de pedra e 3 caudas opcionais, escolha sem repetição imediata; não depender somente de variar pitch do mesmo arquivo. [Tutorial oficial de gemas](https://www.audiokinetic.com/en/courses/wwise101/?id=importing_an_audio_file_folder&source=wwise101). O resultado de busca disponibilizou o conteúdo; abertura direta posterior retornou 403.
- **Overwatch / equipe Blizzard na GDC:** a descrição da sessão coloca reconhecimento pelo som como objetivo do design em partidas com múltiplos personagens. Aplicação: teste cego deve distinguir Hit, Break, Sell, Upgrade e Secret antes de aumentar a densidade do mix. [Descrição primária da apresentação](https://www.gdcvault.com/play/1023010/Overwatch-The-Elusive-Goal-Play). Foi lida a descrição; não foi assistida a palestra.

Não há neste trabalho evidência suficiente para afirmar que foram jogados e avaliados auditivamente simuladores comerciais de Roblox. Beyond the Dark fornece a referência Roblox verificável. As recomendações seguintes são decisões de design para este projeto, não receitas atribuídas aos jogos citados.

## Direção de som proposta

Identidade: pedra compacta, metal curto e cristais quentes; ataques definidos sem agudo agressivo, ressonância mágica reservada à progressão. Motivo original de recompensa com intervalos de quinta/segunda, reapresentado com timbres diferentes. Sem samples, melodias ou falas extraídos de anime ou dos jogos de referência.

| Evento | Proposta inicial | Antifadiga / hierarquia |
|---|---|---|
| Swing | 4 variações, 90–180 ms, sopro com textura metálica sutil | 6–10 dB abaixo do hit; pitch 0,97–1,03 |
| Mining Hit | 5 takes por família; ataque físico e corpo integrados, 140–300 ms | Baralho embaralhado sem repetição na fronteira; ganho ±0,6 dB; pitch 0,97–1,03 |
| HP baixo | Acrescentar crack curto nas faixas <35% e <15% | Debounce por cruzamento de faixa; não tocar crack em todo golpe |
| Break | 3 variações, 350–700 ms; crack + corpo + poucos fragmentos | Deve substituir o hit pleno do último golpe ou atenuá-lo; evitar dobrar ataque |
| Pickup | 80–180 ms; cristal arredondado | Janela de agregação 70–100 ms; sequência de 5 notas limitada; reset após pausa |
| Sell | confirmação + moedas + pequena resolução musical | 5 faixas de valor logarítmicas; duração/timbre/cadência mudam antes do volume |
| UI | família curta de click, tab, open, close, confirm, error | Hover opcional e baixo; cooldown de 80 ms; erro neutro |
| Legendary/Mythic/Secret | textura, motivo e envelope distintos | Secret com antecipação curta + assinatura; ducking breve de fundo |
| Auto Mine | preservar transiente de confirmação | Reduzir corpo/magia, controlar densidade; não acelerar pitch com velocidade |

Esses números são pontos de partida e devem mudar após audição. Um hit com várias camadas pode ser renderizado como um sample composto, deixando somente material/magia variável em runtime. Isso reduz vozes e torna o transiente previsível.

### Comparação de protótipos

Produzir e comparar A metálico, B rochoso, C arcade e D híbrido com a mesma intensidade percebida. Escolher pela leitura após 100 golpes, não pelo golpe mais impressionante isolado. Retirar temporariamente cada camada; manter apenas quando sua remoção reduzir materialidade, clareza ou satisfação. Pitch aleatório nunca corrige um sample irritante.

## Engenharia Roblox verificada

### APIs, grupos e espacialização

A documentação atual classifica SoundGroups como legado e recomenda os objetos modernos de áudio. Para um projeto que já usa Sound, uma arquitetura Sound/SoundGroup coerente continua documentada; migrar tudo para AudioPlayer/Wire é uma decisão separada que exige revisão de roteamento. Sound.SoundGroup deve ser atribuído explicitamente; a posição do Sound na hierarquia decide a emissão, não seu bus. [Sound groups](https://create.roblox.com/docs/sound/groups).

Estrutura recomendada, se permanecer em Sound: MASTER > MUSIC, AMBIENCE, SFX; SFX > MINING, REWARDS, UI, WORLD. Os volumes são multiplicativos. Guardar preferências do jogador separadamente dos ganhos de ducking evita que a restauração de um tween desfaça um mute. Ducking de recompensa deve acumular pedidos e liberar pelo mais longo ou mais forte, sem disputa de tweens.

Para forja/portal, usar Attachment pontual; grandes Parts podem gerar emissão volumétrica que amplia inesperadamente o alcance. Sound em SoundService/Workspace emite sem posição. InverseTapered dá transição suave até o limite. Proposta inicial: impacto 5–45 studs; portal 7–55; forja 8–65. Ajustar à escala real, distância da câmera e proximidade entre objetos. [Sound objects](https://create.roblox.com/docs/sound/objects).

EmitterSize, MinDistance, MaxDistance e Pitch estão deprecated. Usar RollOffMinDistance, RollOffMaxDistance e PlaybackSpeed. IsLoaded é estado local, não replicado. [Sound API](https://create.roblox.com/docs/reference/engine/classes/Sound).

### Preload e tolerância a falhas

PreloadAsync aceita lista e callback por asset com AssetFetchStatus. Preparar pequenas listas de instâncias Sound com IDs deduplicados, priorizando mineração e UI; carregar ambiência/música em segundo plano. Registrar sucesso/falha individual; pcall apenas captura erro da chamada e não substitui avaliação do callback. Não bloquear o jogo indefinidamente esperando Loaded. Fallback só pode usar asset aprovado e carregável já verificado; caso contrário, omitir a camada e registrar a falha. [ContentProvider API e exemplo de callback](https://create.roblox.com/docs/reference/engine/classes/ContentProvider).

### Pool e orçamento de vozes

Recomendação de implementação, não limite oficial do engine: orçamento inicial de 24 one-shots ativos por cliente, além de 2 músicas de crossfade e até 4 loops ambientais relevantes. Reservar 6 vozes para feedback do jogador; limites locais de 4 hits, 3 pickups, 2 UI e 2 stings. Uma voz corresponde a uma camada; limitar eventos sem contar camadas falha.

Alocar slots reutilizáveis no início. Cada slot mantém Sound, attachment/part reutilizável se necessário, estado busy, prioridade, horário de início e token de geração. Antes de reutilizar: Stop, reiniciar TimePosition, ajustar SoundId, SoundGroup, Volume, PlaybackSpeed, Looped e posição. Liberar no Ended, no cancelamento explícito e por watchdog limitado; callback antigo não pode liberar uma reprodução nova. Conectar callbacks uma vez e destruir o pool completo no teardown. Loops nunca entram no pool de one-shots.

Em saturação: rejeitar evento distante/baixo antes de interromper o feedback local. Se necessário roubar a voz menos importante e mais antiga. Pickup agregado não é uma fila que toca atrasada por segundos. Contadores úteis: active, peak, droppedByBudget, aggregated, reused, loadFailures e stolen.

Evitar PlayLocalSound como substituto do pool: uma resposta de engenharia Roblox explica que ele cria reprodução interna separada, que dificulta localizar/controlar as cópias. O mesmo tópico sugere pooling quando criação/destruição for preocupação. [Resposta de engenharia Roblox](https://devforum.roblox.com/t/audioplayer-playing-should-overlap/4055469). Conteúdo confirmado no resultado indexado; a abertura direta exigiu JavaScript.

### Sincronização e rede

Conectar GetMarkerReachedSignal("SwingStart") e GetMarkerReachedSignal("Hit") uma vez por AnimationTrack. O marcador é um KeyframeMarker do asset de animação; nomes de keyframes comuns não são equivalentes. Marcadores homônimos disparam múltiplas vezes, logo precisam de deduplicação por ciclo. [KeyframeMarker](https://create.roblox.com/docs/reference/engine/classes/KeyframeMarker/Value).

Quando a animação é procedural e não possui AnimationTrack, o código que determina o frame de contato deve publicar o mesmo evento semântico de impacto usado por SFX/VFX; não inventar um AnimationTrack vazio para alegar integração. Documentar essa exceção. Som previsto local de swing/contato pode ser imediato; break, venda, compra e raridade precisam refletir o resultado confirmado do gameplay. Não modificar validação, saldo ou drops para facilitar áudio.

O cliente cria e controla UI/recompensas locais. Reutilizar os eventos existentes de gameplay para feedback remoto quando possível; nunca disparar um RemoteEvent por layer. Sons de outros jogadores usam menos camadas e passam pelo orçamento e culling de distância do receptor.

## Origem dos assets e limitações

Roblox permite áudio próprio/licenciado e assets gratuitos do Creator Store. Imports exigem direitos, formatos mp3/ogg/wav/flac, menos de 20 MB e 7 minutos, taxa até 48 kHz; passam por moderação e permissões. Upload concluído não prova autorização da experiência nem carregamento em cliente. [Requisitos oficiais de áudio](https://create.roblox.com/docs/audio/assets).

Usar mono para fontes físicas e estéreo controlado para música/UI é recomendação deste projeto. Manter manifesto com nome, ID, autor/origem, licença/permissão, duração e estado de carregamento. Não inferir licença a partir de um ID já presente no jogo. Este estudo não concede direitos sobre sons de referência e não extraiu nenhum arquivo deles.

## Critérios de QA

- **100 hits:** conferir distribuição, ausência de repetição imediata, pico de vozes estável e sincronia. Audição humana decide fadiga; logs não provam conforto.
- **100 pickups:** 30 no mesmo frame e sequência rápida; confirmar agregação, cadência limitada e nenhuma reprodução atrasada longa.
- **Stress:** velocidade máxima, outro minerador, break, venda, UI e música juntos; conferir prioridades e ausência de vazamentos após término.
- **Economia:** valores de várias ordens de grandeza devem mudar tier; aumento de duração/timbre sem crescimento linear de Volume.
- **Raridade:** teste cego com ordem randomizada e volumes comparáveis; Common/Rare/Epic/Legendary/Mythic/Secret reconhecíveis por desenho.
- **Espacial:** perto, limite e fora do raio, rotacionar câmera, cruzar portal rapidamente e retornar; nenhum loop abandonado.
- **Mix:** sem música, com música, volume baixo, fone e alto-falante pequeno; ausência de clipping requer medição/escuta real, não só Volume < 1.
- **Persistência:** preferências de Master/Music/SFX persistem somente se houver caminho de dados confiável; testar mute durante duck/crossfade e após respawn.

Pendências perceptuais não podem ser declaradas aprovadas por análise estática. Fontes técnicas e as propostas aqui reduzem riscos, mas a aceitação final depende da reprodução efetiva no jogo.
