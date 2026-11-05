"""Private commands run fixed code and return its output without a model."""
import asyncio
import json
from pathlib import Path
import subprocess

SCRIPT = '/home/faiz/KIM/agents/sentry/runtime.py'


def home():
    from hermes_constants import get_hermes_home
    path = get_hermes_home()
    if path != Path('/home/faiz/.hermes/profiles/sentry'):
        raise PermissionError('Sentry commands are available only in the Sentry profile.')
    return path


def execute(action):
    result = subprocess.run(['/usr/bin/python', SCRIPT, action, '--home', str(home())],
                            capture_output=True, text=True, timeout=20, check=False)
    return result.stdout.strip() if result.returncode == 0 else 'Sentry could not read its operational state.'


def authorized(source):
    from agent.secret_scope import get_secret
    allowed = set((get_secret('TELEGRAM_ALLOWED_USERS') or '').split(','))
    user = str(getattr(source, 'user_id', ''))
    return user in allowed and str(getattr(source, 'chat_id', '')) == user


async def health(raw_args='', source=None, **kwargs):
    if not authorized(source): return 'This command is private to Faiz.'
    return await asyncio.to_thread(execute, 'status')


async def pause(raw_args='', source=None, **kwargs):
    if not authorized(source): return 'This command is private to Faiz.'
    return await asyncio.to_thread(execute, 'pause')


async def resume(raw_args='', source=None, **kwargs):
    if not authorized(source): return 'This command is private to Faiz.'
    return await asyncio.to_thread(execute, 'resume')


async def approve(raw_args='', source=None, **kwargs):
    if not authorized(source): return 'This command is private to Faiz.'
    parts = raw_args.strip().split(maxsplit=1)
    if len(parts) != 2:
        return 'Use /approve_repair <incident ID> <exact action approved>. Add new-budget before the action to authorize two more attempts.'
    scope = parts[1]
    extra = []
    if scope.startswith('new-budget '):
        extra = ['--new-budget']; scope = scope[len('new-budget '):]
    def perform():
        result = subprocess.run(['/usr/bin/python', SCRIPT, 'approve-repair', '--home', str(home()),
            '--incident', parts[0], '--approval', scope, *extra], capture_output=True, text=True, timeout=20)
        return result.stdout.strip() if result.returncode == 0 else 'Approval could not be recorded.'
    return await asyncio.to_thread(perform)


def status_tool(args, **kwargs):
    return json.dumps({'status': execute('status')})


def register(ctx):
    from .provider import install
    install()
    ctx.register_command('approve_repair', approve, description='Approve one incident action; preserve budget unless new-budget is explicit')
    ctx.register_command('health', health, description='Checked KIM service status; no AI')
    ctx.register_command('pause_repairs', pause, description='Pause automatic repairs; keep monitoring')
    ctx.register_command('resume_repairs', resume, description='Resume automatic repairs')
    ctx.register_tool(name='sentry_status', toolset='sentry', handler=status_tool,
                      schema={'name':'sentry_status','description':'Read checked KIM status and repair budgets; use for all factual status queries.', 'parameters':{'type':'object','properties':{}}},
                      description='Read deterministic KIM service status', emoji='🛡️')
