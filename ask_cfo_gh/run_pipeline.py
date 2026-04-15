#!/usr/bin/env python3
"""
Pipeline Runner — processes all PDFs in input/ folder.
Used by GitHub Actions workflow.

Usage: python run_pipeline.py [--api-key KEY] [--skip-stage1] [--input DIR] [--output DIR]
"""

import os
import sys
import warnings
import argparse
import traceback
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))


def run(input_dir, output_dir, api_key="", skip_stage1=False):
    os.makedirs(output_dir, exist_ok=True)

    pdfs = sorted(Path(input_dir).glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {input_dir}")
        return []

    print(f"\n{'='*60}")
    print(f"  ASK MY CFO — M1 Automation")
    print(f"  Processing {len(pdfs)} PDF(s)")
    print(f"{'='*60}\n")

    all_outputs = []

    for fi, pdf_path in enumerate(pdfs):
        pdf_path = str(pdf_path)
        stem = Path(pdf_path).stem
        print(f"\n━━━ [{fi+1}/{len(pdfs)}] {Path(pdf_path).name} ━━━")

        # ═══ STAGE 1 ═══
        working_pdf = pdf_path
        if skip_stage1:
            print("  Stage 1: skipped")
        else:
            print("  Stage 1: Detecting BS/PL pages...")
            try:
                from page_detector import extract_pages
                bs_pl_pdf = extract_pages(pdf_path, output_dir)
                if bs_pl_pdf and os.path.exists(bs_pl_pdf):
                    working_pdf = bs_pl_pdf
                    all_outputs.append(bs_pl_pdf)
                    print(f"  ✓ {os.path.basename(bs_pl_pdf)}")
                else:
                    print("  ⚠ No sections found, using full PDF")
            except Exception as e:
                print(f"  ⚠ Stage 1 error: {e}")

        # ═══ STAGE 2 ═══
        print(f"  Stage 2: Extracting tables from {os.path.basename(working_pdf)}...")
        extracted_xlsx = None
        try:
            from extract_tables import extract_tables as do_extract
            do_extract(working_pdf, output_dir)

            expected = Path(output_dir) / f"{Path(working_pdf).stem}_extracted.xlsx"
            if expected.exists():
                extracted_xlsx = str(expected)
            else:
                for f in sorted(Path(output_dir).glob("*_extracted.xlsx"),
                                key=os.path.getmtime, reverse=True):
                    extracted_xlsx = str(f)
                    break

            if extracted_xlsx:
                all_outputs.append(extracted_xlsx)
                print(f"  ✓ {os.path.basename(extracted_xlsx)}")
            else:
                print("  ✗ No extracted Excel generated!")
                continue
        except Exception as e:
            print(f"  ✗ Stage 2 failed: {e}")
            traceback.print_exc()
            continue

        # ═══ STAGE 3 ═══
        if not api_key:
            print("  Stage 3: skipped (no API key)")
        else:
            print("  Stage 3: GPT-4o mapping...")
            try:
                from bs_pl_mapper import process_file
                report_path = process_file(
                    input_file=extracted_xlsx,
                    template_file=extracted_xlsx,
                    api_key=api_key,
                    output_dir=output_dir,
                )
                if report_path and os.path.exists(report_path):
                    all_outputs.append(report_path)
                    print(f"  ✓ {os.path.basename(report_path)}")
                else:
                    print("  ⚠ No report generated")
            except Exception as e:
                print(f"  ✗ Stage 3 failed: {e}")
                traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"  Done — {len(all_outputs)} output file(s)")
    for f in all_outputs:
        print(f"    → {os.path.basename(f)}")
    print(f"{'='*60}\n")

    return all_outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASK MY CFO — Pipeline Runner")
    parser.add_argument("--input", default="input", help="Input directory with PDFs")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""), help="OpenAI API key")
    parser.add_argument("--skip-stage1", action="store_true", help="Skip page detection")
    args = parser.parse_args()

    results = run(args.input, args.output, args.api_key, args.skip_stage1)
    if not results:
        sys.exit(1)
