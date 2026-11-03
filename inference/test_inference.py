"""
Unit and integration tests for DeepSpill Computer Vision Inference Service.
Tests preprocessing normalization, morphological noise filtering, and overlay pipelines.
"""
import numpy as np
import pytest
from PIL import Image
import sys
import os

# Ensure inference module is on path
sys.path.insert(0, os.path.dirname(__file__))

from server import (
    preprocess_image,
    clean_mask,
    postprocess_prediction,
    create_enhanced_overlay,
    pil_to_base64,
)


class TestImagePreprocessing:
    def test_preprocess_grayscale_single_channel(self):
        img = Image.new("L", (500, 500), color=128)
        processed = preprocess_image(img, target_size=(128, 128), channels=1)
        assert processed.shape == (1, 128, 128, 1)
        assert processed.dtype == np.float32
        assert 0.0 <= processed.min() <= processed.max() <= 1.0
        assert np.isclose(processed.mean(), 128 / 255.0, atol=1e-2)

    def test_preprocess_rgb_three_channel(self):
        img = Image.new("RGB", (640, 480), color=(255, 100, 50))
        processed = preprocess_image(img, target_size=(128, 128), channels=3)
        assert processed.shape == (1, 128, 128, 3)
        assert processed.dtype == np.float32
        assert 0.0 <= processed.min() <= processed.max() <= 1.0

    def test_preprocess_two_channel_sar(self):
        img = Image.new("L", (256, 256), color=200)
        processed = preprocess_image(img, target_size=(128, 128), channels=2)
        assert processed.shape == (1, 128, 128, 2)
        assert processed.dtype == np.float32


class TestMorphologicalPostprocessing:
    def test_clean_mask_suppresses_small_noise(self):
        # Create a mask with a large spill blob and isolated tiny noise speckles
        mask = np.zeros((128, 128), dtype=np.float32)
        # Large valid spill: 20x20 = 400 pixels (> min_area 100)
        mask[30:50, 30:50] = 1.0
        # Tiny noise specs: 2x2 = 4 pixels (< min_area 100)
        mask[10:12, 10:12] = 1.0
        mask[90:92, 90:92] = 1.0

        cleaned = clean_mask(mask, min_area=100)
        # Noise should be completely eliminated
        assert cleaned[10:12, 10:12].sum() == 0.0
        assert cleaned[90:92, 90:92].sum() == 0.0
        # Main spill should be preserved
        assert cleaned[35:45, 35:45].mean() > 0.9

    def test_postprocess_prediction_structure(self):
        pred_map = np.zeros((128, 128, 1), dtype=np.float32)
        # Create prominent circular slick: area > 200
        y, x = np.ogrid[:128, :128]
        dist_from_center = (x - 64)**2 + (y - 64)**2
        pred_map[dist_from_center <= 15**2, 0] = 0.95

        result = postprocess_prediction(pred_map, original_size=(500, 500), threshold=0.1)
        assert "mask_image" in result
        assert isinstance(result["mask_image"], Image.Image)
        assert result["mask_image"].size == (500, 500)
        assert "confidence" in result
        assert result["confidence"] > 0.0
        assert "oil_pixel_ratio_05" in result


class TestOverlayAndEncoding:
    def test_enhanced_overlay_blending(self):
        base_img = Image.new("RGB", (200, 200), color=(0, 50, 100)) # Ocean blue
        mask = Image.new("L", (200, 200), color=0)
        # Draw high-confidence spill in center
        mask_arr = np.array(mask)
        mask_arr[50:150, 50:150] = 255
        mask_pil = Image.fromarray(mask_arr)

        overlay = create_enhanced_overlay(base_img, mask_pil, alpha=0.6)
        assert overlay.size == (200, 200)
        assert overlay.mode == "RGBA"

    def test_pil_to_base64_serialization(self):
        img = Image.new("RGB", (50, 50), color=(255, 0, 0))
        b64_str = pil_to_base64(img)
        assert isinstance(b64_str, str)
        assert len(b64_str) > 50
        # Valid base64
        import base64
        decoded = base64.b64decode(b64_str)
        assert len(decoded) > 0
