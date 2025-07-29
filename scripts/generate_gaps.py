import argparse
import os
import json
import re
import time
from pathlib import Path
from openai import AzureOpenAI

# -------------------- Parsing Functions --------------------

def parse_codebert_summary(report_path):
    summary_path = Path(report_path) / "codebert-summary.md"
    if not summary_path.exists():
        print(f"Warning: {summary_path} not found, relying on fallback.")
        return []
    summaries = []
    try:
        with open(summary_path, encoding="utf-8") as f:
            current_file = None
            for line in f:
                if line.startswith("File: "):
                    current_file = line.replace("File: ", "").strip()
                elif line.startswith("Summary: ") and current_file:
                    summary = line.replace("Summary: ", "").strip()
                    summaries.append({"file": current_file, "summary": summary})
    except Exception as e:
        print(f"Error: Failed to parse {summary_path}: {str(e)}")
    return summaries

def parse_sonar_report(report_path):
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

# -------------------- Context & Prompt Builders --------------------

def truncate_text(text, max_chars=1000):
    return text if len(text) <= max_chars else text[:max_chars] + "... [truncated]"

def build_context(summaries, sonar_issues, industry, entity_name):
    context = f"Industry: {industry}\nEntity: {entity_name}\n\nCode Analysis:\n"
    for summary in summaries:
        context += f"File: {summary['file']}\nSummary: {summary['summary']}\n\n"
    context += "SonarQube Issues:\n"
    for issue in sonar_issues:
        context += f"Component: {issue.get('component', 'unknown')}, Type: {issue.get('type', 'unknown')}, Message: {issue.get('message', 'No message')}\n"
    return truncate_text(context, max_chars=1000)

def build_prompt(context, industry, entity_name):
    return f"""
You are a software modernization expert. Based on the following code analysis and SonarQube issues, identify modernization gaps for a {industry} application managing {entity_name} entities. Focus on modernizing legacy projects. 
List modernization gaps in the following format:

Gap: <description>
Recommendation: <action>

Only return the list of gaps.

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

# -------------------- Gap Extraction & Generation --------------------

def extract_gaps_from_response(result_text):
    return re.findall(r"(?i)(?:-\s*)?Gap:.*Recommendation:.*(?=\n|$)", result_text)

def call_azure_openai_model(client, deployment, prompt, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a software modernization expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            result_text = response.choices[0].message.content.strip()
            print("Raw response from Azure OpenAI:{result_text}...")  # Log first 100 chars for debugging
            gaps = extract_gaps_from_response(result_text)
            if gaps:
                return gaps
            print("Warning: No valid gaps extracted from Azure OpenAI output.")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Error: Azure OpenAI error (attempt {attempt + 1}): {str(e)}")
            if "rate limit" in str(e).lower() or "429" in str(e):
                time.sleep(2 ** attempt)
                continue
            break
    return None

def generate_gaps_from_model(summaries, sonar_issues, source_dir, entity_name, industry):
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not key or not deployment:
        print("Error: One or more Azure OpenAI environment variables are not set. Using fallback.")
        return None

    try:
        client = AzureOpenAI(
            api_key=key,
            api_version="2024-12-01-preview",
            azure_endpoint=endpoint
        )
    except Exception as e:
        print(f"Error: Failed to initialize Azure OpenAI client: {str(e)}")
        return None

    context = build_context(summaries, sonar_issues, industry, entity_name)
    prompt = build_prompt(context, industry, entity_name)
    return call_azure_openai_model(client, deployment, prompt)

def generate_fallback_gaps(summaries, sonar_issues, source_dir):
    gaps = []
    for summary in summaries:
        s = summary["summary"].lower()
        f = summary["file"]
        if "servlet" in s:
            gaps.append(f"Gap: {f} uses legacy servlet architecture. Recommendation: Migrate to Spring Boot REST APIs.")
        if "dependency injection" in s:
            gaps.append(f"Gap: {f} lacks dependency injection. Recommendation: Adopt Spring Framework for DI.")
        if "jsp" in s:
            gaps.append(f"Gap: {f} uses JSP for rendering. Recommendation: Migrate to modern frontend framework like React or Angular.")
        if "jdbc" in s:
            gaps.append(f"Gap: {f} uses raw JDBC. Recommendation: Adopt Spring Data JPA with Neon for modern ORM.")
        if "logging" in s:
            gaps.append(f"Gap: {f} uses outdated logging. Recommendation: Adopt SLF4J with Logback.")
    for issue in sonar_issues:
        if issue.get("type") == "CODE_SMELL":
            gaps.append(f"Gap: Code smell in {issue.get('component', 'unknown')}: {issue.get('message', 'No message')}. Recommendation: Refactor code.")
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

# -------------------- Main Orchestration --------------------

def generate_gaps(reports_dir, output_path, entity_name="Policy", industry="Insurance", source_dir="PolicyManagementJSP/src/main/java"):
    codebert_summaries = parse_codebert_summary(reports_dir)
    sonar_issues = parse_sonar_report(reports_dir)
    gaps = generate_gaps_from_model(codebert_summaries, sonar_issues, source_dir, entity_name, industry)
    if not gaps:
        print("Warning: No gaps generated from model, using fallback.")
        gaps = generate_fallback_gaps(codebert_summaries, sonar_issues, source_dir)
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-reports", required=True, help="Directory containing analysis reports")
    parser.add_argument("--output", required=True, help="Output path for gaps.md")
    parser.add_argument("--entity-name", default="Policy", help="Entity name (e.g., Policy)")
    parser.add_argument("--industry", default="Insurance", help="Industry (e.g., Insurance)")
    args = parser.parse_args()
    generate_gaps(
        reports_dir=args.analysis_reports,
        output_path=args.output,
        entity_name=args.entity_name,
        industry=args.industry,
        source_dir="PolicyManagementJSP/src/main/java"
    )

if __name__ == "__main__":
    main()