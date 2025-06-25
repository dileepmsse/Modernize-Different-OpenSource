# Legacy Modernization Demo: Policy Management System

This repository provides an open-source, AI-powered framework for analyzing and documenting legacy web applications, demonstrated with a JavaServer Pages (JSP) insurance policy management system (`PolicyManagementJSP`). It automates reverse-engineering (Step 1: Legacy Analysis) and requirements documentation (Step 2: Requirements Documentation) using a cloud-based GitHub Actions pipeline, leveraging tools like Hugging Face’s CodeBERT, LangChain, SonarQube, and Supabase PostgreSQL. The framework is reusable across industries (e.g., insurance, banking, healthcare) and sellable to enterprises seeking cost-effective modernization with zero licensing costs.

## Table of Contents
- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the Pipeline](#running-the-pipeline)
- [Deploying the JSP Application](#deploying-the-jsp-application)
- [Pipeline Outputs](#pipeline-outputs)
- [Reusability](#reusability)
- [Contributing](#contributing)
- [License](#license)

## Overview
The `PolicyManagementJSP` application is a legacy-style web app built with JSP 3.1, Jakarta Servlet 6.0, JSTL 2.0, and Supabase PostgreSQL, mimicking a 2010s-era insurance policy management system. It supports searching policies by number or customer name, displaying results in a responsive HTML table. The pipeline analyzes this app to produce:
- **System Inventory**: Components, features, and issues.
- **Requirements**: Functional and non-functional requirements (IEEE 830-compliant).
- **Gap Analysis**: Current vs. desired state (e.g., no APIs, scalability limits).
- **Process Flow**: Visual diagram of the search process.

The pipeline uses open-source AI tools (CodeBERT, LangChain with Mixtral-8x7B) for code summarization and requirements extraction, ensuring enterprise-grade deliverables with auditability (e.g., SOC 2, GDPR).

## Repository Structure

my-repo/├── PolicyManagementJSP/│   ├── src/main/java/com/example/    # Java classes (Policy, PolicyDAO, PolicySearchServlet)│   ├── src/main/webapp/              # JSP (policySearch.jsp), CSS, web.xml│   ├── pom.xml                       # Maven build configuration├── scripts/                          # Pipeline scripts│   ├── codebert_summary.py           # CodeBERT analysis│   ├── setup_supabase.py             # Supabase schema setup│   ├── analyze_queries.py            # SQL query analysis│   ├── generate_requirements.py      # Requirements generation│   ├── generate_gaps.py              # Gap analysis│   ├── generate_inventory.py         # System inventory├── docs/                             # Pipeline outputs│   ├── inventory.md                  # System components and issues│   ├── requirements.md               # Functional/non-functional requirements│   ├── gaps.md                       # Gap analysis│   ├── process-flow.png              # Process flow diagram├── .github/workflows/│   ├── legacy-analysis-pipeline.yml  # GitHub Actions pipeline├── README.md                         # This file

## Features
- **Legacy Analysis**: Static code analysis (SonarQube, Checkstyle) and AI-driven summarization (CodeBERT) of JSP/Java code.
- **Dynamic Analysis**: SQL query performance analysis via Supabase PostgreSQL.
- **Documentation**: Automated generation of IEEE 830-compliant requirements, system inventory, and gap analysis.
- **Cloud-Based**: Fully managed with Supabase, SonarCloud, and Hugging Face APIs, no self-hosted infrastructure.
- **Reusable**: Configurable for other entities (e.g., Account) or industries (e.g., Banking).
- **Enterprise-Ready**: Audit-ready Markdown outputs, Obsidian-compatible, with trending AI tools (800k+ GitHub stars).

## Prerequisites
- **GitHub Account**: For hosting the repository and running Actions.
- **Supabase Account**: Free tier for hosted PostgreSQL (5-minute setup).
- **SonarCloud Account**: Free for public repos, $10/month for private.
- **Hugging Face Account**: Free for <1,000 API requests/day, $9/month for Pro.
- **Java 17**: For local development (optional, pipeline uses `actions/setup-java@v4`).
- **Maven**: For building the JSP app (optional, pipeline handles builds).
- **Tomcat 10.1**: For local deployment (optional, use Render.com for cloud).

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/my-repo.git
   cd my-repo


Set Up Supabase:

Create a free Supabase project at supabase.com.
Note the project’s API URL and anon key (Settings > API).
The pipeline’s setup_supabase.py creates the Policies table automatically.


Set Up SonarCloud:

Sign up at sonarcloud.io.
Create a project for your repository and generate a SONAR_TOKEN.
Configure the project key in SonarCloud.


Set Up Hugging Face:

Sign up at huggingface.co.
Generate an API token (Settings > Access Tokens).
Ensure free tier limits (<1,000 requests/day) or upgrade to Pro ($9/month).


Configure GitHub Secrets:

Go to Settings > Secrets and variables > Actions in your GitHub repository.
Add the following secrets:
SONAR_TOKEN: From SonarCloud.
SONAR_HOST_URL: https://sonarcloud.io.
HUGGINGFACE_TOKEN: From Hugging Face.
SUPABASE_URL: From Supabase (Settings > API > URL).
SUPABASE_KEY: From Supabase (Settings > API > anon key).




Create Process Flow Diagram:

Open diagrams.net.
Use docs/process-flow.png description to create a diagram:
Flow: User → Form Submit (policySearch.jsp) → PolicySearchServlet → PolicyDAO → Supabase → policySearch.jsp → User.
Export as docs/process-flow.png (800x600 resolution).


Commit to repository:git add docs/process-flow.png
git commit -m "Add process flow diagram"
git push origin main





Running the Pipeline
The pipeline automates legacy analysis and documentation. Trigger it manually or on push to main:
gh workflow run legacy-analysis-pipeline.yml \
  -f source_path=PolicyManagementJSP \
  -f entity_name=Policy \
  -f industry=Insurance


Jobs:
static-analysis: Runs SonarQube, Checkstyle, and CodeBERT on PolicyManagementJSP/src/main/java.
dynamic-analysis: Analyzes SQL queries via Supabase (analyze_queries.py).
documentation: Generates docs/ files (inventory.md, requirements.md, gaps.md).


Duration: ~20 minutes (static: 8min, dynamic: 4min, documentation: 8min).
Outputs: Committed to docs/; check GitHub Actions logs for details.

Deploying the JSP Application
For testing or demo purposes, deploy PolicyManagementJSP locally or on a cloud platform:

Local Deployment:

Install Java 17 and Maven.
Build the WAR file:cd PolicyManagementJSP
mvn clean package


Deploy to Tomcat 10.1:
Copy target/PolicyManagementJSP.war to tomcat/webapps/.
Start Tomcat: tomcat/bin/startup.sh (Linux/Mac) or tomcat\bin\startup.bat (Windows).


Access at http://localhost:8080/PolicyManagementJSP/policySearch.jsp.


Cloud Deployment (Recommended):

Use Render.com free tier:
Create a Web Service, select your GitHub repository.
Set build command: mvn clean package -f PolicyManagementJSP/pom.xml.
Set start command: java -jar $JAVA_OPTS target/PolicyManagementJSP.war.
Add environment variables: SUPABASE_URL, SUPABASE_KEY.


Access at https://<your-render-url>/PolicyManagementJSP/policySearch.jsp.



Pipeline Outputs
The pipeline generates the following files in docs/:

inventory.md: Lists components (JSP, Servlet, Supabase), features (policy search), and issues (slow queries, no APIs).
requirements.md: IEEE 830-compliant functional (e.g., search policies) and non-functional (e.g., <5s response) requirements, with AI insights.
gaps.md: Identifies gaps (e.g., no REST APIs, limited interactivity) and desired states (e.g., cloud scaling).
process-flow.png: Manual Draw.io diagram of the search process (user → JSP → servlet → Supabase → JSP).

View outputs in GitHub Pages (enable in Settings > Pages) or Obsidian for client presentations.
Reusability
Customize the framework for other legacy systems:

Change Source Code: Replace PolicyManagementJSP/ with another Java app (e.g., BankingApp/).
Update Entity: Set entity_name (e.g., Account) in pipeline inputs.
Switch Industry: Set industry (e.g., Banking) to tailor requirements.
Adapt Schema: Modify setup_supabase.py for other tables (e.g., Accounts).
Pipeline Scripts: codebert_summary.py, generate_requirements.py, etc., support .java and other languages.

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch: git checkout -b feature-name.
Commit changes: git commit -m "Add feature".
Push to branch: git push origin feature-name.
Open a pull request.

Report issues in the GitHub Issues tab.
License
This project is licensed under the xxx License. See LICENSE for details.

Contact: For enterprise pilots ($15,000 for tailored analysis), reach out via GitHub Issues or email (placeholder: dileepmsse@yahoo.com).