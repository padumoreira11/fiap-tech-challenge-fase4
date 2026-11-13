"""Fila local persistente para demonstração, sem entrega externa."""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


@contextmanager
def connect(path):
    path=Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(path, timeout=10)
    try:
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, run_id TEXT NOT NULL, source TEXT NOT NULL, event_time TEXT NOT NULL, message TEXT NOT NULL, created_utc TEXT NOT NULL, acknowledged_utc TEXT)')
            yield db
    finally:
        db.close()


def enqueue(path, run_id, alerts):
    if not run_id: raise ValueError('A simulação precisa ter identificador.')
    inserted=0
    with connect(path) as db:
        for alert in alerts:
            payload=json.dumps([run_id,alert['source'],alert['time'],alert['message']],ensure_ascii=False,separators=(',',':'))
            key=hashlib.sha256(payload.encode('utf-8')).hexdigest()
            result=db.execute('INSERT OR IGNORE INTO alerts VALUES (?,?,?,?,?,?,NULL)',
                (key,run_id,alert['source'],str(alert['time']),alert['message'],datetime.now(timezone.utc).isoformat()))
            inserted+=result.rowcount
    return inserted


def list_alerts(path, run_id):
    with connect(path) as db:
        db.row_factory=sqlite3.Row
        return [dict(row) for row in db.execute('SELECT * FROM alerts WHERE run_id=? ORDER BY created_utc,id',(run_id,))]


def acknowledge(path, run_id, alert_id):
    with connect(path) as db:
        result=db.execute('UPDATE alerts SET acknowledged_utc=? WHERE id=? AND run_id=? AND acknowledged_utc IS NULL',
                          (datetime.now(timezone.utc).isoformat(),alert_id,run_id))
        return result.rowcount == 1
