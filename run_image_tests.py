"""
Runner Script: Test OCR on Image Dataset & Generate Output Visual Artifacts
File: run_image_tests.py
"""

import os
import sys
import time
import cv2

from src.ocr_engine import load_ocr_engine, detect_and_extract_text

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_IMAGES_DIR = os.path.join(ROOT_DIR, "tests", "test_images")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("=" * 65)
    print("   UNIVERSAL OCR SYSTEM — IMAGE TEST BENCHMARK RUNNER")
    print("=" * 65)

    print("\n[1/3] Loading AI Deep Learning Engine...")
    engine = load_ocr_engine()
    print("      Deep Learning CRAFT + CRNN Engine Loaded Successfully!\n")

    image_files = [f for f in sorted(os.listdir(TEST_IMAGES_DIR)) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    print(f"[2/3] Processing {len(image_files)} Benchmark Images from tests/test_images/...\n")

    total_start = time.time()

    for idx, fname in enumerate(image_files, start=1):
        fpath = os.path.join(TEST_IMAGES_DIR, fname)
        img = cv2.imread(fpath)
        if img is None:
            print(f"  [{idx}/{len(image_files)}] FAILED to read {fname}")
            continue

        start_time = time.time()
        result = detect_and_extract_text(img, engine=engine)
        elapsed_ms = (time.time() - start_time) * 1000.0

        # Save annotated image artifact into output/
        out_name = f"result_{fname}"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        cv2.imwrite(out_path, result["annotated_image"])

        first_line = result["extracted_text"].split("\n")[0] if result["extracted_text"] else "[NO TEXT]"
        if len(first_line) > 30:
            first_line = first_line[:27] + "..."

        print(f"  [{idx}/{len(image_files)}] {fname:<32} | Blocks: {result['total_text_blocks']:<2} | {elapsed_ms:>6.0f}ms | Extracted: '{first_line}'")
        print(f"        --> Saved annotated visual artifact to output/{out_name}")

    total_time = time.time() - total_start
    print(f"\n[3/3] Completed all {len(image_files)} benchmark images in {total_time:.2f}s!")
    print(f"      All annotated visual artifacts are ready in: output/\n")
    print("=" * 65)


if __name__ == "__main__":
    main()
