# Área 2 — Vale Capsule (Dragon Ball) · Documento de Level Design

Área do jogo: `Config.Areas[2]` (tema `ki`, centro `(1600,100,0)`), construída no Blender com o mesmo
pipeline da Vila da Folha (primitivas compatíveis com Part → script Luau colado no command bar →
`ServerStorage.DragonBallArea` → `Core.CapsuleIsland` clona na Área 2).

## 1. Análise das referências

Fontes: Capsule Corporation / West City (Dragon Ball Wiki), Namek (Dragon Ball Wiki), Gizard Wasteland
(Vegeta Saga; "Rocky Field" do FighterZ), mapas do Dragon Ball Z: Kakarot, arenas do Tenkaichi Budokai.

| O que faz alguém dizer "isso é Dragon Ball" | Regra de design no mapa |
|---|---|
| **Capsule Corp.**: cúpula branca gigante, faixa azul, letreiro grande, janelas redondas, prédios anexos arredondados, antenas | Landmark principal = *Complexo Capsule* (cúpula de 64 studs + torre-cogumelo + refinaria) num platô elevado, visível da chegada |
| **West City**: arquitetura "pílula" — domos, cápsulas deitadas, torres finas com bulbo no topo, cores pastel (creme, amarelo, azul), carros flutuantes | Kit modular de casas-domo, casas-cápsula, apartamentos cilíndricos com varandas em anel, torre-cogumelo, garagem arqueada |
| **Paisagens de batalha**: colunas/mesas de rocha verticais com topo plano e estratos horizontais, cor ocre-laranja, arcos naturais, crateras de impacto | Landmark natural = *Cânion das Colunas* (pilares de 60–110 studs, arco natural sobre a trilha) + *Cratera* com pod caído |
| **Natureza Toriyama**: árvores "bola" (copa redonda e fofa), grama verde saturada, lagos azuis, cachoeiras, nuvens de algodão | Árvores-bola em 3 escalas, árvore Ajisa (tronco fino + bulbo), lago com cachoeira, nuvens estilizadas em volta da ilha |
| **Símbolos**: esferas laranjas com estrelas vermelhas, cápsulas Hoi-Poi, nave-esfera de gravidade, pods redondos, arena de torneio com piso quadriculado | Esferas só no Santuário do Dragão (invocação); cápsulas como props de carga; nave-esfera no platô; pod na cratera; arena de torneio = arena do chefe |
| **Paleta**: céu azul, verde vivo, ocre/laranja das rochas, branco/creme, azul Capsule, laranja das esferas | ~40 materiais, sem textura fotográfica; neon só para energia (ki ciano, dourado, roxo) |

**O que evitar:** a ilha antiga da Área 2 é um retângulo plano com 3 domos e 7 esferas numa plataforma —
lê como "simulator genérico". Também evitar copiar a Capsule Corp literal ou pôr personagens no cenário.

## 2. Direção artística — "Vale Capsule"

**História visual:** a Capsule Corp. descobriu um vale com minerais de *ki* condensado (energia de
batalhas antigas cristalizada na rocha). Instalou uma refinaria, uma mina dentro da montanha e uma
pequena vila de técnicos. A mineração é o motivo de tudo existir: esteiras levam minério da Pedreira
até a refinaria, tubulações de energia saem da cúpula, a cratera é a origem do ki.

Contraste principal: **natureza ocre/verde orgânica × tecnologia branca/azul arredondada**, unidas pelo
**brilho ciano do ki** que aparece nas rochas, nas máquinas e nas placas.

## 3. Silhueta da ilha

Contorno irregular (polígono suavizado), ~390 × 400 studs:
- **Península sul**: pista de pouso (chegada).
- **Lobo sudoeste**: Vila Capsule.
- **Península leste**: Cratera de Batalha.
- **Lobo nordeste**: Portal para a próxima ilha.
- **Norte**: Montanha contínua com a Mina Capsule; **noroeste**: Cânion das Colunas + Caverna de Ki.
- **Ilhotas flutuantes** com colunas de rocha e **nuvens** em volta, para o fundo nunca ser céu vazio.
- Base da ilha em estratos ocre (vista de outras ilhas).

## 4. Layout (Blender: X leste, Y norte; chão y=0 → Roblox Y=6 local)

```
                          N
   ┌──── MONTANHA (estratos, 60–110) ── MINA CAPSULE ────────────────┐
   │ CAVERNA DE KI                    ║ (túnel)                     │
   │  ▲ ▲ CÂNION DAS    cachoeira     ║        ┌───── PLATÔ +12 ────┐ │ ◇ PORTAL
   │ ▲ COLUNAS (arco)   ░ LAGO ░   PÁTIO DA    │ COMPLEXO CAPSULE   │ │  (NE)
   │      │                        MINA        │ cúpula·torre·tanques│ │
   │      │ riacho→borda              │        └────── rampa ───────┘ │
   │ VILA ┼──────────── anel ─────────┼────────────── anel ─────┐     │
   │ CAPSULE      ╔══════ PEDREIRA ENERGÉTICA (piso −10) ═══════╗│  CRATERA
   │ (domos,      ║   só minérios; esteira ↗ refinaria          ║├── (piso −6,
   │ cápsulas,    ║   paredes com veios de ki                   ║│    pod caído)
   │ torre)       ╚════════════ rampa sul ═════════════════════╝│     │
   │   SANTUÁRIO DO DRAGÃO ◄─ avenida ─► ARENA DE TORNEIO (chefe)    │
   │   (invocação, 7 esferas)  │          casa-domo isolada (SE)       │
   └─────────────────── PISTA DE POUSO (chegada) ───────────────────┘
                          S
```

**Primeira visão (spawn olhando norte):** foreground = pista de pouso, postes de luz, árvores-bola;
middleground = Pedreira aberta (cristais nas paredes, esteira), Santuário à esquerda, Arena à direita,
domos da vila à esquerda; background = cúpula + torre do Complexo Capsule (direita do eixo), colunas de
rocha do cânion (esquerda), portal da Mina brilhando no fim do eixo central, montanha fechando o norte.
Nada alto fica entre a pista e a pedreira.

**Fluxo:** chegada → avenida → Pedreira (hub central, anel viário em volta) → escolhe:
Vila/Santuário (oeste) · Arena/Cratera (leste) · Pátio e Mina Capsule (norte) · Complexo (platô) →
Portal (nordeste). Exploração: Cânion das Colunas → Caverna de Ki (escondida atrás do arco).

**Guias sem setas:** caminho claro com faixa azul = onde andar; terra ocre escura + cristais ciano = onde
minerar; luz ciano em torres de energia marca cada entrada de zona de mineração; o Complexo e a torre são
visíveis de quase toda a ilha como referência de orientação.

## 5. Zonas de mineração
1. **Pedreira Energética** — poço central arredondado (piso −10), 4 rampas, paredes estratificadas com
   veios e cristais de ki, piso limpo só com minérios. Máquinas ficam na borda (esteira, perfuratriz, torres de luz).
2. **Mina Capsule** — pátio com trilhos e túnel dentro da montanha com arcos metálicos, luzes e cristais.
3. **Caverna de Ki** — gruta escondida no cânion, cristais roxos/dourados e fissuras luminosas.
4. **Cratera de Batalha** — bacia de impacto (piso −6), rocha rachada com brilho, pod caído na borda.

## 6. Kit modular (Blender → collections)
- **DRAGONBALL_BUILDINGS**: Casa_Domo_P, Casa_Domo_Dupla, Casa_Capsula, Casa_Antena, Apartamento_Redondo,
  Loja_Capsule, Laboratorio, Torre_Cogumelo, Garagem, Fabrica_Pequena, Deposito, Casa_Montanha
- **DRAGONBALL_CAPSULE_TECH**: Gerador, Refinador, Esteira, Tubo, Terminal, Drone, Veiculo_Hover,
  Capsula_HoiPoi, Container_Tech, Torre_Energia, Antena_Parabolica, Poste_Luz_Tech, Broca_Mineradora, Nave_Gravidade, Pod_Espacial
- **DRAGONBALL_PROPS**: Banco_Tech, Placa_Tech, Grade_Tech, Caixa_Carga, Barril_Metal, Maquina_Venda, Cone
- **DRAGONBALL_ROCKS**: Rocha_S/M/L, Pilar_A/B/C, Rocha_Equilibrio, Arco_Rocha, Penhasco, Mesa_Natural
- **DRAGONBALL_NATURE**: Arvore_Bola_G/M, Arvore_Ajisa, Palmeira, Arbusto_Bola, Flores, Tufo
- **DRAGONBALL_MINING**: Cristal_Ki (ciano/dourado/roxo), Cristal_Ki_G, Veio_Ki, Rocha_Fissura, Trilho_Tech,
  Vagoneta_Tech, Luminaria_Mina, Arco_Mina
- **DRAGONBALL_LANDMARKS**: Complexo_Capsule, Santuario_Dragao, Arena_Torneio, Portal_Capsule, Entrada_Mina
- **DRAGONBALL_DECORATION**: Esfera_Dragao, Bandeira_Capsule, Painel_Capsule, Nuvem, Ilhota_Flutuante

## 7. Otimização
Orçamento ≤ 8.000 Parts (Konoha: 4.706). Malhas compartilhadas, variações por escala/rotação, ~40
materiais, luzes limitadas a 60 e partículas só nos pontos focais (cachoeira, portal, santuário, caverna, cratera).
Rochas grandes e fundo sem colisão quando fora da área jogável.
