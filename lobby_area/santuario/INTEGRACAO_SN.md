# Integracao do lobby Santuario do Deus-Ferreiro no Roblox Studio (roteiro)

SO DEPOIS DO OK DO USUARIO NOS RENDERS. Nunca salvar o place (o usuario salva). Avisar as outras sessoes antes de usar
o Studio ou dar Play. Nunca usar SendKeys.

Pre-requisitos: `renders/build/build.blend` montado (`sn_build.py`), `sn_qa.py` com QA OK, export gerado em `export/`
(LOBBY_SN_<grupo>_<id6>.fbx + montar_lobby_santuario.lua + lobby_sn_data.json). Studio alvo aberto (copia de avaliacao
ou o place que o usuario liberar), MCP conectado.

1. Servidor http (Git Bash, pasta `lobby_area/santuario`): `python -m http.server 8774` (8772/8773/8776 sao de outras
   sessoes). Desligar no fim.
2. Backup no Studio alvo (Edit, execute_luau): `workspace.LOBBY_FORJA` -> `ServerStorage.LOBBY_FORJA_antes_Santuario_<data>`
   (Clone + Destroy), idem as propriedades do `Lighting` (atributos) e objetos soltos (Mystical Spawn Point.SpawnLobby,
   MailBox, LojaMochilas.PadLoja, NPCs['npc vendedor ']) em `ServerStorage.LobbySoltos_antes_Santuario`.
3. Importar os 7 FBX UM POR VEZ (Import 3D; o Import Preview do ultimo fica escondido com varios na fila), com o
   Studio alvo na frente (receita do importador sem foco: memoria studio-importer-sem-foco / import_preview_one.ps1).
   Cada FBX entra como Model em workspace; o montar junta tudo em `workspace.LOBBY_FORJA` (ALINHAR = true).
   ESPERAR as texturas processarem (MeshParts brancas por alguns minutos): sao 40 atlas de pintura assada (SNB_*).
4. Montar (Edit): `loadstring(game:GetService("HttpService"):GetAsync("http://127.0.0.1:8774/export/montar_lobby_santuario.lua"))()`
   - alinha as MeshParts, aplica a SurfaceAppearance de cada atlas, colisoes (Parts invisiveis), marcadores, luzes
     (braseiros NightOnly), VOID_CATCH, CONTRATO (Santuario.Portal1..6 com Disco/AreaId, LobbyRevision 'Santuario',
     Top100Origin + PivotTo do GlobalTop100 para as Tabuas dos Campeoes, POSICIONAR_JOGO move SpawnLobby/MailBox/
     PadLoja/npc vendedor), VFX (fogo, brasas, poeira dourada, faiscas de runa, folhas, brilho dos cristais) + tremor
     das luzes de fogo, letreiros das estacoes.
   - `APLICAR_LIGHTING = true` so na copia (perfil de manha clara de sn_lights.LOBBY_PROFILE); no place oficial o
     perfil vai para o AreaAtmosphere da area 0.
5. Ignis golem: o contrato e o mesmo (Root (-0.9, 7, -60.7) olhando +Z, piso Y 7, envoltoria livre - conferida no
   sn_qa). Se o Studio alvo nao tiver o golem novo, usar o rebuild_ignis.lua de output/ignis_golem_20261007.
6. `ServerScriptService.Core.LobbyLayout`: trocar os Vector3 pelos valores do cabecalho do montar:
   Spawn (0, 13.3, 64), Shop (71.146, 11.7, -33.175), ShopFacing (76.583, 11.7, -35.711), Ignis (-0.9, 10.5, -46),
   PortalIsland (-51.968, 10.5, -1.815).
7. GlobalTop100: se nao existir dentro do LOBBY_FORJA, `Top100Builder.Build(root, {OriginCF = root:GetAttribute('Top100Origin')})`.
8. Play (Server+Client): spawn olhando a forja; prompt do Ignis; loja (porta, PadLoja, NPC atras do balcao); tabuas;
   portais 1..6 (Disco toca -> Main); ponte a pe ate a Ilha 1 (z 222, cota 6); FPS; luzes/VFX; sem buracos.
   `screen_capture` derruba o Play: capturas so no Edit.
9. Nunca salvar o place. Relatorio + capturas para o usuario; so depois do OK dele levar ao place oficial.
