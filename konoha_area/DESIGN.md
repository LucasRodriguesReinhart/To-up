# Área 1 — Vila da Folha (Konoha) · Documento de Level Design

## 1. Análise das referências

Fontes: mapa aéreo de Konohagakure, Hokage Rock, Hokage Residence e Ichiraku (Narutopedia/Fandom),
e o estado atual da ilha no Studio (place 101959830085647).

| Elemento | O que faz Konoha ser reconhecível | Como vira regra de design |
|---|---|---|
| Monumento Hokage | Paredão bege/ocre contínuo, rostos em fileira, vegetação no topo, escadaria em zigue-zague, prédios na base | Paredão fecha o norte da ilha inteiro; 4 rostos estilizados (não retratos exatos) a ~55–80 studs; escada zigue-zague até um mirante |
| Residência do Hokage | Cilindro largo, beirais em anel entre andares, telhado plano com emblema, logo abaixo dos rostos | Landmark secundário no eixo central, alinhado com o portão e com os rostos |
| Casas | Paredes creme/bege, cantos quadrados, telhados vermelho/laranja/verde em faixas, caixas d'água cilíndricas, varandas externas, escadas externas, placas verticais | Kit modular: corpos + telhados + caixa d'água + varanda + escada + placa (sem repetir o mesmo prédio) |
| Comércio | Ichiraku: madeira, noren azul-marinho com texto, lanterna vermelha, balcão aberto para a rua | Rua principal comercial ligando o portão à praça |
| Muralha/Portão | Muralha circular clara, portão gigante com portas de madeira abertas | O arco da muralha define a silhueta da ilha; portão enquadra a primeira visão |
| Paisagem | Vila dentro de floresta densa, rios cruzando, penhasco ao norte | Floresta fora da muralha, rio com cachoeira que cai do monumento e sai pela borda da ilha |
| Paleta | Creme, ocre, vermelho-telha, verde-folha, azul-céu, madeira média | Paleta de ~24 materiais, sem textura fotográfica |

O que evitar: a ilha atual lê como "simulator genérico" (praça plana, 4 casas iguais nas laterais,
minério no chão de terra, muro de blocos). Nada ali diz "Konoha" além de 3 rostos pequenos.

## 2. Layout (coordenadas locais; +Z = norte/avanço, entrada ao sul; chão da rua y=6)

```
                    N  (+Z)
   ┌──────────── MONTE HOKAGE (4 rostos) ─────────────┐   z 110..165, até y≈100
   │  mirante ◄escada   RESIDÊNCIA   GRANDE MINA ★ cachoeira
   │  CAVERNA           HOKAGE       + pátio/arena     │ rio
   │  SECRETA   ACADEMIA   (z≈80)     do chefe         │  ║
   │                                     PORTAL ►      │  ║
   │  PEDREIRA NINJA ◄── PRAÇA CENTRAL ──► ponte ── CAMPO DE TREINO
   │  (poço -6 y)         (fonte folha)     vermelha   (rochedos)
   │                  RUA COMERCIAL (ramen, dango...)  ║
   └──────────── muralha ─── PORTÃO ─── muralha ──────╨── cachoeira sai da ilha
                     PRAÇA DE CHEGADA (spawn, invocação, lobby)
                    S  (−Z)
```

Fluxo do jogador: chegada → portão (primeira visão/thumbnail) → rua comercial → praça central (hub)
→ escolhe: Pedreira (oeste, perto, minério comum) · Campo de Treino (leste, atravessa a ponte)
→ Grande Mina + arena do chefe (nordeste, landmark de progressão) → Portal para a próxima ilha.
Descoberta: Caverna Secreta (noroeste, escondida atrás de árvores e santuário) e o mirante na escada do monumento.

Guias sem setas: rua pavimentada clara (anda) × terra/pedra escura com afloramentos (minera);
lanternas vermelhas em fio puxam para a praça; cristais de chakra brilhando marcam cada zona de mineração;
a Grande Mina tem a maior massa de cristais e fica visível do portão.

> **Revisão 2 (feedback):** a mineração principal agora é a **Pedreira Central** (poço 134×106 studs, piso −8,
> 4 rampas, 4 terraços a −4, mesa central com guindaste) no coração da vila, com anel viário em volta.
> O **Santuário da Invocação** (selo no chão, pergaminho gigante, sapos guardiões, torii, cristais roxos) fica logo
> à esquerda depois do portão, com a máquina de gacha no centro do selo. A antiga pedreira oeste virou bairro residencial.

## 3. Zonas de mineração (integradas)
1. **Pedreira Ninja** — poço escalonado 6 studs abaixo da rua, rampa de acesso, paredes com veios de cristal, guindaste de madeira, andaimes, vagonetas.
2. **Campo de Treino** — clareira depois da ponte, rochedos com veios, postes de treino e alvos.
3. **Grande Mina do Monumento** — entrada monumental escavada no monte, escoras de madeira, trilhos, cristais gigantes; pátio com arena do chefe.
4. **Caverna Secreta** — gruta com cristais roxos/dourados raros.

`SpawnMinerio` passa a aceitar pontos só dentro dessas zonas (qualquer altura), então minério nunca nasce na rua ou entre casas.

## 4. Lista de assets (kit modular no Blender)
- **KONOHA_BUILDINGS**: Casa_P_Duas-Aguas, Casa_P_Laje-Caixa, Casa_M_Varanda-Escada, Casa_M_Telhado-Escalonado, Casa_G_Tres-Andares, Torre_Cilindrica, Loja_Ramen, Loja_Dango, Loja_Armas, Loja_Flores, Academia, Muralha_Modulo, Torre_Vigia, Quiosque_Invocacao
- **KONOHA_PROPS**: Caixote, Barril, Banca_Mercado, Banco, Poste_Luz, Poste_Fios, Placa_Rua, Cerca, Escada_Madeira, Ponte_Vermelha, Poste_Treino, Alvo_Treino
- **KONOHA_NATURE**: Arvore_Folha_G, Arvore_Folha_M, Arvore_Gigante, Arbusto, Tufo, Canteiro_Flores
- **KONOHA_ROCKS**: Rocha_S/M/L (facetadas), Penhasco_Modulo, Rochedo_Veio
- **KONOHA_MINING**: Cristal_Chakra (fogo, água, vento, raio, terra, chakra), Escora_Mina, Trilho, Vagoneta, Guindaste, Andaime, Pilha_Minerio, Placa_Mina
- **KONOHA_LANDMARKS**: Monte_Hokage + 4 rostos, Residencia_Hokage, Portao_Principal, Grande_Mina, Fonte_Folha, Arena_Chefe, Portal_Progressao
- **KONOHA_DECORATION**: Fio_Lanternas, Estandarte_Folha, Noren, Vasos, Emblemas

## 5. Pipeline Blender → Roblox
- Tudo é modelado com primitivas compatíveis com Part (Block, Wedge, CornerWedge, Cylinder, Ball): conversão 1:1, sem upload de mesh, editável no Studio, no mesmo estilo Plastic das outras ilhas.
- Malhas compartilhadas; os assets do kit são collections instanciadas (reuso real no .blend).
- Exportador gera `konoha_parts.txt` (formato compacto) + marcadores de gameplay (spawn, zonas, chefe, portal).
- No Studio, o modelo fica em `ServerStorage.KonohaArea` e `IslandWorld` clona-o para a Área 1 em runtime.
- Orçamento: ≤ 8.000 parts na ilha (a atual tem 5.417), luzes e partículas só nos pontos focais.
