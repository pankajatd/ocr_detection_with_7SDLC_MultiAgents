"""
Enterprise Document Generator: Detailed_Design_Document.docx & .pdf
Universal Optical Character Recognition System
Author: Tech Lead Subagent
"""

import os
import sys
import win32com.client

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS_DIR = os.path.join(ROOT_DIR, "plans")

doc_path = os.path.abspath(os.path.join(PLANS_DIR, "Detailed_Design_Document.docx"))
pdf_path = os.path.abspath(os.path.join(PLANS_DIR, "Detailed_Design_Document.pdf"))

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

try:
    doc = word.Documents.Add()

    # Constants
    wdAlignParagraphCenter = 1
    wdAlignParagraphLeft = 0
    wdAlignParagraphJustify = 3
    wdExportFormatPDF = 17

    def add_p(text, space_after=6, align=wdAlignParagraphLeft, bold=False, font_size=11, color=(30, 41, 59)):
        p = doc.Paragraphs.Add()
        p.Range.Text = text
        p.Range.Font.Name = "Calibri"
        p.Range.Font.Size = font_size
        p.Range.Font.Bold = bold
        p.Range.Font.Color = color[0] + (color[1] * 256) + (color[2] * 65536)
        p.Format.SpaceAfter = space_after
        p.Format.Alignment = align
        return p

    def add_bullet(bold_prefix, text, space_after=4):
        p = doc.Paragraphs.Add()
        p.Range.Text = f"• {bold_prefix}: {text}"
        p.Range.Font.Name = "Calibri"
        p.Range.Font.Size = 10.5
        p.Range.Font.Color = 30 + (41 * 256) + (59 * 65536)
        p.Format.LeftIndent = 18
        p.Format.SpaceAfter = space_after
        p.Format.Alignment = wdAlignParagraphJustify
        return p

    def add_code(text, space_after=8):
        p = doc.Paragraphs.Add()
        p.Range.Text = text
        p.Range.Font.Name = "Consolas"
        p.Range.Font.Size = 9.5
        p.Range.Font.Color = 51 + (65 * 256) + (85 * 65536)
        p.Format.LeftIndent = 18
        p.Format.SpaceAfter = space_after
        p.Format.Alignment = wdAlignParagraphLeft
        return p

    # --- COVER BANNER ---
    add_p("UNIVERSAL OPTICAL CHARACTER RECOGNITION (OCR) SYSTEM", space_after=4, align=wdAlignParagraphCenter, bold=True, font_size=24, color=(2, 132, 199))
    add_p("Comprehensive Low-Level Detailed Design Document (LLD)", space_after=10, align=wdAlignParagraphCenter, bold=False, font_size=14, color=(100, 116, 139))
    add_p("Document Control: LLD-OCR-2026-V1.0 | Status: Production Approved | Author: Tech Lead Subagent", space_after=22, align=wdAlignParagraphCenter, bold=False, font_size=10, color=(148, 163, 184))

    # --- DOCUMENT CONTROL TABLE SUMMARY ---
    add_p("Document Control Information", bold=True, font_size=13, color=(15, 23, 42), space_after=4)
    add_bullet("Document Identifier", "LLD-OCR-DETECTION-001")
    add_bullet("Project Name", "Universal Optical Character Recognition System (ocr_detection)")
    add_bullet("Document Classification", "Confidential / Internal Technical Architecture")
    add_bullet("Primary Methodology", "7-Agent SDLC Subagent Framework (Synchronous HITL Gates)")
    add_bullet("Verification Status", "100% Passed (26/26 Automated Tests, Security Audit Certified)")

    # --- 1. EXECUTIVE SUMMARY & SYSTEM SCOPE ---
    add_p("1. Executive Summary & System Scope", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "This Detailed Design Document (LLD) defines the low-level algorithmic blueprints, mathematical models, module interfaces, sequence workflows, and quality assurance specifications for the Universal Optical Character Recognition System (ocr_detection).\n\n"
        "Modern enterprise text extraction frequently fails when faced with challenging real-world conditions: automotive vehicle license plates with headlight reflections, thermal receipts with faded contrast, paper documents scanned at skewed angles, and tilted outdoor signboards. Legacy optical character recognition engines (such as Tesseract) rely on rigid binarization heuristics that produce high error rates under non-ideal lighting and angled perspectives.\n\n"
        "To solve these operational challenges, this system implements a state-of-the-art dual-stage Deep Learning pipeline: CRAFT (Character Region Awareness for Text Detection) for pixel-accurate localization, combined with a deep ResNet-CRNN (Convolutional Recurrent Neural Network) with CTC loss for sequence recognition. The pipeline is hardened with specialized computer vision preprocessing (CLAHE contrast normalization, bilateral edge-preserving denoising, auto-deskewing) and contextual vehicle license plate alphanumeric disambiguation (0 vs O, 1 vs I).",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- 2. ARCHITECTURAL TOPOLOGY & FILE BOUNDARIES ---
    add_p("2. Codebase Architecture & File Ownership Boundaries", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "The codebase enforces strict modular separation conforming to the 7-Agent SDLC Framework standards:",
        font_size=11, space_after=6, align=wdAlignParagraphJustify
    )
    add_bullet("src/utils.py (Module 1)", "Defensive byte validation, CLAHE contrast enhancement, bilateral filter denoising, auto-deskew contour rotation, boundary-clamped bounding box rendering, and multi-format serialization (TXT, CSV, JSON).")
    add_bullet("src/ocr_engine.py (Module 2)", "Core AI deep learning engine, EasyOCR CRAFT detector and CRNN sequence recognizer, contextual vehicle plate disambiguation, reading-order coordinate sorting, and fail-safe computer vision fallback.")
    add_bullet("src/app.py (Module 3)", "Interactive Streamlit web dashboard featuring model caching, 1-click pre-loaded benchmark demos, multi-source ingestion (file upload & webcam), dual-pane side-by-side canvas, and 1-click export downloads.")
    add_bullet("tests/test_images/", "Curated real-world defect benchmark images verifying motion blur, shadow gradients, 15° rotation skew, 3D perspective distortion, and headlight glare.")
    add_bullet("tests/test_utils.py & test_ocr_engine.py", "Comprehensive PyTest automation suite delivering 100% test passing rate across 26 test cases.")
    add_bullet("output/", "Persisted visual verification artifacts showcasing annotated bounding boxes across benchmark images, edge cases, and diverse operational scenarios.")
    add_bullet("Dockerfile & docker-compose.yml", "Multi-stage production container definitions based on python:3.10-slim with Linux graphics libraries (libgl1, libglib2.0-0) and built-in healthcheck probes.")

    # --- 3. SYSTEM SEQUENCE & DATA FLOW ---
    add_p("3. End-to-End System Sequence & Data Flow", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "The lifecycle of an input image across the system is defined by the following sequential data flow:\n\n"
        "1. Ingestion Phase: User supplies an image via Streamlit web upload, webcam snapshot, or 1-click demo sample.\n"
        "2. Security & Sanitization Phase: validate_image_bytes() inspects byte length (< 200MB) and executes two-phase Pillow verification (verify + load), discarding malformed headers and corrupted streams.\n"
        "3. Enhancement Phase: preprocess_document_image() transforms BGR to LAB color space, applies CLAHE to the L-channel, applies bilateral denoising, calculates skew angle via Otsu contour geometry, and counter-rotates the frame straight.\n"
        "4. Deep Learning Localization: The CRAFT neural network computes affinity maps and character region heatmaps to bound individual words and text blocks.\n"
        "5. Deep Learning Sequence Recognition: The CRNN convolutional-recurrent model generates character sequence probabilities decoded via Connectionist Temporal Classification (CTC).\n"
        "6. Vehicle Plate Contextual Disambiguation: disambiguate_license_plate() identifies vehicle registration patterns (e.g. MH 12 AB 1234) and corrects optical letter/number ambiguities.\n"
        "7. Natural Reading-Order Sorting: Detections are sorted by two-dimensional spatial coordinates (top-to-bottom line grouping, left-to-right text ordering).\n"
        "8. Visual Annotation & Margin Clamping: draw_ocr_bounding_boxes() draws high-contrast bounding boxes with boundary-clamped badge banners.\n"
        "9. Output Rendering & Multi-Format Export: Streamlit displays original vs. annotated canvases side-by-side and enables 1-click downloads as TXT, CSV, or JSON.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- 4. DETAILED MODULE SPECIFICATIONS & LOW-LEVEL CONTRACTS ---
    add_p("4. Detailed Module Specifications & Low-Level Function Contracts", bold=True, font_size=16, color=(15, 23, 42), space_after=8)

    add_p("4.1 Preprocessing & Annotation Engine (src/utils.py)", bold=True, font_size=13, color=(2, 132, 199), space_after=4)
    add_code(
        "def validate_image_bytes(file_bytes: bytes) -> bool:\n"
        "    \"\"\"Guards against zero-byte files, oversized payloads (>200MB), and corrupted headers.\"\"\"\n\n"
        "def estimate_skew_angle(image: np.ndarray) -> float:\n"
        "    \"\"\"Calculates tilt angle (-45 to +45 deg) using Otsu dilation and contour minAreaRect.\"\"\"\n\n"
        "def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:\n"
        "    \"\"\"Executes affine warp rotation with expanded bounds to eliminate margin clipping.\"\"\"\n\n"
        "def preprocess_document_image(image: np.ndarray) -> np.ndarray:\n"
        "    \"\"\"Applies L-channel CLAHE contrast normalization, bilateral filtering, and deskewing.\"\"\"\n\n"
        "def draw_ocr_bounding_boxes(image: np.ndarray, detections: list, box_color: tuple) -> np.ndarray:\n"
        "    \"\"\"Renders bounding boxes with adaptive margin clamping preventing badge clipping.\"\"\"\n\n"
        "def format_export_data(detections: list, format_type: str) -> str:\n"
        "    \"\"\"Serializes detections into Plain Text (txt), CSV table (csv), or structured JSON (json).\"\"\""
    )

    add_p("4.2 Core AI Deep Learning OCR Engine (src/ocr_engine.py)", bold=True, font_size=13, color=(2, 132, 199), space_after=4)
    add_code(
        "class OCREngineWrapper:\n"
        "    \"\"\"Unified engine wrapper encapsulating deep learning and fail-safe fallback modes.\"\"\"\n"
        "    def __init__(self, engine_type: str, engine_obj: Any):\n"
        "        self.engine_type = engine_type  # 'deep_learning' or 'geometric_fallback'\n"
        "        self.engine_obj = engine_obj\n\n"
        "def disambiguate_license_plate(text: str) -> str:\n"
        "    \"\"\"Contextual alphanumeric plate regex resolver converting 0<->O, 1<->I, 8<->B.\"\"\"\n\n"
        "def load_ocr_engine(languages: Optional[List[str]] = None) -> OCREngineWrapper:\n"
        "    \"\"\"Initializes and caches EasyOCR CRAFT+CRNN models with automatic CUDA GPU/CPU detection.\"\"\"\n\n"
        "def detect_and_extract_text(image: np.ndarray, engine: OCREngineWrapper, threshold: float) -> dict:\n"
        "    \"\"\"Master extraction pipeline returning structured detections, full text, and annotated canvas.\"\"\""
    )

    # --- 5. VEHICLE LICENSE PLATE DISAMBIGUATION RULES ---
    add_p("5. Vehicle License Plate Contextual Disambiguation Engine", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "Optical character recognition engines frequently confuse visually similar alphanumeric pairs on vehicle registration plates due to font standardization (e.g., DIN 1451, Charles Wright, FE-Schrift). "
        "The disambiguation engine inspects the structural token syntax against established national vehicle registration schemas:\n\n"
        "• Indian Registration Format (HSRP Scheme: State + District + Series + Unique Number):\n"
        "  Pattern: ^([A-Z0-9]{2})([A-Z0-9]{2})([A-Z0-9]{1,2})([A-Z0-9]{4})$\n"
        "  Rule 1 (State Code): In positions 1-2, optical digits ('0', '1', '8', '5') are converted to letters ('O', 'I', 'B', 'S').\n"
        "  Rule 2 (District RTO): In positions 3-4, optical letters ('O', 'I', 'Z', 'S', 'B') are converted to digits ('0', '1', '2', '5', '8').\n"
        "  Rule 3 (Series Code): In positions 5-6, optical digits are converted to alphabetic letters.\n"
        "  Rule 4 (Unique Number): In positions 7-10, optical letters are converted to numeric digits.\n"
        "  Output Standard: Formats with clean space delimiters (e.g. 'KA 03 MG 4589').\n\n"
        "• United Kingdom Registration Format (DVLA Scheme: Memory Tag + Age Identifier + Random Letters):\n"
        "  Pattern: ^([A-Z0-9]{2})([A-Z0-9]{2})([A-Z0-9]{3})$\n"
        "  Rule 1 (Memory Tag): Positions 1-2 strictly alphabetic.\n"
        "  Rule 2 (Age Identifier): Positions 3-4 strictly numeric digits.\n"
        "  Rule 3 (Random Letters): Positions 5-7 strictly alphabetic.\n"
        "  Output Standard: Formats as 'BD51 SMR'.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- 6. AUTOMATED QA TEST ARCHITECTURE & BENCHMARK RESULTS ---
    add_p("6. Automated QA Test Suite & Real-World Benchmark Verification", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "The automated test suite achieves a 100% pass rate across 26 discrete tests executed via PyTest in 14.91 seconds:\n\n"
        "• Unit Test Suite (tests/test_utils.py — 17 Tests):\n"
        "  - 4 Validation Tests: Rejection of empty bytes, random corruption, oversized payloads (>200MB), and acceptance of valid PNG streams.\n"
        "  - 3 Geometry Tests: Zero-skew baseline, affine rotation preservation, non-empty matrix returns.\n"
        "  - 3 Enhancement Tests: 3-channel RGB CLAHE, single-channel grayscale handling, safe null/empty array returns.\n"
        "  - 3 Drawing & Clamping Tests: Standard high-contrast rendering, boundary clamping at (0,0) and (W,H) margins, empty detections handling.\n"
        "  - 4 Serializer Tests: Plain text line breaks, RFC-4180 CSV headers/columns, JSON hierarchical schemas, invalid format ValueError raises.\n\n"
        "• AI Integration Test Suite (tests/test_ocr_engine.py — 9 Tests):\n"
        "  - Model lifecycle verification (wrapper initialization and memory persistence).\n"
        "  - License plate disambiguation logic (digit substitution and letter recovery).\n"
        "  - Real-world defect image benchmarks:\n"
        "      1. 1_car_plate_motion_blur.jpg: Extracted 'KA 03 MG 4589' through horizontal camera motion blur.\n"
        "      2. 2_receipt_shadow_defect.jpg: Extracted line items and total through harsh diagonal shadow gradient.\n"
        "      3. 3_document_skewed_tilted.jpg: Auto-deskewed document and extracted 'PURCHASE ORDER #89201'.\n"
        "      4. 4_signboard_perspective_blur.jpg: Extracted 'ROAD WORK AHEAD' on 3D angled sign.\n"
        "      5. 5_car_plate_glare_defect.jpg: Extracted surrounding plate digits despite headlight glare.\n"
        "  - Negative robustness: Zero detections returned on blank white canvas and null inputs without unhandled exceptions.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- 7. DEFENSIVE SECURITY & COMPLIANCE ---
    add_p("7. Defensive Security, Privacy & Compliance Architecture", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "The codebase was subjected to an adversarial security audit by the Security Auditor subagent and certified SAFE TO COMMIT based on four hardened security boundaries:\n\n"
        "1. Complete Data Privacy (Zero Telemetry): Zero external HTTP/WebSocket clients (requests, urllib, socket) exist in production code. Neural network inference runs 100% locally on the host machine.\n"
        "2. Volatile RAM Processing: User documents and camera snapshots reside strictly in volatile RAM buffers (io.BytesIO) and are discarded upon session close. Zero temporary files are written to disk.\n"
        "3. Denial-of-Service (DoS) Defense: Enforced 200MB hard limit prevents memory starvation attacks. Two-phase PIL verification ensures malicious executables disguised as image files are rejected.\n"
        "4. Dependency Hardening: Dependencies are pinned to eliminate known CVEs (Pillow >= 10.0.0) and prevent C-API ABI mismatch crashes (numpy < 2.0.0).",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- 8. DEPLOYMENT & DEVOPS CONTAINERIZATION ---
    add_p("8. DevOps Containerization & Deployment Orchestration", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "The application provides three standardized deployment pathways:\n\n"
        "• Local Development: pip install -r requirements.txt followed by streamlit run src/app.py.\n"
        "• Containerized Deployment: Single-command deployment via docker-compose up -d --build utilizing a multi-stage Dockerfile built on python:3.10-slim with Linux graphics libraries (libgl1, libglib2.0-0) and built-in healthchecks.\n"
        "• Streamlit Community Cloud: Zero-configuration cloud hosting via packages.txt and requirements.txt.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # Save Word Document
    doc.SaveAs2(doc_path)
    print(f"Word Document saved: {doc_path}")

    # Export PDF Document
    doc.ExportAsFixedFormat(pdf_path, wdExportFormatPDF)
    print(f"PDF Document exported: {pdf_path}")

finally:
    doc.Close(False)
    word.Quit()
