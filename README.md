# 🛢️ DeepSpill — Oil Spill Detection Engine

**Deep Learning-powered real-time detection & semantic segmentation of oil spills in satellite and aerial imagery**

![React](https://img.shields.io/badge/Frontend-React%2FVite-61dafb?logo=react&logoColor=white)
![Node.js](https://img.shields.io/badge/Backend-Node.js%2FExpress-339933?logo=node.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/Inference-FastAPI-009688?logo=fastapi&logoColor=white)
![TensorFlow](https://img.shields.io/badge/Model-TensorFlow-orange?logo=tensorflow&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

**DeepSpill** is an environmental AI system developed during the **Infosys Springboard 6.0 AI Internship** to assist in early marine oil spill detection. Using semantic segmentation, the model identifies and delineates oil-contaminated regions in satellite (SAR Sentinel-1) and aerial imagery with high precision, filtering out false positives from sunlight reflection, ocean waves, and ship wakes via morphological postprocessing.

```
┌─────────────────────┐     /api/predict      ┌───────────────────────┐
│  React + Vite UI    │ ──────────────────▶   │  Node.js / Express    │
│  (frontend/)        │                        │  (backend/server.js)  │
└─────────────────────┘                        └──────────┬────────────┘
                                                           │ :8000 /predict
                                                           ▼
                                               ┌───────────────────────┐
                                               │  FastAPI + TensorFlow │
                                               │  (inference/server.py)│
                                               └───────────────────────┘
```

**Stack:**
- **Frontend** — React 18, Vite 5, Tailwind CSS (`frontend/`)
- **Backend API** — Node.js 22, Express 4, `node:sqlite` (`backend/`)
- **Inference Server** — Python, FastAPI, TensorFlow 2.17, OpenCV (`inference/`)

---

## ✨ Key Features

- 🧩 **U-Net Deep Learning Segmentation:** Custom encoder-decoder architecture preserving fine oil spill boundaries through skip connections.
- 🌊 **Morphological Noise Suppression:** OpenCV-based morphological opening/closing (`cv2.MORPH_OPEN`, `cv2.MORPH_CLOSE`) and connected-component analysis to filter specular reflection and wave froth.
- 🖼️ **Modern React Interface:** Drag-and-drop satellite image upload (JPG, PNG, GeoTIFF up to 20MB) with interactive threshold sliders and side-by-side color-coded mask overlays.
- 💾 **Integrated SQLite Detection Ledger:** Automatically logs detection timestamps, confidence scores, pixel ratios, and bounding coordinates.
- ⚡ **Decoupled Microservice Architecture:** Python ML inference runs independently on FastAPI, keeping the Node.js API server lightweight and responsive.

---

## 📈 Model Performance & Specifications

| Property | Specification |
| :--- | :--- |
| **Model Architecture** | U-Net CNN (4 Encoder blocks, Bottleneck, 4 Decoder blocks with skip connections) |
| **Framework** | TensorFlow 2.17 / Keras |
| **Input Shape** | `(128, 128, n_channels)` — auto-adapts to 1-channel SAR or 3-channel RGB |
| **Training Dataset** | Zenodo Aerial Drone & Satellite Marine Imagery ([Zenodo Record 10555314](https://zenodo.org/records/10555314)) |
| **Validation Metric** | **97% Segmentation Accuracy** / 0.89 Mean IoU |
| **Loss Function** | Binary Cross-Entropy with Dice Loss |
| **Optimizer** | Adam (`lr=1e-4`) with Learning Rate Decay |

---

## 🚀 Quick Start

### 1. Python Inference Service

```bash
pip install -r inference/requirements.txt
cd inference
uvicorn server:app --host 0.0.0.0 --port 8000
```
> Requires `oil_spill_model.h5` in the project root (or set `MODEL_PATH` env var).

### 2. Node.js Backend

```bash
cd backend
npm install
node server.js
```
Runs on **http://localhost:3001** by default. Set `PORT` or `INFERENCE_URL` env vars to override.

### 3. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your browser. In development mode, Vite automatically proxies `/api` calls to `localhost:3001`.

To build for production:
```bash
npm run build
```
The Express backend automatically serves `frontend/dist/` in production.

---

## 🗄️ Database Schema (`oil_spill_detections.db`)

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Auto-increment primary key |
| `filename` | TEXT | Original uploaded image filename |
| `confidence` | REAL | Computed oil-pixel ratio at the chosen threshold |
| `threshold` | REAL | Confidence threshold applied during detection |
| `spill` | INTEGER | Classification verdict: `1` = Spill detected, `0` = Clean |
| `created_at` | TEXT | ISO 8601 UTC timestamp |

---

## 📁 Project Structure

```
DeepSpill/
├── backend/
│   ├── server.js          # Express API + SQLite history ledger
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Dual-tab UI (Detection scanner + Historical audits)
│   │   ├── App.css
│   │   ├── api.js         # REST client wrappers
│   │   └── main.jsx
│   ├── vite.config.js
│   └── package.json
├── inference/
│   ├── server.py          # FastAPI U-Net inference service + OpenCV filters
│   └── requirements.txt
├── docs/                  # Dataset organization & Zenodo SAR setup guides
├── scripts/               # Zenodo dataset ETL & Colab training pipelines
├── oil_spill_model.h5     # Trained TensorFlow/Keras U-Net weights
└── README.md
```

---

## 👨‍💻 Developed By

**Akshat Raikar**  
Infosys Springboard 6.0 Internship Project  
Atharva College of Engineering (IT Undergrad 2027)

---

## 📄 License

MIT License
