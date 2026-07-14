---
paths:
  - "project-control/**"
---

The project-control directory is authoritative. Producer agents may create/update only their own task progress and report files. Reviewers may create gate reports. Only the orchestrator may mark tasks accepted, change dependencies, modify the master plan, or unlock tasks.
