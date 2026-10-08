# Perfil [5] do AreaAtmosphere: Wano de dia (proposta do agente de luz/VFX, M4)

Para o lead aplicar no M5. Troque **só a linha `[5]`** do `AreaAtmosphere_area5.lua` desta pasta. O formato é o mesmo das chaves `[OP]` que já estão lá (`lat`, `eds`, `ess`, `cbright`). Bloom e SunRays continuam no topo do `CeuWano.client.lua`.

Fonte das contas: `op_lights.sun_check()`. Ele usa o modelo de sol do `export_roblox.sun_setup`, que já foi conferido no Studio:

```
sol = (sin a · cos t, −cos a · cos t, −sin t)
a = 2π · ClockTime / 24
t = 23,5° − latitude
```

O rumo local da ilha vem do giro de 145°.

## 1. O achado: 13,5 / 30 deixa o castelo em contraluz

O plano (seção 10) e o `LEIA_M5` pedem sol de **trás-esquerda de quem chega pela ponte**, com a fachada sul do castelo clara. A componente horizontal pedida para `GetSunDirection()` em X/Z é ≈ (+0,98; −0,17). Os valores iniciais fazem o contrário:

| ClockTime / lat | sol no rumo LOCAL (x, y, z) | elevação | leitura para quem chega |
|---|---|---|---|
| 13,5 / 30 (linha atual `[5]`) | (0,25; 0,31; 0,92) | 67° | sol na **frente**, quase a pino: fachada sul em sombra própria, sombra curta, cidade chapada |
| 15,3 / 22 (perfil antigo `GrandLine`) | (0,64; 0,41; 0,65) | 40° | **contraluz** do castelo |
| **9,05 / 10 (proposta)** | (−0,42; −0,58; 0,70) | 44° | **trás-esquerda**: castelo, torii e fachadas da rua ao sol, sombras longas para o fundo-direita |

Com 9,05 / 10, `GetSunDirection()` fica **(0,676; 0,699; −0,234)**. A componente horizontal X/Z é **(0,95; −0,33)**, a 10° do alvo do `LEIA_M5`. Este é exatamente o sol de prévia do Blender (`SUN_Key`, `op_scene.SUN_DIR`), que é o sol de todas as folhas M1–M4. O jogo passa então a ter a mesma luz que foi aprovada nas folhas.

**Alternativa**, se a elevação de 44° parecer baixa no Play: 9,3 / 14 dá ~48° no mesmo rumo. Não use tarde (> 12h). Em qualquer latitude, à tarde o sol vem de +Y local (do castelo para a ponte).

## 2. Linha proposta

```lua
 [5]={name='GrandLine',time=9.05,lat=10,brightness=2.4,ambient=C(138,146,164),out=C(150,162,182),eds=.5,ess=.3,air=C(190,216,246),decay=C(104,150,206),density=.24,offset=.12,haze=.8,glare=.12,cst=C(255,242,224),tint=C(255,250,244),contrast=.08,saturation=.10,cbright=0,exposure=-.05}, -- [OP] Ilha 5 Wano (PLANO_OP sec. 10 + op_lights): DIA, sol de tras-esquerda de quem chega (ClockTime 9,05 / lat 10 = o SUN_Key das folhas; GetSunDirection ~ (0,68; 0,70; -0,23)); bloom/sunrays/nuvens/mar local: CeuWano
```

O que muda em relação à linha atual, e por quê:

| Chave | Atual | Proposta | Motivo |
|---|---|---|---|
| `time` / `lat` | 13,5 / 30 | **9,05 / 10** | Sol de trás-esquerda (seção 1). |
| `brightness` | 2,6 | **2,4** | O reboco do castelo (234,228,212) e as lajes da praça (196–206) ficam de frente para o sol com esse rumo. Com 2,6, somado ao Exposure 0 e ao `cbright` 0,02, o branco chapa no Play. |
| `exposure` / `cbright` | 0 / 0,02 | **−0,05 / 0** | Mesmo motivo. Os outros perfis de dia usam −0,08 a −0,12. |
| `haze` / `density` / `offset` | 1,0 / 0,26 / 0,15 | **0,8 / 0,24 / 0,12** | O prompt (seção 17) pede para "preservar azul do céu". Haze 1 embranquece o horizonte e as falésias do fundo. A DS fica ~200 à frente e continua com profundidade. |
| `air` / `decay` | (196,220,246) / (112,156,206) | **(190,216,246) / (104,150,206)** | Céu um tom mais saturado, o azul da concept. |
| `glare` | 0,15 | **0,12** | Com o sol baixo atrás do jogador, o glare cai no horizonte da frente. |
| `cst` (ColorShift_Top) | — | **(255,242,224)** | Sol quente leve. Sem ele, a face iluminada fica neutra contra o Ambient frio (sombras azuladas de propósito). |
| `contrast` | 0,06 | **0,08** | Profundidade das sombras (prompt seção 17). |
| `eds` | 0,6 | **0,5** | Reflexo difuso do céu um pouco menor: o reboco ao sol já está no limite. |

O resto fica igual: `ambient`, `out`, `ess`, `tint`, `saturation` 0,10 e o `name` `GrandLine` (o `CeuWano` e o `CurrentIslandMood` dependem do nome).

## 3. Bloom e SunRays (topo do `CeuWano`)

Fique com o plano: Bloom Intensity 0,35, Size 24, Threshold 1,6; SunRays 0,04 / 0,12. Com o sol atrás de quem chega, os SunRays quase não aparecem nas visadas principais, e isso é desejado (sem véu sobre a arquitetura).

O que fica Neon e aceso **de dia** (medido no .blend, `op_lights.neon_report`):
- papel das lanternas `Glass_OP_Lantern`: 455 studs²;
- núcleo/estrela do summon: `Summon_OPStar_Glow` 232 + `Summon_Blue_Glow` 47;
- portão OPM: `P_Gold_Glow` 824 + `Energy_Core_OnePunchMan_Glow` 280 + `P_Red_Glow` 33.

`Window_OP_Warm` (5003) e `Crystal_SumPortal_Glow` (588) são SmoothPlastic no Roblox: não fazem bloom. Se no Play o dourado do portão OPM estourar mais que a estrela do summon (hierarquia sol > summon > castelo), o ajuste é no limiar do bloom do `CeuWano` (1,6 → 1,8), não nas cores.

## 4. Conferência no Play (área 5, cabeça da ponte)

1. Rode `print(game.Lighting:GetSunDirection())`. O esperado é ≈ (0,68; 0,70; −0,23), com tolerância de 0,05.
2. Olhando o castelo do início da ponte e do topo da escadaria, a **fachada sul da torre** deve estar ao sol, com a sombra dos beirais para baixo e para a direita.
3. Na praça ao sol, o reboco do castelo e a laje mais clara devem ficar **abaixo do branco puro** (sem halo de bloom nas paredes). Se chapar, baixe `brightness` 0,1 por vez.
4. As luzes de dia são 8:
   - summon (4): `L_OPSum_Core` Range 12,6 / Brightness 0,71, `L_OPSum_Star` 10,7 / 0,56, `L_OPSum_Lamp_L/R` 7,2 / 0,38;
   - salão (3): `L_OPCas_Hall_1..3`, Range 18 / Brightness 0,69 (override de interior);
   - casa de chá (1): `L_OPCap_Int_Cha`, Range 14 / Brightness 0,60 (**override novo**, `export_op.INTERIOR_LIGHTS`).

   As 57 `NightOnly` (janelas, lanternas, tōrō) ficam apagadas. A área é dia fixo e o `CeuWano` não as liga.
5. Saindo de Wano, `GeographicLatitude` volta ao valor base (22) pelo tween do `[OP]`.

## 5. Emissores que o `op_vfx` grava (para o `pos_montagem` não listar como "sem receita")

São 12 `FX_*` com `vfx='emissor'`, todos lidos pelo `receita()` do `OnePieceIsland.lua` sem mudança. Os padrões `^FX_Fall_.+_Lip/Step/Base$` já aceitam nomes com letra.

| Marcador | O quê | rate × vida | Dist |
|---|---|---|---|
| `FX_Petals_Tree` (reposto) | Caixa sob o lobo oeste da copa: subida do castelo e oeste do pátio | 10 × 11 | 320 |
| `FX_Petals_TreeRoots` (novo) | Caixa sob o lobo leste: raízes e base da árvore | 8 × 11 | 260 |
| `FX_Petals_Plaza` (novo) | Metade norte da praça, 5–22 acima do piso, vento para a ponte | 16 × 8 | 260 |
| `FX_Petals_Street` (novo) | Rua de chegada e pátio do torii | 5 × 8 | 160 |
| `FX_Fall_Castle_Lip/Step/Base` | Crista, degraus de espuma e pé da cachoeira do castelo | 2 / 6 / 10 | 260 / 240 / 260 |
| `FX_Mist_CastleFall` | Névoa baixa da bacia do adro (transp 0,9) | 1 × 10 | 220 |
| `FX_Fall_E_Lip/Base` | Queda leste → enseada | 1,5 / 6 | 300 / 420 |
| `FX_Fall_W_Lip/Base` | Queda oeste → mar | 1,5 / 6 | 300 / 420 |

- **Pétalas:** seguem a linguagem das aprovadas do lobby Murim:
  - cor 255,172,198 → 248,140,170;
  - tamanho 0,36, queda −1,1, giro ±60 (`rotv`);
  - textura `petala`, que é a reserva do `TEX`.
- **Fumaça:** nenhuma. A capital não tem chaminé nem cozinha com fogo.
- **Peças móveis:** foram conferidas sem mudança.
  - `VFX_OP_Wheel`: 4 rpm, eixo −X. A pá de baixo anda a favor da correnteza (−Y local), com aro a 2,7 studs/s.
  - `VFX_OPSUM_*`: 4 peças, todas no pivô da estrela.

**Opcional (M5, não é sistema novo):** dar `IlhaPulso` + `Cor0` ao Neon do núcleo do summon (`Summon_OPStar_Glow` / `Summon_Blue_Glow`), como a DS faz com a brasa da fornalha. O `ILHAS_Cliente` já anima a tag.
