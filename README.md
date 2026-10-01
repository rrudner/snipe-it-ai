# Snipe-IT AI

Operate an existing Snipe-IT instance with AI agents: one API transport, reusable skills,
and an optional local instruction file. Python 3.9+, with no runtime dependencies beyond
its standard library. This project does not install or host Snipe-IT.

## Start

1. Copy `.env.example` to `.env`, set your instance URL and personal API token,
   and run `chmod 600 .env`. See [API usage](scripts/README.md).
2. Optionally copy [CUSTOM.example.md](CUSTOM.example.md) to `CUSTOM.md` and describe
   your inventory conventions. Keep actual field names and values unchanged.
3. Open the repository in your AI agent. Agents that honor [AGENTS.md](AGENTS.md)
   are instructed to read CUSTOM.md at the start of each conversation.
   For other tools, explicitly start each conversation with:

   > Read AGENTS.md and CUSTOM.md if present, then use the relevant local skill for my request.

4. Ask to find an asset by tag. The available [asset-read skill](skills/snipe-asset-read/SKILL.md)
   calls the shared API script. More workflows are added when needed.

Instruction loading depends on your agent's integration; files alone cannot force an
arbitrary model to read them. CUSTOM.example.md is a template, never active configuration.

## Design

Request → skill → `scripts/snipe_api.py` → Snipe-IT API.

| Owner | Responsibility |
| --- | --- |
| API script | Authentication, HTTP request, errors, write plan and explicit execution |
| `skills/<name>/SKILL.md` | Operations, pagination, duplicate checks and result verification |
| `CUSTOM.md`, optional | Local inventory purpose, fields, conventions and special workflows |
| `AGENTS.md` | Startup instructions and shared working rules |

Keep public skills generic. Extend an existing skill or add one when a requested workflow
is missing, use it, then keep it for future requests. Local differences belong in CUSTOM.md.
There is no second API client or custom code layer.

Snipe-IT remains the source of truth. Tokens, local instructions, personal data, exports,
photos and backups stay outside Git. Writes require a reviewed plan and explicit execution
within the user's requested scope. Instance-specific API compatibility must be checked
before use; local tests do not establish compatibility with every Snipe-IT version.

## Checks

```bash
python3 -m unittest discover -s tests -v
```

Tests use a local HTTP server and fictitious data, without modifying a real instance.
