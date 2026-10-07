# Importar o kit Shadow Garden

Arquivo a selecionar no importador 3D do Roblox Studio:

`C:\Users\lucas\OneDrive\Desktop\To up\shadowgarden_area\export\shadowgarden_kit.fbx`

Use o criador **LSation**, proprietário da experiência. Preserve a hierarquia dos modelos `K_*`, os marcadores `__origem` e as texturas. O atlas também está em `export/SG_Palette.png` caso o importador solicite o arquivo.

O arquivo contém uma biblioteca de módulos sobrepostos na origem; essa é a forma de exportação do kit. O cenário completo é montado pelo manifesto depois da normalização dos pivôs.

Depois da importação, a continuação técnica é:

1. Inspecionar o modelo importado, confirmar 61 grupos `K_*` e suas malhas/IDs/escala.
2. Executar o conteúdo de `finalize_import.lua` na barra de comandos ou pela integração do Studio. O modelo de entrada esperado chama-se `shadowgarden_kit` em Workspace. Se o importador alterar a hierarquia ou escala, corrigir com base no resultado observado antes de executar.
3. Iniciar Play. `IslandWorld` passa a usar `Core.ShadowGardenIsland` para a Área 4 quando `ServerStorage.ShadowGardenKit` existir.
4. Fazer os testes finais listados em `STATUS.md` e limpar os objetos de prévia.

Os scripts da área já estão preparados no Studio. A importação não foi automatizada até o fim porque o controle do seletor de arquivos falhou. O lugar não foi salvo/publicado.
