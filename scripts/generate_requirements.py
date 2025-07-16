import os
import argparse
import requests
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate

def generate_requirements(source_path, entity_name, industry, output, token):
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
        huggingfacehub_api_token=token,
        max_new_tokens=512
    )
    prompt = PromptTemplate(
        input_variables=["code", "entity", "industry"],
        template="Extract functional and non-functional requirements for a {industry} system managing {entity} from this code: {code}"
    )

    requirements = []
    for root, _, files in os.walk(source_path):
        for file in files:
            if file.endswith(".cs"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    code = f.read()[:512]  # Truncate for API limits
                result = llm.invoke(prompt.format(code=code, entity=entity_name, industry=industry))
                requirements.append(result)
   
    os.makedirs(os.path.dirname(output), exist_ok=True)
    # Write the requirements to the output file
    if not requirements:
        requirements.append("No requirements extracted.")
    requirements = [f"- {req}" for req in requirements]
    
    with open(output, "w") as f:
        f.write(f"# {industry} {entity_name} Requirements\n\n")
        # f.write("### Functional Requirements\n")
        # f.write(f"- FR1: Search {entity_name.lower()} by number or name.\n")
        # f.write(f"- FR2: Display {entity_name.lower()} details (number, name, premium, issue date).\n")
        # f.write("\n### Non-Functional Requirements\n")
        # f.write("- NFR1: Response time <10 seconds (current: 5-10s).\n")
        # f.write("- NFR2: Support 10,000 concurrent users (current: fails at 1,000).\n")
        f.write("\n### AI-Generated Insights\n" + "\n".join(requirements))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--entity", required=True)
    parser.add_argument("--industry", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    generate_requirements(args.source, args.entity, args.industry, args.output, os.environ["HUGGINGFACE_TOKEN"])