
from pathlib import Path
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "week2"
CHART_DIR = REPORT_DIR / "charts"

# Collect CSV files
csv_files = sorted(REPORT_DIR.glob("*.csv"))
chart_files = sorted(CHART_DIR.glob("*.png"))

results = []

for file in csv_files:
    df = pd.read_csv(file)

    results.append({
        "File": file.name,
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing Cells": int(df.isna().sum().sum()),
        "Duplicate Rows": int(df.duplicated().sum()),
        "Status": "PASS" if len(df) > 0 else "CHECK"
    })

# Generate Markdown report
lines = [
    "# Week 2 Output Validation Report",
    "",
    "## 1. Validation Overview",
    "",
    f"- CSV files found: {len(csv_files)}",
    f"- Chart files found: {len(chart_files)}",
    f"- Total CSV records: {sum(r['Rows'] for r in results)}",
    "",
    "## 2. CSV Validation Results",
    "",
    "| File | Rows | Columns | Missing Cells | Duplicate Rows | Status |",
    "|---|---:|---:|---:|---:|---|"
]

for r in results:
    lines.append(
        f"| {r['File']} | {r['Rows']} | {r['Columns']} "
        f"| {r['Missing Cells']} | {r['Duplicate Rows']} "
        f"| {r['Status']} |"
    )

lines += [
    "",
    "## 3. Visualization Validation",
    ""
]

for chart in chart_files:
    lines.append(f"- PASS: `{chart.name}`")

lines += [
    "",
    "## 4. Validation Scope",
    "",
    "- CSV file existence and readability",
    "- Record and column counts",
    "- Missing cell counts",
    "- Duplicate row counts",
    "- PNG chart file existence",
    "",
    "## 5. Conclusion",
    "",
    "This report summarizes the structural validation of Week 2 "
    "analysis outputs. Missing values and duplicate rows are "
    "reported for further investigation where necessary.",
    "",
    "Note: This is a structural validation, not a complete "
    "verification of analytical correctness."
]

output_file = REPORT_DIR / "week2_output_validation.md"
output_file.write_text("\n".join(lines), encoding="utf-8")

print("Week 2 validation completed.")
print(f"CSV files checked: {len(csv_files)}")
print(f"Charts checked: {len(chart_files)}")
print(f"Report saved: {output_file}")
