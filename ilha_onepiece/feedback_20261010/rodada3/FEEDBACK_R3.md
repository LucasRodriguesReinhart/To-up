# Ilha 5 Wano: rodada 3 do feedback (10/10, depois de jogar a V2 no Play)

O usuário reprovou a V2 jogando (export 20f29090). Disse que "ficou a pior de todas" e que os mesmos problemas existem nas outras ilhas.

As capturas estão nesta pasta, de `01` a `20`.

## Texto do usuário (literal)
> ta com perguiça dresgraça?, olha que meda ta tudo mal montado, casas horriveis, grudads uma na outras, modelos de arovres parecendo pedras, hitboxes mal feitas para camarmba, tudo cagado velho, mdoelos flutuandi, pare de colocar bandeiras com detalhes do anime que podem nos dar copyright, caminhaos mal montados tortos, ano a refinamento nehum nisso, procure um jeito emlohor de fazer hitbox para os modelos por que vc colocas essa barreitras invisieis e fica uma bosta, em todas a asmilah tem esse mesmos problemas, mas essa ficou o pior de todos,cahoeriras estao ruim procure na internet como fazer cahcoieras melhores

## Itens, com evidência e causa
| # | Item | Capturas | Causa provável no pipeline |
|---|---|---|---|
| R1 | **Hitbox / barreiras invisíveis.** Ocorre o seguinte: <br>• jogadores em pé no ar acima de guarda-corpos e muros; <br>• jogadores andando sobre o telhado e a muralha do castelo; <br>• jogadores atravessando paredes de casas; <br>• a câmera bate em paredes invisíveis. | 06, 10, 11, 12, 19 | A colisão é feita de caixas invisíveis (`op_col`, `COL_*`) **separadas** do visual: <br>• as caixas são erguidas acima do visual (`raise_guards`: 140 guardas erguidas); <br>• as caixas `CamOccluder` fazem a câmera bater no invisível; <br>• o visual tem `CanCollide=false`. |
| R2 | **Casas grudadas umas nas outras.** | 02, 05, 08 | A capital V2 usa "parede-meia": os lotes ficam encostados, então os telhados encostam e se sobrepõem. |
| R3 | **Árvores parecem pedras.** | 07, 13, 14, 15, 17 | As copas são esferas facetadas com sombreamento chapado e, no Roblox, leem como rocha. A franja de agulhas também lê como pedra. |
| R4 | **Modelos flutuando.** | 02 (telheiro sobre a escada), 07 (tufo rosa), 15 (moita) | Não há teste de apoio para props e vegetação contra o chão real. |
| R5 | **Bandeiras e elementos com marca do anime (copyright).** | 03, 16, 19 | • Jolly Roger do chapéu de palha nas velas e mastros (Summon e navio); <br>• carranca de leão do Sunny; <br>• o portão OPM também deve ser conferido. |
| R6 | **Caminhos tortos e mal montados.** | 09, 17 (lajes desencontradas, buracos, sobreposição) | Os caminhos são feitos de retângulos de lajes por trecho; as juntas entre trechos se sobrepõem ou deixam buracos. |
| R7 | **Sem refinamento.** Muralhas do porto lisas com manchas de "tijolo", faixas azuis finas nas paredes e borda chapada da praça. | 01, 02, 03 | • muralhas com padrão de lajes aleatório e chapado; <br>• as bicas d'água viram riscos azuis. |
| R8 | **Cachoeiras ruins.** O pedido é pesquisar como fazer melhor. | 20 | A cachoeira é uma malha chapada com textura e pedras soltas. Falta o sistema em camadas: queda, white water, splash, espuma e névoa. |

## Pesquisa (cachoeira e colisão)
**Cachoeira.** O tutorial oficial "Create waterfalls with VFX" (create.roblox.com) monta a cachoeira em 5 camadas:

- **Cascata:** 2 Beams com textura rolando.
  - `FastDrop`: textura 16808804567; Width 5→10; CurveSize 10/20; TextureSpeed 1,3; TextureLength 2; ZOffset 2; FaceCamera.
  - `SlowDrop`: mesma textura; Width1 20; TextureLength 1,5; TextureSpeed 1.
  - `Outflow`: textura 4787437624; Width 60→20; TextureSpeed 0,4; TextureLength 64; Wrap.
- **Splash:** ParticleEmitter, textura 16829556885; Rate 30; Lifetime 0,25–0,35; Speed 20–35; SpreadAngle 50; Acceleration −40.
- **White water:** textura 16808075391; Rate 12; Lifetime 1,25–1,5; Speed 15–18; Drag 0,25.
- **Espuma:** textura 16811365086; orientação VelocityPerpendicular; Size 5→20; Rate 5.
- **Névoa:** textura 16830667309; Rate 20; Speed 35–50; Drag 1,5. Mais uma névoa que sobe (Rate 3; Lifetime 4).

**Colisão.** A doc do Roblox lista 4 níveis de `CollisionFidelity`:

| Fidelity | Uso |
|---|---|
| `Box` | Props pequenos |
| `Hull` | Formas convexas |
| `Default` | Formas côncavas moderadas |
| `PreciseConvexDecomposition` | Precisa, para vãos e portas; é a mais cara |

O problema atual vem de a colisão **não ser** o visual. A V3 inverte isso: **o que se vê é o que colide**. Malhas sólidas e de piso colidem pela própria forma. Folhagem, bandeira, lanterna pequena e efeitos não colidem. Caixas invisíveis só onde não há forma visível que segure o jogador, e nunca acima do visual. A câmera passa a bater só em geometria visível.
