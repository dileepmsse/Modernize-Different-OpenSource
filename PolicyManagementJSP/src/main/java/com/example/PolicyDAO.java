package com.example;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import com.supabase.SupabaseClient;

public class PolicyDAO {
    private SupabaseClient supabaseClient;

    public PolicyDAO() {
        // Initialize Supabase client
        String supabaseUrl = System.getenv("SUPABASE_URL");
        String supabaseKey = System.getenv("SUPABASE_KEY");
        supabaseClient = new SupabaseClient(supabaseUrl, supabaseKey);
    }

    public List<Policy> searchPolicies(String query) {
        List<Policy> policies = new ArrayList<>();
        String sql = "SELECT Id, PolicyNumber, CustomerName, Premium, IssueDate FROM Policies WHERE PolicyNumber ILIKE ? OR CustomerName ILIKE ?";

        try (Connection conn = supabaseClient.getJdbcConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, "%" + query + "%");
            stmt.setString(2, "%" + query + "%");
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                Policy policy = new Policy(
                    rs.getInt("Id"),
                    rs.getString("PolicyNumber"),
                    rs.getString("CustomerName"),
                    rs.getBigDecimal("Premium"),
                    rs.getDate("IssueDate")
                );
                policies.add(policy);
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error: " + e.getMessage());
        }
        return policies;
    }
}