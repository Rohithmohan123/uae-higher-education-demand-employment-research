"""Run the full research pipeline: simulated data -> analysis, tables and charts -> report (Markdown + PDF).

Usage:
    python run_pipeline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from uae_research import analysis, generate, report  # noqa: E402


def main() -> None:
    print("1/3 Generating simulated survey and scenario inputs")
    generate.main()
    print("2/3 Running analysis, tables and charts")
    findings = analysis.run()
    print("3/3 Writing report")
    md, pdf = report.write_reports(findings)
    print(f"Done: {md.name} and {pdf.name} in reports/")


if __name__ == "__main__":
    main()
