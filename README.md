# Cantos de Aves con TinyML (Miniproyecto 2)

IA para Móviles y Embebidos · UAO 2026-2 · Sebastián Santana, Juan Camilo Díaz y César Armando Reyes

Informe: [docs/Informe_Miniproyecto2_Aves_TinyML.pdf](docs/Informe_Miniproyecto2_Aves_TinyML.pdf) ([versión Word](docs/Informe_Miniproyecto2_Aves_TinyML.docx))
App: https://santa250613.github.io/miniproyecto2_tinyml/

## Idea

Un sistema TinyML que escucha el canto de 6 aves comunes del Valle del Cauca y dice cuál es, o "ave no registrada" si es otro sonido. Usamos la misma metodología del ejercicio KWS: MFCC calculados a mano en numpy y una red MLP pequeña. La demo es una app web, "Modo Cazador", con dos modos: un quiz para adivinar el ave por su canto y un identificador que usa el micrófono del celular.

## Las 6 aves

| # | Ave | Canto de referencia |
|---|-----|---------------------|
| 1 | Garrapatero común | https://www.youtube.com/watch?v=cXy-PI2FzSg |
| 2 | Pellar común | https://www.youtube.com/watch?v=FsAHVK_7mfo |
| 3 | Pigua | https://www.youtube.com/shorts/r1Hes0l5Mps |
| 4 | Bichofué gritón | https://www.youtube.com/shorts/Nb5J-ZJmBl0 |
| 5 | Azulejo común | https://www.youtube.com/shorts/xMFmLZLevJY |
| 6 | Lora andina | https://www.youtube.com/shorts/uJaGIdL4ZSQ |

## Cómo funciona

```
Grabaciones (xeno-canto, Arduino Nano 33 BLE Sense con Edge Impulse, celular)
    |  clips etiquetados por ave y por sesión (_S<n>_)
    v
Notebook en Colab
    MFCC en numpy -> MLP 1274-64-7
    Experimento A (split aleatorio) vs. Experimento B (una sesión fuera)
    exporta el modelo a TensorFlow.js
    v
App web "Modo Cazador" (celular)
    graba 7 s -> MFCC en JavaScript -> modelo -> "Es un Bichofué gritón (94 %)"
```

## Estructura

```
├── README.md
├── docs/
│   └── Informe_Miniproyecto2_Aves_TinyML.pdf / .docx   informe IEEE
├── dataset/                        zips de audio por sesión (S1 a S7)
├── edge-impulse/                   grabación del dataset con el Nano 33 BLE Sense
├── celular/                        sesión de grabación con el celular y recortes de YouTube
├── notebooks/
│   └── 02_entrenamiento_aves.ipynb datos -> MFCC -> MLP -> A vs. B -> exportar
└── app/
    ├── index.html                  app "Modo Cazador"
    ├── sesion.html                 página para grabar sesiones largas con el celular
    ├── css/style.css
    ├── js/app.js                   quiz + grabación + MFCC en JS + inferencia
    └── modelo/                     modelo exportado (model.json, pesos, labels.json)
```

## Cómo correrlo

1. **Entrenar:** abrir el [notebook en Colab](https://colab.research.google.com/github/santa250613/miniproyecto2_tinyml/blob/main/notebooks/02_entrenamiento_aves.ipynb) y darle *Entorno de ejecución → Ejecutar todo*. Descarga solo los zips de `dataset/` y al final baja `modelo_aves.zip`.
2. **Actualizar el modelo:** descomprimir `modelo_aves.zip` dentro de `app/modelo/`.
3. **Abrir la app:** usar el enlace de GitHub Pages, o en local `python3 -m http.server` dentro de `app/` y entrar a `http://localhost:8000` (el micrófono necesita HTTP o HTTPS).

## Créditos

Cantos de referencia: videos públicos de YouTube citados arriba. Clips del dataset: grabaciones con licencia CC de [xeno-canto.org](https://xeno-canto.org) y grabaciones propias con el Arduino Nano 33 BLE Sense y el celular. Metodología basada en el [Miniproyecto 1 — Bartender TinyML](https://github.com/caesar-dat-com/miniproyecto1-tinyml).
