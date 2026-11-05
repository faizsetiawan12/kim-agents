"""Load allowlisted profile credentials privately for the deterministic supervisor."""
import os
from pathlib import Path
import subprocess
import sys


def main():
    home = Path(os.environ['KIM_SENTRY_HOME'])
    helper = home / 'resolve-secrets.py'
    result = subprocess.run(['/usr/bin/python', str(helper)], capture_output=True, text=True, timeout=5, check=True)
    allowed = {'TELEGRAM_BOT_TOKEN', 'TELEGRAM_ALLOWED_USERS', 'TELEGRAM_HOME_CHANNEL',
               'KIM_SENTRY_GO_KEY', 'KIM_SENTRY_ROUTER_KEY'}
    env = {k: v for k, v in os.environ.items() if k in {
        'PATH', 'HOME', 'USER', 'LANG', 'LC_ALL', 'TZ', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS'}}
    for line in result.stdout.splitlines():
        key, value = line.split('=', 1)
        if key not in allowed:
            raise ValueError('Unexpected credential name')
        env[key] = value
    env['KIM_SENTRY_HOME'] = str(home)
    env['KIM_SENTRY_TELEGRAM_TOKEN'] = env['TELEGRAM_BOT_TOKEN']
    env['KIM_SENTRY_TELEGRAM_CHAT_ID'] = env['TELEGRAM_HOME_CHANNEL']
    os.execve('/usr/bin/python', ['/usr/bin/python', str(Path(__file__).with_name('runtime.py')), *sys.argv[1:]], env)


if __name__ == '__main__':
    main()
