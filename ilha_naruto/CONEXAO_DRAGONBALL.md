# Interface entre ilhas — Ilha 1 (Naruto) → Ilha 2 (Dragon Ball)

A Ilha 1 termina fisicamente numa **cabeceira de ponte** depois do portão de compra Dragon Ball. A Ilha 2 (e
qualquer ilha seguinte) se encaixa nesse ponto. A ponte nunca termina quebrada no vazio.

```
VILA (T1, cota 16,2) → caminho → PONTE DE SAÍDA (96 studs, largura 18, arcos sobre o vale leste)
   → ILHOTA → PORTÃO DE COMPRA DB (vão 16 × 18) → patamar → CABECEIRA (ISLAND_NEXT_ANCHOR)
```

## 1. Valores da âncora

| | referencial de projeto (Blender, `il_layout`) | Roblox (depois do `export_ilha`) |
|---|---|---|
| `ISLAND_EXIT_Naruto` (início da ponte) | (96,0; 96,0; 16,2) | (−96,0; 16,2; 516,0) |
| `GATE_DB` (eixo do portão) | (172,37; 172,37; 16,2) | (−172,37; 16,2; 592,37) |
| `GATE_DB_EXIT` (12 depois do portão) | (180,85; 180,85; 16,4) | (−180,85; 16,4; 600,85) |
| **`ISLAND_NEXT_ANCHOR`** | **(192,17; 192,17; 16,2)** | **(−192,17; 16,2; 612,17)** |
| rumo (direção de avanço) | 45° (nordeste do projeto) | vetor (−0,7071; 0; +0,7071) |

A âncora em si:

| | valor |
|---|---|
| largura do tabuleiro | 18 studs (padrão de todas as passagens entre ilhas; `il_gate_std.DECK_W`) |
| cota do piso | 16,2 (topo do tabuleiro, = nível T1 da Ilha 1) |
| altura livre mínima | 22 studs (vão do portão 18 + 4) |
| alinhamento | a âncora é o **centro da borda** do piso da cabeceira. O eixo de avanço aponta para FORA da Ilha 1 |
| guarda provisória | `EXIT_AnchorGuard` (2 correntes entre os pilones, Model atômico) + `COL_ExitAnchorGuard_001` (parede invisível) impedem cair da cabeceira enquanto não há Ilha 2. Saem do export com o atributo `next_island_guard = true` e a tag `GuardaProximaIlha`: **a integração da Ilha 2 apaga essas peças** quando a ponte seguinte encosta |

No Roblox, o marcador `ISLAND_NEXT_ANCHOR` é uma Part invisível em `ILHA_NARUTO.GAMEPLAY_MARKERS` com os atributos:
- `width`, `deck_z`, `clear_h`, `next_area`;
- `heading_deg` (plano XZ do Roblox) e `fwd_x`/`fwd_z`, que são o vetor de avanço.

A orientação da Part segue a convenção do export: o eixo Y do Blender vira o `UpVector` da Part. Use os
atributos `fwd_x`/`fwd_z` e não o `LookVector`.

## 2. Como encaixar a Ilha 2

A Ilha 2 precisa de um marcador de chegada `WORLD_FROM_PREV`, no centro da borda do piso da ponte de chegada dela,
com avanço apontando para DENTRO da Ilha 2. É o equivalente ao `WORLD_FROM_LOBBY` desta ilha.

Regra de encaixe (a mesma para toda a corrente de ilhas):
0. Apagar a guarda provisória: `for _, d in CS:GetTagged('GuardaProximaIlha') do d:Destroy() end`.
1. A posição de `WORLD_FROM_PREV` (Ilha 2) coincide com a de `ISLAND_NEXT_ANCHOR` (Ilha 1).
2. O avanço de `WORLD_FROM_PREV` tem a MESMA direção do avanço de `ISLAND_NEXT_ANCHOR`.
3. Largura 18 e cota do piso iguais. Se a Ilha 2 tiver outro nível, a própria ponte de chegada dela sobe ou desce
   em degraus de no máximo 0,8.

Em Luau, com `fwd` do atributo e `entradaLocal` = CFrame de `WORLD_FROM_PREV` relativo ao pivô do modelo da Ilha 2:

```lua
local a = ilha1.GAMEPLAY_MARKERS.ISLAND_NEXT_ANCHOR
local fwd = Vector3.new(a:GetAttribute('fwd_x'), 0, a:GetAttribute('fwd_z'))
local ancora = CFrame.lookAt(a.Position, a.Position + fwd)          -- LookVector = avanco
ilha2:PivotTo(ancora * entradaLocal:Inverse())                        -- entradaLocal com LookVector = avanco da Ilha 2
```

No Blender vale a mesma regra. O referencial de projeto de cada ilha tem a entrada ao sul (−Y) e o avanço em +Y.
A matriz de mundo da Ilha 2 é:

```
W2 = T(âncora_mundo) · Rz(rumo_mundo − 90°) · T(−entrada_local)
```

- `âncora_mundo`: a âncora da Ilha 1 já levada ao mundo por `export_ilha.WORLD`, no Blender do lobby. Aqui é
  (−192,17; −612,17; 16,2).
- `rumo_mundo`: o rumo da âncora no mundo. Aqui 45° + 180° = 225°, então a Ilha 2 gira 135° em Z.
- `entrada_local`: a posição de `WORLD_FROM_PREV` no projeto da Ilha 2.

## 3. O portão Dragon Ball (bloqueio)
- Padrão `il_gate_std`, o mesmo das outras ilhas: vão 16 × 18, interação 7 antes do plano da barreira, saída 12
  depois, âncora do painel de preço `PURCHASE_UI_ANCHOR_DB` DENTRO do vão (z 14, 2,5 à frente da barreira).
- Moldura "moon gate" (ref 13): painel de pedra no retângulo do vão com furo circular r 8,2; a barreira de energia é
  circular. Com o portão aberto passa-se pelo círculo (soleira de 0,8; na altura do joelho a passagem tem ~8 nas
  bordas, 16 no eixo).
- **LOCKED** (padrão), com três partes marcadas pela tag `PortaoCompra`:
  - `GATE_DB_Barrier` (energia laranja, Neon, Transparency 0,2) e `GATE_DB_Lock` (cadeado), com atributos
    `gate`/`gate_part`;
  - `COL_GateDBLock_001`, uma Part invisível que bloqueia a passagem.
- **UNLOCKED:** `require(game.ReplicatedStorage.PortoesCompra).Estado('DB', true)`.
  - No servidor, vale para todos.
  - Num LocalScript, vale só para o jogador que pagou: o mesmo esquema do `ParedesClient` atual.
  - A barreira e o cadeado ficam invisíveis e a colisão sai. O efeito de abertura sai no marcador `GATE_DB_OpenFX`.
- **UI:** `GATE_DB_INTERACT` é o lugar do ProximityPrompt (raio 10) e `PURCHASE_UI_ANCHOR_DB` é onde vai o
  BillboardGui de preço. Não há placa 3D com preço.

## 4. O que o jogo atual precisa mudar ao trocar a Área 1 por esta ilha
- **Mundo em linha reta:** hoje as áreas ficam em Roblox z = 420·n. A Área 2 (Vale Capsule) está em z 840, e o
  `IslandTravel` decide a área pela faixa de z (`floor((z+210)/420)`).
  - A saída desta ilha fica a NORDESTE e a âncora em (−192; 16,2; 612).
  - Quando a Ilha 2 nova for encaixada aqui, ela sai da linha reta.
  - O `IslandTravel` precisa passar a decidir a área por região (caixa ou polígono por ilha, por exemplo com
    `BoundsHalfSize` e o centro de cada ilha), não só por z.
- **`Core.Paredes`:** a parede de custo entre as Áreas 1 e 2 (Parede2, z 630) fica sem função, porque este portão a
  substitui. Os nomes do contrato do `ParedesClient` (Barreira/Brilho/Zona/…) podem ser ligados às peças com a tag
  `PortaoCompra`.
- **Ponte do lobby:** nada muda. O `WORLD_FROM_LOBBY` desta ilha cai exatamente na ponta do patamar da ponte do
  lobby, em Roblox (0; 6,2; 222), com a mesma largura (24) e a mesma cota.
- **Minério:** os pontos `ORE_<RARIDADE>_<nn>` (28/16/8/2) e a zona `GP_Zone_Pit` ficam em `GAMEPLAY_MARKERS`.
  - O `SpawnMinerio` já aceita zonas por marcador (Konoha).
  - As pedras `MINE_Ore_*` do Blender são só prévia: ficam FORA do export (o jogo gera as rochas nos `ORE_*`).
