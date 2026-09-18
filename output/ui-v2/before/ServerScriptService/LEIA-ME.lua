--[[
================================================================
  ANIME MINING SIMULATOR - ESTADO DO PROJETO
  Documento de handoff. ModuleScript, nao roda sozinho.
  Atualizado: setembro/2026
================================================================

## ARQUITETURA

ReplicatedStorage
  Config          Fonte unica de verdade: temas, minerios, picaretas,
                  mochilas, hats, pets, gachas, areas, icones.
  Remotes         3 eventos + 12 funcoes
  Sons            9 efeitos (Pro Sound Effects, gratuitos)

ServerScriptService.Core
  PlayerData      Perfil, DataStore, stats calculados
  AreaBuilder     Gera as 6 areas clonando modelos de ServerStorage.Modelos
  Mineracao       Dano, drop, respawn, desbloqueio de area
  IgnisService    Vender, picareta, mochila, hats
  GachaService    Rola ovo -> pet
  PetService      Equipar, fundir, equipar melhores
  PicaretaTool    Da a Tool ao jogador e troca quando ele compra outra
  Main            Liga tudo, remotes, teleportes, pads

StarterPlayerScripts
  ClienteMina     HUD, paineis, hotbar, inventario, gacha
  AutoMinerar     Clique escolhe rocha, boneco anda e bate
  MineracaoVisual Sons e animacao de golpe
  AmbienteLobby   (feito fora desta sessao)

ServerStorage.Modelos   24 minerios + gacha + ovos + templates

================================================================
## DECISOES QUE PARECEM ESTRANHAS MAS SAO INTENCIONAIS

1. GACHA DA PET, NAO HAT.
   Rocha -> hat (dano). Ovo -> pet (velocidade).
   O primeiro pet equipa sozinho, senao o jogador nao sente que ganhou.

2. NOMES DE AREA SAO LUGARES, NAO FRANQUIAS.
   "Vila da Folha", nao "Naruto". Nome de franquia atrai DMCA no Roblox.
   Os minerios usam chakra/ki/nichirin/sombra/mare/serio pelo mesmo motivo.

3. ANIMACAO DE GOLPE E VIA "toolanim", NAO Motor6D NEM ASSET.
   O rig R15 novo usa AnimationConstraint, entao mexer em Motor6D.C0
   nao faz NADA e nao da erro. E animacao de terceiro na toolbox nao
   toca em jogo que nao e do dono do asset.
   O caminho que funciona: StringValue "toolanim" = "Slash" dentro da Tool.
   O script Animate padrao do Roblox le isso.

4. MINERACAO SO NA ROCHA SELECIONADA.
   Nao encadeia sozinho pra proxima. Foi pedido explicito.

5. O GOLPE VEM DO CLIENTE (RemoteEvent Golpear).
   ClickDetector nao dispara direito com Tool equipada.
   Toda validacao continua no servidor: tipo, nome, atributo,
   distancia da superficie, area desbloqueada, cooldown.

================================================================
## BUGS JA RESOLVIDOS (nao reintroduzir)

- Mochila cheia travava a rocha em HP 0 pra sempre: o quebrar()
  saia por um return antes de agendar o respawn.
  Corrigido recusando o golpe ANTES de causar dano.

- Braco do Ignis desalinhava: a posicao do ombro estava salva em
  atributo fixo, que virava mentira toda vez que ele era movido ou
  escalado. Agora o script le shoulder_l em runtime.

- string.find(nome, "orb") casava com "corbel" e pintou 47 misulas
  de pedra como cristal ciano. Pintura agora e por nome exato.

- Fallback do DataStore era codigo morto: GetDataStore NAO falha
  com a API desligada, quem falha e o GetAsync. Agora tem sondagem.

- Estrada com pecas de 13 studs a cada 12 se sobrepunham 1 stud e
  faziam o personagem tremer. Virou peca unica.

- Chao, praca e estrada coplanares em Y=0 causavam z-fighting.
  Praca e caminhos subiram 0.2 stud.

- Baseplate com topo em Y=-4 abria buraco onde faltava tile.

- Icones nao apareciam: os IDs do Asset Manager eram DECAL (tipo 13).
  ImageLabel.Image precisa do ID da IMAGE (tipo 1) por baixo.
  Resolver com InsertService:LoadAsset e ler .Texture.

- Escalar o lobby depois de posicionar coisas com coordenada fixa
  quebrou santuario e estrada. Sempre reposicionar depois de escalar.

================================================================
## PENDENTE

ALTO
  - Balanceamento nunca testado de verdade. Os numeros de vida,
    valor e custo das 6 areas foram estimados no olho.
    Falta medir quanto tempo leva pra faturar cada tier.
  - Pets nao aparecem seguindo o jogador. So existem como stat.
    O campo "modelo" ja existe em cada pet na Config.
  - Lighting.Technology esta em Voxel. Trocar pra Future no painel
    de propriedades. Script NAO pode escrever nessa propriedade.
    E a maior causa do jogo parecer feio.

MEDIO
  - Setas apontando pro Ignis quando a mochila enche.
  - Aba de index da colecao (o painel SUA COLECAO foi removido).
  - Sistema de quest (o painel SUA JORNADA foi removido).
  - Config.Icones.areas ainda esta em 0.

BAIXO
  - Painel de inventario tem fundo preto opaco, destoa do resto
    do HUD que e azul translucido.

================================================================
## ARMADILHAS DO AMBIENTE

- execute_luau roda num VM separado do jogo. require() la dentro
  cria uma instancia NOVA do modulo, com cache vazio. Pra testar
  estado do servidor, criar um Script em Edit e dar play.

- Modelo importado de GLB vem SEM COR. Sempre pintar por nome de
  peca depois de clonar.

- Antes de apagar modelo do usuario, clonar pro ServerStorage.
  Ja perdi as muralhas do lobby antigo por nao fazer isso.
--]]

return {}

