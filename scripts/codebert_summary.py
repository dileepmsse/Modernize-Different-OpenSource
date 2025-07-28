import argparse
import os
import time
import logging
import requests
from pathlib import Path

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unixcoder_summary.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

def truncate_text(text, max_chars=2000):
    """Truncate text to fit model context limit."""
    if len(text) <= max_chars:
        return text
    logger.warning(f"Truncating input text to {max_chars} characters")
    return text[:max_chars] + "... [truncated]"

def generate_summary(code, file_name, token):
    """Generate a summary for a Java file using UniXcoder via Hugging Face Inference API."""
    if not code:
        logger.warning(f"No content for {file_name}, using fallback")
        return generate_fallback_summary(code, file_name)

    if not token:
        logger.warning("HUGGINGFACE_TOKEN not set, using fallback")
        return generate_fallback_summary(code, file_name)

    code = truncate_text(code, max_chars=2000)
    prompt = f"Summarize the following Java code in plain English:\n\n{code}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7
        }
    }

    url = "https://router.huggingface.co/hf-inference/models/google/pegasus-xsum"

    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"result: {result}")
            if isinstance(result, list) and "generated_text" in result[0]:
                summary = result[0]["generated_text"].strip()
                logger.info(f"Generated summary for {file_name}: {summary[:50]}...")
                return summary
            else:
                logger.warning(f"Unexpected response format for {file_name}, attempt {attempt + 1}")
        except Exception as e:
            logger.error(f"Exception during UniXcoder inference for {file_name} (attempt {attempt + 1}): {str(e)}")
            if "rate limit" in str(e).lower() or "429" in str(e):
                time.sleep(2 ** attempt)
                continue
            break

    logger.warning(f"UniXcoder failed for {file_name}, using fallback")
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

def generate_unixcoder_summary(source_dir, output_path):
    """Generate UniXcoder summaries for all Java files in source_dir."""
    logger.info(f"Processing source directory: {source_dir}")
    source_path = Path(source_dir)
    if not source_path.exists():
        logger.error(f"Source directory {source_dir} does not exist")
        raise FileNotFoundError(f"Source directory {source_dir} does not exist")

    token = os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        logger.warning("HUGGINGFACE_TOKEN not set, using fallback for all files")

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
        summary = generate_fallback_summary(code, str(relative_path)) if not token else generate_summary(code, str(relative_path), token)
        summaries.append({"file": str(relative_path), "summary": summary})

    if not summaries:
        logger.warning("No summaries generated, adding default")
        summaries.append({
            "file": "N/A",
            "summary": "No Java files found or processed successfully in the source directory. Ensure the directory contains valid Java files and HUGGINGFACE_TOKEN is set."
        })

    output_path = Path(output_path)
    logger.info(f"Writing summaries to: {output_path}")
    os.makedirs(output_path.parent, exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# UniXcoder Summaries\n\n")
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
    generate_unixcoder_summary(args.source_dir, args.output)
# This script generates summaries for Java files using UniXcoder via Hugging Face Inference API.
# It reads Java files, generates summaries, and writes them to a markdown file. 