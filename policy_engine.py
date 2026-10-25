from dataclasses import dataclass

@dataclass
class Decision:
    status: str
    reason: str
    requires_approval: bool = False

def evaluate_action(action: dict, rules: dict, daily_cap: float = 10000) -> Decision:
    """Deterministic demo policy checks. This is a local simulation, not a payment processor."""
    action_type = str(action.get("type", "")).lower()
    amount = float(action.get("amount", 0) or 0)
    vendor_new = bool(action.get("new_vendor", False))

    if action_type == "payment":
        if amount < 0:
            return Decision("block", "Payment amount cannot be negative.")
        if amount > daily_cap:
            return Decision("block", f"Payment exceeds this demo agent's daily cap of ₹{daily_cap:,.0f}.")
        threshold = float(rules.get("new_vendor_approval_threshold", 5000))
        if vendor_new and amount > threshold:
            return Decision("ask", f"New-vendor payment exceeds ₹{threshold:,.0f}; owner approval is required.", True)

    if action_type in {"delete_customer", "export_customer_data"}:
        return Decision("ask", "Sensitive customer-data action requires owner approval.", True)

    return Decision("allow", "No configured demo rule blocked this action.")
