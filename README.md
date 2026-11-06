# 🛰️ DeepSpill AI — Autonomous Satellite Radar & Optical Maritime Oil Spill Detection System

[![Infosys Springboard AI 6.0](https://img.shields.io/badge/Infosys%20Springboard-AI%206.0%20Internship-007ACC?style=for-the-badge&logo=infosys&logoColor=white)](https://springboard.infosys.com/)
[![Sentinel-1 SAR](https://img.shields.io/badge/ESA%20Copernicus-Sentinel--1%20SAR-004B87?style=for-the-badge&logo=satellite&logoColor=white)](https://sentinels.copernicus.eu/)
[![TensorFlow 2.17](https://img.shields.io/badge/Model-TensorFlow%202.17%20%2F%20Keras-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org/)
[![Test Accuracy 92.75%](https://img.shields.io/badge/Held--Out%20Test%20Accuracy-92.75%25-brightgreen?style=for-the-badge)](https://github.com/akshatraikar11/INFOSYS-_INTERNSHIP-OIL_SPILL_DETECTION-)
[![Streamlit](https://img.shields.io/badge/HUD-Streamlit%201.40-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![React 18](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Microservice-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Node.js 22](https://img.shields.io/badge/Gateway-Node.js%2022%20%2F%20Express-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)

---

## 📖 Executive Summary

**DeepSpill AI** is an enterprise-grade maritime remote sensing intelligence solution engineered during the **Infosys Springboard AI Internship 6.0 (Milestones 1–4, Modules 1–7)**. 

Leveraging European Space Agency (ESA) **Copernicus Sentinel-1 Synthetic Aperture Radar (SAR)** and high-resolution optical imagery, DeepSpill autonomous delineates offshore oil slicks from natural ocean backscatter. By fusing an ImageNet-pretrained **EfficientNet-B0 Transfer Learning U-Net** with **Marangoni capillary damping physics**, **Bonn Agreement thickness estimation**, and **IMO 4-tier emergency protocols**, DeepSpill provides sub-pixel segmentation and automated decision support for maritime authorities, coastal environmental agencies, and clean-up skimmer dispatch.

---

## 🏛️ System Architecture

DeepSpill provides dual deployment modes: a lightweight **Streamlit Mission Control HUD** for field operators and an **Enterprise 3-Tier Full-Stack Suite** with asynchronous microservice orchestration and SQLite audit logging.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      DEEPSPILL OPERATOR CLIENTS                        │
├─────────────────────────────────────────┬──────────────────────────────┤
│ 1. React 18 Cyber HUD (Port 5173)       │ 2. Streamlit HUD (Port 8501) │
│    - Drag & Drop Satellite Upload       │    - Multimodal Dual Sensor  │
│    - 1-Click SAR Benchmark Scenes       │    - Look-Alike Veracity Card│
│    - Multi-View Gallery (Tri-View)      │    - Bonn Volume Estimation  │
└────────────────────┬────────────────────┴──────────────────────────────┘
                     │ HTTP / Multipart REST
                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   NODE.JS 22 EXPRESS API GATEWAY (Port 3001)           │
│  - Multipart Image Payload Streaming    - Sample Benchmark Feeds       │
│  - Native SQLite Audit Persistence      - CORS Security & Rate Limits  │
└────────────────────┬───────────────────────────────────────────────────┘
                     │ Forwarding /api/predict (:8000)
                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│             PYTHON FASTAPI MACHINE LEARNING SERVICE (Port 8000)         │
│  - Pretrained EfficientNet-B0 U-Net     - Morphological Noise Filter   │
│  - Dynamic SAR Damping Constraint       - Calibrated Cutoff (T = 0.85) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Syllabus Alignment (Infosys Springboard AI 6.0)

The project directly maps to all 4 Milestones and 7 Modules of the internship curriculum:

| Milestone | Curriculum Module | Technical Implementation in `Oil_Spill_Detection.ipynb` |
| :--- | :--- | :--- |
| **Milestone 1** | **Module 1: Dataset Acquisition & Scanner** | Multi-class M4D / Zenodo SAR scanner with automated train/val/test carving (852 train / 150 val / 110 test). |
| **Milestone 2** | **Module 2: Preprocessing & SAR Physics** | Bilateral speckle filtering, CLAHE contrast equalization, Marangoni capillary wave damping, and multi-class mask normalizer. |
| **Milestone 2** | **Module 3: Deep Learning Architectures** | Pretrained EfficientNet-B0 Transfer Learning U-Net (9.05M params) with hierarchical skip connections vs. Custom Residual U-Net. |
| **Milestone 3** | **Module 4: SOTA Loss & Training Pipeline** | Hybrid Focal-Tversky + Sørensen-Dice + Weighted BCE loss to conquer extreme class imbalance (98% ocean vs 2% oil). |
| **Milestone 4** | **Module 5: Model Evaluation & Benchmarks** | Normalized pixel & image confusion matrices, 5-axis polar radar charts, and decision threshold calibration ($T = 0.85$). |
| **Milestone 4** | **Module 6: Streamlit Mission Control App** | Interactive `streamlit_app.py` HUD featuring look-alike physical veracity cards and Bonn Agreement volume estimation. |
| **Milestone 4** | **Module 7: Enterprise Full-Stack Deployment** | React 18 + Node.js 22 + FastAPI 3-tier microservice architecture with SQLite persistence and 1-click batch launcher. |

---

## 📈 Verified Model Performance

Evaluated on the held-out Sentinel-1 SAR test set (110 authentic scenes) using the calibrated decision cutoff ($T = 0.85$):

| Evaluation Metric | Baseline U-Net | DeepSpill Transfer U-Net (Ours) | Relative Improvement |
| :--- | :---: | :---: | :---: |
| **Overall Pixel Accuracy** | 81.20% | **92.75%** | **+11.55%** |
| **Mean IoU (Jaccard Index)** | 0.62 | **0.82** | **+32.2%** |
| **Sørensen-Dice Score (F1)** | 0.69 | **0.88** | **+27.5%** |
| **True Positive Recall (Oil Pixels)** | 71.4% | **89.0%** | **+17.6%** |
| **Precision (False Positive Rejection)** | 64.0% | **87.0%** | **+23.0%** |
| **Look-Alike False Alarms (`img_0002.jpg`)** | 96,799 px | **2,790 px** | **97.1% Reduction** |

> **Addressing the Accuracy Paradox:** Satellite marine scenes are ~98% sea surface and ~2% oil slick. Conventional models achieve high accuracy simply by predicting all-black masks. DeepSpill monitors **IoU** and **Dice**, ensuring the **89% recall** and **87% precision** reflect genuine boundary segmentation.

---

## 🌊 Physical SAR Principles & IMO Standards

1. **Marangoni Capillary Damping:**
   Oil films reduce the surface tension of sea water, suppressing short capillary gravity waves. Synthetic Aperture Radar detects this as severe backscatter damping ($\Delta \sigma^0 \ge -3.5\text{ dB}$).
2. **Look-Alike Discrimination:**
   Natural biogenic slicks (fish oils, algal blooms) lack sharp boundary transitions. DeepSpill applies edge gradient analysis ($\nabla I$) and physical thresholding to eliminate low-wind look-alikes.
3. **Bonn Agreement Oil Thickness Estimation:**
   $$\text{Contaminated Volume } (m^3) = \text{Area } (km^2) \times \text{Weighted Thickness Factor } (\mu m)$$
4. **4-Tier IMO Incident Severity Matrix:**
   * **Tier 0 — Maritime Surface Clear:** Nominal ambient envelope ($\text{Ratio} < 0.005$).
   * **Tier 1 — Minor Sheen Discharge:** Operational bilge or sheen ($< 0.25\text{ km}^2$).
   * **Tier 2 — Moderate Harbor Spill:** Local containment boom advisory ($0.25 - 1.50\text{ km}^2$).
   * **Tier 3 — Major Maritime Oil Spill:** Regional Coast Guard skimming triggered ($1.50 - 5.00\text{ km}^2$).
   * **Tier 4 — Catastrophic Contamination:** National emergency response ($> 5.00\text{ km}^2$).

---

## 🚀 1-Click Launch Instructions (Windows)

### Option A: Enterprise Full-Stack Suite (React + Express + FastAPI)
Simply **double-click** the included batch script:
```bash
start_fullstack.bat
```
* Automatically supervises Python FastAPI (:8000), Node.js Express (:3001), and React Vite (:5173).
* Launches your default web browser directly to `http://localhost:5173`.
* Press `Ctrl+C` in the console window to stop all 3 services gracefully.

### Option B: Streamlit Mission Control HUD
Simply **double-click**:
```bash
start_streamlit.bat
```
* Opens the standalone Streamlit dashboard at `http://localhost:8501`.

---

## 💻 Manual CLI Execution

### 1. Python Environment Setup
```bash
python -m venv deepspill-venv
deepspill-venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Launch FastAPI Inference Microservice
```bash
uvicorn inference.server:app --host 127.0.0.1 --port 8000
```

### 3. Launch Node.js API Gateway
```bash
cd backend
npm install
npm start
# Gateway listens on http://localhost:3001
```

### 4. Launch React Production Dashboard
```bash
cd frontend
npm install
npm run dev
# Dashboard available on http://localhost:5173
```

---

## 📁 Repository Structure

```
DeepSpill/
├── 📂 backend/                    # Node.js 22 Express API Gateway (Port 3001)
│   ├── server.js                  # Multipart file streaming, sample routes, SQLite persistence
│   └── package.json
├── 📂 frontend/                   # React 18 + Vite Cyber HUD Dashboard (Port 5173)
│   ├── src/
│   │   ├── App.jsx                # Mission control UI, file upload, multi-view comparisons
│   │   ├── App.css                # Glassmorphic cyber-maritime telemetry styles
│   │   └── api.js                 # Axios REST client integration
│   ├── dist/                      # Pre-built production bundle
│   └── package.json
├── 📂 inference/                  # Python FastAPI ML Microservice (Port 8000)
│   ├── server.py                  # Model inference, speckle filtering, postprocessing
│   └── test_inference.py          # Automated endpoint test suite
├── 📂 data/                       # Sentinel-1 SAR Dataset (395 MB)
├── 📂 docs/                       # Technical specifications & remote sensing guides
├── 📂 scripts/                    # Zenodo SAR dataset download & extraction tools
├── 📂 notebooks_archive/          # Preserved exploratory notebook drafts
│   ├── RGB_OilSpill_Detection.ipynb
│   └── SAR_Oil_Spill_Detection.ipynb
│
├── 📓 Oil_Spill_Detection.ipynb   # 🌟 PRIMARY MASTER NOTEBOOK (Modules 1-7, 92.75% Test Acc)
├── 🌐 streamlit_app.py            # 🌟 Streamlit Mission Control HUD (Port 8501)
├── ⚡ start_fullstack.bat         # 🚀 1-Click Double-Tap Launcher (Full-Stack)
├── ⚡ start_streamlit.bat         # 🚀 1-Click Double-Tap Launcher (Streamlit)
├── ⚙️ run_fullstack.py            # Multi-process supervisor for Full-Stack
├── 🧠 unet_oilspill_best.keras    # Trained SOTA EfficientNetB0 U-Net Weights (9.05M params)
├── 🧠 oil_spill_model.h5          # Legacy Model Weights
├── 📋 model_config.json           # Calibrated Metadata & Optimal Threshold (T = 0.85)
├── 🗄️ oil_spill_detections.db     # SQLite Detection Audit Ledger
├── 📄 requirements.txt            # Python Dependencies
├── 📑 DeepSpill.pdf               # Internship Problem Statement & Specs
└── 📘 README.md                   # Complete Production Documentation
```

---

## 🗄️ SQLite Database Schema (`oil_spill_detections.db`)

Every analysis run through the full-stack system is automatically recorded into the SQLite ledger:

| Column | Type | Description |
| :--- | :---: | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-increment unique detection identifier |
| `filename` | `TEXT` | File name of the satellite scene |
| `confidence` | `REAL` | Calculated contamination ratio ($0.000 - 1.000$) |
| `threshold` | `REAL` | Calibrated decision cutoff applied ($0.10 - 0.95$) |
| `spill` | `INTEGER` | Classification binary flag: `1` = Contaminated, `0` = Clear |
| `created_at` | `TEXT` | ISO 8601 UTC acquisition timestamp |

---

## 👨‍💻 Author & Project Credits

* **Developer:** **Akshat Raikar**
* **Program:** **Infosys Springboard AI Internship 6.0**
* **Track:** Artificial Intelligence & Machine Learning
* **Domain:** Computer Vision, Remote Sensing & Environmental AI

---

## 📜 Certification & Credential Verification

This engineering solution was officially evaluated and completed under **Infosys Limited** and **Infosys Springboard**:

<p align="center">
  <img src="docs/infosys_certificate.png" alt="Infosys Springboard Certificate of Completion - Akshat Raikar" width="750" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);" />
</p>

* **Awarded To:** **Akshat Raikar**
* **Project Assignment:** `Internship 6.0 (B2): Development of AI-Driven System for Oil Spill Identification and Monitoring`
* **Issuing Authority:** **Infosys Limited** (Education, Training and Assessment)
* **Authentication Portal:** [verify.onwingspan.com](https://verify.onwingspan.com)

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute for educational, research, and non-commercial maritime safety applications.
