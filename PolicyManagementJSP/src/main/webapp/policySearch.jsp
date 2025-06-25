<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt" prefix="fmt" %>
<!DOCTYPE html>
<html>
<head>
    <title>Insurance Policy Management</title>
    <link rel="stylesheet" href="resources/css/style.css"/>
</head>
<body>
    <h1>Insurance Policy Management</h1>
    <div class="search-box">
        <form action="search" method="post">
            <label>Search by Policy Number or Customer Name: </label>
            <input type="text" name="searchQuery" value="${param.searchQuery}"/>
            <input type="submit" value="Search"/>
        </form>
    </div>
    <c:if test="${not empty requestScope.policies}">
        <table class="table">
            <tr>
                <th>Policy Number</th>
                <th>Customer Name</th>
                <th>Premium</th>
                <th>Issue Date</th>
            </tr>
            <c:forEach items="${requestScope.policies}" var="policy">
                <tr>
                    <td>${policy.policyNumber}</td>
                    <td>${policy.customerName}</td>
                    <td><fmt:formatNumber value="${policy.premium}" type="currency" currencySymbol="$"/></td>
                    <td><fmt:formatDate value="${policy.issueDate}" pattern="MM/dd/yyyy"/></td>
                </tr>
            </c:forEach>
        </table>
    </c:if>
    <c:if test="${empty requestScope.policies and not empty param.searchQuery}">
        <p>No policies found.</p>
    </c:if>
</body>
</html>