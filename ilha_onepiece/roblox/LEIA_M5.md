# M5: Ilha 5 One Piece / Wano no Roblox (passo a passo)

Os scripts desta pasta foram escritos **sem abrir o Studio**, copiando o contrato da Ilha 4 (`ilha_demonslayer/roblox/`, testado no Play em 2026-10-07). Tudo o que depende do jogo rodando está em "Testes no Play" e nas pendências.

**Regras:**
- **O agente não salva o place.** O usuário salva com Ctrl+S.
- **Antes de começar, confirme que o Studio está livre.** Outra sessão pode estar no Studio, e o usuário pode estar jogando no Roblox Player. A janela dele volta para a frente.
- **Não use `screen_capture` durante o Play.** Ele derruba o Play. Prepare a câmera e capture por último, uma captura por ciclo.
- **Teleporte de teste sempre pelo SERVIDOR.** O jogador teleportado pelo cliente para uma área não comprada é resgatado pelo `IslandTravel` (lição do Play da Ilha 4).

Exemplo, na Command Bar do servidor durante o Play:

```lua
local p = game.Players:GetPlayers()[1]
p.Character:PivotTo(CFrame.new(workspace.Areas.Area5:GetAttribute('EntryPosition')))
```

## Arquivos

| Arquivo | Vai para | O que faz |
|---|---|---|
| `OnePieceIsland.lua` | `ServerScriptService.Core.OnePieceIsland` (ModuleScript) | Clona `ServerStorage.IlhaOnePiece` para a área 5 e liga os sistemas que já existem: região, mineração, summon, portão OPM, guarda, água e VFX. |
| `CeuWano.client.lua` | `StarterPlayer.StarterPlayerScripts.CeuWano` (LocalScript) | Dia da área 5 só neste cliente: garantia de céu de dia, nuvens, bloom, sun rays, mar local turquesa em 36, fundo do lobby, água rolando, reverb, sons `AUDIO_*`, `PadGacha`. |
| `AreaAtmosphere_area5.lua` | `StarterPlayerScripts.AreaAtmosphere` | Script inteiro. As 3 linhas `[DS]` estão iguais à versão aplicada. As linhas `[OP]` trazem o perfil `[5]` diurno, lat/eds/ess por perfil, `ColorCorrection.Brightness` por perfil e `WanoMood`. |
| `IslandWorld_linha.md` | `Core.IslandWorld` | A linha de despacho (forma sem `require` no topo), as guardas e o `AreaAtmosphere` |
| `pos_montagem_onepiece.lua` | Command Bar | Depois do montar: confere tudo e move a ilha para `ServerStorage.IlhaOnePiece` |

## Passo a passo

### 0. Backup (no Studio)

Crie `ServerStorage.BeforeIlhaOnePiece_<data>` com cópias de:
- `Core.IslandWorld`;
- `StarterPlayerScripts.AreaAtmosphere`;
- `Core.DemonSlayerIsland`, só para referência (não é editado).

A construção genérica da área 5 é gerada pelo `IslandWorld` e não precisa de cópia.

### 1. Export (M4 concluído)

Rode `./run.sh export` na pasta `ilha_onepiece/`. O resultado vai para `ilha_onepiece/export/`:
- os FBX `ILHA5_<grupo>_<ID6>.fbx`, nos grupos `02_TERRAIN`, `03_PLAZA`, `04_CASTLE`, `05_CAPITAL`, `06_SUMMON`, `07_WATER`, `08_NEXT_ISLAND`, `08_PURCHASE_GATES`, `09_PROPS`, `10_VEGETATION`, `12_VFX_HELPERS`, `16_HARBOR`, `17_LANDMARKS` e `18_ENTRY`;
- `montar_ilha_onepiece.lua`;
- `ilha5_data.json`;
- `conexao_roblox.json`.

**Exigências:**
- o log tem de mostrar `CONEXAO WORLD_FROM_PREV x ancora da Ilha 4 ...: distancia 0.0000 OK`;
- os `WATER_*` / `FX_*` têm de ser os medidos pelo `op_water` (com `spout_waypoints`, `step2_pos`, `mouth_a_pos`, `wheel_pos`). O export do M2 (`export_m2/`) ainda tem as estimativas do M1.

### 2. Import

1. Crie um `Model` vazio `workspace.ILHA_ONEPIECE`.
2. Importe os FBX pelo botão **Import** do ribbon (3D Importer). O importador ignora clique sem a janela ativa: veja a memória "Importer do Studio sem foco".
3. Ponha **cada modelo importado DENTRO** de `workspace.ILHA_ONEPIECE`.
4. Espere as texturas processarem. As MeshParts ficam brancas por alguns minutos.
5. Nomes longos saem truncados com `...`. Renomeie pelo `ilha5_data.json`.

O trecho do M2 (`workspace.ILHA_ONEPIECE_M2`), se ainda estiver no place, sai antes: o `pos_montagem` avisa.

### 3. Montar

Cole `montar_ilha_onepiece.lua` na Command Bar. Ele é pesado e pode derrubar a conexão do MCP por cerca de 2 minutos.

O Output tem de mostrar:
- N/N por FBX;
- colisões, até 1.300;
- marcadores;
- luzes: até 36 de dia, mais as `NightOnly`;
- `pecas moveis marcadas (IlhaMovel)` > 0: roda d'água e anéis/estrela do summon;
- `pecas de portao de compra marcadas (PortaoCompra)` > 0;
- `pecas da guarda da ancora marcadas (GuardaProximaIlha)` > 0.

### 4. Scripts e patches

Aplique o que está em `IslandWorld_linha.md`:
- crie `Core.OnePieceIsland` e `CeuWano` com o conteúdo dos arquivos;
- acrescente a linha no `IslandWorld`, na forma sem `require` no topo, logo depois do `local SS` do `M.build`;
- aplique as linhas `[OP]` no `AreaAtmosphere`.

A DS não precisa de patch.

### 5. Pós-montagem

Cole `pos_montagem_onepiece.lua` na Command Bar. Ele:
- desliga `ILHA_ONEPIECE_Servidor`;
- recusa a ilha se houver proxy de minério, stub de QA ou `PREVIEW_`;
- confere os marcadores: ORE 72, GP_Block 76, SAFE 17, AUDIO 9, PATH 11, água medida e mar 36/2200;
- confere o encaixe contra `ServerStorage.IlhaDemonSlayer`, que tem de dar `distancia 0.000, frentes 1.0000`;
- confere a roda, as peças móveis, o portão e a guarda, e as luzes;
- lê o `Source` do passo 4 e avisa o que falta;
- move a ilha para `ServerStorage.IlhaOnePiece`. A anterior vai para `IlhaOnePiece_anterior`.

**A última linha tem de dizer `sem avisos`.** A lista "FX_* sem receita" é só informativa enquanto o `op_vfx` não existir.

### 6. Play: testes

Use o perfil sem salvar (`DebugV31 semSalvar`) e veja a tabela abaixo.

### 7. Antes e depois

Imagens no jogo em `ilha_onepiece/renders/ingame/`, com as câmeras `CAM_OP_*` (Ref_01 = concept, Ref_02 = anime).

## Testes no Play

| # | Teste | Como medir | Esperado |
|---|---|---|---|
| 1 | Montagem da área | Output do servidor | Sem erro. Linhas esperadas: `[OnePieceIsland] N emissores FX_*` (≥ 2: pétalas e névoa do pé da cachoeira); `agua: queda Castle: 8 pontos + bica do labio; queda E: 6 pontos; queda W: 6 pontos; nascente W: 4 pontos; bacia: contorno N pontos -> N-2 triangulos; canal leste: 11 trechos; canal oeste: 10 trechos; espuma da roda: ok`; `mineracao: ...`. Nenhum aviso de "canal leste comeca a X da boca". |
| 2 | Encaixe 0,000 | Command bar (servidor): `(Areas.Area5.ILHA_ONEPIECE.GAMEPLAY_MARKERS.WORLD_FROM_PREV.Position - Areas.Area4.ILHA_DEMONSLAYER.GAMEPLAY_MARKERS.ISLAND_NEXT_ANCHOR_OnePiece.Position).Magnitude` | 0,000 |
| 3 | Guarda da DS removida | Procurar `next_island_guard` em `Areas.Area4` | Nada. A guarda de Wano (OPM) **continua** em `Areas.Area5`, até existir `IlhaOnePunchMan`. |
| 4 | Travessia DS ↔ Wano, nos 2 sentidos | A pé pela ponte de 120, com a área 5 comprada. `CurrentAreaId`, `CurrentIslandMood` e `AreaRecoveries` no jogador. | 4 → 5 no meio da ponte e 5 → 4 na volta. Sem resgate (`AreaRecoveries` parado) e sem piscar (histerese). Céu noite → dia → noite sem ficar preso. Mar de nuvens (−60) some e o mar turquesa (36) entra com fade, e o contrário na volta. |
| 5 | 15 rotas a pé | `op_layout.routes()` | DS_GATE→ENTRY, ENTRY→PLAZA, ENTRY→SUMMON (viela, sem praça), PLAZA↔SUMMON, PLAZA→CASTLE (até o salão), PLAZA→HARBOR (até o convés pela prancha), PLAZA→EXIT_OPM, SUMMON→EXIT_OPM, PLAZA→OESTE (2 pontes do canal), PLAZA→TERRACO_ALTO, ENTRY→BAIRRO_CANAL, BAIRRO_CANAL→OESTE, PLAZA→NE, NE→SANTUARIO. Nenhum salto nem trava. Cair da borda resgata para o último ponto seguro (`SafeMaxY` 150: salva até o pátio do castelo 136,2). Cair no mar resgata em 28. |
| 6 | Mineração | Atributos de `Areas.Area5`: `OrePontosMarcadores`, `OreMarcadoresFora`, `OrePontosGrade`; contar `Area5.Rochas` | Cerca de 72 marcadores válidos (0 fora no QA) mais a grade. **70 minérios vivos** = `min(SPAWN.minerios 70, pontos − 2)`. Golpe tira HP. Quebra dá recompensa do tema `mare` (minério +1 / moedas). A rocha renasce. Nada nasce fora da elipse, nas margens de 34 a 40, no emblema rebaixado errado ou na escada. |
| 7 | Summon real | Ir ao terraço (`SUMMON_PlayerPosition`) e invocar com moeda de debug | Prompt "Invocar", catálogo e animação do tema `mare`, e a unidade entra no inventário. Sem linha de neon do `PadGacha` (o `CeuWano` esconde o pad neste cliente). A estrela e os anéis giram (`IlhaMovel`). |
| 8 | Portão OPM, por jogador | Sem a área 6: prompt "Desbloquear" e compra pela UI de sempre. Depois, com a área 6 comprada (debug). | Placa "CIDADE Z" com o preço. Bloqueado: barreira visível e colisão `COL_GateOnePunchManLock_001` ligada. Comprado: a barreira some, a colisão desliga, o prompt desliga e **não há teleporte**. Atravessa a pé até a âncora, onde a guarda provisória fecha a passagem (término seguro). Brilho dourado do portão. Para 2 jogadores, ver "Multiplayer". |
| 9 | Céu e atmosfera | `Lighting.ClockTime`, `GeographicLatitude`, `Brightness` e `GetSunDirection()` na área 5 | 13,5 / 30 / 2,6. **O sol vem de trás-esquerda de quem chega pela ponte.** A componente horizontal de `GetSunDirection()` deve ficar perto de (+0,98; −0,17) em X/Z. Se não ficar, ajuste `time`/`lat` do perfil `[5]`. Céu azul com nuvens brancas, sem lua grande, estrelas nem skybox noturno. Bloom 0,35 (o reboco branco não estoura). SunRays 0,04. |
| 10 | Transições | SG → DS → Wano → DS, Wano → lobby e lobby → Wano pelo menu Viajar | O céu nunca fica "preso" (skybox `sky512_`, lua 18/32) em Wano nem no lobby. Se ficar, o `CeuWano` avisa no Output `o Sky chegou em Wano com o skybox noturno`: anote o caminho que causou. Mar turquesa e nuvens somem ao sair. `Lighting.GeographicLatitude` e `ColorCorrection.Brightness` voltam ao valor base fora de Wano. |
| 11 | Mar local | Cliente: `workspace.MarWanoLocal`, e olhar da praça, do castelo e da cabeça da ponte | 2 × 2 ladrilhos de 1100 (fundo opaco em 29–30 e superfície em 34,95–35,95), textura correndo devagar. A quilha de Wano some. **A DS aparece saindo do mar.** Sem borda visível do quadrado do pátio do castelo (se aparecer, `MAR_ESCALA`). As quedas E e W terminam no mar, entre as pedras. Não existe na área 4 nem no lobby. |
| 12 | Água | Ver de perto | Bica do lábio (lâmina deitada da boca escura até a frente). Cortina da cachoeira do castelo passando pelos 2 degraus de espuma até a bacia. Bacia com o contorno desenhado, sem retângulo vazando e **sem emendas brancas**. Canal leste começando na linha da boca (sem lâmina dupla), degrau 3 × 2, curva e bica da queda leste. Bica da nascente oeste → canal oeste sob as 2 pontes → degrau 2 × 2 → espuma da roda → queda oeste. A textura corre no sentido da água: se correr ao contrário, troque o sinal de `Velocidade` no `fita` / `cortinaPts`. |
| 13 | VFX | Ver de perto e de longe | Pétalas rosa caindo devagar da copa (discretas, Dist 320). Névoa no pé da cachoeira e nos degraus. Respingos nos 2 degraus dos canais, na nascente e na roda. Brilho dourado do portão OPM. Desligam além do `Dist` (`ILHAS_Cliente`). |
| 14 | Peças móveis | Ver a roda | A roda d'água gira a 4 rpm a favor da correnteza (as pás de baixo empurradas para o sul local). Anéis e estrela do summon. |
| 15 | Luzes | De dia | Salão real (3 luzes `L_OPCas_Hall_*`, Range 18) iluminando as paredes. Núcleo e estrela do summon contidos (hierarquia: sol > summon > castelo). Casa de chá acesa por dentro. As `NightOnly` (lanternas, janelas) ficam apagadas: a área é dia fixo. Até 36 de dia. |
| 16 | Som | Na praça, na cachoeira, nas quedas, na roda, no porto, no summon e no castelo | Fontes `AUDIO_*` pelo `SomJogo` (wind/water/energy). Reverb no salão real e na casa de chá. A música ("Pirate King", `AudioCatalog.Music[5]`) não reinicia. |
| 17 | FPS | Protocolo de `ilha_shadowgarden/_audit/PERF_BASELINE.md`: cliente, 1 jogador, 6 s parado | **≥ 58 na praça, no porto e no pátio do castelo.** Medir também **na cabeça da ponte olhando a DS**, com as duas ilhas visíveis juntas (cerca de 600k + 620k tris, risco 1 do plano). Anote instâncias, Parts, MeshParts, luzes e emissores. |
| 18 | Output | Cliente e servidor | Sem erros nem avisos do `OnePieceIsland`/`CeuWano`. |

**Multiplayer:** "comprado por jogador" com 2 jogadores não dá para testar pelo MCP, a mesma limitação das Ilhas 3 e 4. O estado é por cliente (`ILHAS_Cliente` + `PortoesCompra` num LocalScript), como os portões já validados.

## Diferenças para o contrato da DS (`DemonSlayerIsland`)

| Ponto | DS (Ilha 4) | Wano (Ilha 5) |
|---|---|---|
| Portão | `GATE_KEY` OnePiece → área 5, placa azul-água | `GATE_KEY` **OnePunchMan** → área **6**, placa e brilho dourados |
| Guarda da ponta | Sai com `IlhaOnePiece` (já existe) | Sai com **`IlhaOnePunchMan`** (nome suposto, a ilha não existe): **fica** |
| Altura segura | `SafeMaxY` 100 | `SafeMaxY` **150** (pátio do castelo 136,2) |
| Região | `BoundsMinY` −12 | `BoundsMinY` **28**, abaixo do mar local 36: queda na água é resgatada. O teto da caixa passa da copa (~305). |
| Mineração | Clareira 112 × 150, piso 60,2 | **Praça 152 × 120, piso 92,2**, 76 bloqueios (48 borda + 28 canto). Ilha girada 145°: a zona vira lista de células, igual. |
| Céu | Noite: o `CeuNatagumo` troca skybox, lua e estrelas, e faz o mar de nuvens em −60 | **Dia:** o `CeuWano` **não troca o Sky**. Ele só garante que o céu de dia volte (rede de segurança contra o céu preso), põe nuvens, bloom 0,35 e sun rays, e faz o **mar turquesa em 36** (ladrilhos ≤ 2048, fade de entrada e saída). |
| `AreaAtmosphere` | Brightness por perfil, `NatagumoMood` | Mais latitude, `EnvironmentDiffuse`/`Specular` e `ColorCorrection.Brightness` por perfil, e `WanoMood`. Os outros perfis ficam no valor base. |
| Luzes noturnas | O `CeuNatagumo` liga as `NightOnly` | Ficam **apagadas** (dia fixo) |
| Água | Lagoa, calha, canal, aqueduto, poço da roda | Bica deitada do lábio (`spout_waypoints` em coordenada **local**, convertida pelo `WORLD_FROM_PREV`), cachoeira com 2 degraus (`step2_pos`), bacia poligonal com boca por `mouth_a_pos`/`mouth_b_pos` (já no mundo), 2 canais com degraus, nascente (bica), espuma da roda (`wheel_pos`), respingos nos `FX_Weir_*`, 2 quedas até o mar |
| Quedas | `FX_Fall_<n>_*` numeradas | `FX_Fall_<k>_*` com chave de nome (`Castle`/`E`/`W`): os padrões aceitam qualquer chave |
| Emissores | Receita gravada (`ds_vfx`), reserva de fumaça/brasas/névoa | Sem `op_vfx` ainda: reservas de **pétalas** (textura padrão, a mesma das pétalas aprovadas do lobby Murim; aceita `tex='rbxassetid://...'`) e névoa do pé da cachoeira. Receitas futuras (`vfx='emissor'`) entram sozinhas. |
| `IlhaPulso` | Brasa da fornalha | Nenhum |
| Reverb | Fornalha, V6, chaya | Salão real (raio 22) e casa de chá (raio 8) |
| Cores da água | Noite (azul escuro) | Dia: turquesa, na família do mar 48,176,196 |

## Só o Play confirma

- direção do sol com 13,5 / latitude 30;
- se a rede de segurança do céu precisa agir: ela não deveria, porque o `CeuNatagumo` e o `CeuSombras` já devolvem o Sky;
- borda do mar de 2200 vista do pátio do castelo (`MAR_ESCALA`);
- emenda do mar local de Wano com o mar azul da Ilha 1, visto de longe (o fundo do lobby fica escondido em Wano, como na DS);
- `Clouds` local: se o place já tem `Clouds` no Terrain, o script ajusta e devolve;
- bloom e sun rays somados a algum efeito global do lobby (se existir, baixe os valores do `CeuWano`);
- sentido da textura nas fitas e cortinas;
- triangulação da bacia: o contorno tem a boca retangular;
- `PadGacha` sem vazamento;
- histerese da região na ponte de 120;
- FPS com as duas ilhas;
- contagem real de minérios vivos;
- raios do reverb (22 e 8 são estimativas).

## Pendências e sistemas que NÃO existem

Nada disso foi inventado. Ficam registrados.

1. **Área 6 (One Punch Man):** não existe como ilha. O portão OPM vende a área 6, e a âncora termina na guarda provisória. O nome `ServerStorage.IlhaOnePunchMan` é **suposição** (`M.FONTE_PROXIMA`). A integração da área 6 deve usar esse nome ou mudar a constante.
2. **Asset do portão OPM** (`il_gate_opm` da galeria): sem aprovação explícita registrada (PLANO_OP 15.4). Pendência do usuário.
3. **`op_vfx` (M4) não existe:** nenhum `FX_*` tem receita gravada (`vfx='emissor'`). O módulo usa as reservas, e o `pos_montagem` lista os `FX_*` sem receita.
4. **`OreMax`:** nenhum script o lê. O teto real é `Config.SPAWN.minerios` = 70. Fica como documentação, igual à SG e à DS.
5. **`SAFE_*`, `PATH_ENTRY_*`, `ISLAND_EXIT_*`:** não têm consumidor no jogo. São marcadores de QA e documentação.
6. **`AUDIO_*`:** não há consumidor de marcador. O `CeuWano` usa a API que já existe (`SomJogo.RegisterEmitter`). Se o usuário não quiser, ponha `Som = nil`. O leito regional do `SomJogo` para a área 5 é `wind` 0,10 (`SomJogo:295-296`), o que serve para Wano.
7. **Mar local só no cliente:** outros jogadores fora da área 5 não veem o mar. É de propósito, como o mar de nuvens da DS. Da DS, Wano "flutua" sobre as nuvens (quilha em estratos até −10).
8. **`spout_waypoints` em coordenada local:** o `export_op.to_world` só converte `waypoints` e trios `*_pos`. O módulo converte, mas o certo seria o export converter também (chave `spout_waypoints`). Não editado: `export_op.py` é da integração do Blender.
9. **Rotas no Roblox:** o `teste_caminhadas.lua` da Ilha 2 precisa da tabela ROTAS em coordenadas do Roblox. Falta um passo (`op_qa` ou script avulso) que imprima as 15 rotas com `op_layout.to_roblox`.
10. **Peças móveis:** o `ILHA_NARUTO_Movel` percorre todas as peças `IlhaMovel` a cada frame, sem corte por distância. Wano acrescenta a roda e os anéis do summon. Medir.
11. **Interiores:** o salão real e a casa de chá não têm "esconder interior de longe" (não há Model `*_Int_*` separado). Só reverb.
12. **Valores de luz:** o perfil `[5]` usa a seção 10 do PLANO_OP. O `AreaAtmosphere_area5.md` do agente de luz não existia na entrega. Se chegar, troque só a linha `[5]`, e o Bloom/SunRays no topo do `CeuWano`.
