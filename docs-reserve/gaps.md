# Gap Analysis

- Gap 1: No RESTful APIs
  - Impact: Prevents integration with modern systems (e.g., mobile apps, microservices).
  - Desired State: Implement Jakarta REST APIs using Supabase endpoints.
- Gap 2: Limited client-side interactivity
  - Impact: Poor user experience for dynamic filtering or sorting.
  - Desired State: Add AJAX with JavaScript or adopt PrimeFaces for rich components.
- Gap 3: No AI-driven insights
  - Impact: Missed opportunities for predictive analytics (e.g., policy risk scoring).
  - Desired State: Integrate Hugging Face models for AI recommendations.
- Gap 4: Suboptimal scalability
  - Impact: Application fails with 10,000+ users due to lack of connection pooling and load balancing.
  - Desired State: Deploy on cloud (e.g., Render.com) with Supabase connection pooling and Tomcat clustering.
