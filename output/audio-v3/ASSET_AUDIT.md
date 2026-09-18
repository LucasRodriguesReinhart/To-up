# Auditoria de fontes de audio - 17/09/2026

Foram consultados metadados de 25 IDs existentes e feitas 27 buscas no Creator Store. Esta subtarefa foi somente leitura no Studio: nao inseriu assets, nao alternou modo e nao ouviu ou validou carregamento dos candidatos.

O catalogo `ASSET_CANDIDATES.json` registra nomes, IDs, duracoes declaradas, criadores, links, recomendacoes e resultados brutos. A shortlist usa ProSoundEffects para todos os efeitos novos. A [documentacao oficial de audio](https://create.roblox.com/docs/audio/assets) descreve o uso de audio gratuito do Creator Store nas experiencias Roblox; nenhuma permissao de extracao/reuso externo foi presumida.

| Familia | IDs recomendados | Observacao |
|---|---|---|
| Pedra | 9118598279, 9118598469, 9118598729, 9118598470, 9118598240 | 0,4 a 0,8 s; cinco variacoes PSE |
| Whoosh | 9120972321, 9120972444, 9120972323 | Existentes confirmados PSE; 0,8/0,8/0,9 s |
| UI click/toggle | 9119717523, 9119717529 | Switch Click, 0,4/0,5 s |
| UI erro | 9125540237 | Electronic Tinkles Falling Beeps, 0,6 s |
| Pickup cristalino | 9125531715, 9125531911 | Crystalline Gated Blips, 0,7 s |
| Cristal fisico | 9114619221 | Glass Tinks 3, 2,7 s; precisa recorte ouvido |
| Moeda | 9125509503, 9125444889 | Metal de moeda, 1,4/1,6 s; crop/envelope |
| Portal | 9125636853, 9125515917 | Magic Glow/Hum, 36 s; emenda ainda nao ouvida |
| Forja | 9112780438, 9112780193 | Fireplace Constant Flame, 36 s; metadata Loop |
| Vento natural | 9116258071 | Leaves Rustle Wind, 75,8 s; inclui passaros |
| Agua | 9112855484, 9120551511 | Chuva suave em agua (Loop) / cachoeira; 36 s |

Problemas encontrados: o erro de UI atual e um Metal Hits de 3,6 s, desacelerado ainda mais; o metal de golpe tem caudas de 1,255 a 2,619 s no runtime anterior. Isso pede limites de duracao e releases, nao apenas volume menor. A moeda 4608067546 pede credito ao uploader; o pickup 93529351909119 credita Freesound sem esclarecer licenca. Recomenda-se substituir ambos pela shortlist PSE.

Musicas atuais: Woodle Caves (112898538778548), Hidden Lotus Pond (82061470648013) e The Forgotten Crypt (131334832939011) pertencem a DistrokidOfficial; Space Atmosphere (1845421369), Mysterious Forest (9048681794), Pirate King (1835322563) e Home Bound (1845676363) pertencem a APMOfficial. Propriedade foi confirmada por GetProductInfo, com AssetType3. A adequacao musical exige audicao, e nenhuma fonte foi declarada como trilha de anime.

Revisao critica: nomes e metadados ajudam a reduzir candidatos, mas nao substituem ouvir ataques, timbre, clique da emenda e mascaramento na mix. Duracoes declaradas podem divergir de TimeLength. A configuracao verifiedCreatorsOnly retornou uploads com IP de jogos; portanto foi rejeitada como prova suficiente de direitos. O catalogo prioriza o criador PSE e descricao de proveniencia explicita.
