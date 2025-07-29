# Insurance Policy Requirements

### File: PolicyDAO.java
Functional Requirements:
- FR1: The system should be able to search for policies based on a given policy number.
- FR2: The system should retrieve policy details such as ID, policy number, policy holder, and coverage amount from the database.

Non-Functional Requirements:
- NFR1: The system should establish a secure connection to the PostgreSQL database.
- NFR2: The system should handle database connections efficiently to ensure optimal performance.

### File: PolicySearchServlet.java
Functional Requirements:
- FR1: The system should allow users to search for policies based on a search query.
- FR2: The system should retrieve a list of policies matching the search query from the PolicyDAO.
- FR3: The system should forward the retrieved list of policies to the policySearch.jsp page for display.

Non-Functional Requirements:
- NFR1: The system should have low response time for searching policies to provide a seamless user experience.
- NFR2: The system should be able to handle concurrent search requests efficiently to support multiple users accessing the system simultaneously.

### File: Policy.java
Functional Requirements:
- FR1: The system should be able to create a Policy entity with specified attributes such as id, policy number, policy holder, customer name, premium, issue date, and coverage amount.
- FR2: The system should allow setting and getting values for each attribute of the Policy entity.

Non-Functional Requirements:
- NFR1: The system should ensure data integrity by validating inputs for attributes such as id, policy number, premium, issue date, and coverage amount.
- NFR2: The system should provide efficient performance for setting and getting Policy entity attributes to ensure responsiveness.
