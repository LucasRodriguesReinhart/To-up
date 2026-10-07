# Auditoria de tipografia e componentes — UI V3

Estado: implementação local em integração, ainda sem aprovação visual ou validação em Play. Base: fresh export em `ui-v3/before`; implementação canônica em `ui-v3/src`. A UI V2 foi rejeitada e não é a direção final.

## Causas verificadas da leitura fraca

| Causa no Theme/Client anterior | Efeito | Tratamento V3 |
|---|---|---|
| `fitText` reduzia toda linha para caber, com mínimo 10 | Rótulos de ações e nomes longos perdiam hierarquia | Removido. `T.text` preserva tamanho nominal e usa reticências |
| `Paragraph` e texto com quebra acionavam `TextScaled` | Descrições encolhiam para o retângulo disponível | `T.para` mantém tamanho, permite quebra e pede altura suficiente ao layout |
| Medição usava apenas `Size.Offset`; campos com largura por Scale podiam cair no autoscale | Decisões de tamanho desconectadas da largura efetiva | Removida essa medição global; `TextOverflow` expõe `TextFits` para inspeção |
| Canvas 1440×850 com escala pela menor dimensão | 14 nominais viravam 11,69px a escala 0,835; 10 viravam 8,35px | Root definiu piso 1, com reflow real dos componentes e crescimento só em telas maiores |
| Chips medidos com Builder, desenhados com Fredoka e compensação inversa da escala | Largura calculada não correspondia ao rótulo | Medição e desenho usam GothamBlack/Heavy no mesmo tamanho |
| Texto pequeno com contorno grosso e botão cheio de brilho | Interiores das letras menores, controles pesados e pouco semelhantes às refs | Contorno seletivo mais leve; botões sem Lip nem Gloss |

Não basta um teste retornar zero transbordamentos: autoscale pode fazer tudo caber com letras ilegíveis. A documentação do [TextLabel](https://create.roblox.com/docs/reference/engine/classes/TextLabel/Text) também recomenda evitar `TextScaled` quando a consistência do tamanho é necessária. Para métricas com `FontFace` fora dos enums usados aqui, preferir [GetTextBoundsAsync](https://create.roblox.com/docs/reference/engine/classes/TextService/GetTextBoundsAsync), com cache; não medir a cada frame.

## Contrato implementado no Theme

- **Texto:** `TextScaled=false`; mínimo 14 geral, 12 somente papéis explícitos `caption`/`footer`. Títulos e botões FredokaOne; labels Gotham Heavy; corpo Builder Bold. `T.Type` estabelece corpo 16, label 16, botão 22, título 26 e display 32. Uma linha trunca; parágrafo quebra, sem reduzir a fonte. O layout deve reservar altura para o conteúdo relevante.
- **Botão:** face quase plana, raio 7, borda preta 2,5, aro interno 1,5, gradiente vertical com base 10% mais escura e duas facetas brancas de 7% de opacidade. Tamanho padrão 22, mínimo 18 para override explícito. Foco clareia aro e face sem aumentar o controle por padrão. Estados e áudio continuam centralizados.
- **Abas:** texto 22, fundo transparente, wash 15% na selecionada e linha inferior 3px. Quantidade e largura total pertencem ao Client. Não usar duas abas ocupando uma barra gigantesca sem necessidade.
- **Superfícies:** preto e slate quase neutros, violeta reservado à arte, raridade e superfícies específicas. Branco de leitura; sombra passa a ser uma borda sólida com deslocamento máximo 6px.
- **Campos/chips:** busca em Builder 20, mínimo 14; chip Gotham com medida correspondente. Bordas, nomes e contratos de retorno mantidos.

Preservados `Face.Caption`, `ToneColor`, `Disabled`, `Fill/Tint`, assinaturas públicas e interações. Nenhuma API pública removida. `T.preview` e o restante do módulo a partir dele estavam byte-equivalentes ao fresh export no encerramento desta edição; a inserção de `T.characterViewport` pertence ao Root.

## Composição derivada das três referências

A semelhança depende da proporção da arte, não apenas da fonte. Na referência do inventário, grid ocupa aproximadamente 27% da largura, personagem central cerca de 50%, detalhe e ações o restante; são estimativas visuais, não especificação exata. Na V2, grid 38% e detalhe 28% espremiam o personagem em cerca de 34%. Root controla essa recomposição e a arte 3D.

Summon deve ter personagens grandes integrados ao banner, placa de título com facetas e CTAs verdes legíveis. Daily combina estrutura preta e laranja, arte de recompensa dominante e estados fortes de recebido/disponível. Não espalhar sete cores por cada estatística nem aplicar o mesmo grande painel a todas as telas.

## Pendências e critérios de validação

1. Confirmar piso de escala 1 no Client; manter leitura 14/16/22 em pixels físicos, usando colunas, paginação, rolagem e alturas responsivas. Não recuperar espaço reduzindo todas as letras.
2. Conferir nomes longos, português acentuado, valores grandes, gamepad e touch. Rótulos de ações essenciais não podem terminar apenas em reticências. Botões de toque precisam pelo menos 44px físicos; 52 nominais dão margem no layout.
3. Rever overrides externos: `Notify.Name` ainda liga autoscale 16–27 e `IslandTransition.Title` 18–38 no snapshot auditado. Billboards, dano no mundo e glyph de badge têm contexto próprio e não foram alterados neste escopo.
4. Comparar capturas sem redimensionamento da imagem, em desktop, portrait e landscape baixo. Validar cortes e rolagem com texto fixo; o registro `TextOverflow` é diagnóstico, não aprovação visual.
5. Root compila, testa em Play e valida os fluxos/arte. Esta auditoria fez inspeção estática e comparação de contratos; não prova persistência no Studio, legibilidade final ou equivalência visual às referências.
