"""dataset_youtube.zip a partir de los 6 videos de YouTube que usa la app (README).
- <clase>_completo.wav : el video entero (para armar sesion_youtube.wav; el notebook lo salta)
- <clase>_S7_NN.wav    : ~14 recortes de 5 s desplazados a lo largo del video (sesión 7)
Bajar los audios: yt-dlp -x --audio-format wav -o "<clase>.%(ext)s" <url>
Uso: python3 crear_dataset_youtube.py <carpeta con <clase>.wav> ../dataset"""
import sys, os, io, wave, zipfile, subprocess
import numpy as np
SR, LARGO, N = 16000, 5.0, 14
CLASES = ['garrapatero-comun', 'pellar-comun', 'pigua', 'bichofue-griton', 'azulejo-comun', 'lora-andina']
carpeta, ds = sys.argv[1], sys.argv[2]

def leer(r):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', r, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768

def wav(x):
    b = io.BytesIO()
    with wave.open(b, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1) * 32767).astype(np.int16).tobytes())
    return b.getvalue()

with zipfile.ZipFile(os.path.join(ds, 'dataset_youtube.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for c in CLASES:
        x = leer(os.path.join(carpeta, c + '.wav'))
        z.writestr(f'dataset_youtube/{c}/{c}_completo.wav', wav(x))
        L = int(LARGO * SR)
        if len(x) <= L:      # video corto: el video entero, corrido dentro de una ventana de 5 s
            inicios = np.linspace(0, L - len(x), N).astype(int)
            recortes = [np.concatenate([np.zeros(i), x, np.zeros(L - len(x) - i)]) for i in inicios]
        else:
            inicios = np.linspace(0, len(x) - L, N).astype(int)
            recortes = [x[i:i + L] for i in inicios]
        for k, r in enumerate(recortes, 1):
            z.writestr(f'dataset_youtube/{c}/{c}_S7_{k:02d}.wav', wav(r))
        print(f'{c:18} {len(x)/SR:5.1f} s → {len(recortes)} recortes')
