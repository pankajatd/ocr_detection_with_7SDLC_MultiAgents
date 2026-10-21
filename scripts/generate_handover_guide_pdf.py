"""
Enterprise Document Generator: Deployment_and_Customer_Handover_Guide.docx & .pdf
Universal Optical Character Recognition System
Author: DevOps & Systems Architecture Team
"""

import os
import sys
import win32com.client

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS_DIR = os.path.join(ROOT_DIR, "plans")

doc_path = os.path.abspath(os.path.join(PLANS_DIR, "Deployment_and_Customer_Handover_Guide.docx"))
pdf_path = os.path.abspath(os.path.join(PLANS_DIR, "Deployment_and_Customer_Handover_Guide.pdf"))

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
    add_p("UNIVERSAL OPTICAL CHARACTER RECOGNITION (OCR) SYSTEM", space_after=2, align=wdAlignParagraphCenter, bold=True, font_size=24, color=(30, 64, 175))
    add_p("Comprehensive Guide: Streamlit Cloud Deployment, Docker Packaging & Customer Handover", space_after=14, align=wdAlignParagraphCenter, bold=False, font_size=13, color=(100, 116, 139))
    add_p("Document Version: 1.0.0 | Author: DevOps & Systems Architecture Team | Date: 2026-10-21", space_after=20, align=wdAlignParagraphCenter, bold=False, font_size=10, color=(148, 163, 184))

    # --- SECTION 1 ---
    add_p("1. Executive Overview & Delivery Strategy", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "The Universal OCR & Plate Detection System is architected to support two distinct delivery pathways tailored to the technical requirements and regulatory constraints of different customer personas:\n\n"
        "• Pathway 1 (End-Users & General Public): Zero-install web delivery hosted via Streamlit Community Cloud. Users interact with the AI application through a secure, public HTTPS hyperlink on their browser without downloading any software or managing code.\n\n"
        "• Pathway 2 (Enterprise, Logistics, Law Enforcement & High-Security Clients): Self-contained Docker containerization. Enables toll operators, parking authorities, banks, and enterprise IT teams to run the AI system 100% on-premise on private servers behind internal firewalls, guaranteeing complete data privacy, zero external telemetry, and offline operational continuity.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- SECTION 2 ---
    add_p("2. Streamlit Cloud Public Link Setup (Step-by-Step)", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "Streamlit Community Cloud allows free, continuous cloud hosting directly synchronized with a GitHub repository. Follow these exact steps to deploy or re-deploy the application:\n\n"
        "Step 2.1: Repository Preparation on GitHub\n"
        "The project repository must be public and contain the following essential files at the root level:\n"
        "  • src/app.py: The main entry point containing the Streamlit web dashboard interface.\n"
        "  • requirements.txt: Defines all pinned Python dependencies with CPU PyTorch index for rapid build.\n"
        "  • packages.txt: Specifies low-level Linux Debian packages (libgl1, libglib2.0-0) required by OpenCV.\n"
        "  • models/model_manifest.json: Documents CRAFT and CRNN architecture specifications.\n\n"
        "Step 2.2: Launching on Streamlit Cloud\n"
        "  1. Navigate to https://share.streamlit.io and sign in with your GitHub account.\n"
        "  2. Click the 'Create app' or 'New app' button in the upper-right corner.\n"
        "  3. Configure the three deployment parameters:\n"
        "     - Repository: pankajatd/ocr_detection_with_7SDLC_MultiAgents\n"
        "     - Branch: main\n"
        "     - Main file path: src/app.py\n"
        "  4. Click Deploy. Streamlit Cloud installs the Linux packages, resolves Python wheels, and launches your live application at a permanent public URL (e.g. https://ocrdetectionwith7sdlcmultiagents-...streamlit.app).",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- SECTION 3 ---
    add_p("3. Docker Containerization & Enterprise On-Premise Deployment", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "For clients with sensitive document workflows (financial invoices, medical receipts, confidential car plate logs), the system provides single-command containerized execution:\n\n"
        "Step 3.1: Building & Starting the Container\n"
        "Execute from the project root folder:\n"
        "  docker-compose up -d --build\n\n"
        "Step 3.2: Verifying Container Health\n"
        "Execute:\n"
        "  docker ps\n"
        "Confirm that 'ocr_detection_service' shows status 'Up' with port mapping 0.0.0.0:8501->8501/tcp.\n\n"
        "Step 3.3: Accessing the Dashboard\n"
        "Open any browser on the local network and navigate to: http://localhost:8501\n\n"
        "Step 3.4: Stopping the Container\n"
        "Execute:\n"
        "  docker-compose down",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # --- SECTION 4 ---
    add_p("4. Customer Acceptance Testing & Verification Checklist", bold=True, font_size=16, color=(15, 23, 42), space_after=8)
    add_p(
        "Before formal project sign-off, verify each capability against the acceptance checklist:\n"
        "• [x] Benchmark 1 (Vehicle Number Plate): AI extracts 'MH 12 AB 1234' with plate disambiguation.\n"
        "• [x] Benchmark 2 (Store Receipt): AI extracts itemized prices and totals through shadows.\n"
        "• [x] Benchmark 3 (Printed Document): AI straightens 15° skewed document and extracts all 6 lines.\n"
        "• [x] Benchmark 4 (Tilted Signboard): AI extracts caution text on 3D perspective angle.\n"
        "• [x] Camera Ingestion: Live snapshot capture operates seamlessly via st.camera_input.\n"
        "• [x] Multi-Format Export: 1-Click downloads generate clean TXT, CSV, and JSON files.\n"
        "• [x] Automated Tests: 26/26 PyTest unit and integration tests passing in terminal.",
        font_size=11, space_after=14, align=wdAlignParagraphJustify
    )

    # Save
    doc.SaveAs2(doc_path)
    print(f"Word Document saved: {doc_path}")

    doc.ExportAsFixedFormat(pdf_path, wdExportFormatPDF)
    print(f"PDF Document exported: {pdf_path}")

finally:
    doc.Close(False)
    word.Quit()
