import os
import argparse
from pathlib import Path
from openai import AzureOpenAI

def extract_requirements_from_code(code, entity, industry, client, deployment):
    """Call Azure OpenAI to extract requirements from code."""
    prompt = f"""
You are a software analyst. Given the following Java code for a {industry} system managing {entity} entities, extract both functional and non-functional requirements.

Return the output in this format:
Functional Requirements:
- FR1: <requirement>
- FR2: <requirement>

Non-Functional Requirements:
- NFR1: <requirement>
- NFR2: <requirement>

Code:
{code}
"""
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a software analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        result_text = response.choices[0].message.content.strip()
        print("Raw Azure OpenAI response:\n", result_text)
        return result_text
    except Exception as e:
        print(f"Error during Azure OpenAI call: {str(e)}")
        return None

def generate_requirements(source_path, entity_name, industry, output_path):
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not key or not deployment:
        print("Error: One or more Azure OpenAI environment variables are not set.")
        return

    client = AzureOpenAI(
        api_key=key,
        api_version="2024-12-01-preview",
        azure_endpoint=endpoint
    )

    requirements = []
    for root, _, files in os.walk(source_path):
        for file in files:
            # Support multiple code file formats
            supported_extensions = [".java", ".cs", ".py", ".js", ".ts"]
            if any(file.endswith(ext) for ext in supported_extensions):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        if not code.strip():
                            continue
                        print("Trigerred Azure OpenAI:\n", file_path)
                        result = extract_requirements_from_code(code, entity_name, industry, client, deployment)
                        if result:
                            requirements.append(f"### File: {file}\n{result}\n")
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {industry} {entity_name} Requirements\n\n")
        if requirements:
            f.write("\n".join(requirements))
        else:
            f.write("No requirements extracted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to source directory containing .cs files")
    parser.add_argument("--entity", required=True, help="Entity name (e.g., Policy)")
    parser.add_argument("--industry", required=True, help="Industry name (e.g., Insurance)")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    args = parser.parse_args()

    generate_requirements(args.source, args.entity, args.industry, args.output)

    # Example launch.json configuration for VS Code debugging
    # Place this in a .vscode/launch.json file in your project root

    # {
    #     "version": "0.2.0",
    #     "configurations": [
    #         {
    #             "name": "Python: generate_requirements",
    #             "type": "python",
    #             "request": "launch",
    #             "program": "${workspaceFolder}/scripts/generate_requirements.py",
    #             "console": "integratedTerminal",
    #             "args": [
    #                 "--source", "/path/to/source",
    #                 "--entity", "Policy",
    #                 "--industry", "Insurance",
    #                 "--output", "/path/to/output/requirements.md"
    #             ],
    #             "env": {
    #                 "AZURE_OPENAI_ENDPOINT": "https://your-endpoint.openai.azure.com/",
    #                 "AZURE_OPENAI_KEY": "your-azure-openai-key",
    #                 "AZURE_OPENAI_DEPLOYMENT": "your-deployment-name"
    #             }
    #         }
    #     ]
    # }