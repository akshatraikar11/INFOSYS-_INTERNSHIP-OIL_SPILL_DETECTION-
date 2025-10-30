

# 🌊 DeepSpill — Oil Spill Detection

**Deep Learning-powered real-time detection of oil spills in satellite and aerial imagery**

![Streamlit App](https://img.shields.io/badge/Framework-Streamlit-ff4b4b?logo=streamlit\&logoColor=white)
![TensorFlow](https://img.shields.io/badge/Backend-TensorFlow-orange?logo=tensorflow\&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌍 Overview

**DeepSpill** is designed to assist in early oil spill detection to prevent environmental disasters and improve marine ecosystem protection.  
Using semantic segmentation, the model identifies oil-contaminated regions in satellite imagery with confidence-based visualization.

---

## ✨ Features

- 🧩 **Deep Learning Model:** Trained using TensorFlow/Keras for high-precision spill segmentation.  
- 🖼️ **Interactive Streamlit Interface:** Upload and visualize spill detection results instantly.  
- 💾 **Integrated SQLite Database:** Stores detection history and metrics for future reference.  
- 📊 **Smart Post-Processing:** Reduces false positives from reflections and wakes.  
- ⚡ **AI Confidence Metrics:** Multi-level detection indicators (High, Medium, Low).
- 🚀 **Model Training & Hyperparameter Tuning** using KerasTuner  

---

## 🚀 Live Demo(Deployed)
👉 [Click here to view the deployed app](https://deepspill.streamlit.app/)

---

## 🧰 Tech Stack

| Category | Tools / Libraries |
|-----------|------------------|
| **Frontend** | Streamlit, HTML/CSS |
| **Backend** | Python, TensorFlow / Keras |
| **Database** | SQLite3 |
| **Visualization** | PIL, NumPy, Matplotlib |
| **Version Control** | Git & GitHub |

---

## 📈 Model Performance
| Metric | Value |
|---------|--------|
| Detection Accuracy | **97%** |
| Model | U-Net  |
| Framework | PyTorch |
| Dataset | Drone imagery (Zenodo) |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/akshatraikar11/INFOSYS-_INTERNSHIP-OIL_SPILL_DETECTION-.git
cd INFOSYS-_INTERNSHIP-OIL_SPILL_DETECTION-
```

### 2️⃣ Create and Activate Virtual Environment

python -m venv venv
venv\Scripts\activate     # for Windows
source venv/bin/activate  # for macOS/Linux


### 3️⃣ Install Dependencies

Make sure you have **Python 3.8+** installed.
Then install dependencies using:
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application and Upload an Image

```bash
streamlit run streamlit_oil_spill_app.py
```
Upload any satellite or aerial image (JPG, PNG, or TIFF) and view:

* The **AI-detected oil spill mask**
* The **confidence metrics**
* A **color-coded overlay visualization**

---

## 🧾 Dataset & Model

* Model File: `oil_spill_model.h5`
* Framework: **TensorFlow / Keras**
* Input Shape: `(128, 128, n_channels)`
* The model performs **semantic segmentation** to identify oil spill regions.
* Architecture: U-Net
* Input: RGB images (3 channels)
* Optimizer: Adam
* Loss: Binary Cross-Entropy


---

## 💾 Database Structure (`oil_spill_detections.db`)

Each detection is logged with:

| Field       | Type    | Description               |
| ----------- | ------- | ------------------------- |
| id          | TEXT    | Unique detection ID       |
| timestamp   | TEXT    | Time of detection         |
| filename    | TEXT    | Uploaded image name       |
| confidence  | REAL    | Model confidence          |
| severity    | TEXT    | Low/Medium/High/Critical  |
| location    | TEXT    | (Optional) Detection area |
| notes       | TEXT    | (Optional) User input     |
| image_path  | TEXT    | Path of uploaded image    |
| result_path | TEXT    | Path of generated overlay |
| is_alerted  | INTEGER | 1 if alert sent, else 0   |

---



## 📁 Folder Structure

```
📦 DeepSpill
├── .streamlit/ — Streamlit config (theme, layout) via config.toml
├── uploads/ — Saved uploaded images for detection
├── results/ — Saved overlays/masks (e.g., result_YYYYMMDD_HHMMSS.jpg )
├── venv/ — Local Python virtual environment (activate before running)
├── Oil_Spill_Detection.ipynb — Model training and evaluation notebook
├── streamlit_oil_spill_app.py — Main Streamlit application (UI + inference pipeline)
├── oil_spill_model.h5 — Trained TensorFlow/Keras segmentation model
├── oil_spill_detections.db — SQLite database for detections
├── requirements.txt — Python dependencies
└── README.md — Project documentation
```

---


## 🧑‍💻 Developed By

**Akshat Raikar**
*Infosys AI Internship Project*

> "Building AI tools that protect our oceans 🌊"

---

## 🪪 License

This project is licensed under the **MIT License** – feel free to use, modify, and distribute.

