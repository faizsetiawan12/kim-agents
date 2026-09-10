# Runbook: OpenClaw Chief Telegram Access

## Goal

Keep Chief useful in the KIM Telegram group without allowing arbitrary groups or
unknown senders to trigger the agent.

## Desired State

- `channels.telegram.groupPolicy` is `allowlist`.
- No wildcard Telegram group is configured.
- Only the KIM Telegram group is configured for Chief.
- Trusted sender allowlist is stored in OpenClaw config, not workspace docs.
- Normal group interactions require a mention.

## Checks

```bash
openclaw config validate
openclaw doctor
openclaw security audit --deep
```

Confirm doctor no longer reports open Telegram group policy.
