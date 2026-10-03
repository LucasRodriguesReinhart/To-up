# AMS — Redesign da loja de Equipamentos

Protótipo navegável em HTML/CSS/JS puro da tela **Equipamentos** (Picaretas / Mochilas) do Anime Mining Simulator.
Abra `index.html` direto no navegador. Sem frameworks, sem build.

---

## PARTE 1 — Diagnóstico da tela atual

Leitura da captura em 1920×1080, como revisão de direção de UI antes de lançamento.

### Composição
- **Cards de 1600×165 px para três linhas de texto.** Cerca de 70 % de cada card é superfície preta vazia entre o nome (x≈280–540) e o status (x≈1500). A largura não transmite luxo, transmite falta de conteúdo.
- **Só 3 de 12 itens cabem na tela.** A progressão da categoria exige 4 telas de scroll. O jogador nunca vê a escada inteira (onde está, o que falta).
- **O banner "Categoria concluída" ocupa 215 px de altura** para dizer quatro vezes a mesma coisa: "Categoria concluída", "Atual: Mochila Ciborgue", "Você possui a melhor opção", "✓ COMPLETO". O item em si aparece num ícone de 110 px, sem tratamento de recompensa.
- **Painel de 1680 px cobre a coluna de HUD esquerda** (Loja / Itens / Missões ficam parcialmente escondidos).
- Ritmo vertical arbitrário: banner 215 → gap 20 → cabeçalho de seção 40 → cards 165 + 15. Nada é múltiplo de uma base.

### Hierarquia (o que o olho vê primeiro)
1. Placa laranja "Equipamentos" (chrome, não conteúdo).
2. Tab amarela "Mochilas" (chrome).
3. Banner teal com listras (status, não produto).
4. Só depois os itens, que são a parte mais escura e menos contrastada da tela.

O elemento mais importante de um simulator — **o próximo upgrade** — não é destacado em nenhum lugar. Não há comparação com o item atual, nem noção de "quanto melhora".

### Problemas específicos
- **Mesmo ícone para as 12 mochilas.** Nenhuma sensação de coleção, recompensa ou progressão visual.
- **"Adquirida" + "✓ ADQUIRIDA"** repetidos lado a lado, três vezes por tela. O segundo tem forma de botão mas não é ação: affordance morta ocupando 235×45 px.
- **Números tratados como frase**: "39 de capacidade" com o 39 no mesmo peso do resto. O atributo principal não é escaneável.
- **Seis matizes de acento competindo** sem sistema: laranja (placa), amarelo (tab), vermelho (fechar), teal (banner), verde (completo), ciano (linha da seção).
- **Borda laranja de 3 px do painel** é a linha mais saturada da tela e compete com o conteúdo.
- **Interface plana**: cards com fundo #111 e borda de 1 px, sem material, sem profundidade, sem luz. Botão de estado com borda fina e fundo transparente.
- **Tabs parecem dois botões soltos**, não um controle de navegação encaixado no painel.
- **Sem raridade / tier visual**: "Nível 1 · Vila da Folha" é a única diferenciação, no mesmo peso que a capacidade.
- **"12 opções"** no canto é informação inútil para a decisão; "qual é o próximo e quanto custa" é a informação que falta.
- Listras diagonais do banner são decorativas, não se repetem em nenhum outro lugar do sistema.

Resumo: a tela comunica *tabela de inventário administrativa*, não *loja de equipamentos de um anime simulator*.

---

## PARTE 2 — Princípios do redesign

1. **O item é o herói.** Cada equipamento tem arte própria, palco com luz e um showcase grande quando selecionado.
2. **Progressão legível em 1 segundo.** Os 12 itens cabem na tela, em ordem de nível; a escada de segmentos no cabeçalho mostra adquiridos / equipado / próximo / bloqueados.
3. **Um único CTA por tela.** "Adquirido" e "Equipado" são *estados* (selo, texto, borda), nunca botões gigantes. O botão grande só existe quando há ação real: Comprar ou Equipar.
4. **Números, não frases.** `1.600` grande, `cap.` pequeno; delta `+850` e `+113 %` em chip. Uma linha de utilidade só quando ajuda a entender o atributo.
5. **Próximo upgrade auto-selecionado ao abrir.** É o produto mais importante da tela; o jogador não precisa procurá-lo.
6. **Comparação explícita**: Atual → Este item → Delta. Downgrade também é mostrado honestamente (chip cinza, sinal negativo).
7. **Um acento por papel.** Dourado = valor e ação de compra; ciano = seleção e equipar; verde = possuído / equipado; vermelho = bloqueio / falta. A cor de categoria (ember para picaretas, teal para mochilas) marca só ícones, labels e indicador de tab. O chrome fica dessaturado para o cenário e as artes serem mais coloridos que o painel.
8. **Luz consistente** vinda da esquerda-cima: highlight de 1 px no topo das superfícies, aresta escura embaixo, sombras curtas para baixo.
9. **Raridade = riqueza visual.** Comum/incomum neutros; épico ganha tint; lendário e mítico ganham moldura colorida e um brilho que passa a cada 5–7 s. Sem quebrar a consistência.
10. **Tudo implementável no Roblox** com Frame + UICorner + UIStroke + UIGradient + UIPadding + UIGridLayout + ImageLabel. Blur = BlurEffect no Lighting; noise = ImageLabel tile.

---

## PARTE 3 — Arquiteturas estudadas

| | A · Lista refinada | B · Grid + Showcase | C · Trilho de progressão (RPG) |
|---|---|---|---|
| Estrutura | Linhas compactas de 80 px, CTA inline, chips de status | Grid 4×3 à esquerda, vitrine fixa à direita com arte grande, comparação e um CTA | Carrossel horizontal por nível embaixo, vitrine grande em cima |
| Legibilidade | Boa para texto, fraca para arte | Alta: arte grande + números grandes separados do grid | Média: nomes espremidos no trilho |
| Rapidez | Alta (tudo em uma coluna) | Alta: próximo já selecionado; 1 clique para trocar | Scroll horizontal obrigatório a partir de ~8 itens |
| Sensação premium | Baixa: continua "lista" | Alta: vitrine de coleção | Alta, mas custa área |
| Mostrar arte | Pequena | Grande no showcase + média no tile | Grande só no selecionado |
| Progressão | Linear, mas exige scroll | Grid ordenado + escada + flag "Próximo" | Metáfora forte, porém escala mal |
| Roblox | ScrollingFrame + UIListLayout | ScrollingFrame + UIGridLayout + Frame fixo | ScrollingFrame horizontal + lógica de centralização |
| Escalabilidade (20+ itens) | Boa | Boa (grid rola, showcase fixo) | Ruim |

---

## PARTE 4 — Direção escolhida: **B, Grid + Showcase**

Por quê, na ordem dos critérios de decisão:
- **Experiência**: ao abrir, o jogador vê os 12 itens, qual está equipado, qual é o próximo, e o próximo já está na vitrine com preço e botão. Zero scroll para a decisão principal.
- **Clareza**: separa "escolher" (grid) de "decidir" (showcase). Um CTA só.
- **Hierarquia**: a vitrine com arte de 240 px e número de 44 px domina; o grid é secundário mas completo.
- **Progressão**: ordem de nível + índice 01–12 + escada de segmentos + chips de delta nos tiles.
- **Estética e game feel**: tiles com palco, flag pregada "PRÓXIMO", botão físico com aresta.
- **Roblox**: é a arquitetura mais direta de reproduzir (um UIGridLayout e um Frame fixo).

Dimensões em 1920×1080: painel 1560×900 (deixa o HUD esquerdo visível), cabeçalho 76 px, grid 4×3 com tiles de ~230×228 px, showcase de 520 px.

---

## PARTE 5 — Design System

### Escala
`1rem = 16px` em 1920. A raiz usa `clamp(12px, 0.8333vw, 16px)`: toda a UI escala proporcionalmente (equivalente ao UIScale do Roblox). Em 1366×768 o painel vira 1170×675 sem reflow.

### Cor (tokens em `styles.css`)
| Grupo | Tokens | Por que existe |
|---|---|---|
| Base | `--bg-deep` `--bg-panel` `--surface-01/02/03` `--surface-hover` | Quatro degraus de luminância em grafite azulado; a profundidade vem do contraste de luminância, não de matiz. |
| Linhas | `--border-soft` `--border-strong` `--edge-light` `--edge-dark` | Highlight superior e aresta inferior consistentes com a luz da esquerda-cima. |
| Acentos | `--accent-primary` (ciano) `--accent-gold` `--accent-secondary` (azul-aço) | Ciano = energia/seleção/equipar. Dourado = valor, compra, próximo upgrade. Azul-aço para ícones neutros. |
| Estados | `--success` `--warning` `--danger` | Verde = adquirido/equipado; vermelho = bloqueado/falta de moedas. |
| Texto | `--text-primary/secondary/muted` | Três níveis, contraste mínimo 4.5:1 no primário e secundário. |
| Raridade | `--rarity-common … mythic` | Aço → verde → azul → roxo → âmbar → rosa-carmim. Usado em tint do palco, pill e moldura. |
| Categoria | `--cat-accent` | Ember `#ff8a4a` (picaretas: impacto) / Teal `#3fd1c3` (mochilas: armazenamento). Muda com `body[data-cat]`. |

### Tipografia
Fredoka (display) + Nunito (texto). Ambas existem como fontes nativas do Roblox (`FredokaOne`, `Nunito`).

| Nível | Uso | Spec |
|---|---|---|
| L1 | Título da tela | Fredoka 700 · 30 px · caixa alta · tracking .04em |
| L2 | Nome do item (showcase) | Fredoka 700 · 32 px |
| L3 | Atributo principal | Fredoka 700 · 44 px · tabular |
| L4 | Nome no tile / info secundária | Nunito 800 · 15 px |
| L5 | Metadata (ilha, nível, notas) | Nunito 800 · 12–13 px · muted |
| L6 | Labels e badges | Nunito 900 · 10–11 px · caixa alta · tracking .08–.12em |

### Materiais e luz
- **Cabeçalho**: aço escovado (gradiente vertical + linhas verticais a 2.5 % de opacidade), highlight de 1 px no topo, costura escura embaixo.
- **Painel**: gradiente diagonal grafite, moldura de aço de 3 px + linha escura externa, noise SVG a 4.5 % em overlay.
- **Tiles**: gradiente vertical, highlight no topo, sombra de 2 px + 16 px. Palco interno rebaixado (inset shadow) com tint radial de raridade e linhas diagonais a 3 %.
- **Botão físico**: face em gradiente, highlight superior, aresta inferior de 4 px, sombra curta; pressiona 3 px e a aresta encolhe para 1 px.

### Geometria
Raios: 6 (chips) · 10 (controles) · 14 (tiles) · 16 (cards) · 20 (painel). Espaçamento em múltiplos de 4: 4 · 8 · 12 · 16 · 20 · 24. Bordas: 1 px suave, 2 px seleção, 3 px painel.

### Estados
| Estado | Tile | Showcase |
|---|---|---|
| Locked | arte em grayscale escura, selo de cadeado, "Ilha N" | eyebrow vermelho, botão de aço "Bloqueado", preço em muted |
| Available | preço em dourado | eyebrow "Disponível", botão dourado Comprar |
| Not enough | preço em muted | nota "Faltam X" em vermelho, botão de aço, shake ao clicar |
| Owned | texto "Adquirido" | botão ciano Equipar (pulso convite) |
| Equipped | selo verde + texto verde | eyebrow verde, selo plano "Equipado", atalho para o próximo |
| Next upgrade | flag dourada pregada no topo + anel suave | eyebrow dourado "Próximo upgrade" |
| Best | — | eyebrow "Melhor da categoria" |
| New | flag ciano "Novo" | — |
| Hover | sobe 3 px, borda forte, arte cresce 5 % | — |
| Selected | stroke ciano 2 px + glow | — |

### Motion (tudo com `prefers-reduced-motion` respeitado)
- Entrada do painel 340 ms (scale .94 → 1); tiles em cascata de 22 ms.
- Troca de item: arte entra em 340 ms com overshoot leve.
- Próximo upgrade: pulso de 2.4 s na borda e no segmento da escada.
- Lendário/mítico: brilho atravessa o palco a cada 7 s / 5.5 s.
- Compra: anel dourado expande, arte "pop", carteira pulsa, toast; tile recebe flash. "Próximo" migra para o item seguinte.
- Botão: hover sobe 1 px; pressed desce 3 px em 80 ms.

---

## PARTE 8 — QA (três passagens)

**Passagem 1 (estrutura)**: chaves de arte fora do slug deixavam 3 tiles vazios; linha de preço estourava quando havia delta; a comparação quebrava em 2 linhas; grid 16 px mais baixo que o showcase; fontes não carregavam no headless. Tudo corrigido.

**Passagem 2 (refinamento)**: espaço morto no showcase (resolvido com palco maior, atributo secundário e placa de rodapé); "+11900 %" absurdo em itens distantes (vira "×120 do atual"); `+2K` arredondando 1.600 (números completos até 9.999); toast cobria a última linha do grid (movido para o topo); preço escondido em itens bloqueados (agora visível em muted); Manto das Sombras lia como "dente" (silhueta refeita); Akatsuki escura demais.

**Passagem 3 (polish)**: índice dos tiles alinhado ao padding do palco; selo só para equipado e bloqueado (adquirido usa só o texto); arte do tile 6 rem e do showcase 15 rem; marca d'água da ilha a 9 %; nota de nível removida do cabeçalho; nomes longos encurtados nos dados em vez de quebrar linha.

**Checklist visual** (ver `screenshots/`):
1. Sem texto (`test-no-text.png`): composição continua legível — seleção, flag, chips e selos carregam a hierarquia.
2. Só texto: níveis tipográficos distintos (44 / 32 / 15 / 11 px).
3. 1 segundo: tab ativa (placa clara + indicador), equipado (selo verde), próximo (flag dourada + vitrine).
4. 50 %: números e artes sobrevivem; labels L6 somem primeiro, como devem.
5. Grayscale (`test-grayscale.png`): hierarquia mantida por luminância.
6. Espaçamentos em múltiplos de 4 em todo o sistema.
7. Tiles idênticos em estrutura; variação só por raridade e estado.
8. Comum → mítico: tint, moldura e brilho aumentam.
9. Lê como interface de jogo: materiais, botão físico, palco, flag pregada.

### Equivalência Roblox
| Protótipo | Roblox |
|---|---|
| `.shop` | Frame + UICorner + UIStroke(3) + ImageLabel noise |
| `.tabs` / `.tab` | Frame + UIListLayout + TextButton + UIGradient |
| `.grid` | ScrollingFrame + UIGridLayout + UIAspectRatioConstraint |
| `.tile__stage` | Frame com UIGradient radial (ImageLabel) + ImageLabel da arte |
| `.btn` | ImageButton 9-slice ou Frame + UIGradient + Frame "aresta" de 4 px |
| `.ladder` | Frame + UIListLayout horizontal |
| blur do mundo | BlurEffect no Lighting enquanto a loja está aberta |
| `rem` | UIScale ligado ao viewport |
