

# 🛢️ Oil Spill Detection AI

**Deep Learning-powered real-time detection of oil spills in satellite and aerial imagery**

![Streamlit App](https://img.shields.io/badge/Framework-Streamlit-ff4b4b?logo=streamlit\&logoColor=white)
![TensorFlow](https://img.shields.io/badge/Backend-TensorFlow-orange?logo=tensorflow\&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌍 Overview

This project is a **complete AI-based system** that detects **oil spills** from satellite or aerial images using **deep learning (TensorFlow)** and a **Streamlit web interface**.
It is designed with a focus on:

* **Accuracy:** Reduces false positives from sunlight reflection or wave patterns.
* **Interactivity:** Real-time image uploads and visual results.
* **Automation:** Stores detections in a database and optionally sends **email alerts** for high-severity events.

---

## 🚀 Live Demo
👉 [Click here to view the deployed app](https://deepspill-oilspilldetection.streamlit.app/)


## ⚙️ Features

✅ **AI-Powered Detection** – Built using a custom-trained CNN model (`oil_spill_model.h5`)
✅ **Streamlit Web Interface** – Simple drag-and-drop interface for real-time predictions
✅ **Advanced Postprocessing** – Reduces false positives via shape and texture analysis
✅ **Overlay Visualization** – Displays color-coded confidence masks (Red, Orange, Yellow, Blue)
✅ **Detection History** – Automatically stores detections in `oil_spill_detections.db`
✅ **Monitoring Dashboard** – Real-time performance metrics and refresh mode
✅ **Email Alerts (Optional)** – Sends alerts when oil spills are detected above a threshold

---

## 🧠 System Architecture

```
                  ┌──────────────────────────┐
                  │    Streamlit Frontend    │
                  │  (User Upload Interface) │
                  └────────────┬─────────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ TensorFlow Model (h5)    │
                  │  - Preprocessing          │
                  │  - Segmentation           │
                  │  - Confidence Estimation  │
                  └────────────┬─────────────┘
                               │
                               ▼
              ┌────────────────────────────────────┐
              │  Post-processing (OpenCV filters)  │
              │  - Morphological operations         │
              │  - Shape & reflection filtering     │
              └────────────────┬────────────────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ SQLite Database Logging  │
                  │ Email Alert System (Opt) │
                  └──────────────────────────┘
```

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/akshatraikar11/INFOSYS-_INTERNSHIP-OIL_SPILL_DETECTION-.git
cd INFOSYS-_INTERNSHIP-OIL_SPILL_DETECTION-
```

### 2️⃣ Install Requirements

Make sure you have **Python 3.8+** installed.
Then install dependencies using:

```bash
pip install -r requirements.txt
```

### 3️⃣ Launch the Streamlit App

```bash
streamlit run streamlit_oil_spill_app.py
```

### 4️⃣ Upload an Image

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
📦 INFOSYS-_INTERNSHIP-OIL_SPILL_DETECTION-
├── Oil_Spill_Detection.ipynb     # Model training & evaluation notebook
├── streamlit_oil_spill_app.py    # Main Streamlit application
├── oil_spill_model.h5            # Trained model weights
├── oil_spill_detections.db       # SQLite database
├── requirements.txt              # Required dependencies
└── README.md                     # Project documentation
```

---


## 🧑‍💻 Developed By

**Akshat Raikar**
*Infosys AI Internship Project*

> "Building AI tools that protect our oceans 🌊"

---

## 🪪 License

This project is licensed under the **MIT License** – feel free to use, modify, and distribute.

-
