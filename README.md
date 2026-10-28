# 🐦 Cantos de Aves — TinyML (Miniproyecto 2)

> IA para Móviles y Embebidos · UAO 2026-2 · Sebastián Santana, Juan Camilo Díaz y César Armando Reyes
> 📄 Informe IEEE: [docs/Informe_Miniproyecto2_Aves_TinyML.pdf](docs/Informe_Miniproyecto2_Aves_TinyML.pdf) ([.docx](docs/Informe_Miniproyecto2_Aves_TinyML.docx))
> Inspirado en la metodología del [Miniproyecto 1 — Bartender TinyML](https://github.com/caesar-dat-com/miniproyecto1-tinyml)

**La idea:** un sistema TinyML que **escucha el canto de 6 aves comunes del Valle del Cauca y las identifica**, con la misma metodología del Ejercicio KWS (MFCC a mano en numpy + MLP). La demo final es una **app web "Modo Cazador"** estilo parque zoológico: escucha un canto, adivina cuál ave es, y luego **identifica con el microfono** usando el modelo entrenado.

## 🎯 Las 6 aves

| # | Ave | Canto de referencia |
|---|-----|---------------------|
| 1 | Garrapatero común | https://www.youtube.com/watch?v=cXy-PI2FzSg |
| 2 | Pellar común | https://www.youtube.com/watch?v=FsAHVK_7mfo |
| 3 | Pigua | https://www.youtube.com/shorts/r1Hes0l5Mps |
| 4 | Bichofué gritón | https://www.youtube.com/shorts/Nb5J-ZJmBl0 |
| 5 | Azulejo común | https://www.youtube.com/shorts/xMFmLZLevJY |
| 6 | Lora andina | https://www.youtube.com/shorts/uJaGIdL4ZSQ |

## 🧭 Arquitectura

```
  🎙️ GRABACIONES (celular / Edge Impulse)
        │  clips de 3–5 s por ave, varias sesiones
        ▼
  📓 GOOGLE COLAB — notebook 02
        MFCC a mano en numpy (metodología KWS)
        → Experimento A (split aleatorio)  ← trampa: fuga por sesión
        → Experimento B (leave-one-session-out) ← métrica honesta
        → Keras → export TensorFlow.js + labels
        ▼
  🌐 APP WEB "Modo Cazador"
        · Desafío de Aves: suena un canto (YouTube embebido) y adivinas
        · Identificador: grabas 7 s con el micrófono → MFCC en el navegador
          → modelo TinyML (tfjs) → "Es un Bichofué gritón (94%)"
```

## 📁 Estructura

```
├── README.md                  ← este archivo
├── docs/
│   ├── metodologia.md         ← decisiones del pipeline (por qué MFCC, por qué sesión)
│   └── presentacion.md        ← guion de la presentación (5 min)
├── edge-impulse/
│   └── README.md              ← guía EXACTA para grabar el dataset (paso a paso)
├── notebooks/
│   └── 02_entrenamiento_aves.ipynb ← Colab: datos → MFCC → MLP → A vs B → export
└── app/
    ├── index.html             ← la app "Modo Cazador"
    ├── css/style.css
    ├── js/app.js              ← desafío + grabación + MFCC en JS + inferencia tfjs
    └── modelo/                ← AQUÍ va el modelo exportado por el Colab
        └── (model.json + grupo1-*.bin + labels.json)
```

## 🚀 Cómo correr

1. **Dataset** → dos vías:
   - **Edge Impulse (recomendada)**: subir el dataset zip del repo (`dataset/dataset_aves_nano.zip`, 91 clips 15-16 por ave) a *Data acquisition → Uploader* y grabar clips propios según `edge-impulse/README.md`. La base de datos vive en EI, como el KWS.
   - **Directa**: el zip ya está en el repo — tu dataset nuevo (`dataset/dataset_aves_nano.zip`, 91 clips, 16 kHz, ~15-16 por ave): usa `DATA_URL = 'https://raw.githubusercontent.com/santa250613/miniproyecto2_tinyml/main/dataset/dataset_aves_nano.zip'` (o el de 80 clips: `.../dataset/dataset_aves.zip`), o ejecuta sin URL (paths locales).
2. **Entrenar en Colab** → [abrir el notebook en Colab](https://colab.research.google.com/github/santa250613/miniproyecto2_tinyml/blob/main/notebooks/02_entrenamiento_aves.ipynb) → Entorno de ejecución → Ejecutar todo (descarga solo los 6 zips de `dataset/`) → se descarga `modelo_aves.zip`.
3. **Descomprimir** el zip en una carpeta temporal y **mover el contenido de `modelo_export/`** (model.json, group*.shard, labels.json) directamente a `app/modelo/` — app.js carga `modelo/model.json` y `modelo/labels.json`.
4. **Abrir la app** → `python3 -m http.server` en `app/` (necesita servir por HTTP para el micrófono) → `http://localhost:8000`.
5. O publicar con **GitHub Pages** → la app queda en línea para la demo.

## 🔑 Puntos fuertes para la sustentación

- Metodología **validada con el KWS**: front-end MFCC manual (ventana 25 ms / salto 10 ms, 40 filtros mel, 13 coeficientes), 1 s de audio útil → 1.274 features, modelo chico apto para embebido.
- **Split por sesión obligatorio**: los cantos se graban en tomas continuas; un split aleatorio filtra por sesión y miente (Experimento A vs B, como en el KWS: 100% vs 85,8%).
- Cero TensorFlow en el entrenamiento del core (numpy puro) → luego la misma red pasa a **TFLite/tfjs** para el edge y el navegador.

## 📜 Licencia / créditos

Cantos de referencia: videos públicos de YouTube citados arriba. Clips del dataset: **xeno-canto.org** (grabaciones comunitarias CC, 4 por ave). Dataset propio.