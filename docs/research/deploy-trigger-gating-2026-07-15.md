# Research: gating Render/Vercel deploys on CI migrations (for M0-T006 rework)

Gathered by the orchestrator on **2026-07-15** via direct fetch of official documentation, to give the M0-T006 rework producer verified platform facts (producer sandbox has no web access). Every claim below carries its official source URL; retrieval date for all entries is 2026-07-15.

## 1. Render Blueprint: `autoDeployTrigger` (replaces deprecated `autoDeploy`)

Source: https://render.com/docs/blueprint-spec (retrieved 2026-07-15)

- The current field is **`autoDeployTrigger`**; the docs state it "replaces the deprecated `autoDeploy` field. If you include both, this field takes precedence."
- Values:
  - `commit` — deploy on each commit to the linked branch ("Equivalent to the deprecated setting `autoDeploy: true`").
  - `checksPass` — "Trigger a deploy only if the linked branch's CI checks pass."
  - `off` — disable auto-deploys ("Equivalent to the deprecated setting `autoDeploy: false`").
- Default if omitted: `commit` for new services; existing services retain their current value.
- Implication for the owner's mandated model: production services must set **`autoDeployTrigger: off`** (not the deprecated `autoDeploy: false`), because even `checksPass` cannot encode the required human-production-approval step — deploys must be initiated by the GitHub Actions pipeline itself.

## 2. Render deploy hooks

Source: https://render.com/docs/deploy-hooks (retrieved 2026-07-15)

- A deploy hook is a per-service **secret URL** (Dashboard → Settings) that triggers "an on-demand deploy of your Render service with a single HTTP request" — "a basic `GET` or `POST` request ... (no special headers required)".
- Security: "Provide the URL only to people and systems you trust to trigger deploys. If you believe a deploy hook URL has been compromised, replace it by clicking **Regenerate Hook**." → store as a GitHub **environment secret** (production environment, required reviewers), never in the repo.
- Query parameters: `ref` (deploy a specific Git commit SHA — lets the pipeline deploy exactly the validated commit) and `imgURL` (image-backed services only).
- Responses: 200 (deploy started, returns deploy ID), 202 (queued behind a running deploy), 401 (unauthorized).
- The docs include an official GitHub Actions example: hook URL stored as a repository secret, called via `curl` after tests pass.

## 3. Vercel: deploying from GitHub Actions instead of git integration

Sources:
- https://vercel.com/guides/how-can-i-use-github-actions-with-vercel (retrieved 2026-07-15)
- https://vercel.com/docs/project-configuration/git-configuration (retrieved 2026-07-15)

- CI-driven deploy sequence (official guide): `vercel pull --yes --environment=<env> --token=$VERCEL_TOKEN` → `vercel build` (`--prod` for production) → `vercel deploy --prebuilt` ("skips the build step on Vercel and uploads the previously generated `.vercel/output` folder"). Required secrets: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
- Disabling automatic git-integration deploys: `vercel.json` → `git.deploymentEnabled` (Type: object keyed by branch, or boolean; **default `true`**). "Specify branches that should not trigger a deployment upon commits." To disable all automatic deployments: `{"git": {"deploymentEnabled": false}}`. Per-branch control is supported (e.g. `{"production": false}`), including minimatch patterns.
- Note: `github.enabled` is deprecated in favor of `git.deploymentEnabled`.

## 4. Consequence for the M0-T006 deployment model (owner directive 2026-07-15)

- Render production services: `autoDeployTrigger: off` in render.yaml; production deploys triggered by GitHub Actions calling the service's deploy hook (with `ref=<validated SHA>`) only after: migration validation → production migrations succeed → required CI checks pass → human production approval (GitHub environment required reviewers).
- Frontend: automatic git deploys disabled for the production branch (`git.deploymentEnabled`), production deploy performed by the same Actions pipeline after migrations succeed. (Under ADR-004, when the frontend moves to Render, the same deploy-hook mechanism applies instead.)
- Any "pipeline halts automatically" language is valid **only** as a description of GitHub Actions job dependencies (`needs:`) inside the deploy workflow — platform-side auto-deploys no longer exist to halt.
