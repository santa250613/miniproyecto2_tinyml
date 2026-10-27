#!/usr/bin/env python3
"""Convierte el export WAV de Edge Impulse al formato del notebook.

En Edge Impulse se graba con label "<ave>-S<n>" (ej. pigua-S2).
Este script genera:  dataset_aves/<ave>/<ave>_S<n>_<k>.wav  y su zip.

Uso:  python3 renombrar_export.py <export.zip o carpeta> [salida.zip]
"""
import re, sys, shutil, zipfile, tempfile, pathlib, collections

CLASES = ['garrapatero-comun', 'pellar-comun', 'pigua',
          'bichofue-griton', 'azulejo-comun', 'lora-andina', 'ave-no-registrada']
PATRON = re.compile(r'^(?P<ave>[a-z\-]+?)-s(?P<ses>\d+)$', re.I)

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    origen = pathlib.Path(sys.argv[1]).expanduser()
    salida = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else 'dataset_aves_nano.zip').expanduser()
    tmp = pathlib.Path(tempfile.mkdtemp())
    if origen.suffix == '.zip':
        with zipfile.ZipFile(origen) as z:
            z.extractall(tmp / 'export')
        origen = tmp / 'export'

    destino = tmp / 'dataset_aves'
    cuenta = collections.Counter()
    saltados = []
    for wav in sorted(origen.rglob('*.wav')):
        label = wav.name.split('.')[0]          # Edge Impulse: <label>.<id>.wav
        m = PATRON.match(label)
        if not m or m['ave'] not in CLASES:
            saltados.append(wav.name); continue
        ave, ses = m['ave'], int(m['ses'])
        cuenta[(ave, ses)] += 1
        (destino / ave).mkdir(parents=True, exist_ok=True)
        shutil.copy(wav, destino / ave / f'{ave}_S{ses}_{cuenta[(ave, ses)]:02d}.wav')

    with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(destino.rglob('*.wav')):
            z.write(f, f.relative_to(tmp))

    print('Clips por ave y sesión:')
    for ave in CLASES:
        por_ses = {s: n for (a, s), n in sorted(cuenta.items()) if a == ave}
        total = sum(por_ses.values())
        aviso = '' if total >= 15 and len(por_ses) >= 3 else '  ⚠️ faltan (≥15 clips, ≥3 sesiones)'
        print(f'  {ave:18} total {total:3}  {por_ses}{aviso}')
    if saltados:
        print(f'Saltados ({len(saltados)}), label sin formato <ave>-S<n>:', saltados[:5])
    print('✅ Zip listo:', salida.resolve())

if __name__ == '__main__':
    main()
