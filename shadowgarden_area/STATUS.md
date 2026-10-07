# Shadow Garden — estado da entrega

Atualizado em 17/09/2026. A modelagem e a prévia estão produzidas; a substituição definitiva da Área 4 ainda NÃO foi concluída.

## Produzido

- Pesquisa e direção artística em `DESIGN.md`, seguidas por blockout de entrada e visão geral.
- `shadowgarden_area.blend`: ilha, kit modular, materiais e collections organizados.
- `export/shadowgarden_kit.fbx`: 61 módulos com marcador `__origem`, atlas único `SG_Palette.png` e hierarquia `K_*`.
- 202 instâncias visuais, 193 volumes simples de colisão, 44.385 triângulos únicos e aproximadamente 105.751 triângulos colocados, antes de minérios/VFX. Maior módulo: 3.572 triângulos. Isso é orçamento geométrico, não medição de FPS.
- Pedreira extensa no centro, sem objetos decorativos no piso; quatro rampas; cidadela sobre a mina; cripta, ruínas, bairro nobre, arco de basalto, lago e ponte.
- Árvores com troncos e ramos, copas irregulares; arbusto próprio de 204 triângulos. A revisão dos arbustos reduziu 48.400 triângulos colocados.
- Água com margens curvas, ondulações e lâminas de queda curvas; Beams, espuma e névoa usam texturas internas do Roblox.
- Cinco formações de minério e integração preparada para as variantes existentes. A paleta das novas malhas é preservada por `ShadowGardenPalette`.

## Estado atual no Studio

- PlaceId: 101959830085647; proprietário: grupo LSation.
- A Área 4 original continua ativa.
- `Workspace.ShadowGarden_Review`: prévia separada em (0,106,5000), marcada `PreviewOnly`.
- `ServerStorage.ShadowGardenPreviewKit`: 61 modelos com geometria real do Blender transportada por EditableMesh. O conteúdo desta prévia é temporário da sessão; NÃO substitui a importação estática.
- `ServerStorage.BeforeShadowGarden_20260917`: backup verificado da área anterior.
- `Core.ShadowGardenIsland`, `Core.ShadowGardenLayout` e `StarterPlayerScripts.ShadowGardenWater` estão preparados. `IslandWorld` só seleciona o novo mapa quando `ServerStorage.ShadowGardenKit` existir.
- Ajustes de `AreaBuilder` permitem variantes próprias de sombra e preservam o atlas apenas dos novos modelos marcados. Nenhuma alteração de preço, HP ou recompensa foi solicitada/aplicada.
- O mapa não foi salvo nem publicado.

## Verificações realizadas

- Renders do blockout e modelos finais, revisão da entrada, vila, lago e pedreira. `renders/studio_quarry_preview.jpg` mostra a prévia com o perfil noturno existente da Área 4.
- Teste em Play numa área de QA separada: 70 minérios gerados, 94 pontos disponíveis após as correções de acesso. Esse teste de spawn utilizou os modelos de minério que já estavam no jogo.
- Personagem R15 de teste percorreu entrada, quatro rampas da pedreira, acesso e patamar do castelo, ponte e mina. Todos os nove percursos passaram após corrigir a interseção da rampa com o patamar.
- Os novos minérios aparecem na prévia visual (61 pontos autorados), sem interferir na economia ou nos minérios da Área 4 original.
- Scripts temporários de QA foram removidos; iluminação global de edição restaurada.
- Layout local e manifesto de exportação equivalentes, incluindo rampa/patamar corrigidos.
- Após o ajuste da paleta, uma nova inicialização em Play confirmou seis áreas/420 rochas e 70 hitboxes de minério de sombra na Área 4 original, sem erros no console. Play foi encerrado.

## Impedimento e verificações restantes

O importador 3D abriu, mas a automação nativa não consegue preencher o seletor de arquivos. Captura nativa: `SetIsBorderRequired` indisponível; clique: `coordinate input geometry is unavailable`; edição UIA: propriedade ausente no CacheRequest (0x80070057). Não há `ShadowGardenKit` estático instalado.

1. Importar `export/shadowgarden_kit.fbx` pelo Studio, com criador LSation, preservando hierarquia, pivôs, atlas e marcadores `__origem`.
2. Inspecionar escala e hierarquia reais importadas; executar `finalize_import.lua`. Esse script exige 61 modelos e IDs de malhas publicados antes de ativar o kit.
3. Validar a Área 4 real em Play: entrada/retorno, anti-snapback, portal para Área 5, colisões, spawn, mineração/recompensas/respawn e raridades novas.
4. Verificar acesso às texturas do grupo, replicação e aparência no cliente, água animada, partículas e desempenho em dispositivos modestos.
5. Só depois remover a prévia/kit temporários e oferecer a revisão final para salvar o lugar. Não declarar a instalação concluída apenas porque o FBX foi importado.

Não foi possível comparar diretamente com a imagem de água antiga: ela não estava acessível neste contexto.

## Tentativa de integração sem intervenção local

Após o usuário informar que estava fora de casa, foi implementado um protótipo alternativo em `ShadowGardenMeshRuntime.lua`: guardar os vértices/triângulos do Blender no projeto e gerar MeshParts com `CreateDataModelContentAsync` uma vez por servidor. Os vértices são recentrados para manter os limites físicos e pivôs corretos. A geometria original continua no FBX e nos JSONs.

O teste isolado em Play falhou por restrição da própria experiência: `EditableMesh is not accessible. Go to the Security Tab in Experience Settings to enable this API.` No Creator Dashboard da experiência 10765150093, a opção `Enable Mesh / Image APIs` estava desmarcada e desabilitada, acompanhada de exigência de verificação de identidade. Nenhuma configuração de segurança, identidade, credencial ou termos foi alterada.

O painel web de Models & Packages não ofereceu upload de novos modelos. A recuperação da automação nativa permitiu fechar e reabrir o importador, mas a entrada no seletor de arquivos continuou falhando; a captura voltou a retornar `SetIsBorderRequired ... 0x80004002`. O seletor foi fechado. A CLI pública do Studio não documenta importação direta de FBX.

Play foi encerrado e os módulos/dados/scripts experimentais foram removidos do Studio. O protótipo permanece somente em arquivos locais para eventual uso futuro. A Área 4 original permanece ativa; não houve instalação definitiva, salvamento ou publicação do lugar.
