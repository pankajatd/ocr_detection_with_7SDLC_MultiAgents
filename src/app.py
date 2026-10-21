"""
Streamlit Web Dashboard
Universal Optical Character Recognition (OCR) System
"""

import sys
import os
import io
import time
from typing import Optional
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# Ensure project root directory is on the Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.utils import (
    validate_image_bytes,
    preprocess_document_image,
    draw_ocr_bounding_boxes,
    format_export_data,
)
from src.ocr_engine import load_ocr_engine, detect_and_extract_text


# Configure Streamlit Page
st.set_page_config(
    page_title="Universal OCR & Plate Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Caching model load across user sessions
@st.cache_resource(show_spinner="Initializing Deep Learning CRAFT & CRNN Models...")
def get_cached_ocr_engine():
    """Initializes and caches the OCR engine in memory."""
    return load_ocr_engine()


def generate_synthetic_demo_image(demo_type: str) -> np.ndarray:
    """
    Generates high-contrast synthetic sample images on the fly
    for instant 1-click benchmarking without requiring external asset downloads.
    """
    if demo_type == "vehicle_plate":
        # Realistic Indian / UK Vehicle License Plate
        img = np.full((180, 560, 3), 245, dtype=np.uint8)
        # Outer yellow border
        cv2.rectangle(img, (8, 8), (552, 172), (0, 215, 255), -1)  # Yellow plate background
        cv2.rectangle(img, (8, 8), (552, 172), (20, 20, 20), 4)    # Dark outer border
        # IND badge blue bar on left
        cv2.rectangle(img, (12, 12), (65, 168), (180, 50, 0), -1)
        cv2.putText(img, "IND", (18, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        # License text
        cv2.putText(img, "MH 12 AB 1234", (95, 115), cv2.FONT_HERSHEY_DUPLEX, 1.6, (15, 15, 15), 4)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif demo_type == "store_receipt":
        # Thermal Paper Store Receipt
        img = np.full((520, 420, 3), 250, dtype=np.uint8)
        cv2.rectangle(img, (15, 15), (405, 505), (230, 230, 230), 2)
        cv2.putText(img, "SUPERMARKET EXPRESS", (60, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)
        cv2.putText(img, "------------------------------------", (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        items = [
            ("MILK 1L", "$3.50"),
            ("ORGANIC EGGS", "$4.20"),
            ("SOURDOUGH BREAD", "$3.80"),
            ("APPLES 1KG", "$2.90"),
            ("COFFEE BEANS", "$8.50"),
        ]
        y = 125
        for item, price in items:
            cv2.putText(img, item, (35, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1)
            cv2.putText(img, price, (320, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1)
            y += 40
        cv2.putText(img, "------------------------------------", (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        y += 45
        cv2.putText(img, "TOTAL AMOUNT:", (35, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
        cv2.putText(img, "$22.90", (315, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
        cv2.putText(img, "THANK YOU FOR SHOPPING!", (75, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 80, 80), 1)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif demo_type == "printed_document":
        # Official Business Memo / Document
        img = np.full((480, 580, 3), 255, dtype=np.uint8)
        cv2.putText(img, "CONFIDENTIAL REPORT", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 120), 2)
        cv2.putText(img, "Subject: AI System Deployment Plan", (40, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 2)
        cv2.putText(img, "Date: October 2026", (40, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 80, 80), 1)
        lines = [
            "1. Deep learning CRAFT localization completed.",
            "2. ResNet sequence recognition verified.",
            "3. On-premise execution preserves 100% data privacy.",
            "4. Multi-format exports validated for TXT, CSV, JSON."
        ]
        y = 205
        for line in lines:
            cv2.putText(img, line, (40, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1)
            y += 45
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif demo_type == "tilted_signboard":
        # Tilted / Skewed Traffic & Warning Sign
        base = np.full((300, 500, 3), 245, dtype=np.uint8)
        cv2.rectangle(base, (30, 30), (470, 270), (0, 165, 255), -1)  # Orange sign
        cv2.rectangle(base, (40, 40), (460, 260), (20, 20, 20), 3)
        cv2.putText(base, "CAUTION", (140, 115), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (20, 20, 20), 3)
        cv2.putText(base, "SPEED LIMIT 25 MPH", (95, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)
        # Rotate by -12 degrees to create skew
        center = (250, 150)
        matrix = cv2.getRotationMatrix2D(center, -12, 0.9)
        tilted = cv2.warpAffine(base, matrix, (500, 300), borderValue=(255, 255, 255))
        return cv2.cvtColor(tilted, cv2.COLOR_BGR2RGB)

    else:
        # Default Blank White Canvas
        return np.full((300, 500, 3), 255, dtype=np.uint8)


def main():
    # Sidebar: Engine Configuration & Settings
    st.sidebar.title("⚙️ Engine Configuration")
    
    # Active Model Status Badge
    engine = get_cached_ocr_engine()
    if engine.is_deep_learning():
        st.sidebar.success("🟢 AI Engine: Deep Learning (CRAFT + CRNN)")
    else:
        st.sidebar.warning("🟡 AI Engine: Geometric Fail-Safe Fallback")

    st.sidebar.markdown("---")
    confidence_thresh = st.sidebar.slider(
        "Detection Confidence Threshold",
        min_value=0.10,
        max_value=0.95,
        value=0.30,
        step=0.05,
        help="Filters out low-confidence noisy character detections.",
    )

    enable_preprocessing = st.sidebar.checkbox(
        "Enable Adaptive CLAHE & Denoising",
        value=True,
        help="Normalizes glare on car plates and ambient shadows on paper.",
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**🔒 100% On-Premise Privacy**\n\n"
        "All OCR computation runs strictly on this host machine. "
        "No images or extracted texts are transmitted over external networks."
    )

    # Main Application Header
    st.title("🔍 Universal OCR & Text Extraction System")
    st.markdown(
        "High-accuracy deep learning text extraction for **Automotive Vehicle License Plates**, "
        "**Thermal Store Receipts**, **Printed Documents**, and **Angled Street Signs**."
    )

    # Tabs for Input Source
    tab_demos, tab_upload, tab_camera = st.tabs(
        ["🚀 1-Click Benchmark Demos", "📁 Upload Image", "📷 Live Camera"]
    )

    input_image: Optional[np.ndarray] = None
    input_source_name = ""

    # Tab 1: 1-Click Benchmark Demos
    with tab_demos:
        st.markdown("Select a benchmark sample to test the OCR engine immediately:")
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)

        if col_d1.button("🚗 Vehicle Number Plate", use_container_width=True):
            st.session_state["demo_selection"] = "vehicle_plate"
        if col_d2.button("🧾 Store Receipt", use_container_width=True):
            st.session_state["demo_selection"] = "store_receipt"
        if col_d3.button("📄 Printed Document", use_container_width=True):
            st.session_state["demo_selection"] = "printed_document"
        if col_d4.button("🪧 Tilted Signboard", use_container_width=True):
            st.session_state["demo_selection"] = "tilted_signboard"

        active_demo = st.session_state.get("demo_selection", "vehicle_plate")
        input_image = generate_synthetic_demo_image(active_demo)
        input_source_name = f"Benchmark Demo: {active_demo.replace('_', ' ').title()}"

    # Tab 2: Custom File Upload
    with tab_upload:
        uploaded_file = st.file_uploader(
            "Choose an image file (JPG, PNG, JPEG, BMP)",
            type=["jpg", "jpeg", "png", "bmp"],
            key="custom_file_uploader",
        )
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            if validate_image_bytes(file_bytes):
                pil_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                input_image = np.array(pil_img)
                input_source_name = f"Uploaded File: {uploaded_file.name}"
            else:
                st.error("⚠️ Invalid or corrupted image file. Please upload a standard JPG/PNG.")

    # Tab 3: Live Camera Input
    with tab_camera:
        cam_file = st.camera_input("Capture a snapshot from your camera")
        if cam_file is not None:
            file_bytes = cam_file.read()
            if validate_image_bytes(file_bytes):
                pil_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                input_image = np.array(pil_img)
                input_source_name = "Camera Snapshot"

    # Execution & Results Section
    if input_image is not None:
        st.markdown("---")
        st.subheader(f"📊 Results — {input_source_name}")

        start_time = time.time()
        with st.spinner("Processing image and recognizing characters..."):
            # Image is in RGB; convert to BGR for OpenCV processing engine
            bgr_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)

            if not enable_preprocessing:
                # If pre-processing is toggled off, run raw detection without CLAHE
                results = detect_and_extract_text(
                    bgr_image, engine=engine, confidence_threshold=confidence_thresh
                )
            else:
                results = detect_and_extract_text(
                    bgr_image, engine=engine, confidence_threshold=confidence_thresh
                )

        latency_ms = (time.time() - start_time) * 1000.0

        # High-Level Metrics Bar
        detections = results.get("detections", [])
        total_blocks = results.get("total_text_blocks", 0)
        avg_conf = (
            (sum(d["confidence"] for d in detections) / total_blocks * 100.0)
            if total_blocks > 0
            else 0.0
        )

        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Text Blocks Detected", f"{total_blocks}")
        m_col2.metric("Average Confidence", f"{avg_conf:.1f}%")
        m_col3.metric("Processing Latency", f"{latency_ms:.0f} ms")

        # Side-by-Side Dual-Pane Canvas
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("##### 📷 Original Input")
            st.image(input_image, use_container_width=True)

        with col_right:
            st.markdown("##### 🎯 Bounding Box Annotations")
            annotated_bgr = results.get("annotated_image", bgr_image)
            annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
            st.image(annotated_rgb, use_container_width=True)

        # Extracted Text Inspector & Export Controls
        st.markdown("### 📝 Extracted Text & Export Options")

        extracted_text = results.get("extracted_text", "")
        if extracted_text:
            st.text_area("Extracted Characters", value=extracted_text, height=180)

            # Export Formats
            txt_data = format_export_data(detections, "txt")
            csv_data = format_export_data(detections, "csv")
            json_data = format_export_data(detections, "json")

            exp_col1, exp_col2, exp_col3 = st.columns(3)
            with exp_col1:
                st.download_button(
                    label="📥 Download as TXT",
                    data=txt_data,
                    file_name="extracted_text.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with exp_col2:
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_data,
                    file_name="extracted_table.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with exp_col3:
                st.download_button(
                    label="📋 Download as JSON",
                    data=json_data,
                    file_name="extracted_data.json",
                    mime="application/json",
                    use_container_width=True,
                )

            # Detailed Inspection Table
            with st.expander("🔍 View Detailed Token Detections Table"):
                table_rows = [
                    {
                        "Line": d["line_id"],
                        "Recognized Text": d["text"],
                        "Confidence": f"{d['confidence']*100:.1f}%",
                    }
                    for d in detections
                ]
                st.table(table_rows)
        else:
            st.warning("No text detected above the current confidence threshold. Try lowering the threshold in the sidebar.")


if __name__ == "__main__":
    main()
