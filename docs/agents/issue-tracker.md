# Repair tracking

Use GitHub Issues through `gh` in the affected repository; infer the repository from its Git remote. A repair worker receives a stable incident ID and prior issue/PR links from the supervisor. Search issues for that ID before creating one. Put the ID in the issue body and reference it from the repair PR, so retries reuse the original issue.

The incident's expected behavior and current user decisions are the requirements for the Spec review. Pin the pre-repair commit for both review agents. A clear incident repair brief is sufficient; setup, triage and ticket-generation interviews are not part of unattended incident handling.
