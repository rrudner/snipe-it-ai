# Custom inventory instructions

Copy this file to CUSTOM.md and adapt it to your instance. CUSTOM.md is ignored by Git.
Describe conventions here; store credentials only in local .env or environment variables.
This example is illustrative and does not configure Snipe-IT or authorize writes.

## Purpose

Track shared workshop equipment. Each physical item is a separate asset.

## Local conventions

- Use existing instance categories, models, statuses and locations; record their exact names here.
- Asset tags follow the instance's configured numbering. Check availability before allocation.
- Distinguish ownership from the current holder assigned through checkout.
- Record facts supplied by the user; leave unknown values empty where the instance allows it.

## Custom fields

List the exact field names, allowed values and their meaning. Resolve API DB Field Name
values from the instance; do not put fixed dictionary IDs here.

## Special workflows

Describe local handover, return, inspection or repair steps that differ from generic skills.
For example, confirm included accessories on return and record any reported damage.
Do not assume an item has passed inspection without supplied evidence.
