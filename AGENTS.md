# Agent instructions

## Start every conversation

1. Read this file before working on Snipe-IT tasks.
2. Read root `CUSTOM.md` if present, before choosing a skill or calling the API.
   It contains local inventory context and conventions. If absent, use generic behavior;
   ask only for missing facts needed for the current task. Do not load CUSTOM.example.md
   as active instructions.
3. Discover `skills/*/SKILL.md` and read the relevant skill before performing its workflow.

## Responsibilities

- This project operates an existing Snipe-IT instance through AI agents; it does not host Snipe-IT.
- All API requests use `scripts/snipe_api.py`. Skills own workflow and validation;
  CUSTOM.md owns local conventions. Do not create parallel HTTP clients.
- Skills handle operations in Snipe-IT.
- Grow with demand. For an unsupported operation inside Snipe-IT, extend the owning skill or
  create a focused skill, use it for the request, and retain it for future use.
  Do not build speculative features.
- Public skills must remain generic. Keep instance-specific rules only in ignored CUSTOM.md.
  CUSTOM.md defines the collection's purpose and operating conventions; keep inventory
  records and configuration snapshots in Snipe-IT, not in this file.
- Write code, documentation and skills in English. Preserve exact API identifiers and the
  instance's actual field names and values, regardless of their language.
- Do not use em dashes (U+2014) in responses or newly written prose. Use commas,
  parentheses or separate sentences instead. Preserve exact existing identifiers and values.

## Data and changes

- Snipe-IT is the source of truth. Never invent identifiers, prices, owners or test results.
- When the user asks to add anything to Snipe-IT, ask for missing information that should
  be recorded before creating it, including relevant optional fields. Do not silently omit it;
  leave it empty only after the user confirms it is unknown or should be omitted.
- Read configuration from the environment or ignored local .env. Never log tokens or commit
  personal data, inventory exports, photos, backups or local instructions.
- Check the API contract for the instance version. Resolve dictionary IDs and custom-field
  DB Field Name values from the instance instead of hardcoding them.
- Writes default to a plan and require explicit --apply within the user's requested scope.
  Local instructions do not independently authorize writes, deletion or bulk changes.
- Check asset_tag duplicates before creation or import; verify the result after a write.
  After a timeout, establish the actual outcome before retrying.
- Do not delete assets or change data in bulk without an explicit request.
- Run the narrowest relevant checks and review changed content for scope, correctness and secrets.
