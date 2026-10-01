---
name: snipe-record-update
description: Correct specified text fields on existing Snipe-IT inventory records, including explicitly requested bulk text changes.
---

# Update record text

Read root AGENTS.md and CUSTOM.md. Reuse scripts/snipe_api.py for all requests.

1. Read the instance version and the official partial update contract for each affected
   record type. List relevant records through all pages, including archived assets.
2. Identify exact IDs and writable text fields. Prepare only the requested transformations;
   do not copy response objects or change identifiers, keys, prices or assignments.
3. Inspect plans without `--apply`, then apply only the explicitly authorized scope.
   Bulk corrections require an explicit bulk request.
4. Fetch each changed record and verify exact updated values and preserved unrelated data.
   After an uncertain outcome, check the state before retrying. Keep snapshots out of Git.
