# Shadow Garden: decisões tomadas na auditoria (2026-09-28)

Base: `_audit/AUDIT_A_mineracao.md`, `_audit/AUDIT_B_dados_ui.md`, `_audit/AUDIT_C_progressao_ambiente.md` e `_audit/PERF_BASELINE.md`.

## D1: ordem das ilhas (Dragon Ball → Shadow Garden → Demon Slayer)
A economia inteira é indexada pela posição do tema (`Config.ORDEM_TEMAS` e as tabelas do `EconomiaV31` por mundo): vida do minério comum, preço do portal, dano base dos hats, picarete do mundo e gacha. Hoje a ordem é `chakra, ki, nichirin, sombra, …`. O caminho pedido pela missão é Dragon Ball → Shadow Garden → Demon Slayer.

**Decisão:** trocar a posição dos temas `sombra` e `nichirin`.
- A Shadow Garden passa a ser o mundo/área **3**, com a curva que já existe para o 3º mundo (portal 52.000, vida do comum 6.600 e gacha).
- O Monte Natagumo passa a ser o mundo/área **4**.

Nenhum número novo é inventado: só a ordem muda, para bater com o caminho a pé.

**Efeitos conhecidos:**
- Quem já comprou a área 3 passa a ter a Shadow Garden, com o mesmo valor pago. O save recebe uma migração única (`perfil.migSG34`) que troca `areas`, `paredes` e missões 3↔4. Assim, quem tinha o Monte Natagumo continua com ele.
- Os hats do tema sombra passam a ter a base do mundo 3 e os do nichirin a do mundo 4, porque a base vem da posição.
- Os ramos procedurais por id (`IslandWorld`, `AreaAtmosphere`, áudio e imagens) passam a seguir o **tema**, não o id. O Monte Natagumo procedural continua saindo igual, agora como área 4.

## D1b: invocação da Shadow Garden
Hoje a área sombra não tem gacha nem personagens: `GACHA_MUNDO[4]=false` e não há `PETS_POR_AREA[4]`. A missão exige a invocação na ilha, reaproveitando a que já existe.

**Decisão:**
- O gacha segue o **tema**, com os preços que já existem:
  - Shadow Garden = posição 3, custo 55.000, o mesmo do 3º mundo simulado;
  - Monte Natagumo mantém o gacha dele, com o mesmo custo atual de 55.000, agora como mundo 4.
- **Pets da Shadow Garden:** montados como os pets atuais (rig R15 com acessórios UGC), usando **só itens que já estão no catálogo `HatCatalogo.sombra`** do jogo. São os personagens Cid, John Smith, Zeta, Beta, Delta, Alpha e Shadow, um por raridade de comum a secreto.
- Os bônus saem das fórmulas existentes (`PET_BONUS`, `PET_LB` e `PET_BONUS_MUNDO`). Nenhum número novo.
- **Limitação registrada:** o `GACHA_GIRO` do mundo 4 nunca foi simulado (o gerador `gerar.py` não está no repositório). O custo do Natagumo fica marcado como **provisório** até a economia ser recalibrada.

**Reversão:** um único ponto no `Config` (a ordem da lista e os ids das áreas 3/4) mais os mapeamentos por id listados no `INTEGRACAO_JOGO.md`.

## D2: mineração principal dentro do castelo
Reusa o `SpawnMinerio` por zona, sem sistema novo.
- Zona no piso do Mining Hall, com bloqueios nas colunas e grade hexagonal de pontos (100 ou mais).
- Nada colidível até piso+12 sobre a zona. Pé-direito de pelo menos 26, com teto opaco e colidível para segurar a câmera.
- A região da área (`BoundsCenter`) é obrigatória, porque o `Config.centro` fica longe da ilha. `SafeMaxY` também.

## D3: dungeon (trial de mineração)
Reusa `AreaBuilder.novoMinerio` com os minérios oficiais do tema `sombra`. A extensão mínima no `Mineracao` é:
- atributo `Temporario`, que pula energia, chefe e respawn;
- atributo `DonoRun`;
- evento `Quebrou`.

O agendamento fica no servidor, nas fronteiras XX:00 e XX:30 do `GetServerTimeNow`, com máquina de estados explícita. As salas ficam dentro da região da área 3, abaixo da ilha.

## D4: ingredientes e poções
- Estoque novo `perfil.itens = {[id] = qtd}`, com catálogo em módulo de configuração próprio (`CraftConfig`).
- Nada vai na mochila, porque a venda apaga a mochila inteira.
- As poções usam o `adicionarBoost` existente, com o catálogo de boosts centralizado.
- Todos os valores são provisórios e marcados como tal no `CraftConfig`.

## D5: portões de compra
- **Entrada:** o portão Shadow Garden da Ilha 2, que já existe, passa a vender a área 3 (`GATE_AREA`).
- **Saída:** o portão aprovado Demon Slayer (`ilha_naruto/il_gate_ds.py`) vende a área 4 (Monte Natagumo).
- Nos dois, sem teleporte depois de liberado, como já acontece nas Ilhas 1 e 2.

## D6: código antigo da área 4
- `ShadowGardenIsland` e `ShadowGardenLayout` (antigo "Domínio da Veia Arcana") saem do `require` no boot. O código fica no backup.
- `workspace.ShadowGarden_Review` sai do workspace e vai para a ServerStorage.
- O builder novo usa a fonte `ServerStorage.IlhaShadowGarden`. Nunca usar o nome `ShadowGardenKit`.
