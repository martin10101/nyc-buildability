---
description: Initializes and audits the project control plane before implementation. Use when starting the repository or when the control files are missing.
---

Read all imported project instructions, including `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`. Run:

```bash
python tools/project_control.py init
python tools/project_control.py status
```

Verify the master plan, milestones, task directories, reports, gates, checkpoints, blockers, skills, and agent definitions exist. Create `docs/IMPLEMENTATION_STATUS.md` if missing. Do not implement application features until M0 has ready task packets and G0 passes.


Before installing dependencies or starting services:

1. Detect whether execution is on the owner’s local PC or an approved cloud development environment.
2. Check available disk space.
3. When on the owner’s PC, do not install Docker, local databases, full dependencies, browser binaries, or datasets. Prefer GitHub Codespaces/GitHub Actions/Render/Supabase.
4. Record the execution location and storage plan in the M0 checkpoint.
5. Create a blocker rather than consuming the owner’s remaining disk space.
