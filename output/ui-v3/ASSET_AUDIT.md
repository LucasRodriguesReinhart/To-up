# Auditoria de assets para UI V3

Inspeção de 17/09/2026. Fontes: arquivos locais, código canônico em `output/ui-v2/src`, snapshot `output/ui-v2/before/ReplicatedStorage/Config.lua` e uma leitura de `ReplicatedStorage.PreviewModelos.Pets` no Studio em Edit. Nenhum script ou objeto do jogo foi alterado. Nenhum Play iniciado. As resoluções abaixo são dos arquivos locais; não são uma confirmação da resolução servida pelo CDN do Roblox.

## Achado principal: Invocar amplia a imagem errada

Na [captura de Invocar](../ui-v2/screenshots/summon.png), Kakashi, Madara e Itachi aparecem como cabeças grandes, com cabelo/rosto ocupando o espaço dos nomes e controles. A perda de definição é visível nessa captura. Não há prova local de que os retratos sejam 420 ou 512 px: seus originais não foram encontrados.

O código explica o enquadramento: `Menus.lua`, na composição `BannerHero`, escolhe **`art.busto or art.corpo`**, mesmo para o protagonista. O tamanho central é `min(sw * .59, sh * 1.04)` e os laterais têm 87% desse quadrado. A origem central fica em `sh * .11 - 28`; a faixa de ações ocupa os últimos 242 px. Esse arranjo amplia um recorte de rosto e depois cobre sua base. O efeito não se resolve aumentando a resolução do fundo nem adicionando brilho.

Correção de asset/composição indicada: bustos na grade e nos pequenos seletores; corpo ou viewport de corpo inteiro no destaque. Um protagonista grande com laterais menores evita três rostos igualmente dominantes. O screenshot da referência fornecida pelo usuário tem um personagem central reconhecível de corpo inteiro; a captura atual não tem essa silhueta.

| Personagem visível na captura | Busto usado pelo Summon | Alternativa `corpo` já configurada |
|---|---|---|
| Kakashi | `101241966476297` | `72282019042075` |
| Madara | `99855140449535` | `106406917127696` |
| Itachi | `136726988718866` | `87331029272074` |
| Muzan, seleção usada no inventário | `126402076522827` | `136358139677268` |

`T.preview(..., animated=false)` também prefere busto; `animated=true` prefere corpo e ativa movimento. A escolha de corpo não precisa ativar movimento: pode ser feita explicitamente. Atualmente a função retorna a imagem antes de chegar ao fallback 3D quando `Config.PetArte[id]` existe; portanto, usar o modelo exige um modo explícito de viewport, não apenas chamar `T.preview` de novo.

## Artes novas localizadas: 21 PNGs de Downloads

Pasta: `C:/Users/lucas/Downloads`. Cada linha abaixo usa o nome completo `ChatGPT Image 15 de set. de 2026, <horário>.png`.

[Contato visual dos 21 arquivos](ASSET_CONTACT_SHEET.png) · [metadados completos, caminhos e alpha](ASSET_LOCAL_METADATA.json).

| # | Horário do arquivo | Conteúdo inspecionado | Resolução | Uso que suporta |
|---|---|---|---|---|
| 01 | 22_18_46 | fragmentos de cristal, transparente | 1254×1254 | textura em tile; não esticar como cenário |
| 02 | 22_18_55 | picareta laranja/prata, dano | 1254×1254 | ícone 24–160 px; ilustração 250–450 px |
| 03 | 22_19_01 | raio amarelo/azul | 1254×1254 | velocidade; silhueta simples e legível pequena |
| 04 | 22_19_06 | mochila marrom | 1254×1254 | capacidade; boa em 48–160 px, detalhes somem em 24 px |
| 05 | 22_19_16 | estrela amarela/roxa | 1254×1254 | sorte; ícone ou recompensa pequena |
| 06 | 22_19_21 | insígnia de nível dourada | 1254×1254 | nível; boa em 40–120 px |
| 07 | 22_19_26 | explosão de raios dourados | 1254×1254 | efeito de fundo; alpha parcial intencional, não personagem |
| 08 | 22_19_30 | brilho de quatro pontas | 1254×1254 | acento pequeno; ampliar não acrescenta detalhe |
| 09 | 22_19_36 | emblema com picareta/cristal | 1774×887 | marca 2:1; manter proporção, não encaixar em quadrado |
| 10 | 22_25_11 | minério branco | 1254×1254 | comum; prêmio/feed, não cenário |
| 11 | 22_25_15 | minério verde | 1254×1254 | incomum; prêmio/feed |
| 12 | 22_25_22 | minério azul | 1254×1254 | raro; prêmio/feed |
| 13 | 22_25_25 | minério roxo | 1254×1254 | épico; prêmio/feed |
| 14 | 22_25_31 | minério dourado | 1254×1254 | lendário; prêmio/feed |
| 15 | 22_25_36 | minério vermelho | 1254×1254 | mítico/secreto atual; prêmio/feed |
| 16 | 22_25_40 | vila com monumento na montanha | 1672×941 | painel Vila da Folha; cenário 16:9 |
| 17 | 22_25_45 | lagos e planeta verde | 1672×941 | painel Namekusei; cenário 16:9 |
| 18 | 22_25_49 | montanha/floresta à noite | 1672×941 | painel Monte Natagumo; cenário 16:9 |
| 19 | 22_25_54 | ruínas roxas | 1672×941 | painel da quarta área; cenário 16:9 |
| 20 | 22_27_22 | costa/ilhas ao pôr do sol | 1672×941 | painel Grand Line; cenário 16:9 |
| 21 | 22_27_30 | cidade densa ao pôr do sol | 1672×941 | painel Cidade Z; cenário 16:9 |

Os seis cenários têm alpha totalmente opaco. Os demais têm transparência real. O alpha parcial dos ícones não significa necessariamente imagem lavada: nos pixels não transparentes, a picareta tem alpha médio 242,7/255 e o minério branco 249,6/255; os raios têm média 121,2/255, apropriada a um efeito luminoso.

Os cenários têm pixels locais suficientes para uma área de aproximadamente 1400×790 físicos sem upscale. Em 1920 px de largura, há ampliação de 1,15×; aceitável para fundo secundário a validar, não para prometer nitidez de detalhes arquitetônicos. Evitar `Crop` extremo em painel muito quadrado: ele remove laterais, não cria composição própria. Camadas escuras podem melhorar leitura, mas os personagens devem se destacar pela silhueta e pela escala.

Os papéis acima foram identificados visualmente e correspondem aos papéis de `Theme.Assets`; não há manifesto local novo que prove, por hash, qual PNG gerou cada ID publicado. Os IDs atuais permanecem em `Theme.Assets`.

## Pasta `ui-assets` anterior: reaproveitamento seletivo

Pasta existente: `C:/Users/lucas/Documents/Codex/2026-09-12/co/outputs/ui-assets`.

[Contato visual da pasta anterior e das capturas](ASSET_LEGACY_CONTACT_SHEET.png) · [metadados completos](ASSET_LEGACY_METADATA.json).

| Arquivo | Resolução | Decisão concreta |
|---|---|---|
| `area1.jpg` … `area6.jpg` | 960×540 cada | capturas antigas do mapa. Servem para pequenas miniaturas; não usar em destaque de 1200–1600 px. O mapa foi alterado desde essas capturas, logo podem representar o ambiente antigo. |
| `lobby.jpg` | 1306×623 | captura do lobby antigo, proporção 2,10:1. Fundo secundário largo; não substituir as novas artes por isso em Invocar. |
| `icons.png` | 1254×1254, atlas 4×4 | cada célula original é ~313 px; serve para ícones pequenos. O manifesto anterior registra normalização do upload para 1024×1024 e células runtime 256×256, que explica `ImageRectSize=256` atual. Não reaproveitar uma célula como hero. |
| `header.png` + `header.svg` | 640×180, vetor disponível | faixa ornamental branca/preta com roda/arabescos. Pode ser rasterizada de novo; não tem o recorte angular da referência atual. Resolução não é o obstáculo, o estilo é. |
| `pattern.png` + `pattern.svg` | 256×256 | padrão de curvas/roda com alpha já baixo. Tile útil; visual marítimo, pouco coerente com palco de personagem. |
| `halftone.png` + `halftone.svg` | 32×32 | tile de pontos, com opacidade já embutida em ~10%. Esticar a tela inteira produz pontos enormes. Usar TileSize explícito; ImageTransparency=.94 por cima deixa a textura quase invisível. |

O manifesto anterior está em `.../co/outputs/ui-manifest.json`; os metadados vetoriais em `.../co/work/art/art-manifest.json`. Suas notas de gameplay refletem a versão antiga e não devem substituir Config/remotes atuais.

`output/hud/hud-icons-atlas.png` tem 1774×887 e fundo totalmente opaco, com 8 ícones em 4×2. Não é um atlas transparente pronto para o HUD; colá-lo sobre roxo gera retângulos escuros. Separar as células e preparar transparência seria uma etapa de arte, não um mero ajuste de `ImageRectOffset`.

As três imagens `output/ui-v2/screenshots/{inventory,summon,daily}.png` são capturas 1143×643. São evidência de QA, não material para compor a nova UI.

## Retratos de unidades: o que existe e o que ainda não foi medido

O snapshot `Config.lua` contém **32 pares completos** `busto`/`corpo`, um para cada unidade. Os 64 IDs estão em [PET_ART_MANIFEST.json](PET_ART_MANIFEST.json). Não foram encontrados PNGs desses retratos no workspace atual, na pasta `Documents/Codex` examinada ou no scratch antigo mencionado pelo histórico. Não atribuir resolução nativa aos IDs sem medir a imagem entregue pelo Roblox.

O comentário de Config documenta a intenção: busto para grade, corpo para detalhe. Ele também registra que o caminho 2D foi usado para roupas em camadas. Isso é uma razão para testar a roupa no viewport atual; não é prova de que todos os 32 modelos renderizem mal hoje.

Para a UI V3, os bustos existentes continuam adequados como candidatos a cards de 100–150 px, sujeitos à captura final. Eles não passaram no destaque atual de centenas de pixels de altura. A alternativa `corpo` melhora a proporção, mas sozinha não certifica resolução nem pose. Não chamar um upscale do mesmo retrato de “nova arte HD”.

## Alternativa 3D confirmada em Edit

`ReplicatedStorage.PreviewModelos.Pets` contém 32 Models, todos com Humanoid e Head; 17–20 BaseParts por modelo, 16–19 MeshPart/SpecialMesh e nenhum script descendente. Dezenove possuem WrapLayer. Muzan tem 18 parts, 17 meshes, 2 acessórios, 1 WrapLayer e bounds aproximados 4,54×5,86×2,39 studs.

Um viewport único para a seleção evita a ampliação de bitmap e permite enquadrar o corpo. Manter a grade em 2D evita instanciar dezenas de rigs simultaneamente. Usar clone em WorldModel, câmera isolada e limpeza ao destruir a seleção; não tocar nos seguidores ou nos modelos originais.

**Quatro modelos têm bounds globais fora da escala do corpo:**

| Modelo | Bounds X×Y×Z em studs | Risco |
|---|---|---|
| kuririn | 35,99×9,26×109,10 | `GetBoundingBox` bruto afasta demais a câmera |
| boros | 87,83×9,56×160,94 | idem |
| suiryu | 87,78×9,18×160,80 | idem |
| metal_bat | 87,50×8,58×160,60 | idem |

Os demais modelos medidos têm dimensões compatíveis com personagens de aproximadamente 4–7 studs. A origem exata das quatro extensões não foi isolada nesta leitura. Investigar acessórios/partes distantes e usar partes corporais como base de enquadramento; não reduzir indiscriminadamente a escala do modelo original. O `Theme.preview` anterior usa Head/UpperTorso/LowerTorso para enquadrar rigs, mas seu corte inferior fica próximo ao torso, não garante corpo inteiro.

Não houve renderização de viewport nem teste de deformação nesta subtarefa. O root está fazendo essa validação visual separadamente.

## Outros modelos locais aproveitáveis

- `output/pickaxes_game`: oito pares GLB/FBX (`enferrujada`, `ferro`, `aco`, `rubi`, `runica`, `obsidiana`, `estelar`, `ignis`), `picaretas_arsenal.blend` e `IMPORTAR_8_PICARETAS.fbx`. São assets reais para loja/preview; não são substitutos de retratos de unidades. Há `roblox_asset_ids.json` no mesmo diretório.
- `output/emerald_pickaxe/emerald_warden_pickaxe.{blend,glb}`: alternativa de picareta, com preview local. Não introduzir no catálogo sem o contrato de gameplay correspondente.
- `export_roblox/*.fbx` e arquivos `.blend` do lobby: geometria de ambiente. Se necessário, permitem renderizar um fundo atual do jogo; têm custo de produção e não resolvem as cabeças ampliadas em Invocar.

## Ordem recomendada para decidir os assets

1. Validar um único viewport de corpo inteiro com Muzan e um modelo sem WrapLayer. Conferir roupa, rosto e ocupação do palco antes de replicar aos demais.
2. Validar os quatro modelos com bounds anormais sem alterar os originais. Se o clone não ficar consistente, usar a arte `corpo` como fallback explícito por personagem.
3. Reusar os cenários PNG 1672×941; preservar bustos exclusivamente nos cards/seletores pequenos. Remover a composição com três bustos enormes.
4. Escolher um único sistema de ícones. O atlas transparente 4×4 e os cinco ícones de atributo separados estão prontos; o atlas opaco de HUD não está.
5. Confirmar tamanho físico e carregamento da versão publicada. O tamanho do PNG local e o sucesso de um upload não substituem essa verificação.
