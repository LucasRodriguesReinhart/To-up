# Ilha 4 Demon Slayer: brief comum das ondas de produção

A fonte de verdade é `PROMPT_USUARIO.md` (o prompt mestre do usuário). Leia de novo as seções 3, 4, 15–26, 33, 34, 37, 39 e 41. O plano aprovado é `plano/PLANO_DS.md`, e as referências são `ref/ref_01..05.jpg`, vistas do mesmo mapa. O blockout da onda 0 já passou no gate e está commitado (`ds_*.py`, `ilha_demonslayer.blend`, `renders/onda0/`).

## Leitura do lead sobre o blockout
O que precisa mudar na produção:
- **A ilha lê CHATA.** As referências mostram falésias altas em colunas, com terraços bem marcados e escadas de pedra entre eles. Os arrimos de pedra separam vila, clareira e forja, e a forja fica claramente NO ALTO, sobre um muro alto.
  - Hoje os desníveis existem (52 → 80), mas leem pouco: as bordas dos terraços são rampas e faixas finas, e a massa de baixo é rasa e em camadas.
  - O terreno precisa de MUROS DE ARRIMO e falésias verticais com leitura forte.
  - A quilha deve ser alta e em colunas de basalto e rocha, como nas referências (na `ref_01` a falésia ocupa metade do quadro).
- **A clareira é o vazio intencional**, mas a BORDA dela precisa de intenção: raízes, poucas pedras, cerca baixa em setores, transição de grama para terra.
- **Vida:** a densidade cresce do centro vazio para fora.
- **Caminhos:** são de terra e laje, com lanternas tōrō nos nós e cercas de madeira baixas. Nada de faixa cinza lisa.
- **Equilíbrio de destaque:** o summon dourado não pode ofuscar a forja. A forja é o herói.

## Craftsmanship desde o primeiro asset (seção 18 do prompt)
A ordem é SILHUETA → PROPORÇÃO → ESTRUTURA → ENCAIXE → ESPESSURA → BEVEL → MATERIAL → DETALHE → LUZ.

Considere NÃO FINAL tudo o que parecer:
- cubo colorido, cilindro com detalhe, esfera com emissive;
- primitivas empilhadas, inflável, detalhe colado;
- peça sem espessura;
- procedural não revisado.

A pergunta é sempre "um artista decidiu como essa forma deveria ser construída?".

## Realidade do Roblox (aprendida nas ilhas 1–3)
- **Sem textura no jogo.** A forma tem de ler sozinha. Valide SEMPRE também com `FM_MAT_PREVIEW=roblox`.
- **Neon claro vira branco com o bloom.** Luz quente só DENTRO de moldura (janela com caixilho, lanterna com gaiola), nunca um bloco inteiro de Neon.
- **Z-fight:** nenhuma face visível pode ficar coplanar, nem a menos de 0,12 de outra paralela de material diferente. Janela acesa fica ≥ 0,12 atrás do vidro. Piso sobre piso: ou o de baixo não existe, ou fica ≥ 0,3 abaixo.
- **Escala:** o avatar tem ~5 studs. Portas com ≥ 4 de vão livre (ideal 5–6), degraus com 0,6–0,8 de espelho.

## Regras
- **Escopo:** mexa SÓ nos arquivos da sua linha na seção 12 do `PLANO_DS.md`.
  - `ds_layout`, `ds_core`, `ds_col`, `ds_qa`, `build_ds`, `studio_ds` e `export_ds` são da integração: faça só acréscimos pontuais e documente.
  - Em `ds_scene`, só câmeras novas.
  - Em `ds_lib`, só materiais novos, com uma linha cada.
  - Releia antes de editar e reaplique se a edição falhar.
- **Não mude** planta, cotas, rotas nem marcadores sem combinar no relatório.
- **Não modele minérios.** Não crie cristais que pareçam minério.
- **Não edite** nada em `ilha_shadowgarden\`, `fm_lib.py` nem `export_roblox.py`.
- **Orçamento** da sua zona em `studio_ds.BUDGET` e na seção do plano. Teto da ilha 600k tris / 650 MeshParts. Ganhe por reuso e instanciamento do kit; não gaste geometria de herói no fundo.
- **Proibido:** Roblox Studio MCP, Blender MCP ao vivo, computer-use e browser. Sem commit. Sem `taskkill`. Use Blender com `--factory-startup`.
- **Renders** em 960 × 540: outros agentes estão renderizando ao mesmo tempo. Se o driver cair, refaça.
- **Scratchpad:** `C:\Users\lucas\AppData\Local\Temp\claude\C--Users-lucas-OneDrive-Desktop-To-up\47322845-c826-4095-8966-df3813237567\scratchpad\ds_<sua sigla>\`.

## Entrega
- **Voltas:** mínimo de 3 de render → crítica honesta ("isso sobreviveria a close-up?") → correção, nos 2 modos.
- **Folhas:** em `renders/<onda>/<sigla>/`, com as câmeras gerais e PlayerHeight da sua zona, mais closes dos assets principais e as câmeras de referência quando a sua zona aparecer nelas.
- **QA:** `build_ds` completo e `ds_qa` OK (rotas, `CLAREIRA_LIVRE`, sondas, técnico), mais o BUDGET da zona.
- **Relatório curto:** o que foi feito, orçamento, QA, folhas e pendências.
