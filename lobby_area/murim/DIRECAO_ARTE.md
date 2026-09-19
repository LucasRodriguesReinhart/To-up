# Lobby "Seita da Forja Celeste" — pesquisa, direcao de arte e planta

Lobby original para o Anime Mining Simulator: China imperial + Murim, em cartoon estilizado premium para Roblox.
Nada aqui deriva de Anime Expeditions. Eixo do mundo: saida para as areas no +Z (corredor x ±46, piso y=0 a partir
de z=178), forja no -Z. Spawn (0, 0.6, -62). Elementos funcionais que continuam onde estao: Santuario (6 portais em
x≈124, z -32..32, y≈6.4), Loja de Mochilas (pad em (-116, 8.2, 0)), MailBox (-116, 10, -18), NPC Ignis (pes em y=10,
posicao original (0, 17, -116), modelo de 12 x 14.5 x 11.6 studs).

## 1. Pesquisa (resumo do que importa para construir)

Arquitetura imperial chinesa (Cidade Proibida, Salao da Suprema Harmonia; fontes: Wikipedia, Britannica,
travelchinaguide, archinatour, SCMP):
- Hierarquia por plataforma: os saloes importantes ficam sobre terracos de marmore em 3 niveis ("sumeru"), com
  balaustradas brancas e escadarias triplas; o Salao da Suprema Harmonia tem 63 m de largura x 37 m de fundo x 35 m de
  altura sobre um terraco de 8 m — proporcao largura:altura ≈ 1,8:1, terraco ≈ 23% da altura do salao. Uso: a Forja
  fica num terraco alto (10 studs) e e o unico volume com telhado duplo dourado.
- Telhados: hierarquia por tipo (wudian = 4 aguas imperial, xieshan = 4 aguas com empena "descansando", telhado duplo
  = maior status). Beirais curvos e levantados nos cantos, cumeeira com terminais (chiwen) e figuras na aresta. Telha
  vidrada amarela = imperial; verde/cinza = templos, principes, seitas. Uso: Forja = telha dourada; todo o resto =
  telha verde-jade escura; cantos das aguas exagerados no cartoon.
- Dougong: consolas encaixadas em blocos (dou) e bracos (gong) sob o beiral; quanto mais elaborado, maior o status.
  Uso: dougong simplificado em 2-3 degraus de blocos arredondados, pintados em faixas (verde/azul/ouro) — so nos
  edificios principais.
- Colunas vermelhas (vermelhao) sobre bases de pedra, vigas pintadas, paredes vermelhas com barra de pedra; portao
  imperial = base macica de muralha com 3 passagens em arco e pavilhao de 2 beirais em cima (Portao do Meridiano);
  paifang = portico de postes e lintéis com varios telhadinhos (portico de honra).
- Jardim: ponte-lua (arco alto que forma um circulo com o reflexo), espelho d'agua parado para refletir o pavilhao,
  rochas de forma forte, pinheiros em camadas, bordos vermelhos, bambu; caminhos de pedra irregulares.

Forja tradicional (islandblacksmith, Wikipedia Bladesmith/Forge, hanbonforge):
- Componentes: fole de caixa (fuigo) separado da lareira por um murete, lareira baixa com duas paredes paralelas,
  tuyere (bico de ar), reservatorio de carvao, bigorna baixa (o mestre trabalha sentado/agachado, ajudantes de pe com
  marretas), calha de tempera com agua, prateleira de laminas em fase (sanmei: nucleo duro entre placas moles).
  Uso: a forja do Ignis mostra lareira monumental com boca em arco, chamine-torre, fole gigante, bigorna, calha de
  tempera e um "altar de laminas" — tudo em escala do Ignis (3x o jogador).

Murim / seitas de espada (Mount Hua Sect, Huashan; wikis de wuxia):
- Complexo em montanha sagrada, isolado por penhascos; hierarquia de patios; patio de treino com postes de madeira
  (postes de flor de ameixeira), bonecos de palha, estantes de armas; estandartes com o simbolo da seita; salao da
  espada com pedestais de espadas dos ancestrais; nomes com "Pavilhao", "Salao", "Portao". Simbolo escolhido para a
  seita (original): espada vertical sobre uma chama dentro de um circulo de bronze.

Estilizado em jogos (Liyue/Genshin, referencias de Roblox cartoon):
- Paleta quente e organizada (vermelho, ouro, madeira, pedra clara) com verde da vegetacao; formas dos telhados
  exageradas; detalhes concentrados em beirais e cumeeiras; superficies grandes lisas com variacao suave; leitura a
  distancia por silhueta e cor, nao por microdetalhe.

## 2. Direcao de arte (regras que valem para tudo)

Estilo: cartoon premium. Volumes chanfrados, cantos arredondados, proporcoes robustas (colunas grossas, beirais
fundos, degraus altos), curvas de beiral exageradas, detalhe seletivo (beirais, cumeeiras, portas, pedestais).
Sem textura fotografica: albedo pintado em cores chapadas com variacao suave + AO/gradiente pintado + realce de
aresta claro; normal map so para telhas e pedra grande. Sem microdetalhe, sem ornamento que nao leia a 40 studs.

Linguagem de formas:
- Coluna: diametro 2.2-2.6, leve entasis, base de pedra em "tambor", anel de ouro no topo.
- Telhado: 2 beirais no edificio principal, 1 nos secundarios; balanco 5-6 studs; canto levantado; telhas em
  fiadas largas (1.2 stud) com beiral de "gotas" arredondadas; cumeeira grossa em ouro com terminais em chifre
  (chiwen simplificado) e 3 figuras-bloco na aresta.
- Dougong: 2-3 degraus de blocos arredondados sob o beiral, so onde importa.
- Pedra: blocos grandes com juntas suaves e cantos gastos; balaustrada com postes de topo em "nuvem".
- Rochas: facetadas e lisas, silhuetas em cunha; pinheiros em 3-4 camadas de "nuvem"; bordos em massas redondas.
- Metal: bronze com desgaste pintado; ferro escuro; ouro fosco (Reflectance <= .1), nada espelhado.

Paleta (hex) — funcao:
- Vermelho imperial #B8321E (colunas, paredes) / sombra #7E2014
- Ouro #E0A83A (cumeeiras, aneis, emblemas) / bronze #8C6A2E (braseiros, sinos, ferragens)
- Madeira escura #4A2E1E (vigas, portas) / madeira media #7A4B2A
- Pedra clara quente #DCCDB0 (terracos, balaustradas) / pedra do piso #B9AD95 / juntas #8F846E
- Telha jade escuro #2E5A4C (telhados gerais) / telha imperial #D4A034 (so a Forja)
- Forja: ferro #2B2624, brasa #FF7A1A, chama #FFC84A
- Vegetacao: pinheiro #3E6B3A, folha clara #6E9A45, bordo vermelho #C4432B, bambu #7FA85A
- Agua: turquesa clara #3FA0A0 com fundo #2A6C6A (turquesa so na agua = detalhe secundario)

Iluminacao: fim de tarde quente (ClockTime ~15.5), sol amarelo suave, ambiente levemente azulado para separar
sombras, Bloom baixo; luzes pontuais laranja na Forja (lareira, chamine, braseiros) e lanternas ambar.

Materiais Roblox: SmoothPlastic + SurfaceAppearance (ColorMap pintado; NormalMap so telha/pedra), Glass na agua,
Neon so em brasas e chamas pequenas, Metal fosco no ouro.

## 3. Conceito

"Seita da Forja Celeste": o patio interno de uma antiga seita de espadachins onde a forja e um lugar sagrado.
Tres marcos que se veem de qualquer ponto: (1) o Salao da Forja com telhado dourado e a Torre do Fogo (chamine) no
fundo (-Z), (2) a Espada Ancestral fincada no Altar no centro do patio, (3) o Grande Portao com torre de 2 beirais na
saida (+Z). Progressao lida no espaco: o jogador nasce aos pes da escadaria da Forja (mestre Ignis acima e ATRAS dele
hoje — ver 4b), atravessa o patio pela Espada e sai pelo Portao para as areas; o caminho de volta e o mesmo eixo,
terminando subindo ate a Forja.

## 4. Planta (coordenadas Roblox, y = altura do piso)

- Patio Central x -70..70, z -60..60, y 0. Centro: Altar da Espada — estrado octogonal r=14 (y 0→2.5), pedestal
  de pedra + espada de 30 studs; anel de espelho d'agua r 14..22 (agua y -1) cruzado por 4 pontes de pedra (largura 8)
  nos eixos; 4 braseiros de bronze.
- Escadaria Monumental z -60..-92, largura 46: 12 degraus (0.83 x 2.5) em dois lances separados por rampa esculpida
  central (danbi) de 10 de largura; patamar intermediario; pedestais de espada e leoes de pedra no pe.
- Terraco da Forja y 10, x -62..62, z -92..-150, balaustrada branca; Salao da Forja x -36..36, z -108..-146
  (72 x 38), porta aberta ao patio (colunata frontal z -108, alpendre de 10 de fundo), colunas de 14; telhado duplo
  dourado (beiral inferior y 24, cumeeira y 44); Ignis em (0, 10, -116) sob o alpendre, de frente para o patio;
  lareira monumental no fundo (z -140) com boca em arco de 12; Torre do Fogo (chamine de tijolo/bronze) atravessando o
  telhado ate y≈62 com brasa e fumaca; fole gigante, bigorna, calha de tempera, altar de laminas.
- Fundo -Z (z -150..-200): penhascos estilizados y ate 70 com pinheiros; cascata a leste alimentando o lago.
- Via Imperial z 60..140, x -16..16: avenida de lajes com postes-lanterna a cada 20, 2 pares de estandartes,
  leoes de pedra em z 135.
- Grande Portao z 140..160: base de muralha x -46..46, y 0→16, 3 passagens (central 22 x 15, laterais 12 x 11);
  pavilhao de 2 beirais em cima (cumeeira y≈42); muralha vermelha com telhadinho verde ate x ±150; torres de canto.
  Passa direto para o corredor Lobby_Area1 (piso y 0 em z 178).
- Lago de Jade (leste) x 70..100, z -70..130, agua y -1.5; Ponte-lua x 70→100 em z 0 (comprimento 30, largura 8,
  flecha 4). Santuario dos Portais: galeria aberta (lang) x 104..146, z -45..45, piso y 6.4 (mantem os 6 portais),
  escada de 8 de largura desde a margem; telhado verde de 1 beiral; muro + penhasco atras.
- Jardim Oeste x -70..-100: pinheiros, bordos, rochas, riacho raso; caminho de pedra de (-70,0) ate a Casa do
  Intendente (Loja) em x -104..-130, piso y 8 (pad da loja em (-116, 8.2, 0), MailBox em (-116,10,-18)); Patio de
  Treino ao sul (z 20..60): postes de madeira, bonecos de palha, estantes de armas, estandartes.
- Limites: muros vermelhos com capa de telha a leste e oeste, penhascos ao norte, muralha do Portao ao sul.

Distancias: spawn→Ignis 54 studs (escada incluida); spawn→Altar 62; Altar→Portao 150; Altar→Portais 110 (ponte);
Altar→Loja 116. Alturas (como construido no blockout): patio 0 / terraco 10 / galeria 6.4 / loja 8 / torre do portao 42 /
cumeeira da Forja 46 / Torre do Fogo 66 / espada 33 / penhascos 48-84.

## 4b. Medido no blockout (Play, 2026-09-19)

- Spawn real: o `IslandTravel` coloca o personagem em (0, 5, -66) olhando +Z (para o Altar e o Portao), NAO para a
  Forja. A orientacao do `SpawnLocation` e ignorada. Fazer o jogador nascer olhando a Forja exige mudar uma linha do
  `IslandTravel` (`put`) — decisao do usuario, nao aplicada.
- Os 6 portais do Santuario sao viagem rapida ATIVA: pisar no pad teleporta para a area (testado: pad em z -20 levou
  a (0, 9, 1595)). A galeria leste tem que ser lida como lugar de viagem, nao como decoracao.
- Caminhada por waypoints, 0 quedas: escadaria → Ignis (raiz a 13.3 do `belly`, prompt alcanca 18) → Altar (contornar
  o pedestal; o centro e solido) → Via Imperial → Portao → corredor z 186; ponte-lua → escada da galeria; caminho oeste
  → escada da loja → pad → MailBox → patio de treino; escada lateral leste do terraco + ponte do riacho.
- Corrigido: a faixa de base do portao atravessava as 3 passagens (degrau de 1.6); agora so nos pilares.
- NAO feito: capturas em arquivo do Studio (View > Screenshot precisa do controle da tela; o usuario pediu para usar
  depois). As vistas do blockout so foram conferidas pelo `screen_capture` do MCP, que nao grava arquivo.

## 5. Processo

1 pesquisa (este arquivo) → 2 direcao de arte → 3 planta → 4 blockout no Roblox (`blockout.lua`, Parts) → 5 teste de
circulacao (caminhada por waypoints, quedas, linhas de visao) → aprovacao → 6 arquitetura e marcos no Blender
(`murim_*.py`, modelagem por edicao de malha) → 7 Forja e Ignis → 8 agua/vegetacao/caminhos → 9 materiais e luz →
10 import → 11 validacao → 12 polimento.
