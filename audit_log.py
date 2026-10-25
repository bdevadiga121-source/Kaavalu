import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "kaavalu.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_json TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            )
        """)
        conn.commit()

def add_entry(action: dict, decision: str, reason: str):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
        previous_hash = row[0] if row else "GENESIS"
        timestamp = datetime.now(timezone.utc).isoformat()
        action_json = json.dumps(action, sort_keys=True)
        raw = "|".join([timestamp, action_json, decision, reason, previous_hash])
        entry_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        conn.execute(
            "INSERT INTO audit_log(timestamp, action_json, decision, reason, previous_hash, entry_hash) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, action_json, decision, reason, previous_hash, entry_hash)
        )
        conn.commit()

def get_entries(limit: int = 100):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

def verify_chain():
    entries = list(reversed(get_entries(10000)))
    previous = "GENESIS"
    for entry in entries:
        raw = "|".join([
            entry["timestamp"], entry["action_json"], entry["decision"],
            entry["reason"], previous
        ])
        expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if entry["previous_hash"] != previous or entry["entry_hash"] != expected:
            return False
        previous = entry["entry_hash"]
    return True
