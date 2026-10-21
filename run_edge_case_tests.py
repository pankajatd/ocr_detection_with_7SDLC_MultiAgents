"""
Runner Script: Test OCR on Edge Cases (Occlusion, Glare, Inverted, Blank)
File: run_edge_case_tests.py
"""

import os
import sys
import time
import numpy as np
import cv2

from src.ocr_engine import load_ocr_engine, detect_and_extract_text

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output", "edge_cases")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("=" * 65)
    print("   UNIVERSAL OCR SYSTEM — EDGE CASE BENCHMARK RUNNER")
    print("=" * 65)

    print("\n[1/3] Loading AI Deep Learning Engine...")
    engine = load_ocr_engine()

    edge_cases = []

    # Edge Case 1: Pure White Blank Canvas (Zero Text)
    blank = np.full((300, 500, 3), 255, dtype=np.uint8)
    edge_cases.append(("edge_1_blank_canvas.jpg", blank, "Zero Text / Blank Canvas"))

    # Edge Case 2: Extreme Noise (Salt & Pepper)
    noise_img = np.full((200, 500, 3), 245, dtype=np.uint8)
    cv2.putText(noise_img, "EMERGENCY EXIT", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (10, 10, 10), 3)
    noise = np.random.normal(0, 25, noise_img.shape).astype(np.int16)
    noise_img = np.clip(noise_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    edge_cases.append(("edge_2_salt_pepper_noise.jpg", noise_img, "Heavy Sensor Noise"))

    # Edge Case 3: High Aspect Ratio Ribbon (10:1 banner)
    banner = np.full((80, 700, 3), (0, 200, 255), dtype=np.uint8)
    cv2.putText(banner, "PARKING PERMIT REQUIRED - TOW AWAY ZONE", (20, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2)
    edge_cases.append(("edge_3_wide_aspect_banner.jpg", banner, "Ultra-Wide Banner (10:1)"))

    # Edge Case 4: Inverted Dark Mode Document (White text on black background)
    inverted = np.full((400, 500, 3), 15, dtype=np.uint8)
    cv2.putText(inverted, "NIGHT MODE TERMINAL", (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (240, 240, 240), 2)
    cv2.putText(inverted, "STATUS: SYSTEM ONLINE", (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    cv2.putText(inverted, "IP: 192.168.1.105", (40, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    edge_cases.append(("edge_4_inverted_dark_mode.jpg", inverted, "Dark Mode / Inverted Contrast"))

    print(f"\n[2/3] Executing {len(edge_cases)} Edge Case Experiments...\n")

    for idx, (fname, img, desc) in enumerate(edge_cases, start=1):
        res = detect_and_extract_text(img, engine=engine)
        out_path = os.path.join(OUTPUT_DIR, f"result_{fname}")
        cv2.imwrite(out_path, res["annotated_image"])
        print(f"  [{idx}/{len(edge_cases)}] {desc:<30} | Blocks: {res['total_text_blocks']:<2} | Saved: output/edge_cases/result_{fname}")

    print(f"\n[3/3] Edge case suite complete! Visual outputs saved to output/edge_cases/\n")
    print("=" * 65)


if __name__ == "__main__":
    main()
