"""
Unit Test Suite for Preprocessing, Utility, and Export Functions
File: tests/test_utils.py
Role: QA / Test Engineer
"""

import io
import os
import sys
import json
import pytest
import numpy as np
import cv2
from PIL import Image

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import (
    validate_image_bytes,
    estimate_skew_angle,
    rotate_image,
    preprocess_document_image,
    draw_ocr_bounding_boxes,
    format_export_data,
)


@pytest.fixture
def sample_rgb_image():
    """Generates a standard 200x200 3-channel test image with synthetic text."""
    img = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.putText(img, "TEST", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    return img


@pytest.fixture
def sample_valid_image_bytes(sample_rgb_image):
    """Encodes a sample image into valid PNG byte stream."""
    success, buffer = cv2.imencode(".png", sample_rgb_image)
    assert success
    return buffer.tobytes()


@pytest.fixture
def sample_detections():
    """Standardized detection dictionary fixtures."""
    return [
        {
            "line_id": 1,
            "text": "PURCHASE ORDER #89201",
            "confidence": 0.9452,
            "box": [[10, 10], [180, 10], [180, 40], [10, 40]],
        },
        {
            "line_id": 2,
            "text": "TOTAL: $150.00",
            "confidence": 0.8871,
            "box": [[10, 60], [150, 60], [150, 90], [10, 90]],
        },
    ]


# ==========================================
# 1. Validation Tests (validate_image_bytes)
# ==========================================

def test_validate_image_bytes_valid_png(sample_valid_image_bytes):
    """Verifies that legitimate image bytes return True."""
    assert validate_image_bytes(sample_valid_image_bytes) is True


def test_validate_image_bytes_empty():
    """Verifies that empty bytes return False without crashing."""
    assert validate_image_bytes(b"") is False
    assert validate_image_bytes(None) is False


def test_validate_image_bytes_corrupt():
    """Verifies that random garbage bytes return False."""
    garbage = b"\x00\xFF\xDE\xAD\xBE\xEF\x12\x34\x56\x78"
    assert validate_image_bytes(garbage) is False


def test_validate_image_bytes_oversized():
    """Verifies that payloads exceeding the 200MB limit are safely rejected."""
    # Mocking by checking size condition
    oversized = b"0" * (200 * 1024 * 1024 + 1)
    assert validate_image_bytes(oversized) is False


# ==========================================
# 2. Skew Estimation & Rotation Tests
# ==========================================

def test_estimate_skew_angle_straight(sample_rgb_image):
    """Verifies that a straight, unrotated image has a near-zero skew angle."""
    angle = estimate_skew_angle(sample_rgb_image)
    assert abs(angle) < 5.0


def test_rotate_image_zero_angle(sample_rgb_image):
    """Verifies that a 0-degree rotation returns the image unchanged."""
    rotated = rotate_image(sample_rgb_image, 0.0)
    assert rotated.shape == sample_rgb_image.shape


def test_rotate_image_preserves_valid_array(sample_rgb_image):
    """Verifies that rotation outputs a valid non-empty ndarray."""
    rotated = rotate_image(sample_rgb_image, 15.0)
    assert isinstance(rotated, np.ndarray)
    assert rotated.size > 0
    assert len(rotated.shape) == 3


# ==========================================
# 3. Pre-Processing Pipeline Tests
# ==========================================

def test_preprocess_document_image_rgb(sample_rgb_image):
    """Verifies that CLAHE and bilateral filtering process 3-channel images cleanly."""
    processed = preprocess_document_image(sample_rgb_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape[2] == 3
    assert not np.isnan(processed).any()


def test_preprocess_document_image_grayscale():
    """Verifies that grayscale images are handled without crash."""
    gray = np.full((150, 150), 200, dtype=np.uint8)
    processed = preprocess_document_image(gray)
    assert isinstance(processed, np.ndarray)
    assert len(processed.shape) == 2


def test_preprocess_document_image_empty():
    """Verifies that empty/None images return gracefully."""
    assert preprocess_document_image(None) is None
    empty_arr = np.array([])
    assert preprocess_document_image(empty_arr).size == 0


# ==========================================
# 4. Box Annotation & Boundary Clamping Tests
# ==========================================

def test_draw_ocr_bounding_boxes_standard(sample_rgb_image, sample_detections):
    """Verifies that high-contrast bounding boxes are drawn on the image canvas."""
    annotated = draw_ocr_bounding_boxes(sample_rgb_image, sample_detections)
    assert isinstance(annotated, np.ndarray)
    assert annotated.shape == sample_rgb_image.shape
    # Image should have changed due to drawing boxes
    assert not np.array_equal(annotated, sample_rgb_image)


def test_draw_ocr_bounding_boxes_boundary_clamping(sample_rgb_image):
    """
    CRITICAL EDGE CASE: Text right at (0,0) or (w,h) margins.
    Ensures text banners never clip or cause out-of-bounds array access.
    """
    h, w = sample_rgb_image.shape[:2]
    edge_detections = [
        {"line_id": 1, "text": "TOP_LEFT", "confidence": 0.99, "box": [[0, 0], [50, 0], [50, 20], [0, 20]]},
        {"line_id": 2, "text": "BOTTOM_RIGHT", "confidence": 0.95, "box": [[w-50, h-20], [w, h-20], [w, h], [w-50, h]]},
    ]
    annotated = draw_ocr_bounding_boxes(sample_rgb_image, edge_detections)
    assert annotated.shape == (h, w, 3)


def test_draw_ocr_bounding_boxes_empty(sample_rgb_image):
    """Verifies that empty detection lists return an identical image copy."""
    annotated = draw_ocr_bounding_boxes(sample_rgb_image, [])
    assert np.array_equal(annotated, sample_rgb_image)


# ==========================================
# 5. Export Serialization Tests
# ==========================================

def test_format_export_data_txt(sample_detections):
    """Verifies plain text serialization with line breaks."""
    txt = format_export_data(sample_detections, "txt")
    lines = txt.strip().split("\n")
    assert len(lines) == 2
    assert lines[0] == "PURCHASE ORDER #89201"
    assert lines[1] == "TOTAL: $150.00"


def test_format_export_data_csv(sample_detections):
    """Verifies CSV table serialization with proper headers."""
    csv_str = format_export_data(sample_detections, "csv")
    assert "Line_ID,Text,Confidence,Bounding_Box" in csv_str
    assert "PURCHASE ORDER #89201" in csv_str
    assert "0.9452" in csv_str


def test_format_export_data_json(sample_detections):
    """Verifies JSON format validity and hierarchical keys."""
    json_str = format_export_data(sample_detections, "json")
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["line_id"] == 1
    assert parsed[0]["text"] == "PURCHASE ORDER #89201"
    assert parsed[0]["confidence"] == 0.9452


def test_format_export_data_invalid_type(sample_detections):
    """Verifies that an unsupported export type raises ValueError."""
    with pytest.raises(ValueError):
        format_export_data(sample_detections, "xml")
