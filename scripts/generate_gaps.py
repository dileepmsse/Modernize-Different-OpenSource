import argparse
import os
from pathlib import Path

def parse_codebert_summary(report_path):
    """Parse human-readable summaries from codebert-summary.md."""
    summary_path = Path(report_path) / "codebert-summary.md"
    if not summary_path.exists():
        return []
    summaries = []
    current_file = None
    with open(summary_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("File: "):
                current_file = line.replace("File: ", "").strip()
            elif line.startswith("Summary: ") and current_file:
                summary = line.replace("Summary: ", "").strip()
                summaries.append({"file": current_file, "summary": summary})
    return summaries

def parse_sonar_report(report_path):
    """Parse SonarQube issues."""
    sonar_path = Path(report_path) / "sonar-report.json"
    if not sonar_path.exists():
        return []
    with open(sonar_path) as f:
        import json
        data = json.load(f)
        return data.get("issues", [])

def generate_gaps(reports_dir, output_path):
    """Generate modernization gaps."""
    codebert_summaries = parse_codebert_summary(reports_dir)
    sonar_issues = parse_sonar_report(reports_dir)
    gaps = []

    # Process CodeBERT summaries
    for summary in codebert_summaries:
        if "servlet" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} uses legacy servlet architecture. Recommendation: Migrate to Spring Boot REST APIs.")
        if "dependency injection" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} lacks dependency injection. Recommendation: Adopt Spring Framework for DI.")
        if "jsp" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} uses JSP for rendering. Recommendation: Migrate to modern frontend framework like React or Angular.")

    # Process SonarQube issues
    for issue in sonar_issues:
        if issue.get("type") == "CODE_SMELL":
            gaps.append(f"Gap: Code smell in {issue.get('component')}: {issue.get('message')}. Recommendation: Refactor code.")

    # Write gaps to output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Modernization Gaps\n\n")
        for gap in gaps:
            f.write(f"- {gap}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-reports", required=True, help="Directory containing analysis reports")
    parser.add_argument("--output", required=True, help="Output path for gaps.md")
    args = parser.parse_args()
    generate_gaps(args.analysis_reports, args.output)