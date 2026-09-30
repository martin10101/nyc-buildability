# Memory index

- [CRLF/LF digest-normalization review method](feedback_crlf_lf_digest_review_method.md) — how to independently QA a line-ending digest-normalization task at a frozen SHA (independent oracle for red/green; extract-LF + synthesize-CRLF for both-representation validate; monkeypatch normalization to identity for the red-half; patch top-level `directive_registry` not `tools.directive_registry`)
