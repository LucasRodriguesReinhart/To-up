# Overhaul de acabamento, "zero tolerância" (2026-09-29)

Continuam valendo `AGENT_BRIEF.md`, `REFINAMENTO*_BRIEF.md` e `ACABAMENTO_BRIEF.md`: planta, marcadores, rotas, salão
livre, dungeon limpa, orçamentos e ciclo de teste. A lista real de problemas está em **`AUDITORIA2.md`** (162 itens, 67 críticos),
por setor e com a função de origem. Corrija os itens do SEU setor e procure os que a auditoria não viu.

## Critério
A pergunta não é "melhorou?", é **"está realmente bom de perto?"**. Avalie a imagem DEPOIS isolada.

Não final = qualquer coisa que ainda pareça:
- primitiva óbvia (cubo, cilindro, esfera, cone) ou primitivas empilhadas;
- bloco colorido ou detalhe colado;
- forma inflável ou "salsicha";
- massa sem estrutura ou placeholder com brilho;
- procedural sem direção ou ornamento sem encaixe;
- peça atravessando outra;
- flutuante acidental, espessura de papel ou escala errada ao lado do avatar de cerca de 5 studs.

Níveis de acabamento:
- **Tier A** (hero): sobrevive a close-up direto;
- **Tier B**: sobrevive à câmera normal do jogador;
- **Tier C** (fundo): só silhueta e massas.

Não gaste geometria de hero em fundo.

## Realidade do Roblox (o jogador vê ISTO, não a prévia texturizada do Blender)
- **Sem textura no jogo:** o ruído e a textura procedural das pedras NÃO aparecem, e a forma tem de ler sozinha.
  Valide com **`FM_MAT_PREVIEW=roblox`**: as cores que o Roblox recebe, sem ruído nem textura, com o Neon brilhando.
  Rode assim: `FM_MAT_PREVIEW=roblox "<blender>" -b --factory-startup --python studio_sg.py -- <zona> <saida> --all-detail --cams ...`.
- **Vidro:** vira Glass com transparência 0,3 (os frascos da alquimia, 0,55). Nenhum objeto importante pode depender de transparência para ler.
  O conteúdo tem de ler pela forma (gargalo, ombro, aro, cinta) e pela cor do líquido.
- **Neon claro vira branco com o bloom.** Use Neon médio ou escuro e só onde a magia tem função. Luz quente (`Lantern_Glow` e
  `Window_Warm`) só DENTRO de moldura: nunca um bloco inteiro de Neon.
- **Bevel:** o `mb.box(..., bevel)` é a sua ferramenta. Use uma linguagem só: peças perto do jogador com chanfro pequeno e consistente.
- **Normais:** o export sai com face plana. Superfícies curvas precisam de segmentos suficientes (sem exagero), senão facetam.

## Regras
- NÃO mude layout, gameplay nem sistemas. NÃO crie áreas nem conteúdo "para encher". NÃO modele minérios.
- Se algo piora a composição, REMOVA. Menos e melhor.
- Variação é DIRIGIDA: nada de rotação, escala ou cor aleatórias chamadas de refinamento.
- Desempenho: melhore por silhueta, bevel, proporção, material, encaixe e reuso, não por polycount.
  Respeite `studio_sg.BUDGET`; o total da ilha fica ≤ 560k tris e ≤ 800 MeshParts.
- Faça os passes de interseção, flutuantes e escala em tudo o que o seu setor gera.

## Antes e depois
- Antes de editar, renderize as câmeras do seu setor (as da auditoria em `renders/auditoria2_antes/` já servem de ANTES; acrescente
  as suas, se precisar), em `renders/overhaul/<setor>/antes`.
- No fim, faça as MESMAS câmeras em `renders/overhaul/<setor>/depois`, nos dois modos: prévia normal e `FM_MAT_PREVIEW=roblox`.
- Monte a folha com `tools_sheet.py`.
- Use ângulos naturais de gameplay, não só o melhor ângulo.

## Ciclo de teste
Ver `ACABAMENTO_BRIEF.md`. `ROTAS`, `ROTAS_MODULOS`, `SONDAS`, `SALAO_LIVRE`, `DUNGEON_LIMPA`, BUDGET e `STUDIO tecnico` (0 degeneradas)
precisam ficar OK. Proibido para agentes: Roblox Studio MCP, Blender MCP ao vivo, computer-use, browser. Não faça commit.
