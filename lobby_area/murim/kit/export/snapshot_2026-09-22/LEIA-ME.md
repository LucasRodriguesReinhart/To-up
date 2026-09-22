# Snapshot externo do lobby - 2026-09-22 (pos F16/F17, pre F18)

Persistencia criada porque o place NAO pode ser salvo remotamente (Ctrl+S exige
acao local e o acesso de tela foi negado com reason=user_denied).

## Conteudo e alcance
- `index_cena.json` - 187 containers (Folders/Models) de LOBBY_MURIM, Santuario,
  LojaMochilas e NPCs + Lighting (propriedades e 5 efeitos).
- `parts_0001-0300.json` ... `parts_3301-3952.json` - chunks brutos exportados.
- `parts_tudo.json` - merge validado: **3.952 BaseParts** com CFrame (12 floats),
  Size, Color, Material, Transparency, CanCollide, Shape, MeshId/TextureID.
- `restaurar_snapshot.lua` - verificacao (padrao) e reconstrucao de pecas ausentes.

## O que este snapshot NAO cobre (declarado)
- Luzes, ParticleEmitters, Decals, atributos, scripts e joints: ficam de fora.
  As luzes/particulas das fases hex sao recriaveis rodando os `hex_*.lua`.
- SurfaceAppearance dos MeshParts: recriada pelo asset do MeshId quando o
  CreateMeshPartAsync devolve a malha com aparencia; caso contrario a peca volta
  como Part bloco (fallback declarado no script).
- Ele NAO substitui o Ctrl+S: e uma rede de seguranca de layout, suficiente para
  reconstruir a geometria e retomar producao, nao um .rbxl identico.

## Como restaurar
1. `python -m http.server 8766` nesta pasta.
2. No command bar do Studio: loadstring(game.HttpService:GetAsync("http://127.0.0.1:8766/restaurar_snapshot.lua",true))()
3. Rodar primeiro em MODO "verificar" (so relata); mudar para "reconstruir" so
   depois de conferir o relatorio.
