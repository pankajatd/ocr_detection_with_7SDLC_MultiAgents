"""
Runner Script: Test Diverse Real-World OCR Scenarios & Save Visual Outputs
File: run_diverse_tests.py
"""

import os
import sys
import time
import numpy as np
import cv2

from src.ocr_engine import load_ocr_engine, detect_and_extract_text

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output", "diverse_tests")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("=" * 65)
    print("   UNIVERSAL OCR SYSTEM — DIVERSE REAL-WORLD BENCHMARK RUNNER")
    print("=" * 65)

    print("\n[1/3] Loading AI Deep Learning Engine...")
    engine = load_ocr_engine()

    benchmarks = []

    # 1. Commercial Vehicle Truck Plate
    p1 = np.full((180, 560, 3), (255, 255, 255), dtype=np.uint8)
    cv2.rectangle(p1, (8, 8), (552, 172), (20, 20, 20), 4)
    cv2.putText(p1, "HR 26 DQ 5511", (75, 115), cv2.FONT_HERSHEY_DUPLEX, 1.6, (20, 20, 20), 4)
    benchmarks.append(("diverse_1_commercial_truck_plate.jpg", p1, "Commercial Truck Plate"))

    # 2. Medical Prescription / Doctor Note
    rx = np.full((400, 480, 3), 250, dtype=np.uint8)
    cv2.putText(rx, "CITY GENERAL CLINIC", (40, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 0, 0), 2)
    cv2.putText(rx, "Rx: Amoxicillin 500mg", (40, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 2)
    cv2.putText(rx, "Sig: Take 1 tablet every 8 hrs", (40, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50, 50, 50), 1)
    cv2.putText(rx, "Duration: 7 Days with meals", (40, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50, 50, 50), 1)
    cv2.putText(rx, "Dr. Sarah Jenkins, MD", (40, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)
    benchmarks.append(("diverse_2_medical_prescription.jpg", rx, "Medical Prescription Note"))

    # 3. Airport Boarding Pass Snippet
    bp = np.full((240, 600, 3), 245, dtype=np.uint8)
    cv2.rectangle(bp, (10, 10), (590, 230), (0, 80, 160), 3)
    cv2.putText(bp, "BOARDING PASS", (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 80, 160), 2)
    cv2.putText(bp, "PASSENGER: SMITH / J", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)
    cv2.putText(bp, "FLIGHT: BA 184   GATE: B24", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)
    cv2.putText(bp, "SEAT: 14A   BOARDING: 10:45", (30, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 1)
    benchmarks.append(("diverse_3_airline_boarding_pass.jpg", bp, "Airline Boarding Pass"))

    # 4. Warehouse Shipping Pallet Label
    pl = np.full((320, 480, 3), 252, dtype=np.uint8)
    cv2.putText(pl, "PRIORITY AIR CARGO", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (10, 10, 10), 2)
    cv2.putText(pl, "TRACKING: 9400 1000 8920", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 2)
    cv2.putText(pl, "DESTINATION: HEATHROW TERMINAL 4", (40, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 40, 40), 1)
    cv2.putText(pl, "WEIGHT: 42.5 KG", (40, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (10, 10, 10), 2)
    benchmarks.append(("diverse_4_shipping_pallet_label.jpg", pl, "Warehouse Shipping Label"))

    print(f"\n[2/3] Processing {len(benchmarks)} Diverse Real-World Scenarios...\n")

    for idx, (fname, img, desc) in enumerate(benchmarks, start=1):
        res = detect_and_extract_text(img, engine=engine)
        out_path = os.path.join(OUTPUT_DIR, f"result_{fname}")
        cv2.imwrite(out_path, res["annotated_image"])
        print(f"  [{idx}/{len(benchmarks)}] {desc:<28} | Blocks: {res['total_text_blocks']:<2} | Saved: output/diverse_tests/result_{fname}")

    print(f"\n[3/3] Diverse test suite complete! Visual outputs saved to output/diverse_tests/\n")
    print("=" * 65)


if __name__ == "__main__":
    main()
