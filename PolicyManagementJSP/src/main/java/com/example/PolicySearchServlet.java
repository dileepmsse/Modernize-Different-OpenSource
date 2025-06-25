package com.example;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;

@WebServlet("/search")
public class PolicySearchServlet extends HttpServlet {
    private PolicyDAO policyDAO;

    @Override
    public void init() throws ServletException {
        policyDAO = new PolicyDAO();
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String query = request.getParameter("searchQuery");
        List<Policy> policies = null;

        if (query != null && !query.trim().isEmpty()) {
            policies = policyDAO.searchPolicies(query.trim());
        }

        request.setAttribute("policies", policies);
        request.getRequestDispatcher("/policySearch.jsp").forward(request, response);
    }
}