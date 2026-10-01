---
name: snipe-asset-checkout
description: Assign existing Snipe-IT assets, license seats and available accessory units to a confirmed user.
---

# Assign inventory

Read root AGENTS.md and CUSTOM.md. Use scripts/snipe_api.py for every API request.

1. Resolve each asset and target user from the instance. Ownership must come from
   confirmed user instructions or an explicit ownership field or note; names and existing
   assignments alone do not prove ownership. Preserve correct existing assignments.
2. Check the instance version and the official
   [checkout contract](https://snipe-it.readme.io/reference/hardware-checkout).
   Use `POST hardware/ID/checkout` with `checkout_to_type: user`, resolved `assigned_user`
   and the existing deployable `status_id`. Do not make archived or untested assets
   deployable merely to satisfy checkout.
3. If another holder is assigned, resolve the requested transfer before changing it.
   Retain ownership notes and default storage. Do not infer a historical checkout date.
4. Inspect the plan without `--apply`, then execute within the user's assignment request.
5. Fetch the asset and verify the holder, tag, status, ownership notes and default storage.
   After an uncertain write, inspect the assignment before retrying.

## License seats and accessories

- Paginate licenses and `GET licenses/ID/seats`. A seat is unassigned only when both
  `assigned_user` and `assigned_asset` are empty. Preserve existing assignments.
- Check the official [seat update contract](https://snipe-it.readme.io/reference/licensesidseatsseat_id-2).
  Assign a resolved seat with `PATCH licenses/ID/seats/SEAT_ID` and `assigned_to: USER_ID`.
  Fetch its seats again to verify the user and unchanged asset assignment; verify license
  notes and unrelated fields remain unchanged.
- Paginate accessories and inspect `GET accessories/ID/checkedout`. Asset and location
  checkouts count as existing assignments. Use only available units reported by `remaining`.
- Check the official [accessory checkout contract](https://snipe-it.readme.io/reference/accessories-checkout).
  Use `POST accessories/ID/checkout` with `assigned_user` and `checkout_qty` within
  available stock. Verify remaining stock and checkout rows after each write.
- Inspect every write plan without `--apply`, then apply only the requested scope.
  After uncertain writes, establish the actual outcome before retrying. Do not add seats,
  stock, ownership notes or change archived statuses merely to satisfy an assignment.
