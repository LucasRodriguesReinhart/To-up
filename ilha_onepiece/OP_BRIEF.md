# Ilha 5 One Piece / Wano: brief comum das ondas de produção

A fonte de verdade é `PROMPT_USUARIO.md` (o prompt mestre do usuário): leia-o inteiro. O plano aprovado é `plano/PLANO_OP.md`. As referências estão em `ref/`:
- **`ref_01_concept_aprovada.jpg`:** define a composição.
- **`ref_02_anime_castelo_arvore.jpg`:** mostra a relação entre o castelo e a árvore arqueada.

O blockout M1 está pronto: `op_*.py`, `ilha_onepiece.blend` e as folhas em `renders/m1/`. O template de processo é a Ilha 4 (`../ilha_demonslayer/`, **só leitura**): pipeline, `DS_BRIEF.md` e `renders/onda6/AUDITORIA_DS.md`, que reúne as lições de acabamento.

## O que o lead viu no blockout (`renders/m1/FOLHA_ref_M1.jpg`)
- **Árvore:** é o ponto mais fraco. Hoje é um arame fino e uniforme passando por cima do castelo.
  - Ela precisa ser **monumental**: base larga com raízes que agarram a rocha do castelo, tronco grosso afinando aos poucos, e um arco que nasce atrás/ao lado e enquadra o castelo como na `ref_02`.
  - A copa deve ter massas principais e secundárias, com aberturas para o céu.
- **Castelo:** falta o rochedo alto sob ele. Na concept o castelo fica no topo de uma falésia própria, com cachoeira central e estandartes. Hoje está sobre um bloco cinza chapado.
- **Ilha:** a borda e os terraços leem como bolo de camadas cinza.
  - As falésias precisam de massas maiores e variadas, com verde no topo e escorrendo.
  - O prompt pede para evitar uma sequência interminável de colunas iguais.
  - Laterais e traseira também têm de ser resolvidas.
- **Praça:** é um grande vazio bege.
  - O centro continua livre, por causa da mineração.
  - A borda precisa de intenção: escadas, muretas baixas, lanternas e estandartes nas entradas (como na concept), além de piso com desenho, juntas e emblema rebaixado.
- **Capital:** está esparsa e com intervalos regulares. A densidade e a variedade entram no M4, com o kit validado no M2.

## Craftsmanship (seção 15 do prompt)
A ordem de trabalho é: SILHUETA → PROPORÇÃO → ESTRUTURA → ENCAIXE → ESPESSURA → BORDAS → MATERIAL → DETALHE → ILUMINAÇÃO.

Primitivas e módulos são válidos. O problema é quando a peça parece inacabada.

## Realidade do Roblox (aprendida nas ilhas 1 a 4)
- **Sem textura no jogo:** a forma tem de ler sozinha. Valide sempre com `FM_MAT_PREVIEW=roblox`.
- **Bloom do dia:** Wano é DIURNA, então paredes claras não podem estourar. Use reboco off-white (cerca de 225–235), não branco puro.
- **Neon:** Neon claro vira branco no bloom. Use emissive só onde se justifica.
- **Z-fight:** nenhuma face visível pode ficar coplanar, nem a menos de 0,12 de outra face paralela de material diferente. Janela acesa fica ≥ 0,12 atrás do vidro. Piso sobre piso: ≥ 0,3 de diferença, ou só um deles.
- **Escala:** o avatar tem cerca de 5 studs.
  - Portas: vão livre ≥ 4 (ideal 5–6).
  - Degraus: espelho de 0,6 a 0,8.
- **Hash de variação:** use um finalizador do tipo murmur, não `crc32` puro. O crc32 sai correlacionado entre chaves vizinhas (lição da Ilha 4).
- **Ruído do Blender:** chame `mathutils.noise.seed_set(...)` no build para ele ser determinístico.

## Regras
- **Escopo:** mexa só nos arquivos da sua linha na seção 14 do plano.
  - `op_layout`, `op_core`, `op_col`, `op_qa`, `build_op`, `studio_op` e `export_op` pertencem à integração: só acréscimos pontuais, documentados.
  - `op_scene`: só câmeras novas.
  - `op_lib`: só materiais novos, uma linha cada.
  - Releia antes de editar.
- **Não mude** planta, cotas, rotas nem marcadores sem combinar no relatório.
- **Não modele minérios** nem cristais que pareçam minério. Não invente sistemas.
- **Não edite** nada em `..\ilha_demonslayer\`, `..\ilha_shadowgarden\`, `fm_lib.py` nem `export_roblox.py`.
- **Orçamento:** siga o dono no plano (seção 9). O teto é 620k tris / 650 MeshParts / 1300 colisões / 36 luzes de dia.
- **Proibido:** Roblox Studio MCP, Blender MCP ao vivo, computer-use, browser, commit e `taskkill`.
  - Use Blender com `--factory-startup`.
  - Renders em 960 × 540; se o driver cair, refaça.
- **Builds de teste:** `OP_OUT=<scratchpad>/op_<sigla>/teste.blend` (ou a variável que o `build_op` usar). O build oficial só acontece no fim; se outro agente estiver no meio de um, espere.
- **Scratchpad:** `C:\Users\lucas\AppData\Local\Temp\claude\C--Users-lucas-OneDrive-Desktop-To-up\47322845-c826-4095-8966-df3813237567\scratchpad\op_<sigla>\`.

## Entrega
- **Voltas:** mínimo de 3 voltas de render → crítica honesta ("isso sobreviveria a close-up na altura do jogador?") → correção, nos 2 modos.
- **Folhas:** em `renders/<onda>/<sigla>/`. Inclua câmeras gerais, `PlayerHeight` da sua zona, closes e as 2 câmeras de referência quando a sua zona aparece nelas.
- **QA:** build completo + `./run.sh qa` OK + orçamento do dono.
- **Relatório curto:** o que fez, orçamento, QA, folhas e pendências.
