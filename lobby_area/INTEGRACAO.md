# Conhecimento de integracao Blender -> Roblox (lobby)

Registro do que foi aprendido nas versoes V9/V10 (arquivadas em `arquivo_v10/` e em `ServerStorage.LV10_Arquivo`).
As versoes visuais V9/V10 estao REJEITADAS como base artistica; o que vale daqui e so o conhecimento tecnico.

## Eixos e escala
- 1 unidade Blender = 1 stud. Blender (+X, +Y, +Z) -> Roblox (-X, +Z, +Y). Exportar FBX com `axis_forward='-Z'`, `axis_up='Y'`,
  `apply_scale_options='FBX_SCALE_ALL'`, `mesh_smooth_type='FACE'`, `path_mode='COPY'`, `embed_textures=True`.
- Marcador `_ORIGEM` (cubo em Blender (0,0,120)) em cada FBX: no Studio, `M:PivotTo(M:GetPivot() + (Vector3.new(0,120,0) - org.Position))`.

## Importacao (Studio)
- Home > Import 3D. Com computer-use: botao (570,83), campo do arquivo (343,379), Abrir (600,401), checkbox Anchored (~872,460),
  Import (~967,648). Se aparecer o banner "Have you imported this before?" os botoes descem.
- Numa 2a importacao o item pode ficar DESMARCADO na Import Queue: marcar o checkbox e clicar "Start Import".
- O importador cria `SurfaceAppearance` (ColorMap + NormalMap) a partir do Principled BSDF (Base Color + Normal Map node). Roughness
  ligado ao BSDF vira RoughnessMap. Nao precisa upload manual. Materiais so com cor viram `TextureID`/Color.
- Objetos com varios materiais sao FUNDIDOS num MeshPart: um objeto por material no Blender.
- Objetos > ~15k tris: dividir antes de exportar (o importador rejeita/simplifica).

## Materiais no Studio
- Nomear `PREFIXO__nome` e aplicar Material/Color/Reflectance por prefixo via script (`execute_luau`).
- SurfaceAppearance.Color escurece/clareia a textura (tint) sem reimportar: util para separar valor entre materiais.
- Neon so para elementos luminosos pequenos; Glass para cupulas; Metal para ouro com Reflectance baixa (<= .1).

## Colisao
- Padrao voxel deixa atravessar lajes finas: pisos/estruturas = `PreciseConvexDecomposition`.
- Meshes fundidos com componentes separados NAO podem usar `Box` (a caixa vira parede invisivel) e Precise pode ligar componentes
  distantes: decorativos (balaustres, troncos, canteiros) = `Default` (voxel) ou `CanCollide=false`.
- Aplicar colisao em LOTES (uma chamada com 30+ Precise derruba a bridge do MCP por ~1 min).
- `character_navigation` nao acha rota em escadas de mesh: testar com `Humanoid:MoveTo` em etapas, medindo posicoes e
  contando `Freefall`.

## Agua
- Terrain water em blocos retangulares vaza pelos cantos de margens curvas: preencher em faixas seguindo a margem
  (ou FillCylinder + recortes com Air) e checar com `Terrain:ReadVoxels`.
- A grade de voxels (4 studs) deixa agua abaixo do fundo modelado: fechar por baixo com laje/saia opaca.

## Ignis (funcional)
- NPC em `workspace.NPCs.Ignis` (modelo original; `ScaleTo` aplicado com atributo `EscalaOriginal` guardado).
- O `Main` cria `ProximityPrompt` "IgnisPrompt" no `belly` (MaxActivationDistance 18); `IgnisService.pertoDoIgnis` exige
  root a <= 22 studs do belly. Teste em Play: `pr:InputHoldBegin(); pr:InputHoldEnd()` abre a UI "Forja de Ignis";
  "Vender tudo" = `PlayerGui.ExpeditionUI.Canvas.ModalLayer.Window.Body.SaleSummary.SellAll` (clicar com `user_mouse_input`
  + `instance_path`). Fechar pelo `Window.Close` (o `Lighting.ExpeditionMenuBlur` fica ativo se so esconder a janela).

## Capturas limpas (Play)
- `StarterGui:SetCoreGuiEnabled(All,false)`; `ScreenGui.Enabled=false` em `PlayerGui`; `BillboardGui.Enabled=false`;
  `Humanoid.DisplayDistanceType=None`; unidades em `workspace.PetsVisuais` (Transparency=1 local). Studio: View > Screenshot
  salva em `OneDrive/Imagens/Roblox/RobloxScreenShot*.png`.

## Backups no ServerStorage
- `BeforeLobbyV9_*`, `BeforeLobbyV10_*`, `LV9_Guardado` (pecas V9), `LV10_Arquivo` (trechos V10 v1..v3), `VFX_Guardado_Lobby`
  (pacote VFX flutuante + 81 Parts soltas), `ParedesDeCusto_EditStale` (paredes antigas em z<0; `Paredes.build` recria em Play).
- Iluminacao: valores V9 guardados em atributos `V9_*` no Lighting e nos efeitos.
