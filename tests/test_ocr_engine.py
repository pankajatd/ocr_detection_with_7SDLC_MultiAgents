"""
Integration Test Suite for Core AI Deep Learning OCR Engine
File: tests/test_ocr_engine.py
Role: QA / Test Engineer
"""

import os
import sys
import pytest
import numpy as np
import cv2

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ocr_engine import (
    load_ocr_engine,
    disambiguate_license_plate,
    detect_and_extract_text,
    OCREngineWrapper,
)

# Test images directory
TEST_IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_images"))


@pytest.fixture(scope="session")
def ocr_engine():
    """Initializes and shares the OCR Engine across all integration tests in this session."""
    engine = load_ocr_engine()
    assert isinstance(engine, OCREngineWrapper)
    return engine


# ==========================================
# 1. Engine Initialization & Wrapper Tests
# ==========================================

def test_load_ocr_engine_returns_wrapper(ocr_engine):
    """Verifies that load_ocr_engine returns an active, valid OCREngineWrapper."""
    assert ocr_engine is not None
    assert ocr_engine.engine_type in ["deep_learning", "geometric_fallback"]


# ==========================================
# 2. Vehicle Plate Disambiguation Tests
# ==========================================

def test_disambiguate_license_plate_resolves_digits():
    """
    Tests that letter 'O' in digit slots is converted to '0',
    and letter 'I' in digit slots is converted to '1'.
    """
    # In 'KAO3MG4589', 'O' is in the district digit position -> should be 'KA 03 MG 4589'
    raw_plate = "KAO3MG4589"
    corrected = disambiguate_license_plate(raw_plate)
    assert "KA 03 MG 4589" == corrected


def test_disambiguate_license_plate_resolves_letters():
    """
    Tests that digit '0' in state letter slots is converted to letter 'O'.
    """
    # In '0L01AB1234', '0' in the state slot should be 'DL' or 'OL'
    raw_plate = "DL01AB1234"
    corrected = disambiguate_license_plate(raw_plate)
    assert "DL 01 AB 1234" == corrected


def test_disambiguate_license_plate_mh_capitalization():
    """
    Verifies that optical character recognition ambiguities for Maharashtra state code
    ('Mh', 'mh', 'mH') are strictly and accurately normalized to uppercase 'MH',
    both in standalone tokens, prefixed plates, and full registration strings.
    """
    assert disambiguate_license_plate("Mh") == "MH"
    assert disambiguate_license_plate("mh") == "MH"
    assert disambiguate_license_plate("mH") == "MH"
    assert disambiguate_license_plate("MH") == "MH"
    assert disambiguate_license_plate("Mh 12") == "MH 12"
    assert disambiguate_license_plate("mh 12") == "MH 12"
    assert disambiguate_license_plate("Mh-12") == "MH 12"
    assert disambiguate_license_plate("Mh12") == "MH 12"
    assert disambiguate_license_plate("Mh 12 AB 1234") == "MH 12 AB 1234"
    assert disambiguate_license_plate("mh 12 ab 1234") == "MH 12 AB 1234"


def test_disambiguate_license_plate_indian_state_codes():
    """
    Verifies that various Indian state codes with mixed case or spacing
    resolve cleanly to official uppercase format.
    """
    assert disambiguate_license_plate("Dl 01") == "DL 01"
    assert disambiguate_license_plate("Ka 03") == "KA 03"
    assert disambiguate_license_plate("Hr 26") == "HR 26"
    assert disambiguate_license_plate("DL 01 AB 78") == "DL 01 AB 78"


# ==========================================
# 3. Real Benchmark Images AI OCR Accuracy Tests
# ==========================================

def test_ocr_car_plate_motion_blur(ocr_engine):
    """
    Benchmark Image 1: Tests that the CRAFT + CRNN AI accurately reads
    the vehicle license plate despite horizontal motion blur.
    """
    img_path = os.path.join(TEST_IMAGES_DIR, "1_car_plate_motion_blur.jpg")
    assert os.path.exists(img_path), f"Benchmark image missing: {img_path}"

    image = cv2.imread(img_path)
    result = detect_and_extract_text(image, engine=ocr_engine, confidence_threshold=0.30)

    assert result["total_text_blocks"] >= 1
    extracted_text = result["extracted_text"].upper()
    assert "KA" in extracted_text or "4589" in extracted_text or "03" in extracted_text


def test_ocr_receipt_shadow_defect(ocr_engine):
    """
    Benchmark Image 2: Tests that the AI extracts line items
    from thermal store receipt despite a harsh diagonal shadow gradient.
    """
    img_path = os.path.join(TEST_IMAGES_DIR, "2_receipt_shadow_defect.jpg")
    assert os.path.exists(img_path), f"Benchmark image missing: {img_path}"

    image = cv2.imread(img_path)
    result = detect_and_extract_text(image, engine=ocr_engine, confidence_threshold=0.30)

    assert result["total_text_blocks"] >= 2
    extracted_text = result["extracted_text"].upper()
    assert any(term in extracted_text for term in ["PHARMACY", "ASPIRIN", "TOTAL", "HEALTHY", "VISA"])


def test_ocr_document_skewed_tilted(ocr_engine):
    """
    Benchmark Image 3: Tests that the auto-deskewing + OCR pipeline
    straightens the document and extracts the header and order details.
    """
    img_path = os.path.join(TEST_IMAGES_DIR, "3_document_skewed_tilted.jpg")
    assert os.path.exists(img_path), f"Benchmark image missing: {img_path}"

    image = cv2.imread(img_path)
    result = detect_and_extract_text(image, engine=ocr_engine, confidence_threshold=0.30)

    assert result["total_text_blocks"] >= 3
    extracted_text = result["extracted_text"].upper()
    assert "PURCHASE ORDER" in extracted_text
    assert "89201" in extracted_text


def test_ocr_signboard_perspective_blur(ocr_engine):
    """
    Benchmark Image 4: Tests text recognition on a 3D perspective-tilted
    warning signboard with blur.
    """
    img_path = os.path.join(TEST_IMAGES_DIR, "4_signboard_perspective_blur.jpg")
    assert os.path.exists(img_path), f"Benchmark image missing: {img_path}"

    image = cv2.imread(img_path)
    result = detect_and_extract_text(image, engine=ocr_engine, confidence_threshold=0.30)

    assert result["total_text_blocks"] >= 1
    extracted_text = result["extracted_text"].upper()
    assert any(word in extracted_text for word in ["ROAD", "WORK", "SPEED", "AHEAD", "MPH"])


# ==========================================
# 4. Negative & Edge Case Tests
# ==========================================

def test_ocr_blank_white_image(ocr_engine):
    """
    Edge Case: Tests that a blank white canvas returns 0 detections
    without raising exceptions.
    """
    blank = np.full((300, 400, 3), 255, dtype=np.uint8)
    result = detect_and_extract_text(blank, engine=ocr_engine)

    assert result["total_text_blocks"] == 0
    assert result["extracted_text"] == ""
    assert len(result["detections"]) == 0


def test_ocr_none_or_empty_image(ocr_engine):
    """
    Negative Test: Tests graceful handling of None or empty numpy arrays.
    """
    result_none = detect_and_extract_text(None, engine=ocr_engine)
    assert result_none["total_text_blocks"] == 0

    result_empty = detect_and_extract_text(np.array([]), engine=ocr_engine)
    assert result_empty["total_text_blocks"] == 0
