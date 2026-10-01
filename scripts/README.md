# API transport

Run from the repository root with Python 3.9+. No additional runtime dependencies.
SNIPE_IT_URL is the instance URL without /api/v1; SNIPE_IT_TOKEN is your account's API token.
The script reads these keys from root .env regardless of the working directory.
Environment variables take precedence, including empty values. Quoted values are supported;
the file does not execute shell code or expand variables. Use .env.example and chmod 600 .env.
Never pass a token on the command line.

```bash
python3 scripts/snipe_api.py GET hardware --param 'limit=1'
python3 scripts/snipe_api.py GET hardware --param 'search=ASSET-000001' --param 'limit=100' --param 'offset=0'
python3 scripts/snipe_api.py PATCH hardware/123 --data '{"name":"Example asset"}'
```

Tags, IDs and payloads above are fictitious. The last command only prints a plan.
Add --apply to execute a write authorized by the user's request.
Use --data @/path/payload.json to load JSON from a file; --param KEY=VALUE is repeatable.
Methods: GET, POST, PUT, PATCH, DELETE. Default timeout: 30 seconds; override with --timeout.
Endpoints are relative to /api/v1, without a full URL or query string.

Successful JSON goes to stdout. Errors go to stderr with a nonzero exit code.
The script detects status: error even with HTTP 200, refuses redirects, and requires HTTPS
except for localhost. It does not retry requests. After an uncertain write outcome,
check the actual state before another attempt.

Skills own operation selection, pagination, duplicate checks and result verification.
Read [AGENTS.md](../AGENTS.md) and local CUSTOM.md before using a workflow.
