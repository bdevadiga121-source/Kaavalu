# Kaavalu — AI Agent Safety and Control Gateway

**Team:** Innovexa  
**Institution:** Mangalore Institute of Technology and Engineering  
**Problem statement:** PS 2.1 — AI Agent Safety and Control

Kaavalu is a small, local demonstration of a safety gateway that evaluates simulated AI-agent actions against deterministic rules. It illustrates the idea described in the project proposal.

## Current MVP features

- FastAPI web dashboard.
- Simulated agent actions: payment, read, and sensitive customer-data actions.
- Deterministic allow / ask / block policy checks.
- Example rule: a new-vendor payment above ₹5,000 requires approval.
- Demo payment cap of ₹10,000.
- SQLite audit log with SHA-256 hash chaining and a chain-integrity check.
- Emergency STOP and resume controls for the demo agent.
- Basic automated policy tests.

## Important limitations

This is a **prototype / simulation**, not a production security gateway. It does not make real payments, connect to real business systems, send WhatsApp messages, compile Kannada/Hindi/English rules with an LLM, or provide a production-grade trust ladder or red-team scorecard. The STOP control affects this local demo process only. Do not connect it to real business systems without a security review.

## Requirements

- Python 3.10 or newer
- Internet connection for installing Python packages

## Run on Windows PowerShell

Open PowerShell in the `Kaavalu` project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

If PowerShell blocks activation, you can install and run without activating:

```powershell
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

## Run tests

```powershell
py -m pytest
```

## API endpoints

- `GET /` — dashboard
- `GET /health` — health check
- `GET /audit` — audit log and chain verification
- `GET /docs` — interactive API docs

## Example demo scenario

1. Open the dashboard.
2. Submit a payment for ₹48,000 to a new vendor.
3. The demo should block it because it exceeds the ₹10,000 daily cap.
4. Submit a smaller new-vendor payment above ₹5,000 but not above ₹10,000; it should be marked as requiring approval.
5. Inspect the audit log and hash-chain integrity.

## GitHub upload checklist

Upload the source files and this README. Do not upload `.venv`, `kaavalu.db`, `.env`, API keys, passwords, or personal data.
