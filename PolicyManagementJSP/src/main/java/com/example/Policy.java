package com.example;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

public class Policy implements Serializable {
    private int id;
    private String policyNumber;
    private String customerName;
    private BigDecimal premium;
    private Date issueDate;

    // Default constructor
    public Policy() {}

    // Parameterized constructor
    public Policy(int id, String policyNumber, String customerName, BigDecimal premium, Date issueDate) {
        this.id = id;
        this.policyNumber = policyNumber;
        this.customerName = customerName;
        this.premium = premium;
        this.issueDate = issueDate;
    }

    // Getters and setters
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public String getPolicyNumber() { return policyNumber; }
    public void setPolicyNumber(String policyNumber) { this.policyNumber = policyNumber; }
    public String getCustomerName() { return customerName; }
    public void setCustomerName(String customerName) { this.customerName = customerName; }
    public BigDecimal getPremium() { return premium; }
    public void setPremium(BigDecimal premium) { this.premium = premium; }
    public Date getIssueDate() { return issueDate; }
    public void setIssueDate(Date issueDate) { this.issueDate = issueDate; }
}