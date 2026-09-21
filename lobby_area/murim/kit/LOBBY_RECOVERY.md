# Continuidade do lobby Murim

Arquivo curto de retomada. Serve para a proxima sessao comecar de um estado conhecido, sem repetir
teste nem perder correcao. Nao e historico do projeto.
Tudo aqui foi MEDIDO; onde for suposicao, esta escrito que e.

## Caminhos reais

```
lobby_area/murim/kit/
  k_core.py        Builder, t_box/t_prism/t_lathe/t_tube/t_blob/t_sweep, xf, instance, smooth01
  k_materiais.py   PD (dicionario de tintas), build_paint, unwrap, bake, finalize
  k_montagem.py    build_lobby(): masters + colocacao de TODO o lobby
  k_lobby.py       pecas grandes: forja, penhasco, serra/nevoa de fundo, picareta
  k_relva.py       relva geometrica (manta + ladrilho de tufos + franja + musgo)
  k_veg.py         pinheiro, arbusto, tufo     k_jardim.py  flores e props de vila
  k_portal.py      um portal por area (moldura, vortice, marca do anime)
  run_bg.py        etapas do pipeline em Blender headless
  gerar_lobby.py   gera export/montar_lobby.lua a partir de lobby_placements.json
  picareta_aurora.blend   malha do monumento (ver "Picareta")
  export/          FBX + scripts Lua de montagem no Studio
```

Blender: `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`

## Pipeline, na ordem

```bash
blender -b kit_forja_celeste.blend   --python run_bg.py -- lobby       # ~35 s, monta e renderiza
blender -b lobby_forja_celeste.blend --python run_bg.py -- lobby_uv    # ~10 s
blender -b lobby_forja_celeste.blend --python run_bg.py -- lobby_bake A_LOBBY_1,...,A_LOBBY_6 color 2048 20
blender -b lobby_forja_celeste.blend --python run_bg.py -- lobby_bake ... rough 2048 12
blender -b lobby_forja_celeste.blend --python run_bg.py -- lobby_bake ... normal 2048 8
blender -b lobby_forja_celeste.blend --python run_bg.py -- lobby_final # materiais finais + FBX
```

No Studio: importar `export/LOBBY_FORJA_CELESTE.fbx` pelo 3D Importer e rodar `export/tudo.lua` pelo
Command Bar (encadeia montar -> portais -> alpha -> agua -> verificar).
O import falha em ~45% das vezes depois de 45-90 min; re-enfileirar (marcar a linha, Start Import)
conclui na hora, porque as malhas ja subiram.

## Armadilhas que ja custaram tempo

1. **`k_export.py` indexava o manifesto por nome de OBJETO; `run_bg.py` grava por nome de MALHA.**
   26 malhas sumiam do FBX em silencio. Corrigido, com guarda que aborta o export se voltar.
2. **AlphaMode.** Os atlas sao RGB 24 bits, sem alfa. O importador deixa toda `SurfaceAppearance` em
   `Overlay`, que usa o alfa para mesclar sobre a cor da Part - sem alfa, sai o cinza da Part.
   `export/materiais_alpha.lua` troca para `Transparency`. Sem esse passo o lobby fica cinza, e
   **nao** e problema de UV nem de textura.
3. **Teto de 20.000 triangulos por malha** no importador. `run_bg lobby` imprime quem passou de 19 mil.
4. **Master + instancia.** Um Builder com ~90 blocos estoura o teto. Peca repetida vira master + `K.put`.
5. **Raycast nao e teste de caminhada.** Raycast amostra superficie. Para circulacao, andar.
6. **Cavity do Workbench.** `k_render.workbench` liga `show_cavity` e `show_shadows`. Em peca de kit
   isso da definicao; em cenario de 900 studs vira HACHURA fina que parece defeito de malha e nao e.
   Medido: com `show_cavity=False` a serra sai limpa. Ao julgar cenario distante pelo preview, descontar.
7. **Peca de kit ampliada nao vira cenario.** `pico()` era o feixe de agulhas do penhasco esticado
   para 200 studs: cada faceta virou faixa de vinte studs e leu como chapa corrugada. Cenario distante
   quer POUCAS faces grandes e contraste baixo - a distancia se faz por perda de contraste.
8. **Superficie desenhada duas vezes.** A 1a versao de `anel_serra` emitia a faixa `linha->dentro` na
   banda de rocha E na de neve. A medida que achou: 624 vertices coincidentes em 1.248. Contar
   vertices coincidentes e o teste barato para isso.
9. **Zonas DURO envelhecem.** A barreira do lago continuou sendo o retangulo de quando o lago era
   retangular, muito depois de ele virar poligono. Quando uma forma mudar, conferir quem a referencia
   por literal.
10. **Cotas.** A geometria grava `lobby_cotas.json` e a colisao em `gerar_lobby.py` le de la. Nao
    escrever altura a mao nos dois lugares.
11. A elevacao do terraco do Santuario esta amarrada aos pads de teleporte (Roblox Y=10) e **nao**
    pode ser renivelada.

## Feito e verificado nesta rodada

- **Relva geometrica** (`k_relva.py`) no lugar das 760 placas `t_box`. O defeito nao era cor nem
  quantidade: era silhueta - 9 a 18 studs de aresta reta por 0,18 de altura, e a face dominante vista
  de cima era um quadrilatero. Tres camadas: manta continua de borda recortada (carrega a cor),
  ladrilho de tufos instanciado (97 colocacoes, 3 malhas, denso na divisa e ralo no miolo) e franja de
  borda com musgo cobrindo o encontro com a pedra. A lamina e um prisma de 3 lados que fecha em BICO,
  com gradiente raiz->ponta na cor de vertice.
- **Calcada**: modulo de 11 -> 7 studs, junta rebaixada de verdade, laje escura rara. Lia como xadrez.
- **Praca hexagonal**: aneis concentricos, seis raios ate os vertices, espelho d'agua hexagonal girado
  30 graus (para cada ponte cruzar uma face) e marco de pedra em cada vertice.
  Vertice N = via imperial | vertice S = escadaria da Forja | face L = portais | face O = Loja.
- **Picareta** de 40 studs no lugar do dragao (ver abaixo).
- **Fundo do mundo**: aneis fechados (`anel_serra`, `anel_nevoa`), malha unica, sem emenda.
- **Telhado do Salao da Forja**: ouro macico -> verde-jade, como pedia o brief.
- **Pe da escadaria do Santuario**: 0 -> 6 lajes na faixa que o retangulo velho do lago barrava.

## Picareta - de onde ela vem

A referencia era a *Dwarven Pickaxe Handpainted* do Sketchfab (imagem 42.png), que **nao e baixavel**
(HTTP 403, confirmado). O usuario mandou no lugar a foice *Desolate Devil* com a instrucao de adaptar
aquela foice. A meia-lua **nao foi desenhada**: foi recortada da ilha da lamina do `Desolator.fbx`,
sem o colo espinhoso, cortada no plano X e espelhada. As duas meias-luas sao 3.872 dos 9.988
triangulos e trazem o acabamento esculpido original.

O que fez funcionar: a lamina da foice e fina demais para monumento (raiz de 0,53). Cada vertice foi
empurrado para LONGE da polilinha do gume - o gume nao se move, a curva assinatura da foice fica
intacta, e a massa cresce so para dentro (raiz 0,53 -> 1,28).

A malha vive em `picareta_aurora.blend` e **nao** e reconstruida a cada build: o recorte depende de
indices de ilha e de planos de corte medidos naquele FBX. `k_lobby.minha_picareta()` so anexa a malha
e a reempacota num Builder, slot por slot, preservando a cor de vertice `rnd`.

Limite honesto: a cor e assada em atlas RGB, sem alfa e sem emissivo. O verde e MATERIA (gemas, veio
de jade rente ao gume, ranhuras) e nunca o halo luminoso da referencia.

## Aberto

- **Cinza residual por densidade de texel.** `SANT_galeria` amostra 0,75 texel/poligono contra 23,88
  de uma peca que sai certa, e 17% de ilhas degeneradas contra 0%. As pecas nessa faixa continuam
  lavadas mesmo com o AlphaMode corrigido. Caminho: aumentar a area de UV dessas malhas
  (`SANT_galeria`, `ESCADA_*`, `TEL_G_*`) - nao mexer em tinta.
- **Teste de caminhada com avatar**: nunca executado.
- **Dois lagos de lotus simetricos com pontes vermelhas**: o brief pedia no plural; existe um so, a
  leste. Nao foi feito porque a reorganizacao hexagonal veio antes.
- **Modelos de arvore prontos da internet**: pedido pelo usuario; as arvores seguem procedurais.
- **6 malhas espelhadas (`*_esp`)** cujo atlas declarado difere do material aplicado - conferir.
- **Correcoes feitas so na cena** (posicao/escala dos leoes) precisam ir para os geradores, senao o
  proximo build as desfaz.
