#!/usr/bin/env python3
"""Graba automáticamente las 6 aves con el Nano 33 BLE Sense en Edge Impulse.

El PC reproduce cada canto por los parlantes y, al mismo tiempo, le pide al
Nano (conectado con edge-impulse-daemon) que grabe 5 s con label <ave>-S<n>.

Uso:
  EI_API_KEY=ei_xxx python3 grabar_auto.py <carpeta dataset_aves> [--clips 5] [--prueba]

  --prueba  graba un solo clip (pigua-S1) para revisar el volumen.
"""
import os, sys, json, time, glob, re, subprocess, tempfile, urllib.request, argparse

API = 'https://studio.edgeimpulse.com/v1/api'
CLASES = ['garrapatero-comun', 'pellar-comun', 'pigua',
          'bichofue-griton', 'azulejo-comun', 'lora-andina']
SESIONES = {1: 1.00, 2: 0.75, 3: 0.55}       # sesión → volumen de reproducción
LARGO_MS = 5000
SENSOR = 'Built-in microphone'

def api(ruta, datos=None):
    req = urllib.request.Request(API + ruta, method='POST' if datos is not None else 'GET',
                                 headers={'x-api-key': os.environ['EI_API_KEY'],
                                          'Content-Type': 'application/json'},
                                 data=json.dumps(datos).encode() if datos is not None else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if not res.get('success', False):
        sys.exit(f'❌ Edge Impulse: {res.get("error")}')
    return res

def contar(pid):
    return api(f'/{pid}/raw-data/count?category=training')['count']

def fuentes(carpeta, ave, sesion):
    """Clips de la sesión original equivalente (si no hay, cualquiera del ave)."""
    todos = sorted(glob.glob(f'{carpeta}/{ave}/*.wav'))
    propios = [f for f in todos if re.search(rf'_S{sesion}_', f)]
    return propios or todos

def audio_8s(a, b, destino):
    """Une dos clips de 4 s → 8 s, cubre los 2 s de espera del firmware + 5 s de grabación."""
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a, '-i', b, '-filter_complex',
                    '[0:a][1:a]concat=n=2:v=0:a=1', destino], check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('carpeta'); ap.add_argument('--clips', type=int, default=5)
    ap.add_argument('--prueba', action='store_true')
    a = ap.parse_args()

    pid = api('/projects')['projects'][0]['id']
    devs = [d for d in api(f'/{pid}/devices')['devices'] if d.get('remote_mgmt_connected')]
    if not devs:
        sys.exit('❌ No hay dispositivo conectado. ¿Está corriendo edge-impulse-daemon?')
    dev = devs[0]
    sensores = [s['name'] for s in dev.get('sensors', [])]
    if SENSOR not in sensores:
        sys.exit(f'❌ El dispositivo no tiene micrófono. Sensores: {sensores}')
    print(f'✅ Proyecto {pid} · dispositivo {dev["name"]} ({dev["deviceId"]})')

    plan = [('pigua', 1)] if a.prueba else [(ave, s) for s in SESIONES for ave in CLASES]
    n_clips = 1 if a.prueba else a.clips
    tmp = tempfile.mkdtemp()
    for ave, ses in plan:
        fs = fuentes(a.carpeta, ave, ses)
        for k in range(n_clips):
            label = f'{ave}-S{ses}'
            wav = f'{tmp}/play.wav'
            audio_8s(fs[(2 * k) % len(fs)], fs[(2 * k + 1) % len(fs)], wav)
            antes = contar(pid)
            api(f'/{pid}/device/{dev["deviceId"]}/start-sampling',
                {'label': label, 'lengthMs': LARGO_MS, 'category': 'training',
                 'intervalMs': 1000 / 16000, 'sensor': SENSOR})
            vol = str(int(65536 * SESIONES[ses]))
            subprocess.run(['paplay', '--volume', vol, wav])
            t0 = time.time()                          # esperar a que suba la muestra
            while contar(pid) <= antes:
                if time.time() - t0 > 90:
                    sys.exit(f'❌ La muestra {label} no llegó a Edge Impulse en 90 s')
                time.sleep(2)
            print(f'  🎙️ {label}  clip {k + 1}/{n_clips}  ✓')
    print('✅ Grabaciones terminadas. Total en training:', contar(pid))

if __name__ == '__main__':
    main()
