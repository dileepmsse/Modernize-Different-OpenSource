// package com.example;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class PolicyDAO {
    private static final String DB_URL = "jdbc:postgresql://ep-cool-forest-123456.us-east-2.aws.neon.tech/policies";
    private static final String DB_USER = "neon_user";
    private static final String DB_PASSWORD = "your_password";

    public List<Policy> searchPolicies(String policyNumber) {
        List<Policy> policies = new ArrayList<>();
        String sql = "SELECT id, policy_number, policy_holder, coverage_amount FROM policies WHERE policy_number LIKE ?";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, "%" + policyNumber + "%");
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                Policy policy = new Policy();
                policy.setId(rs.getInt("id"));
                policy.setPolicyNumber(rs.getString("policy_number"));
                policy.setPolicyHolder(rs.getString("policy_holder"));
                policy.setCoverageAmount(rs.getDouble("coverage_amount"));
                policies.add(policy);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return policies;
    }
}