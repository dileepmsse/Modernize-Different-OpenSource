import os
import argparse
from pathlib import Path
from openai import AzureOpenAI

def generate_requirements(source_path, entity_name, industry, output_path):
    # Load Azure OpenAI credentials from environment
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not key or not deployment:
        raise EnvironmentError("Missing Azure OpenAI environment variables.")

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=key,
        api_version="2024-02-15-preview",
        azure_endpoint=endpoint
    )

    requirements = []

    for root, _, files in os.walk(source_path):
        for file in files:
            if file.endswith(".cs"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue

                prompt = (
                    f"You are a software analyst. Extract functional and non-functional requirements "
                    f"for a {industry} system managing {entity_name} entities based on the following C# code:\n\n{code}\n\n"
                    f"List the requirements clearly under two headings:\n"
                    f"### Functional Requirements\n- ...\n\n### Non-Functional Requirements\n- ..."
                )

                try:
                    response = client.chat.completions.create(
                        model=deployment,
                        messages=[
                            {"role": "system", "content": "You are a software analyst."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=800,
                        temperature=0.5
                    )
                    result_text = response.choices[0].message.content.strip()
                    requirements.append(f"## File: {file}\n{result_text}\n")
                except Exception as e:
                    print(f"Error generating requirements for {file_path}: {e}")

    # Write the requirements to the output markdown file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {industry} {entity_name} Requirements\n\n")
        if requirements:
            f.write("\n".join(requirements))
        else:
            f.write("No requirements extracted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to source code directory")
    parser.add_argument("--entity", required=True, help="Entity name (e.g., Policy)")
    parser.add_argument("--industry", required=True, help="Industry name (e.g., Insurance)")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    args = parser.parse_args()

    generate_requirements(args.source, args.entity, args.industry, args.output)
