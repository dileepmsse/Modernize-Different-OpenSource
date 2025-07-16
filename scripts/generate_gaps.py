import argparse
import os
import requests
from pathlib import Path
import json

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
        data = json.load(f)
        return data.get("issues", [])

def generate_gaps_from_model(summaries, sonar_issues, token, entity_name="Policy", industry="Insurance"):
    """Generate modernization gaps using a language model."""
    headers = {"Authorization": f"Bearer {token}"}
    gaps = []
    
    # Prepare context for the model
    context = f"Industry: {industry}\nEntity: {entity_name}\n\nCode Analysis:\n"
    for summary in summaries:
        context += f"File: {summary['file']}\nSummary: {summary['summary']}\n\n"
    context += "SonarQube Issues:\n"
    for issue in sonar_issues:
        context += f"Component: {issue.get('component', 'unknown')}, Type: {issue.get('type', 'unknown')}, Message: {issue.get('message', 'No message')}\n"
    
    # Prompt for gap analysis
    prompt = f"""
You are a software modernization expert. Based on the following code analysis and SonarQube issues, identify modernization gaps and provide specific recommendations for a {industry} application managing {entity_name} entities. Focus on modernizing legacy Java servlets, JSP, database access (using Neon), and other outdated practices. Output gaps in the format: "Gap: <description>. Recommendation: <action>."

Context:
{context}

Provide a list of modernization gaps and recommendations.
"""
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mixtralai/Mixtral-8x7B-Instruct-v0.1",
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {"max_new_tokens": 500, "temperature": 0.7}
            }
        )
        if response.status_code == 200:
            result = response.json()[0]["generated_text"]
            # Extract gaps from response (assuming model outputs in requested format)
            for line in result.split("\n"):
                if line.startswith("Gap:"):
                    gaps.append(line.strip())
        else:
            gaps.append(f"Error: Failed to generate gaps from model (status: {response.status_code})")
    except Exception as e:
        gaps.append(f"Error: Exception in model inference: {str(e)}")
    
    return gaps

def generate_gaps(reports_dir, output_path, entity_name="Policy", industry="Insurance"):
    """Generate modernization gaps using a model."""
    codebert_summaries = parse_codebert_summary(reports_dir)
    sonar_issues = parse_sonar_report(reports_dir)
    token = os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_TOKEN environment variable not set")
    
    gaps = generate_gaps_from_model(codebert_summaries, sonar_issues, token, entity_name, industry)
    
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
    parser.add_argument("--entity-name", default="Policy", help="Entity name (e.g., Policy)")
    parser.add_argument("--industry", default="Insurance", help="Industry (e.g., Insurance)")
    args = parser.parse_args()
    generate_gaps(args.analysis_reports, args.output, args.entity_name, args.industry)