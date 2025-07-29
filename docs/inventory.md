## System Inventory

### Components
- Frameworks: Servlet API, JSP
- Architecture style: Model-View-Controller (MVC)

### Features
- List policies
- View policy details
- Generate policy report

### Database
- Schema: policydb
- Tables: policies
  - Fields:
    - id (int)
    - policy_number (String)
    - customer_name (String)
    - start_date (Date)
    - end_date (Date)

### Dependencies
- Servlet API
- JDBC
- JSP

### Issues
- Hardcoded credentials in `LegacyServlet.java`
- Outdated architecture with direct JDBC connections and SQL queries in servlets