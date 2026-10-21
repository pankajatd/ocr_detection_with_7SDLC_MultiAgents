"""
Enterprise Document Generator: Docker_Generation_and_Testing_Manual.docx & .pdf
Universal Optical Character Recognition System
Author: DevOps & Systems Engineering Team
"""

import os
import sys
import win32com.client

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS_DIR = os.path.join(ROOT_DIR, "plans")

doc_path = os.path.abspath(os.path.join(PLANS_DIR, "Docker_Generation_and_Testing_Manual.docx"))
pdf_path = os.path.abspath(os.path.join(PLANS_DIR, "Docker_Generation_and_Testing_Manual.pdf"))

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

    # --- TITLE BANNER ---
    add_p("DOCKERFILE GENERATION & TESTING MANUAL", space_after=2, align=wdAlignParagraphCenter, bold=True, font_size=24, color=(2, 132, 199))
    add_p("A Complete Engineer's Guide: Constructing, Building, and Verifying the Universal OCR Container", space_after=12, align=wdAlignParagraphCenter, bold=False, font_size=13, color=(100, 116, 139))
    add_p("Document Version: 1.0.0 | Author: DevOps & Systems Engineering Team | Date: 2026-10-21", space_after=20, align=wdAlignParagraphCenter, bold=False, font_size=10, color=(148, 163, 184))

    # --- SECTION 1 ---
    add_p("1. What is a Dockerfile and Why is it Generated?", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "A Dockerfile is an automated build manifest containing step-by-step instructions that assemble a self-contained, reproducible virtual environment (called a Docker Container). "
        "In artificial intelligence and optical character recognition applications, Python code depends heavily on low-level operating system C++ binaries, graphics drivers (e.g. libgl1, libglib2.0-0), "
        "PyTorch C-extensions, and specific numerical libraries. Without containerization, moving code to a different machine frequently produces missing shared object errors or version conflicts.\n\n"
        "By generating a Dockerfile, the entire application—including the mini-Debian Linux operating system, OpenCV graphics libraries, Python 3.10 interpreter, pre-downloaded CRAFT and CRNN deep learning weights, "
        "and the Streamlit dashboard—is sealed into a universal container that runs identically on any laptop, server, or cloud platform.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- SECTION 2 ---
    add_p("2. Line-by-Line Anatomy of the Generated Dockerfile", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "The project Dockerfile is structured into six hardened stages:\n\n"
        "Stage 1: Base Operating System\n"
        "  Directive: FROM python:3.10-slim\n"
        "  Explanation: Pulls an official lightweight (~150 MB) Debian Linux system with Python 3.10 pre-installed, minimizing container size and reducing attack surfaces.\n\n"
        "Stage 2: Low-Level System Dependencies\n"
        "  Directive: RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 curl && rm -rf /var/lib/apt/lists/*\n"
        "  Explanation: OpenCV requires Linux shared C++ libraries (libgl1 and libglib) to decode image matrices. Installing these via apt-get ensures cv2 never crashes with missing shared object errors.\n\n"
        "Stage 3: Working Directory Definition\n"
        "  Directive: WORKDIR /app\n"
        "  Explanation: Sets the primary execution and storage folder inside the container to /app.\n\n"
        "Stage 4: Dependency Caching & Installation\n"
        "  Directive: COPY requirements.txt . followed by RUN pip install --no-cache-dir -r requirements.txt\n"
        "  Explanation: Copies requirements.txt first and runs pip. If dependencies haven't changed, Docker reuses the cached layer, making future rebuilds take only seconds.\n\n"
        "Stage 5: Pre-Baking Neural Network Weights\n"
        "  Directive: RUN python -c \"import easyocr; easyocr.Reader(['en'], gpu=False)\"\n"
        "  Explanation: Pre-downloads the CRAFT detector and CRNN recognition weights during the build step so end-users never experience runtime model download delays.\n\n"
        "Stage 6: Port Exposure & Launch Entrypoint\n"
        "  Directive: EXPOSE 8501 | CMD [\"streamlit\", \"run\", \"src/app.py\", \"--server.port=8501\", \"--server.address=0.0.0.0\", \"--server.headless=true\"]\n"
        "  Explanation: Opens networking port 8501 and instructs Streamlit to broadcast on 0.0.0.0 so external browsers can connect.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- SECTION 3 ---
    add_p("3. The Companion Configuration: docker-compose.yml", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "To eliminate the need for memorizing long terminal execution flags, docker-compose.yml stores all operational settings:\n\n"
        "• Port Forwarding: Maps host machine port 8501 to container port 8501 ('8501:8501').\n"
        "• Container Naming: Assigns a clean, human-readable name ('ocr_detection_service').\n"
        "• Restart Policy: Set to 'unless-stopped' so the container automatically recovers if the host reboots.\n"
        "• Healthcheck: Periodically pings Streamlit's internal health endpoint (/_stcore/health) to ensure high availability.\n\n"
        "With this file present, the entire build and launch process is compressed into a single command: docker-compose up -d --build.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- SECTION 4 ---
    add_p("4. Step-by-Step Protocol to Test the Docker Container", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "Follow these exact steps to launch, inspect, and verify the container on your system:\n\n"
        "Step 4.1: Launch Docker Desktop\n"
        "  • Open Docker Desktop from the Windows Start Menu.\n"
        "  • Verify the bottom-left status indicator turns GREEN and displays 'Engine running'.\n\n"
        "Step 4.2: Execute the Launch Command in Terminal\n"
        "  • Open Command Prompt or PowerShell.\n"
        "  • Navigate to: cd C:\\Pankaja\\AUTOMATED_SDLC_AGENT_PROJECTS\\ocr_detection\n"
        "  • Execute the build and run command:\n"
        "     docker-compose up -d --build\n"
        "  • Docker builds the layers and reports: 'Container ocr_detection_service Started'.\n\n"
        "Step 4.3: Terminal Status Verification\n"
        "  • In terminal, run: docker ps\n"
        "  • Confirm the output shows:\n"
        "     - IMAGE: ocr-detection:1.0.0\n"
        "     - STATUS: Up X seconds / minutes\n"
        "     - PORTS: 0.0.0.0:8501->8501/tcp\n"
        "     - NAMES: ocr_detection_service\n\n"
        "Step 4.4: Web Browser Functional Verification\n"
        "  • Open Google Chrome, Microsoft Edge, or Firefox.\n"
        "  • Navigate to: http://localhost:8501\n"
        "  • Functional Tests to Execute:\n"
        "     1. Click '🚗 Vehicle Number Plate' -> Verify bounding box extracts 'MH 12 AB 1234'.\n"
        "     2. Click '🧾 Store Receipt' -> Verify line items and totals extracted.\n"
        "     3. Click '📄 Printed Document' -> Verify full document text extracted.\n"
        "     4. Click 'Download as CSV' -> Verify extracted_table.csv downloads to your computer.\n\n"
        "Step 4.5: Internal Automated Test Execution Inside Docker\n"
        "  • To run the automated 26-point pytest suite directly inside the Linux container, execute:\n"
        "     docker exec -it ocr_detection_service pytest tests/\n"
        "  • This verifies all unit tests, model loading, and character algorithms pass natively within Linux.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- SECTION 5 ---
    add_p("5. Container Lifecycle Management Commands", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "• Start container in background: docker-compose up -d\n"
        "• Rebuild and restart after updates: docker-compose up -d --build\n"
        "• View real-time container logs: docker logs -f ocr_detection_service\n"
        "• Stop container gracefully: docker-compose down\n"
        "• Inspect container resource usage (CPU/RAM): docker stats ocr_detection_service",
        font_size=11, space_after=14, align=wdAlignParagraphLeft
    )

    # Save
    doc.SaveAs2(doc_path)
    print(f"Word Document saved: {doc_path}")

    doc.ExportAsFixedFormat(pdf_path, wdExportFormatPDF)
    print(f"PDF Document exported: {pdf_path}")

finally:
    doc.Close(False)
    word.Quit()
