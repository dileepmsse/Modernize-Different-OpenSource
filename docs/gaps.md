# Modernization Gaps

- Gap: Servlet-based architecture detected. Legacy Java servlets are used for handling HTTP requests and responses.
- Gap: Raw JDBC usage is detected in PolicyServlet.java. This approach can lead to code that is hard to maintain and test.
- Gap: JSP-based UI rendering is detected in Policy.jsp. JSPs can be limiting and harder to maintain compared to modern front-end frameworks.
- Gap: Outdated Java packages (jakarta.servlet, JAKARTA.http.Servlet, Java.IO.PrintWriter, Java.sql, Java.util) are used in LegacyServlet.java and PolicyServlet.java. These outdated packages can lead to compatibility issues with newer libraries and frameworks.
- Gap: Hardcoded database credentials are present in PolicyServlet.java. This approach is insecure and makes it difficult to manage and update credentials.
- Gap: The Policy class does not follow Java naming conventions (using uppercase for the first letter of the class name).
- Gap: The use of java.sql.Date in the Policy class is not recommended as it is outdated and lacks important features.
- Gap: The imports in the files are not organized and sorted. This can make the code harder to read and maintain.
- Gap: The SonarQube analysis shows that there are several code smells, technical debt, and maintainability issues in the codebase.
