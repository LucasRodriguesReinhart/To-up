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
| town | 40k / 50 |
| houses | 90k / 180 |
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
| Pedra | 124,130,142 / 96,100,112; cantaria 160,158,150 |
| Paralelepípedo | 178,166,146; meio-fio 140,132,120 |
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
