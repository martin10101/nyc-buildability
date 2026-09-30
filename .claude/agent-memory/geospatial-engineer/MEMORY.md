# Memory index

- [Source accuracy facts](project_source-accuracy-facts.md) — nyzd +/-20 ft documented; MapPLUTO accuracy NOT documented (assumed); ZTLDB has no percentages, possible vintage skew (OQ-3)
- [Connector internal_error log safety](connector-internal-error-log-safety.md) — findable-but-non-leaky log: log class+constant only, NEVER str(exc); sanitize_retry_after doesn't strip text
