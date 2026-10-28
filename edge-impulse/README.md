# Grabación del dataset con Edge Impulse

Cada ave se grabó varias veces y en sesiones distintas, porque el notebook valida dejando una sesión completa fuera.

## Reglas que seguimos

- Una grabación de Edge Impulse = un clip = un archivo.
- Una sesión es una toma continua (mismo volumen, misma posición, mismo día).
- Clips de 3 a 5 s; el notebook se queda con las partes de más energía.
- Al menos 15 clips por ave repartidos en 3 o más sesiones.

## Nombres de archivo

El label de Edge Impulse es el nombre del ave sin espacios:

```
garrapatero-comun   pellar-comun   pigua   bichofue-griton   azulejo-comun   lora-andina
```

La sesión va en el nombre del archivo, porque el notebook la lee de ahí:

```
<clase>_S<n>_<k>.wav      ejemplo: bichofue-griton_S1_03.wav
```

## Grabación automática con el Nano 33 BLE Sense

1. Flashear el firmware de Edge Impulse en el Nano y conectarlo con `edge-impulse-daemon`.
2. `EI_API_KEY=<clave> python3 grabar_auto.py <carpeta con audios por ave>`: el PC reproduce cada canto por los parlantes y el Nano graba 5 s con el label `<ave>-S<n>`. Sesiones S1, S2 y S3 a 100 %, 75 % y 55 % de volumen, 5 clips por ave en cada una.
3. Exportar los datos (o bajarlos por la API) y renombrarlos con `python3 renombrar_export.py <export> dataset_aves_nano.zip`.

## Sesiones S4 y S5

En estas sesiones también se grabó la clase `ave-no-registrada` con el Nano, para que las dos clases tuvieran el mismo micrófono. La reproducción pasa por `loudnorm` (ffmpeg) para que música y cantos suenen a un nivel parecido.

```bash
# API key en ~/.config/ei_api_key y edge-impulse-daemon corriendo
python3 grabar_auto.py <dataset_aves> --no-aves <carpeta con ave-no-registrada/> \
        --sesiones "4:0.9,5:0.65" --clips 8 --clips-no-aves 15
# para continuar si se corta: --clases <clase> --inicio <k>
python3 descargar_api.py dataset_nano_s45.zip --sesiones 4,5
```

## Más audio

Las grabaciones originales salen de [xeno-canto.org](https://xeno-canto.org) (licencia CC).
