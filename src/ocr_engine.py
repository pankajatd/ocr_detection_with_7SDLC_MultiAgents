"""
Core AI Deep Learning OCR Engine Module
Universal Optical Character Recognition (OCR) System
"""

import re
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import cv2

# Import pre-processing and visualization from src.utils
try:
    from src.utils import preprocess_document_image, draw_ocr_bounding_boxes
except ImportError:
    from utils import preprocess_document_image, draw_ocr_bounding_boxes

logger = logging.getLogger(__name__)

# Cached singleton instance of the OCR Engine
_CACHED_ENGINE: Optional["OCREngineWrapper"] = None


class OCREngineWrapper:
    """
    Unified wrapper supporting primary Deep Learning CRAFT/CRNN engine
    and fail-safe morphological computer vision fallback.
    """
    def __init__(self, engine_type: str, engine_obj: Any):
        self.engine_type = engine_type  # 'deep_learning' or 'geometric_fallback'
        self.engine_obj = engine_obj

    def is_deep_learning(self) -> bool:
        return self.engine_type == "deep_learning"


# Official Indian State & Union Territory Vehicle Registration Codes (Motor Vehicles Act)
INDIAN_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL", "DN",
    "GA", "GJ", "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD",
    "MH", "ML", "MN", "MP", "MZ", "NL", "OD", "PB", "PY", "RJ",
    "SK", "TN", "TR", "TS", "UK", "UP", "WB",
}


def disambiguate_license_plate(text: str) -> str:
    """
    Applies contextual disambiguation for vehicle registration / license plates.
    e.g., resolving '0' vs 'O', '1' vs 'I', '8' vs 'B' based on plate regex schemas,
    and ensuring state codes (such as 'MH' for Maharashtra) and registration strings
    are strictly and accurately capitalized (e.g., resolving optical 'Mh' or 'mh' to 'MH').
    """
    if not text:
        return text

    cleaned = text.strip()
    upper_cleaned = cleaned.upper()
    compact = re.sub(r"[^A-Z0-9]", "", upper_cleaned)

    # 1. Standalone Indian State Code check (e.g., "MH", "Mh", "mh", "DL", "dl", "KA", "ka")
    if compact in INDIAN_STATE_CODES:
        return compact

    # 2. Standard Indian Plate Pattern: 2 Letters (State) + 2 Digits (RTO) + 1-2 Letters + 4 Digits
    # Example: MH12AB1234, DL01A1234, Mh 12 ab 1234
    ind_match = re.match(r"^([A-Z0-9]{2})([A-Z0-9]{2})([A-Z0-9]{1,2})([A-Z0-9]{4})$", compact)
    if ind_match:
        p1, p2, p3, p4 = ind_match.groups()
        # p1: State (Letters) - e.g. MH, DL
        p1 = p1.replace("0", "O").replace("1", "I").replace("8", "B").replace("5", "S")
        # p2: RTO code (Digits) - e.g. 12, 01
        p2 = p2.replace("O", "0").replace("I", "1").replace("Z", "2").replace("S", "5").replace("B", "8")
        # p3: Series (Letters) - e.g. AB
        p3 = p3.replace("0", "O").replace("1", "I").replace("8", "B").replace("5", "S")
        # p4: Unique Number (Digits) - e.g. 1234
        p4 = p4.replace("O", "0").replace("I", "1").replace("Z", "2").replace("S", "5").replace("B", "8")
        return f"{p1} {p2} {p3} {p4}"

    # 3. Two-line Indian Plate Header Pattern: State (2 Letters) + RTO Code (2 Digits)
    # Example: "MH 12", "Mh 12", "MH-12", "Mh12"
    ind_prefix_match = re.match(r"^([A-Z0-9]{2})([A-Z0-9]{2})$", compact)
    if ind_prefix_match:
        p1, p2 = ind_prefix_match.groups()
        p1 = p1.replace("0", "O").replace("1", "I").replace("8", "B").replace("5", "S")
        p2 = p2.replace("O", "0").replace("I", "1").replace("Z", "2").replace("S", "5").replace("B", "8")
        if p1 in INDIAN_STATE_CODES or p2.isdigit():
            return f"{p1} {p2}"

    # 4. Partial Indian Plate Pattern (e.g. "DL 01 AB 78" or short series):
    ind_short_match = re.match(r"^([A-Z0-9]{2})([A-Z0-9]{2})([A-Z0-9]{1,2})([A-Z0-9]{1,3})$", compact)
    if ind_short_match:
        p1, p2, p3, p4 = ind_short_match.groups()
        p1 = p1.replace("0", "O").replace("1", "I").replace("8", "B").replace("5", "S")
        p2 = p2.replace("O", "0").replace("I", "1").replace("Z", "2").replace("S", "5").replace("B", "8")
        p3 = p3.replace("0", "O").replace("1", "I").replace("8", "B").replace("5", "S")
        p4 = p4.replace("O", "0").replace("I", "1").replace("Z", "2").replace("S", "5").replace("B", "8")
        if p1 in INDIAN_STATE_CODES:
            return f"{p1} {p2} {p3} {p4}"

    # 5. UK Plate Pattern: 2 Letters (Memory tag) + 2 Digits (Age) + 3 Letters
    # Example: BD51 SMR
    uk_match = re.match(r"^([A-Z0-9]{2})([A-Z0-9]{2})([A-Z0-9]{3})$", compact)
    if uk_match:
        p1, p2, p3 = uk_match.groups()
        p1 = p1.replace("0", "O").replace("1", "I")
        p2 = p2.replace("O", "0").replace("I", "1").replace("Z", "2").replace("S", "5")
        p3 = p3.replace("0", "O").replace("1", "I")
        return f"{p1}{p2} {p3}"

    # 6. Normalize any state code prefix (e.g., "Mh", "mh" -> "MH") in general alphanumeric tokens
    refined = re.sub(r"\b[mM][hH](?=[\s\-_0-9]|$)", "MH", cleaned)
    for code in INDIAN_STATE_CODES:
        pattern = r"\b" + code[0] + r"[" + code[1].lower() + code[1].upper() + r"](?=[\s\-_0-9]|$)"
        refined = re.sub(pattern, code, refined)

    return refined


def load_ocr_engine(languages: Optional[List[str]] = None) -> OCREngineWrapper:
    """
    Initializes and caches the Deep Learning OCR engine (English alphanumeric default).
    If GPU (CUDA) is available, uses GPU; otherwise runs smoothly on CPU.
    Defensively falls back to geometric fallback if neural network weights cannot be initialized.
    """
    global _CACHED_ENGINE
    if _CACHED_ENGINE is not None:
        return _CACHED_ENGINE

    lang_list = languages if languages else ["en"]

    try:
        import torch
        import easyocr

        use_gpu = torch.cuda.is_available()
        # Initialize EasyOCR reader (downloads model weights on first run, cached locally in ~/.EasyOCR)
        reader = easyocr.Reader(lang_list, gpu=use_gpu, verbose=False)
        _CACHED_ENGINE = OCREngineWrapper(engine_type="deep_learning", engine_obj=reader)
        logger.info("Successfully loaded Deep Learning OCR Engine (EasyOCR CRAFT + CRNN).")
        return _CACHED_ENGINE

    except Exception as exc:
        logger.warning(
            f"Failed to load Deep Learning OCR engine: {exc}. Activating Fail-Safe Computer Vision fallback."
        )
        _CACHED_ENGINE = OCREngineWrapper(engine_type="geometric_fallback", engine_obj=None)
        return _CACHED_ENGINE


def _geometric_fallback_detection(
    image: np.ndarray, confidence_threshold: float = 0.30
) -> List[Dict[str, Any]]:
    """
    Fail-safe morphological text detection using OpenCV contour analysis
    when deep learning weights are not yet downloaded or in restricted offline environments.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    line_idx = 1

    for cnt in sorted(contours, key=lambda c: cv2.boundingRect(c)[1]):
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 20 and h > 8 and w * h > 150:
            box = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
            detections.append({
                "line_id": line_idx,
                "text": f"[Detected Text Block #{line_idx}]",
                "confidence": 0.85,
                "box": box,
            })
            line_idx += 1

    return detections


def detect_and_extract_text(
    image: np.ndarray,
    engine: Optional[OCREngineWrapper] = None,
    confidence_threshold: float = 0.30,
) -> Dict[str, Any]:
    """
    Master Optical Character Recognition Pipeline:
    1. Pre-processes input image (CLAHE, bilateral denoising, auto-deskewing).
    2. Executes CRAFT text localization and CRNN sequence recognition.
    3. Resolves vehicle plate alphanumeric ambiguities (e.g. 0 vs O, 1 vs I).
    4. Renders visual bounding boxes on image canvas.
    5. Returns structured schema:
       {
           "annotated_image": np.ndarray,
           "total_text_blocks": int,
           "extracted_text": str,
           "detections": [
               {"line_id": int, "text": str, "confidence": float, "box": (x1, y1, x2, y2)}
           ]
       }
    """
    if image is None or image.size == 0:
        return {
            "annotated_image": image,
            "total_text_blocks": 0,
            "extracted_text": "",
            "detections": [],
        }

    # Ensure engine is loaded
    if engine is None:
        engine = load_ocr_engine()

    # Step 1: Preprocess image
    preprocessed = preprocess_document_image(image)

    detections: List[Dict[str, Any]] = []

    # Step 2: Inference execution
    if engine.is_deep_learning() and engine.engine_obj is not None:
        try:
            # EasyOCR expects RGB image array or path
            if len(preprocessed.shape) == 3:
                rgb_img = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2RGB)
            else:
                rgb_img = cv2.cvtColor(preprocessed, cv2.COLOR_GRAY2RGB)

            raw_results = engine.engine_obj.readtext(rgb_img)

            # Sort detected blocks in natural reading order (top-to-bottom, left-to-right)
            def _reading_order_key(item):
                box = item[0]
                y_min = min(pt[1] for pt in box)
                x_min = min(pt[0] for pt in box)
                return (int(y_min // 25) * 25, x_min)

            sorted_results = sorted(raw_results, key=_reading_order_key)

            line_idx = 1
            for bbox, text, conf in sorted_results:
                if conf < confidence_threshold:
                    continue

                # Disambiguate if looks like license plate
                refined_text = disambiguate_license_plate(text)

                # Format bbox as polygon [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                box_pts = [[int(pt[0]), int(pt[1])] for pt in bbox]

                detections.append({
                    "line_id": line_idx,
                    "text": refined_text,
                    "confidence": float(conf),
                    "box": box_pts,
                })
                line_idx += 1
        except Exception as exc:
            logger.error(f"Error during deep learning OCR inference: {exc}. Using fallback.")
            detections = _geometric_fallback_detection(preprocessed, confidence_threshold)
    else:
        detections = _geometric_fallback_detection(preprocessed, confidence_threshold)

    # Step 3: Draw high-contrast bounding boxes with boundary clamping
    annotated_image = draw_ocr_bounding_boxes(preprocessed, detections)

    # Step 4: Aggregate extracted text string
    extracted_lines = [d["text"] for d in detections if d["text"]]
    extracted_text = "\n".join(extracted_lines)

    return {
        "annotated_image": annotated_image,
        "total_text_blocks": len(detections),
        "extracted_text": extracted_text,
        "detections": detections,
    }
