"""Arma sesion_aves.wav: todos los cantos (y no-aves) en orden mezclado, con un barrido de
sincronía al inicio y al final. Guarda sesion_aves.json con el tiempo de cada clip.
Uso: python3 crear_sesion.py ../dataset ~/Descargas
     python3 crear_sesion.py ../dataset ~/Descargas youtube
       → sesion_youtube.wav: los 6 videos de YouTube de la app (dataset_youtube.zip), 3 veces
         cada uno a distinto volumen, + 10 no-aves"""
import sys, os, io, json, wave, zipfile, random
import numpy as np
SR, GAP = 16000, 1.5

def leer(b):
    w = wave.open(io.BytesIO(b)); sr = w.getframerate(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    if ch > 1: x = x.reshape(-1, ch).mean(1)
    if sr != SR: x = np.interp(np.linspace(0, len(x)-1, int(len(x)*SR/sr)), np.arange(len(x)), x)
    return x

def nivelar(x, rms_obj=0.08):          # mismo volumen para todos, sin pasar de 0.95
    x = x * rms_obj / (np.sqrt(np.mean(x**2)) + 1e-9)
    return x * min(1, 0.95 / (np.abs(x).max() + 1e-9))

def barrido(d=1.0):
    t = np.arange(int(d*SR)) / SR
    return 0.6 * np.sin(2*np.pi*(1500*t + (6000-1500)/(2*d)*t**2)) * np.hanning(len(t))**0.2

ds, salida = sys.argv[1], os.path.expanduser(sys.argv[2])
modo = sys.argv[3] if len(sys.argv) > 3 else 'aves'
clips = []
random.seed(7)
if modo == 'youtube':                    # videos completos de YouTube (los que usa el quiz)
    with zipfile.ZipFile(os.path.join(ds, 'dataset_youtube.zip')) as z:
        for n in z.namelist():
            if n.endswith('_completo.wav'):
                for g in (1.0, 0.55, 0.3): clips.append((n.split('/')[-2], nivelar(leer(z.read(n))) * g))
    N_NO = 10
else:
    with zipfile.ZipFile(os.path.join(ds, 'dataset_aves.zip')) as z:   # cantos originales (xeno-canto)
        for n in z.namelist():
            if n.endswith('.wav'): clips.append((n.split('/')[-2], nivelar(leer(z.read(n)))))
    N_NO = 30
with zipfile.ZipFile(os.path.join(ds, 'dataset_no_aves.zip')) as z:    # música, ruido, otras aves
    nombres = sorted(n for n in z.namelist() if n.endswith('.wav'))
    for n in random.sample(nombres, N_NO):
        x = leer(z.read(n)); L = 5*SR
        if len(x) > L:   # los 5 s con más energía
            e = np.convolve(x**2, np.ones(SR//10), 'valid')[::SR//10]
            i = int(np.argmax([e[k:k+50].sum() for k in range(max(1, len(e)-50))])) * (SR//10)
            x = x[i:i+L]
        clips.append(('ave-no-registrada', nivelar(x)))
random.shuffle(clips)

sil = lambda s: np.zeros(int(s*SR))
partes, linea, t = [sil(1), barrido(), sil(2)], [], 4.0
for c, x in clips:
    linea.append({'clase': c, 'ini': t, 'fin': t + len(x)/SR})
    partes += [x, sil(GAP)]; t += len(x)/SR + GAP
partes += [barrido(), sil(1)]
fin_barrido = t
audio = np.concatenate(partes)
with wave.open(os.path.join(salida, f'sesion_{modo}.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((audio*32767).astype(np.int16).tobytes())
json.dump({'barrido_ini': 1.0, 'barrido_fin': fin_barrido, 'clips': linea},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'sesion_{modo}.json'), 'w'), indent=1)
print(f'{len(clips)} clips, {len(audio)/SR/60:.1f} min →', os.path.join(salida, f'sesion_{modo}.wav'))
print({c: sum(1 for k, _ in clips if k == c) for c in sorted(set(k for k, _ in clips))})
