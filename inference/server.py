"""
DeepSpill inference API – FastAPI server for oil spill detection.
Run: uvicorn server:app --reload --host 0.0.0.0 --port 8000
"""
import os
import io
import base64
from contextlib import asynccontextmanager

import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "oil_spill_model.h5"),
)
DEFAULT_INPUT_SIZE = (128, 128)

model = None


def load_inference_model(path=MODEL_PATH):
    global model
    if model is None:
        try:
            from tensorflow.keras.models import load_model
        except ImportError:
            try:
                from keras.models import load_model
            except ImportError:
                raise RuntimeError('TensorFlow/Keras required for inference.')
        model = load_model(path, compile=False)
    return model


def preprocess_image(pil_img, target_size, channels=1):
    if channels == 1:
        img = pil_img.convert("L")
        arr = np.array(img.resize(target_size, Image.LANCZOS), dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, axis=-1)
    elif channels == 2:
        img = pil_img.convert("L")
        arr = np.array(img.resize(target_size, Image.LANCZOS), dtype=np.float32) / 255.0
        arr = np.stack([arr, arr], axis=-1)
    else:
        img = pil_img.convert("RGB")
        arr = np.array(img.resize(target_size, Image.LANCZOS), dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def clean_mask(mask, min_area=100):
    try:
        import cv2
        mask_uint8 = (mask * 255).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_cleaned = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_cleaned, 8)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] < min_area:
                mask_cleaned[labels == i] = 0
        return mask_cleaned.astype(np.float32) / 255.0
    except ImportError:
        return mask


def postprocess_prediction(pred, original_size, threshold=0.1):
    if isinstance(pred, list):
        pred = pred[0]
    mask = np.array(pred)
    if mask.ndim == 4:
        mask = mask[0]
    if mask.ndim == 3 and mask.shape[2] in (1, 3):
        mask = mask[:, :, 0]
    if mask.min() < -1 or mask.max() > 1:
        mask = 1 / (1 + np.exp(-mask))
    mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)
    try:
        import cv2
        mask_uint8 = (mask * 255).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_cleaned = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_mask = np.zeros_like(mask_cleaned)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = max(w, h) / max(min(w, h), 1)
                if aspect_ratio < 10:
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > 0.1:
                            cv2.fillPoly(filtered_mask, [contour], 255)
        mask_cleaned = filtered_mask.astype(np.float32) / 255.0
    except ImportError:
        mask_cleaned = clean_mask(mask, min_area=200)

    oil_pixel_ratio_05 = float((mask_cleaned > 0.5).mean())
    oil_pixel_ratio_03 = float((mask_cleaned > 0.3).mean())
    oil_pixel_ratio_01 = float((mask_cleaned > 0.1).mean())
    oil_pixel_ratio_005 = float((mask_cleaned > 0.05).mean())
    # confidence is the ratio at the requested threshold (clamped to nearest bucket)
    confidence = float((mask_cleaned > threshold).mean())

    mask_img = Image.fromarray((mask_cleaned * 255).astype(np.uint8)).resize(
        original_size, Image.LANCZOS
    )
    return {
        "mask_image": mask_img,
        "oil_pixel_ratio_05": oil_pixel_ratio_05,
        "oil_pixel_ratio_03": oil_pixel_ratio_03,
        "oil_pixel_ratio_01": oil_pixel_ratio_01,
        "oil_pixel_ratio_005": oil_pixel_ratio_005,
        "confidence": confidence,
    }


def create_enhanced_overlay(image_pil, mask_pil, alpha=0.6):
    mask_arr = np.array(mask_pil.convert("L"))
    overlay_arr = np.zeros((image_pil.size[1], image_pil.size[0], 4), dtype=np.uint8)
    overlay_arr[mask_arr > 200, 0] = 255
    overlay_arr[mask_arr > 200, 3] = int(255 * alpha)
    med = (mask_arr > 150) & (mask_arr <= 200)
    overlay_arr[med, 0] = 255
    overlay_arr[med, 1] = 165
    overlay_arr[med, 3] = int(255 * alpha * 0.8)
    low = (mask_arr > 100) & (mask_arr <= 150)
    overlay_arr[low, 1] = 255
    overlay_arr[low, 3] = int(255 * alpha * 0.5)
    vlow = (mask_arr > 50) & (mask_arr <= 100)
    overlay_arr[vlow, 2] = 255
    overlay_arr[vlow, 3] = int(255 * alpha * 0.3)
    overlay = Image.fromarray(overlay_arr, "RGBA")
    return Image.alpha_composite(image_pil.convert("RGBA"), overlay)


def pil_to_base64(pil_img, fmt="PNG"):
    buf = io.BytesIO()
    if pil_img.mode == "RGBA":
        pil_img.save(buf, format="PNG")
    else:
        pil_img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.path.exists(MODEL_PATH):
        load_inference_model()
    else:
        print(
            f"Warning: Model not found at {MODEL_PATH}. "
            "Set MODEL_PATH env var or place oil_spill_model.h5 in the project root."
        )
    yield


app = FastAPI(title="DeepSpill Inference", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(
    image: UploadFile = File(...),
    threshold: str = Form("0.1"),
):
    threshold_f = float(threshold)
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))
    orig_size = img.size
    mdl = load_inference_model()
    if mdl is None:
        return {"error": "Model not loaded"}
    input_shape = tuple(mdl.inputs[0].shape)
    channels = int(input_shape[3]) if len(input_shape) > 3 and input_shape[3] else 1
    target_size = (
        (int(input_shape[1]), int(input_shape[2]))
        if input_shape[1] and input_shape[2]
        else DEFAULT_INPUT_SIZE
    )
    x = preprocess_image(img, target_size, channels)
    preds = mdl.predict(x)
    result = postprocess_prediction(preds, orig_size, threshold=threshold_f)
    overlay = create_enhanced_overlay(img, result["mask_image"])
    return {
        "originalBase64": pil_to_base64(img.convert("RGB"), "PNG"),
        "maskBase64": pil_to_base64(result["mask_image"]),
        "overlayBase64": pil_to_base64(overlay.convert("RGB"), "PNG"),
        "confidence": result["confidence"],
        "oil_pixel_ratio_05": result["oil_pixel_ratio_05"],
        "oil_pixel_ratio_03": result["oil_pixel_ratio_03"],
        "oil_pixel_ratio_01": result["oil_pixel_ratio_01"],
        "oil_pixel_ratio_005": result["oil_pixel_ratio_005"],
    }
