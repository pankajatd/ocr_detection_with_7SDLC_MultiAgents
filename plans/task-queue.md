# Task Queue & Low-Level Technical Specifications
## Project: Universal Optical Character Recognition System (`ocr_detection`)
**Author:** Tech Lead Subagent  
**Status:** DRAFT FOR HITL GATE 3 REVIEW  
**Input References:** `plans/PRD.md`, `plans/architecture-spec.md`  

---

## 1. Execution Strategy & Task Dependency Graph

To guarantee conflict-free, sequential development and prevent merge regressions, development is partitioned into distinct atomic tasks with strict file ownership boundaries:

```
[ Task 1: Package Manifest & Environment (requirements.txt, packages.txt) ]
                                   │
                                   ▼
[ Task 2: Utility, Pre-processing & Box Annotation Engine (src/utils.py) ]
                                   │
                                   ▼
[ Task 3: Core Deep Learning OCR Engine (src/ocr_engine.py) ]
                                   │
               ┌───────────────────┴───────────────────┐
               ▼                                       ▼
[ Task 4: Interactive Web Dashboard (src/app.py) ]  [ Task 5: Automated QA Suite & Datasets (tests/) ]
               │                                       │
               └───────────────────┬───────────────────┘
                                   ▼
[ Task 6: Defensive Security Audit (reports/security-audit.md) ]
                                   │
                                   ▼
[ Task 7: DevOps Containerization & Packaging (Dockerfile, compose, README.md) ]
```

---

## 2. Project File Layout & File Ownership Boundaries

```
ocr_detection/
├── requirements.txt            <-- Package manifest (Task 1)
├── packages.txt                <-- Linux system graphics libraries (Task 1)
├── src/
│   ├── utils.py                <-- Preprocessing, validation, drawing, and export (Task 2)
│   ├── ocr_engine.py           <-- Core AI Deep Learning OCR engine (Task 3)
│   └── app.py                  <-- Streamlit interactive web dashboard (Task 4)
├── tests/
│   ├── test_images/            <-- Real-world benchmark images (Task 5)
│   ├── test_utils.py           <-- Unit tests for preprocessing & utilities (Task 5)
│   └── test_ocr_engine.py      <-- Integration tests for OCR detection & accuracy (Task 5)
├── reports/
│   └── security-audit.md       <-- Defensive security review (Task 6)
├── Dockerfile                  # Production container definition (Task 7)
├── docker-compose.yml          # Single-command container deployment (Task 7)
└── README.md                   # System documentation & usage guide (Task 7)
```

---

## 3. Low-Level Function Contracts & Interfaces

The Software Engineer must implement these exact function signatures and data contracts:

### 3.1 Utility & Pre-Processing Engine (`src/utils.py`)
```python
def validate_image_bytes(file_bytes: bytes) -> bool:
    """Validates that uploaded raw bytes represent a readable, non-corrupt image format."""

def preprocess_document_image(image: np.ndarray) -> np.ndarray:
    """
    Applies computer vision pre-processing pipeline:
    1. CLAHE (Contrast Limited Adaptive Histogram Equalization) on L-channel to eliminate shadows/glare.
    2. Bilateral filtering to denoise background while preserving sharp character edge gradients.
    3. Auto-deskew estimation for text tilted up to 45 degrees.
    """

def draw_ocr_bounding_boxes(
    image: np.ndarray,
    detections: list,
    box_color: tuple = (0, 180, 255)
) -> np.ndarray:
    """
    Draws high-contrast bounding boxes around detected text blocks with adaptive
    background banners displaying text snippets and confidence percentages.
    """

def format_export_data(detections: list, format_type: str = "txt") -> str:
    """
    Serializes extracted detections into requested format:
    - 'txt': Plain text with preserved line breaks.
    - 'csv': Comma-separated table (Line_ID, Text, Confidence, Bounding_Box).
    - 'json': Hierarchical JSON representation.
    """
```

### 3.2 Core Deep Learning OCR Engine (`src/ocr_engine.py`)
```python
class OCREngineWrapper:
    """Unified wrapper supporting primary Deep Learning CRAFT/CRNN engine and fail-safe fallback."""
    def __init__(self, engine_type: str, engine_obj: any):
        self.engine_type = engine_type  # 'deep_learning' or 'geometric_fallback'
        self.engine_obj = engine_obj

def load_ocr_engine(languages: list = None) -> OCREngineWrapper:
    """Initializes and caches the Deep Learning OCR engine (English alphanumeric default)."""

def detect_and_extract_text(
    image: np.ndarray,
    engine: Optional[OCREngineWrapper] = None,
    confidence_threshold: float = 0.30
) -> dict:
    """
    Master coordination pipeline:
    1. Pre-processes image via src.utils.
    2. Executes CRAFT text localization and CRNN sequence recognition.
    3. Resolves vehicle plate alphanumeric ambiguities (e.g., 0 vs O, 1 vs I).
    4. Renders visual bounding boxes on image canvas.
    5. Returns structured results dictionary:
       {
           "annotated_image": np.ndarray,
           "total_text_blocks": int,
           "extracted_text": str,
           "detections": [
               {"line_id": int, "text": str, "confidence": float, "box": (x1, y1, x2, y2)}
           ]
       }
    """
```

---

## 4. Atomic Task Breakdown for Developers

### Task 1: Package Manifest & Environment Configuration
* **Assigned Role**: Software Engineer
* **Target Files**: `requirements.txt`, `packages.txt`
* **Deliverables**:
  - `requirements.txt`: `easyocr>=1.7.0`, `opencv-python-headless>=4.8.0,<4.11.0`, `numpy>=1.24.0,<2.0.0`, `Pillow>=10.0.0`, `streamlit>=1.28.0`, `pytest>=7.4.0`.
  - `packages.txt`: `libgl1`, `libglib2.0-0` (ensures zero missing shared library errors on Streamlit Cloud Linux).
* **Required Unit Tests**: Verification that imports load cleanly in a fresh environment without binary ABI conflicts.
* **Definition of Done**: Packages install with 0 errors; `python -c "import cv2, easyocr, streamlit"` succeeds.

---

### Task 2: Utility, Pre-Processing & Box Annotation Engine
* **Assigned Role**: Software Engineer
* **Target File**: `src/utils.py`
* **Deliverables**:
  - `validate_image_bytes()` using Pillow byte verification.
  - `preprocess_document_image()` implementing CLAHE contrast normalization, bilateral denoising, and deskewing.
  - `draw_ocr_bounding_boxes()` with adaptive font scaling, boundary-clamping (never clipping margins), and high-contrast bounding boxes.
  - `format_export_data()` generating clean TXT, CSV, and JSON outputs.
* **Required Unit Tests**: `tests/test_utils.py` verifying valid/corrupt bytes, CLAHE output dimensions, export formatting, and box boundary safety.
* **Definition of Done**: All unit tests in `tests/test_utils.py` pass with 100% assertions.

---

### Task 3: Core Deep Learning OCR Engine
* **Assigned Role**: Software Engineer
* **Target File**: `src/ocr_engine.py`
* **Deliverables**:
  - Model initialization wrapper supporting deep learning CRAFT/CRNN with lightweight fallback.
  - Text localization and character sequence recognition.
  - Contextual alphanumeric plate disambiguation for Vehicle License Plates (`0` vs `O`, `1` vs `I`).
  - Aggregation of structured detections, average confidence, and full extracted text.
* **Required Unit Tests**: `tests/test_ocr_engine.py` testing model loading, synthetic text ROIs, and vehicle plate character recognition.
* **Definition of Done**: Accepts an image array and returns the complete structured schema with accurate text and bounding coordinates.

---

### Task 4: Interactive Streamlit Web Dashboard
* **Assigned Role**: Software Engineer
* **Target File**: `src/app.py`
* **Deliverables**:
  - Header with system status indicator (Deep Learning OCR Active).
  - Tab 1: **1-Click Pre-Loaded Benchmark Demos** (Vehicle Number Plate, Store Receipt, Printed Document, Skewed Sign, Handwritten Note).
  - Tab 2: **Custom File Uploader** (Drag-and-drop `.jpg`, `.png`, `.pdf`).
  - Tab 3: **Live Webcam Capture** (`st.camera_input`).
  - Interactive confidence slider ($0.20\text{--}0.95$).
  - Dual-Pane Side-by-Side Canvas (Original Image vs Annotated Bounding Box Result).
  - Extracted Text Inspector with 1-click **Download as TXT**, **Download as CSV**, **Download as JSON**, and **Copy to Clipboard**.
* **Required Verification**: Visual verification in browser at `http://localhost:8501`.
* **Definition of Done**: App runs error-free, switching between demo samples and custom uploads smoothly.

---

### Task 5: Automated QA Test Suite & Benchmark Datasets
* **Assigned Role**: QA / Test Engineer
* **Target Files**: `tests/test_images/`, `tests/test_utils.py`, `tests/test_ocr_engine.py`
* **Deliverables**:
  - Real-world benchmark images covering:
    1. *Vehicle License Plate / Car Number Plate*
    2. *Printed Business Document*
    3. *Thermal Store Receipt*
    4. *Tilted / Skewed Signboard*
    5. *Blank / Non-Text Image*
  - Comprehensive automated `pytest` suite testing all happy, negative, and edge cases.
  - Visual output verification artifacts saved to `output/`.
* **Definition of Done**: Running `pytest -v tests/` reports 100% passing tests.

---

### Task 6: Defensive Security Audit
* **Assigned Role**: Security Auditor
* **Target File**: `reports/security-audit.md`
* **Deliverables**:
  - Memory buffer inspection (ensuring no temporary user files leak to disk).
  - Upload payload sanitization (MIME format verification, 200MB DoS defense).
  - Zero hardcoded secrets, keys, or external network calls verified.
* **Definition of Done**: Formal report generated with verdict `SAFE TO COMMIT`.

---

### Task 7: DevOps Containerization & Packaging
* **Assigned Role**: DevOps & Release Engineer
* **Target Files**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.gitignore`, `README.md`
* **Deliverables**:
  - Production `Dockerfile` on `python:3.10-slim` with system graphics libraries.
  - `docker-compose.yml` for single-command launch (`docker-compose up -d --build`).
  - `.dockerignore` and `.gitignore` isolating `.agents/` and internal plans.
  - Customer-facing `README.md` with quick-start guides for Python, Cloud, and Docker.
* **Definition of Done**: Container builds cleanly; `README.md` is complete.

---

## 5. Quality Gates & Definition of Done

```
[ HITL Gate 3: Task Queue Approved ] 
                 │
                 ▼
[ Phase 4: Software Engineer Implements Tasks 1, 2, 3, 4 ]
                 │
                 ▼
[ Phase 5: QA Engineer Verifies Task 5 (100% pytest pass rate) ]
                 │
                 ▼
[ Phase 6: Security Auditor Certifies Task 6 (SAFE TO COMMIT) ]
                 │
                 ▼
[ Phase 7: DevOps Engineer Packages Task 7 (Docker & README) ]
                 │
                 ▼
[ Final HITL Sign-Off & Live Customer Handover ]
```

---
*End of Task Queue — Awaiting Human-in-the-Loop (HITL) Gate 3 Approval.*
