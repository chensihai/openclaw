---
name: gog-live
description: "Use Gmail, Calendar, Drive, Contacts, Sheets, and Docs through the local gog-live Docker HTTP service, including read-only checks and confirmed email/calendar/sheet changes."
homepage: https://gogcli.sh
metadata: { "openclaw": { "emoji": "🎮" } }
---

# gog-live

Use the local `gog-live` service whenever the user asks to use Gmail, email,
Calendar, Drive, Contacts, Sheets, or Docs from OpenClaw running in Docker. The
user does not need to mention `gog-live`; natural requests such as "send an
email", "check Gmail", "read this sheet", or "move this meeting" should use this
service.

Endpoint from the OpenClaw gateway container:

- `http://gog-live:8082/gog`

Call it with HTTP POST JSON:

```json
{ "args": ["auth", "list"] }
```

The response is JSON:

```json
{
  "ok": true,
  "code": 0,
  "stdout": "...",
  "stderr": ""
}
```

Common checks

- Auth list: `["auth", "list"]`
- Gmail recent messages: `["gmail", "messages", "search", "newer_than:7d", "--max", "3", "--json", "--no-input"]`
- Gmail thread search: `["gmail", "search", "newer_than:7d", "--max", "10", "--json", "--no-input"]`
- Gmail draft email: `["gmail", "drafts", "create", "--to", "<recipient>", "--subject", "<subject>", "--body-file", "-"]`
- Gmail send email after confirmation: `["gmail", "send", "--to", "<recipient>", "--subject", "<subject>", "--body-file", "-"]`
- Calendar list: `["calendar", "events", "primary", "--from", "<iso>", "--to", "<iso>", "--json", "--no-input"]`
- Sheets get: `["sheets", "get", "<sheetId>", "Tab!A1:D10", "--json", "--no-input"]`
- Drive search: `["drive", "search", "name contains 'foo'", "--max", "10", "--json", "--no-input"]`

Rules

- Prefer read-only test commands first: `auth list`, Gmail search, Calendar list,
  Drive search, Sheets get.
- Confirm before sending email, creating calendar events, updating sheets, or
  changing Drive/Docs content. For email, draft the exact recipient, subject,
  and body in chat first, then send only after the user approves.
- If the user asks to email a person by name, resolve the email address from
  context or ask for the address before sending.
- If the response has `"ok": false`, report `stderr` and the command args.
- Do not print secrets or OAuth token files.

Auth recovery

- If `["auth", "list"]` shows no account, or Gmail/Calendar/Sheets returns an
  OAuth error such as `invalid_grant`, tell the user to run this from the
  repository root on the host:

  ```powershell
  docker compose run --rm -it gog-svc auth add <email> --services gmail,calendar,drive,contacts,docs,sheets --manual --force-consent
  ```

- Explain the manual flow briefly: open the Google auth URL in the host browser,
  approve access, copy the final redirect URL, and paste it back into the
  terminal.
- After the user completes auth, verify with:

  ```powershell
  docker compose run --rm gog-svc auth list
  docker compose run --rm gog-svc gmail messages search "newer_than:7d" --max 1 --json --no-input
  ```
