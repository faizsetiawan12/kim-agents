"""Host-local Ops supervisor. Product pipelines remain owned by their repos."""
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import subprocess
import datetime
import re
import signal
import urllib.request

from operations import Store, SERVICES, card, send_telegram


def run(args, **kwargs):
    return subprocess.run(args, check=False, **kwargs)


def probe(unit):
    try:
        if run(['systemctl', '--user', 'is-active', '--quiet', unit], timeout=15).returncode != 0:
            return False
        if unit == '9router.service':
            key = os.environ['KIM_OPS_ROUTER_KEY']
            req = urllib.request.Request('http://127.0.0.1:20128/v1/models', headers={'Authorization': 'Bearer '+key})
            with urllib.request.urlopen(req, timeout=10) as response:
                return bool(json.load(response).get('data'))
        if unit == 'hermes-gateway.service':
            state = json.loads((Path.home()/'.hermes/gateway_state.json').read_text())
            os.kill(int(state['pid']), 0)
            return state.get('platforms', {}).get('kim-ops:telegram', {}).get('state') == 'connected'
        if unit == 'openclaw-gateway.service':
            result = run(['openclaw', 'health', '--json', '--timeout', '5000'], capture_output=True, text=True, timeout=15)
            text = result.stdout
            data = json.loads(text[text.index('{'):])
            return result.returncode == 0 and data.get('ok') is True
        # Kotrade's application/trading path is not exercised by a watchdog.
        return True
    except (OSError, subprocess.TimeoutExpired, KeyError, ValueError):
        return False


READINESS_UNITS = {'9router.service', 'hermes-gateway.service', 'openclaw-gateway.service'}


def investigate(args, timeout):
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)


def notify(store, title, detail):
    with store.db:
        store.db.execute('INSERT INTO outbox(body) VALUES (?)', (card(title, detail),))


def status(store):
    rows = store.status()
    if not rows:
        return 'Ops has not completed its first health check yet.'
    return '\n'.join(f"{'🟢' if row['healthy'] else '🔴'} {row['target']}: {'check passed' if row['healthy'] else 'check failed'}; checked {row['checked_at']}; AI attempts {row['repair_attempts']}/2." + (f" Incident: {row['incident_id']}." if row['incident_id'] else '') + (f" Blocked: {json.loads(row['evidence']).get('summary', 'Approval required.')}" if row['blocked'] else '')
                     for row in rows)


def initialize(store):
    store.db.execute('CREATE TABLE IF NOT EXISTS settings (name TEXT PRIMARY KEY, value TEXT NOT NULL)')
    store.db.commit()


def paused(store):
    row = store.db.execute("SELECT value FROM settings WHERE name='paused'").fetchone()
    return row is not None and row[0] == 'yes'


def control(store, action):
    initialize(store)
    if action == 'status':
        return status(store) + ('\nAutomatic repairs are paused.' if paused(store) else '\nAutomatic repairs are enabled.')
    with store.db:
        store.db.execute("INSERT INTO settings VALUES ('paused',?) ON CONFLICT(name) DO UPDATE SET value=excluded.value", ('yes' if action == 'pause' else 'no',))
    return 'Automatic repairs paused; monitoring continues.' if action == 'pause' else 'Automatic repairs enabled.'


def approve_repair(store, incident, scope, new_budget=False):
    if not incident or len(scope.strip()) < 8:
        return 'Provide the incident ID and the exact action you approve.'
    with store.db:
        store.db.execute('BEGIN IMMEDIATE')
        row = store.db.execute('SELECT target,attempts,evidence FROM incidents WHERE incident_id=?', (incident,)).fetchone()
        if row is None:
            return 'That incident is not open.'
        if row[1] >= 2 and not new_budget:
            return 'Two attempts were used. Include new-budget only if you authorize two more attempts.'
        evidence = json.loads(row[2]) if row[2] else {}
        evidence['approval'] = {'scope':scope, 'new_budget':new_budget, 'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        evidence.setdefault('approval_history', []).append(evidence['approval'])
        store.db.execute('UPDATE incidents SET blocked=0,attempts=?,evidence=? WHERE incident_id=?',
                         (0 if new_budget else row[1], json.dumps(evidence), incident))
    return 'Approval recorded for this incident only. Investigation can resume.'


def tick(store):
    # cron's flock serializes scheduled runs. This file lock also protects manual invocations.
    with store.exclusive('check'):
        for label, unit in SERVICES.items():
            healthy = probe(unit)
            store.observe(label, healthy, 'The configured service check failed. Investigation is required.')
            if healthy and unit in READINESS_UNITS:
                try:
                    with store.exclusive('repair', blocking=False):
                        store.confirm_recovery(label)
                except BlockingIOError:
                    pass
        if not paused(store) and any(not row['healthy'] and row['repair_attempts'] < 2 and not row['blocked'] for row in store.status()):
            try:
                with store.exclusive('repair', blocking=False):
                    subprocess.Popen(['/usr/bin/python', str(Path(__file__).with_name('launch.py')), 'repair'],
                        env=dict(os.environ), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, start_new_session=True)
            except BlockingIOError:
                pass
        store.deliver(send_telegram)


def repair(store, home):
    # Lock survives independently of Hermes and releases automatically on worker death.
    with store.exclusive('repair'):
        if paused(store):
            return
        for row in store.status():
            target = row['target']
            if row['healthy'] or probe(SERVICES[target]):
                continue
            attempt = store.claim_repair(target)
            if attempt is None:
                continue
            if row['blocked']:
                continue
            prompt = f'''Investigate and repair this KIM infrastructure incident now.
Target: {target}. Unit: {SERVICES[target]}. Persisted AI attempt: {attempt}/2.
Incident ID: {row['incident_id']}. Prior evidence: {row['evidence'] or 'None'}.
Service failed its configured check. Recheck before acting.
Use the ops-repair skill and all six selected engineering skills in its instructions.
Expected behavior: the named service starts, passes its own readiness check, and remains running.
A process being active alone is not proof that requests or Telegram routing work.
For code changes: create an incident issue in the affected repository, a NEW git worktree,
a failing public-interface test, fix, two independent reviews, PR and green checks.
Automerge/deploy only reversible operational changes with a tested rollback and real recovery check.
Approval exceptions: trading decisions/orders, credentials, permanent data deletion, spending.
KATMA integration is deferred. Do not edit KATMA or kim-data or enable their jobs.
Do not change other profiles' models, memory, permissions, or bot routes.
Never print credentials or dump config/auth files. Send no messages yourself: return a concise
result; the deterministic supervisor handles notifications. Return BLOCKED if approval is needed.
If unable to reproduce, do not invent a fix. Exit with the exact blocker.
Return ONLY one JSON object: {{"status":"fixed|unresolved|blocked", "summary":"reason or precise action required", "issue_url":"", "pr_url":"", "evidence":[]}}.
A blocked approval must identify exactly what Faiz must approve. Reuse the prior incident issue.

'''
            path = home / 'runtime' / 'repair-prompt.txt'
            path.write_text(prompt)
            path.chmod(0o600)
            try:
                result = investigate(['hermes', '-p', 'kim-ops', 'chat', '--query-file', str(path),
                              '--oneshot', '-Q', '--max-turns', '100', '--run-budget', '3300',
                              '-s', 'ops-repair'], timeout=3450)
                summary = (result.stdout or '')[-16000:]
                for key, value in os.environ.items():
                    if value and any(word in key for word in ('KEY', 'TOKEN', 'SECRET', 'PASSWORD')):
                        summary = summary.replace(value, '<REDACTED>')
                summary = re.sub(r'\b\d{6,}:[A-Za-z0-9_-]{20,}', '<REDACTED>', summary)
                log = home / 'runtime' / f'repair-{datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")}.txt'
                log.write_text(summary)
                log.chmod(0o600)
                try:
                    outcome, _ = json.JSONDecoder().raw_decode(summary[summary.index('{'):])
                    if outcome.get('status') not in ('fixed', 'unresolved', 'blocked') or not isinstance(outcome.get('summary'), str):
                        raise ValueError('Invalid worker outcome')
                except (ValueError, TypeError, AttributeError):
                    outcome = {'status':'unresolved', 'summary':'The worker did not return a valid repair result.'}
                store.outcome(target, outcome)
                if outcome['status'] == 'blocked':
                    notify(store, '🔴 Ops — Your approval is needed', outcome['summary'][:1000])
                    store.deliver(send_telegram)
                    break
            except (OSError, subprocess.TimeoutExpired):
                notify(store, '🔴 Ops — Investigation interrupted', 'The repair worker failed or exceeded its time limit. The attempt remains counted.')
            # Never announce repair success solely from the model's final answer.
            healthy = probe(SERVICES[target])
            store.observe(target, healthy, 'The configured check still fails after investigation.')
            if healthy and SERVICES[target] in READINESS_UNITS:
                store.confirm_recovery(target)
            if not healthy:
                title = '🔴 Ops — Your help is needed' if attempt >= 2 else '🔴 Ops — Repair did not restore service'
                detail = ('Two AI attempts were used. Further automatic repairs have stopped.' if attempt >= 2
                          else 'The service is still unavailable. One AI attempt remains.')
                notify(store, title, detail)
            else:
                notify(store, '🟡 Ops — Service is running', 'The configured check passed after investigation. Full repair evidence is available from Ops.')
            store.deliver(send_telegram)
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('check', 'repair', 'status', 'pause', 'resume', 'delivery-test', 'approve-repair'))
    parser.add_argument('--home', type=Path, default=Path(os.environ.get('KIM_OPS_HOME', str(Path.home()/'.hermes/profiles/kim-ops'))))
    parser.add_argument('--incident', default='')
    parser.add_argument('--approval', default='')
    parser.add_argument('--new-budget', action='store_true')
    args = parser.parse_args()
    home = args.home
    store = Store(home / 'runtime' / 'operations.sqlite')
    initialize(store)
    try:
        if args.action == 'approve-repair': print(approve_repair(store, args.incident, args.approval, args.new_budget))
        elif args.action == 'check': tick(store)
        elif args.action == 'repair': repair(store, home)
        elif args.action == 'delivery-test':
            notify(store, '🟢 Ops — Delivery test', 'This message was generated and delivered by code without an AI model.')
            store.deliver(send_telegram)
        else: print(control(store, args.action))
    finally:
        store.close()


if __name__ == '__main__':
    main()
