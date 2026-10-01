---
name: snipe-asset-create
description: Add a physical inventory item as a Snipe-IT asset, reusing or creating its model. Use for an explicitly requested new copy, not bulk imports or licenses.
---

# Create an asset

Use [scripts/snipe_api.py](../../scripts/snipe_api.py) for every API request;
see [API usage](../../scripts/README.md). Read root AGENTS.md and CUSTOM.md if present.

1. Establish the instance version with `GET version` and check the current contracts:
   [create asset](https://snipe-it.readme.io/reference/hardware-create),
   [create model](https://snipe-it.readme.io/reference/models-1).
2. Resolve categories, models, status labels, fieldsets and custom-field DB column names
   from the instance. Reuse a model only when its item variant or title, platform and
   edition match. Create missing dictionary records only as required by this request.
3. Search existing assets by title and tag, including archived and deleted records.
   Process every matching page; incomplete or failed searches do not establish absence.
   Preserve established tag conventions and verify a proposed tag has no exact match
   before writing. A different physical copy may share a model, never a tag.
4. Prepare `POST models` only if needed, then `POST hardware` with resolved `model_id`,
   `status_id`, unique `asset_tag` and supplied facts. Store condition and contents in
   supported fields or notes. Do not infer purchase dates, ownership or test results.
   Use custom-field choices when available; if a requested value is unavailable, retain
   it in the model name or notes rather than silently changing shared configuration.
5. Print each write plan without `--apply`. Execute with `--apply` only within the user's
   explicit add request. Verify any new model before using its returned ID.
6. Fetch the created asset by returned ID and compare its tag, model, price, notes and
   custom fields with the planned data. After an uncertain write, inspect the actual
   outcome before retrying. Report the verified record and any missing requested data.

Keep payloads and responses out of Git; use temporary files when necessary.
