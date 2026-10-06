# Ilha 3 Shadow Garden: integração no Roblox (2026-09-29)

Export `ac1e1ae5` importado e montado no place **Anime Mining Simulator**. O agente NÃO salvou nem publicou o place:
as mudanças do Studio abaixo só ficam permanentes quando o usuário salvar.

## O que foi feito no Studio
- **Import**: 14 FBX `ILHA3_*_ac1e1a` importados, 678/678 MeshParts. O importador truncou 2 nomes do portão Demon
  Slayer (`GATE_DemonSlayer_Barrier__Energy_Core_DemonSlayer_Glow`, `GATE_DemonSlayer_Lock__Energy_Core_DemonSlayer_Glow`),
  e eles foram renomeados antes da montagem.
- **Montagem** (`export/montar_ilha_shadowgarden.lua`): 14/14 FBX ok, ALINHAR girou 180° (escala 1,000), 733 colisões,
  169 marcadores, 40 luzes, 14 pontos seguros.
- **Fonte**: o modelo montado virou `ServerStorage.IlhaShadowGarden`, com a mesma estrutura de `IlhaDragonBall`.
  `ServerScriptService.ILHA_SHADOWGARDEN_Servidor` ficou **desligado**, como o da Ilha 2.
- **Scripts** (cópias iguais em `roblox/`):
  - `Core.JardimSombrasIsland` (novo);
  - `Core.DungeonService`, com o gancho Studio-only `ServerStorage.DebugMasmorra` e a correção das recompensas;
  - `Core.CraftService`, com a mensagem "Voce criou: X!";
  - `CeuSombras`, que esconde o chão distante do lobby e escurece o mar da Ilha 1, só no cliente e só na área.
- **Patches no código do jogo** (cópias em `roblox/patches_jogo/`):
  - `Core.Mineracao`: o evento `Quebrou` do minério temporário passa uma LISTA de jogadores.
    - **Antes** mandava um mapa `{[player] = golpes}`, e o BindableEvent descarta chaves que são objetos.
    - **Efeito**: a masmorra não entregava a recompensa por minério, só o bônus de limpeza.
  - `OreVFX`: o círculo mágico de chão do tema ShadowMana (só a Ilha 3 usa) ficou menor e mais translúcido.
    - `0,8 + 0,2·tier` em vez de `1,2 + 0,35·tier`, e transparência 0,45.
    - **Motivo**: no Mining Hall os círculos se sobrepunham numa malha de linhas magenta.
- **Ilha 2**: duas ilhotas decorativas caíam dentro da Ilha 3.
  - `(340,180)` aparecia no gramado oeste da praça.
  - `(440,110)` ficava dentro do penhasco.
  - Foram movidas em `ilha_dragonball/db_scene.py`, sem mudar a quantidade nem a ordem, então as outras ilhotas não mudam.
  - Só as 5 MeshParts `DB_Sky_Islets__*` foram trocadas em `ServerStorage.IlhaDragonBall.SKYLINE`, pela mesma regra do
    montar (centro do export + giro 180°).
  - As antigas estão em `ServerStorage.BeforeShadowGarden_20260929.DB_Sky_Islets_antigas`.
- **Backup** de tudo o que foi alterado: `ServerStorage.BeforeShadowGarden_20260929`.

## Testes no Play (sem salvar o progresso: `DebugV31 semSalvar`)
| Teste | Resultado |
|---|---|
| Encaixe na âncora da Ilha 2 | exato: (-579,23; 28,2; 650,73) |
| Rota âncora → escadaria → praça → vila → pátio → Mining Hall | andando, OK; área 3 detectada |
| Clima da área | noite, lua 24, 3.000 estrelas, bloom 0,35; tudo restaurado ao sair |
| Mineração no salão | 51 minérios; golpe tira HP, minério +1, rocha renasce |
| Invocação | pela ponte até a plataforma; "Invocar" abre o gacha da área 3 |
| Alquimia | longe → "Va ate o caldeirao"; sem ingredientes → recusa; receita inválida → recusa; Elixir e Poção de Sorte fabricados com o consumo exato; mesmo `requestId` não fabrica de novo; beber a poção ativa |
| Masmorra | WAITING → COUNTDOWN (entrada fechada) → ENTRY_OPEN (abre) → entrada leva ao salão de baixo → 17 minérios → fim antecipado → FINISHING (portal de saída aceso, entrada fechada para atrasados) → RESETTING (volta ao pátio, rochas somem) → WAITING |
| Recompensas da masmorra (depois da correção) | 6 comuns + 4 incomuns + bônus = 17 Pó; 6 épicas + 1 lendária = 7 Essência; 1 Fragmento |
| Rota de saída | até a ilhota do portão Demon Slayer; aviso "Desbloquear" desligado para quem já tem a área 4 (sem teleporte) |
| Paredes de custo | 2 ativas (a Ilha 3 tem `RotaPropria`, como a Ilha 2) |
| Output | sem erros |

**Não testado com 2 jogadores reais.** O "Server and Clients" do Studio não abriu por comando, e os clientes seriam
processos que a ferramenta não alcança. Foi verificado só o que afeta vários jogadores:
- a lista de quem golpeou chega completa;
- a entrega é idempotente por minério+jogador;
- o bônus é marcado antes de entregar.

## Desempenho (Play, cliente, 1 jogador; mesma medição de `_audit/PERF_BASELINE.md`)
| Ponto | FPS | Memória | Instâncias (workspace) | Parts | MeshParts | Luzes | Emissores |
|---|---|---|---|---|---|---|---|
| lobby | 60 | 3.104 MB | 24.704 | 14.143 | 4.093 | 236 | 690 |
| Ilha 2 (âncora) | 60 | 3.104 MB | 24.790 | 14.224 | 4.172 | 237 | 690 |
| Ilha 3 (praça) | 60 | 3.105 MB | 24.790 | 14.224 | 4.172 | 237 | 690 |
| Ilha 3 (Mining Hall) | 60 | 3.105 MB | 24.790 | 14.224 | 4.172 | 237 | 690 |

A Área 3 inteira soma **3.429 instâncias e 1.931 Parts**. A área antiga genérica somava cerca de 15 mil instâncias e
11,4 mil Parts.

## Imagens no jogo
`renders/ingame_v3/IG_01..IG_11` e a folha `renders/ingame_v3_folha.jpg`, com as mesmas câmeras dos renders.

## Pendências
- **Salvar o place** (o agente não salva).
- O custo do gacha Natagumo (55.000) continua provisório (D1b).
- As recompensas e os tempos da masmorra são provisórios (`AlquimiaConfig`).

## Passe final de acabamento (craftsmanship), 2026-09-29
Export `4ec5f0f0` (665 MeshParts, 483k tris, 730 colisões, 40 luzes), reimportado (665/665) e montado. A fonte
anterior ficou em `ServerStorage.IlhaShadowGarden_ac1e1ae5` (rollback: renomear).

- **Símbolo da ordem** (`sg_emblem.py`):
  - malha limpa: anel contínuo, crescente num único polígono, espada simétrica com guarda, cabo e pomo;
  - estandarte com espessura e verga de verdade;
  - `emblem_flat` para os medalhões do piso do salão e do pátio.
- **Alquimia:** caldeirão com perfil de revolução (pés, cintas, medalhão com aro), kit de livros e frascos arrumados à mão, estantes com rodapé e cornija, móveis com estrutura, exterior com menos neon (anéis armilares, câmaras de vidro com flange).
- **Dungeon:** caverna antiga em ruína. O exterior é quase natural, com poucos danos deliberados; a magia vem de dentro.
- **Castelo e Hall:** janelas com moldura, recuo e vidro (a maioria quente), janelão com rendilhado, soleira, trims fechados, estandartes presos, brilho baixo (`SG_VioletSoft_Glow`).
- **Vila, entrada, pátio e invocação:**
  - variações dirigidas do kit (janelas, enxaimel, cumeeiras), sem neon roxo na vila;
  - menos bandeiras e árvores fora de lugar;
  - estátuas e obeliscos refeitos, com a espada da estátua esculpida;
  - invocação com brilho moderado.
- **Paleta:** pedra mais neutra, madeira quente, telhados e obsidiana legíveis, ferro com leitura de metal.
  - No Roblox o `SG_Rune_Glow` ficou mais escuro, porque o crescente virava branco com o bloom.
  - Os frascos da alquimia ficaram com transparência 0,55.
  - Estas duas mudanças estão aplicadas no Studio (Color/Transparency) e no `sg_lib`; o próximo export já sai com elas.
- **Luz da área 3** (`AreaAtmosphere`): luar mais neutro, com ambient C(142,140,174), out C(162,160,194), saturação −0,03 e exposição 0,19.
  - Cópia em `roblox/patches_jogo/AreaAtmosphere.client.lua`; o backup do original está em `ServerStorage.BeforeShadowGarden_20260929`.
- **Testes no Play:**
  - rotas (âncora → Mining Hall, dungeon, caldeirão, invocação pela ponte) OK;
  - marcadores OK e 50 minérios no salão;
  - alquimia e masmorra ligadas;
  - Output sem erros.
- **Antes/depois:**
  - Blender: `renders/finesse_ad_closeups_1.jpg`, `finesse_ad_closeups_2.jpg`, `finesse_ad_gerais.jpg`, `finesse_ad_sem_brilho.jpg`;
  - jogo: `renders/finesse_ad_jogo.jpg` e `renders/finesse_jogo_gerais.jpg`;
  - folhas por zona em `renders/finesse_folhas_*` e `renders/finesse_depois_castelo_hall/`.
- **Correção de prévia:** o `sea()` do `sg_scene` reconstruía todos os materiais e anulava o limite de brilho da prévia. O ANTES foi renderizado de novo com a correção e a paleta antiga, para a comparação ser justa.

## Trilha da área 3: Moonlight Sonata, 1º movimento (2026-09-29)
- **Faixa:** `AudioCatalog.Music[3]` passou a ser o asset `1848050065`, "Moonlight Sonata, Adagio Sostenuto": Beethoven, Sonata nº 14, op. 27 nº 2, I. Adagio sostenuto; 367 s no Roblox.
  - A faixa anterior era "The Forgotten Crypt" (`131334832939011`).
  - Cópia em `roblox/patches_jogo/AudioCatalog.lua`; backup em `ServerStorage.BeforeShadowGarden_20260929.AudioCatalog`.
- **Origem e uso:** gravação da biblioteca de música licenciada do Roblox.
  - Asset publicado no Creator Store pela conta `APMOfficial` (APM Music, parceira de licenciamento do Roblox; biblioteca Sonia Classic, descrição "Courtesy of APM Music").
  - É a mesma fonte das outras músicas de área do jogo (o `AudioCatalog` já registra "Licensed Roblox library sources").
  - A composição é de domínio público. A GRAVAÇÃO **não** é domínio público: o uso vale dentro de experiências Roblox pela licença do catálogo.
  - Nada foi baixado nem reenviado de serviço externo.
- **Sistema:** o existente (`SomJogo`, duas faixas com crossfade por área). Nenhum sistema novo.
  - Castelo, alquimia e masmorra ficam na mesma área, então a música NÃO reinicia.
  - O `CeuSombras` troca só o `SoundService.AmbientReverb`: StoneRoom no Mining Hall e na alquimia, StoneCorridor na masmorra. Restaura ao sair.
- **Teste no Play:**
  - Dragon Ball → Shadow Garden: crossfade de cerca de 2 s e depois só a Moonlight Sonata;
  - pátio → Mining Hall: continua em 33 s, com reverb;
  - Mining Hall → pátio: sem reverb, música contínua;
  - alquimia: reverb, música contínua;
  - masmorra: StoneCorridor, música contínua;
  - morte na masmorra: respawn no lobby do jogo, crossfade para a trilha do lobby, uma trilha só.
  - As outras áreas usam as mesmas faixas de antes.

## Overhaul de acabamento + pedidos do usuário (2026-09-30)
Export `58cdd0bf` (766 MeshParts, 745k tris estáticos, 749 colisões, 195 marcadores, 40 luzes), importado (766/766) e
montado. A fonte anterior ficou em `ServerStorage.IlhaShadowGarden_4ec5f0f0` (rollback: renomear). Os scripts antigos
(DungeonService, AlquimiaConfig, AlquimiaUI) estão em `ServerStorage.BeforeShadowGarden_20260930`.

- **Overhaul por setores 01–16:** folhas em `renders/overhaul/<setor>/`, cada uma em prévia e no modo roblox.
- **Salão do castelo maior:** nave 96 × 99 × 48, abside, arco triunfal, rosácea da lua e trono em cátedra gótica com assento fundo. A MiningZone passou a 90 × 89 e o salão tem 61 minérios no jogo.
- **Dungeon maior e infinita:** boca, túnel e vãos cabem um grupo; R1 48 × 48, R2 e R3 60 × 60.
  - As salas não têm fim e alternam R2/R3, com nível = 1 + floor((sala − 1) / 5).
  - HP, raridade e recompensa sobem com o nível; há bônus por sala e marco a cada 5 salas.
  - Cada sala tem tempo limite de 150 s.
  - Saída a qualquer momento pelo portal da R3 (toque) ou pela R1 (prompt).
- **Jardinagem "bonemeal":** kit `sg_garden.py` com cerca de 78k tris de capim e flores. O gramado visível das rotas ficou coberto, com jardins por casa e um jardim formal no pátio. FPS na vila: 56 (60 no resto).
- **Teste no Play:**
  - salão com os minérios;
  - trono;
  - vila e pátio;
  - dungeon:
    - entrada;
    - sala 1 com 17 minérios na R2;
    - limpeza, com teleporte para a sala 2 na R3;
    - pulo até a sala 5 e limpeza: marco, sala 6 no nível 2, HP 3300 → 4455;
    - 17 minérios quebrados com golpes reais (Golpear), com recompensa por minério e sala 7;
    - tempo da sala esgotado: FINISHING → RESETTING → WAITING, volta ao pátio;
    - morte: sai da corrida;
    - reentrada durante ENTRY_OPEN;
    - saída pela R1.
  - Output sem erros.
- **Correção de teste:** `debugAbrirEm` pula a abertura já encerrada no servidor.
- **Fotos no jogo:** `renders/ingame_final/`.
- **Pendente:** salvar o place. Os NPCs da vila e o pianista na entrada do castelo vêm depois desta avaliação.

## Efeitos visuais, luz da noite e export pós-finesse (2026-10-06)
**No Studio** (place Anime Mining Simulator, NÃO salvo pelo agente; backup das fontes em
`ServerStorage.BeforeEfeitosSG_20261006`):
- **Luz** (`AreaAtmosphere` perfil `[3]` + `CeuSombras`): ClockTime 3,5 põe a lua a 37° em -X, sobre o castelo
  para quem cruza a ponte. Lua 32 e 3500 estrelas. O skybox anime de dia é trocado pelo `sky512_*` padrão
  só na área. Atmosphere: Color (28,82,240), Decay (8,10,32), Density 0,22, Haze 1,05, Glare 0,15 e Offset 0,4.
  O resultado é zênite preto descendo para a faixa azul elétrico do horizonte. Ambient (112,118,162),
  OutdoorAmbient (122,132,186) e luar ColorShift_Top (178,198,255). Contraste e saturação +0,1. Bloom 0,55/36/1,15.
  O `AreaAtmosphere` passou a aceitar `cst/csb/glare/offset` por perfil; as outras áreas seguem como antes.
- **`StarterPlayerScripts.EfeitosShadowGarden`** (novo, só cliente, culling por distância):
  - Invocação:
    - círculo de runas girando no piso;
    - motas subindo;
    - 2 fitas em espiral até a esfera;
    - halo e cintilas no núcleo;
    - névoa escorrendo da porta.
  - Ao invocar: carga → flash + onda + coluna na cor da raridade. Os outros jogadores veem na hora; quem
    invocou vê quando a tela da estrela fecha. O `PadGacha` neon vazava luz por uma fresta do piso e fica
    invisível neste cliente.
  - Portal do Salão Sombrio:
    - núcleo escuro;
    - vórtice em 2 velocidades;
    - borda clara;
    - sucção;
    - névoa rasteira;
    - a `L_SGCave_Portal` pulsa (sem luz nova: teto de 6 na caverna).
    - O neon da malha do vórtice é escurecido no cliente. A força sobe com `MasmorraEstado.Estado = ENTRY_OPEN`.
  - Portais das salas (`MasmorraProxima_*`): selado tem véu escuro com runas; aberto tem vórtice + sucção, e a
    placa é escurecida no cliente (o lilás neon estourava em branco).
- **`Core.Main`**: `RolarGacha` dispara `Remotes.InvocacaoFX(areaId, userId, melhorRaridade)` (só visual, em pcall).
- **`JardimSombrasIsland`**: saíram as faíscas fracas Sum_Energia/Dun_Portal (o portão DS ficou como estava).
- **Testado no Play:**
  - portal aberto e selado;
  - sala aberta e selada (simulada no cliente);
  - ato lendário;
  - plano da ponte com a lua;
  - Output sem erros.

**Export `7fc3e990`** (build atual com finesse3/3B/3C: 862.655 tris no .blend, QA verde): 14 FBX, 854 MeshParts,
853k tris estáticos, 281 marcadores (iguais aos do b4d23c3b). Gravado com `SG_BUDGET=warn`. As metas globais
estão dentro, mas 4 limites por dono estouraram:
- castelo: 141/135 MeshParts;
- caverna: 74/65 MeshParts;
- props: 37,5k/30k tris e 51/50 MeshParts;
- luzes de dia: 49/48.

**PENDENTE:** importar os FBX `ILHA3_*_7fc3e9` + montar. Isso exige a interface do Studio
(File > Import; o ribbon está recolhido nesta versão). Não foi feito porque o usuário estava usando o PC.
Depois: salvar o place.
