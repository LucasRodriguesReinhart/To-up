# Ilha 4 Demon Slayer: brief da onda 6b (finesse)

## Base
- **Fonte dos itens:** `renders/onda6/AUDITORIA_DS.md` (56 itens: 21 P, 35 L), com evidências em `renders/onda6/aud/` e a planta numerada `aud/A00_planta_itens.jpg`.
- **Regras gerais:** `DS_BRIEF.md` continua valendo inteiro.
- **O que vale é o Roblox:** sem textura, com bloom e na altura do jogador. Veja as capturas reais em `renders/ingame/`.
- **Valide sempre** com `FM_MAT_PREVIEW=roblox`. Câmera com olho a +5,5 do piso.

## Regras desta onda
- **Escopo:** só os itens do seu grupo, só nos arquivos do seu grupo.
  - Todos os P são obrigatórios.
  - Faça os L que couberem no orçamento.
  - Se um item exigir mexer em arquivo de outro grupo, não mexa: descreva no relatório.
- **Não mude** planta, cotas, rotas, marcadores nem colisões de rota. O QA tem de continuar 12/12 + 4/4 internas, com `CLAREIRA_LIVRE` e `CLAREIRA_PISO` OK.
- **Orçamento:** a ilha está em 580k / 498 MeshParts / col 1233. O teto é 600k / 650 / 1300.
  - O seu grupo pode crescer no máximo o indicado no seu prompt.
  - Pague com cortes onde não se vê, como fundos e faces de baixo.
- **Z-fight:** nenhuma face exposta a menos de 0,12 de outra de material diferente.
- **Builds de teste:** `DS_OUT=<scratchpad>/ds_fin_<sigla>/teste.blend`. O build oficial só acontece no fim.
  - Se outro agente estiver no meio de um build oficial, espere e refaça.
  - O build tem de ser determinístico: 2 builds dão o mesmo número de tris.
- **Proibido:**
  - Roblox Studio MCP, Blender MCP ao vivo, computer-use, browser;
  - commit e taskkill;
  - mexer em `..\ilha_shadowgarden\`, `fm_lib.py` e `export_roblox.py`;
  - modelar minérios.
- **Blender:** sempre com `--factory-startup`. Renders em 960×540.
- **Portão One Piece (`il_gate_op`):** foi aprovado pelo usuário. Não redesenhe.

## Entrega
- **Voltas:** no mínimo 3 de render, crítica ("isso sobreviveria a close-up na altura do jogador?") e correção.
- **Folhas:** em `renders/onda6/fin_<sigla>/`, antes × depois de cada item, usando as mesmas câmeras da auditoria. Os runners da auditoria estão em `scratchpad/ds_aud/`.
- **QA:** build completo + `./run.sh qa` OK.
- **Relatório curto:** item a item (feito / parcial / não feito e por quê), orçamento e pendências.
