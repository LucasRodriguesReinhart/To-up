# coleta_capturas.py - copia as capturas mais recentes do Studio (View > Screenshot) para pranchas/ com nomes dados.
# uso: python coleta_capturas.py <minutos> nome1 nome2 ...  (as N mais recentes, em ordem cronologica)
import os, sys, glob, shutil, time
SRC = r'C:\Users\lucas\OneDrive\Imagens\Roblox'
R = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(R, 'pranchas'); os.makedirs(OUT, exist_ok=True)
minutes = float(sys.argv[1]); names = sys.argv[2:]
files = [f for f in glob.glob(os.path.join(SRC, 'RobloxScreenShot*.png')) if time.time() - os.path.getmtime(f) < minutes * 60]
files.sort(key=os.path.getmtime)
files = files[-len(names):]
if len(files) < len(names):
    print('AVISO: so', len(files), 'capturas recentes para', len(names), 'nomes')
for f, n in zip(files, names[-len(files):]):
    dst = os.path.join(OUT, n + '.png'); shutil.copy2(f, dst); print(os.path.basename(f), '->', n + '.png')
