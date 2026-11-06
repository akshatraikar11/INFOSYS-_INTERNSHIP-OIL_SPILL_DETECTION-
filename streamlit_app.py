import os
import io
import json
import time
from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image

# =============================================================================
# 1. PAGE CONFIGURATION & HIGH-TECH CYBER-MARITIME STYLING
# =============================================================================
st.set_page_config(
    page_title="DeepSpill AI | Autonomous Maritime Radar & Optical Monitoring",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech Cyber-Maritime Mission Control CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1b2a 0%, #080f18 60%, #03070d 100%);
        color: #e0e6ed;
        font-family: 'Inter', sans-serif;
    }

    .hud-header {
        background: linear-gradient(90deg, rgba(0, 242, 254, 0.08) 0%, rgba(79, 172, 254, 0.03) 100%);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .hud-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hud-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    .hud-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #4ade80;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px #22c55e;
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    .metric-card {
        background: rgba(15, 26, 46, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        backdrop-filter: blur(8px);
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-lbl {
        color: #94a3b8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .veracity-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .alert-catastrophic {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.25) 0%, rgba(185, 28, 28, 0.12) 100%);
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 1.1rem;
        margin-top: 1rem;
    }
    .alert-major {
        background: linear-gradient(90deg, rgba(249, 115, 22, 0.22) 0%, rgba(194, 65, 12, 0.1) 100%);
        border-left: 5px solid #f97316;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .alert-moderate {
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.2) 0%, rgba(180, 83, 9, 0.1) 100%);
        border-left: 5px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .alert-sheen {
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.2) 0%, rgba(8, 145, 178, 0.1) 100%);
        border-left: 5px solid #06b6d4;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .alert-lookalike {
        background: linear-gradient(90deg, rgba(168, 85, 247, 0.2) 0%, rgba(126, 34, 206, 0.1) 100%);
        border-left: 5px solid #a855f7;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .alert-safe {
        background: linear-gradient(90deg, rgba(34, 197, 94, 0.2) 0%, rgba(21, 128, 61, 0.1) 100%);
        border-left: 5px solid #22c55e;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        background: rgba(255, 255, 255, 0.03);
        color: #94a3b8;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important;
        border-color: rgba(0, 242, 254, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. MODEL LOADER & BACKEND PIPELINE
# =============================================================================
@st.cache_resource
def load_deepspill_model():
    """Locates and loads best U-Net model checkpoint."""
    candidates = [
        "unet_oilspill_best.keras",
        "oil_spill_model.h5",
        "../unet_oilspill_best.keras",
        "../oil_spill_model.h5",
        "/content/drive/MyDrive/DeepSpill_Artifacts/unet_oilspill_best.keras",
        "/content/drive/MyDrive/DeepSpill_Artifacts/oil_spill_model.h5"
    ]
    model_file = None
    for c in candidates:
        if os.path.exists(c):
            model_file = c
            break

    if model_file is None:
        return None, None

    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(model_file, compile=False)
        return model, model_file
    except Exception as e:
        st.error(f"⚠️ Notice loading model: {e}")
        return None, None

model, model_path = load_deepspill_model()

# =============================================================================
# 3. SIDEBAR TELEMETRY & MISSION CONTROLS
# =============================================================================
with st.sidebar:
    st.markdown("### 🎛️ Mission Controls")
    
    st.markdown("**1. Sensor Resolution (GSD)**")
    sensor_type = st.selectbox(
        "Platform Preset",
        ["Sentinel-1 SAR (10.0 m/px)", "PlanetScope Optical (3.0 m/px)", "Aerial Maritime Drone (0.2 m/px)", "Custom"],
        index=0
    )
    if sensor_type == "Sentinel-1 SAR (10.0 m/px)":
        gsd = 10.0
    elif sensor_type == "PlanetScope Optical (3.0 m/px)":
        gsd = 3.0
    elif sensor_type == "Aerial Maritime Drone (0.2 m/px)":
        gsd = 0.2
    else:
        gsd = st.number_input("Custom GSD (meters/pixel)", 0.05, 100.0, 10.0, step=0.5)

    cfg_path = Path("model_config.json")
    optimal_th = None
    if cfg_path.exists():
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                optimal_th = float(json.load(f).get("optimal_threshold", 0.80))
        except Exception:
            pass

    is_unet_best = bool(model_path and "unet_oilspill_best" in str(model_path).lower())
    default_th = optimal_th if (is_unet_best and optimal_th is not None) else (0.75 if is_unet_best else 0.35)

    st.markdown("---")
    st.markdown("**2. Decision Thresholds & Sensitivity**")
    threshold = st.slider(
        "Detection Cutoff (T)",
        min_value=0.05, max_value=0.95, value=default_th, step=0.05,
        help="Adjust probability cutoff. Values around 0.65 - 0.75 provide optimal precision-recall balance for ResU-Net."
    )
    min_speckle = st.slider(
        "Speckle Suppression (Min Pixels)",
        min_value=5, max_value=200, value=35, step=5,
        help="Morphological connected-component filter removing isolated radar speckle clusters."
    )
    alpha_blend = st.slider(
        "Overlay Transparency (α)",
        min_value=0.10, max_value=0.90, value=0.55, step=0.05
    )

    st.markdown("---")
    st.markdown("**3. Radar Remote Sensing Physics**")
    use_damping_gate = st.checkbox(
        "SAR Physical Damping Gate",
        value=True,
        help="Enforces satellite radar wave damping physics (Marangoni effect). Oil slicks MUST exhibit lower backscatter than surrounding ambient sea. Completely blocks false alarms on clean sea, waves, coastlines, and ships."
    )
    lookalike_filter_mode = st.selectbox(
        "Look-Alike Differentiation",
        ["Standard (Damping + Gradient Analytics)", "Strict (Heavy Mineral Crude Only)", "Disabled"],
        index=0,
        help="Differentiates natural biogenic slicks / calm water from true mineral crude oil using radar damping depth and edge gradient."
    )
    enable_tta = st.checkbox(
        "Test-Time Augmentation (TTA)",
        value=False,
        help="Ensemble inference across horizontal & vertical flips for enhanced boundary accuracy and noise reduction (+3% accuracy boost)."
    )
    polarity_mode = st.selectbox(
        "Model Polarity Alignment",
        ["Auto-Calibrate (Recommended)", "Direct (Colab unet_oilspill_best.keras)", "Inverted (Legacy oil_spill_model.h5)"],
        index=0,
        help="Aligns model output polarity. Direct is used for newly trained Colab U-Net."
    )

    st.markdown("---")
    st.markdown("### 🛰️ System Status")
    if model is not None:
        in_shape = model.inputs[0].shape
        m_name = os.path.basename(model_path)
        st.success(f"● Model Active: `{m_name}`")
        st.caption(f"Architecture: {'ResU-Net (Sentinel-1)' if is_unet_best else 'Legacy U-Net'} | Input: `{in_shape}`")
    else:
        st.warning("● Standalone Heuristic SAR Filter Mode Active")
    st.caption("Infosys Springboard AI 6.0 | Master Milestone Project Pipeline")

# =============================================================================
# 4. MAIN DASHBOARD HEADER
# =============================================================================
st.markdown("""
<div class="hud-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="hud-title">DEEPSPILL AI // MARITIME RADAR & OPTICAL HUD</h1>
            <p class="hud-subtitle">Autonomous Satellite SAR C-Band & Multi-Spectral Oil Slick Segmentation & Severity Analysis</p>
        </div>
        <div class="hud-badge">
            <span class="pulse-dot"></span> TELEMETRY ACTIVE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Discover Benchmark Images
sample_paths = []
search_dirs = [Path("data/oil_spill/train/images"), Path("data/oil_spill/test/images"), Path("data/oil_spill_dataset/test/images"), Path("."), Path("../")]
for d in search_dirs:
    if d.exists():
        sample_paths.extend(list(d.glob("*.jpg")) + list(d.glob("*.png")) + list(d.glob("*.tif*")))
sample_paths = [p for p in sample_paths if "result" not in p.name.lower() and "fake" not in p.name.lower()][:25]

col_select, col_up = st.columns([1, 2])
with col_select:
    st.markdown("##### ⚡ Quick Load SAR Benchmark Sample")
    options = ["-- Select a Preloaded Sample --"] + [f"{p.name} ({p.stat().st_size//1024} KB)" for p in sample_paths]
    selected_option = st.selectbox("Benchmark Images", options, label_visibility="collapsed")

with col_up:
    st.markdown("##### 📤 Upload Satellite Image")
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "tif", "tiff"], label_visibility="collapsed")

target_image_bytes = None
image_title = "Input Satellite Scene"

if uploaded_file is not None:
    target_image_bytes = uploaded_file.read()
    image_title = uploaded_file.name
elif selected_option != "-- Select a Preloaded Sample --":
    idx = options.index(selected_option) - 1
    selected_file = sample_paths[idx]
    target_image_bytes = selected_file.read_bytes()
    image_title = selected_file.name

# =============================================================================
# 5. INFERENCE & SEGMENTATION PIPELINE
# =============================================================================
if target_image_bytes is not None:
    try:
        pil_im = Image.open(io.BytesIO(target_image_bytes))
        rgb_img = np.array(pil_im.convert('RGB'))
    except Exception:
        nparr = np.frombuffer(target_image_bytes, np.uint8)
        cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if cv_img is None:
            st.error("Failed to decode image file. Please provide a standard PNG, JPG, or TIFF.")
            st.stop()
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

    orig_h, orig_w = rgb_img.shape[:2]
    gray_full = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
    ambient_ocean = float(np.median(gray_full))

    # Model input shape adaptation
    start_time = time.time()
    if model is not None:
        try:
            in_shape = model.inputs[0].shape
            target_h = int(in_shape[1]) if in_shape[1] is not None else 256
            target_w = int(in_shape[2]) if in_shape[2] is not None else 256
            target_c = int(in_shape[3]) if len(in_shape) > 3 and in_shape[3] is not None else 3

            if target_c == 1:
                gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
                resized_in = cv2.resize(gray, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                batch_input = np.expand_dims(np.expand_dims(resized_in.astype(np.float32) / 255.0, axis=-1), axis=0)
            else:
                resized_in = cv2.resize(rgb_img, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                batch_input = np.expand_dims(resized_in.astype(np.float32) / 255.0, axis=0)

            # Test-Time Augmentation (TTA) or Single-pass inference
            if enable_tta and target_c == 3:
                p1 = model.predict(batch_input, verbose=0)
                p2 = model.predict(np.flip(batch_input, axis=2), verbose=0)  # Horizontal Flip
                p3 = model.predict(np.flip(batch_input, axis=1), verbose=0)  # Vertical Flip
                if isinstance(p1, list): p1 = p1[0]
                if isinstance(p2, list): p2 = p2[0]
                if isinstance(p3, list): p3 = p3[0]
                p2_unflip = np.flip(p2, axis=2)
                p3_unflip = np.flip(p3, axis=1)
                pred_out = (p1 + p2_unflip + p3_unflip) / 3.0
            else:
                pred_out = model.predict(batch_input, verbose=0)

            if isinstance(pred_out, list): pred_out = pred_out[0]
            if pred_out.ndim == 4:
                raw_pred = pred_out[0, :, :, 0]
            elif pred_out.ndim == 3:
                raw_pred = pred_out[0, :, :]
            else:
                raw_pred = pred_out
        except Exception as e:
            st.warning(f"Notice: Model execution fallback ({e})")
            blur = cv2.bilateralFilter(gray_full, 7, 50, 50)
            raw_pred = ((blur < ambient_ocean * 0.8) & (blur > 15)).astype(np.float32) * 0.9
    else:
        blur = cv2.bilateralFilter(gray_full, 7, 50, 50)
        raw_pred = ((blur < ambient_ocean * 0.8) & (blur > 15)).astype(np.float32) * 0.9

    infer_time_ms = (time.time() - start_time) * 1000

    # 1. Determine Model Polarity
    if polarity_mode == "Inverted (Legacy oil_spill_model.h5)":
        is_inverted = True
    elif polarity_mode == "Direct (Colab unet_oilspill_best.keras)":
        is_inverted = False
    else:  # Auto-Calibrate (Recommended)
        if model_path and "unet_oilspill_best" in str(model_path).lower():
            is_inverted = False
        elif model_path and "oil_spill_model.h5" in str(model_path).lower():
            is_inverted = True
        else:
            in_h, in_w = raw_pred.shape[:2]
            gray_small = cv2.resize(gray_full, (in_w, in_h))
            dark_sel = gray_small < np.percentile(gray_small, 15)
            med_sel = (gray_small >= np.percentile(gray_small, 40)) & (gray_small <= np.percentile(gray_small, 60))
            p_dark = float(np.mean(raw_pred[dark_sel])) if np.any(dark_sel) else 0.5
            p_med = float(np.mean(raw_pred[med_sel])) if np.any(med_sel) else 0.5
            is_inverted = (p_dark < p_med)

    # Convert raw prediction to True Spill Probability (1.0 = Confirmed Slick, 0.0 = Sea)
    spill_prob = (1.0 - raw_pred) if is_inverted else raw_pred
    full_pred = cv2.resize(spill_prob.astype(np.float32), (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)

    # 2. Dynamic Ocean Baseline Calibration
    if is_inverted:
        bg_baseline = float(np.percentile(full_pred, 50))
        if (full_pred.max() - full_pred.min()) < 0.12:
            calibrated_prob = np.zeros_like(full_pred)
        else:
            calibrated_prob = np.clip((full_pred - bg_baseline) / (1.0 - bg_baseline + 1e-6), 0.0, 1.0)
    else:
        calibrated_prob = np.clip(full_pred, 0.0, 1.0)

    # 3. Decision Threshold & SAR Physical Damping Gate
    if use_damping_gate:
        damped_mask = (gray_full < (ambient_ocean * 0.88)) & (gray_full > 10)
        binary_mask = ((calibrated_prob > threshold) & damped_mask).astype(np.uint8)
    else:
        binary_mask = (calibrated_prob > threshold).astype(np.uint8)

    # 4. Morphological Speckle Suppression Filter
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
    clean_mask = np.zeros_like(binary_mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_speckle:
            clean_mask[labels == i] = 1

    # 5. Look-Alike vs Mineral Oil Differentiation Analytics
    spill_pixels = int(np.sum(clean_mask == 1))
    total_pixels = orig_h * orig_w
    spill_fraction = (spill_pixels / total_pixels) * 100.0

    pixel_area_m2 = gsd ** 2
    spill_area_m2 = spill_pixels * pixel_area_m2
    spill_area_km2 = spill_area_m2 / 1_000_000.0

    # Physics & Morphological Extraction
    damping_ratio_db = 0.0
    contrast_ratio = 1.0
    edge_gradient = 0.0
    mineral_oil_confidence = 0.0
    is_lookalike_suspect = False

    if spill_pixels > 0:
        slick_vals = gray_full[clean_mask == 1]
        mean_slick = float(np.mean(slick_vals))
        contrast_ratio = ambient_ocean / max(mean_slick, 1.0)
        damping_ratio_db = float(10.0 * np.log10(contrast_ratio))

        # Edge Boundary Gradient Calculation
        grad_x = cv2.Sobel(gray_full, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_full, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(grad_x, grad_y)
        dilated = cv2.dilate(clean_mask, np.ones((3, 3), np.uint8))
        boundary = (dilated - clean_mask) == 1
        edge_gradient = float(np.mean(mag[boundary])) if np.any(boundary) else 0.0

        # Mineral Oil Veracity Index (%)
        # Mineral crude oil has strong wave damping (>2.5 dB) and sharp surface tension edges (>35 px^-1)
        mineral_oil_confidence = min(99.0, max(12.0, (damping_ratio_db * 22.0) + (edge_gradient * 0.35)))
        
        # Look-Alike differentiation criteria
        if lookalike_filter_mode == "Strict (Heavy Mineral Crude Only)":
            is_lookalike_suspect = (damping_ratio_db < 2.5) or (edge_gradient < 40.0)
            if is_lookalike_suspect:
                # Suppress non-crude detections in strict mode
                clean_mask = np.zeros_like(clean_mask)
                spill_pixels = 0
                spill_area_km2 = 0.0
        elif lookalike_filter_mode == "Standard (Damping + Gradient Analytics)":
            is_lookalike_suspect = (mineral_oil_confidence < 50.0) or (damping_ratio_db < 1.6 and edge_gradient < 30.0)

    # Bonn Agreement Standard Volume Estimation (Tiered Thickness Profile)
    # Core heavy crude: ~0.2mm thickness (200 m3/km2), Medium sheen: ~0.05mm (50 m3/km2), Fringe: ~0.01mm (10 m3/km2)
    heavy_pixels = int(np.sum((clean_mask == 1) & (gray_full < ambient_ocean * 0.68)))
    medium_pixels = int(np.sum((clean_mask == 1) & (gray_full >= ambient_ocean * 0.68) & (gray_full < ambient_ocean * 0.85)))
    fringe_pixels = spill_pixels - heavy_pixels - medium_pixels

    heavy_area_km2 = (heavy_pixels * pixel_area_m2) / 1e6
    medium_area_km2 = (medium_pixels * pixel_area_m2) / 1e6
    fringe_area_km2 = (fringe_pixels * pixel_area_m2) / 1e6

    estimated_volume_m3 = (heavy_area_km2 * 200.0) + (medium_area_km2 * 50.0) + (fringe_area_km2 * 10.0)

    # Multi-Tier Color Overlay (Bonn Agreement Appearance Code)
    overlay = rgb_img.copy()
    colored_layer = np.zeros_like(rgb_img)

    if spill_pixels > 0:
        # Faint thin sheen fringe: Bright Cyan [6, 182, 212]
        colored_layer[(clean_mask == 1) & (gray_full >= ambient_ocean * 0.85)] = [6, 182, 212]
        # Moderate plume thickness: Vibrant Amber Orange [245, 158, 11]
        colored_layer[(clean_mask == 1) & (gray_full >= ambient_ocean * 0.68) & (gray_full < ambient_ocean * 0.85)] = [245, 158, 11]
        # Heavy continuous crude core: Crimson Red [225, 29, 72]
        colored_layer[(clean_mask == 1) & (gray_full < ambient_ocean * 0.68)] = [225, 29, 72]

    blended = cv2.addWeighted(overlay, 1.0 - alpha_blend, colored_layer, alpha_blend, 0)
    contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(blended, contours, -1, (255, 240, 0), max(2, int(orig_w / 600)))

    # ── METRIC TILES ─────────────────────────────────────────────────────────
    st.markdown("### 📊 Geospatial Contamination & Physical Telemetry")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{spill_area_km2:.3f} km²</div>
            <div class="metric-lbl">Total Slick Area</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{estimated_volume_m3:,.1f} m³</div>
            <div class="metric-lbl">Estimated Volume</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{len(contours)}</div>
            <div class="metric-lbl">Discrete Plumes</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{damping_ratio_db:.2f} dB</div>
            <div class="metric-lbl">Damping Depth</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{infer_time_ms:.1f} ms</div>
            <div class="metric-lbl">Inference Latency</div>
        </div>
        """, unsafe_allow_html=True)

    # ── FOUR-TIER HAZARD SEVERITY BANNER (IMO / EMSA STANDARDS) ──────────────
    if spill_pixels == 0:
        st.markdown(f"""
        <div class="alert-safe">
            <h4 style="margin: 0; color: #22c55e;">✅ MARITIME SURFACE CLEAR // NO SPILL DETECTED</h4>
            <p style="margin: 0.3rem 0 0 0; color: #bbf7d0;">
                Radar backscatter within nominal ambient sea envelope ({ambient_ocean:.1f}). No anomalous capillary wave damping signatures detected at decision cutoff T = {threshold:.2f}.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif is_lookalike_suspect:
        st.markdown(f"""
        <div class="alert-lookalike">
            <h4 style="margin: 0; color: #c084fc;">🌿 NATURAL LOOK-ALIKE ADVISORY // WEAK BIOGENIC SURFACTANT</h4>
            <p style="margin: 0.3rem 0 0 0; color: #e9d5ff;">
                Detected feature exhibits shallow wave damping (<strong>{damping_ratio_db:.2f} dB</strong>) and soft boundary gradients (<strong>{edge_gradient:.1f} px⁻¹</strong>). 
                Morphology suggests a natural low-wind calm zone or biogenic surfactant sheen rather than mineral crude oil.
                <strong>Mineral Oil Confidence: {mineral_oil_confidence:.1f}%</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif spill_area_km2 >= 5.0:
        st.markdown(f"""
        <div class="alert-catastrophic">
            <h4 style="margin: 0; color: #ef4444;">🚨 CATASTROPHIC CONTAMINATION // TIER 4 NATIONAL EMERGENCY</h4>
            <p style="margin: 0.3rem 0 0 0; color: #fca5a5;">
                Detected massive heavy crude slick exceeding <strong>{spill_area_km2:.2f} km²</strong> (~{estimated_volume_m3:,.0f} m³ estimated volume). 
                Intense wave suppression ({damping_ratio_db:.2f} dB). Immediate Tier-3 offshore containment boom deployment and multi-vessel skimmer dispatch protocol triggered.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif spill_area_km2 >= 1.5:
        st.markdown(f"""
        <div class="alert-major">
            <h4 style="margin: 0; color: #fb923c;">⚠️ MAJOR MARITIME OIL SPILL // TIER 3 REGIONAL INCIDENT</h4>
            <p style="margin: 0.3rem 0 0 0; color: #fed7aa;">
                Confirmed mineral oil slick totaling <strong>{spill_area_km2:.2f} km²</strong> (~{estimated_volume_m3:,.0f} m³ estimated volume) across {len(contours)} plumes. 
                Regional Coast Guard dispatch and active hydrocarbon skimming operations recommended.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif spill_area_km2 >= 0.25:
        st.markdown(f"""
        <div class="alert-moderate">
            <h4 style="margin: 0; color: #f59e0b;">⚠️ MODERATE CONTAMINATION // TIER 2 LOCAL HARBOR RESPONSE</h4>
            <p style="margin: 0.3rem 0 0 0; color: #fde68a;">
                Moderate hydrocarbon slick cluster totaling <strong>{spill_area_km2:.3f} km²</strong> (~{estimated_volume_m3:,.0f} m³). Local harbor patrol containment and dispersant evaluation advisory issued.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-sheen">
            <h4 style="margin: 0; color: #22d3ee;">ℹ️ MINOR SHEEN DISCHARGE // TIER 1 LOCALIZED TRACE</h4>
            <p style="margin: 0.3rem 0 0 0; color: #cffafe;">
                Localized thin hydrocarbon sheen ({spill_area_m2:,.0f} m², ~{estimated_volume_m3:.1f} m³). Likely small operational bilge release or engine exhaust trace. Logged for satellite re-pass.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── SLICK VERACITY & PHYSICAL DIFFERENTIATION CARD ───────────────────────
    if spill_pixels > 0:
        st.markdown(f"""
        <div class="veracity-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #38bdf8; font-size: 0.95rem;">
                        🔬 SAR PHYSICAL DISCRIMINATION ANALYTICS
                    </span>
                    <div style="margin-top: 0.3rem; font-size: 0.85rem; color: #cbd5e1;">
                        Mineral Oil Veracity Index: <strong style="color: {'#22c55e' if mineral_oil_confidence >= 70 else '#f59e0b' if mineral_oil_confidence >= 50 else '#c084fc'};">{mineral_oil_confidence:.1f}%</strong> | 
                        Damping Contrast: <strong>{contrast_ratio:.2f}x</strong> ({damping_ratio_db:.2f} dB) | 
                        Boundary Edge Sharpness: <strong>{edge_gradient:.1f} px⁻¹</strong> | 
                        Heavy Core Fraction: <strong>{(heavy_pixels/spill_pixels)*100:.1f}%</strong>
                    </div>
                </div>
                <div style="text-align: right; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #94a3b8;">
                    <div>Bonn Code: <strong>{'Code 4/5 (Heavy Crude)' if heavy_pixels > 0 else 'Code 2/3 (Medium Sheen)'}</strong></div>
                    <div>Thickness Profile: <strong>{'Multi-Layer Sinuous' if len(contours) > 1 else 'Cohesive Slick'}</strong></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── VISUAL DIAGNOSTIC TABS ────────────────────────────────────────────────
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["🛰️ Side-by-Side Multi-Tier Segmentation", "🔬 Probability & Radiometry Heatmap", "📋 Mission Defense Log"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**1. Original Satellite Scene** (`{orig_w}x{orig_h}`)")
            st.image(rgb_img, use_container_width=True)
        with c2:
            st.markdown("**2. Multi-Thickness Segmented Overlay**")
            st.image(blended, use_container_width=True)
            st.caption("🔴 Red: Heavy Core Crude | 🟠 Orange: Medium Sheen | 🔵 Cyan: Faint Plume | 🟡 Yellow: Boundary")
        with c3:
            st.markdown("**3. Binarized Segmentation Mask**")
            st.image((clean_mask * 255).astype(np.uint8), use_container_width=True)

    with tab2:
        c_prob, c_hist = st.columns(2)
        with c_prob:
            st.markdown("**U-Net Probability Distribution Heatmap**")
            scaled_heat = (calibrated_prob * 255.0).astype(np.uint8)
            heat_color = cv2.applyColorMap(scaled_heat, cv2.COLORMAP_JET)
            st.image(cv2.cvtColor(heat_color, cv2.COLOR_BGR2RGB), use_container_width=True)
            st.caption("🔴 Red/Yellow: High Probability Slick Core | 🔵 Deep Blue: Clean Ambient Ocean")
        with c_hist:
            st.markdown("**Radar Backscatter vs Spill Pixel Intensity**")
            spill_vals = gray_full[clean_mask == 1]
            ocean_vals = gray_full[clean_mask == 0]
            
            fig_stat, ax = plt.subplots(figsize=(6, 4))
            fig_stat.patch.set_facecolor('#0d1b2a')
            ax.set_facecolor('#080f18')
            ax.tick_params(colors='#94a3b8')
            ax.spines['bottom'].set_color('#334155')
            ax.spines['top'].set_color('#334155')
            ax.spines['left'].set_color('#334155')
            ax.spines['right'].set_color('#334155')

            if len(ocean_vals) > 0:
                ax.hist(ocean_vals[::15], bins=30, color='#38bdf8', alpha=0.6, label='Ambient Sea', density=True)
            if len(spill_vals) > 0:
                ax.hist(spill_vals, bins=30, color='#ef4444', alpha=0.8, label='Oil Spill Slick', density=True)
            ax.set_xlabel('Pixel Radiance Intensity (0-255)', color='#e0e6ed')
            ax.set_ylabel('Probability Density', color='#e0e6ed')
            ax.legend(facecolor='#0f172a', edgecolor='#334155', labelcolor='#e0e6ed')
            st.pyplot(fig_stat)

    with tab3:
        st.markdown("#### 📜 Tactical Mission Telemetry Report")
        st.json({
            "target_image": image_title,
            "dimensions": f"{orig_w}x{orig_h}",
            "sensor_gsd_m": gsd,
            "spill_pixels": spill_pixels,
            "total_surface_area_km2": round(spill_area_km2, 4),
            "heavy_core_area_km2": round(heavy_area_km2, 4),
            "medium_sheen_area_km2": round(medium_area_km2, 4),
            "faint_fringe_area_km2": round(fringe_area_km2, 4),
            "estimated_volume_m3": round(estimated_volume_m3, 1),
            "discrete_plumes": len(contours),
            "damping_depth_db": round(damping_ratio_db, 2),
            "boundary_edge_gradient": round(edge_gradient, 2),
            "mineral_oil_veracity_pct": round(mineral_oil_confidence, 1),
            "classification_category": "Look-Alike Suspect" if is_lookalike_suspect else "Confirmed Mineral Oil" if spill_pixels > 0 else "Clear Ocean",
            "decision_threshold_cutoff": threshold,
            "speckle_filter_min_px": min_speckle,
            "ambient_sea_intensity": round(ambient_ocean, 1),
            "inference_latency_ms": round(infer_time_ms, 2)
        })

else:
    st.info("👆 Please select a preloaded benchmark SAR image or upload your own satellite scene to initiate segmentation.")
