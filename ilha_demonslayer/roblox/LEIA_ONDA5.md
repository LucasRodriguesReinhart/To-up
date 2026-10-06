# Onda 5: Ilha 4 Demon Slayer no Roblox (passo a passo)

Os scripts desta pasta foram escritos **sem abrir o Studio**. Tudo o que depende do jogo rodando está na seção "Testes no Play" e nas pendências.

**Regras:**
- **O agente não salva o place.** O usuário salva com Ctrl+S.
- **Antes de começar, confirme que o Studio está livre.** Outra sessão mexe nos efeitos da Ilha 3, e o usuário pode estar jogando no Roblox Player. A janela dele volta para a frente.
- **Não use `screen_capture` durante o Play.** Ele derruba o Play. Prepare a câmera e capture por último, uma captura por ciclo.

## Arquivos

| Arquivo | Vai para | O que faz |
|---|---|---|
| `DemonSlayerIsland.lua` | `ServerScriptService.Core.DemonSlayerIsland` (ModuleScript) | Clona a fonte para a área 4 e liga os sistemas que já existem. É o contrato do `JardimSombrasIsland`. |
| `CeuNatagumo.client.lua` | `StarterPlayer.StarterPlayerScripts.CeuNatagumo` (LocalScript) | Noite da área 4 só neste cliente: skybox noturno, lua, bloom, mar de nuvens em −60, fundos, `NightOnly`, água rolando, reverb, sons `AUDIO_*`. |
| `AreaAtmosphere_area4.lua` | `StarterPlayerScripts.AreaAtmosphere` | Perfil `[4]` da seção 10, `Brightness` por perfil e `NatagumoMood`. São 3 trechos `-- [DS]`. |
| `IslandWorld_linha.md` | `Core.IslandWorld` e `Core.JardimSombrasIsland` | A linha de despacho e o patch da guarda da âncora da SG, com antes e depois |
| `pos_montagem_demonslayer.lua` | Command Bar | Depois do montar: confere tudo e move a ilha para `ServerStorage.IlhaDemonSlayer` |

## Passo a passo

### 0. Backup (no Studio)

Crie `ServerStorage.BeforeIlhaDemonSlayer_<data>` com cópias de:
- `Core.IslandWorld`;
- `Core.JardimSombrasIsland`;
- `StarterPlayerScripts.AreaAtmosphere`;
- o `Model` / scripts da área 4 procedural, se houver algo além do `IslandWorld`.

### 1. Export (Onda 4)

Rode `blender -b ilha_demonslayer.blend --python export_ds.py`. O resultado vai para `ilha_demonslayer/export/`:
- 12 FBX `ILHA4_<grupo>_<ID6>.fbx`, nos grupos `02_TERRAIN`, `03_CLEARING`, `04_FORGE`, `05_VILLAGE`, `06_SUMMON`, `07_WATER`, `08_NEXT_ISLAND`, `08_PURCHASE_GATES`, `09_PROPS`, `10_VEGETATION`, `12_VFX_HELPERS` e `18_ENTRY`;
- `montar_ilha_demonslayer.lua`;
- `ilha4_data.json`;
- `conexao_roblox.json`.

**Exigência:** o log tem de mostrar `CONEXAO WORLD_FROM_PREV x ancora da Ilha 3 ...: distancia 0.0000 OK`.

### 2. Import

1. Crie um `Model` vazio `workspace.ILHA_DEMONSLAYER`.
2. Importe os 12 FBX por **File > Import** (3D Importer). O ribbon fica recolhido nesta versão do Studio, e o importador ignora clique sem a janela ativa: veja a memória "Importer do Studio sem foco".
3. Ponha **cada modelo importado DENTRO** de `workspace.ILHA_DEMONSLAYER`. Sem isso o montar acusa "0/N FALTANDO".
4. Espere as texturas processarem. As MeshParts ficam brancas por alguns minutos.
5. Nomes longos saem truncados com `...`. Renomeie pelo nome do `ilha4_data.json` antes de montar.

### 3. Montar

Cole `montar_ilha_demonslayer.lua` na Command Bar. Ele é pesado e pode derrubar a conexão do MCP por cerca de 2 minutos.

O Output tem de mostrar:
- N/N por FBX;
- colisões, cerca de 1.300 no teto;
- marcadores;
- luzes: cerca de 16 de dia (teto 36) e cerca de 24 `NightOnly`;
- `pecas moveis marcadas (IlhaMovel)` > 0: roda, eixo, pilões e anéis do summon;
- `pecas de portao de compra marcadas (PortaoCompra)` > 0;
- `pecas da guarda da ancora marcadas (GuardaProximaIlha)` > 0.

### 4. Scripts e patches

Aplique o que está em `IslandWorld_linha.md`:
- crie `Core.DemonSlayerIsland` e `CeuNatagumo` com o conteúdo dos arquivos;
- acrescente as 2 linhas no `IslandWorld`;
- aplique o bloco da guarda no `JardimSombrasIsland`, pelo texto-âncora e só com a outra sessão fora do arquivo;
- aplique os 3 trechos `[DS]` no `AreaAtmosphere`.

### 5. Pós-montagem

Cole `pos_montagem_demonslayer.lua` na Command Bar. Ele:
- desliga `ILHA_DEMONSLAYER_Servidor`;
- recusa a ilha se houver proxy de minério, stub de QA ou `PREVIEW_`;
- confere marcadores (ORE 72, SAFE 13, AUDIO 8, FX com receita);
- confere o encaixe contra `ServerStorage.IlhaShadowGarden`, que tem de dar `distancia 0.000, frentes 1.0000`;
- confere peças móveis, portão, guarda e luzes;
- lê o `Source` dos scripts e patches do passo 4 e avisa o que falta;
- move a ilha para `ServerStorage.IlhaDemonSlayer`. A anterior vai para `IlhaDemonSlayer_anterior`.

**A última linha tem de dizer `sem avisos`.**

### 6. Play: testes

Use o perfil sem salvar (`DebugV31 semSalvar`) e veja a tabela abaixo.

### 7. Antes e depois

Imagens no jogo em `ilha_demonslayer/renders/ingame/`, com as câmeras `CAM_DS_*` do `ds_cams`.

## Testes no Play

| # | Teste | Como medir | Esperado |
|---|---|---|---|
| 1 | Montagem da área | Output do servidor | Sem erro. Linhas: `[DemonSlayerIsland] N emissores FX_*`, `agua: queda 1..., queda 2..., lagoa: contorno 26 pontos -> 24 triangulos (96 cunhas)` (ou perto), `calha`, `canal`, `aqueduto`, `poco da roda: ok`, `mineracao: ...`. Nenhum aviso de "canal comeca a X da boca". |
| 2 | Encaixe 0,000 | Command bar (servidor): `(Areas.Area4.ILHA_DEMONSLAYER.GAMEPLAY_MARKERS.WORLD_FROM_PREV.Position - Areas.Area3.ILHA_SHADOWGARDEN.GAMEPLAY_MARKERS.ISLAND_NEXT_ANCHOR_DemonSlayer.Position).Magnitude` | 0,000 |
| 3 | Guarda da SG removida | Procurar `next_island_guard` em `Areas.Area3` | Nada. A pé, a ponte passa sem bater. |
| 4 | Região | `CurrentAreaId` no jogador e `AreaRecoveries` | 3 → 4 ao cruzar a ponte de 100, e de volta. Sem resgate (`AreaRecoveries` parado). Cair da borda resgata para o último ponto seguro (`SafeMaxY` 100: salva até T4 80,2). |
| 5 | 10 rotas | A pé, ou com `ilha_dragonball/roblox/teste_caminhadas.lua` e as ROTAS do `ds_qa` em coordenadas do Roblox (pendência 6) | SHADOW_GATE→ENTRY, ENTRY→VILLAGE, ENTRY→CLEARING (trilha e bambuzal), CLEARING→FORGE, CLEARING→SUMMON, CLEARING→ONE_PIECE_GATE, FORGE→ONE_PIECE_GATE, SUMMON→CLEARING, VILLAGE→FORGE. Nenhum salto. |
| 6 | Mineração | Atributos de `Areas.Area4`: `OrePontosMarcadores`, `OreMarcadoresFora`, `OrePontosGrade`; contar `Area4.Rochas` | Cerca de 70 marcadores válidos (72 menos os fora) mais a grade. **70 minérios vivos** = `min(SPAWN.minerios 70, pontos − 2)`. Golpe tira HP, minério +1, rocha renasce. Nada nasce fora da mancha elíptica, no antecampo, no pé da subida ou na lagoa. |
| 7 | Gacha | Ir ao platô do summon (`SUMMON_PlayerPosition`) | Prompt "Invocar" e gacha do tema nichirin. Sem linha de neon do `PadGacha` (o `CeuNatagumo` esconde o pad neste cliente). |
| 8 | Portão One Piece | Sem a área 5: prompt "Desbloquear" e compra pela UI de sempre. Depois, com a área 5 comprada (debug). | A barreira some, a colisão de bloqueio desliga, o prompt desliga e **não há teleporte** (atravessa a pé até a âncora). A placa "GRAND LINE" com o preço. O brilho do portão cai para 0,8 depois de liberado. |
| 9 | Céu e atmosfera | `Lighting.ClockTime`, `Lighting:GetMoonDirection()` e `Lighting.Brightness` na área 4 | ClockTime 20,5, Brightness 1,6. **A lua fria vem de trás-esquerda de quem chega pela ponte** (lado +X). Se não vier, ajuste o `time` do perfil `[4]`. Mar de nuvens em −60 com a quilha da SG saindo dele. Bloom 0,3. |
| 10 | Transições | SG → DS → SG → DS, e DS → lobby pelo menu Viajar | O céu nunca fica "preso" com a lua 18/32 nem com o skybox noturno fora das áreas 3/4. O mar de nuvens some ao sair. Sem piscar na ponte (histerese do `IslandTravel`). |
| 11 | Água | Ver de perto | Cascata única da bica até a lagoa, passando pelo degrau. Lagoa com o contorno desenhado, sem retângulo vazando pelo barranco. O canal começa na linha da boca, sem lâmina dupla. Calha do terraço, sangradouro em 3 poços com a bica final, aqueduto até o bico sobre a roda e o poço da roda. A textura corre no sentido da água (se correr ao contrário, troque o sinal de `Velocidade` no `fita`). |
| 12 | VFX | Ver de perto e de longe | Fumaça fina da chaminé com deriva, lanternim, brasas na boca, névoa rasteira no bambuzal e na ravina, espuma das quedas. Desligam além do `Dist` (`ILHAS_Cliente`). A brasa da boca "respira" (`IlhaPulso`). |
| 13 | Peças móveis | Ver a roda | A roda gira a 3 rpm, o eixo gira junto e os 2 pilões batem (0,10 e 0,15 batida/s). Anéis e estrela do summon. |
| 14 | Luzes | Na vila à noite | Lanternas `NightOnly` acesas na área 4, apagadas ao sair. Boca da fornalha como a luz mais forte. |
| 15 | Som | Perto da forja, roda, cascata, bambu e summon | Fontes `AUDIO_*` (fire/water/wind/energy) pelo `SomJogo`. Reverb leve dentro do salão da fornalha, da casa V6 e da chaya V1. A música não reinicia. |
| 16 | FPS | Protocolo de `ilha_shadowgarden/_audit/PERF_BASELINE.md`: cliente, 1 jogador, 6 s parado | **≥ 58 na vila e na forja; 60 no resto.** Medir também **na cabeça da ponte olhando a SG**, com as duas ilhas visíveis juntas (cerca de 1,3 M tris). Anote também instâncias, Parts, MeshParts, luzes e emissores. |
| 17 | Output | Cliente e servidor | Sem erros nem avisos do `DemonSlayerIsland`/`CeuNatagumo`. |

**Multiplayer:** com 2 jogadores não dá para testar pelo MCP. Mesma limitação da Ilha 3.

## Diferenças para o contrato da SG (`JardimSombrasIsland`)

| Ponto | SG | Ilha 4 |
|---|---|---|
| Portão | `GATE_KEY` DemonSlayer → área 4 | `GATE_KEY` **OnePiece** → área **5**, placa azul-água |
| Altura segura | `SafeMaxY` 60 | `SafeMaxY` **100** (forja em 80,2) |
| Teto de minérios | `OreMax` 90 | `OreMax` **80** |
| Região | `BoundsMinY` desce até o subsolo | `BoundsMinY` **−12** fixo: não há subsolo, e queda é resgatada antes da quilha (−34) e da rede (−45) |
| Teto da caixa | | O teto da caixa passa da chaminé (152,2) |
| Sistemas | Masmorra, alquimia, trono, `CRAFT_`/`DUNGEON_`, cristais `IlhaPulso` | Nada disso. A brasa da boca da fornalha usa o mesmo `IlhaPulso`. |
| Mineração | Salão coberto | **A céu aberto.** A zona girada vira lista de células, igual. |
| Chefe | | Primeiro `ORE_SUPERLEGENDARY_*`, ou um `EPIC` |
| Água | Cachoeiras e fonte | **Lagoa poligonal** triangulada em WedgeParts (Glass + ForceField), **fitas deitadas** para calha, canal e aqueduto (a mesma lâmina da cortina, com a face para cima), **poço da roda**. O canal começa na boca da lagoa (ponto 1 alinhado ao meio de `mouth`). |
| Atributos locais | | `mouth` e `pit_rect` vêm em coordenada **local** do projeto (o export não converte). O módulo converte pelo `WORLD_FROM_PREV` (origem local (0, −`bridge_len`), frente +Y). |
| Emissores | Escritos à mão | Pela **receita gravada no marcador** (`vfx='emissor'`: tex, cor, `cor_ini`/`cor_fim`, rate, vida, vel, tam, fim, transp, luz, infl, spread, area, forma, Dist, `acc_up`, drift), com reserva igual ao `ds_vfx` se o export vier sem receita. |
| Guarda da ponta | | Sai quando existir `ServerStorage.IlhaOnePiece` (nome suposto da fonte da área 5) |

## Só o Play confirma

- direção da lua com ClockTime 20,5;
- sentido da textura nas fitas deitadas (a cortina é o caso já validado na SG);
- triangulação da lagoa sem fresta: o contorno tem uma reentrância na boca;
- `PadGacha` sem vazamento;
- histerese da região na ponte;
- o mar de nuvens não piscar na transição SG → DS;
- FPS com as duas ilhas;
- contagem real de minérios vivos;
- reverb pelos raios das luzes de interior: 16, 11 e 7 são estimativas.

## Pendências e sistemas que NÃO existem

Nada disso foi inventado. Ficam registrados.

1. **`OreMax`:** nenhum script do repositório o lê. Só o `JardimSombrasIsland` o grava. O teto real é `Config.SPAWN.minerios` = 70 (`AreaBuilder:447`). Fica como documentação, igual à SG.
2. **`SAFE_*`, `PATH_ENTRY_*`, `ISLAND_EXIT_*`:** não têm consumidor no jogo, também na SG. O `IslandTravel` usa uma só `SafePosition`, mais o ponto seguro salvo pelo chão. Ficam como marcadores de QA e documentação.
3. **`AUDIO_*`:** não há consumidor de marcador. O `CeuNatagumo` usa a API que já existe (`SomJogo.RegisterEmitter`, a mesma do `AudioWorld`). Se o usuário não quiser, ponha `Som = nil` no topo.
4. **`SomJogo:295-296`:** o leito regional usa `area==4 and 'energy'`. Isso é da época em que a SG era a área 4, e a auditoria C (item 7) mandava trocar para `area==3`. **Conferir no Studio:** se não foi trocado, a área 4 (Natagumo) toca o leito "energy" da SG. Também `AudioCatalog.Music[4]` (trilha do Natagumo).
5. **Atributos locais no export:** `WATER_Pond.mouth` e `WATER_Flume.pit_rect` saem em coordenada local. O módulo converte, mas o certo seria o `export_ds.to_world` converter também (chaves `mouth` e `pit_rect`). Não editado: `export_ds.py` é da Onda 4.
6. **Rotas no Roblox:** o `teste_caminhadas.lua` da Ilha 2 precisa da tabela ROTAS em coordenadas do Roblox. Falta um passo no `ds_qa` (ou script avulso) que imprima as 10 rotas com `ds_layout.to_roblox`.
7. **Fonte da área 5:** o nome `ServerStorage.IlhaOnePiece` é suposição (`M.FONTE_PROXIMA`). A integração da One Piece deve usar esse nome ou mudar a constante.
8. **Desempenho das peças móveis:** o `ILHA_NARUTO_Movel` percorre todas as peças `IlhaMovel` a cada frame, sem corte por distância. A Ilha 4 acrescenta roda, eixo e 2 pilões. Medir. Se pesar, o corte é no script gerado pelo `export_ilha_lua`, que é de outra ilha (não editado).
9. **Interiores:** V1 e V6 fazem parte do próprio objeto da casa (`DS_Vil_HouseV1` / `DS_Vil_HouseV6`), não de um Model `*_Int_*` separado. Por isso não há "esconder interior de longe" como na SG (`SG_Vil_Int_`). Só reverb.
10. **NightOnly da SG vista daqui:** as lanternas da SG só acendem com o jogador na área 3 (`CeuSombras`). Da cabeça da ponte, a SG aparece com as lanternas apagadas.
11. **Gacha do Natagumo:** o custo de 55.000 continua provisório (D1b da SG).
12. **`time` do perfil `[4]`:** 20,5 é estimativa, simétrica aos 3,5 medidos na SG. A direção exata se ajusta no Play (risco 5 do plano).
