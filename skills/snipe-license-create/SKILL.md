---
name: snipe-license-create
description: Add a requested Snipe-IT license record with its seat count, purchase cost and notes. Use for games when local collection conventions classify them as licenses.
---

# Create a license

Read root AGENTS.md and CUSTOM.md if present. Use only
[scripts/snipe_api.py](../../scripts/snipe_api.py), following [API usage](../../scripts/README.md).

1. Establish the instance version with `GET version`; check the
   [create contract](https://snipe-it.readme.io/reference/testinput).
2. Resolve the License category from `GET categories`. Search `GET licenses` for the
   requested item and any collection number. Process all result pages before deciding
   that no duplicate exists. Distinguish another physical copy from an accidental retry.
3. Prepare `POST licenses` with `name`, `seats`, `category_id` and supplied facts.
   Follow local naming and seat conventions. Retain platform, edition, condition and
   contents in supported fields or notes. Leave unknown dates, owners and keys empty.
   License keys are sent as `serial`, although reads return `product_key`.
4. Print the plan without `--apply`; execute with `--apply` only within the user's
   explicit creation request. After an uncertain outcome, inspect the actual state
   before retrying.
5. Fetch `GET licenses/ID` using the returned ID and compare name, category, seat count,
   cost and notes with the plan. Report the verified record. Keep payloads and responses
   out of Git.
