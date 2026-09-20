# Continuidade do lobby Murim

Arquivo curto de retomada. Serve para a proxima sessao comecar de um estado conhecido, sem repetir
teste nem perder correcao. Nao e historico do projeto.

## Caminhos reais

| o que | onde |
|---|---|
| repositorio | `C:\Users\lucas\OneDrive\Desktop\To up` (branch `lobby-v3-tech`) |
| geradores | `lobby_area/murim/kit/` — `k_montagem.py` (monta), `k_lobby.py` / `k_kit2.py` / `k_veg.py` (pecas), `gerar_lobby.py` (gera o lua de montagem e a colisao) |
| pipeline | `run_bg.py -- lobby` / `lobby_uv` / `lobby_bake <atlas> <passe> 2048 20` / `lobby_final` |
| atlas assados | `lobby_area/murim/kit/tex/A_LOBBY_{1..6}_{color,rough,normal}.png` |
| FBX | `lobby_area/murim/kit/export/LOBBY_FORJA_CELESTE.fbx` |
| montagem em Lua | `lobby_area/murim/kit/export/montar_lobby.lua` (gerado, nao editar a mao) |
| cotas compartilhadas | `lobby_area/murim/kit/lobby_cotas.json` (a geometria grava, a colisao le) |
| place | Roblox Studio, "Anime Mining Simulator", placeId 101959830085647 |
| backup da cena | `ServerStorage.BACKUP_LOBBY.LOBBY_MURIM_pre_relevo` (2119 partes) |
| commit de referencia | `80dddf2` |

Uma unica sessao de Studio responde pela cena. Agentes nao abrem instancia (numa rodada anterior 14
instancias travaram a maquina do usuario).

## BLOQUEIO ABERTO: malhas renderizam cinza

Parte das malhas renderiza cinza/branco no Roblox em vez da cor assada.

- **Afetadas:** `SANT_galeria`, `TEL_G_*` (telhado da galeria), copas de arvore.
- **Nao afetadas (controle):** `KIT_lanterna_palacio`, `KIT_muro_seg`, `POR_*` (portais).
- Todas as 2204 MeshParts tem `SurfaceAppearance` com `ColorMap` preenchido e IDs distintos.
- A peca afetada examinada: `SANT_galeria`, ColorMap `rbxassetid://126054264539349`.
  A de controle: `KIT_lanterna_palacio`, ColorMap `rbxassetid://133604368309600`.
- Ambas: `AlphaMode = Overlay`, `NormalMap` e `RoughnessMap` presentes, `Color` da peca
  `0.639, 0.635, 0.647`, `Material = Plastic`, `TextureID` vazio.

### Hipoteses que eu declarei eliminadas SEM base suficiente

Corrigido pelo usuario. Nao repetir estes argumentos como se fossem prova:

| afirmei | por que nao vale |
|---|---|
| "PreloadAsync sem erro, logo carregou" | `PreloadAsync` nao lanca excecao quando um asset falha, e nao suporta `SurfaceAppearance` (usa pacote de textura processado). Nao demonstra carregamento. |
| "RGB sem alfa deixa o resultado indefinido" | RGB 24 bits E a especificacao de albedo do Roblox. A ausencia de alfa nao e defeito. |
| "ficou branco ao trocar AlphaMode, logo e UV" | E observacao, nao diagnostico. Overlay e Transparency usam o alfa de formas diferentes; trocar nao identifica qual imagem ou regiao esta sendo amostrada. |
| "UV dentro de [0,1], logo UV esta ok" | Coordenada valida pode apontar para a regiao ERRADA da textura. |
| "os 6 PNG tem saturacao 0.39-0.50, logo o bake esta correto" | Nao demonstra que a peca problematica recebeu o arquivo certo nem que os UV dela caem na regiao pintada. |

### CAUSA ENCONTRADA (com arquivo e linha)

`k_export.py` linha 13 indexa `lobby_atlas.json` por nome de **OBJETO**:

```python
for n in names: mesh_atlas[bpy.data.objects[n].data.name] = atlas
```

Mas `run_bg.py` (`objs_de` / `unwrap`) grava e le o MESMO json por nome de **MALHA**. Para as pecas
que existem em duas geracoes (as `KIT_*` com sufixo `.001`), os dois espacos de nome nao coincidem e
a associacao malha->atlas se perde no export.

**Medido:** 168 malhas assadas nos atlas, **26 ausentes do FBX** (`KIT_arbusto_a.001`,
`KIT_arquitrave.001`, `KIT_bal_seg.001`, `KIT_besta_*`, `KIT_chiwen.001`, `KIT_lanterna_palacio.001`,
`KIT_muro_seg.001/.002`, entre outras). Comparar `lobby_atlas.json` com `export/kit_meshes.json`.

O que o rastreio DESCARTOU por medida, e nao deve ser reinvestigado:
- UV: 1 unica camada `UVMap` com `active_render=True` nas 169 malhas; nao ha camada competindo
- amostragem do PNG nas UV reais: `SANT_galeria` cai em **98.5% de pixel colorido** (sat 0.57);
  `POR_fragmento_1_ki`, que renderiza CERTO, cai em 91.9% de PRETO — logo cobertura de UV nao explica
- branco: a fracao de pixel BRANCO e **0.0% em todos os 8 atlas**; o cinza visto no jogo nao pode vir
  do conteudo do ColorMap
- FBX: md5 do PNG embutido == md5 do arquivo em `tex/`; render do proprio FBX com emissao=ColorMap
  mostra `SANT_galeria` em vermelho-laca correto

**Correcao a fazer:** alinhar os dois espacos de nome em `k_export.py:13` (indexar por malha, como o
`run_bg.py` faz) e reexportar. Depois confirmar que as 26 malhas aparecem no FBX, e so entao
reimportar. Verificar tambem o achado lateral: 6 malhas espelho (`*_esp`) carregam material de atlas
diferente do que o json declara (ex.: `TEL_G_espigao_esp` diz `A_LOBBY_4`, usa `F_A_LOBBY_3`).

**Estado real: a causa ESTA identificada; falta corrigir e validar.**

### Proximo passo executavel

Rastrear de ponta a ponta, comparando peca afetada contra peca de controle em cada elo:

```
objeto de origem -> conjunto UV -> imagem no material (Blender) -> PNG exportado
   -> textura dentro do FBX -> asset importado -> SurfaceAppearance da peca no Studio
```

O teste que decide o elo do bake e local e barato: **amostrar o PNG nas coordenadas UV reais dos
poligonos da malha afetada** e ver se ali ha pixel pintado ou vazio. Se estiver pintado, o defeito e
depois do bake; se vazio, e no bake ou no empacotamento de UV.

Testes controlados sugeridos, uma variavel por vez, numa COPIA da peca:
1. textura de diagnostico chapada e opaca — a cor aparece na peca?
2. grade colorida e numerada — os marcadores caem nas faces esperadas?
3. textura verdadeira — as regioes pintadas correspondem as faces esperadas?

Nao remover todos os `SurfaceAppearance`, nao refazer todos os bakes e nao pintar o cenario de forma
uniforme para esconder o defeito.

## Correcoes que existem SO NA CENA e ainda nao voltaram aos geradores

Registrar como pendente num commit **nao** e incorporar ao gerador. Estas tres serao desfeitas pela
proxima montagem se nao forem portadas:

| correcao | onde esta | onde precisa entrar |
|---|---|---|
| terreno de agua reesculpido seguindo o contorno novo do lago (52 faixas) | aplicado na cena por Lua | `agua_cartoon.lua` ainda esculpe retangulo de 30x200 |
| sombra/colisao/query desligadas em 520 pecas de cenario distante (penhasco, nuvem, pico, cascata) | aplicado na cena | `gerar_lobby.py`, junto da regra `SEM_SOMBRA` |
| leoes ampliados 1.65x e movidos para o pe da escadaria | `export/leoes_escadaria.lua`, rodado na cena | posicao e escala em `k_montagem.py` |

A posicao da ponte JA foi portada para `k_montagem.py` (de `y=0` para `y=60`).

## Pendencias conhecidas do trecho sudoeste

O trecho escolhido e o canto sudoeste (Blender x -184..-64, y -58..40). Ele reune borda rochosa,
muralha e torre, terraco do Santuario com escadaria, canteiro, calcada e margem do lago.

- [x] escadaria descia dentro do lago (11.5 studs de sobreposicao) — corrigido, 17.0 studs de terra
      firme, verificado por geometria
- [x] ponte-lua atravessava a escadaria (o raio batia em `ponte6` a 5.65 no lugar do degrau) —
      corrigida na cena e no gerador
- [ ] **queda de 3.40 studs** entre o pe da escada e a agua: a lista `DURO` em `k_montagem.py` ainda
      barra o calcamento no retangulo ANTIGO do lago (`-103..-67, -77..137`), entao a terra que a
      reentrancia liberou ficou sem piso. Precisa de piso visivel E apoio na mesma altura.
- [ ] **contorno do lago nao e fonte unica**: `OESTE`/`LESTE` em `k_montagem.py` definem a malha, mas
      `agua_cartoon.lua` e a lista `DURO` usam o retangulo antigo. Centralizar.
- [ ] acabamento do trecho: vegetacao com volume, margem integrada, telhado verde-jade no modulo
      arquitetonico do trecho
- [ ] rochas: as colunas verticais ainda leem como modulo repetido; trabalhar massas e juncoes
- [ ] teste de percurso com AVATAR — nunca foi executado

## Sobre os testes ja feitos

Separar o que foi medido do que foi observado:

- **Verificado por calculo (raycast/geometria, no Blender ou por script no Studio):** sobreposicao
  escada/lago, interferencia ponte/escada, perfil da escada (0.8 por degrau, zero pontos sem chao),
  queda de 3.40, equivalencia das cotas antes/depois do refactor.
- **Observado no Studio (captura):** materiais cinza, repeticao das colunas de rocha, placas verdes.
- **Testado com o personagem em execucao:** NADA. O teste com avatar nao foi executado em nenhuma
  rodada. Raycast e amostragem de superficie ao longo de um raio, com filtro `Include` restrito a
  `LOBBY_MURIM` — exclui terreno, agua e grupos de colisao fora desse modelo. Nao demonstra caminhada.

## Regras do projeto que ja custaram tempo

- A chave `'torre'` ja e a Torre do Fogo da Forja. A torre de muralha e `'mtorre'`.
- Os seis discos de teleporte estao travados em Roblox X=124.5, Z de 13 em 13 (-32.5 a 32.5).
  Construir em outro modulo quebra o teleporte. A cota do Santuario tambem esta acoplada a eles.
- `Lighting.Technology` nao pode ser lida nem escrita por script neste contexto (falta capability).
- O import do FBX costuma falhar perto dos 45% depois de ~45 min; reenfileirar (marcar a linha e
  Start Import) completa na hora, porque as malhas ja subiram. Nao refazer o bake por causa disso.
- Comentario no fim de uma linha de tupla come os itens seguintes da mesma linha.
- `_r` (random) so e importado na secao de vegetacao de `k_montagem.py`; secoes anteriores precisam
  de import local.
