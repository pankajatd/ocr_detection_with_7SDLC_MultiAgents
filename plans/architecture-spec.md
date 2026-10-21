# Technical Architecture Specification
## Project: Universal Optical Character Recognition System (`ocr_detection`)
**Author:** Technical Architect Subagent  
**Status:** DRAFT FOR HITL GATE 2 REVIEW  
**Scope:** High-Level System Design & Technology Stack Selection  

---

## 1. System Overview & Architectural Approach

To satisfy the business and functional requirements defined in `plans/PRD.md`, the system is architected as a modular, high-performance visual processing application divided into two primary high-level tiers:

```
+-------------------------------------------------------------+
|                 PRESENTATION LAYER (Web UI)                 |
|   - Handles multi-format document uploads (.png, .jpg, .pdf)|
|   - Handles real-time camera snapshot capture               |
|   - Provides interactive confidence sensitivity sliders     |
|   - Renders side-by-side visual comparison canvas           |
|   - Provides 1-click export tools (TXT, CSV, JSON)          |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                 AI OCR INFERENCE ENGINE (Backend)           |
|   - Stage 1: Document Pre-processing (Denoise & Contrast)   |
|   - Stage 2: Text Localization (Finds text bounding boxes)  |
|   - Stage 3: Text Recognition (Transcribes characters)      |
|   - Stage 4: Annotation Renderer (Overlays boxes & scores)  |
+-------------------------------------------------------------+
```

---

## 2. Technology Stack Selection & Rationale

| System Layer | Selected Technology | Architectural Rationale |
| :--- | :--- | :--- |
| **Core Runtime** | Python 3.10+ | Industry standard for machine learning, computer vision, and rapid, robust application development. |
| **Computer Vision Engine** | OpenCV | Provides ultra-fast, CPU-optimized image decoding, adaptive contrast normalization (CLAHE), bilateral denoising, and geometric canvas drawing. |
| **AI Inference Model** | Deep Learning OCR (CRAFT + ResNet/CRNN) | A two-stage deep learning pipeline: CRAFT detects oriented text bounding boxes on vehicle plates, signs, and paper; CRNN recognizes characters with sequence modeling and high alphanumeric accuracy. |
| **Web UI Framework** | Streamlit | Enables building clean, interactive web applications directly in Python with built-in support for file drag-and-drop, sliders, and camera feeds. |
| **Automated Test Runner** | Pytest | Standard test runner for verifying image processing pipelines, character transcription fidelity, and edge-case resilience. |

---

## 3. High-Level System Components & Boundaries

### Component A: Web Presentation Layer
- **Responsibility**: Manages all user-facing interactions.
- **Boundaries**: Strictly handles user inputs, file uploads, display of annotated images, extracted text viewers, and download actions. Contains no AI recognition algorithms or image filtering logic.

### Component B: AI Detection & Inference Engine
- **Responsibility**: Ingests raw image matrices, enhances contrast, localizes text regions, and transcribes characters (including vehicle plates, receipts, printed docs, and signage).
- **Boundaries**: Pure analytical engine. Operates independently of the web framework so it can be tested in isolation, containerized, or reused in other interfaces.

### Component C: Annotation & Visualization Engine
- **Responsibility**: Combines recognition results with the original visual input.
- **Boundaries**: Applies color-coded bounding box overlays around localized text blocks, formats line-by-line transcription, and computes recognition statistics (total blocks, average confidence).

---

## 4. Non-Functional System Attributes

- **Hardware Efficiency**: Architected to execute efficiently on standard multi-core consumer and server CPUs without requiring expensive dedicated GPUs.
- **Modularity**: The AI engine is completely decoupled from the UI presentation layer to allow independent testing and future upgrades.
- **Privacy & Security**: All image processing executes strictly on-premise in memory. Zero external network calls or cloud API dependencies exist.
- **Isolation**: The internal development tools (`.agents/`) are completely decoupled from production distribution code.
