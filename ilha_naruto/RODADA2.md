# Rodada 2 — o que mudou desde a rodada 1 (leia antes de mexer no seu módulo)

A ilha foi **integrada**. O build completo (`build_ilha.py`) monta todas as zonas em detalhe em ~20 s e passa em
20 rotas de QA: as 14 da missão e mais 6 internas/travessias (porta → balcão do salão, loja, ramen e moinho, ponte em
arco e portão DB aberto → âncora). Os renders do conjunto estão em `renders/int2/` (e `_compare.jpg`).

## Mudanças na planta (`il_layout.py` — já aplicadas; o seu módulo tem que seguir)
1. **Água (reestruturada).** A cascata T2 → vale em y 126 caía dentro da faixa da ponte de saída. Agora:
   - **Sistema NE:** queda do paredão em (80, 188) → poço no T2 → canal `L.STREAM_T2` (no T2) → **queda pela borda
     NE** em `L.NE_FALL` = (119,2; 141,2) até o mar, ao lado da ponte de saída, sem cruzar a faixa dela.
   - **Sistema do vale:** um aqueduto subterrâneo (implícito) sai numa **bica** na face do muro x=108 em
     `L.SPOUT` = (108, 80, T1−3,2), que cai numa bacia no nível G. Dali o riacho segue `L.STREAM` (que agora começa
     em (110,5; 80)) → roda d'água → ponte em arco (`L.FOOTBRIDGE`) → queda pela borda SE.
   - O sistema oeste não mudou.
2. **T2 recortado** da faixa da ponte de saída: o T2 só existe onde `x − y <= L.T2_EXIT_CUT` (−14,85). O canto x
   108..118 / y 126..133 virou vale (G), sob a ponte. `IL.t2_poly()`, `il_col` e `L.zone_of` já seguem isso.
3. **Borda alargada na frente do portão:** o contorno agora passa por (±24; −118,6). Os pedestais dos leões ficam
   inteiros sobre a ilha.
4. **Minério:** `ore_points()` exclui as escadas N/S do fosso (antes 2 pontos caíam dentro delas).
5. **Casa T2 leste:** `HOUSES_T2[1]` = (96,5; 149,5; 13,5 × 12) (a pegada real do agente de casas).

## Padrões novos da integração
- **Prévia do Blender** em `Standard`, não AgX, para a cor sair saturada como nas referências.
  `il_scene.tone_emissives()` limita a força de emissão (só no Blender; a cor do Roblox não muda).
- **Barreira dos portões** (`il_gate_std.barrier`): ganhou anéis e rachaduras de energia em `Energy_Core_Glow`
  nas 2 faces. No Roblox ela sai com Transparency 0,2.
- **Galeria:** o piso da plataforma fica exatamente no nível do portão (gz); a base tem 38 × 46.
- **Export:** todo material com `Glow` no nome vira Neon. Peças móveis `VFX_*` aceitam `pivot`/`axis`/`rpm`
  (com sinal), `bob` (flutuar) e `rate` (pilão: sobe devagar e cai rápido).
- **Vegetação e props** (`il_veg`/`il_props`, dono: integração): respeitam as zonas livres que os módulos pediram
  (moinho, portas, abertura NE do summon, canais e poços, campo de treino) e as 20 rotas.
- **QA:** `il_qa.py` roda as 14 rotas + 6 extras. Todas têm que continuar OK.

## Como testar agora
Além do `studio.py <zona>` (a sua zona em detalhe e o resto em blockout), há o **build integrado** para uma pasta
sua:

```
IL_OUT="C:/Users/lucas/OneDrive/Desktop/To up/ilha_naruto/_studio/<zona>/int.blend" "/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python build_ilha.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b "<...>/_studio/<zona>/int.blend" --python il_qa.py -- nav markers
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b "<...>/_studio/<zona>/int.blend" --python il_cam.py -- "<pasta ABSOLUTA>" nome:x,y,z:tx,ty,tz[:lente] [...]
```

Nunca grave por cima de `ilha_naruto.blend`: o `IL_OUT` tem que apontar para a sua pasta em `_studio/`. Os
arquivos temporários levam o prefixo da sua zona.

## Rodada 2B (depois da critica independente) — mudancas ja aplicadas pela integracao
- **Planta:** `PIT_RAMP_W` 8 (era 6); escada NE (52 graus) com 12 de largura (caminho da progressao; `il_col.RADIAL_STAIRS`
  ja abre o entalhe); `LIONS` em (+-20, -116); `BACK_FALLS` ganhou a 3a queda em (-30, 188) com `CANAL_MID` ate o
  poco NO; `SIDE_STAIRS` (escadas gramado G -> anel em 247 e 293 graus) e `VALLEY_STAIR` (vale leste G -> T1 ao
  longo do muro de 26 graus) especificadas para o terreno construir.
- **Colisao do nucleo (il_col):** faixas mais largas (teto do export) e o LEITO do riacho do vale fora do chao G:
  la a colisao fica em `L.STREAM_WATER` (4,6), a lamina d'agua; quem pisa no riacho anda dentro dele.
- **Portoes (il_gate_std):** barreira = UMA placa fechada (normais certas; antes o Roblox mostrava um cata-vento com
  fatias faltando), nucleo de energia TINGIDO por portao (`core_mat(chave)`), aneis/rachaduras com secao 0,3 a
  0,15 das faces, halo no cadeado; ancora de preco `PURCHASE_UI_ANCHOR_<k>` agora DENTRO do vao (z 14, 2,5 a frente)
  - o telhado dos portoes nao precisa mais subir por causa dela.
- **Export:** minerio estatico `MINE_Ore_*` e `COL_MineOre` FORA do export (o jogo gera as rochas nos `ORE_*`; os
  nossos ficam como previa no Blender); sombra medida do centro da ilha; lanternas externas so a noite; oclusao de
  camera pelas paredes COL dos interiores (tag CamOccluder), sem cascas visuais; estado dos portoes persistente no
  streaming; colisao de bloqueio dentro do Model atomico do portao.
- **QA (il_qa.py):** alem das 20 rotas, os modulos podem registrar `EXTRA_ROUTES = {nome: (pontos, z0)}` e
  `EXTRA_PROBES = [(nome, x, y, z_piso, dx, dy)]` (sondas de borda: a 2 studs do piso, na direcao (dx, dy), tem que
  bater numa colisao em ate 3,5). Sondas fixas hoje: fenda do canto NE do T2 e borda da ancora (as 2 FALHAM ate as
  correcoes desta rodada). Passe de largura informativo com corpo de raio 1,7.
- **Regras novas (vindas da critica tecnica):** nada com menos de 0,1 de folga entre superficies de materiais
  diferentes (z-fighting no Roblox); bevel 0 em caixa com menor dimensao < 1,0 e bevel <= 5% da menor dimensao no
  resto; apagar pecas com todas as dimensoes < 0,35; frisos/gregas com secao >= 0,3.
- **Mantenha o modulo SEMPRE funcionando** (edite em passos pequenos, rode o estudio a cada passo) e anote o que ja
  fez em `_studio/<zona>/PROGRESSO.md`: se a sessao cair no meio, quem continuar parte dali.
