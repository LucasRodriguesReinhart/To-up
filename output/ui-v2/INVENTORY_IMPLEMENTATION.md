# Inventário V2 — implementação entregue para integração

Arquivo: `src/ReplicatedStorage/ExpeditionUI/Inventory.lua`. Base: snapshot LIVE `before/.../Inventory.lua`.

## Mudança estrutural

- Substitui grade + palco gigante + ficha por grade pesquisável e ficha contida. O shell e as abas Unidade/Hats continuam sob controle do ExpeditionClient.
- Busca normaliza acentos, nome original, apelido, ID e raridade. Ordenação selecionável: recomendados, dano, raridade, nível e nome. Filtro de raridade, estado (todos/equipados/favoritos/protegidos) e escopo (meus itens/coleção).
- Cards com retrato estático, nome, raridade escrita, nível, dano, equipado/selecionado e marcadores de favorito/proteção. Nenhum loop animado por card.
- Ficha com um preview destacado, XP, atributos, comparação com equipado de menor dano, favorito/proteção, renomear, quantidade de cópias e CTAs fixos. Detalhes internos rolam sem esconder as ações.
- Abaixo de 620 unidades de largura do canvas, grade e ficha viram etapas com Voltar. Na largura mobile virtual esperada de ~760, duas colunas continuam úteis.
- Empty states distinguem inventário vazio de busca sem resultados e oferecem a ação correspondente.

## Consumo seguro e escopo

- Favoritos e protegidos usam somente `ctx.favorites`/`ctx.locks`, identificados por `kind:UID`. O texto declara explicitamente que valem **nesta sessão**. Não existe alegação de persistência no save.
- Equipados, alvo, favoritos e protegidos não aparecem como alimento/material de fusão; atalhos também usam essa lista filtrada.
- Seleção → revisão explícita dos itens consumidos → confirmação. Voltar à seleção mantém o conjunto; cancelar popup não envia remote.
- A ordem de consumo é estável (raridade/XP/UID), e a seleção excedente depois de atingir nível máximo é removida da revisão. Proteção local é revalidada imediatamente antes da chamada.
- Remotes e argumentos permanecem: EquiparHat/EquiparPet, EquiparMelhores/EquiparMelhoresPets, DesequiparTodos/DesequiparPets, AlimentarPet(alvoUID,listaUID), FundirHat(alvoUID,listaUID), RenomearPet(UID,texto).
- Dados persistentes, economia e servidores não foram modificados pelo subagente.

## Revisão e teste

Revisão estática concluída: chamadas e identidade UID, candidatos protegidos, compatibilidade com Theme API, comportamento de máximo nível, retorno de errors, layouts sem painel externo maior que área disponível, remoção de `fx = nil` sem função. A compilação Studio de uma revisão anterior foi confirmada pelo agente principal; compilação final e QA Play devem ser executados no conjunto integrado (Theme novo é necessário).

Casos prioritários no Play:

1. Abrir H/J, alternar coleção, limpar pesquisa/filtro; scroll mantém posição apropriada.
2. Digitar pesquisa devagar/rápido, com acentos, e sair do TextBox; foco deve continuar na busca durante atualização e não voltar quando já saiu.
3. Todos 5 sorts e 4 estados; favorito/protegido deve aparecer no filtro e no detalhe; ambos não podem surgir na seleção de consumo.
4. Equipar/unequip/melhores/limpar com slots cheios; ação principal não deve consumir; rename continua filtrado pelo servidor.
5. Alimentar/fundir com lista vazia, 1 item, multiseleção, comuns, proteção, voltar/revisar/cancelar, erro de servidor e teto de nível.
6. Testar desktop 1366×768/1920×1080/2560×1440 e mobile portrait/landscape; dropdown deve sobrepor grade sem clipping.
7. Preview da ficha deve manter rosto/corpo legível; os retratos mapeados usam Config.PetArte e hats usam thumbnails existentes.

Limites deliberados: favoritos/proteção não persistem entre sessões; a proteção é aplicada pela interface e não cria uma nova regra de servidor. “Coleção completa” mostra catálogo atual, enquanto Index mantém histórico de obtenção. Não foi adicionado trading, remoção arbitrária de itens ou saved loadouts.
