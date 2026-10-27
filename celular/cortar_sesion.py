"""Corta la grabación del celular en un WAV por clip.
Va siguiendo la grabación clip por clip: compara la envolvente (volumen en el tiempo) de un tramo
del original sesion_aves.wav alrededor de cada clip y busca dónde quedó en la grabación.
Aguanta que la grabación empiece tarde, se corte antes o pierda segundos en la mitad.
Uso: python3 cortar_sesion.py ~/Descargas/sesion_celular_XXXX.m4a 6 ../dataset
     (6 = número de sesión → <clase>_S6_NN.wav dentro de dataset/dataset_celular_s6.zip)"""
import sys, os, io, json, wave, zipfile, subprocess
import numpy as np
SR, HOP = 16000, 160                       # envolvente cada 10 ms
aqui = os.path.dirname(os.path.abspath(__file__))
grab, ses, ds = os.path.expanduser(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
info = json.load(open(os.path.join(aqui, 'sesion_aves.json')))

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', grab, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
w = wave.open(os.path.expanduser('~/Descargas/sesion_aves.wav'))
ORIG = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768

env = lambda v: np.log(np.sqrt(np.convolve(v**2, np.ones(HOP)/HOP, 'same')[::HOP]) + 1e-3)
EX, EO = env(x), env(ORIG)

def ncc(o, E):
    """Correlación normalizada de la plantilla o (sin media) contra cada posición de E (por FFT)."""
    n, L = len(o), len(E); m = 1 << int(np.ceil(np.log2(L + n)))
    num = np.fft.irfft(np.fft.rfft(E, m) * np.conj(np.fft.rfft(o, m)), m)[:L - n + 1]
    c1, c2 = np.concatenate([[0], np.cumsum(E)]), np.concatenate([[0], np.cumsum(E**2)])
    var = (c2[n:] - c2[:-n]) - (c1[n:] - c1[:-n])**2 / n
    return num / (np.sqrt(np.maximum(var, 1e-9)) * np.linalg.norm(o) + 1e-9)

# 1) tramos largos (20 s, cada 5 s) del original → dónde quedaron en la grabación (búsqueda global)
VENT, PASO = 20, 5
tramos = []                                  # (inicio en el original, desfase, calidad)
for t0 in np.arange(0, len(EO)/100 - VENT, PASO):
    o = EO[int(t0*100):int((t0+VENT)*100)]; o = o - o.mean()
    if len(EX) <= len(o): break
    c = ncc(o, EX); k = int(np.argmax(c))
    tramos.append((t0, k/100 - t0, c[k]))

# 2) desfases confiables: los que se repiten en ≥ 4 tramos seguidos (los sueltos son falsas coincidencias
#    con otro clip parecido). Hay más de uno si la grabación perdió segundos en la mitad.
confiables, racha = [], 1
for (_, d0, _), (_, d1, _) in zip(tramos, tramos[1:]):
    racha = racha + 1 if abs(d1 - d0) <= 0.05 else 1
    if racha >= 4 and all(abs(d1 - c) > 0.05 for c in confiables): confiables.append(d1)
print('desfases encontrados (s):', [round(d, 2) for d in confiables])

# 3) para cada clip, el desfase confiable que mejor alinea su entorno (clip ± 3 s), afinando ± 0,1 s
des = []
for c in info['clips']:
    a, b = int((c['ini'] - 3) * 100), int((c['fin'] + 3) * 100)
    o = EO[max(0, a):b]; o = o - o.mean(); mejor = (0, None)
    for d in confiables:
        lo = int((c['ini'] + d) * 100) - (int(c['ini']*100) - max(0, a)) - 10
        if lo < 0 or lo + len(o) + 20 > len(EX): continue
        q = ncc(o, EX[lo:lo + len(o) + 20]); k = int(np.argmax(q))
        if q[k] > mejor[0]: mejor = (q[k], (lo + k + (int(c['ini']*100) - max(0, a))) / 100 - c['ini'])
    des.append(mejor[1] if mejor[0] >= 0.6 else None)

perdidos, cuenta, carpeta = [], {}, f'dataset_celular_s{ses}'
z = zipfile.ZipFile(os.path.join(ds, carpeta + '.zip'), 'w', zipfile.ZIP_DEFLATED)
for c, d in zip(info['clips'], des):
    if d is None: perdidos.append((c['clase'], round(c['ini']))); continue
    t = c['ini'] + d
    i, j = int((t - 0.2) * SR), int((t + c['fin'] - c['ini'] + 0.8) * SR)
    if i < 0 or j > len(x): perdidos.append((c['clase'], round(c['ini']), 'borde')); continue
    cuenta[c['clase']] = cuenta.get(c['clase'], 0) + 1
    b = io.BytesIO()
    with wave.open(b, 'wb') as wo:
        wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(SR)
        wo.writeframes((np.clip(x[i:j], -1, 1) * 32767).astype(np.int16).tobytes())
    z.writestr(f"{carpeta}/{c['clase']}/{c['clase']}_S{ses}_{cuenta[c['clase']]:02d}.wav", b.getvalue())
z.close()
print('✅', os.path.join(ds, carpeta + '.zip'), cuenta, f'({sum(cuenta.values())} de {len(info["clips"])} clips)')
if perdidos: print(f'descartados {len(perdidos)} (no grabados o no coinciden):', perdidos)
