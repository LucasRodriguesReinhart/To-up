# Passe final de acabamento (craftsmanship / finesse), 2026-09-29

A ilha está **aprovada** em layout, composição macro, posição das áreas, castelo, vila, mineração dentro do castelo,
dungeon, alquimia, conexões e sistemas. Este passe **não redesenha**. O objetivo é sair de "muito bom de longe" para
"convincente e cuidadosamente modelado também de perto".

Continuam valendo as regras de `AGENT_BRIEF.md`, `REFINAMENTO_BRIEF.md` e `REFINAMENTO2_BRIEF.md`:
- planta travada;
- marcadores e rotas iguais;
- nada em rota;
- salão livre e dungeon limpa;
- orçamento;
- ciclo de teste.

## Proibido
- Mudar layout, criar áreas, construções, torres, casas ou sistemas.
- Espalhar cristais, árvores ou bandeiras novas. Menos elementos muito bons vale mais que muitos medianos.
  Se algo atual piora a composição, **remova**.
- **Modelar minérios** ou criar qualquer coisa que possa ser confundida com minério (cristal solto no chão do salão, pedra facetada com brilho).
- Esconder forma ruim com brilho, VFX, partículas, vegetação ou bandeira.
- Randomizar rotação, escala ou cor e chamar isso de refinamento. Variação tem de ser dirigida.
- Realismo, PBR ou microdetalhe fotográfico. O estilo continua Roblox + anime + cartoon estilizado. Finesse = intenção.
- Subdivisão indiscriminada. Resolva com silhueta, bevel, normais, material e topologia melhor.

## Sequência por asset
SILHUETA → PROPORÇÃO → ESTRUTURA → ENCAIXE → ESPESSURA → BEVEL → MATERIAL → DETALHE → ILUMINAÇÃO.
Se a forma base estiver ruim, refaça a forma.

## Checklists (aplicar em tudo o que o seu módulo gera)
- **Encaixe**: nada atravessando nada sem motivo; tubo → flange → parede; perna embaixo do tampo (não atravessando);
  pilar chega na base; trim não termina no ar; escada não entra no piso.
- **Flutuantes**: todo objeto toca superfície, está preso ou está suspenso de propósito (corrente, suporte).
  Magia pode flutuar; garrafa comum não.
- **Espessura**: nada com cara de papel (metal, estandarte, trim, guarda-corpo, prateleira, porta, moldura).
- **Bevel**: uma linguagem só. Peças perto do jogador têm chanfro pequeno e consistente (use o parâmetro de bevel do
  `mb.box`); nem tudo arredondado, nem tudo afiado.
- **Escala**: o avatar Roblox (boneco de escala `SCALE_Dummy_*`, cerca de 5 studs) é a régua.
  Porta de passagem com cerca de 7 a 9 de altura; mesa com cerca de 3; livro com 0,8 a 1,4; frasco com 0,6 a 2; lanterna de parede com 1,5 a 2,5.
- **Portas importantes**: moldura + espessura + soleira + ligação com a parede + ferragem quando fizer sentido.
  Nunca um retângulo escuro colado.
- **Janelas**: moldura + recuo + vidro + luz interior. A maioria em luz quente (`Window_Warm`); magia só onde tem função.
- **Símbolos, emblemas e placas**: são assets próprios (o emblema da ordem é refeito em `sg_emblem.py`; não faça versões locais).

## Materiais (paleta já ajustada em `sg_lib.py`, não edite o `sg_lib`)
Leitura clara entre PEDRA, MADEIRA, METAL, VIDRO, TECIDO e MAGIA, mesmo sem brilho.
- **Pedra**: `Stone_SG_Castle`/`Block`, com `Trim` só em remate.
- **Madeira**: `Wood_SG_Dark`, agora quente.
- **Metal**: `Metal_Gold`, `Metal_SG_Iron`/`BlackIron`, `Metal_SG_Silver`.
- **Vidro**: `Glass_SG_Rose` ou material local com prefixo `Glass_`.
- **Tecido**: `Cloth_SG_Purple`/`Navy`.

Hierarquia de brilho (Neon no Roblox):
- **DUNGEON**: alto, **mas** só de dentro para fora (exterior quase natural → entrada começando → interior forte).
- **ALQUIMIA e INVOCAÇÃO**: moderado.
- **Detalhes mágicos do CASTELO e do HALL**: baixo. Use `SG_VioletSoft_Glow` (novo, escuro) ou pedra violeta sem brilho.
- **VILA**: quase nenhum roxo mágico; só lanterna (`Lantern_Glow`), janela quente e luar.

Material novo só registrado no seu módulo (`fm_lib.MATS.setdefault`), com prefixo coerente (Neon = `SG_`, vidro = `Glass_`).

## Teste sem brilho
`SG_SEM_EMISSAO=1` antes do comando do Blender quase desliga toda emissão e as luzes. Se a sua zona fica feia assim,
a modelagem ou o material ainda estão fracos: melhore a forma, não o brilho.

## Câmeras de antes e depois (não mude)
Câmeras de close em `sg_scene.CAMS` (`CAM_SG_CU_*`); o ANTES delas já está em `renders/finesse_antes/`.
Antes de editar, renderize também as câmeras do seu módulo e guarde como ANTES. No fim, renderize as MESMAS câmeras como
DEPOIS e monte a folha com `python tools_sheet.py <antes> <depois> <saida.jpg> CAM_A,CAM_B "ANTES" "DEPOIS"`.
Uma mudança só fica se melhora o acabamento, não prejudica o gameplay, não piora o desempenho de forma relevante e não
adiciona clutter.

## Ciclo de teste
```
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "C:/Users/lucas/OneDrive/Desktop/To up/ilha_shadowgarden/studio_sg.py" -- <zona> "C:/Users/lucas/OneDrive/Desktop/To up/ilha_shadowgarden/_studio/<pasta>" --all-detail --cams CAM_A,CAM_B --res 960x540
```
Estas linhas da saída precisam ficar OK: `ROTAS`, `ROTAS_MODULOS`, `SONDAS`, `SALAO_LIVRE`, `DUNGEON_LIMPA`, o BUDGET da zona e a
linha `TECH` (0 degeneradas). Veja os JPGs com Read. Itere até não sobrar problema de acabamento perceptível de perto.

Proibido para os agentes: Roblox Studio MCP, Blender MCP ao vivo, computer-use e browser. Não faça commit.
