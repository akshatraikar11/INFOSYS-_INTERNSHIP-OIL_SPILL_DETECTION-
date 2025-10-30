# Oil Spill Detection App - Enhanced UI
import streamlit as st
from PIL import Image
import numpy as np
import os, io, json, glob, uuid
from datetime import datetime
import requests
import tensorflow as tf
from tensorflow.keras.models import load_model
import sqlite3
import pandas as pd
# Using native Streamlit components for visualization as plt
# Removed plotly dependency
from streamlit_autorefresh import st_autorefresh
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# ------------------ CONFIG ------------------
MODEL_PATH = "oil_spill_model.h5"
DEFAULT_INPUT_SIZE = (128, 128)
DB_PATH = "oil_spill_detections.db"
ALERT_THRESHOLD = 0.3  # Threshold for sending alerts
ENABLE_EMAIL_ALERTS = False  # Set to True to enable email alerts
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",  # Replace with your email
    "sender_password": "",  # Replace with your app password
    "recipient_emails": ["recipient@example.com"]  # Replace with recipient emails
}

# Auto-refresh every 5 minutes (300000 milliseconds) for monitoring
refresh_interval = 300000  # 5 minutes
if 'monitor_mode' in st.session_state and st.session_state.monitor_mode:
    st_autorefresh(interval=refresh_interval, key="datarefresh")

# ------------------ DATABASE SETUP ------------------
def init_db():
    # Using URI mode with write-binary mode enabled
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=rwc", uri=True)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        filename TEXT,
        confidence REAL,
        oil_pixel_ratio_high REAL,
        oil_pixel_ratio_medium REAL,
        oil_pixel_ratio_low REAL,
        severity TEXT,
        location TEXT,
        notes TEXT,
        image_path TEXT,
        result_path TEXT,
        is_alerted INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    return conn

def save_detection_to_db(detection_data):
    conn = init_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO detections (
        id, timestamp, filename, confidence, 
        oil_pixel_ratio_high, oil_pixel_ratio_medium, oil_pixel_ratio_low,
        severity, location, notes, image_path, result_path, is_alerted
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        detection_data["id"],
        detection_data["timestamp"],
        detection_data["filename"],
        detection_data["confidence"],
        detection_data["oil_pixel_ratio_high"],
        detection_data["oil_pixel_ratio_medium"],
        detection_data["oil_pixel_ratio_low"],
        detection_data["severity"],
        detection_data["location"],
        detection_data["notes"],
        detection_data["image_path"],
        detection_data["result_path"],
        detection_data["is_alerted"]
    ))
    conn.commit()
    conn.close()

def get_all_detections():
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM detections ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_detection_by_id(detection_id):
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM detections WHERE id = ?", conn, params=(detection_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None

# Initialize database on startup
init_db()

# Page configuration with enhanced settings
st.set_page_config(
    page_title="Oil Spill Detection AI",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(""" 
 <style> 
 body { 
     background-color: #f8fafc; 
 } 
  .main-header { 
      text-align: center; 
      padding: 5rem 1rem 4rem; 
      background: linear-gradient(135deg, #1f4e79 0%, #2d5a87 100%);
      margin-bottom: 2rem;
      border-radius: 20px; 
      border: 1px solid rgba(255, 255, 255, 0.12); 
      box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
  } 
 .main-header h1 { 
     font-size: 3.5rem; 
     margin-bottom: 0.5rem; 
     font-weight: 800; 
     letter-spacing: 0.5px; 
 } 
 .main-header p { 
     font-size: 1.5rem; 
     opacity: 0.9; 
 } 
 
 
 
 .upload-section { 
     background: white; 
     padding: 2.2rem; 
     border-radius: 14px; 
     box-shadow: 0 6px 20px rgba(0,0,0,0.05); 
     margin-top: 1rem; 
 } 
 
 .result-section { 
     background: #f8f9fa; 
     padding: 1.8rem; 
     border-radius: 14px; 
     margin: 2.5rem 0; 
     border: 1px solid #e3f2fd;
 } 
 
 .stButton>button { 
     background: linear-gradient(90deg, #42a5f5, #64b5f6); 
     color: #1a237e; 
     border-radius: 6px; 
     border: none; 
     padding: 0.6rem 1.4rem; 
     font-weight: 600; 
 } 
  .stButton>button:hover { 
      background: linear-gradient(90deg, #2196f3, #42a5f5); 
  } 
  
  hr { 
      margin-top: 3rem; 
  }
  /* Consistent spacing between major sections */
  .settings-section { margin: 2rem 0; }
  .hero-wrap { margin: 2rem 0; }
    .hero-grid { display: grid; grid-template-columns: 1.15fr .85fr; gap: 1.5rem; align-items: center; }
    .hero-title { font-size: 2.2rem; line-height: 1.15; margin: 0 0 .5rem 0; letter-spacing: .2px; }
    .hero-sub { color: #cde4ff; margin: 0 0 1rem 0; }
    .badge-row { display: flex; flex-wrap: wrap; gap: .5rem; margin: .75rem 0 0 0; }
    .pill-badge { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.14); color: #dff1ff; padding: .35rem .6rem; border-radius: 999px; font-size: .85rem; }
    .glass-card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: .9rem; color: #e9f3ff; box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02); }
    .mini-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: .75rem; }
    .accent { color: #7dd3ff; }
    .upload-shell { position: relative; border-radius: 14px; padding: .75rem; background:
        radial-gradient(150px 60px at 10% 0%, rgba(125,211,255,.25), transparent 60%),
        radial-gradient(200px 80px at 90% 0%, rgba(34,197,94,.18), transparent 60%);
    }
    .upload-glow { border-radius: 12px; padding: 1.25rem; background: linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.08)); border: 1px solid rgba(255,255,255,0.18);
        box-shadow: 0 10px 30px rgba(0,0,0,0.35), 0 0 0 4px rgba(125,211,255,0.05);
    }
    .stepper { display:flex; gap: .75rem; align-items:center; flex-wrap: wrap; }
    .step { display:flex; align-items:center; gap:.5rem; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 999px; padding: .4rem .7rem; color:#e6f4ff; font-size: .9rem; }
    .step .num { background:#1f4e79; color:#fff; width: 22px; height:22px; display:inline-flex; align-items:center; justify-content:center; border-radius:999px; font-weight:700; font-size:.8rem; }
    .callout { background: #0f2a40; border-left: 3px solid #57b7ff; color:#cfeaff; padding: .75rem .9rem; border-radius: 8px; }
    /* Streamlit core widgets polish */
    .stFileUploader > div[data-baseweb="file-uploader"] { border-radius: 10px; border: 1px dashed rgba(255,255,255,0.25); background: rgba(255,255,255,0.04); }
    .stFileUploader label { color: #e1f0ff !important; font-weight: 600; }
    .st-emotion-cache-1jicfl2, .st-emotion-cache-1jicfl2 p { color: #cfeaff !important; }
    @media (max-width: 900px){ .hero-grid{ grid-template-columns: 1fr; } }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f4e79;
    }
    .result-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    .upload-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5a87 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #2d5a87 0%, #1f4e79 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ------------------ UTILITIES ------------------
@st.cache_resource(show_spinner=False)
def load_inference_model(path=MODEL_PATH):
    try:
        model = load_model(path, compile=False)
        return model
    except Exception as e:
        st.error(f"Failed to load model from {path}: {e}")
        return None

# Load the model at startup
model = load_inference_model()

def preprocess_image(pil_img, target_size, channels=1):
    if channels == 1:
        img = pil_img.convert("L")
        arr = np.array(img.resize(target_size, Image.LANCZOS), dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, axis=-1)
    elif channels == 2:
        # Convert to grayscale and duplicate to create 2-channel input
        img = pil_img.convert("L")
        arr = np.array(img.resize(target_size, Image.LANCZOS), dtype=np.float32) / 255.0
        arr = np.stack([arr, arr], axis=-1)  # Duplicate to create 2 channels
    else:
        img = pil_img.convert("RGB")
        arr = np.array(img.resize(target_size, Image.LANCZOS), dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

def clean_mask(mask, min_area=100):
    try:
        import cv2
        mask_uint8 = (mask * 255).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        mask_cleaned = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_cleaned, 8)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] < min_area:
                mask_cleaned[labels == i] = 0
        return mask_cleaned.astype(np.float32)/255.0
    except ImportError:
        return mask

def postprocess_prediction(pred, original_size):
    if isinstance(pred, list):
        pred = pred[0]
    mask = np.array(pred)
    if mask.ndim == 4: mask = mask[0]
    if mask.ndim == 3 and mask.shape[2] in (1,3): mask = mask[:,:,0]
    # sigmoid if logits
    if mask.min() < -1 or mask.max() > 1:
        mask = 1 / (1 + np.exp(-mask))
    # normalize
    mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)
    
    # Improved detection with false positive reduction
    mask_enhanced = np.copy(mask)
    
    # Apply shape and texture analysis to reduce false positives
    try:
        import cv2
        
        # Convert to uint8 for OpenCV operations
        mask_uint8 = (mask_enhanced * 255).astype(np.uint8)
        
        # Apply morphological operations to clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_cleaned = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel)
        
        # Find contours to analyze shape characteristics
        contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter out small, irregular shapes that are likely false positives
        filtered_mask = np.zeros_like(mask_cleaned)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:  # Minimum area threshold
                # Check aspect ratio to filter out linear reflections
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = max(w, h) / max(min(w, h), 1)
                if aspect_ratio < 10:  # Filter out very elongated shapes (likely reflections)
                    # Check circularity to prefer blob-like shapes
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > 0.1:  # Prefer more circular shapes
                            cv2.fillPoly(filtered_mask, [contour], 255)
        
        mask_cleaned = filtered_mask.astype(np.float32) / 255.0
        
    except ImportError:
        # Fallback if OpenCV not available
        mask_cleaned = clean_mask(mask_enhanced, min_area=200)
    
    # More conservative confidence calculation
    oil_pixel_ratio_05 = float((mask_cleaned > 0.5).mean())
    oil_pixel_ratio_03 = float((mask_cleaned > 0.3).mean())
    oil_pixel_ratio_01 = float((mask_cleaned > 0.1).mean())
    oil_pixel_ratio_005 = float((mask_cleaned > 0.05).mean())
    
    # Use more conservative confidence (only high confidence areas)
    confidence = oil_pixel_ratio_03  # Use medium confidence as primary indicator
    
    mask_img = Image.fromarray((mask_cleaned*255).astype(np.uint8)).resize(original_size, Image.LANCZOS)
    return {
        "type":"mask",
        "mask_image": mask_img,
        "oil_pixel_ratio_05": oil_pixel_ratio_05,
        "oil_pixel_ratio_03": oil_pixel_ratio_03,
        "oil_pixel_ratio_01": oil_pixel_ratio_01,
        "oil_pixel_ratio_005": oil_pixel_ratio_005,
        "confidence": confidence
    }

def create_enhanced_overlay(image_pil, mask_pil, alpha=0.6):
    mask_arr = np.array(mask_pil.convert("L"))
    overlay_arr = np.zeros((image_pil.size[1], image_pil.size[0],4), dtype=np.uint8)
    
    # More conservative overlay with better color coding
    high_mask = mask_arr > 200
    overlay_arr[high_mask, 0] = 255; overlay_arr[high_mask, 3] = int(255*alpha)  # Red for high confidence
    
    medium_mask = (mask_arr>150) & (mask_arr<=200)
    overlay_arr[medium_mask,0] = 255; overlay_arr[medium_mask,1] = 165; overlay_arr[medium_mask,3] = int(255*alpha*0.8)  # Orange for medium confidence
    
    low_mask = (mask_arr>100) & (mask_arr<=150)
    overlay_arr[low_mask,1] = 255; overlay_arr[low_mask,3] = int(255*alpha*0.5)  # Yellow for low confidence
    
    # Very low confidence areas in blue (likely false positives)
    very_low_mask = (mask_arr>50) & (mask_arr<=100)
    overlay_arr[very_low_mask,2] = 255; overlay_arr[very_low_mask,3] = int(255*alpha*0.3)  # Blue for very low confidence
    
    overlay = Image.fromarray(overlay_arr,"RGBA")
    return Image.alpha_composite(image_pil.convert("RGBA"), overlay)

def interpret_result(result, threshold=0.05):
    if result["type"]=="mask":
        confidence = result.get("oil_pixel_ratio_03",0)
        if confidence >= threshold:
            return f"Oil Spill (confidence: {confidence:.3f})"
        else:
            return f"No Oil Spill (confidence: {confidence:.3f})"
    return "Unknown"

def save_file_bytes(folder, filename, bytes_data):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path,"wb") as f: f.write(bytes_data)
    return path

# ------------------ ALERT SYSTEM ------------------
def determine_severity(confidence):
    if confidence >= 0.5:
        return "Critical"
    elif confidence >= 0.3:
        return "High"
    elif confidence >= 0.1:
        return "Medium"
    else:
        return "Low"

def send_email_alert(detection_data, image_path, result_path):
    if not ENABLE_EMAIL_ALERTS:
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['Subject'] = f'🚨 ALERT: Oil Spill Detected - {detection_data["severity"]} Severity'
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = ", ".join(EMAIL_CONFIG["recipient_emails"])
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>🚨 Oil Spill Detection Alert</h2>
            <p><b>Detection ID:</b> {detection_data['id']}</p>
            <p><b>Timestamp:</b> {detection_data['timestamp']}</p>
            <p><b>Confidence:</b> {detection_data['confidence']:.3f}</p>
            <p><b>Severity:</b> {detection_data['severity']}</p>
            <p><b>Location:</b> {detection_data['location'] or 'Unknown'}</p>
            <p><b>Notes:</b> {detection_data['notes'] or 'None'}</p>
            <p>Please check the attached images for details.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Attach original image
        with open(image_path, 'rb') as f:
            img_data = f.read()
            img_attach = MIMEImage(img_data, name=os.path.basename(image_path))
            msg.attach(img_attach)
        
        # Attach result image
        with open(result_path, 'rb') as f:
            img_data = f.read()
            img_attach = MIMEImage(img_data, name=os.path.basename(result_path))
            msg.attach(img_attach)
        
        # Send email
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Failed to send email alert: {e}")
        return False

# ------------------ UI ------------------
# ------------------ HEADER (Gradient Hero Section) ------------------ 
st.markdown(""" 
<div class="main-header"> 
    <h1>🌊 DeepSpill</h1> 
    <p>AI Powered Oil Spill Detection System using Deep Learning</p> 
</div> 
""", unsafe_allow_html=True) 

# ------------------ INFO SECTION (White Cards with 4 cards) ------------------ 
st.markdown("""

<style>
 .info-grid {
   display: grid;
   grid-template-columns: repeat(2, 1fr);
   gap: 2rem;
   justify-items: center;
   margin-top: 2rem;
   margin-bottom: 2rem;
 }

@media (max-width: 900px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}

.info-card {
  background: radial-gradient(circle at top left, rgba(0,150,255,0.1), rgba(17,20,28,0.95));
  border-radius: 22px;
  border: 1px solid rgba(0, 150, 255, 0.25);
  box-shadow: 0 0 20px rgba(0, 150, 255, 0.25);
  padding: 1.8rem 1.5rem;
  color: #e0e0e0;
  width: 420px;
  transition: 0.3s ease;
}

.info-card:hover {
  box-shadow: 0 0 35px rgba(0, 150, 255, 0.45);
  transform: translateY(-4px);
}

.info-card h3 {
  color: #1f76ff;
  font-size: 1.4rem;
  margin-bottom: 0.7rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-card p {
  font-size: 1rem;
  line-height: 1.6;
  color: #cfd8dc;
}
</style>

<div class="info-grid">

  <div class="info-card">
    <h3>🌍 What is an Oil Spill?</h3>
    <p>Oil spills occur when petroleum is accidentally released into oceans or coastal waters, causing severe environmental and economic harm.</p>
  </div>

  <div class="info-card">
    <h3>🚀 Why Early Detection Matters</h3>
    <p>Timely detection allows authorities to respond faster, reducing marine pollution and protecting aquatic life and coastal ecosystems.</p>
  </div>

  <div class="info-card">
    <h3>🤖 How AI Helps</h3>
    <p>Deep learning models analyze satellite or aerial images to automatically identify oil spills, minimizing human error and enabling 24/7 monitoring.</p>
  </div>

  <div class="info-card">
    <h3>🌱 Environmental Impact</h3>
    <p>Oil spills can devastate marine habitats, suffocate coral reefs, and harm wildlife. Early detection and cleanup reduce long-term ecological damage.</p>
  </div>

</div>
""", unsafe_allow_html=True)


# Settings moved to main area
st.markdown('<div class="settings-section">', unsafe_allow_html=True)
st.markdown("## ⚙️ Settings")

# Create columns for settings
col1, col2 = st.columns(2)

with col1:
    # Model information
    st.markdown("### 📊 Model Information")
    st.info(f"**Model:** {MODEL_PATH}")
    
    # Settings
    st.markdown("### 🔧 Detection Settings")
    prob_threshold = st.slider(
        "Confidence Threshold", 
        0.0, 1.0, 0.1, 0.001,
        help="Higher values = more conservative detection (recommended: 0.1-0.3 to avoid false positives from water reflections)"
    )

with col2:
    st.markdown("### 💾 Save Options")
    save_uploads = st.checkbox("Save uploaded images", True, help="Save uploaded images to local storage")
    save_results = st.checkbox("Save results", True, help="Save detection results and masks")
    
    st.markdown("### ℹ️ About")
    st.markdown("""
    This AI model uses deep learning to detect oil spills in satellite and aerial imagery. 
    Upload an image to get started with detection.
    """)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Main content area - Detection only

# Unique hero section before upload
st.markdown(
    """
    <div class="hero-wrap">
      <div class="hero-grid">
        <div>
          <div class="pill-badge">Real‑time AI · Remote Sensing · False‑positive reduction</div>
          <h2 class="hero-title">Detect oil spills with <span class="accent">clarity</span> and <span class="accent">confidence</span>.</h2>
          <p class="hero-sub">Purpose‑built semantic segmentation and conservative post‑processing help distinguish reflective water and wake patterns from true spills.</p>
          <div class="mini-grid" style="margin-top:.75rem;">
            <div class="glass-card">🔒 Conservative thresholds reduce glare/reflection noise</div>
            <div class="glass-card">🌊 Multi‑band friendly pre‑processing</div>
            <div class="glass-card">📈 Confidence tiers with quick metrics</div>
            <div class="glass-card">🗂️ Auto save to history</div>
          </div>
        </div>
        <div class="upload-shell">
          <div class="upload-glow">
            <div class="stepper" style="margin-bottom:.75rem;">
              <div class="step"><span class="num">1</span> Choose your image</div>
              <div class="step"><span class="num">2</span> Run detection</div>
              <div class="step"><span class="num">3</span> Review overlay</div>
            </div>
            <div class="callout">Tip: satellite or aerial imagery works best; JPG/PNG/TIF are supported.</div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# File uploader with enhanced styling
st.markdown("### 📤 Upload Image")
uploaded = st.file_uploader(
    "Choose an image file", 
    type=["jpg","jpeg","png","tif"],
    help="Upload satellite or aerial imagery for oil spill detection"
)

# Metadata section removed

# All monitoring and history functionality removed

# Load model
model = load_inference_model()
if uploaded and model:
    # Processing indicator
    with st.spinner("🔄 Processing image and running AI detection..."):
        file_bytes = uploaded.read()
        img = Image.open(io.BytesIO(file_bytes))
        orig_size = img.size
        if save_uploads: save_file_bytes("./uploads", uploaded.name, file_bytes)
        
        # preprocess with better error handling
        try:
            input_shape = tuple(model.inputs[0].shape)
            channels = int(input_shape[3]) if len(input_shape)>3 and input_shape[3] else 1
            target_size = (int(input_shape[1]), int(input_shape[2])) if input_shape[1] and input_shape[2] else DEFAULT_INPUT_SIZE
            
            st.info(f"Model expects input shape: {input_shape} (channels: {channels})")
            
            x = preprocess_image(img, target_size, channels)
            st.info(f"Preprocessed image shape: {x.shape}")
            
            preds = model.predict(x)
        except Exception as e:
            st.error(f"Model prediction failed: {e}")
            st.warning("Trying fallback preprocessing methods...")
            
            # Try different channel configurations
            fallback_success = False
            for fallback_channels in [1, 2, 3]:
                try:
                    st.info(f"Trying {fallback_channels} channel(s)...")
                    x = preprocess_image(img, DEFAULT_INPUT_SIZE, fallback_channels)
                    preds = model.predict(x)
                    st.success(f"Success with {fallback_channels} channel(s)!")
                    fallback_success = True
                    break
                except Exception as fallback_e:
                    st.warning(f"Failed with {fallback_channels} channel(s): {fallback_e}")
                    continue
            
            if not fallback_success:
                st.error("All preprocessing methods failed. The model may be incompatible.")
                st.stop()
        result = postprocess_prediction(preds, orig_size)
    
    # Results section with enhanced styling
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    
    # Final prediction with enhanced display
    final_verdict = interpret_result(result, threshold=prob_threshold)
    confidence = result.get("oil_pixel_ratio_03", 0)
    
    # Prediction result with color coding
    if confidence >= prob_threshold:
        st.markdown("### 🚨 **Oil Spill Detected**")
        st.error(f"**Confidence:** {confidence:.3f} | **Status:** Oil spill detected in the image")
    else:
        st.markdown("### ✅ **No Oil Spill Detected**")
        st.success(f"**Confidence:** {confidence:.3f} | **Status:** No oil spill detected in the image")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📸 Original Image")
        st.image(img, caption="Uploaded Image", use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Detection Mask")
        st.image(result["mask_image"], caption="AI-Generated Detection Mask", use_container_width=True)
    
    # Overlay visualization with explanation
    st.markdown("### 🔍 Overlay Visualization")
    overlay = create_enhanced_overlay(img, result["mask_image"])
    st.image(overlay, caption="Original Image with Oil Spill Detection Overlay", use_container_width=True)
    
    # Quick actions: download overlay and mask
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        _ov_buf = io.BytesIO()
        overlay.convert("RGB").save(_ov_buf, format="JPEG", quality=95)
        st.download_button(
            label="⬇️ Download Overlay (JPG)",
            data=_ov_buf.getvalue(),
            file_name="oil_spill_overlay.jpg",
            mime="image/jpeg",
            help="Save the overlay visualization as a high-quality JPG"
        )
    with col_dl2:
        _mask_buf = io.BytesIO()
        result["mask_image"].save(_mask_buf, format="PNG")
        st.download_button(
            label="⬇️ Download Mask (PNG)",
            data=_mask_buf.getvalue(),
            file_name="oil_spill_mask.png",
            mime="image/png",
            help="Download the raw detection mask as a PNG"
        )
    
    # Detailed metrics with enhanced detection
    st.markdown("### 📊 Detection Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "High Confidence", 
            f"{result['oil_pixel_ratio_05']:.3f}",
            help="Areas with >50% confidence of oil spill"
        )
    
    with col2:
        st.metric(
            "Medium Confidence", 
            f"{result['oil_pixel_ratio_03']:.3f}",
            help="Areas with >30% confidence of oil spill"
        )
    
    with col3:
        st.metric(
            "Low Confidence", 
            f"{result['oil_pixel_ratio_01']:.3f}",
            help="Areas with >10% confidence of oil spill"
        )
    
    with col4:
        st.metric(
            "Ultra-Sensitive", 
            f"{result['oil_pixel_ratio_005']:.3f}",
            help="Areas with >5% confidence (catches dark oil spills)"
        )
    
    # Enhanced detection explanation
    st.markdown("### 🔍 Detection Analysis")
    if result['oil_pixel_ratio_005'] > 0.01:
        st.warning("⚠️ **Enhanced Detection Active**: The model is using ultra-sensitive detection to catch dark oil spill areas that might be missed by standard thresholds.")
        st.info("💡 **Tip**: If you see dark areas that look like oil spills but aren't detected, try lowering the confidence threshold to 0.005 or 0.001")
    else:
        st.success("✅ **Standard Detection**: No significant oil spill indicators detected at any confidence level.")
    
    # Save results if enabled
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"result_{timestamp}.jpg"
        # Convert to RGB and save as JPG
        rgb_overlay = overlay.convert("RGB")
        img_byte_arr = io.BytesIO()
        rgb_overlay.save(img_byte_arr, format='JPEG', quality=95)
        result_path = save_file_bytes("./results", result_filename, 
                                    img_byte_arr.getvalue())
        st.success(f"✅ Results saved to: {result_path}")
        
        # Save to database
        detection_id = str(uuid.uuid4())
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        severity = determine_severity(confidence)
        
        # Location and notes removed
        location = ""
        notes = ""
        
        # Prepare detection data
        detection_data = {
            "id": detection_id,
            "timestamp": current_time,
            "filename": uploaded.name,
            "confidence": confidence,
            "oil_pixel_ratio_high": result["oil_pixel_ratio_05"],
            "oil_pixel_ratio_medium": result["oil_pixel_ratio_03"],
            "oil_pixel_ratio_low": result["oil_pixel_ratio_01"],
            "severity": severity,
            "location": location,
            "notes": notes,
            "image_path": os.path.join("./uploads", uploaded.name) if save_uploads else "",
            "result_path": result_path,
            "is_alerted": 0
        }
        
        # Save to database
        try:
            save_detection_to_db(detection_data)
            st.success("✅ Detection saved to database")
            
            # Send alert if confidence exceeds threshold
            if confidence >= ALERT_THRESHOLD and ENABLE_EMAIL_ALERTS:
                if send_email_alert(detection_data, detection_data["image_path"], detection_data["result_path"]):
                    st.success("✅ Alert sent successfully")
                    
                    # Update alert status in database
                    conn = init_db()
                    c = conn.cursor()
                    c.execute("UPDATE detections SET is_alerted = 1 WHERE id = ?", (detection_id,))
                    conn.commit()
                    conn.close()
        except Exception as e:
            st.error(f"Failed to save to database: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>🛢️ Oil Spill Detection AI</strong> | Powered by Deep Learning</p>
    <p>Upload satellite or aerial imagery to detect potential oil spills</p>
    <p>Developed by Akshat Raikar</p>
</div>
""", unsafe_allow_html=True)

