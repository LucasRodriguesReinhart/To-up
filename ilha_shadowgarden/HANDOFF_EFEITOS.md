# Passagem de contexto: Ilha 3 (Shadow Garden), Anime Mining Simulator

Cole este arquivo no início do novo chat. Ele resume uma conversa longa feita numa sessão na nuvem (sem acesso ao
Roblox Studio) e diz exatamente onde parar e por onde continuar.

## 1. Onde está o trabalho

- Repositório `LucasRodriguesReinhart/To-up`, branch **`lobby-v3-tech`** (tudo commitado e enviado).
- Pasta da ilha: `ilha_shadowgarden/`. Pipeline: módulos Blender `sg_*.py` → `build_sg.py` (gera
  `ilha_shadowgarden.blend`) → `sg_qa.py` (rotas, sondas, salão livre, dungeon limpa) → `export_sg.py` (FBX + Lua de
  montagem para o Studio). Atalhos em `run.sh` (Blender 5.2 no Windows).
- Briefs e auditorias: `AGENT_BRIEF.md`, `ACABAMENTO2_BRIEF.md`, `AUDITORIA3.md` (151 itens), `FINESSE3_BRIEF.md` e
  `FINESSE3B_BRIEF.md` (os dois têm, no fim, a seção de fechamento com pendências).

## 2. O que já foi feito (ondas de finesse, todas aprovadas pelas folhas antes/depois no modo Roblox)

| Onda | Zonas | Commits |
|---|---|---|
| finesse3 | terreno, entrada, vila, interiores, castelo, salão, Salão Sombrio, masmorra | `e030350`…`541a9e5` |
| finesse3B | pátio e mirante, vegetação, alquimia, invocação/saída/água | `779f155`…`7e98f72` |
| finesse3C | props e vida nas ruas | `8354bd2` |

Estado final validado: **build OK com 862.692 tris** (teto 870k), 2203 objetos, 1679 colisões, 61 luzes.
QA: ROTAS 27/27, ROTAS_ABERTAS 3/3, ROTAS_MODULOS 52/52, SONDAS 29/29, SALAO_LIVRE, DUNGEON_LIMPA, CAVE_LIVRE e TECH OK.
Folhas antes/depois de cada zona em `renders/finesse3/<AGENTE>/folha*.jpg`.

Todas as zonas estão no teto de tris (e a zona dressing também em luzes e MeshParts): qualquer coisa nova precisa
tirar geometria antes de pôr.

## 3. O jogo AINDA NÃO TEM nada disso

O export que está no repositório (`export/`, id `b4d23c3b`) é anterior às ondas de finesse. O usuário aprovou levar
para o jogo: falta **rodar `export_sg.py` no `ilha_shadowgarden.blend` atual e montar no Studio**
(`export/montar_ilha_shadowgarden.lua`), depois testar no Play.

## 4. Decisões pendentes do usuário

1. Teto de luzes da zona cave de 6 para 8 (luz nos cristais e na queda d'água do Salão Sombrio). Mantido em 6.
2. Baixar um tom o Neon do painel do portão Demon Slayer (asset aprovado `il_gate_ds`/`sg_core`). Não mexido.

## 5. Conferir no Play

- Fresta de luz na base das casas (no Roblox a PointLight não faz sombra; quem fecha é o forro e o piso).
- Vão do portão da muralha (06.13): ficou aberto, sem barreira.
- Escuridão do salão (se ficar escuro demais, clarear `Stone_SG_MarbleBlack` em `sg_lib.SMATS`).
- Braseiro da casa da guarda e lanterna do pórtico do beco (NightOnly).
- Aberturas dos portões das muretas da taverna e do boticário (~3,8).

## 6. PRÓXIMA TAREFA (pedido do usuário, em andamento)

> "Trabalhe nos efeitos visuais, na área de invocação, nos portais e na luz do ambiente, deixando semelhantes ao do
> vídeo. Faça com perfeição, nada qualquer; pesquise referências para ter base do que é bom."

### 6.1 A referência (vídeo de 4 s do usuário, cena noturna de outro jogo Roblox)
- Céu: preto no zênite descendo para um **azul elétrico muito saturado** na faixa do horizonte.
- Lua **grande, brilhante, branco-lavanda com textura**, alta no céu.
- Água/chão ao fundo azul, refletindo o brilho do horizonte.
- Contraste forte: personagem quase em silhueta com contorno claro; **bloom generoso** nas partes claras.
- Paleta quase monocromática azul + branco; o roxo da ilha vira acento.

### 6.2 Onde mexer
- **Luz ambiente**: perfil `[3] ShadowGarden` em `roblox/patches_jogo/AreaAtmosphere.client.lua` (ClockTime 0.6,
  Ambient, OutdoorAmbient, Atmosphere Color/Decay/Density/Haze/Glare, ColorCorrection Tint/Contrast/Saturation,
  ExposureCompensation). Hoje: ambient (142,140,174), air (132,116,186), decay (74,56,120), density 0.3, haze 0.85,
  contraste -0.02, saturação -0.03 (lilás claro e lavado, longe da referência).
- **Céu, lua, bloom**: `roblox/CeuSombras.client.lua` (`MOON_SIZE = 24`, `STARS = 3000`,
  `BLOOM = {Intensity 0.35, Size 42, Threshold 1.55}`; Sky e Bloom são dele, o AreaAtmosphere não toca neles).
- **Efeitos atuais (fracos)**: função `vfx(model, mk)` em `roblox/JardimSombrasIsland.lua`: só ~4 faíscas/s na
  invocação, ~6/s no portal e ~3/s no portão DS, com texturas padrão `sparkles_main.dds`. Emissores recebem a tag
  `IlhaVFX` e os atributos `Dist`/`Rate0` (o cliente `ILHAS_Cliente` faz o culling por distância); peças Neon com a tag
  `IlhaPulso` + atributo `Cor0` pulsam.
- **Marcadores** (pasta `GAMEPLAY_MARKERS` do modelo `ILHA_SHADOWGARDEN`; posições Roblox do export b4d23c3b):
  - `SUMMON_Main` (-882.0, 40.2, 896.1): torre de invocação; `SUMMON_PlayerPosition` (-884.8, 40.2, 880.4).
    Peças da torre: `SG_Sum_Tower_Glow` (materiais `SG_SumPortal_Glow`, `SG_SumPortalDeep_Glow`, `SG_SumStar_Glow`),
    esfera armilar `VFX_SGSUM_*` (gira, tag IlhaMovel) com núcleo ~y 97.5.
  - `DUNGEON_Portal`/`DUNGEON_Hall` (-1240.6, -10.4, 740.0), raio 13: portal do Salão Sombrio (frente para o norte).
  - `DUN_NEXT_R2` (-1332.2, -72.0, 756.2) e `DUN_NEXT_R3` (-1436.6, -72.0, 774.6): portais das salas, Part w27 h21.
  - `DUN_EXIT_R1`, `DUN_EXIT_R3`/`DUNGEON_ExitPortal`: saídas da masmorra.
  - `GATE_DemonSlayer` (-1513.0, 52.2, 944.4) e `GATE_DemonSlayer_OpenFX`.
- **Texturas de efeito já publicadas no jogo** (`roblox/patches_jogo/OreVFX.lua`, tabela TX): `glow_soft`,
  `spark_star`, `sparkle_diamond`, `shockwave_ring`, `swirl_vortex`, `magic_circle`, `energy_beam`,
  `rune_glyphs_2x2`, `aura_flipbook_4x4`, `smoke_flipbook_4x4`, `lightning_flipbook_4x4`, `ki_column`. Reutilizar
  esses IDs (funcionam no jogo), não inventar asset.

### 6.3 O que a pesquisa trouxe (base para "bom")
- Efeito bom = **3 a 5 camadas simples empilhadas**, cada uma com papel claro (núcleo, borda, brilho, partículas,
  onda), não um emissor com Rate alto.
- Portal precisa **agir no entorno**: derramar luz nas superfícies (PointLight/SurfaceLight de cor), **puxar
  partículas para dentro** e soltar névoa no chão. Borda nítida e clara contra um **núcleo escuro**.
- Invocação estilo gacha: círculo mágico girando no chão como base + motas subindo + coluna/pilar de luz; no momento
  da invocação, acumulação de energia e liberação (onda de choque + flash), com cor ligada à raridade.
- Ferramentas Roblox (docs oficiais):
  - Sucção: ParticleEmitter `Shape = Disc`, `ShapeInOut = Inward`, `ShapeStyle = Surface`.
  - Anéis e ondas deitados: `Orientation = VelocityPerpendicular`; `Squash` para esticar.
  - Brilho aditivo no escuro: `LightEmission = 1`, `LightInfluence = 0`, `Brightness` > 1.
  - Camadas na ordem certa: `ZOffset`. Animação de textura: `Flipbook*` (grade 4x4 já existe nas texturas).
  - Arcos de energia: `Beam` com `CurveSize0/1`, `Segments`, `TextureSpeed`, `FaceCamera`.
  - Céu: `Atmosphere` (Color = horizonte, Decay = cor longe do sol, Haze alto para o gradiente aparecer, Glare >0
    para o Decay valer, Offset para a silhueta do horizonte), `Sky.MoonAngularSize`, `Sky.StarCount`,
    `Sky.SkyboxOrientation`; ColorShift_Top/Bottom para a cor do luar nas superfícies.

### 6.4 Plano sugerido (a testar no Play, ajustar pelo olho)
1. **Luz ambiente** (AreaAtmosphere + CeuSombras): noite mais profunda e azul. Ponto de partida: Ambient e
   OutdoorAmbient mais escuros e azulados; ColorShift_Top branco-azulado (luar); Atmosphere Color azul elétrico
   saturado, Decay navy quase preto, Haze alto (~2), Glare baixo (~0.3), Density baixa para a ilha ainda ler;
   ColorCorrection com contraste positivo e saturação positiva leve, tint frio; lua maior e mais brilhante; bloom
   mais forte só nas partes claras (Threshold perto de 1). Cuidar para pedra, madeira e casas continuarem legíveis.
2. **Portal do Salão Sombrio e portais das salas**: núcleo escuro + borda clara girando (Beam/anel), vórtice
   (`swirl_vortex`) em 2 velocidades, partículas sendo sugadas (Disc Inward), névoa rasteira saindo, PointLight
   violeta-azulada pulsando suave iluminando o chão e as colunas.
3. **Invocação**: círculo mágico girando no chão da plataforma, motas subindo em espiral até a esfera armilar,
   feixe de energia do núcleo; no ato de invocar (hook do gacha), carga → flash + onda de choque + coluna de luz,
   cor pela raridade.
4. **Portão Demon Slayer**: manter a identidade dele, só harmonizar.
5. Performance: tudo client-side com culling por distância (seguir o padrão `IlhaVFX`/`Dist`/`Rate0`), poucos
   emissores e Rate moderado.

## 7. Showcase em vídeo (Blender)
Um vídeo parcial de 48 s (15 planos, modo Roblox) foi renderizado na nuvem a partir do build atual; o usuário achou
fraco. A luz do Blender não é a do jogo: o showcase que vale é gravado no Play depois dos efeitos e da luz nova.
Existe `roblox/showcase_camera.lua` para gravar um passeio de câmera dentro do Play (coordenadas da versão antiga;
revisar os planos).

## 8. Regras do projeto que continuam valendo
- Direção de arte "elegância escura"; roxo dessaturado só como acento de função (portal, invocação, craft, rosácea,
  barreira). Nada de "visual de IA": nenhum efeito sem função.
- Não modelar minério; nada colidível no MINE_RECT do salão; rotas e QA sempre verdes; orçamento da ilha ≤ 870k tris.
- Commits em `lobby-v3-tech`.
