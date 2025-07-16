import os
import argparse
import requests
import re

file_types = [".cs", ".java", ".js", ".py", ".rb", ".go", ".ts", ".cpp", ".c", ".php", ".swift"]

def clean_code(code):
    """Clean code by removing comments and normalizing whitespace."""
    # Remove block comments (/* ... */)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Remove line comments (// ...)
    code = re.sub(r'//.*?\n', '\n', code)
    # Normalize whitespace
    code = re.sub(r'\s+', ' ', code.strip())
    return code[:1000]  # Truncate to 1000 chars for API limits

def process_file(root, file, headers, summaries):
    file_path = os.path.join(root, file)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        # Clean and truncate code
        cleaned_code = clean_code(code)
        if not cleaned_code:
            summaries.append(f"File: {file}\nSummary: Empty or invalid code after cleaning\n")
            return
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
            headers=headers,
            json={
                "inputs": cleaned_code,
                "parameters": {"max_length": 100, "min_length": 30}
            }
        )
        if response.status_code == 200:
            summary = response.json()[0]["summary_text"]
            summaries.append(f"File: {file}\nSummary: {summary}\n")
        else:
            summaries.append(f"File: {file}\nSummary: Error processing code: {response.status_code}\n")
    except Exception as e:
        summaries.append(f"File: {file}\nSummary: Exception occurred: {str(e)}\n")

def summarize_code(source_path, token):
    headers = {"Authorization": f"Bearer {token}"}
    summaries = []
    for root, _, files in os.walk(source_path):
        for file in files:
            if any(file.endswith(file_type) for file_type in file_types):
                process_file(root, file, headers, summaries)
    os.makedirs("reports", exist_ok=True)
    with open("reports/codebert-summary.md", "w", encoding="utf-8") as f:
        f.write("# CodeBERT Summaries\n\n" + "\n".join(summaries))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", help="Path to source code")
    parser.add_argument("--output", default="reports/codebert-summary.md", help="Output file for summaries")
    args = parser.parse_args()
    token = os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_TOKEN environment variable not set")
    summarize_code(args.source_path, token)