# Integracao do lobby Wolfberg no Roblox Studio (roteiro)

Pre-requisitos: `lobby_wolfberg.blend` montado (`build_wb.py`), `wb_qa.py` sem falhas, `export_wb.py` gerado em `export/`
(LOBBY_WB_<grupo>_<id6>.fbx + montar_lobby_wolfberg.lua + lobby_wb_data.json). Studio alvo aberto (copia
AMS_Lobby_Champions_Avaliacao.rbxl ou o place que o usuario liberar), MCP conectado. AVISAR as outras sessoes antes.

1. Servidor http (Git Bash, pasta `lobby_area/wolfberg`): `python -m http.server 8773` (8772 e 8776 sao de outras sessoes).
2. Backup no Studio alvo (Edit, execute_luau): `workspace.LOBBY_FORJA` -> `ServerStorage.LOBBY_FORJA_antes_Wolfberg_<data>`
   (Clone + Destroy), idem `Lighting` (copia das propriedades) e objetos soltos (Mystical Spawn Point.SpawnLobby, MailBox,
   LojaMochilas.PadLoja, NPCs['npc vendedor ']) em `ServerStorage.LobbySoltos_antes_Wolfberg`.
3. Importar os FBX UM POR VEZ (o Import Preview do ultimo fica escondido com varios na fila), com o Studio alvo na
   frente: `STUDIO_TITLE='*AMS_Lobby_Champions*' powershell -ExecutionPolicy Bypass -File ilha_dragonball/tools/import_preview_one.ps1 -Folder <pasta export, caminho Windows> -File LOBBY_WB_02_TERRAIN_<id6>.fbx`
   (File > Import (17,33)->(42,182), dialogo Win32, Start Import (1867,891), Import Preview -> Import (1275,856)).
   Cada FBX entra como Model em workspace; o montar junta tudo em `workspace.LOBBY_FORJA` (ALINHAR = true).
   ESPERAR as texturas processarem (MeshParts brancas por alguns minutos).
4. Montar (Edit): `loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8773/export/montar_lobby_wolfberg.lua"))()`
   - confere/alinha as MeshParts, SurfaceAppearance das texturas, colisoes, marcadores, luzes (NightOnly), VOID_CATCH,
     Script LOBBY_FORJA_Servidor, CONTRATO (Santuario.Portal1..6, LobbyRevision, Top100Origin + PivotTo do GlobalTop100,
     POSICIONAR_JOGO move SpawnLobby/MailBox/PadLoja/npc vendedor), VFX (particulas) + LocalScript de tremor.
   - `APLICAR_LIGHTING = true` so na copia (perfil de dia quente de wb_lights.LOBBY_PROFILE); no place oficial o perfil
     vai para o AreaAtmosphere da area 0.
5. Ignis golem (se o Studio alvo nao tiver o golem novo): servidor 8773 em `output/ignis_golem_20261007` e
   `local f = loadstring(HttpService:GetAsync("http://127.0.0.1:8773/roblox/rebuild_ignis.lua"))(); print(f({root = CFrame.new(-0.9, 7, -60.7), parent = workspace.NPCs}))`
   + clonar o LetreiroIgnis do lobby antigo (~14 acima do root).
6. `ServerScriptService.Core.LobbyLayout`: trocar os Vector3 pelos valores do cabecalho do montar (script_read + multi_edit):
   Spawn (0, 10.3, 32), Shop (62, 10.9, -9), ShopFacing (72, 10.9, -9), Ignis (-0.9, 10.5, -46), PortalIsland (-100, 10.5, 58).
7. GlobalTop100: se nao existir dentro do LOBBY_FORJA, `Top100Builder.Build(root, {OriginCF = root:GetAttribute('Top100Origin')})`.
8. Play (Server+Client): spawn olhando a forja; prompt do Ignis; loja (porta, PadLoja, NPC atras do balcao); mural;
   portais 1..6 (Disco toca -> Main); ponte a pe ate a Ilha 1 (z 222); FPS; luzes/VFX; sem buracos (VOID_CATCH).
   `screen_capture` derruba o Play: capturas so no Edit ou pelo shots_ingame.ps1.
9. Nunca salvar o place. Relatorio + capturas para o usuario; so depois do OK dele levar ao place oficial.
