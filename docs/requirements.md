# Insurance Policy Requirements

### File: PolicyDAO.java
Functional Requirements:
- FR1: The system should be able to search for policies based on a given policy number.
- FR2: The system should retrieve policy details such as id, policy number, policy holder, and coverage amount from the database.

Non-Functional Requirements:
- NFR1: The system should establish a secure connection to the PostgreSQL database to retrieve policy information.
- NFR2: The system should handle database connections efficiently to ensure optimal performance during policy searches.

### File: PolicySearchServlet.java
Functional Requirements:
- FR1: The system should allow users to search for policies based on a search query.
- FR2: The system should retrieve a list of policies matching the search query from the PolicyDAO.
- FR3: The system should forward the retrieved list of policies to the policySearch.jsp page for display.

Non-Functional Requirements:
- NFR1: The system should have low response time for searching policies to provide a seamless user experience.
- NFR2: The system should be secure to protect policy data and prevent unauthorized access.
- NFR3: The system should be scalable to handle a large number of concurrent policy search requests efficiently.

### File: Policy.java
Functional Requirements:
- FR1: The system should be able to create a Policy entity with the provided attributes such as id, policy number, policy holder, customer name, premium, issue date, and coverage amount.
- FR2: The system should allow setting and getting the values of the Policy attributes such as id, policy number, customer name, premium, and issue date.

Non-Functional Requirements:
- NFR1: The system should ensure data consistency by validating the input values for attributes like id, premium, and coverage amount to prevent data corruption.
- NFR2: The system should be designed to handle a large number of Policy entities efficiently to ensure scalability and performance.
