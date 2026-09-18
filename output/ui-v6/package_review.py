from pathlib import Path
import base64, html, zipfile
root=Path(__file__).parent
out=root/'review'; out.mkdir(exist_ok=True)
shots=[('13-inventory-clean','Inventário — PC, versão final sem ferramentas de teste'),('01-store-final','Loja — ícones oficiais e preços do Roblox'),('04-settings-desktop','Configurações — escala no PC'),('07-forge-verified','Forja portátil — acesso bloqueado sem o passe'),('08-hud-phone','HUD — Samsung Galaxy A06 na horizontal'),('09-inventory-phone','Inventário — celular horizontal'),('10-settings-phone','Configurações — escala no celular'),('11-summon-phone','Invocação — celular horizontal'),('12-daily-phone','Diário — celular horizontal')]
for key,label in shots:
    (out/(key+'.jpg')).write_bytes(base64.b64decode((root/'preview'/(key+'.b64')).read_text()))
    old=out/(key+'.png')
    if old.exists(): old.unlink()
reference='https://allthings.how/anime-expeditions-summer-siege-how-to-get-the-new-units-and-fishing-rods/'
refimage='https://static.allthings.how/wp-content/uploads/2026/09/anime-expeditions-summer-siege-how-to-get-the-new-units-and-1320448788.webp'
cards=''.join(f'<figure><a href="{key}.jpg"><img loading="lazy" src="{key}.jpg" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>' for key,label in shots)
page=f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Anime Mining Simulator — revisão V6</title><style>body{{margin:0;background:#10131b;color:#eee;font:16px/1.6 system-ui}}main{{max-width:1400px;margin:auto;padding:28px}}h1{{font-size:30px}}p{{max-width:1000px}}a{{color:#71d9ef}}figure{{margin:0;background:#080b10;border:1px solid #38404d;padding:10px;border-radius:8px}}img{{display:block;width:100%;height:auto}}figcaption{{padding:10px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}table{{border-collapse:collapse;width:100%;margin:24px 0}}td,th{{text-align:left;border-bottom:1px solid #38404d;padding:12px}}@media(max-width:800px){{.grid{{grid-template-columns:1fr}}main{{padding:14px}}}}</style><main><h1>Anime Mining Simulator · UI V6</h1><p>Capturas reais do Roblox Studio. A organização atual foi preservada. A comparação usa a linguagem visual de Anime Expeditions: painéis escuros, detalhes de vento, cores por raridade, contornos finos, cabeçalhos coloridos e botões em relevo.</p><h2>Comparação visual</h2><div class="grid"><figure><img src="{refimage}" alt="Referência pública de Anime Expeditions"><figcaption><a href="{reference}">Anime Expeditions — referência publicada por All Things How</a>. Esta imagem exige internet.</figcaption></figure><figure><img src="13-inventory-clean.jpg" alt="Inventário do Anime Mining Simulator"><figcaption>Anime Mining Simulator — inventário atual, escala de 85%.</figcaption></figure></div><table><thead><tr><th>Aspecto</th><th>Adaptação e limite da comparação</th></tr></thead><tbody><tr><td>Composição</td><td>Janela central com margem para o mundo; três áreas do inventário mantidas conforme solicitado. A referência mostra outra categoria de inventário, portanto não é uma comparação idêntica de conteúdo.</td></tr><tr><td>Tipografia</td><td>Texto branco com contorno, títulos menores e correção da restrição que impedia as letras de acompanhar a escala.</td></tr><tr><td>Materiais da UI</td><td>Fundo escuro, arabescos discretos, linhas de raridade e botões com borda e relevo curto.</td></tr><tr><td>Personagens</td><td>Modelos reais do jogo, pose por articulações e respiração discreta. Os pés e a raiz ficam estáveis. A qualidade das malhas e texturas continua limitada aos modelos existentes.</td></tr><tr><td>Celular</td><td>Layout horizontal; ajuste independente de escala. Em 115% algumas áreas exigem mais rolagem, sem trocar a organização.</td></tr></tbody></table><h2>Capturas verificadas</h2><div class="grid">{cards}</div><p><a href="VALIDACAO.md">Alterações, testes e limites</a>. Abra as imagens para inspecionar em tamanho original.</p></main></html>'''
(out/'comparativo.html').write_text(page,encoding='utf-8')
qa='''# UI V6 — Anime Mining Simulator

## Implementação
- Escala de 65% a 115%, em passos de 5%, com preferências independentes para PC e celular. Padrões: 85% e 80%. Salva no perfil existente.
- Ajuste da tipografia que ignorava a redução da interface; refinamento de cabeçalhos, bordas, barras, botões, fundo e raridades, mantendo a organização.
- Personagens com pose articulada e movimentos pequenos; sem balanço do modelo inteiro. Respeita a opção de reduzir movimentos.
- Forja portátil exige o passe 1983332510, com validação no servidor. Venda gratuita permanece disponível junto do NPC Ignis. O passe portátil não concede venda automática.
- Nove passes reais configurados; imagens oficiais via rbxthumb e preços consultados no Roblox. Pet equip +3, hat equip +3, inventário +50/+300/+1000 cumulativos.
- Aviso de chegada compacto, com duração de cinco segundos, escondido ao abrir menus.

## Verificação
- 20 arquivos compilam e correspondem às fontes locais.
- 18 verificações de lógica passaram: validação da escala, limite e campos permitidos, acesso à forja, tentativa de burlar o contexto do NPC, bônus de slots/inventário e sorte.
- Ícones: nove de nove carregados no cliente. Preços: nove consultas respondidas pelo Roblox.
- PC: HUD, inventário, loja, configurações, forja bloqueada, diário, missões e invocação.
- Celular horizontal: iPhone 17 Pro e Samsung Galaxy A06; escala de 65%, 80% e 115% revisada no iPhone. Capturas Samsung em 80%.
- Caminho real até Ignis testado: viagem gratuita, aproximação e abertura por interação; botão de venda disponível no NPC.
- Raiz e pés do preview permaneceram fixos em uma amostragem de 2,1 segundos; cabeça e mãos tiveram movimento articulado.
- Sessão final sem ferramentas de teste: inventário aberto pela tecla H, escala PC 85% restaurada e console sem erros.
- Script e gancho temporários de teste removidos. Backup: ServerStorage.BeforeUIV6_1789676670.

## Limites e decisões
- Não foram feitas compras reais, vendas de minérios nem consumo de unidades durante os testes.
- Lucky mantém ×1,25. Lucky+ usa provisoriamente ×1,50, pois os passes não tinham descrição; juntos resultam em ×1,875. A pergunta sobre o balanceamento ainda aguardava resposta ao preparar esta entrega.
- A comparação visual não afirma equivalência de qualidade ou cópia exata: mantém os modelos, conteúdo e organização do Anime Mining Simulator.
- As capturas da forja bloqueada usam a simulação local de não possuir o passe; o bloqueio também foi testado independentemente no servidor.
- A imagem externa de referência é exibida pelo endereço original no HTML e exige internet. Não foi incorporada como asset do jogo.

## Referências
- Anime Expeditions: https://allthings.how/anime-expeditions-summer-siege-how-to-get-the-new-units-and-fishing-rods/
- Roblox MarketplaceService: https://create.roblox.com/docs/reference/engine/classes/MarketplaceService
- Roblox assets e miniaturas: https://create.roblox.com/docs/projects/assets
'''
(out/'VALIDACAO.md').write_text(qa,encoding='utf-8')
with zipfile.ZipFile(root/'Anime-Mining-UI-V6.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in out.iterdir(): z.write(p,p.name)
    for p in (root/'src').rglob('*.lua'): z.write(p,'fontes/'+p.relative_to(root/'src').as_posix())
print(root/'Anime-Mining-UI-V6.zip')
