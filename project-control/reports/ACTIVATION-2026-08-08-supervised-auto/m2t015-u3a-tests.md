# M2-T015 unit-3a test evidence (orchestrator capture)
worktree HEAD: a059b5000a6cd5d6e9061347066d7ec79166dfd5  branch: task/M2-T015-survey-ingestion
command: python -m pytest tests/documents/ -q (cwd services/api)
```
........................................                                 [100%]
40 passed in 0.07s
EXIT:0
```
duplicate error classes flagged by Codex REVISE:
app/documents/errors.py:112:class IllegalTransitionError(DocumentIngestionError):
app/documents/state.py:88:class IllegalTransition(DocumentStateError):
