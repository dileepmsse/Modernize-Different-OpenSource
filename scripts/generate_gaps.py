import argparse
import os
from pathlib import Path
import json
import re
from openai import OpenAI
import time

def parse_codebert_summary(report_path):
    """Parse human-readable summaries from codebert-summary.md."""
    summary_path = Path(report_path) / "codebert-summary.md"
    if not summary_path.exists():
        print(f"Warning: {summary_path} not found, relying on fallback.")
        return []
    summaries = []
    current_file = None
    try:
        with open(summary_path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("File: "):
                    current_file = line.replace("File: ", "").strip()
                elif line.startswith("Summary: ") and current_file:
                    summary = line.replace("Summary: ", "").strip()
                    summaries.append({"file": current_file, "summary": summary})
    except Exception as e:
        print(f"Error: Failed to parse {summary_path}: {str(e)}")
        return []
    return summaries

def parse_sonar_report(report_path):
    """Parse SonarQube issues."""
    sonar_path = Path(report_path) / "sonar-report.json"
    if not sonar_path.exists():
        print(f"Warning: {sonar_path} not found, relying on fallback.")
        return []
    try:
        with open(sonar_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("issues", [])
    except Exception as e:
        print(f"Error: Failed to parse {sonar_path}: {str(e)}")
        return []

def truncate_text(text, max_chars=1000):
    """Truncate text to fit model token limit."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "... [truncated]"

def build_context(summaries, sonar_issues, industry, entity_name):
    """Build context string for model prompt."""
    context = f"Industry: {industry}\nEntity: {entity_name}\n\nCode Analysis:\n"
    for summary in summaries:
        context += f"File: {summary['file']}\nSummary: {summary['summary']}\n\n"
    context += "SonarQube Issues:\n"
    for issue in sonar_issues:
        context += f"Component: {issue.get('component', 'unknown')}, Type: {issue.get('type', 'unknown')}, Message: {issue.get('message', 'No message')}\n"
    return truncate_text(context, max_chars=1000)

def build_prompt(context, industry, entity_name):
    """Build prompt for gap analysis."""
    return f"""
You are a software modernization expert. Based on the following code analysis and SonarQube issues, identify modernization gaps for a {industry} application managing {entity_name} entities. Focus on modernizing legacy Java servlets, JSP, database access (using Neon), and outdated libraries. Output gaps in the format: "Gap: <description>. Recommendation: <action>."

Example Gaps:
- Gap: Servlet-based architecture detected. Recommendation: Migrate to Spring Boot REST APIs.
- Gap: Raw JDBC usage. Recommendation: Use Spring Data JPA with Neon.
- Gap: JSP-based UI rendering. Recommendation: Adopt React or Angular.
- Gap: Outdated logging library used. Recommendation: Adopt SLF4J with Logback.
- Gap: Hardcoded database credentials. Recommendation: Use environment variables with Spring Security.

Context:
{context}

Provide a list of modernization gaps and recommendations.
"""

def extract_gaps_from_response(result_text):
    """Extract gaps from model response text."""
    return [line.strip() for line in result_text.split("\n") if line.strip().startswith("Gap:")]

def call_huggingface_model(client, model, prompt, max_attempts=3):
    """Call Hugging Face model and return gaps or None."""
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a software modernization expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            result_text = response.choices[0].message.content.strip()
            gaps = extract_gaps_from_response(result_text)
            if gaps:
                return gaps
            print(f"Warning: No valid gaps extracted from {model} output.")
            time.sleep(2 ** attempt)
        except Exception as e:
            error_msg = f"Error: Exception in {model} inference (attempt {attempt + 1}): {str(e)}"
            print(error_msg)
            if "rate limit" in str(e).lower() or "429" in str(e):
                time.sleep(2 ** attempt)
                continue
            break
    return None

def generate_gaps_from_model(summaries, sonar_issues, token, source_dir="PolicyManagementJSP/src/main/java", entity_name="Policy", industry="Insurance"):
    """Generate modernization gaps using Hugging Face Router API."""
    # Validate OpenAI client compatibility with Hugging Face router API
    try:
        client = OpenAI(
            api_key=token,
            base_url="https://api.endpoints.huggingface.cloud/v1"
        )
    except Exception as e:
        print(f"Error: Failed to initialize Hugging Face API client: {str(e)}")
        return generate_fallback_gaps(summaries, sonar_issues, source_dir)

    context = build_context(summaries, sonar_issues, industry, entity_name)
    prompt = build_prompt(context, industry, entity_name)

    # Use endpoints compatible with Hugging Face Inference Endpoints
    model_endpoints = [
        "mistralai/Mistral-7B-Instruct-v0.2",
        "mistralai/Mixtral-8x7B-Instruct-v0.1"
    ]

    for model in model_endpoints:
        gaps = call_huggingface_model(client, model, prompt)
        if gaps:
            return gaps

    print("Warning: All model inferences failed, using fallback.")
    return generate_fallback_gaps(summaries, sonar_issues, source_dir)

def generate_fallback_gaps(summaries, sonar_issues, source_dir="PolicyManagementJSP/src/main/java"):
    """Generate gaps using rule-based logic as a fallback."""
    gaps = []
    # Parse summaries if available
    for summary in summaries:
        if "servlet" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} uses legacy servlet architecture. Recommendation: Migrate to Spring Boot REST APIs.")
        if "dependency injection" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} lacks dependency injection. Recommendation: Adopt Spring Framework for DI.")
        if "jsp" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} uses JSP for rendering. Recommendation: Migrate to modern frontend framework like React or Angular.")
        if "jdbc" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} uses raw JDBC. Recommendation: Adopt Spring Data JPA with Neon for modern ORM.")
        if "logging" in summary["summary"].lower():
            gaps.append(f"Gap: {summary['file']} uses outdated logging. Recommendation: Adopt SLF4J with Logback.")
    
    # Parse SonarQube issues
    for issue in sonar_issues:
        if issue.get("type") == "CODE_SMELL":
            gaps.append(f"Gap: Code smell in {issue.get('component', 'unknown')}: {issue.get('message', 'No message')}. Recommendation: Refactor code.")
    
    # If no summaries, parse raw source code
    if not summaries and os.path.exists(source_dir):
        try:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if file.endswith(".java"):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, encoding="utf-8") as f:
                                content = f.read()
                                if "javax.servlet" in content:
                                    gaps.append(f"Gap: {file} uses legacy servlet architecture. Recommendation: Migrate to Spring Boot REST APIs.")
                                if "java.sql" in content:
                                    gaps.append(f"Gap: {file} uses raw JDBC. Recommendation: Adopt Spring Data JPA with Neon.")
                                if "HttpSession" in content:
                                    gaps.append(f"Gap: {file} uses HttpSession for state management. Recommendation: Use stateless JWT or Spring Session.")
                                if "System.out.println" in content or "log4j" in content:
                                    gaps.append(f"Gap: {file} uses outdated logging. Recommendation: Adopt SLF4J with Logback.")
                                if "password" in content.lower() or "credential" in content.lower():
                                    gaps.append(f"Gap: {file} may contain hardcoded credentials. Recommendation: Use environment variables with Spring Security.")
                        except Exception as e:
                            print(f"Error: Failed to parse {file_path}: {str(e)}")
        except Exception as e:
            print(f"Error: Failed to walk source directory {source_dir}: {str(e)}")
    
    if not gaps:
        gaps.append("Gap: No modernization gaps identified due to missing analysis data. Recommendation: Ensure codebert_summary.py and SonarQube analysis complete successfully.")
    
    return gaps

def generate_gaps(reports_dir, output_path, entity_name="Policy", industry="Insurance"):
    """Generate modernization gaps using Router API with fallback."""
    codebert_summaries = parse_codebert_summary(reports_dir)
    sonar_issues = parse_sonar_report(reports_dir)
    token = os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        print("Error: HUGGINGFACE_TOKEN environment variable not set, using fallback.")
        gaps = generate_fallback_gaps(codebert_summaries, sonar_issues, source_dir="PolicyManagementJSP/src/main/java")
    else:
        gaps = generate_gaps_from_model(codebert_summaries, sonar_issues, token, source_dir="PolicyManagementJSP/src/main/java", entity_name=entity_name, industry=industry)
    
    # Ensure gaps are not empty
    if not gaps:
        print("Warning: No gaps generated, forcing fallback.")
        gaps = generate_fallback_gaps(codebert_summaries, sonar_issues, source_dir="PolicyManagementJSP/src/main/java")
    
    # Write gaps to output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Modernization Gaps\n\n")
            for gap in gaps:
                f.write(f"- {gap}\n")
        print(f"Generated gaps written to {output_path}")
    except Exception as e:
        print(f"Error: Failed to write to {output_path}: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-reports", required=True, help="Directory containing analysis reports")
    parser.add_argument("--output", required=True, help="Output path for gaps.md")
    parser.add_argument("--entity-name", default="Policy", help="Entity name (e.g., Policy)")
    parser.add_argument("--industry", default="Insurance", help="Industry (e.g., Insurance)")
    args = parser.parse_args()
    generate_gaps(args.analysis_reports, args.output, args.entity_name, args.industry)