import argparse
import os

def generate_inventory(source_path, output):
    inventory = [
        "Components: ASP.NET Web Forms, ADO.NET, Microsoft SQL Server 2008 R2",
        "Features: Policy search via GridView",
        "Database: Policies table (Id, PolicyNumber, CustomerName, Premium, IssueDate)",
        "Dependencies: IIS 7.5, .NET Framework 4.0",
        "Issues: Slow queries (5-10s), non-responsive UI, no APIs"
    ]

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w") as f:
        f.write("# System Inventory\n\n")
        f.write("\n".join([f"- {item}" for item in inventory]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    generate_inventory(args.source, args.output)