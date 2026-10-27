"""Corta la grabación del celular en un WAV por clip, usando los barridos de sincronía.
Uso: python3 cortar_sesion.py ~/Descargas/sesion_celular_XXXX.webm 6 ../dataset
     (6 = número de sesión → archivos <clase>_S6_NN.wav y dataset/dataset_celular_s6.zip)"""
import sys, os, io, json, wave, zipfile, subprocess
import numpy as np
SR = 16000
aqui = os.path.dirname(os.path.abspath(__file__))
grab, ses, ds = os.path.expanduser(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
info = json.load(open(os.path.join(aqui, 'sesion_aves.json')))

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', grab, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768

d = 1.0; t = np.arange(int(d*SR)) / SR
ref = np.sin(2*np.pi*(1500*t + (6000-1500)/(2*d)*t**2))
def buscar(a, b):            # posición del barrido dentro de x[a:b] (correlación por FFT)
    seg = x[a:b]; n = len(seg) + len(ref)
    c = np.fft.irfft(np.fft.rfft(seg, n) * np.conj(np.fft.rfft(ref, n)), n)[:len(seg)-len(ref)]
    k = int(np.argmax(np.abs(c))); return a + k, np.abs(c[k]) / (np.median(np.abs(c)) + 1e-12)

dur_teo = info['barrido_fin'] - info['barrido_ini']
p1, q1 = buscar(0, min(len(x), 90*SR))                           # inicio: primeros 90 s
a2 = int(p1 + (dur_teo - 30) * SR)
p2, q2 = buscar(a2, min(len(x), a2 + 60*SR))                     # final: ±30 s de donde debería estar
escala = (p2 - p1) / (dur_teo * SR)
print(f'barrido inicio {p1/SR:.2f}s (calidad {q1:.0f}), final {p2/SR:.2f}s (calidad {q2:.0f}), escala reloj {escala:.5f}')
if q1 < 8 or q2 < 8 or abs(escala - 1) > 0.01:
    sys.exit('⚠️ No encontré bien los barridos: ¿se grabó el audio completo desde antes del inicio?')

carpeta = f'dataset_celular_s{ses}'
cuenta, z = {}, zipfile.ZipFile(os.path.join(ds, carpeta + '.zip'), 'w', zipfile.ZIP_DEFLATED)
for c in info['clips']:
    i = int(p1 + (c['ini'] - info['barrido_ini'] - 0.2) * SR * escala)
    j = int(p1 + (c['fin'] - info['barrido_ini'] + 0.8) * SR * escala)
    seg = np.clip(x[i:j], -1, 1)
    cuenta[c['clase']] = cuenta.get(c['clase'], 0) + 1
    b = io.BytesIO()
    with wave.open(b, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((seg*32767).astype(np.int16).tobytes())
    z.writestr(f"{carpeta}/{c['clase']}/{c['clase']}_S{ses}_{cuenta[c['clase']]:02d}.wav", b.getvalue())
z.close()
print('✅', os.path.join(ds, carpeta + '.zip'), cuenta)
