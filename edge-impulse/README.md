# 🎙️ Guía del dataset — grabaciones en Edge Impulse (paso a paso)

El modelo aprende **tu** audio: graba cada ave varias veces en sesiones distintas. Sigue esto al pie de la letra.

## 1. Reglas de oro

- **Clase 1 grabación = archivo 1.** Cada grabación en Edge Impulse es una muestra.
- **Sesión = una toma continua o un día/grupo de horas.** Esto es CLAVE: el experimento honesto (B) separa por sesión. Sin sesiones no se puede hacer la comparación A vs B.
- **Duración por clip: 3–5 s.** Luego el notebook recorta 1 s con más energía por su cuenta.
- **Mínimo 15–20 clips por ave y por lo menos 3 sesiones distintas** (p. ej. S1 mañana, S2 tarde, S3 otro día).

## 2. Nombrado (OBLIGATORIO — el notebook lo lee así)

Label de Edge Impulse = nombre del ave **sin espacios, con guiones**:

```
garrapatero-comun   pellar-comun   pigua   bichofue-griton   azulejo-comun   lora-andina
```

En Edge Impulse no puedes meter la sesión en el label sin romper las clases → hazlo en el **nombre de archivo**. Después de descargar el export, renombra así:

```
<clase>_S<1|2|3>_<n>.wav
```

Ejemplo: `bichofue-griton_S1_03.wav`

> Truco rápido: en tu PC, dentro de la carpeta de la clase, ejecuta:
> ```bash
> i=1; for f in *.wav; do mv "$f" "${f%.*}_S1_0${i}.wav"; i=$((i+1)); done
> ```
> (cambia `S1` por la sesión que corresponda a cada grupo de archivos).

## 3. Grabar

1. Edge Impulse → tu proyecto → **Data acquisition** → graba desde el celular (o sube audios) con label `<ave>`.
2. Colócate a ~3–5 m del ave (o reproduce el video de YouTube en un volumen natural y graba el ambiente — para la demo vale, pero anótalo como limitación).
3. Reparte cada ave en **≥3 bloques** distintos (hora o día) → eso serán S1/S2/S3 al renombrar.

## 4. Exportar y subir

1. Dashboard → **Data acquisition** → ⋮ → **Export data** → formato **WAV**, se descarga un zip.
2. Descomprime; debe quedar `train/<clase>/*.wav` (y quizá `test/`). Mueve todo junto: el notebook solo mira las carpetas `<clase>/`.
3. Sube el zip a Drive o a un enlace directo y pon el URL en la **celda 2** del notebook (`DATA_URL`).

## 5. Dataset de respaldo (opcional, para aumentar)

Si un día necesitas más audio público: **xeno-canto.org** tiene cantos reales por ave (busca por nombre común o científico). Úsalo solo como dataset de apoyo y dilo en la sustentación (distribución distinta de micrófonos = ruido de dominio).

## Checklist antes de entrenar

- [ ] 6 carpetas con los nombres exactos de arriba
- [ ] ≥ 15 clips por ave
- [ ] Todos los archivos tienen `_S<n>_`
- [ ] Audios de 3–5 s, sin ruido fuerte de fondo hablado
## Grabación automática con el Nano 33 BLE Sense (lo que se usó)

1. Flashear el firmware de Edge Impulse y conectar con `edge-impulse-daemon`.
2. `EI_API_KEY=<clave Admin> python3 grabar_auto.py <carpeta con audios por ave>` → el PC reproduce cada canto por los parlantes y el Nano graba 5 s con label `<ave>-S<n>` (S1 100 %, S2 75 %, S3 55 % de volumen; 5 clips por ave y sesión).
3. Exportar (o bajar por API) y convertir: `python3 renombrar_export.py <export> dataset_aves_nano.zip` → nombres `<ave>_S<n>_<k>.wav` listos para el notebook.

Limitación para la sustentación: la fuente son cantos reproducidos por parlante (no aves en vivo) y algunas sesiones repiten audios de origen.

## Sesiones S4–S5 (27-oct): más aves + clase de rechazo grabada con el Nano

Problema: la clase `ave-no-registrada` venía solo de YouTube (audio limpio) y las aves solo del Nano → el modelo podía separar "micrófono vs. limpio" en vez de cantos. Solución: grabar **las dos clases** con el Nano.

```bash
# API key en ~/.config/ei_api_key (chmod 600) y edge-impulse-daemon corriendo
python3 grabar_auto.py <dataset_aves> --no-aves <carpeta con ave-no-registrada/> \
        --sesiones "4:0.9,5:0.65" --clips 8 --clips-no-aves 15
# si se corta: --clases <clase> --inicio <k> para continuar sin repetir
python3 descargar_api.py dataset_nano_s45.zip --sesiones 4,5
```

- La reproducción pasa por `loudnorm` (ffmpeg) para que música y cantos suenen a nivel parecido (si no, la música saturaba el micrófono y eso sería otro atajo).
- Resultado (leave-one-session-out, umbral 40 %): aves bien nombradas 34 % → 53 %; aves rechazadas por error 43 % → 19 %; no-aves rechazadas 78 %.
