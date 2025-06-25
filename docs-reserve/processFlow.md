Placeholder for process-flow.png (to be created in Draw.io)

Description:
- Diagram Title: Policy Search Process Flow
- Components:
  1. User: Submits search query via form in policySearch.jsp
  2. PolicySearch.jsp: Renders HTML form and table, uses JSTL for iteration
  3. PolicySearchServlet: Handles POST request, invokes PolicyDAO
  4. PolicyDAO: Queries Supabase PostgreSQL with parameterized SQL
  5. Supabase PostgreSQL: Returns policy records
  6. PolicySearchServlet: Sets results in request scope, forwards to policySearch.jsp
  7. PolicySearch.jsp: Displays results in HTML table
- Flow:
  - User → Form Submit (POST /search) → PolicySearchServlet → PolicyDAO → Supabase → PolicyDAO → PolicySearchServlet → PolicySearch.jsp → User
- Notes:
  - Use rectangles for components, arrows for flow.
  - Highlight Supabase as a cloud database.
  - Export as PNG with 800x600 resolution.