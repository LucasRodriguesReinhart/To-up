# Manifesto final de áudio — V3

O catálogo atual contém **31 IDs: 24 efeitos/ambientes e 7 músicas**. Todos constam como carregados no QA final, sem falhas de preload. Este documento registra o conjunto instalado; o catálogo de candidatos contém alternativas não utilizadas.

**Não há aprovação auditiva registrada.** Carregamento e testes técnicos não comprovam timbre, fadiga, clipping perceptível ou emendas inaudíveis. Nenhuma alteração no Studio foi feita para gerar este manifesto.

## Efeitos e ambientes

Todos os 24 IDs abaixo têm autoria **ProSoundEffects** registrada em metadados do Creator Store/Marketplace. O JSON traz título individual, descrição de origem, duração declarada e runtime, trim, ganho e referência de evidência.

| Família | IDs finais | Função |
|---|---|---|
| stone | 9118598279, 9118598469, 9118598729, 9118598470, 9118598240 | Corpo dos impactos de mineração |
| metal | 9116651255, 9116652339 | Picareta, crítico, equipar e martelo da forja |
| heavy | 9118617342 | Impacto pesado/lava, forja e acento de grande recompensa |
| crack | 9118612665, 9125869797 | Rachaduras com HP baixo e quebra por raridade |
| debris | 9118690959 | Detritos após a quebra |
| swing | 9120972321, 9120972444, 9120972323 | Movimento da picareta, menus, equipamento, invocação e portais |
| click | 9119717523, 9119717529 | Interações de UI, erro e confirmação de compra/venda |
| tone | 9125531715 | Coleta, progressão, raridades, confirmação, magia e revelação |
| glass | 9114619221 | Camada física do impacto em minério de cristal |
| coin | 9125509503, 9125444889 | Ticks monetários e conjuntos de moedas na venda |
| fire | 9112780438 | Billet quente de Ignis e chaminé da forja |
| wind | 9116258071 | Fundo regional, exceto área 4 |
| water | 9112855484 | Superfícies de cachoeira com FluxoCachoeira |
| energy | 9125515917 | Portais e fundo regional da área 4 |

O tone final é **9125531715**. O antigo **9114619221** permanece como glass apenas no impacto de cristal. A coleta usa tone; moedas ficam nos ticks monetários e vendas. O erro de UI usa dois clicks graves, não a alternativa eletrônica do levantamento.

## Música preservada

| Área | Título da fonte | ID | Criador | Volume da fonte |
|---|---|---|---|---|
| 0 | Woodle Caves | 112898538778548 | DistrokidOfficial | 0.23 |
| 1 | Hidden Lotus Pond | 82061470648013 | DistrokidOfficial | 0.22 |
| 2 | Space Atmosphere | 1845421369 | APMOfficial | 0.23 |
| 3 | Mysterious Forest | 9048681794 | APMOfficial | 0.2 |
| 4 | The Forgotten Crypt (Dark Fantasy Ambient Music) | 131334832939011 | DistrokidOfficial | 0.2 |
| 5 | Pirate King | 1835322563 | APMOfficial | 0.2 |
| 6 | Home Bound | 1845676363 | APMOfficial | 0.21 |

As músicas usam dois players com transição gradual e loop integral. O produto padrão Master × Music é 0,48 antes do ducking; os volumes da tabela são multiplicados por ele.

## Trims e revisão

Os offsets e ganhos aplicados a efeitos estão no JSON. As janelas são limitadas pela duração restante do arquivo e velocidade, com release de 35 ms. Nenhum offset está fora do arquivo.

- tone: offset **0,200 s**, ganho **2,0**; fonte de **0,657833 s**. Restam **0,457833 s em 1x**, ou **0,183133 s em 2,5x**. Stings longos recebem esse limite real, mesmo quando a janela solicitada é maior.
- glass: offset **0,108 s**, ganho **2,4**; fonte de **2,730667 s**. Atua na camada física de cristal.
- Moeda **9125509503**: offset **0,344 s**, ganho **1,25**, adiantando o primeiro ataque detectado (limiar de 8% do pico). Swing recebe offsets de **0,016–0,065 s** e compensações individuais.
- O artefato de waveform salvo comprova medições anteriores de pedra/metal/glass/moeda/swing; não contém o novo tone. Para ele, offset/ganho são configuração verificada, sem nova medição nesta revisão.
- Loops usam rampas de **0,22 s** nas extremidades. Isso suaviza o corte; não equivale a comprovar uma emenda inaudível.

Não foram encontrados erros numéricos de trim. Sustain do novo tone, ganho perceptivo e emendas continuam sujeitos à audição.

## Proveniência e limites

A [documentação oficial](https://create.roblox.com/docs/audio/assets) descreve o uso de áudio do Creator Store em experiências Roblox. Os metadados PSE/APM fornecem proveniência de parceiros; a identidade DistrokidOfficial confirma o distribuidor dos três tracks, mas suas descrições estavam vazias e os termos individuais não foram capturados. Este registro não constitui garantia jurídica independente nem autorização de extração/reuso fora da plataforma.

Fontes locais: AudioCatalog.lua, SomJogo.lua, AudioWorld.lua, ASSET_CANDIDATES.json e qa/FINAL_QA_UI_SESSION.json. O JSON final inclui hashes dos arquivos usados.
