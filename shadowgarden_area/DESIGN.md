# Jardim das Sombras — domínio da veia arcana

## Referências e análise, antes da modelagem

- Anime oficial: https://shadow-garden.jp/1st/ e https://shadow-garden.jp/1st/story/ . A arte oficial usa preto azulado, linhas douradas finas, pedra e mobiliário nobres, janelas altas e iluminação azul/violeta. O vocabulário deve aparecer nas proporções, não em dezenas de logotipos.
- Master of Garden: https://www.shadow-garden-mog.jp/ . Organização secreta, sete membros fundadores, contraste entre aparência nobre e poder oculto. Adaptação: cidadela e galerias organizam a exploração de uma veia subterrânea; sete lancetas na entrada principal, insígnias discretas, núcleo violeta.
- Alexandria, contexto secundário: https://the-eminence-in-shadow.fandom.com/wiki/Alexandria . Castelo claro, refúgio protegido por escarpas e floresta com névoa. A ilha é uma composição original inspirada nessa ideia, não reprodução canônica da cidade.
- Roblox, arte modular e colisões: https://create.roblox.com/docs/tutorials/curriculums/environmental-art/assemble-an-asset-library e https://create.roblox.com/docs/workspace/collisions . Malhas visuais separadas das colisões simples; nenhuma caixa de colisão atravessando portas, arcos ou caminhos.

Não usar resultados de pesquisa de Midgar de Final Fantasy, imagens de outros animes ou imagens geradas como referência canônica. A imagem antiga de água do usuário não está disponível neste contexto; aplicar a preferência confirmada por água cartoon, margens orgânicas e movimento suave, e revisar dentro do jogo.

## Direção artística

Castelo de calcário frio sobre basalto estratificado. Telhados azul-noite, pináculos altos, metais escuros, filetes de ouro velho. A energia violeta está nos depósitos geológicos, nos vitrais e na entrada da mina. Folhagem verde-azulada com pequenos acentos lilases. Piso minerável cinza lavanda médio: contraste suficiente com minérios escuros. Luz ambiente fria legível, lanternas quentes nas rotas, magia localizada. Água azul-petróleo/turquesa, brilho claro espaçado e costa de pedra.

## Layout e silhueta

Unidade Blender = stud; X lateral, Y rumo ao fundo, Z altura. Conversão Roblox (-X,Z,Y), base (0,106,1600).

- Ilha irregular aproximadamente 350 x 375 studs. Entrada estreita ao sul; flancos assimétricos; paredões e torres ao norte; baía a leste.
- Entrada (0,-169,0): ponte/limiar baixo, sem parede na linha central. Vista da pedreira, galeria sob o castelo, torres e arco natural.
- Pedreira central: aproximadamente 128 x 130, fundo Z=-6. Piso contínuo, somente minérios. Quatro rampas largas; percurso circular no bordo.
- Cidadela (8,110,16): salão central, torre-relógio, sete lancetas, duas alas de alturas diferentes, pináculos, muralhas/contrafortes. Extração sob a galeria frontal a Z=0; acesso superior por rampas laterais.
- Bairro nobre a oeste: três volumes diferentes, pequeno comércio, arquivo e jardim com caminho alternativo.
- Lago a leste (116,-46): margem curva, ponte e ruína; uma queda curta proveniente de uma bacia elevada, efeitos em lâminas curvas e espuma suave.
- Arco de basalto e fissura a nordeste: landmark natural; depósito exposto e caminho até o portal da próxima área.
- Cripta a noroeste; caverna arcana no extremo norte da mina. Iluminação indica entradas. Pisos dos bolsões especiais também livres.
- Portal próximo a (137,65), retorno na entrada. Preservar a ausência atual de gacha funcional de sombra; não modificar economia.

## Kit de produção

Arquitetura: 3 casas nobres, mansão, arquivo, galeria, capela em ruínas, corpo do salão, torre quadrada, torre octogonal, pináculo, arcada, janela lanceta, porta, pórtico, muro, parapeito, escada, ponte de pedra.

Mineração: pórtico de mina, escora, trilho junto à parede, carrinho estacionado, guincho na borda, altar geológico, cristais em veios, 5 silhuetas de minério compatíveis com as raridades existentes.

Natureza: 3 árvores com troncos curvos, raízes e ramos visíveis, copas assimétricas em tufos; cipreste irregular; arbusto, grama e flores discretas. Não usar esfera sobre cilindro.

Rochas: 3 rochas, falésia estratificada, agulha inclinada, arco natural, plataformas e moldura de caverna.

Props: lanterna, banco, caixa, barril, grades, bandeira, brasão discreto, estante/mesa do arquivo.

Collections SHADOWGARDEN_BUILDINGS / PROPS / ROCKS / NATURE / MINING / LANDMARKS / DECORATION / RUINS; auxiliares TERRAIN, GAMEPLAY, KIT e EXPORT.

## Ordem e critérios de aceitação

1. Referências e este documento. 2. Blockout e renders de entrada/topo. 3. Corrigir proporções e visadas. 4. Modelos finais no Blender. 5. Revisão visual. 6. Exportação FBX de malhas reais + manifesto de instâncias/pivôs. 7. Importação para o proprietário do jogo. 8. Integração isolada da Área 4, com backups dos scripts. 9. Play: colisões, rampas, portais, spawns, limites, console e água/árvores. 10. Remover QA temporário; entregar estado exato, sem publicação automática.

Orçamento inicial: até 500 MeshParts colocados, atlas de cores compartilhado, malhas individuais abaixo de 10k triângulos, VFX locais com distância limitada. Ajustar baseado na contagem real. Colisões apenas onde necessárias; nenhuma decoração sobre o piso central. Não confundir contagem de malhas com medição de FPS.
