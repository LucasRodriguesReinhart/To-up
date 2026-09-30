# Marcadores da onda 0 (planta v4) - posicoes ROBLOX (export de teste 6e214e20)

Frente de cada marcador = `fwd` (props fwd_x/fwd_z). Os DUN_ORE_* (46), ORE_* (80), GP_Block_* e PATH_ENTRY_CENTER_nn estao so no JSON (`marcadores_onda0.json`).

## Trono e escada (TronoService)

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `CAVE_Stair_Up` | (-1266.65, -12.00, 730.41) | (-0.985, 0, 0.174) | prompt=Subir ao salao; to=THRONE_Return; optional=True |
| `THRONE_Interact` | (-1417.85, 54.60, 771.28) | (0.985, 0, -0.174) | prompt=Tocar o trono; hold=0.5; dist=10.0 |
| `THRONE_OpenZone` | (-1432.87, 54.60, 773.93) | (-0.985, 0, 0.174) | sx=18.0; sy=25.5; sz=14.0 — caixa (centro na base): nao fecha o trono com jogador dentro |
| `THRONE_Park` | (-1432.47, 54.60, 745.94) | (0.985, 0, -0.174) | travel=27.5; tween_s=3.0 — pivo do trono recolhido no bolso da parede leste |
| `THRONE_Rest` | (-1427.70, 54.60, 773.02) | (0.985, 0, -0.174) | sx=14.0; sy=11.0; sz=20.0 — pivo do trono em repouso (base no piso do presbiterio; frente = nave) |
| `THRONE_Return` | (-1409.97, 54.60, 769.89) | (0.985, 0, -0.174) |  — destino do atalho 'Subir' (prompt em CAVE_Stair_Up), no presbiterio |
| `THRONE_Stair_Bottom` | (-1435.58, 6.60, 774.41) | (0.985, 0, -0.174) |  — saida da escada caracol na galeria do salao sombrio |
| `THRONE_Stair_Top` | (-1441.98, 54.60, 775.54) | (-0.985, 0, 0.174) | prompt=Abrir passagem — patamar de topo da escada caracol (dentro do arco secreto) |

## Masmorra (DungeonService)

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `DUNGEON_Entrance` | (-1248.46, -10.40, 741.42) | (-0.985, 0, 0.174) | radius=8.0 — zona/prompt de entrada na corrida (so com ENTRY_OPEN); <= 14 do marcador |
| `DUNGEON_ExitPortal` | (-1331.42, -72.00, 800.72) | (-0.174, 0, -0.985) |  — saida por PROMPT ('Sair', hold 0,6); sem barreira de toque [alias de DUN_EXIT_R3] |
| `DUNGEON_Hall` | (-1240.58, -10.40, 740.03) | (-0.985, 0, 0.174) | radius=13.0; ring_y_local=100.0 — portal/vortice da masmorra no fundo sul do salao sombrio (frente = para o norte, quem chega) |
| `DUNGEON_Portal` | (-1240.58, -10.40, 740.03) | (-0.985, 0, 0.174) | radius=13.0; ring_y_local=100.0 — portal/vortice da masmorra no fundo sul do salao sombrio (frente = para o norte, quem chega) [alias de DUNGEON_Hall para as particulas do JardimSombrasIsland] |
| `DUNGEON_Return` | (-1270.13, -11.80, 745.24) | (-0.985, 0, 0.174) |  — para onde o jogador volta ao sair/terminar (salao sombrio, na frente do portal, olhando a escada) |
| `DUNGEON_Spawn` | (-1155.89, -71.80, 725.09) | (-0.985, 0, 0.174) |  — chegada na R1 (frente = para a R2) |
| `DUNGEON_UI` | (-1235.66, 21.60, 739.16) | (-0.985, 0, 0.174) | ui=BillboardGui/SurfaceGui: estado e contagem da dungeon (XX:00 / XX:30); w=22.0; h=6.0 |
| `DUN_EXIT_R1` | (-1142.80, -72.00, 753.25) | (-0.985, 0, 0.174) |  — saida por PROMPT ('Sair', hold 0,6); sem barreira de toque |
| `DUN_EXIT_R3` | (-1331.42, -72.00, 800.72) | (-0.174, 0, -0.985) |  — saida por PROMPT ('Sair', hold 0,6); sem barreira de toque |
| `DUN_LINK_R1R2` | (-1227.78, -72.00, 737.77) | (-0.985, 0, 0.174) | w=28.0; h=22.0; t=2.0 — vao de ligacao (largura w perpendicular a frente, altura h); centro no plano medio da parede |
| `DUN_LINK_R2R3` | (-1332.17, -72.00, 756.18) | (-0.985, 0, 0.174) | w=28.0; h=22.0; t=2.0 — vao de ligacao (largura w perpendicular a frente, altura h); centro no plano medio da parede |
| `DUN_NEXT_R2` | (-1332.17, -72.00, 756.18) | (-0.985, 0, 0.174) | w=27.0; h=21.0; t=1.0; room=R2 — portal da PROXIMA sala (e o selo enquanto a sala nao limpa): Part (w, h, t) com CFrame = marcador * (0, h/2, 0); DENTRO do plano medio do vao (R2) / nicho (R3) |
| `DUN_NEXT_R3` | (-1436.56, -72.00, 774.58) | (-0.985, 0, 0.174) | w=27.0; h=21.0; t=1.0; room=R3 — portal da PROXIMA sala (e o selo enquanto a sala nao limpa): Part (w, h, t) com CFrame = marcador * (0, h/2, 0); DENTRO do plano medio do vao (R2) / nicho (R3) |
| `DUN_ROOM_R1` | (-1185.43, -72.00, 730.30) | (-0.985, 0, 0.174) | sx=84.0; sy=84.0; floor=-72.0; ceil=-28.0 — frente = eixo da fila de salas (R1 -> R2 -> R3) |
| `DUN_ROOM_R2` | (-1279.98, -72.00, 746.97) | (-0.985, 0, 0.174) | sx=104.0; sy=104.0; floor=-72.0; ceil=-28.0 — frente = eixo da fila de salas (R1 -> R2 -> R3) |
| `DUN_ROOM_R3` | (-1384.37, -72.00, 765.38) | (-0.985, 0, 0.174) | sx=104.0; sy=104.0; floor=-72.0; ceil=-28.0 — frente = eixo da fila de salas (R1 -> R2 -> R3) |
| `DUN_SPAWN_R2` | (-1238.61, -71.80, 739.68) | (-0.985, 0, 0.174) |  — spawn do grupo ao entrar nesta sala (espalhar em volta; sem minerio a menos de 14) |
| `DUN_SPAWN_R3` | (-1343.00, -71.80, 758.09) | (-0.985, 0, 0.174) |  — spawn do grupo ao entrar nesta sala (espalhar em volta; sem minerio a menos de 14) |

## Salao sombrio

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `CAVE_Zone` | (-1346.94, -12.00, 758.78) | (-0.985, 0, 0.174) | sx=180.0; sy=248.0; h=53.0; floor=-12.0 — salao sombrio: reverb Cave e corte do SUBSOLO no cliente |

## Agua (Roblox)

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `FX_Fall_1_Base` | (-1045.82, -53.00, 900.14) | (0.174, 0, 0.985) | fx=nevoa_base |
| `FX_Fall_1_Lip` | (-1046.60, 42.98, 895.71) | (0.174, 0, 0.985) | fx=nevoa_borda; width=5.4 — borda da bica de pedra (nivel da pedra); agua do Roblox |
| `FX_Fall_1_Step` | (-1046.05, 20.00, 898.86) | (0.174, 0, 0.985) | fx=espuma_degrau |
| `FX_Fall_2_Base` | (-972.20, -53.00, 511.45) | (-0.174, 0, -0.985) | fx=nevoa_base |
| `FX_Fall_2_Lip` | (-971.42, 34.98, 515.88) | (-0.174, 0, -0.985) | fx=nevoa_borda; width=3.8 — borda da bica de pedra (nivel da pedra); agua do Roblox |
| `FX_Fall_2_Step` | (-971.97, 20.00, 512.73) | (-0.174, 0, -0.985) | fx=espuma_degrau |
| `FX_Fall_3_Base` | (-1509.01, -53.00, 849.46) | (-0.906, 0, 0.423) | fx=nevoa_base |
| `FX_Fall_3_Lip` | (-1504.93, 50.98, 847.56) | (-0.906, 0, 0.423) | fx=nevoa_borda; width=5.4 — borda da bica de pedra (nivel da pedra); agua do Roblox |
| `FX_Fall_3_Step` | (-1507.83, 20.00, 848.92) | (-0.906, 0, 0.423) | fx=espuma_degrau |
| `FX_Fall_4_Base` | (-839.76, -53.00, 700.86) | (0.500, 0, 0.866) | fx=nevoa_base |
| `FX_Fall_4_Lip` | (-842.01, 29.98, 696.96) | (0.500, 0, 0.866) | fx=nevoa_borda; width=3.8 — borda da bica de pedra (nivel da pedra); agua do Roblox |
| `FX_Fall_4_Step` | (-840.41, 20.00, 699.74) | (0.500, 0, 0.866) | fx=espuma_degrau |
| `WATER_CaveFall_Base` | (-1363.38, -13.50, 688.57) | (0.985, 0, -0.174) | fx=nevoa_base |
| `WATER_CaveFall_Lip` | (-1369.29, 35.00, 689.61) | (0.985, 0, -0.174) | width=4.0; drop=48.5; to=WATER_CavePool — queda da fenda NE da caverna |
| `WATER_CavePool` | (-1343.00, -13.50, 758.09) | (-0.174, 0, -0.985) | sx=172.0; sy=24.0; level=-13.5; floor=-15.0; depth=1.5 — rio escuro (lamina parada, quase preta); a ponte do eixo atravessa (x +-8) |
| `WATER_Court_L` | (-1152.77, 52.80, 777.35) | (-0.985, 0, 0.174) | sx=20.0; sy=32.0; level=52.8; floor=52.3; depth=0.5 — espelho d'agua do patio-jardim (reflete a fachada); borda de pedra ate P3+0,8 |
| `WATER_Court_R` | (-1170.83, 52.80, 674.92) | (-0.985, 0, 0.174) | sx=20.0; sy=32.0; level=52.8; floor=52.3; depth=0.5 — espelho d'agua do patio-jardim (reflete a fachada); borda de pedra ate P3+0,8 |
| `WATER_Fountain_Basin` | (-919.54, 38.25, 683.42) | (-0.174, 0, -0.985) | radius=6.05; apothem=5.84; sides=12; depth=0.5; hole_r=1.6 — bacia dodecagonal; fwd aponta para um vertice; agua do Roblox |
| `WATER_Fountain_Bowl_1` | (-919.54, 42.44, 683.42) | (-0.362, 0, -0.932) | radius=2.9; sides=16; depth=0.29; hole_r=0.62 |
| `WATER_Fountain_Bowl_2` | (-919.54, 45.20, 683.42) | (-0.362, 0, -0.932) | radius=1.5; sides=16; depth=0.2; hole_r=1.17 |
| `WATER_Fountain_Spout_1` | (-919.89, 45.20, 681.40) | (-0.174, 0, -0.985) | from=Bowl_2; to=Bowl_1; drop=2.76; land_pos_x=-919.962; land_pos_y=42.44; land_pos_z=681.005 — ponta da bica no nivel da agua; fwd = direcao do jato |
| `WATER_Fountain_Spout_2` | (-921.55, 45.20, 683.77) | (-0.985, 0, 0.174) | from=Bowl_2; to=Bowl_1; drop=2.76; land_pos_x=-921.949; land_pos_y=42.44; land_pos_z=683.843 — ponta da bica no nivel da agua; fwd = direcao do jato |
| `WATER_Fountain_Spout_3` | (-919.18, 45.20, 685.44) | (0.174, 0, 0.985) | from=Bowl_2; to=Bowl_1; drop=2.76; land_pos_x=-919.111; land_pos_y=42.44; land_pos_z=685.831 — ponta da bica no nivel da agua; fwd = direcao do jato |
| `WATER_Fountain_Spout_4` | (-917.52, 45.20, 683.06) | (0.985, 0, -0.174) | from=Bowl_2; to=Bowl_1; drop=2.76; land_pos_x=-917.124; land_pos_y=42.44; land_pos_z=682.992 — ponta da bica no nivel da agua; fwd = direcao do jato |
| `WATER_Fountain_Spout_5` | (-922.49, 42.44, 681.35) | (-0.819, 0, -0.574) | from=Bowl_1; to=Basin; drop=4.19; land_pos_x=-923.1; land_pos_y=38.25; land_pos_z=680.923 — ponta da bica no nivel da agua; fwd = direcao do jato |
| `WATER_Fountain_Spout_6` | (-921.60, 42.44, 686.37) | (-0.574, 0, 0.819) | from=Bowl_1; to=Basin; drop=4.19; land_pos_x=-922.031; land_pos_y=38.25; land_pos_z=686.981 — ponta da bica no nivel da agua; fwd = direcao do jato |
| `WATER_Fountain_Spout_7` | (-916.59, 42.44, 685.48) | (0.819, 0, 0.574) | from=Bowl_1; to=Basin; drop=4.19; land_pos_x=-915.973; land_pos_y=38.25; land_pos_z=685.913 — ponta da bica no nivel da agua; fwd = direcao do jato |
| `WATER_Fountain_Spout_8` | (-917.47, 42.44, 680.47) | (0.574, 0, -0.819) | from=Bowl_1; to=Basin; drop=4.19; land_pos_x=-917.041; land_pos_y=38.25; land_pos_z=679.854 — ponta da bica no nivel da agua; fwd = direcao do jato |

## Mundo / portao

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `GATE_DemonSlayer` | (-1513.04, 52.20, 944.45) | (-0.766, 0, 0.643) | open_w=16.0; open_h=18.0; deck_w=18.0; area_id=4; key=DemonSlayer |
| `GATE_DemonSlayer_EXIT` | (-1522.24, 52.40, 952.16) | (-0.766, 0, 0.643) | gate=DemonSlayer |
| `GATE_DemonSlayer_INTERACT` | (-1507.68, 52.40, 939.95) | (-0.766, 0, 0.643) | gate=DemonSlayer; radius=10.0 |
| `GATE_DemonSlayer_LOCKED` | (-1513.04, 61.20, 944.45) | (-0.766, 0, 0.643) | gate=DemonSlayer; state_default=locked |
| `GATE_DemonSlayer_OpenFX` | (-1513.04, 61.20, 944.45) | (-0.766, 0, 0.643) | gate=DemonSlayer; state=unlocked; fx=abertura |
| `ISLAND_EXIT_ShadowGarden` | (-1454.83, 52.20, 895.59) | (-0.766, 0, 0.643) | width=18.0; deck_z=52.2; heading_deg=140.0; heading_deg_local=120.0 |
| `ISLAND_NEXT_ANCHOR_DemonSlayer` | (-1534.49, 52.20, 962.44) | (-0.766, 0, 0.643) | width=18.0; deck_z=52.2; clear_h=22.0; heading_deg=140.0; next_area=4; next_key=DemonSlayer; fwd_roblox=-0.7660,0.0000,0.6428; guard=PROVISORIO: COL_SGAnchorGuard_* (next_island_guard=True); guard_note=a integracao da ilha Demon Slayer REMOVE o guarda quando a ponte seguinte encosta aqui; heading_deg_local=120.0 |
| `WORLD_ENTRY_ShadowGarden` | (-870.30, 36.40, 674.74) | (-0.985, 0, 0.174) |  — chegada da ilha (depois do portico B, olhando a praca e o castelo) |
| `WORLD_FROM_PREV` | (-579.23, 28.20, 650.73) | (-0.920, 0, -0.391) | width=18.0; deck_z=28.2; prev=ISLAND_NEXT_ANCHOR_ShadowGarden (Ilha 2 Dragon Ball); bridge_len=234.1 — centro da borda do tabuleiro da ponte de chegada (curva de 33 graus, 232); avanco = frente |

## Mineracao

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `MiningZone_ShadowGarden` | (-1283.91, 52.20, 747.67) | (-0.985, 0, 0.174) | kind=mining; floor=52.2; sx=104.0; sy=136.0; ceil=136.2 — Mining Hall (dentro do castelo); o jogo usa ORE_* + grade hexagonal + bloqueios GP_Block_* |

## Invocacao / alquimia

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `CRAFT_Station` | (-1072.92, 44.20, 596.74) | (0.174, 0, 0.985) |  — caldeirao/bancada do alquimista: ProximityPrompt 'Craft' abre a pagina de receitas |
| `NPC_Craft` | (-1073.96, 44.90, 590.83) | (0.174, 0, 0.985) |  — alquimista atras do caldeirao, olhando a porta |
| `PLAYER_INTERACT_Craft` | (-1072.05, 45.60, 601.66) | (-0.174, 0, -0.985) | radius=8.0 |
| `SUMMON_Interact` | (-883.24, 40.20, 889.24) | (-0.985, 0, 0.174) |  — gabinete invisivel do Gacha_sombra (prompt Invocar) |
| `SUMMON_Main` | (-882.03, 40.20, 896.14) | (-0.174, 0, -0.985) |  — torre de invocacao (familia das Ilhas 1 e 2), frente para +X (ponte) |
| `SUMMON_PlayerPosition` | (-884.81, 40.20, 880.38) | (0.174, 0, 0.985) |  — onde o jogador fica olhando a torre (pad do gacha) |

## Audio

| nome | pos (X, Y, Z) | fwd | atributos |
|---|---|---|---|
| `AUDIO_Cave` | (-1346.94, 2.00, 758.78) | (-0.985, 0, 0.174) | family=wind; range=140.0 |
| `AUDIO_CaveWater` | (-1353.42, -12.00, 699.00) | (-0.985, 0, 0.174) | family=water; range=70.0 |
| `AUDIO_Craft` | (-1072.92, 47.20, 596.74) | (-0.985, 0, 0.174) | family=fire; range=26.0 |
| `AUDIO_DungeonPortal` | (-1240.58, -4.00, 740.03) | (-0.985, 0, 0.174) | family=energy; range=44.0 |
| `AUDIO_DungeonRooms` | (-1289.82, -62.00, 748.71) | (-0.985, 0, 0.174) | family=wind; range=160.0 |
| `AUDIO_Forge` | (-1283.75, -9.00, 817.70) | (-0.985, 0, 0.174) | family=fire; range=34.0 |
| `AUDIO_Fountain` | (-919.54, 38.20, 683.42) | (-0.985, 0, 0.174) | family=water; range=40.0 |
| `AUDIO_HallAmbience` | (-1283.91, 60.20, 747.67) | (-0.985, 0, 0.174) | family=wind; range=110.0 |
| `AUDIO_Summon` | (-882.03, 46.20, 896.14) | (-0.985, 0, 0.174) | family=energy; range=36.0 |
| `AUDIO_Waterfall_1` | (-1046.60, 33.20, 895.71) | (-0.985, 0, 0.174) | family=water; range=60.0 |
| `AUDIO_Waterfall_2` | (-971.42, 25.20, 515.88) | (-0.985, 0, 0.174) | family=water; range=60.0 |
| `AUDIO_Waterfall_3` | (-1504.93, 41.20, 847.56) | (-0.985, 0, 0.174) | family=water; range=60.0 |
| `AUDIO_Waterfall_4` | (-842.01, 20.20, 696.96) | (-0.985, 0, 0.174) | family=water; range=60.0 |
