---
name: snipe-asset-read
description: Find a Snipe-IT asset by asset_tag, inspect its data, or check whether a tag already exists. Use for read-only asset lookup and duplicate checks.
---

# Read an asset

Use scripts/snipe_api.py from the repository root. Read [AGENTS.md](../../AGENTS.md)
and CUSTOM.md if present before selecting operations. Configuration and arguments:
[API usage](../../scripts/README.md).

1. Establish the requested asset_tag; do not infer it from a model name. Before first use
   on an instance, establish its version and check the
   [hardware list contract](https://snipe-it.readme.io/reference/hardware-list).
2. Search using a single argument for the tag. Do not interpolate raw user text into shell code:

   ```bash
   python3 scripts/snipe_api.py GET hardware --param 'search=ASSET-000001' --param 'limit=100' --param 'offset=0'
   ```

   Replace the fictitious tag with the requested tag.
3. search matches multiple fields. From rows, keep only records whose asset_tag exactly
   matches the requested tag; a substring or matching asset name is insufficient.
4. Fetch successive pages, increasing offset by the number of returned records until
   total is processed. If a page repeats, is empty before total is reached, or has an
   unexpected response shape, stop and report an incomplete lookup.
5. Report no asset only after a complete lookup with zero exact matches. With one match,
   return its ID, tag and requested data. With multiple exact matches, report ambiguity.

An API error does not establish that the asset is absent. Do not write response data to Git.
