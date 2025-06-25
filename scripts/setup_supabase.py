from supabase import create_client

def setup_supabase(url, key):
    supabase = create_client(url, key)
    # Create Policies table
    schema = """
    CREATE TABLE IF NOT EXISTS Policies (
        Id SERIAL PRIMARY KEY,
        PolicyNumber VARCHAR(50) NOT NULL,
        CustomerName VARCHAR(100) NOT NULL,
        Premium DECIMAL(18,2) NOT NULL,
        IssueDate TIMESTAMP NOT NULL
    );
    INSERT INTO Policies (PolicyNumber, CustomerName, Premium, IssueDate)
    VALUES
        ('POL-001', 'John Doe', 1200.00, '2010-01-15'),
        ('POL-002', 'Jane Smith', 1500.00, '2010-03-20'),
        ('POL-003', 'Acme Corp', 2500.00, '2010-06-10')
    ON CONFLICT DO NOTHING;
    """
    supabase.rpc("execute_sql", {"query": schema}).execute()

if __name__ == "__main__":
    import os
    setup_supabase(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])