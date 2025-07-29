import os
import argparse
from pathlib import Path
from openai import AzureOpenAI

def read_java_files(source_dir):
    """Read all Java files from the source directory and return their contents."""
    code_snippets = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            supported_extensions = [".java", ".kt", ".scala", ".groovy"]
            if any(file.endswith(ext) for ext in supported_extensions):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        code_snippets.append(f"// File: {file}\n{code}")
                except Exception as e:
                    print(f"Warning: Failed to read {file_path}: {str(e)}")
    return "\n\n".join(code_snippets)

def build_prompt(codebase_text):
    """Construct a prompt to instruct the model to generate a system inventory."""
    return f"""
You are a software architect. Analyze the following Java codebase and generate a system inventory in markdown format.

The inventory should include:
- Components (e.g., frameworks, libraries, architecture style)
- Features (e.g., search, CRUD, authentication)
- Database (e.g., schema, tables, fields)
- Dependencies (e.g., servlet API, JDBC, JSP)
- Issues (e.g., hardcoded credentials, outdated architecture)

Codebase:
{codebase_text}

Return only the markdown content.
"""

def call_azure_openai(prompt):
    """Call Azure OpenAI to generate the system inventory."""
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not key or not deployment:
        raise EnvironmentError("Missing one or more Azure OpenAI environment variables.")

    client = AzureOpenAI(
        api_key=key,
        api_version="2024-02-15-preview",
        azure_endpoint=endpoint
    )

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a software architect."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

def write_output(markdown_text, output_path):
    """Write the markdown output to a file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    print(f"System inventory written to {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Directory containing Java source files")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    args = parser.parse_args()

    codebase_text = read_java_files(args.source)
    if not codebase_text.strip():
        print("No Java files found or all files are empty.")
        return

    prompt = build_prompt(codebase_text)
    markdown_text = call_azure_openai(prompt)
    write_output(markdown_text, args.output)

if __name__ == "__main__":
    main()
    # Example launch.json for VS Code debugging
    # Save this as .vscode/launch.json in your project root

    # {
    #     "version": "0.2.0",
    #     "configurations": [
    #         {
    #             "name": "Python: Generate Inventory",
    #             "type": "python",
    #             "request": "launch",
    #             "program": "${workspaceFolder}/scripts/generate_inventory.py",
    #             "args": [
    #                 "--source", "${workspaceFolder}/path/to/source",
    #                 "--output", "${workspaceFolder}/output/inventory.md"
    #             ],
    #             "console": "integratedTerminal"
    #         }
    #     ]
    # }
