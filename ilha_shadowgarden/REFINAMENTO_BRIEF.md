# Refinamento visual de alto nível (pedido do usuário, 2026-09-28)

Leia junto com o `AGENT_BRIEF.md`. As regras de lá continuam valendo: planta travada, colisão, rotas, zona de minério livre, orçamento, ciclo de teste e proibições.

## O que o usuário disse (verbatim, resumido)

**O que mais incomoda:**
- a lua/símbolo na frente do castelo quase não aparece;
- roxo e preto, que remetem ao Cid/Shadow, estão fracos;
- o exterior do castelo está morto e sem vida visual;
- a entrada da dungeon está sem impacto e parece genérica;
- muitos elementos parecem simplificados demais;
- no geral, parece mais uma maquete de Hogwarts do que uma ilha de Shadow Garden.

**O que ele quer:** NÃO é um redesign. É um refinamento profundo da versão existente, que tem que ficar:
- premium, sombria, elegante e temática;
- viva e rica visualmente;
- menos infantil, menos genérica, menos homogênea;
- sem cara de IA;
- sem ser Hogwarts genérico nem castelo medieval genérico.

Tem que continuar construível no Roblox: nada de realismo, nada pesado demais, sem poluir.

## Diagnóstico (da integração)

- **Castelo:** tudo no mesmo cinza-azulado, com telhado, torre e parede no mesmo valor. Sem separação base/corpo/coroamento. O símbolo da fachada é pequeno, alto e borrado.
- **Símbolos soltos:** tridente nos estandartes, estrela no frontão, lua na fonte. Nenhum vira marca, e ornamento sem sistema é cara de IA.
- **Cores da ordem:** roxo e preto quase inexistentes. O "escuro" era azul-acinzentado.
- **Dungeon:** portaria quadrada comum, com arco comum e óculo quente. O portal fica escondido dentro dela e não há sinal de desafio.
- **Exterior:** pátio e eixo são lajes lisas. Faltam jardins, estátuas, obeliscos, variação de piso e transições.
- **Hall:** piso cinza com linhas brancas, foco fraco, sem roxo e sem trono nem símbolo central.

## SISTEMA DE IDENTIDADE (obrigatório usar)

### 1. Um único símbolo da ordem
Use `sg_emblem.py` (compartilhado e congelado):
- `emblem(...)`: lua em eclipse (crescente violeta coberta por disco negro) + lâmina de prata + anel de prata. Com `monumental=True` ganha raios.
- `banner(...)`: estandarte da ordem em roxo profundo, com barra negra, bordas de prata, emblema e ponta em V.
- `plaque(...)`: medalhão de obsidiana com o emblema.

**Proibido criar outro símbolo:** nada de tridente, estrela de 8 pontas avulsa ou lua avulsa. Onde já existir, TROQUE pelo emblema.

### 2. Paleta com FUNÇÃO (sg_lib.SMATS)

| Função | Materiais |
|---|---|
| Base / socos / faixas / cantaria nobre | `Stone_SG_Obsidian` (quase preto) |
| Corpo das paredes | `Stone_SG_Castle` / `Stone_SG_Block` (pedra fria) |
| Molduras nobres, emblemas, alternância de fiadas | `Stone_SG_Violet` (pedra violeta) |
| Pisos nobres | `Stone_SG_MarbleBlack` (mármore negro), com incrustação `Stone_SG_Trim` / `Metal_SG_Silver` |
| Telhados | `Roof_SG_Navy` (agora preto-violeta) no castelo; `Roof_SG_Slate` (quase preto) na vila |
| Remates | `Metal_SG_Silver` (prata) |
| Grades, postes, correntes | `Metal_SG_BlackIron` (ferro negro) |
| Tecido da ordem | `Cloth_SG_Purple` (roxo profundo) |
| Energia (Neon), só em LINHAS e FOCOS | `SG_VioletDeep_Glow` (linhas, frisos de energia, janelas da torre-coroa)<br>`SG_Rune_Glow` (runas, miolo do emblema)<br>`SG_Violet_Glow` (portal, vórtice) |
| Vida humana | janelas quentes `Window_Warm` e lanternas `Lantern_Glow` (contraste com o violeta) |

Não use só cinza. Separe visualmente castelo / pátio / edifícios secundários / terreno / caminhos / entrada / dungeon / áreas mágicas.

### 3. Anti-IA
- Cada detalhe obedece ao sistema: símbolo único, material com função, repetição com RITMO (a cada vão, a cada torre), não aleatória.
- Menos objetos, mais bem desenhados. Nada solto flutuando, nada de enfeite para preencher.

## Orçamento do refinamento

A ilha inteira tem teto de 480k tris, 700 MeshParts e 42 luzes. Hoje está em 327k / 471 / 37.

| zona | tris | MeshParts | mat. novos | colisões | luzes |
|---|---|---|---|---|---|
| castle | 120k | 150 | 6 | 160 | 5 |
| dungeon | 60k | 75 | 5 | 140 | 7 |
| hall | 40k | 50 | 4 | 40 | 6 |
| dressing (veg + props + lights + court) | 70k | 120 | 6 | 150 | 7 |

Prefira brilho Neon a luz nova: cada luz a mais sai de um teto quase cheio.
