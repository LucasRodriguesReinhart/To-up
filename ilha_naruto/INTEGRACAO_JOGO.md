# Integração final da Ilha 1 (Naruto) no Roblox Studio

Status em 2026-09-25: **integrada e testada em Play**. O place não foi salvo nem publicado pelo agente, então a decisão de salvar é sua.
Falta um passo, que depende da tela liberada: **reimportar 5 FBX** (ver "Pendente").

## Como ficou montado

```
ServerStorage.IlhaNaruto               <- a ilha montada (export 1c2e6437), a FONTE
   | clone em runtime
workspace.Areas.Area1.ILHA_NARUTO     <- Core.NarutoIsland.build (chamado pelo IslandWorld para a area 1)
```

- `Core.NarutoIsland` (novo, [roblox/NarutoIsland.lua](roblox/NarutoIsland.lua)) implementa o mesmo contrato dos outros builders de ilha. Devolve `{spawns, boss, returnPad, zonas}` e os atributos EntryPosition, SafePosition, GachaPosition, BoundsHalfSize, WorldRevision e ModelStreamingMode PersistentPerPlayer.
- `IslandWorld.build`: uma linha nova antes da Konoha. Se `ServerStorage.IlhaNaruto` existir, a área 1 usa a ilha nova. **Rollback:** renomeie `ServerStorage.IlhaNaruto` e a Konoha (`ServerStorage.KonohaArea`, intocada) volta.
- `TravessiaCorredores` e `Paredes` receberam 1 condição cada, via atributo `RotaPropria` na Area1:
  - não abrem faixas nas colisões da ilha (as colisões também levam `TravessiaKeep`);
  - não criam a Passarela1 nem a Parede2 (z 630), que atravessariam o paredão e o salão principal.
- Arquivados, não apagados, em `ServerStorage.ILHA_NARUTO_substituidos`:
  - `Corredores.Area1_Area2`: estrada visível com postes cruzando o salão principal;
  - `Corredores.Lobby_Area1`: chão invisível de 92 studs sob a ponte.
- O import velho 203d27 foi para `ServerStorage.ILHA_NARUTO_import_203d27_Arquivo`.
- `ILHA_NARUTO_Servidor` (gerado pelo montar) fica **desligado**. Este export não tem cascas SoVisual, e o grupo `Personagens` colidiria com `PetsVisuais`. Quedas continuam com o IslandTravel.
- Backups:
  - antes: `ServerStorage.BeforeIlhaNaruto_20260925`;
  - depois: `ServerStorage.AfterIlhaNaruto_20260925`, com cópia de todos os scripts tocados e a nota `LEIA`.

## Lobby -> ponte -> entrada -> ilha
- A rampa do lobby sobe de 0 para 6.2 entre z 192 e 216 e encosta no deck da ponte da ilha, também a 6.2, em z 222. Não há degrau, buraco nem parede invisível.
- O teste a pé (MoveTo) foi do spawn do lobby até a entrada sem nenhuma recuperação do IslandTravel.
- A primeira entrada da sessão pausa ~5 s enquanto a ilha inteira faz streaming (modelo PersistentPerPlayer). Na segunda entrada não há pausa.
- Spawn: `EntryPosition = WORLD_ENTRY_Naruto` (0, 9.7, 320), com o HRP 3.5 acima do piso. O IslandTravel vira o jogador para +Z, olhando para o fosso, igual ao marcador.

## Mineração: sistema existente, só apontado para a ilha
Cadeia SPAWNER -> ORE MODEL -> DAMAGE -> BREAK -> REWARD -> RESPAWN, com AreaBuilder, SpawnMinerio e Mineracao intactos.

- **MiningZone_Naruto**: piso do fosso, centro (0, 3.2, 420), 104×104, raio útil 50. Fica como peça lógica na Area1, com CanQuery=false.
- **Bloqueios** (circulares, o formato que o SpawnMinerio aceita):
  - marco central r15;
  - escadas S e N r12;
  - rampas de carga L e O r16;
  - anel na borda (centro r60, raio 9, a cada 8 studs), que fecha r ≥ 52: nenhum minério encosta na parede ou na cerca.
- **Pontos:**
  - 54 marcadores ORE_* do Blender, só a posição (raridade continua do SpawnMinerio). 16 ficaram de fora por falharem na mesma folga que o sistema exige: caixa 7×8×7 livre, ou dentro de bloqueio. Eram os que encostavam em escada, rampa, torre de extração e marco;
  - grade hexagonal de 7.5 studs no piso do fosso (122 candidatos);
  - grade própria do SpawnMinerio.
  Sem isso o pool ficava justo (56–62 pontos para 60 minérios) e a amplificação de comum empilharia dois minérios no mesmo ponto.
- **Densidade:**
  - baixa (30): vizinho mínimo 9.1, médio 11.4;
  - normal: o padrão do jogo, `min(SPAWN.minerios=70, pontos−2)` = **70** minérios, vizinho mínimo 7.3, médio 8.2;
  - máxima: todos os pontos ocupados, igual ao padrão, ainda sem empilhar.
  Raio máximo 51.2 e 0 fora da zona, incluindo depois de respawns.
- **Raridades preservadas:** comum 58, incomum 8, raro 3, épica 1 (o `SPAWN.inicial` de sempre).
- **Teste real:** `Golpear` do cliente -> HP -> quebra -> mochila +1 -> respawn de volta a 70 -> venda no Ignis -> moedas.

## Invocação: sistema existente
- A máquina `Gachas.Gacha_chakra` virou o "motor" invisível da torre:
  - o corpo (onde o Main põe o `GachaPrompt`) fica no portal (SUMMON_Interact);
  - o `PadGacha` fica 16 studs à frente, afundado sob a praça. Ele serve para a proximidade do GachaService/cliente e de destino do `UITravel gacha`.
- O visual é só a torre aprovada. Não há modelo novo.
- Teste:
  - a viagem cai na praça;
  - o prompt fica a 3.7 studs do jogador no portal;
  - `AbrirGacha(1)` abre a UI;
  - o giro cobra e entrega o pet.

## Portão Dragon Ball
- **Interação:** peça `PortaoDB_Interacao` com `NextAreaId=2` no pátio. O prompt vem do Core.Main de sempre:
  - bloqueado: `FeedbackMina comprarArea` abre o popup de compra;
  - compra: `Progresso.comprarArea(2)`.
  - Não há DataStore novo. O estado é `perfil.areas[2]`, já salvo pelo PlayerData.
- **Estado por jogador** (LocalScript `ILHA_NARUTO_Cliente`): lê `areas` do snapshot `AtualizarDados`/`PedirDados` e chama `PortoesCompra.Estado('DB', ...)`.
  - LOCKED: barreira visível e pulsando, colisão ligada, placa de preço (PURCHASE_UI_ANCHOR_DB) e prompt "Desbloquear".
  - UNLOCKED: barreira e colisão somem, anel dourado calmo, placa escondida e prompt "Viajar".
- **Testado:**
  - sem moedas: "Faltam 1.4K moedas";
  - com moedas: desbloqueia na hora e o jogador atravessa a pé;
  - reset: continua aberto;
  - nova sessão com o perfil real do DataStore (areas[2]=true): entra aberto;
  - perfil novo: entra fechado.
- **Multiplayer:** não deu para abrir 2 clientes pelo MCP. O estado é local de cada cliente por construção (o servidor nunca abre a barreira para todos). O teste com 2 jogadores fica para quando você puder.

## ISLAND_NEXT_ANCHOR (para a Ilha 2)
Atributos na Area1:
- `NextAnchorPosition` (−192.17, 16.2, 612.17)
- `NextAnchorForward` (−0.7071, 0, 0.7071)
- `NextAnchorWidth` 18
- `NextAnchorClearHeight` 22

A guarda provisória (EXIT_AnchorGuard + COL, tag `GuardaProximaIlha`) continua lá até a ponte da Ilha 2 encostar.

Enquanto isso, um disco `ViagemProximaArea` (NextAreaId=2) na ponta leva à entrada da área 2, pelo sistema de viagem de sempre, com prompt "Viajar".

## VFX (baratos, com culling por distância no cliente)
- **Invocação:** estrela e 3 anéis girando devagar (IlhaMovel, 2–6 rpm), brilho discreto na estrela, poeira subindo no portal, cristais da torre "respirando" (cor 80–100%, ciclo ~5 s).
- **Água:**
  - névoa na base da cachoeira dos fundos (3) e espuma caindo;
  - respingo na roda d'água e no canal oeste;
  - névoa na borda e na base das 4 quedas para o mar.
- **Roda d'água** girando a 4 rpm, com engrenagem e pilões do moinho.
- **Portão:** orbes orbitando e faíscas. Bloqueado: 3/s com a barreira ondulando. Liberado: 0.8/s com o anel calmo.
- **Total:** 17 emissores `IlhaVFX`, cada um com `Dist` (140–700). O cliente desliga o que está longe, 2×/s. Pulsos a 30 Hz, só perto.

## Iluminação
- O global já é o perfil diurno `AreaAtmosphere[1]` (15:06, bloom 0.6 com limiar 1.35). Não foi mexido.
- As luzes da ilha foram rebalanceadas na hierarquia pedida (valores em brilho/alcance):

| Nível | Luz | Brilho / alcance |
|---|---|---|
| 1. Invocação | estrela | 1.7 / r22 |
| | portal | 1.55 / r20 |
| 2. Salão principal | | 1.2 / r18 |
| 3. Portão DB | | 0.8 / r12 |
| 4. Água (nova, fria) | | 0.6 / r16 |
| 5. Props | lojas / ramen | 0.55 |
| | moinho / marco | 0.3–0.45 |

## Colisão e desempenho
- **Colisão:** 1109 Parts invisíveis simples. Nenhuma MeshPart colide e nenhuma usa PreciseConvexDecomposition.
- **Antes (Konoha) → depois (Naruto)**, mesmo ponto e mesmo método (Play no Studio):

| Medida | Antes | Depois |
|---|---|---|
| Instâncias da Area1 | 9.192 | 4.154 (−55%) |
| Parts | 4.921 | 1.386 |
| MeshParts | 319 | 773 (inclui os minérios) |
| Luzes | 37 | 33 |
| Render CPU / GPU (ms/frame) | 11.9 / 5.7 | 7.8 / 4.4 |
| Física por passo (ms) | 0.107 | 0.005 |
| FPS | 60 | 60 |

## Teste de jogo completo (uma sessão, perfil de teste sem salvar)
1. Lobby -> ponte -> entrada a pé.
2. Descer ao fosso.
3. Quebrar 3 minérios, com recompensa na mochila e respawn.
4. Vender.
5. Invocação: UI + giro.
6. A pé: fosso -> escada sul -> anel -> praça da invocação -> trilha de saída -> pátio do portão (pathfinding, 0 recuperações).
7. Portão fechado -> popup de compra -> compra -> atravessa a pé.

Output sem erros nem warnings em todas as sessões.

## Pendente: reimportar 5 FBX (precisa da tela)
O 3D Importer só funciona pela interface, e o Windows estava com a tela bloqueada. Então a ilha foi montada reaproveitando as malhas já enviadas (203d27):
- **434 das 470 malhas são idênticas.**
- **31 malhas ainda estão com a geometria antiga e 5 faltam.** A diferença está na silhueta do paredão, no marco de pedra, em 3 folhagens do platô, na espuma e no moinho.
- O `MINE_Props__Crystal_Blue` antigo espalhava cristais pelo fosso e **ficou de fora** (em `ServerStorage.ILHA_NARUTO_pendente_reimport`).

Para fechar:
1. Import Queue: importe os 10 `export/ILHA1_*_1c2e64.fbx` para `workspace.ILHA_NARUTO`.
2. Rode `export/montar_ilha_naruto.lua`.
3. Rode [roblox/pos_montagem_integracao.lua](roblox/pos_montagem_integracao.lua). Ele reaplica luzes e ajustes e troca a fonte em ServerStorage, guardando a anterior.
