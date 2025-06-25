from supabase import create_client
import os

def analyze_queries(url, key):
    supabase = create_client(url, key)
    query = "SELECT * FROM Policies WHERE PolicyNumber LIKE '%POL-001%';"
    # Simulate EXPLAIN (Supabase doesn't support EXPLAIN directly)
    response = supabase.rpc("execute_sql", {
        "query": f"EXPLAIN {query}"
    }).execute()
    # Mock analysis for demo
    return f"Query: {query}\nAnalysis: Table scan detected, estimated 5-10s due to LIKE '%...%'. Add index for performance."

if __name__ == "__main__":
    print(analyze_queries(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"]))