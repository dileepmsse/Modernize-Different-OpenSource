# Insurance Policy Requirements

### Functional Requirements
- FR1: Search policies by policy number or customer name.
- FR2: Display policy details (policy number, customer name, premium, issue date) in a table.

### Non-Functional Requirements
- NFR1: Response time <5 seconds (current: 5-10s due to unoptimized queries).
- NFR2: Support 10,000 concurrent users (current: fails at ~1,000 users).
- NFR3: Mobile-responsive UI (current: achieved with CSS Flexbox).
- NFR4: Audit logging for compliance (current: not implemented).

### AI-Generated Insights
- Code analysis suggests tight coupling between `PolicySearchServlet` and `policySearch.jsp`, recommending MVC refactoring.
- Database queries use `ILIKE` for case-insensitive search, causing table scans; add index on `PolicyNumber`.
- JSP’s server-side rendering limits client-side interactivity; consider AJAX frameworks like PrimeFaces.
- Supabase integration is robust but lacks connection pooling for high concurrency.