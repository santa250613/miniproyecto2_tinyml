# 🦜 Cantos de Aves · TinyML — app "Modo Cazador"

**▶▶▶ VER LA APP FUNCIONANDO (click aquí):**
### 👉 https://santa250613.github.io/miniproyecto2_tinyml/

📓 Notebook de entrenamiento (Google Colab): https://colab.research.google.com/github/santa250613/miniproyecto2_tinyml/blob/main/notebooks/02_entrenamiento_aves.ipynb

Ese link abre la app publicada (GitHub Pages) — desafío de aves 🦜 + identificador por micrófono 🎯. Solo clic, no hay que instalar nada.

---

## Si prefieres correrla en tu propio PC

```bash
# 1. descargar el repo (botón verde Code → Download ZIP, o:)
git clone https://github.com/santa250613/miniproyecto2_tinyml.git
cd miniproyecto2_tinyml/app

# 2. servir por HTTP (necesario para el micrófono)
python3 -m http.server 8000

# 3. abrir en el navegador
#    http://localhost:8000
```

## Dos modos

| Modo | Qué hace | Requisito |
|---|---|---|
| 🦜 Desafío de Aves | Escucha un canto y adivina cuál ave es (4 opciones, marcador y racha) | Nada — funciona de una |
| 🎯 Identificador IA | Graba 7 s por micrófono y una red neuronal dirá qué ave es | Modelo en `app/modelo/` (ver README raíz, pasos "modelo") |

## Contenido de esta carpeta
- `index.html` — la app (2 pestañas)
- `css/style.css` — tema selva 🌿
- `js/app.js` — lógica: desafío + MFCC en JavaScript + TF.js
- `modelo/` — ✅ modelo ya entrenado (model.json + labels.json + pesos tfjs, 91 clips)

IA para Móviles · UAO 2026-2 · Sebastián Santana, Juan Camilo Díaz y César Armando Reyes · audios CC de xeno-canto.org