# App "Modo Cazador"

App publicada: https://santa250613.github.io/miniproyecto2_tinyml/

Notebook de entrenamiento: https://colab.research.google.com/github/santa250613/miniproyecto2_tinyml/blob/main/notebooks/02_entrenamiento_aves.ipynb

## Correrla en el PC

```bash
git clone https://github.com/santa250613/miniproyecto2_tinyml.git
cd miniproyecto2_tinyml/app
python3 -m http.server 8000      # el micrófono necesita HTTP
# abrir http://localhost:8000
```

## Modos

| Modo | Qué hace |
|---|---|
| Desafío de Aves | Suena un canto y hay que adivinar el ave entre 4 opciones (con marcador y racha) |
| Identificador IA | Graba 7 s con el micrófono y el modelo dice qué ave es, o "ave no registrada" |

Para probar el identificador, lo mejor es abrir la app en el celular y reproducir el canto desde otro aparato (PC o parlante).

## Archivos

- `index.html`: la app
- `sesion.html`: graba sesiones largas con el celular para el dataset
- `css/style.css`: estilos
- `js/app.js`: quiz, grabación, MFCC en JavaScript e inferencia con TensorFlow.js
- `modelo/`: modelo entrenado (model.json, pesos y labels.json)

IA para Móviles · UAO 2026-2 · Sebastián Santana, Juan Camilo Díaz y César Armando Reyes · audios CC de xeno-canto.org
