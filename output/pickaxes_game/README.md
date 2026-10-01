# Picaretas do Mining Simulator

Oito modelos originais baseados nos IDs de `output/revision5/Config.lua`.

| ID / pasta | Dano base | Triangulos |
| --- | ---: | ---: |
| enferrujada | 2 | 1.580 |
| ferro | 8 | 1.428 |
| aco | 34 | 1.944 |
| rubi | 150 | 2.240 |
| obsidiana | 700 | 2.336 |
| runica | 3.400 | 3.756 |
| estelar | 17.000 | 2.724 |
| ignis | 90.000 | 3.400 |

## Arquivos

- `picaretas_arsenal.blend`: colecao editavel com os oito modelos e estudio de apresentacao. As colecoes antigas do teste estao ocultas.
- `arsenal_preview.png`: comparativo dos oito niveis.
- Cada pasta contem um FBX e um GLB do modelo, isolado e sem camera, luzes ou rotulos.
- `manifest.json`: materiais, contagens, IDs e UVs.
- `validation.json`: resultado da reimportacao dos FBX no Blender.

## Preparacao para o jogo

Os modelos possuem UVs geradas e cores definidas por material; nao incluem atlas de texturas pintadas. Sao 5 ou 6 malhas por modelo, agrupadas por material. Modificadores estao aplicados. O pivô fica no centro da empunhadura; a altura varia aproximadamente entre 3 e 4 unidades. As exportacoes nao incluem a inclinacao e o espacamento da vitrine.

Use o FBX para a etapa de importacao no Roblox Studio. Confira escala, cores, orientacao e encaixe na mao antes de substituir a ferramenta atual. O emissivo da previa deve ser configurado no Roblox para as pecas de cristal/energia; a aparencia de Blender nao e uma garantia do resultado do importador.

Para montar a Tool, as partes visuais devem acompanhar um Handle com soldas e ficar sem colisao e sem massa. Os arquivos usam os mesmos IDs do Config para facilitar o mapeamento. Os atributos de dano no Blender sao metadados; a fonte de dano do jogo continua sendo o Config.

Esta entrega cria os assets; nao substitui scripts, nao publica meshes e nao altera a loja no Roblox. Integracao e teste de animacao no Studio ainda nao foram realizados.
