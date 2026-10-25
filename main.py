from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from app.policy_engine import evaluate_action
from app.audit_log import add_entry, get_entries, verify_chain, init_db

app = FastAPI(title="Kaavalu — AI Agent Safety Gateway", version="0.1.0")
init_db()

RULES = {"new_vendor_approval_threshold": 5000}
DAILY_CAP = 10000
FROZEN = False

class ActionRequest(BaseModel):
    agent: str = Field(default="demo-billing-agent", max_length=100)
    type: str = Field(..., max_length=60)
    amount: float = 0
    vendor: str = Field(default="Example Vendor", max_length=120)
    new_vendor: bool = False
    details: str = Field(default="", max_length=500)

@app.get("/", response_class=HTMLResponse)
def dashboard():
    entries = get_entries(30)
    rows = ""
    for e in entries:
        rows += f"<tr><td>{e['timestamp']}</td><td>{e['action_json']}</td><td><b>{e['decision'].upper()}</b></td><td>{e['reason']}</td></tr>"
    frozen = "FROZEN" if FROZEN else "ACTIVE"
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><title>Kaavalu Dashboard</title>
    <style>
    body{{font-family:Arial,sans-serif;background:#0b1220;color:#eef2ff;margin:0;padding:28px}}
    .card{{background:#151f33;border:1px solid #2c3b56;border-radius:12px;padding:18px;margin:12px 0}}
    h1{{color:#83b8ff}} a,button{{color:white}} button{{background:#2359a8;border:0;padding:10px 14px;border-radius:7px;cursor:pointer}}
    input,select{{padding:9px;margin:4px;border-radius:6px;border:1px solid #52627a;background:#0b1220;color:white}}
    table{{width:100%;border-collapse:collapse;font-size:13px}} td,th{{padding:9px;border-bottom:1px solid #35435c;text-align:left;vertical-align:top;overflow-wrap:anywhere}}
    .muted{{color:#b6c4dc}} code{{color:#9fcdff}}
    </style></head><body>
    <h1>KAAVALU</h1><p class="muted">AI Agent Safety and Control Gateway — local demonstration MVP</p>
    <div class="card"><h2>Agent status: {frozen}</h2>
    <form method="post" action="/stop"><button>STOP / Freeze agents</button></form>
    <form method="post" action="/resume"><button>Resume demo agent</button></form></div>
    <div class="card"><h2>Simulate an agent action</h2>
    <form method="post" action="/simulate">
    <label>Action <select name="type"><option value="payment">Payment</option><option value="read">Read record</option><option value="delete_customer">Delete customer</option><option value="export_customer_data">Export customer data</option></select></label>
    <label>Amount ₹ <input name="amount" type="number" value="48000" min="0"></label>
    <label>New vendor? <select name="new_vendor"><option value="true">Yes</option><option value="false">No</option></select></label>
    <label>Vendor <input name="vendor" value="New Vendor Ltd"></label>
    <button type="submit">Submit simulated action</button></form>
    <p class="muted">Demo rule: new-vendor payments above ₹5,000 require approval; demo daily cap is ₹10,000. No real payments or external actions are performed.</p></div>
    <div class="card"><h2>Audit / Flight Log</h2><p>Hash-chain integrity: <b>{'VALID' if verify_chain() else 'CHECK FAILED'}</b> · <a href="/docs">API docs</a> · <a href="/audit">Audit JSON</a></p>
    <table><thead><tr><th>Time (UTC)</th><th>Action</th><th>Decision</th><th>Reason</th></tr></thead><tbody>{rows or '<tr><td colspan="4">No actions yet.</td></tr>'}</tbody></table></div>
    <p class="muted">Prototype only. Approval messaging, multilingual rule compilation, production integrations, and advanced red-team scoring are not implemented.</p>
    </body></html>
    """

@app.post("/simulate", response_class=HTMLResponse)
def simulate(type: str, amount: float = 0, new_vendor: str = "false", vendor: str = "Example Vendor"):
    global FROZEN
    action = {"agent": "demo-billing-agent", "type": type, "amount": amount,
              "new_vendor": new_vendor.lower() == "true", "vendor": vendor}
    if FROZEN:
        status, reason = "block", "Agents are frozen by the emergency STOP control."
    else:
        result = evaluate_action(action, RULES, DAILY_CAP)
        status, reason = result.status, result.reason
    add_entry(action, status, reason)
    return HTMLResponse(f"""<html><body style="font-family:Arial;background:#0b1220;color:white;padding:30px">
    <h1>Action result: {status.upper()}</h1><p>{reason}</p><p>Action recorded in the local audit log.</p>
    <a style="color:#8ec5ff" href="/">Return to dashboard</a></body></html>""")

@app.post("/stop", response_class=HTMLResponse)
def stop():
    global FROZEN
    FROZEN = True
    add_entry({"type": "emergency_stop"}, "allow", "Emergency STOP enabled; demo agent actions are frozen.")
    return HTMLResponse('<html><body style="font-family:Arial;padding:30px"><h1>Demo agent frozen</h1><a href="/">Return to dashboard</a></body></html>')

@app.post("/resume", response_class=HTMLResponse)
def resume():
    global FROZEN
    FROZEN = False
    add_entry({"type": "resume_demo"}, "allow", "Demo agent resumed.")
    return HTMLResponse('<html><body style="font-family:Arial;padding:30px"><h1>Demo agent resumed</h1><a href="/">Return to dashboard</a></body></html>')

@app.get("/audit")
def audit():
    return {"chain_valid": verify_chain(), "entries": get_entries(100)}

@app.get("/health")
def health():
    return {"status": "ok", "project": "Kaavalu demo", "frozen": FROZEN}
