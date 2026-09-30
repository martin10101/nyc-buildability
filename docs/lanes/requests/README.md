# Requests between lanes

A lane that needs a change to a file it does not own writes a request here and moves on to its next
unblocked task (lane prompts, shared rules). The lane that owns the requested file handles it the same
day in a small PR; hot files always go to Lane C.

**File name:** `docs/lanes/requests/<X>-<n>.md`. X is the requesting lane and n counts up per lane.
The requesting lane owns the file (`docs/lanes/OWNERSHIP.yaml`); queues belong to Lane C (the integrator).

**Template:**

```
# <X>-<n>: <one line>

| | |
|---|---|
| From lane | <X> |
| Owner of the file(s) | <lane> (per OWNERSHIP.yaml) |
| Files | <exact paths> |
| Why | <plan task ID and the reason> |
| What is blocked | <queue item(s)> |
| Proposed change | <smallest change that unblocks, e.g. mount route X behind flag Y> |
| State | open / taken by <lane> in <ledger task> / done in <PR> |
```

**State** is updated by the requesting lane (it owns this file), or by the integrator (Lane C) on a non-lane branch (`task/`, `control/`). The lane that owns the requested files never edits the request, and the requesting lane never edits the owner's files.
