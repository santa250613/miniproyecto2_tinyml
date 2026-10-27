#!/usr/bin/env python3
"""Baja por la API de Edge Impulse las grabaciones con label <clase>-S<n> y arma el zip
para el notebook:  <nombre>/<clase>/<clase>_S<n>_<k>.wav

Uso:
  python3 descargar_api.py salida.zip [--sesiones 4,5]
  (API key en EI_API_KEY o en ~/.config/ei_api_key)
"""
import argparse, collections, io, json, os, re, sys, urllib.request, zipfile

API = 'https://studio.edgeimpulse.com/v1/api'
CLASES = ['garrapatero-comun', 'pellar-comun', 'pigua', 'bichofue-griton',
          'azulejo-comun', 'lora-andina', 'ave-no-registrada']
PATRON = re.compile(r'^(?P<clase>[a-z\-]+?)-s(?P<ses>\d+)$', re.I)

def clave():
    k = os.environ.get('EI_API_KEY')
    f = os.path.expanduser('~/.config/ei_api_key')
    if not k and os.path.exists(f): k = open(f).read().strip()
    if not k: sys.exit('❌ Falta la API key (EI_API_KEY o ~/.config/ei_api_key)')
    return k

def get(ruta, crudo=False):
    req = urllib.request.Request(API + ruta, headers={'x-api-key': clave()})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if crudo else json.load(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('salida'); ap.add_argument('--sesiones', default=None)
    a = ap.parse_args()
    quiero = {int(x) for x in a.sesiones.split(',')} if a.sesiones else None
    raiz = os.path.splitext(os.path.basename(a.salida))[0]

    pid = get('/projects')['projects'][0]['id']
    muestras, off = [], 0
    while True:
        r = get(f'/{pid}/raw-data?category=training&limit=200&offset={off}')
        muestras += r['samples']; off += 200
        if len(r['samples']) < 200: break
    cuenta, saltados = collections.Counter(), 0
    with zipfile.ZipFile(a.salida, 'w', zipfile.ZIP_DEFLATED) as z:
        for m in sorted(muestras, key=lambda m: m['id']):
            g = PATRON.match(m['label'])
            if not g or g['clase'] not in CLASES or (quiero and int(g['ses']) not in quiero):
                saltados += 1; continue
            c, s = g['clase'], int(g['ses'])
            cuenta[(c, s)] += 1
            wav = get(f'/{pid}/raw-data/{m["id"]}/wav?axisIx=0', crudo=True)
            z.writestr(f'{raiz}/{c}/{c}_S{s}_{cuenta[(c, s)]:02d}.wav', wav)
    print(f'Proyecto {pid}: {sum(cuenta.values())} clips bajados, {saltados} saltados')
    for c in CLASES:
        por = {s: n for (cc, s), n in sorted(cuenta.items()) if cc == c}
        if por: print(f'  {c:18} {por}')
    print('✅', os.path.abspath(a.salida))

if __name__ == '__main__':
    main()
