from app.policy_engine import evaluate_action

RULES = {"new_vendor_approval_threshold": 5000}

def test_new_vendor_large_payment_requires_approval():
    result = evaluate_action({"type":"payment","amount":6000,"new_vendor":True}, RULES, 10000)
    assert result.status == "ask"
    assert result.requires_approval is True

def test_payment_over_daily_cap_is_blocked():
    result = evaluate_action({"type":"payment","amount":48000,"new_vendor":True}, RULES, 10000)
    assert result.status == "block"

def test_read_action_is_allowed():
    result = evaluate_action({"type":"read"}, RULES, 10000)
    assert result.status == "allow"
