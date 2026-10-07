# Anime Mining Simulator — revisão visual V5

Pedido: aproximar a aparência de Anime Expeditions, mantendo a organização atual.

## Implementação

- Tipografia Gotham Heavy/Bold, botões escuros com bordas finas, seleção ciano, fechamento circular vermelho.
- Cabeçalhos com emblema de mineração e espirais vetoriais próprias; cards com preenchimento por raridade.
- Base escura no inventário, atributos e utilidades no acabamento da referência.
- Pop-ups, diário, loja, equipamentos, viagens, missões e configurações usam os mesmos componentes.
- Textos curtos e atributos ajustados para celular horizontal, sem reorganizar os blocos.
- Assets novos: espirais 105263140080714, emblema 88607305530210. Ambos carregaram com IsLoaded=true no jogo e receberam permissão para a experiência 10765150093.

Referência visual consultada: https://allthings.how/anime-expeditions-summer-siege-how-to-get-the-new-units-and-fishing-rods/
As artes e modelos pertencentes ao nosso jogo foram preservados.

## Validação

Comparação do inventário antes/depois no mesmo canvas de 1306 × 611: mesmos valores de AbsolutePosition e AbsoluteSize nos sete blocos abaixo.

| Bloco | Posição | Tamanho |
|---|---|---|
| Janela | 0, 0 | 1306, 611 |
| Corpo | 20, 94 | 1266, 501 |
| Grade | 20, 150 | 354, 445 |
| Personagem | 388, 94 | 619, 501 |
| Atributos | 1021, 94 | 265, 501 |
| Título | 20, 10 | 280, 50 |
| Abas | 493, 12 | 320, 48 |

- Compilação Luau dos quatro scripts alterados aprovada.
- Inspeção visual em Play: HUD, inventários de unidades/hats, alimentação, missões, diário, coleção, viagens, loja, configurações, invocação, picaretas, mochilas e forja.
- Modelos 3D confirmados na tela de invocação e no inventário; equipamentos renderizados no viewport.
- iPhone 17 Pro horizontal: HUD, inventário, invocação e diário. Game ScreenOrientation=LandscapeSensor. Cortes de rótulos e números corrigidos; nova checagem de TextFits nas áreas ajustadas.
- Alimentação: seleção até Mítico escolheu uma cópia elegível; prévia de XP e revisão funcionaram. Confirmação de consumo não executada.
- Console de Play sem novos erros de UI nos testes.
- Controle temporário UIV5_QARequest removido antes do salvamento. Simulador devolvido ao viewport padrão e FitToWindow. Play encerrado.
- Backup: ServerStorage.BeforeUIV5_AnimeExpeditions_20260917_1789674149; fontes anteriores em before/.

## Prévia

O MP4 é uma sequência de 13 capturas estáticas reais do Studio, começando pelo inventário anterior. Não é uma gravação das animações. A adaptação conserva o layout atual e as artes do Anime Mining Simulator; não representa cópia pixel a pixel de todas as telas de Anime Expeditions. Ícones oficiais dos passes continuam aguardando os arquivos prometidos pelo usuário.
