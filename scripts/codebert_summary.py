import os
import argparse
import requests

def summarize_code(source_path, token):
    headers = {"Authorization": f"Bearer {token}"}
    summaries = []

    for root, _, files in os.walk(source_path):
        for file in files:
            if file.endswith(".cs"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    code = f.read()
                # Use Hugging Face Inference API with CodeBERT
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

    os.makedirs("reports", exist_ok=True)
    with open("reports/codebert-summary.md", "w") as f:
        f.write("# CodeBERT Summaries\n\n" + "\n".join(summaries))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", help="Path to source code")
    args = parser.parse_args()
    summarize_code(args.source_path, os.environ["HUGGINGFACE_TOKEN"])