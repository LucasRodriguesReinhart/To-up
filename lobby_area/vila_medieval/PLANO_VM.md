# Lobby Vila Medieval: plano técnico (V0)

A fonte de verdade é o `SPEC.md`, aprovado pelo usuário em 08/10. Este plano trava a planta em coordenadas reais do place. Os números de código ficam em `vm_layout.py`.

## 1. Eixos e cotas

**Eixos (coordenadas Roblox, origem do place, 1 BU = 1 stud):**
- X aponta para leste.
- Z aponta para o sul: as ilhas seguem em +Z pela ponte.
- Y aponta para cima.
- No Blender vale `(X, −Z, Y)`, o mesmo mapeamento do `export_roblox` compartilhado. A forja fica ao norte (−Z) e o spawn olha −Z para ela.

**Cotas do piso (Y):**

| Piso | Y |
|---|---|
| Praça, ruas, pátio dos portais e ponte da Ilha 1 | 6,0 (igual ao piso 6 da Vila da Folha) |
| Grama do sul | 5,8 |
| Rua norte, largo e forja | 7,0 (contrato do Ignis) |
| Terraço do spawn | 9,6 (5 degraus de 0,72) |
| Loja e palco do ranking | 6,4 |
| Terraço dos portais | 7,2 (2 degraus de 0,6) |
| Espelho d'água | 2,6 |

O `IslandTravel` só salva posição segura com HRP abaixo de 18, e o ponto mais alto andável (o spawn, com HRP em 12,9) cabe nisso.

## 2. Planta

O hub tem cerca de 390 × 280 studs, sem contar a ponte. O contorno do platô é `PLATEAU`.

| Elemento | Onde (Roblox) | Cotas e medidas |
|---|---|---|
| Spawn (terraço octogonal) | x −20..20, z 88..112; nascimento em (0, 9,6, 94) | Escadaria de 20 de largura, de z 80 (pé, 6,0) até z 88 (9,6). Mureta em volta. |
| Correio | (−14, 9,6, 100), no terraço | – |
| Praça central | centro (0, 50), raio 36 | Medalhão rebaixado 0,12, raio 9: picareta cruzando a bigorna, em bronze. Sem colisão própria. |
| Rua do eixo, sul | x ±9, z 15 → 1 | Casas S1W e S1E. Casas PNW e PNE nos cantos da praça. |
| Canal | z −18..−6, x −129..166 | Muros de 1. Mureta de 1,1. Cachoeiras nas pontas. |
| Ponte de pedra | x ±9 (guarda-corpo até ±11), z 1 → −21 | Rampas 6,0 → 7,4 → 7,0, com arco. |
| Rua norte e largo da forja | x ±9, z −21..−36; largo de x −26..24, z −36..−50 | Casas N1W, N1E, N2W e N2E. |
| Forja (salão aberto) | x −16..14, z −50..−77 | Pilares em x −17,2 e 15,2. Verga e tirantes acima de Y 33. Oitão enxaimel com cumeeira até cerca de 51. |
| Forja (alas) | oeste: x −34..−16; leste: x 14..31; ambas z −52..−88 | Base de pedra até 10, andar enxaimel até 19, telhado de 50°. |
| Chaminé | (0, −86) | Base de 13 × 13 até 34; fuste de 11 → 8,6; topo em Y 94 com brasa. |
| Levada e roda d'água | levada x 33..39, z −19..−84; roda com centro (36, 9,4, −66), r 7,5 | A roda fica no flanco da ala leste e gira o martelo-pilão no V3. |
| Loja de mochilas (leste) | x 62..90, z 30..56 | Porta na face oeste em z 43 (6 × 9). Paredes de 16. Vitrines em balanço e toldo. Balcão em x 74..76, vendedor em (78, 43). |
| Ranking Top 100 (oeste) | GroundPivot do GlobalTop100 em (−84, 6,4, 20) | Olha a direção (0,40; 0,92), para a praça e a rua oeste. Palco de 58 × 20; salão da guilda enxaimel atrás. |
| Rua oeste | (−30, 52) → (−104, 70), 14 de largura | Casas R1 e R2. |
| Pátio dos portais | disco de raio 40 com centro (−128, 72), a 6,0 | Terraço em semicírculo de r 40..74 a 7,2. Os 6 portais aprovados ficam em r 56, a 31° um do outro, olhando o centro. |
| Rua curva sudeste | (24, 74) → (50, 146), 14 de largura | Casas dos dois lados: E1–E3 e W0–W2. É o enquadramento da ref_01. |
| Portão | (50, 6, 148), vão de 18 | Torres de pedra com chapéu de telha. Verga de madeira com telhadinho. |
| Ponte da Ilha 1 | (50, 146) → (45, 177) → (17, 202) → (0, 213) | 16 de largura, piso 6,0, muretas e pilares. Patamar em x ±12, z 213..222. |
| Colinas, pinheiros e montanhas | colinas a 150–300 do centro; montanhas a 560–860 | As montanhas são SKYLINE e ficam fora do setor sul, que é o das ilhas. |

**Portais** (marcadores `PORTAL_<tema>`, espiral com centro em Y 18,4):

| Portal | Tema | Área | Posição (x, z) |
|---|---|---|---|
| 1 | Naruto | 1 | (−140, 126) |
| 2 | Dragon Ball | 2 | (−166, 112) |
| 3 | Shadow Garden | 3 | (−181, 87) |
| 4 | Demon Slayer | 4 | (−181, 57) |
| 5 | One Piece | 5 | (−166, 32) |
| 6 | One Punch Man | 6 | (−140, 18) |

Quem entra pelo leste vê os portais do mais fácil (esquerda) ao mais difícil (direita).

**Desvio consciente da planta aprovada:** o portão fica em x 50, e não em x ≈ 120 como no desenho. A ponte precisa encostar reta na praça de chegada da Vila da Folha, em (0, 6, 222) com x ±12. Por isso a rua continua saindo da praça para o sudeste, e a ponte faz a curva de volta para x 0.

## 3. Contratos: nome → onde fica no modelo novo

A raiz continua sendo `workspace.LOBBY_FORJA`. O montar gerado cria e mantém:

| Contrato | No modelo novo |
|---|---|
| `LOBBY_FORJA` (Model) | Raiz do montar. Atributo `EXPORT_ID`. |
| `Santuario.Portal1..6` | Folder filho direto da raiz. Cada `PortalN` é um Model com `Disco` (Part de 14 × 15 × 1,2, invisível, sem colisão, `CanTouch`) e atributo `AreaId` = N, 1,3 à frente de cada espiral. Remove qualquer `PortalKonoha`. O `Main` liga o Touched e o `AudioWorld` reconhece `Portal%d`. |
| `GlobalTop100` | A geometria é do Top100Builder/Controller. O montar só grava `root:SetAttribute('Top100Origin', CFrame)` e, se o modelo existir, faz `PivotTo` para (−84, 6,4, 20) com o +Z local voltado aos visitantes. A envoltória de 54 × 14,4 × 26,5 fica livre (QA). |
| `LobbyRevision` | Folder mantido (o `LobbyServices` exige o filho). Atributo `VilaMedieval = EXPORT_ID`. |
| `GAMEPLAY_MARKERS` | `SPAWN_Lobby`, `SPAWNLOBBY_Part`, `LAYOUT_*` (Spawn, Shop, ShopFacing, Ignis, PortalIsland), `MAILBOX_Correio`, `NPC_Ignis`, `INTERACT_Ignis`, `PLAYER_INTERACT_Ignis`, `IGNIS_Anvil`, `LETREIRO_Ignis`, `NPC_Shop`, `INTERACT_Shop`, `PLAYER_INTERACT_Shop`, `PADLOJA_Shop`, `DOOR_Shop`, `TOP100_Origin`, `LOBBY_GATE_Ilha1`, `ISLE_LINK_Area1`, `ForgeChimney`, `VFX_*`, `REBIRTH_Spot`, `PORTAL_<tema>` (6). São 33 no total. |
| `VOID_CATCH` | Part de 470 × 4 × 420 com centro em (−28, −25, 48) e 21 Attachments seguros: praça, ruas, loja, ranking, pátio, cada portal, portão e ponte. |
| `COLLISION` / `LIGHTS` | Parts invisíveis (374) e luzes (16 de dia, todas dos portais). |
| `LOBBY_FORJA_Servidor` | Regerado pelo montar com a mesma regra de hoje (grupos `Personagens`/`SoVisual` e rede de quedas). |
| `workspace.NPCs.Ignis` | Não é tocado. Root em (−0,9; 7; −60,7) olhando +Z, bigorna em z −55,7. A envoltória livre fica em X −9,9..6,1, Y 7..31, Z −64,7..−52,7, e o chão livre e plano a 7 vai de z −52,7 a −40 (QA: livre). |
| `npc vendedor ` / `LojaPrompt` / `LojaMochilas.PadLoja` | O vendedor vai para (78, 6,4, 43) olhando −X; o PadLoja para (69, 6,45, 43), só como marca. |
| `workspace.MailBox` | (−14, 9,6, 100). |
| `Mystical Spawn Point.SpawnLobby` | Placa em (0, 9,7, 94). |
| `workspace.Rebirth` (sugestão) | (−26, 6, 74), canto sudoeste da praça. |

## 4. Valores novos do `ServerScriptService.Core.LobbyLayout`

São posições de HRP, como hoje.

```lua
return table.freeze({
 Spawn=Vector3.new(0,12.9,94),
 Shop=Vector3.new(69,9.9,43),
 ShopFacing=Vector3.new(78,9.9,43),
 Ignis=Vector3.new(-0.9,10.5,-46),     -- ~15,1 do belly (prompt 18 / servidor 22)
 PortalIsland=Vector3.new(-112,9.5,72) -- entrada do patio dos portais
})
```

**Scripts que ainda precisam de ajuste no Studio (leitura do lead):**
- **`ServerScriptService.CircularGeometry`:** exige exatamente 1783 MeshParts em `LOBBY_FORJA.CircularAuthoredGeometry`. É preciso trocar a contagem e a revisão, senão o `MiningLoading` só libera no timeout de 40 s.
- **`StarterPlayerScripts.PetsSeguidores` (linhas 302–305):** os centros fixos dos serviços passam a ser Ignis (−0,9, 10,5, −46), loja (69, 9,9, 43) e ranking (−84, 6,4, 20).
- **Caixas de `IslandTravel.lobbyAt` e `IslandVisibility`:**
  - O canto de grama atrás dos portais (x < −190 e z > 120, por exemplo (−196, 137)) fica fora das duas caixas. Pode-se aumentar a caixa 2 até z 160 ou cercar esse canto.
  - O resto do platô e a ponte ficam dentro (a ponte entra na área 1 em z > 190, igual a hoje).

## 5. Orçamento

**Alvo do lobby:** até 450 mil tris e 600 MeshParts estáticas, mais uma reserva de VFX de 12 mil tris e 24 peças. Até 110 materiais, 300 MeshParts com sombra, 30 luzes de dia e 900 colisões.

**Teto por dono (tris / MeshParts):**

| Dono | Teto |
|---|---|
| terrain | 40k / 60 |
| backdrop | 12k / 6 |
| town | 80k / 110 (V2b; era 40k / 50) |
| houses | 160k / 140 (V2b; era 90k / 180) |
| forge | 60k / 60 |
| services | 40k / 50 |
| portals | 110k / 160 |
| exit | 18k / 24 |
| water | 6k / 12 |
| vegetation | 40k / 50 |

**Medido no export V0 (`2856eacf`):**

| Medida | Valor |
|---|---|
| MeshParts | 349 |
| Tris | 104,6k |
| Materiais | 91 |
| Colisões | 374 |
| MeshParts com sombra | 164 |

**Portais:** os 6 aprovados já custam 71 MeshParts e 51,8k tris.

**V2b (a vila, `vm_town.py`), export de teste `2eb1e8b9` (com a forja do V2a):** 392 MeshParts / 600, 434k tris / 450k, 100 materiais / 110, 254 com sombra, 19 luzes de dia. Por dono: houses 155k / 103 MP, town 77k / 90 MP, services 31k, exit 13k, portals 63k (portais 52k + pátio 11k), terrain 23k. A subida de houses (90k → 160k) e town (40k → 80k) é acréscimo pontual: 6 casas do trecho V1 (50k) + 18 casas do kit lod 1 + 11 casas de fundo baratas (~1,5k), juntadas por quadra (`VM_House_Q<quadra>`, ≤ 10 materiais) e com as faces das paredes-meias apagadas (ficam dentro da vizinha). O teto da ilha não mudou; sobram ~16k tris para o V3.

**V3a (vegetação + props, `vm_veg.py` / `vm_props.py`):** o lead autorizou subir o teto da ilha para 520k tris / 600 MeshParts e criou os donos `vegetation` (≤ 55k / 40) e `props` (≤ 25k / 25) em `vm_layout.BUDGET_OWNER`; prefixo `VM_Prop_` → `props` no `vm_lib.OWNER_PREFIX`. Export de teste `6c3d0295`: 427 MeshParts, ~500k tris, 101 materiais (+1: `Leaf_VM_Light`), 271 com sombra; vegetation 53,6k / 30 MP, props 23,3k / 20 MP. Substitui a vegetação do blockout (`VM_Veg_Trees_*`) e do V2b (`VM_Veg_Court`). Fica fora da levada, da roda, da pluma da chaminé, das quedas do canal, do largo e das envoltórias (caixas de exclusão do `vm_veg.Probe`).

**V2b, desvios conscientes:** escadaria do spawn alargada de x ±10 para x ±13 (colisão refeita: rampa + meia pisada + banzos); barreiras `COL_Canal` refeitas com as 2 pontezinhas andáveis (x −116 e x 100); a ponta oeste da envoltória do GlobalTop100 entra no disco do pátio (−72° a −40°): ali não há mureta.

**Casas:** cada casa sai com cerca de 9 materiais, o que dá 162 MeshParts para 19 casas. No kit final, os materiais por casa ficam limitados a 6. As casas de fundo se juntam por quadra (um objeto por quadra) para não estourar as 600.

## 6. Kit

Peças por medida de avatar (5,2):
- portas de 4 × 6,4;
- degraus de 0,6 a 0,8;
- térreo de pedra de 7;
- andares de 6 em balanço de 0,8;
- telhado de 50–55°;
- chaminés de 2 × 2.

| Família | Peças |
|---|---|
| Casa enxaimel | Soco escuro, térreo de pedra com quinas de cantaria, andares em balanço (2–3) com frechais, montantes e X/diagonais, janelas recuadas, oitão enxaimel, telhado de duas águas com cumeeira, chaminé e água-furtada. As variações saem de largura, profundidade, andares, eixo da cumeeira, reboco (creme, ocre ou pêssego), telha (A/B) e chaminé. |
| Rua | Paralelepípedo, meio-fio, poste de ferro com lanterna (NightOnly no V3), carroça com roda, barris e caixotes. |
| Forja | Pilares e verga grossos, tirantes, oitão, alas, chaminé com brasa, fornalha com coifa, roda d'água, suportes de picaretas, sacos de carvão, lingotes e placa da bigorna. |
| Vegetação | Pinheiro estilizado (3 cones), árvore de copa redonda (3 esferas), colinas com pinheiros e montanhas com neve. |

## 7. Paleta e luz

**Paleta:** é a cor que o Roblox recebe, sem textura e sem calibração.

| Material | RGB |
|---|---|
| Telha | 200,110,60 / 182,96,54; cumeeira 150,78,44 |
| Reboco | 235,225,200 (teto de valor, nunca branco); 226,208,176; 232,210,186 |
| Viga | 74,50,36 |
| Tábua | 128,88,58 |
| Pedra (V2b: esquentada, a validação do V1 no Roblox saiu fria/azulada) | 150,143,132 / 108,102,96; cantaria 178,170,154; kit 160,148,130 / 140,136,128 |
| Paralelepípedo (V2b) | 198,180,150 / 174,158,132; meio-fio 152,140,122; junta 112,100,86 |
| Grama | 98,168,62 |
| Água | 64,150,190 |
| Bronze | 176,138,70 |
| Neon só na brasa e na boca da fornalha | 255,128,40 |

**Luz:** dia, com sol a sudoeste e alto (cerca de 50°) e sombra suave. No Roblox, o perfil do lobby fica no `AreaAtmosphere` (o Lighting do Edit vira a base do lobby) com o `LobbyBloom` em 0,22. O montar traz um `APLICAR_LIGHTING` opcional.

## 8. Câmeras de QA

Ficam em `vm_layout.cams()`:
- **`CAM_VM_Ref_01`:** enquadramento da ref_01. Fica na rua curva do sudeste, em (53, 13, 140), olhando a praça. Mostra casas dos dois lados, a rua curvando e a chaminé da forja ao fundo.
- **Altura do jogador:** `CAM_VM_P_Spawn`, `P_Praca`, `P_Rua`, `P_Forja`, `P_Loja`, `P_Ranking`, `P_Portais`, `P_Saida`.
- **Aéreas:** `CAM_VM_Air_Sul`, `Air_Oeste`, `Air_Norte`.
- **`CAM_VM_Plan`:** ortográfica no mesmo recorte da planta aprovada (1200 × 1140 px, 0,316 stud/px).

## 9. Pipeline

Atalhos em `run.sh` (build, qa, render, export, sheets, all).

| Arquivo | Função |
|---|---|
| `vm_layout.py` | Planta, contratos, rotas, câmeras e orçamento (sem bpy). |
| `vm_lib.py` | Põe `forja_mineradora` no `sys.path` (somente leitura, sem pycache). Paleta, regras Roblox, conversão Roblox↔Blender, colisão por coordenada Roblox, casa enxaimel, árvores e boneco. |
| `vm_col.py` | Piso andável e barreiras. |
| `vm_core.py` | Marcadores de contrato, volumes de QA (não exportados) e prévias (golem, Top100, Ilha 1). |
| `vm_blockout.py` | Zonas (terreno, cidade, casas, forja, loja, ranking, pátio, saída, água, vegetação). |
| `vm_portals.py` | Os 6 portais aprovados (`fm_pv3_*.build` e `fm_portals.onepiece`, mesma semente do `portal_studio`), sem a escada antiga, levados por transformação rígida ao semicírculo. |
| `vm_scene.py` | Dia, câmeras e bonecos. |
| `build_vm.py` | Monta tudo. É determinístico (`noise.seed_set` e ordem fixa). |
| `vm_qa.py` | nav, env, link, markers, budget, tech. |
| `vm_render.py` | Renderiza prévia ou Roblox. |
| `vm_sheet.py` | Gera as folhas. |
| `export_vm.py` | Configura o `export_roblox` compartilhado com a identidade `LOBBY_VM` e a raiz `LOBBY_FORJA`, e acrescenta o bloco de contrato. |

## 10. Ondas

| Onda | Escopo |
|---|---|
| V1 | Trecho de qualidade: praça → ponte do canal. Inclui 2 casas do kit final (S1W de 3 andares e S1E com oitão para a rua), paralelepípedo em geometria (pedras arredondadas e meio-fio), poste e mureta do canal. Validado na **cópia** do Studio antes de multiplicar o kit. |
| V2 | Forja (a envoltória do golem continua livre), loja, ranking (palco e salão), pátio dos portais (os portais aprovados ficam como estão) e as casas pelo kit, juntando por quadra. |
| V3 | Vegetação final, props, luz do dia no `AreaAtmosphere` e efeitos: fumaça e brasa da chaminé, roda e martelo-pilão, lanternas NightOnly. |
| V4 | Integração. Export, import na cópia (backup do `LOBBY_FORJA` em ServerStorage), `LobbyLayout` e objetos soltos, `CircularGeometry`, `PetsSeguidores`, caixas do `IslandTravel`/`IslandVisibility`. Depois, Play com rotas, prompts, os 6 portais, travessia até a Área 1, quedas e FPS. |
| V5 | Auditoria na altura do jogador e finesse. |

## 11. Luz e VFX (V3b)

Arquivos: `vm_lights.py` (luzes, sol da prévia, proxies `PREVIEW_VFX_*`, câmeras `CAM_VM_L_*`) e `export_vm_vfx.py` (peças móveis e partículas). O `build_vm` chama o `vm_lights` por último; o `export_vm` gera o VFX no mesmo passe, como o `export_all` do lobby atual. Folhas em `renders/v3/luz_vfx/` (`./run.sh luz <pasta_tmp>`; contagem em `./run.sh luz-qa`).

### 11.1 Perfil de dia do lobby (área 0) para o lead

O `AreaAtmosphere` usa o Lighting do Edit como base do lobby. Então estes valores vão **no Lighting do Edit** (ou rode o `montar` com `APLICAR_LIGHTING = true`, que grava os mesmos números). O sol é o `SUN_Key` das folhas: sudoeste, alto (~50°), e `GetSunDirection()` ≈ (−0,42; 0,76; 0,50). Quem sai do spawn olhando a forja tem o sol atrás e à esquerda, então a fachada da forja e a rua norte ficam iluminadas.

| Classe | Propriedade | Valor |
|---|---|---|
| Lighting | ClockTime / GeographicLatitude | **13,929 / 53,448** |
| Lighting | Brightness / ExposureCompensation | 2,3 / −0,05 |
| Lighting | Ambient / OutdoorAmbient | (104, 100, 98) / (150, 158, 178) — sombra fria e suave; o interior da forja fica escuro e a fornalha manda |
| Lighting | ColorShift_Top / ColorShift_Bottom | (255, 238, 214) sol quente / (0, 0, 0) |
| Lighting | EnvironmentDiffuseScale / EnvironmentSpecularScale | 0,5 / 0,3 |
| Lighting | ShadowSoftness | 0,35 (sombra suave) |
| Atmosphere | Density / Offset / Haze / Glare | 0,26 / 0,12 / 0,9 / 0,1 |
| Atmosphere | Color / Decay | (196, 218, 244) / (116, 150, 198) — céu azul; as montanhas (560–860) ganham profundidade sem véu branco |
| Sky | CelestialBodiesShown / SunAngularSize / MoonAngularSize / StarCount | true / 14 / 11 / 0 (céu padrão do Roblox; nada de skybox escuro) |
| Bloom (o filho `Bloom`) | Intensity / Size / Threshold | 0,22 (o `LobbyBloom` força) / 24 / 1,6 — o reboco creme (235, 225, 200) não estoura |
| SunRays | Intensity / Spread | 0,03 / 0,12 |
| ColorCorrection (base, no Edit) | Brightness / Contrast / Saturation / TintColor | 0 / 0,06 / 0,08 / (255, 250, 242). O `IslandAtmosphere` do `AreaAtmosphere` fica neutro no lobby e estes valores somam com ele. |
| Terrain.Clouds (opcional) | Cover / Density / Color | 0,45 / 0,55 / branco (as nuvens da ref_01) |

Nas ilhas, o `AreaAtmosphere` troca `ClockTime`, `Brightness` e os ambientes por perfil. Latitude, EDS/ESS e ColorShift_Bottom só são trocados pelos perfis com as chaves `[OP]` (`lat`, `eds`, `ess`, `csb`). Se uma ilha sem essas chaves ficar com a luz estranha depois da troca do Edit, devolva `GeographicLatitude = 22` nela (o próprio `montar` lembra disso).

### 11.2 Luzes

| Grupo | Nomes | Roblox (alcance / brilho) | Dia |
|---|---|---|---|
| Boca da fornalha (**a mais forte**) | `L_Hearth_Fire_VM` | 24 / 2,2, com sombra, (255, 122, 41) | sim |
| Portais e pads (sem mudança) | `L_Portal_*`, `L_P_*` | 14 / 1,0 e 12,6 / 0,71 | sim |
| Loja por dentro | `L_VM_ShopIn_A/B` | da energia | sim |
| Lanternas dos postes (kit) | `L_VM_Lamp_*` (34) | 14 / 0,8: poça de luz no chão, sem estourar | NightOnly |
| Janelas acesas | `L_VM_Night_Win_*` (30) | 7 / 0,9, (255, 178, 98): a luz fica 1 stud à frente da vidraça e a face do vidro acende | NightOnly |
| Câmara de fogo da chaminé | `L_VM_Night_Chimney` | 18 / 1,2 | NightOnly |

São **19 luzes de dia** (teto 30) e 65 NightOnly. Os overrides ficam em `vm_lights.RBX`, e o `export_vm` os aplica por cima da conta de energia do `export_roblox`. Como o lobby é de dia fixo, as NightOnly só acendem se algum ciclo/céu ligar o atributo `NightOnly`, como o `CeuNatagumo` faz nas ilhas.

As janelas escolhidas são vidraças do kit voltadas para as rotas (spawn, praça, ruas sul/norte/oeste, rua curva, loja), a pelo menos 10 studs umas das outras. Não há material novo: a vidraça é a junta escura `Stone_VM_Mortar`.

### 11.3 VFX (mesmo mecanismo do lobby atual)

O `export_vm_vfx.py` importa o `export_vfx.py` compartilhado (só leitura) e reaproveita a separação por ilhas, as peças móveis com 1 material, o orçamento, o FBX, o `SETUP_LUA` e o `CLIENT_LUA`. Ele troca:
- **as fontes:** `VM_Frg_Wheel` (roda + eixo + 3 cames, gira em +X no pivô (36; 9,4; −66), 6 rpm) e `VM_Frg_TripHammer` (pivô (24,5; 12,2; −73,5); o ângulo positivo sobe a cabeça 2,6 studs; 3 golpes por volta da roda). Os dois são objetos próprios do `vm_forge`, então a cópia fixa não existe;
- **a fase dos cames:** medida na geometria (30°/150°/270°). O came passa da vertical (95°) no instante em que o martelo cai. Folga cabo/came em repouso: 0,02 stud;
- **os efeitos:** saem dos marcadores do `vm_forge`: fogo da boca, pluma da chaminé (raio 3,6, Y 96,7), faíscas da bigorna do Ignis (evento `ignis` = `IgnisImpact` do golem) e do pilão (evento `martinete`), vapor da têmpera, respingos da roda (a levada corre para o norte), as 2 cachoeiras das pontas do canal, as correntes (canal para as pontas e levada para o norte) e os 6 portais (espiral em SurfaceGui virada para o centro do pátio, partículas sugadas, aro Neon);
- **o que sai:** o carrinho de mina (a montagem apaga o molde `MineCart`), os respiros e a fumaça das casas (sem marcadores).

Arquivos do export: `LOBBY_VFX_MOVING_<ID6>.fbx` (5 malhas, 1,2k tris; teto 24 / 12k), `vfx_lobby_vila_medieval.lua` (montagem) e `vfx_lobby_vila_medieval_client.lua` (o LocalScript `VFX_Lobby_Forja_Client` com os dados da vila e o gancho `IgnisImpact`).

Tags e atributos são os de hoje: `FORJA_Spin/Hammer/Pump/Swirl/Pulse/Flicker/Burst/Emitter` e `VFX_Home/Pivot/Axis/Speed/Phase/CamPhase/Cams/Rest/Lift/Event/Base/BaseColor/MaxDist`. `ReplicatedStorage.LOBBY_FORJA_VFX` mantém o `Evento` e o `IgnisImpact`, e a montagem não apaga a pasta. A versão do protocolo continua `vfx-forja-2`; o atributo `VFX_Lobby = "VilaMedieval"` marca a vila.
