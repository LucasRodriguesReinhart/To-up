# Ilha 1 (Naruto / Vila da Folha) — PASS 1: análise das referências

Referências aprovadas em `refs/`, todas do MESMO espaço:

| arquivo | o que mostra | câmera aproximada |
|---|---|---|
| `ref_14_ilha_a_sul_alto` | ilha inteira a partir do sul, alto | sul, ~40° de mergulho |
| `ref_15_ilha_b_sudoeste` | ilha a partir de sul-sudoeste | SSW, ~40° |
| `ref_16_ilha_c_sudoeste_baixo` | ponte de chegada, roda d'água, ponte de saída | SW, ~30°, mais baixo |
| `ref_17_ilha_d_norte` | vista de trás (a vila em primeiro plano) | norte, ~40° |
| `ref_18_ilha_e_topo_sul` | quase planta (a mais útil para medir) | sul, ~55° |
| `ref_08..12_summon_*` | a torre estrelada de invocação em 5 ângulos | — |
| `ref_13_gate_dragonball_locked` | o portão de compra Dragon Ball bloqueado | — |

## 1. Estrutura macro (confirmada em 4 das 5 vistas da ilha)

```
                    penhasco alto + 2 cachoeiras + platô com casinhas
                  (T2) Salão principal redondo (telhado vermelho 2 níveis)
                       ladeado por 2 prédios redondos de telhado azul
                  (T1) muro de arrimo com 3 escadarias (centro, NO, NE)
   SUMMON (O-NO)  ──── ANEL PAVIMENTADO ──── roda d'água / riacho (L)
   praça estrela       FOSSO DE MINERAÇÃO          ponte longa → PORTÃO (NE)
   torre + banners     (terra, cristais azuis,
                        rochedo central)
                       escada curta sobe ao anel
                  PORTÃO DE ENTRADA (telhado verde, pilares vermelhos, 2 leões)
                       PONTE LONGA de chegada (vem do lobby)
```

A `ref_17` (vista de trás) mostra a ponte de saída indo para o sudeste, contra as outras 4, que põem o portão da
saída no NORDESTE. Regra 1 da missão (preservar a intenção recorrente): a saída fica a NE, saindo do lado leste
da vila por uma ponte elevada que passa por cima do vale do riacho (`ref_16`).

## 2. Medidas (px da `ref_18` → studs)

Escala tirada do fosso: raio 280 px ≈ 60 studs (4,7 px/stud na profundidade do fosso). A ponte de chegada tem a
largura da ponte do lobby (24 studs), que é a mesma da abertura do portão.

| elemento | na referência | decisão (studs) |
|---|---|---|
| fosso de mineração | elipse de raio 280 px | Ø 120 (raio 60), piso 7 abaixo do anel |
| anel pavimentado | raio externo ~380 px | de r 60 a r 82 (22 de largura), lanternas nas 2 bordas |
| portão de entrada | ~270 px de largura, colado no anel | 52 de largura, vão 20 × 18, eixo em y −110 |
| praça do portão → anel | escada curta logo atrás do portão | 5 degraus (G → anel, +4) |
| summon | centro a −118 em x, a NO do fosso | praça redonda Ø 56 em (−120, 22), torre na borda NO |
| salão principal | centro no eixo, ~2× o prédio azul | Ø 38 em (0, 158), no terraço T2 |
| prédios redondos azuis | ladeiam o salão | Ø 24 em (±52, 150) |
| ponte de saída | do canto NE da vila até o topo direito | largura 18, de (98, 96) a (170, 168), rumo 45° |
| portão da saída | extremo NE, penhasco próprio | ilhota de rocha em (178, 176) |
| roda d'água | a leste do anel, na altura do centro | (118, 12), no riacho |
| ponte em arco (madeira) | SE, sobre o riacho | (112, −40) |

## 3. Níveis (cota absoluta = Y do Roblox)

| nível | cota | onde |
|---|---|---|
| G | 6,2 | ponte do lobby (patamar dela já termina em 6,2), praça do portão, gramados S/SE/SO, vale do riacho |
| anel | 10,2 | anel pavimentado em volta do fosso |
| fosso | 3,2 | piso de terra do fosso |
| T1 | 16,2 | terraço em "C" que abraça o norte do anel: summon (O), vila baixa (N), início da ponte de saída (NE) |
| T2 | 22,2 | terraço do salão principal |
| penhasco | ~64 | paredão do fundo com o platô de cima |
| mar | −110 | só visual |

Degraus sempre com espelho 0,75–0,8 e piso 1,5–1,8 (o QA aceita até 2,3).

## 4. Linguagem visual

- **Paleta:** grama verde viva, calçamento bege claro, pedra de arrimo cinza-bege, terra do fosso marrom-laranja,
  penhascos castanho-dourados com frestas escuras, telhados vermelho-telha, azul-ardósia e verde, reboco creme,
  laca vermelha nos pilares, ouro nos detalhes e cristais azuis no fosso.
- **Arquitetura:** prédios redondos de telhado cônico em 1 ou 2 níveis, com beirais largos e óculo no topo, e
  casas quadradas de 1 pavimento com telhado de quatro águas. O salão principal é o maior volume e fica no eixo do
  portão.
- **Hierarquia (do mais forte ao mais fraco):** o salão principal fecha o eixo, a torre de summon é o marco
  vertical a oeste, o portão da saída é o marco a nordeste, o fosso é a massa central e o portão de entrada
  enquadra a primeira vista.
- **Bandeiras:** só 2 estandartes vermelhos com a folha na escadaria central da vila (edifício importante), os 2
  estandartes azuis da torre do summon e os da entrada e da saída. Nada de fileiras.
- **Vegetação:** árvores arredondadas em grupos que emolduram escadas e bordas, sakuras só perto do summon e do
  salão, e muito espaço negativo no anel e no fosso.
- **Água:** 2 quedas no paredão do fundo → canal leste → roda d'água → ponte em arco → queda no penhasco SE. Queda
  NO → poço → queda no penhasco oeste, sob o summon. Uma drenagem do fosso sai por uma galeria no muro SO e vira a
  queda à esquerda da ponte de chegada. São 5 quedas, cada uma com origem e destino.

## 5. O que muda por jogabilidade (e por quê)

- **Fosso raso (7) com escadas N/S e rampas de madeira L/O:** nas referências o fosso não tem acesso claro. Aqui
  ele tem 4 acessos e corredores livres até o rochedo central.
- **Rochedo central baixo (Ø 20):** a referência mostra um monte grande. Ele fica como o ponto dos minérios raros
  e continua baixo o bastante para não virar monumento nem bloquear o fosso.
- **Summon no nível T1:** ligado à vila por terra, com praça livre para vários jogadores e escada larga que desce
  ao anel.
- **Casas sem porta:** toda casa que não é entrável fica sem porta (janelas, varandas altas). As entráveis são 4:
  salão principal, loja de armas (prédio redondo azul oeste), ramen (T1) e o moinho de minério (roda d'água).
