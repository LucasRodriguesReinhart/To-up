# Wano V3: brief comum da rodada 3

## Leitura obrigatória
- `FEEDBACK_R3.md` desta pasta e as 20 capturas `01`–`20`, que mostram o jogo real.
- As capturas valem mais que qualquer render do Blender: a V2 passou em todos os gates do Blender e mesmo assim foi reprovada no jogo.
- `../../OP_BRIEF.md` (regras gerais).
- `../FEEDBACK_USUARIO.md` (rodadas 1 e 2, ainda válidas).

## O que mudou no padrão de qualidade
1. **Refinamento antes de quantidade.**
   - Cada peça precisa sobreviver à câmera do jogador (olho a +5,5) e a uma câmera de cima a 20–40 studs, porque o usuário joga com zoom-out.
   - Nada de bloco chapado, junta torta, buraco, sobreposição ou peça solta.
2. **Nada flutua e nada atravessa.**
   - Toda peça apoiada tem a base tocando o suporte real (piso, parede, galho), com tolerância de 0,05.
   - Nenhuma peça entra noutra de outro dono sem intenção.
3. **Sem marca do anime.**
   - Proibido: Jolly Roger do chapéu de palha, carranca do Sunny, símbolos de personagens, logos e textos.
   - Permitido: estética japonesa genérica (mon de flor genérico, ondas, nuvens), pirataria genérica sem personagem (caveira simples original, âncora, timão).
   - Quando houver dúvida, não use.
4. **Colisão V3 = o que se vê é o que colide.**
   - O agente de colisão define o sistema.
   - Os donos de zona garantem que o visual seja **sólido e fechado** onde o jogador anda ou bate: piso contínuo, paredes com espessura, sem fresta.
   - Os donos de zona **não criam caixas invisíveis novas**.

## Regras
- **Escopo:**
  - Mexa só nos seus arquivos.
  - Se precisar de algo em arquivo de outro dono, descreva no relatório.
  - Releia o arquivo antes de editar: outro agente pode ter mexido.
- **Builds de teste:**
  - Só com `OP_OUT=<scratchpad>/op_r3_<sigla>/teste.blend`.
  - **Nunca** rode build sem `OP_OUT`: isso sobrescreve o `ilha_onepiece.blend` oficial.
  - O PC tem 16 GB e o Studio está aberto: **no máximo 2 Blenders ao mesmo tempo**.
    - Antes de cada build ou render, pegue uma vaga com `mkdir <scratchpad>/blender_slot1` (ou `blender_slot2`). O `mkdir` falhar quer dizer que a vaga está ocupada.
    - Se as 2 estiverem ocupadas, espere com um comando em background, por exemplo `until mkdir .../blender_slot1 2>/dev/null; do sleep 10; done`.
    - Solte a vaga com `rmdir` assim que o Blender terminar, inclusive em caso de erro.
    - O scratchpad é `C:\Users\lucas\AppData\Local\Temp\claude\C--Users-lucas-OneDrive-Desktop-To-up\47322845-c826-4095-8966-df3813237567\scratchpad`.
  - Use `--factory-startup`.
  - Renders em 960×540, sempre também com `FM_MAT_PREVIEW=roblox`.
- **Proibido:**
  - Roblox Studio MCP, Blender MCP ao vivo, computer-use, browser, commit, `taskkill`;
  - mexer fora de `ilha_onepiece/`;
  - editar `export_roblox.py` e `fm_lib.py`;
  - modelar minérios;
  - mudar a praça de mineração (centro livre), o núcleo AMS do Summon e o portão OPM (só o que for marca de anime).
- **Orçamento:** a ilha tem teto de 640k tris estáticos. Cresça só pagando com cortes em outro lugar e reporte os tris por dono.

## Entrega
- **Voltas:** no mínimo 3 de render → crítica honesta ("isso sobreviveria ao olho do usuário nas capturas 01–20?") → correção.
- **Folhas:** antes × depois, nas mesmas posições das capturas do usuário quando der.
- **Relatório curto:**
  - o que foi feito, item a item (R1–R8);
  - tris e colisão;
  - pendências.
