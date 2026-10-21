"""
Enterprise Document Generator: Detailed_Design_Document.docx & .pdf
Exact 1-to-1 Parity with Face Mask Detection Template
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

    def add_p(text, space_after=5, align=wdAlignParagraphLeft, bold=False, font_size=11, color=(30, 41, 59)):
        p = doc.Paragraphs.Add()
        p.Range.Text = text
        p.Range.Font.Name = "Calibri"
        p.Range.Font.Size = font_size
        p.Range.Font.Bold = bold
        p.Range.Font.Color = color[0] + (color[1] * 256) + (color[2] * 65536)
        p.Format.SpaceAfter = space_after
        p.Format.Alignment = align
        return p

    def add_table(rows_data, col_widths=None):
        table = doc.Tables.Add(doc.Paragraphs.Add().Range, len(rows_data), len(rows_data[0]))
        table.Borders.Enable = True
        for r_idx, row in enumerate(rows_data):
            for c_idx, val in enumerate(row):
                cell = table.Cell(r_idx + 1, c_idx + 1)
                cell.Range.Text = str(val)
                cell.Range.Font.Name = "Calibri"
                cell.Range.Font.Size = 9.5
                if r_idx == 0:
                    cell.Range.Font.Bold = True
                    cell.Range.Font.Color = 255 + (255 * 256) + (255 * 65536)
                    cell.Shading.BackgroundPatternColor = 2 + (132 * 256) + (199 * 65536)  # Blue Header
                else:
                    cell.Range.Font.Color = 30 + (41 * 256) + (59 * 65536)
        if col_widths:
            for c_idx, w in enumerate(col_widths):
                table.Columns(c_idx + 1).Width = w
        doc.Paragraphs.Add()

    # --- TITLE ---
    add_p("Detailed Design Document (Low-Level Design / LLD)", space_after=2, align=wdAlignParagraphCenter, bold=True, font_size=22, color=(2, 132, 199))
    add_p("Project: Universal Optical Character Recognition System (ocr_detection)  Author: Tech Lead Subagent • Status: Approved Engineering Design", space_after=8, align=wdAlignParagraphCenter, bold=False, font_size=11, color=(100, 116, 139))
    add_p("Purpose: This Detailed Design Document defines the internal data flow, component sequence, module-level function algorithms, input/output schemas, error-handling mechanisms, and automated test design for the 4 primary code files before implementation begins.", space_after=16, align=wdAlignParagraphJustify, font_size=10.5, color=(71, 85, 105))

    # --- SECTION 1 ---
    add_p("1. Core Code Architecture (The 4 Files)", bold=True, font_size=14, color=(15, 23, 42), space_after=6)
    add_p("The codebase is strictly structured across 4 primary code files:", space_after=4)
    arch_tree = (
        "ocr_detection/\n"
        "├── requirements.txt            <-- Package dependencies\n"
        "│\n"
        "├── src/\n"
        "│   ├── utils.py                <-- Module 1: Helper tools (validation, CLAHE, deskew & box drawing)\n"
        "│   ├── ocr_engine.py           <-- Module 2: Core AI engine (CRAFT text detection & CRNN character recognition)\n"
        "│   └── app.py                  <-- Module 3: Streamlit interactive web dashboard\n"
        "│\n"
        "└── tests/\n"
        "    ├── test_images/            <-- Sample verification benchmark photos (plates, receipts, documents)\n"
        "    └── test_ocr_engine.py      <-- Module 4: Automated pytest test suite"
    )
    p_code = add_p(arch_tree, space_after=14, font_size=9.5, color=(51, 65, 85))
    p_code.Range.Font.Name = "Consolas"

    # --- SECTION 2 ---
    add_p("2. End-to-End System Sequence & Data Flow", bold=True, font_size=14, color=(15, 23, 42), space_after=6)
    add_p("The diagram below illustrates the exact runtime flow across all modules:", space_after=4)
    seq_diag = (
        "User (Browser)          src/app.py            src/utils.py             src/ocr_engine.py\n"
        "     |                      |                      |                          |\n"
        "     |--- 1. Upload file -->|                      |                          |\n"
        "     |                      |--- 2. Validate bytes>|                          |\n"
        "     |                      |<-- 3. True / False --|                          |\n"
        "     |                      |                                                 |\n"
        "     |                      |--- 4. Convert to BGR Matrix                     |\n"
        "     |                      |                                                 |\n"
        "     |                      |--- 5. detect_and_extract_text(image, thresh)--->|\n"
        "     |                      |                      |                          |\n"
        "     |                      |                      |<-- a. preprocess_image --|\n"
        "     |                      |                      |       (CLAHE, bilateral, |\n"
        "     |                      |                      |        auto-deskew)      |\n"
        "     |                      |                      |--- b. clean_image ------>|\n"
        "     |                      |                                                 |-- c. CRAFT text detector\n"
        "     |                      |                                                 |-- d. CRNN sequence recognizer\n"
        "     |                      |                                                 |-- e. disambiguate_license_plate\n"
        "     |                      |                                                 |-- f. sort reading order\n"
        "     |                      |                      |<-- g. draw_boxes --------|\n"
        "     |                      |                      |       (boundary clamped) |\n"
        "     |                      |                      |--- h. annotated_image -->|\n"
        "     |                      |                                                 |\n"
        "     |                      |<-- 6. Returns structured results dict ----------|\n"
        "     |                      |       {annotated_image, total_text_blocks, ...} |\n"
        "     |                      |                                                 |\n"
        "     |                      |--- 7. render_metrics(total, confidence, latency)|\n"
        "     |                      |--- 8. format_export_data(detections, 'csv')     |\n"
        "     |<-- 9. Display image -|                                                 |\n"
        "     |    & export buttons  |"
    )
    p_seq = add_p(seq_diag, space_after=14, font_size=8.5, color=(51, 65, 85))
    p_seq.Range.Font.Name = "Consolas"

    # --- SECTION 3 ---
    add_p("3. Module-by-Module Detailed Specifications", bold=True, font_size=14, color=(15, 23, 42), space_after=8)

    add_p("Module 1: src/utils.py (Validation, Enhancement & Drawing Engine)", bold=True, font_size=12, color=(2, 132, 199), space_after=4)
    add_p("1.1 validate_image_bytes(file_bytes: bytes) -> bool", bold=True, font_size=11, space_after=2)
    add_p("Purpose: Verifies that uploaded raw bytes form a valid, uncorrupt image file.\nAlgorithm: Checks byte length > 0 and <= 200MB (DoS defense), verifies format is in ['JPEG', 'JPG', 'PNG', 'BMP'] using PIL, and calls image.verify() and image.load(). Catches all exceptions to return False safely without crashing.", space_after=6)

    add_p("1.2 preprocess_document_image(image: np.ndarray) -> np.ndarray", bold=True, font_size=11, space_after=2)
    add_p("Purpose: Normalizes lighting, eliminates vehicle headlight glare, removes paper shadows, and rotates skewed documents horizontally.\nAlgorithm:\n  1. CLAHE: Converts image to LAB color space, applies CLAHE (clipLimit=2.0, tileGridSize=(8, 8)) on L-channel to balance contrast, merges back to BGR.\n  2. Bilateral Filtering: Denoises background paper grain while preserving sharp character edge gradients (d=5, sigmaColor=50, sigmaSpace=50).\n  3. Auto-Deskew: Calculates contour minAreaRect tilt angle and counter-rotates image via affine matrix with white padding.", space_after=6)

    add_p("1.3 draw_ocr_bounding_boxes(image: np.ndarray, detections: list, box_color: tuple) -> np.ndarray", bold=True, font_size=11, space_after=2)
    add_p("Purpose: Draws high-contrast bounding boxes around detected text blocks with adaptive background banners displaying text snippets and confidence percentages.\nBoundary Clamping Rule: Clamps badge coordinates (max(0, min(dim, val))) so text banners are never cut off at image margins.", space_after=6)

    add_p("1.4 format_export_data(detections: list, format_type: str = 'txt') -> str", bold=True, font_size=11, space_after=2)
    add_p("Purpose: Serializes extracted detections into plain text (.txt), CSV spreadsheet table (.csv), or structured JSON string (.json).", space_after=10)

    add_p("Module 2: src/ocr_engine.py (AI CRAFT Localization & Sequence Recognition)", bold=True, font_size=12, color=(2, 132, 199), space_after=4)
    add_p("2.1 load_ocr_engine(languages: list = None) -> OCREngineWrapper", bold=True, font_size=11, space_after=2)
    add_p("Purpose: Initializes the CRAFT text detection and CRNN sequence recognition model weights into memory.\nImplementation Strategy: Automatically detects whether an NVIDIA CUDA GPU is available (uses GPU if present; runs smoothly on CPU otherwise).", space_after=6)

    add_p("2.2 disambiguate_license_plate(text: str) -> str", bold=True, font_size=11, space_after=2)
    add_p("Purpose: Solves classic alphanumeric OCR confusion on vehicle license plates.\nAlgorithm: Matches tokens against national vehicle registration schemas (e.g. Indian HSRP: 2 State letters + 2 District digits + 1-2 Series letters + 4 Unique digits). Converts optical numbers to letters in letter slots and letters to digits in numeric slots (0 vs O, 1 vs I, 8 vs B).", space_after=6)

    add_p("2.3 detect_and_extract_text(image: np.ndarray, confidence_threshold: float = 0.30) -> dict", bold=True, font_size=11, space_after=2)
    add_p("Purpose: The Master Brain coordinator function that processes a single image frame end-to-end and packages all results into a clean dictionary.", space_after=4)

    add_p("A. What Goes In (Inputs):", bold=True, font_size=10.5, space_after=2)
    add_p("1. image: np.ndarray → The uploaded photo represented as a pixel matrix.\n2. confidence_threshold: float = 0.30 → Sensitivity filter (e.g. 30% confidence threshold).", space_after=4)

    add_p("B. What Happens Inside (4-Step Sequential Pipeline):", bold=True, font_size=10.5, space_after=2)
    add_p("Step 1 (Preprocess & Deskew): Invokes preprocess_document_image() to normalize contrast, denoise, and straighten tilt.\nStep 2 (Localize & Recognize Characters): Runs CRAFT text detector to locate character regions, then runs CRNN deep sequence model to read words.\nStep 3 (Disambiguate & Sort): Applies disambiguate_license_plate() to correct vehicle plate numbers, and sorts text blocks in natural reading order (top-to-bottom, left-to-right).\nStep 4 (Paint Annotations): Calls draw_ocr_bounding_boxes() from src/utils.py to paint high-contrast bounding boxes and badges on the canvas.", space_after=4)

    add_p("C. What Comes Out (Output Dictionary Schema):", bold=True, font_size=10.5, space_after=2)
    schema_code = (
        "{\n"
        "    # 1. The image array with the bounding boxes and text badges painted on it\n"
        "    \"annotated_image\": np.ndarray,\n"
        "\n"
        "    # 2. Total number of text blocks found in the photo (e.g., 6)\n"
        "    \"total_text_blocks\": 6,\n"
        "\n"
        "    # 3. Complete extracted plain text string\n"
        "    \"extracted_text\": \"PURCHASE ORDER #89201\\nVendor: Global Logistical Supplies\\n...\",\n"
        "\n"
        "    # 4. Detailed line-by-line detections list\n"
        "    \"detections\": [\n"
        "        {\n"
        "            \"line_id\": 1,\n"
        "            \"text\": \"PURCHASE ORDER #89201\",\n"
        "            \"confidence\": 0.892,\n"
        "            \"box\": [[40, 70], [450, 70], [450, 110], [40, 110]]\n"
        "        },\n"
        "        {\n"
        "            \"line_id\": 2,\n"
        "            \"text\": \"Vendor: Global Logistical Supplies\",\n"
        "            \"confidence\": 0.704,\n"
        "            \"box\": [[40, 120], [380, 120], [380, 155], [40, 155]]\n"
        "        }\n"
        "    ]\n"
        "}"
    )
    p_schema = add_p(schema_code, space_after=6, font_size=9, color=(51, 65, 85))
    p_schema.Range.Font.Name = "Consolas"

    add_p("D. How the Web Dashboard (src/app.py) Consumes This Output:", bold=True, font_size=10.5, space_after=2)
    add_p("• Takes 'annotated_image' → displays side-by-side with original input in the right column.\n• Takes 'total_text_blocks' → displays on Metric Card 1: 'Text Blocks Detected: 6'.\n• Calculates average confidence → displays on Metric Card 2: 'Average Confidence: 84.5%'.\n• Measures processing latency → displays on Metric Card 3: 'Processing Latency: 640 ms'.\n• Takes 'detections' → populates the Extracted Characters text box and feeds 1-click Download buttons (TXT, CSV, JSON).", space_after=10)

    add_p("Module 3: src/app.py (Streamlit Interactive Web Dashboard)", bold=True, font_size=12, color=(2, 132, 199), space_after=4)
    add_p("3.1 Layout & State Management\n• Page Setup: st.set_page_config(page_title='Universal OCR & Plate Detection System', layout='wide').\n• Sidebar Controls:\n  - App Mode Selection: Tabs between 1-Click Benchmark Demos, Custom File Upload, and Live Camera Snapshot.\n  - Confidence Slider: st.sidebar.slider('Detection Confidence Threshold', 0.10, 0.95, 0.30, 0.05).\n  - Engine Status Badge: Displays 🟢 AI Engine: Deep Learning (CRAFT + CRNN).\n  - Privacy Pledge: 100% On-Premise Privacy badge.\n\n3.2 Photo Upload Workflow\n1. User drops file into st.file_uploader(type=['jpg', 'jpeg', 'png', 'bmp']).\n2. Calls validate_image_bytes(bytes). If invalid, displays clear warning message.\n3. Decodes image and invokes detect_and_extract_text(image, confidence_threshold).\n4. Renders summary metrics via st.columns(3): Text Blocks Detected, Average Confidence, Latency.\n5. Displays original vs. annotated images side-by-side and provides 1-Click Download buttons for TXT, CSV, and JSON.\n\n3.3 Live Camera Workflow\n1. Activates st.camera_input('Capture snapshot from camera').\n2. Automatically runs OCR pipeline on snapshot frame and displays instantaneous text extraction and bounding boxes.\n\n3.4 Launch Command:\nstreamlit run src/app.py", space_after=10)

    add_p("Module 4: tests/test_ocr_engine.py (Automated QA Test Suite)", bold=True, font_size=12, color=(2, 132, 199), space_after=4)
    add_p("4.1 Purpose of the Test Suite\nThe test suite guarantees that all utility functions, AI character recognition pipelines, edge cases, and real-world defect images function correctly before client release. It runs via: pytest tests/ -v.\n\n4.2 Test Data Fixtures (tests/test_images/)\nTo test the model with real-world inputs, curated defect benchmark test images are stored in tests/test_images/:\n• tests/test_images/1_car_plate_motion_blur.jpg: Vehicle license plate with horizontal motion blur (KA 03 MG 4589).\n• tests/test_images/2_receipt_shadow_defect.jpg: Thermal store receipt with harsh diagonal shadow gradient (ASPIRIN, TOTAL DUE).\n• tests/test_images/3_document_skewed_tilted.jpg: Business purchase order tilted by 15° (PURCHASE ORDER #89201).\n• tests/test_images/4_signboard_perspective_blur.jpg: Warning signboard with 3D perspective distortion (ROAD WORK AHEAD).\n• tests/test_images/5_car_plate_glare_defect.jpg: Vehicle license plate with bright headlight glare reflection (DL 01 AB 78).\n\n4.3 Detailed Test Case Specifications:", space_after=4)

    test_table_data = [
        ["Test Function", "What It Tests", "Pass / Assert Condition"],
        ["test_validate_image_bytes_valid()", "Upload validation with real image bytes.", "assert validate_image_bytes(valid_bytes) is True"],
        ["test_validate_image_bytes_corrupt()", "Upload validation with empty or corrupt bytes.", "assert validate_image_bytes(b'bad data') is False"],
        ["test_validate_image_bytes_oversized()", "Rejection of payloads > 200MB (DoS defense).", "assert validate_image_bytes(oversized) is False"],
        ["test_estimate_skew_angle_straight()", "Verifies flat image has near-zero skew angle.", "assert abs(angle) < 5.0"],
        ["test_preprocess_document_image_rgb()", "Contrast and bilateral filtering on 3-channel images.", "assert processed.shape[2] == 3 and not np.isnan(processed).any()"],
        ["test_draw_ocr_bounding_boxes_clamping()", "Margin clamping for text at (0, 0) and (W, H).", "Asserts banner coordinates clamped within (0, W) and (0, H)."],
        ["test_format_export_data_csv()", "CSV table structure and column headers.", "assert 'Line_ID,Text,Confidence,Bounding_Box' in csv_str"],
        ["test_load_ocr_engine_returns_wrapper()", "Deep learning engine initialization.", "assert engine.engine_type == 'deep_learning'"],
        ["test_disambiguate_license_plate_digits()", "Converts letter 'O' to '0' and 'I' to '1' in digit slots.", "assert disambiguate_license_plate('KAO3MG4589') == 'KA 03 MG 4589'"],
        ["test_ocr_car_plate_motion_blur()", "Real detection on 1_car_plate_motion_blur.jpg.", "assert 'KA' in text and '4589' in text"],
        ["test_ocr_receipt_shadow_defect()", "Real detection on 2_receipt_shadow_defect.jpg.", "assert 'PHARMACY' in text and 'TOTAL' in text"],
        ["test_ocr_document_skewed_tilted()", "Real detection on 3_document_skewed_tilted.jpg.", "assert 'PURCHASE ORDER' in text and '89201' in text"],
        ["test_ocr_signboard_perspective_blur()", "Real detection on 4_signboard_perspective_blur.jpg.", "assert 'ROAD' in text or 'WORK' in text"],
        ["test_ocr_blank_white_image()", "Edge case: blank white photo with zero text.", "assert total_text_blocks == 0 without crashing"]
    ]
    add_table(test_table_data, [160, 160, 190])

    add_p("4.4 Visual Verification Artifact Generation:\nWhen test_ocr_engine.py and benchmark runners execute, they write visual output images to an output/ directory:\n• output/result_1_car_plate_motion_blur.jpg: Image showing the plate enclosed in high-contrast box labeled KA 03 MG 4589.\n• output/result_2_receipt_shadow_defect.jpg: Image showing store receipt line items extracted through shadow.\n• output/result_3_document_skewed_tilted.jpg: Image showing straightened purchase order with all 6 lines extracted.\n• output/edge_cases/: Visual artifacts verifying salt-and-pepper noise, wide banners, and inverted dark mode.\n• output/diverse_tests/: Visual artifacts verifying commercial truck plates, medical prescriptions, and boarding passes.", space_after=12)

    # --- SECTION 4 ---
    add_p("4. Error Handling & Edge-Case Matrix", bold=True, font_size=14, color=(15, 23, 42), space_after=6)
    err_table_data = [
        ["Edge Case Scenario", "Potential Failure Point", "System Defense Mechanism"],
        ["Empty or 0-byte file uploaded", "Crash during image decode", "validate_image_bytes checks file length and returns clean error message."],
        ["Corrupted / Truncated image", "Unhandled PIL/OpenCV exception", "Caught in two-phase PIL validation (verify() + load()) without breaking session."],
        ["Oversized payload (> 200 MB)", "Host memory starvation / DoS", "Hard 200MB limit halts processing before memory allocation."],
        ["Photo with 0 text characters", "Loop index out-of-range", "Function returns total_text_blocks = 0, original image displayed intact with banner: 'No text detected.'"],
        ["Text tilted up to 45°", "OCR fragmentation / misreads", "estimate_skew_angle() computes contour angle; rotate_image() counter-rotates frame straight."],
        ["Headlight glare on vehicle plate", "Blinding character washout", "CLAHE equalizes L-channel histogram in LAB color space, restoring character contrast."],
        ["Text touching image boundary", "Coordinate negative out-of-bounds", "Bounding badge coordinates are clamped: startX = max(0, startX)."]
    ]
    add_table(err_table_data, [140, 150, 220])

    # --- SECTION 5 ---
    add_p("5. Traceability Matrix: PRD Requirements to Code", bold=True, font_size=14, color=(15, 23, 42), space_after=6)
    trace_table_data = [
        ["PRD Feature", "Requirement Description", "Implementing Function / File"],
        ["Feature 1 & 2", "Locate text blocks and read alphanumeric characters", "src/ocr_engine.py → detect_and_extract_text()"],
        ["Feature 3", "Vehicle plate alphanumeric disambiguation (0 vs O)", "src/ocr_engine.py → disambiguate_license_plate()"],
        ["Feature 4", "Auto-deskew tilted text up to 45°", "src/utils.py → estimate_skew_angle(), rotate_image()"],
        ["Feature 5", "CLAHE shadow and glare normalization", "src/utils.py → preprocess_document_image()"],
        ["Feature 6", "Draw bounding boxes with boundary clamping", "src/utils.py → draw_ocr_bounding_boxes()"],
        ["Feature 7", "1-Click pre-loaded benchmark demos", "src/app.py → Tab 1 (generate_synthetic_demo_image())"],
        ["Feature 8", "Drag & drop photo uploader", "src/app.py → Tab 2 (st.file_uploader())"],
        ["Feature 9", "Live webcam capture", "src/app.py → Tab 3 (st.camera_input())"],
        ["Feature 10", "Confidence sensitivity slider", "src/app.py → st.sidebar.slider()"],
        ["Feature 11", "Summary metrics cards (Blocks, Confidence, Latency)", "src/app.py → st.columns(3)"],
        ["Feature 12", "Download annotated results (TXT, CSV, JSON)", "src/utils.py → format_export_data() & st.download_button()"],
        ["Quality Gate", "Automated Verification on real images", "tests/test_ocr_engine.py → pytest"]
    ]
    add_table(trace_table_data, [100, 210, 200])

    # Save Word & PDF
    doc.SaveAs2(doc_path)
    print(f"Word Document saved: {doc_path}")

    doc.ExportAsFixedFormat(pdf_path, wdExportFormatPDF)
    print(f"PDF Document exported: {pdf_path}")

finally:
    doc.Close(False)
    word.Quit()
