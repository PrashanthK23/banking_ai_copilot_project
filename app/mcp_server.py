from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("BankingMCP")

CUSTOMERS = {
    "CUST1001": {
        "name": "Aarav Sharma",
        "salary": 95000,
        "credit_score": 758,
        "existing_loan_emi": 18000,
        "months_paid": 16,
        "late_payments_last_12m": 0,
        "avg_balance": 240000,
    },
    "CUST1002": {
        "name": "Meera Iyer",
        "salary": 52000,
        "credit_score": 701,
        "existing_loan_emi": 14000,
        "months_paid": 10,
        "late_payments_last_12m": 2,
        "avg_balance": 40000,
    },
    "CUST1003": {
        "name": "Rohit Verma",
        "salary": 130000,
        "credit_score": 790,
        "existing_loan_emi": 0,
        "months_paid": 0,
        "late_payments_last_12m": 0,
        "avg_balance": 600000,
    },
}


@mcp.tool()
def get_customer_profile(customer_id: str) -> dict:
    """Return simple retail customer profile data for demo banking decisions."""
    customer = CUSTOMERS.get(customer_id.upper())
    if not customer:
        return {"error": "Customer not found"}
    return {"customer_id": customer_id.upper(), **customer}


@mcp.tool()
def calculate_emi(principal: float, annual_rate: float, months: int) -> dict:
    """Calculate EMI for a loan using principal, annual interest rate, and tenure in months."""
    monthly_rate = annual_rate / (12 * 100)
    if months <= 0:
        return {"error": "Months must be greater than zero"}

    if monthly_rate == 0:
        emi = principal / months
    else:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)

    total_payment = emi * months
    total_interest = total_payment - principal
    return {
        "principal": round(principal, 2),
        "annual_rate": annual_rate,
        "months": months,
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
    }


@mcp.tool()
def suggest_next_best_action(customer_id: str) -> dict:
    """Return a simple next best banking action based on mocked customer profile."""
    customer = CUSTOMERS.get(customer_id.upper())
    if not customer:
        return {"error": "Customer not found"}

    actions = []
    if customer["salary"] >= 75000:
        actions.append("Review for premium credit card")
    if customer["avg_balance"] >= 200000:
        actions.append("Offer wealth relationship callback")
    if customer["months_paid"] >= 12 and customer["credit_score"] >= 720 and customer["late_payments_last_12m"] <= 1:
        actions.append("Eligible for personal loan top-up review")

    if not actions:
        actions.append("Focus on service engagement and savings growth")

    return {"customer_id": customer_id.upper(), "recommended_actions": actions}


if __name__ == "__main__":
    mcp.run(transport="stdio")
