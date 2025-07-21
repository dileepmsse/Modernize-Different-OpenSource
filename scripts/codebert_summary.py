import argparse
import os
from pathlib import Path
import re
from openai import OpenAI
import time
import logging

# Set up logging to console and file for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('codebert_summary.log'),
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
    """Generate a summary for a Java file using Hugging Face Router API."""
    if not code:
        logger.warning(f"No content for {file_name}, using fallback")
        return generate_fallback_summary(code, file_name)
    
    if not token:
        logger.warning("HUGGINGFACE_TOKEN not set, using fallback")
        return generate_fallback_summary(code, file_name)
    
    try:
        client = OpenAI(
            api_key=token,
            base_url="https://router.huggingface.co/v1"
        )
        logger.info(f"Initialized Router API client for {file_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Router API client for {file_name}: {str(e)}")
        return generate_fallback_summary(code, file_name)
    
    # Truncate code to avoid exceeding context limit
    code = truncate_text(code, max_chars=2000)
    
    # Prompt for meaningful summary
    prompt = f"""
You are a Java code analysis expert. Analyze the following Java code and provide a concise summary (2–3 sentences, up to 512 tokens) of its functionality, architecture, and potential modernization issues. Focus on identifying legacy patterns (e.g., servlets, JSP, raw JDBC, outdated logging, hardcoded credentials) and suggest modern alternatives (e.g., Spring Boot, Spring Data JPA, SLF4J). Do not list code snippets, imports, or variable declarations; focus on behavior and improvements. Output only the summary text.

Code (File: {file_name}):
{code}
"""
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = client.chat.completions.create(
                model="microsoft/codebert-base",
                messages=[
                    {"role": "system", "content": "You are a Java code analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.7
            )
            summary = response.choices[0].message.content.strip()
            if summary:
                logger.info(f"Generated summary for {file_name}: {summary[:50]}...")
                return summary
            logger.warning(f"Empty summary from CodeBERT for {file_name}, attempt {attempt + 1}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Exception in CodeBERT inference for {file_name} (attempt {attempt + 1}): {str(e)}")
            if "rate limit" in str(e).lower() or "429" in str(e):
                time.sleep(2 ** attempt)
                continue
            break
    
    logger.warning(f"CodeBERT failed for {file_name}, using fallback")
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

def generate_codebert_summary(source_dir, output_path):
    """Generate CodeBERT summaries for all Java files in source_dir."""
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
    
    # Ensure non-empty output
    if not summaries:
        logger.warning("No summaries generated, adding default")
        summaries.append({
            "file": "N/A",
            "summary": "No Java files found or processed successfully in the source directory. Ensure PolicyManagementJSP/src/main/java contains valid Java files and HUGGINGFACE_TOKEN is set."
        })
    
    # Write summaries to output
    output_path = Path(output_path)
    logger.info(f"Writing summaries to: {output_path}")
    os.makedirs(output_path.parent, exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# CodeBERT Summaries\n\n")
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
    parser.add_argument("--output", required=True, help="Output path for codebert-summary.md")
    args = parser.parse_args()
    generate_codebert_summary(args.source_dir, args.output)