"""
Utility & Computer Vision Pre-Processing Module
Universal Optical Character Recognition (OCR) System
"""

import io
import csv
import json
from typing import List, Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image


def validate_image_bytes(file_bytes: bytes) -> bool:
    """
    Validates that uploaded raw bytes represent a readable, non-corrupt image format.
    Guards against null bytes, oversized payloads (>200MB), and invalid formats.
    """
    if not file_bytes:
        return False
    if len(file_bytes) > 200 * 1024 * 1024:  # 200MB DoS protection limit
        return False

    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
        # Verify actual decoding of pixel data
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.load()
        return True
    except Exception:
        return False


def estimate_skew_angle(image: np.ndarray) -> float:
    """
    Estimates document or text tilt angle (-45 to +45 degrees) using contour orientation.
    Returns angle in degrees to counter-rotate.
    """
    try:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Invert and threshold to highlight text features
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Morphological dilation to connect text lines horizontally
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        angles = []

        for cnt in contours:
            if cv2.contourArea(cnt) < 150:
                continue
            rect = cv2.minAreaRect(cnt)
            (w, h) = rect[1]
            angle = rect[2]
            # Standardize orientation angle
            if w < h:
                angle = angle + 90
            if abs(angle) > 0.5:
                angles.append(angle)

        if not angles:
            return 0.0

        # Return median angle to reject outlier noise
        median_angle = float(np.median(angles))
        if -45.0 <= median_angle <= 45.0:
            return median_angle
        return 0.0
    except Exception:
        return 0.0


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotates an image around its center by a specified angle in degrees,
    filling exposed border regions with white background.
    """
    if abs(angle) < 0.5:
        return image

    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    # Calculate rotation matrix
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Calculate new bounding dimensions to prevent clipping
    cos = np.abs(rot_mat[0, 0])
    sin = np.abs(rot_mat[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    rot_mat[0, 2] += (new_w / 2) - center[0]
    rot_mat[0, 2] += (new_h / 2) - center[1]

    # Warp image with white background padding
    border_color = (255, 255, 255) if len(image.shape) == 3 else 255
    rotated = cv2.warpAffine(
        image,
        rot_mat,
        (new_w, new_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_color,
    )
    return rotated


def preprocess_document_image(image: np.ndarray) -> np.ndarray:
    """
    Applies computer vision pre-processing pipeline:
    1. Color normalization: Handles Grayscale, BGR, and RGB inputs.
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization) on L-channel
       to eliminate harsh shadows and headlight glare on plates.
    3. Bilateral filtering to denoise textures while preserving crisp character edges.
    4. Auto-deskew estimation for tilted documents up to 45 degrees.
    """
    if image is None or image.size == 0:
        return image

    processed = image.copy()

    # Step 1: CLAHE Contrast Normalization
    if len(processed.shape) == 3 and processed.shape[2] == 3:
        lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        merged_lab = cv2.merge((cl, a_channel, b_channel))
        processed = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
    elif len(processed.shape) == 2:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        processed = clahe.apply(processed)

    # Step 2: Bilateral Filtering (edge-preserving denoising)
    processed = cv2.bilateralFilter(processed, d=5, sigmaColor=50, sigmaSpace=50)

    # Step 3: Auto-deskew
    skew_angle = estimate_skew_angle(processed)
    if abs(skew_angle) >= 1.0:
        processed = rotate_image(processed, skew_angle)

    return processed


def draw_ocr_bounding_boxes(
    image: np.ndarray,
    detections: List[Dict[str, Any]],
    box_color: Tuple[int, int, int] = (0, 180, 255)
) -> np.ndarray:
    """
    Draws high-contrast bounding boxes around detected text blocks with adaptive
    background banners displaying text snippets and confidence percentages.

    Features boundary clamping so banners are never cut off at image margins.
    """
    if image is None or image.size == 0:
        return image

    annotated = image.copy()
    h, w = annotated.shape[:2]

    # Calculate dynamic font scale relative to image resolution
    base_dim = max(h, w)
    font_scale = max(0.40, min(0.75, base_dim / 1600.0))
    thickness = max(1, int(base_dim / 700.0))
    box_thickness = max(2, int(base_dim / 500.0))

    for det in detections:
        box = det.get("box")
        text = det.get("text", "").strip()
        conf = det.get("confidence", 0.0)

        if box is None:
            continue

        # Handle polygon coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        if isinstance(box, (list, tuple, np.ndarray)) and len(box) == 4 and isinstance(box[0], (list, tuple, np.ndarray)):
            pts = np.array(box, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated, [pts], isClosed=True, color=box_color, thickness=box_thickness)
            x_min = int(min(pt[0] for pt in box))
            y_min = int(min(pt[1] for pt in box))
            x_max = int(max(pt[0] for pt in box))
            y_max = int(max(pt[1] for pt in box))
        elif len(box) == 4:
            # (x1, y1, x2, y2)
            x_min, y_min, x_max, y_max = [int(v) for v in box]
            cv2.rectangle(annotated, (x_min, y_min), (x_max, y_max), box_color, box_thickness)
        else:
            continue

        # Boundary clamping for box coordinates
        x_min = max(0, min(w - 1, x_min))
        y_min = max(0, min(h - 1, y_min))
        x_max = max(0, min(w - 1, x_max))
        y_max = max(0, min(h - 1, y_max))

        # Build label: "TEXT (98%)"
        display_text = text if len(text) <= 24 else text[:21] + "..."
        label = f"{display_text} ({int(conf * 100)}%)"

        (text_w, text_h), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )

        # Determine label placement with boundary clamping
        banner_h = text_h + baseline + 6
        banner_w = text_w + 8

        # Try placing above the box first
        if y_min - banner_h >= 0:
            banner_y1 = y_min - banner_h
            banner_y2 = y_min
        else:
            # Place below box or clamp inside
            banner_y1 = min(h - banner_h, y_max)
            banner_y2 = min(h, banner_y1 + banner_h)

        banner_x1 = max(0, min(w - banner_w, x_min))
        banner_x2 = min(w, banner_x1 + banner_w)

        # Draw solid background badge
        cv2.rectangle(
            annotated,
            (banner_x1, banner_y1),
            (banner_x2, banner_y2),
            box_color,
            thickness=-1,
        )

        # Draw contrasting text (black on bright badge)
        text_origin = (banner_x1 + 4, banner_y2 - baseline - 2)
        cv2.putText(
            annotated,
            label,
            text_origin,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 0, 0),
            thickness,
            lineType=cv2.LINE_AA,
        )

    return annotated


def format_export_data(
    detections: List[Dict[str, Any]], format_type: str = "txt"
) -> str:
    """
    Serializes extracted detections into requested format:
    - 'txt': Plain text with preserved line breaks.
    - 'csv': Comma-separated table (Line_ID, Text, Confidence, Bounding_Box).
    - 'json': Hierarchical structured JSON string.
    """
    fmt = format_type.strip().lower()

    if fmt == "txt":
        lines = [d.get("text", "").strip() for d in detections if d.get("text", "").strip()]
        return "\n".join(lines)

    elif fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Line_ID", "Text", "Confidence", "Bounding_Box"])
        for idx, det in enumerate(detections, start=1):
            line_id = det.get("line_id", idx)
            text = det.get("text", "")
            conf = f"{det.get('confidence', 0.0):.4f}"
            box = str(det.get("box", []))
            writer.writerow([line_id, text, conf, box])
        return output.getvalue()

    elif fmt == "json":
        clean_detections = []
        for idx, det in enumerate(detections, start=1):
            clean_detections.append({
                "line_id": det.get("line_id", idx),
                "text": det.get("text", ""),
                "confidence": round(float(det.get("confidence", 0.0)), 4),
                "box": det.get("box", [])
            })
        return json.dumps(clean_detections, indent=2)

    else:
        raise ValueError(f"Unsupported format_type: '{format_type}'. Use 'txt', 'csv', or 'json'.")
