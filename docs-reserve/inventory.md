# System Inventory

- Components: JavaServer Pages (JSP 3.1), Jakarta Servlet 6.0, JSTL 2.0, Supabase PostgreSQL
- Features: Policy search by number or customer name, displayed in a responsive HTML table
- Database: Policies table (Id, PolicyNumber, CustomerName, Premium, IssueDate)
- Dependencies: Apache Tomcat 10.1, Java 17, PostgreSQL JDBC driver (42.7.3), Supabase Java client (0.1.0)
- Issues: 
  - Slow queries (estimated 5-10s due to `ILIKE '%query%'` without index)
  - No RESTful APIs, limiting integration
  - Non-optimal scalability, fails at 10,000+ concurrent users
  - UI lacks advanced interactivity (e.g., AJAX sorting/filtering)