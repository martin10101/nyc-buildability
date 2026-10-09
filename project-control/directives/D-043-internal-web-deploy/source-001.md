# D-043 source-001 (original, verbatim; owner via interactive chat, 2026-09-12)

Owner message (the directive, verbatim):

> "Authorize the internal web deploy on Render

Capture context: the owner typed the proposed authorization line (leading quote is a copy
artifact). Issued immediately after the D-042 Next.js 15.5.24 upgrade chain produced the
project's first fully green CI (run 34726577993) - i.e., the prior standing restriction
"no hosted web deploy before the Next.js RCE fix" has its condition SATISFIED.

Scope agreed in the same exchange, explicitly: INTERNAL deploy only - an unlisted Render web
service for apps/web behind the unified internal feature flag, pointed at the existing private
API service; NOT a public launch; the current production screens with real data (the visual
redesign remains a separate, later effort); "private" means unlisted + flag-gated + internal/dev
labeling, not secret-proof. Render dashboard actions and any credentials are owner-performed;
nothing sensitive enters repo or chat. The API URL remains private.
