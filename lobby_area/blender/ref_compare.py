# ref_compare.py - compoe render (fundo transparente) sobre a referencia: lado a lado, sobreposicao 50% e
# diferenca de silhueta/arestas. Uso: python ref_compare.py <render.png> <saida_prefixo> [ref.png]
import sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

R = os.path.dirname(os.path.abspath(__file__))
REF_DEFAULT = os.path.join(R, '..', 'refs', 'user_00_line6.png')

def edges(gray):
    a = np.asarray(gray.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    a = a / max(a.max(), 1)
    return a

def main(render_path, out_prefix, ref_path=REF_DEFAULT):
    ref = Image.open(ref_path).convert('RGB')
    ren = Image.open(render_path).convert('RGBA')
    if ren.size != ref.size:
        ren = ren.resize(ref.size, Image.LANCZOS)
    alpha = np.asarray(ren.split()[3], dtype=np.float32) / 255
    ren_rgb = ren.convert('RGB')
    # 1) sobreposicao 50%: onde ha modelo, mistura; onde nao ha, referencia
    a3 = np.repeat(alpha[..., None], 3, -1)
    over = np.asarray(ref, dtype=np.float32) * (1 - .5 * a3) + np.asarray(ren_rgb, dtype=np.float32) * (.5 * a3)
    Image.fromarray(over.astype(np.uint8)).save(out_prefix + '_overlay50.png')
    # 2) diferenca: silhueta do modelo (contorno ciano) + arestas da referencia (vermelho) sobre a referencia escurecida
    sil = Image.fromarray((alpha * 255).astype(np.uint8))
    sil_edge = edges(sil)
    ref_edge = edges(ref.convert('L'))
    base = np.asarray(ref, dtype=np.float32) * .35
    base[..., 0] = np.maximum(base[..., 0], ref_edge * 255)                 # vermelho = arestas da referencia
    base[..., 1] = np.maximum(base[..., 1], sil_edge * 255)                 # ciano = silhueta do modelo
    base[..., 2] = np.maximum(base[..., 2], sil_edge * 255)
    # preenchimento fraco da silhueta para ler a area coberta
    base = base * (1 - .18 * a3) + np.array([40, 160, 200], dtype=np.float32) * (.18 * a3)
    Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).save(out_prefix + '_diff.png')
    # 3) lado a lado
    W, H = ref.size
    sheet = Image.new('RGB', (W * 2 + 10, H), (20, 20, 20))
    sheet.paste(ref, (0, 0)); sheet.paste(ren_rgb, (W + 10, 0))
    sheet.save(out_prefix + '_lado.png')
    print('ok', out_prefix, 'cobertura modelo=%.1f%%' % (alpha.mean() * 100))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else REF_DEFAULT)
