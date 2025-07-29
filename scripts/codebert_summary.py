import argparse
import os
import time
import logging
import openai

from openai import AzureOpenAI

from pathlib import Path

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('azure_openai_summary.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
api_key = os.environ.get("AZURE_OPENAI_KEY")
deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

def read_java_file(file_path):
    """Read content of a Java file."""
    logger.info(f"Attempting to read file: {file_path}")
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            logger.info(f"Successfully read {file_path}, length: {len(content)} characters")
            return content
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {str(e)}")
        return ""

def truncate_text(text, max_chars=8000):
    """Truncate text to fit model context limit."""
    if len(text) <= max_chars:
        return text
    logger.warning(f"Truncating input text to {max_chars} characters")
    return text[:max_chars] + "... [truncated]"

def generate_summary(code, file_name):
    """Generate a summary for a Java file using Azure OpenAI."""
    if not code:
        logger.warning(f"No content for {file_name}, using fallback")
        return generate_fallback_summary(code, file_name)

    if not endpoint or not api_key or not deployment:
        logger.warning("Azure OpenAI credentials not set, using fallback")
        return generate_fallback_summary(code, file_name)

    openai.api_type = "azure"
    openai.api_base = endpoint
    openai.api_version = "2023-07-01"
    openai.api_key = api_key

    prompt = (
        "You are a software architect. Summarize the following Java code in plain English, "
        "highlighting its purpose and any architectural or security concerns:\n\n"
        f"{truncate_text(code)}"
    )

    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version="2024-12-01-preview"
    )

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a software architect who summarizes Java code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=512
            )
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary for {file_name}: {summary[:50]}...")
            return summary
        except Exception as e:
            logger.error(f"Azure OpenAI error for {file_name} (attempt {attempt + 1}): {str(e)}")
            time.sleep(2 ** attempt)

    logger.warning(f"Azure OpenAI failed for {file_name}, using fallback")
    return generate_fallback_summary(code, file_name)

def generate_fallback_summary(code, file_name):
    """Generate a basic summary using rule-based logic."""
    summary = f"{file_name} is a Java class."
    if not code:
        summary += " No code content available, possibly due to file read error."
        return summary

    if "javax.servlet" in code or "jakarta.servlet" in code:
        summary += " It implements a servlet to handle HTTP requests and responses, indicating a legacy web architecture. Migrate to Spring Boot REST APIs for modern scalability."
    if "java.sql" in code:
        summary += " It uses raw JDBC for database operations, which is error-prone. Adopt Spring Data JPA with Neon for modern ORM."
    if "HttpSession" in code:
        summary += " It relies on HttpSession for state management, which can complicate scaling. Use stateless JWT or Spring Session."
    if "System.out.println" in code or "log4j" in code:
        summary += " It uses outdated logging (e.g., System.out or Log4j). Switch to SLF4J with Logback for better logging."
    if "password" in code.lower() or "credential" in code.lower():
        summary += " It may contain hardcoded credentials, posing a security risk. Use environment variables with Spring Security."
    if "implements Serializable" in code:
        summary += " It defines a serializable entity, likely a data model. Consider using Lombok to reduce boilerplate."

    logger.info(f"Generated fallback summary for {file_name}: {summary[:50]}...")
    return summary

def generate_summaries(source_dir, output_path):
    """Generate summaries for all Java files in source_dir."""
    logger.info(f"Processing source directory: {source_dir}")
    source_path = Path(source_dir)
    if not source_path.exists():
        logger.error(f"Source directory {source_dir} does not exist")
        raise FileNotFoundError(f"Source directory {source_dir} does not exist")

    summaries = []
    java_files = list(source_path.rglob("*.java"))
    if not java_files:
        logger.warning(f"No Java files found in {source_dir}")

    for file_path in java_files:
        relative_path = file_path.relative_to(source_path.parent)
        logger.info(f"Processing file: {relative_path}")
        code = read_java_file(file_path)
        if not code:
            summaries.append({
                "file": str(relative_path),
                "summary": f"{relative_path} could not be read, possibly due to file access issues."
            })
            continue
        summary = generate_summary(code, str(relative_path))
        summaries.append({"file": str(relative_path), "summary": summary})

    if not summaries:
        logger.warning("No summaries generated, adding default")
        summaries.append({
            "file": "N/A",
            "summary": "No Java files found or processed successfully in the source directory. Ensure the directory contains valid Java files and Azure OpenAI credentials are set."
        })

    output_path = Path(output_path)
    logger.info(f"Writing summaries to: {output_path}")
    os.makedirs(output_path.parent, exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Java Code Summaries\n\n")
            for entry in summaries:
                f.write(f"File: {entry['file']}\n")
                f.write(f"Summary: {entry['summary']}\n\n")
        logger.info(f"Successfully wrote summaries to {output_path}")
    except Exception as e:
        logger.error(f"Failed to write to {output_path}: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", help="Directory containing Java source files")
    parser.add_argument("--output", required=True, help="Output path for summary markdown file")
    args = parser.parse_args()
    generate_summaries(args.source_dir, args.output)

# This script generates summaries for Java files using Azure OpenAI, with robust error handling and logging.