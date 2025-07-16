import os
import argparse
import requests

file_Types = [".cs", ".java", ".js", ".py", ".rb", ".go", ".ts", ".cpp", ".c", ".php", ".swift"]

def process_file(root, file, headers, summaries):
    file_path = os.path.join(root, file)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/codebert-base",
            headers=headers,
            json={"inputs": code[:512]}  # Truncate for API limits
        )
        if response.status_code == 200:
            summary = f"File: {file}\nSummary: {response.json()[0]['label'] == 'POSITIVE' and 'Handles business logic' or 'Renders UI'}\n"
            summaries.append(summary)
        else:
            summaries.append(f"File: {file}\nSummary: Error processing code\n")
    except Exception as e:
        summaries.append(f"File: {file}\nSummary: Exception occurred: {str(e)}\n")

def summarize_code(source_path, token):
    headers = {"Authorization": f"Bearer {token}"}
    summaries = []

    for root, _, files in os.walk(source_path):
        for file in files:
            if any(file.endswith(file_type) for file_type in file_Types):
                process_file(root, file, headers, summaries)

    os.makedirs("reports", exist_ok=True)
    with open("reports/codebert-summary.md", "w") as f:
        f.write("# CodeBERT Summaries\n\n" + "\n".join(summaries))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", help="Path to source code")
    args = parser.parse_args()
    summarize_code(args.source_path, os.environ["HUGGINGFACE_TOKEN"])