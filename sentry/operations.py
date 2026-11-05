"""Durable incident accounting and deterministic Telegram cards; no model calls."""
import argparse
import fcntl
from contextlib import contextmanager
import datetime
import json
import os
from pathlib import Path
import sqlite3
import uuid
import subprocess
import urllib.request


def card(title, reason):
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime('%H:%M WIB')
    return f'{title}\n\n• {reason}\n\n{stamp} · Ask Sentry for incident details.'


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.db = sqlite3.connect(path, timeout=30)
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS incidents (
                target TEXT PRIMARY KEY, healthy INTEGER NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, detail TEXT NOT NULL,
                checked_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS incident_history (incident_id TEXT PRIMARY KEY, target TEXT NOT NULL, evidence TEXT NOT NULL, closed_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS outbox (
                id INTEGER PRIMARY KEY, body TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0);
        ''')
        columns = {row[1] for row in self.db.execute('PRAGMA table_info(incidents)')}
        for name, definition in [('incident_id', "TEXT NOT NULL DEFAULT ''"), ('blocked', 'INTEGER NOT NULL DEFAULT 0'), ('evidence', "TEXT NOT NULL DEFAULT ''")]:
            if name not in columns:
                self.db.execute(f'ALTER TABLE incidents ADD COLUMN {name} {definition}')
        self.db.commit()

    def close(self):
        self.db.close()

    def observe(self, target, healthy, detail):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            previous = self.db.execute('SELECT healthy FROM incidents WHERE target=?', (target,)).fetchone()
            changed = previous is None or bool(previous[0]) != healthy
            if changed and (not healthy or previous is not None):
                title = f'🟢 Sentry — {target} check passed again' if healthy else f'🔴 Sentry — {target} unavailable'
                body = 'The configured check passed. This alone does not establish application recovery.' if healthy else detail
                self.db.execute('INSERT INTO outbox(body) VALUES (?)', (card(title, body),))
            self.db.execute('''INSERT INTO incidents(target,healthy,attempts,detail,checked_at) VALUES (?, ?, 0, ?, ?)
                ON CONFLICT(target) DO UPDATE SET healthy=excluded.healthy,
                attempts=incidents.attempts,
                detail=excluded.detail, checked_at=excluded.checked_at''',
                (target, int(healthy), '' if healthy else detail, datetime.datetime.now(datetime.timezone.utc).isoformat()))
            if not healthy:
                self.db.execute("UPDATE incidents SET incident_id=? WHERE target=? AND incident_id=''", (uuid.uuid4().hex, target))

    def claim_repair(self, target):
        # Commit the budget before launching work, including when the worker crashes.
        with self.db:
            row = self.db.execute('''UPDATE incidents SET attempts=attempts+1
                WHERE target=? AND healthy=0 AND attempts<2 AND blocked=0 RETURNING attempts''', (target,)).fetchone()
            return row[0] if row else None

    def confirm_recovery(self, target):
        # Only an application readiness verifier or explicit operator may close it.
        with self.db:
            row = self.db.execute('SELECT incident_id,evidence FROM incidents WHERE target=? AND healthy=1', (target,)).fetchone()
            if row and row[0]:
                self.db.execute('INSERT OR IGNORE INTO incident_history VALUES (?,?,?,?)',
                    (row[0], target, row[1], datetime.datetime.now(datetime.timezone.utc).isoformat()))
            self.db.execute("UPDATE incidents SET attempts=0,blocked=0,incident_id='',evidence='' WHERE target=? AND healthy=1", (target,))

    def outcome(self, target, data):
        previous = self.db.execute('SELECT evidence FROM incidents WHERE target=?', (target,)).fetchone()
        previous = json.loads(previous[0]) if previous and previous[0] else {}
        for key in ('issue_url', 'pr_url', 'approval', 'approval_history'):
            if not data.get(key) and previous.get(key):
                data[key] = previous[key]
        with self.db:
            self.db.execute('UPDATE incidents SET blocked=?,evidence=? WHERE target=?',
                            (int(data.get('status') == 'blocked'), json.dumps(data), target))

    @contextmanager
    def exclusive(self, purpose, blocking=True):
        # Kernel-owned locks release on worker death; hold a repair lock through
        # claim, execution and verification, never only through claiming budget.
        lock_path = self.path.with_name(self.path.name + '.' + purpose + '.lock')
        with lock_path.open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def pending(self):
        return self.db.execute('SELECT id,body FROM outbox WHERE sent=0 ORDER BY id').fetchall()

    def deliver(self, sender):
        # At-least-once: a crash after Telegram accepts can repeat one message.
        with self.exclusive("delivery"):
            for ident, body in self.pending():
                sender(body)
                with self.db:
                    self.db.execute('UPDATE outbox SET sent=1 WHERE id=?', (ident,))

    def status(self):
        return [dict(zip(('target', 'healthy', 'repair_attempts', 'detail', 'checked_at', 'incident_id', 'blocked', 'evidence'), row))
                for row in self.db.execute('SELECT target,healthy,attempts,detail,checked_at,incident_id,blocked,evidence FROM incidents ORDER BY target')]


def send_telegram(body):
    token = os.environ['KIM_SENTRY_TELEGRAM_TOKEN']
    chat = os.environ['KIM_SENTRY_TELEGRAM_CHAT_ID']
    payload = json.dumps({'chat_id': chat, 'text': body}).encode()
    req = urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=payload,
                                 headers={'Content-Type': 'application/json'})
    # Do not expose HTTP exceptions containing the bot token in their URL.
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
        if not result.get('ok'):
            raise RuntimeError('Telegram rejected the message.')
    except Exception:
        raise RuntimeError('Telegram delivery failed; message retained for retry.') from None


SERVICES = {'Hermes gateway': 'hermes-gateway.service',
            'AI gateway': '9router.service', 'OpenClaw gateway': 'openclaw-gateway.service',
            'Kotrade messaging': 'kotrade-bot.service'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('check', 'status', 'deliver'))
    parser.add_argument('--state', type=Path, required=True)
    args = parser.parse_args()
    store = Store(args.state)
    try:
        if args.command == 'check':
            for label, unit in SERVICES.items():
                try:
                    result = subprocess.run(['systemctl', '--user', 'is-active', '--quiet', unit], timeout=15, check=False)
                    healthy = result.returncode == 0
                except (subprocess.TimeoutExpired, OSError):
                    healthy = False
                store.observe(label, healthy, 'The service check failed. Investigation is required.')
        elif args.command == 'deliver':
            store.deliver(send_telegram)
        print(json.dumps(store.status(), indent=2))
    finally:
        store.close()


if __name__ == '__main__':
    main()
