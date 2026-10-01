---
name: snipe-asset-location
description: Set an existing Snipe-IT asset's default storage location without changing checkout or ownership.
---

# Set an asset's default location

Read root AGENTS.md and optional CUSTOM.md. Use the shared
[API transport](../../scripts/README.md) for every request.

1. Identify one existing asset through [asset-read](../snipe-asset-read/SKILL.md).
   Resolve a supplied name to a unique record and its actual tag before tag lookup;
   do not infer a tag from a model or use an ambiguous match.
2. Read `locations` with `limit=100` and successive offsets until `total` is processed.
   Resolve the requested location case-insensitively and preserve its actual name.
   Stop on ambiguous matches, repeated pages, premature empty pages, or invalid shapes.
3. Check the instance version and the official
   [partial asset update contract](https://snipe-it.readme.io/reference/hardware-partial-update).
   `rtd_location_id` is the usual storage location when not checked out. It does not
   establish the current holder's location or authorize checkout/checkin changes.
4. Read `hardware/<id>` and retain its tag, default location, status and assignment
   for verification. If the requested default location is already set, report no change.
5. Prepare `PATCH hardware/<id>` with only `{"rtd_location_id": <resolved location ID>}`.
   Run without `--apply` to inspect the plan. Execute with `--apply` only when the
   user has authorized this location change; do not create locations implicitly.
6. Read the asset again and verify its default location, tag, status and assignment.
   After an uncertain write outcome, establish the actual state before retrying.
