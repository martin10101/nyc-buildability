"use client";

/**
 * Lot choice + site facts with source labels (queue D-04, plan M1-13, §3 steps
 * 2-3, §4; §5a). Presentation only, over a contract-shaped lot-choice + site-facts
 * source. It renders:
 *  - the lots that make up the site, each with its approximate size and source,
 *    and — for more than one lot — a "use all (default) or pick" re-pick control;
 *  - whether the selected lots were combined, and — when they were not — the
 *    reason, taken verbatim from B-07's `lot_selection.combination` (the web
 *    never re-checks geometry or adjacency, lane prompt);
 *  - the owner-pinned statement that the app does not verify the zoning lot;
 *  - each site fact with its source label (full source behind a tap), and a
 *    per-fact edit: a typed value is recorded as "Entered" beside the city value.
 *
 * Where the data comes from (the slice-2 design decision; see the producer report):
 *  - When the C-05 store already holds a study for this property (an option has
 *    been confirmed elsewhere), the panel reads and mutates THAT study: a re-pick
 *    calls `repickLots` and a per-fact edit calls `enterSiteFactValue`.
 *  - Otherwise the panel FETCHES the server study SETUP (`fetchStudySetup`) and
 *    renders it directly, holding a working copy. It does NOT `ensureStudyFromSetup`
 *    here: that needs the architect's confirmed option inputs, and nothing in the
 *    app confirms an option at lot setup yet — inventing option inputs is forbidden
 *    (plan M1-06). So the store is ensured only once an option is confirmed; until
 *    then the setup is the honest, real, server-produced source. A re-pick re-fetches
 *    with `selected`; a per-fact edit mirrors enterSiteFactValue on the working copy.
 *
 * No measurement is invented: with no server setup (404 / flag off) the panel shows
 * a plain "not connected yet" card, never a guessed number (plan §5a item 3). The
 * loading, error and empty states follow §5a and reuse the dashboard failure-notice
 * card. No legal logic and no zoning math live here.
 */

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import {
  applyEnteredFactToSource,
  groupSiteFactRows,
  lotChoiceViewOf,
  siteFactRowsOf,
  sourceFromSetup,
  sourceFromStudy,
  validateFactInput,
  type LotRow,
  type LotSiteSource,
  type SiteFactGroup,
} from "@/lib/architect/lot-site-setup";
import { enterSiteFactValue } from "@/lib/study/study-operations";
import {
  fetchStudySetup,
  repickLots,
  type StudySetupFetchOutcome,
} from "@/lib/study/study-setup-api";
import type { SiteFact, Study } from "@/lib/study/study-vocabulary";
import { useStudy, useStudyStore } from "@/lib/study/use-study";
import { FailureNoticeCard } from "./workspace/DashboardFailureNotice";
import { referenceRow, type DashboardFailureNoticeModel } from "./workspace/dashboard-failure";

const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";
const RETRY_SAFE = "The site inputs are fine. Trying again is safe.";

/**
 * The §5a failure notice for a non-setup study-setup fetch outcome, or null when the panel handles
 * the outcome another way (`setup` is success; `not_available` is the "not connected yet" empty
 * card; `aborted` is a superseded request that owns no surface). Reuses the dashboard failure model
 * so the same honest wording is shared; no internal code appears on the face (§5a items 4-5).
 */
export function studySetupFailureNotice(
  outcome: StudySetupFetchOutcome,
): DashboardFailureNoticeModel | null {
  switch (outcome.kind) {
    case "setup":
    case "not_available":
    case "aborted":
      return null;
    case "validation_error":
      return {
        title: "The app could not read this property identifier",
        body: outcome.message,
        recovery: "Check the identifier and try another lot.",
        retryable: false,
        technical: [{ label: "Rejection code", value: outcome.code }, ...referenceRow(outcome.correlationId)],
      };
    case "inputs_unavailable":
      return {
        title: "The site setup is not available right now",
        body: outcome.message,
        recovery: "The official city source did not return the site inputs yet. Trying again is safe.",
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "server_contract_error":
      return {
        title: "The app would not show unreliable site data",
        body: "The server built a site setup that failed its own quality checks and held it back rather than show data it could not trust.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: [{ label: "Failure type", value: "internal_contract_error" }, ...referenceRow(outcome.correlationId)],
      };
    case "internal_error":
      return {
        title: "Something went wrong on our side",
        body: "The app hit an unexpected problem while loading the site setup.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "validation_failure":
      return {
        title: "The site setup did not match the published data format",
        body: "The service returned a site setup that failed this screen's format check. Nothing from that response is shown.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: [
          ...outcome.problems.map((problem) => ({ label: "Format problem", value: problem })),
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "network_error":
      return {
        title: "Could not reach the app's service",
        body: outcome.message,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "client_timeout":
      return {
        title: "The site setup took too long",
        body:
          `The service did not answer within ${Math.round(outcome.timeoutMs / 1000)} seconds, ` +
          "so the request was cancelled. No partial data is shown.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "unexpected_response":
      return {
        title: "Unexpected response from the service",
        body: "The service answered in a way the app does not recognize, so the response was not trusted or shown.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [
          { label: "HTTP status", value: String(outcome.httpStatus) },
          ...(outcome.receivedState ? [{ label: "Response state", value: outcome.receivedState }] : []),
          ...referenceRow(outcome.correlationId),
        ],
      };
  }
}

type PanelStatus = { kind: "empty" } | { kind: "error"; model: DashboardFailureNoticeModel };

export interface LotSiteSetupProps {
  bbl: string;
  /** A study passed directly (display override for tests); absent reads the C-05 store or fetches. */
  study?: Study | null;
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
  /** RFC 3339 clock for recorded edits; defaults to the wall clock. */
  now?: () => string;
}

interface LotSiteSetupState {
  status: PanelStatus | null;
  source: LotSiteSource | null;
  busy: boolean;
  retry: () => void;
  /** Records the edit; returns null on success, or a plain reason to show on the row. */
  editFact: (fact: SiteFact, raw: string) => string | null;
  repick: (selected: readonly string[]) => Promise<void>;
}

function useLotSiteSetup({ bbl, study: studyProp, fetchImpl, now }: LotSiteSetupProps): LotSiteSetupState {
  const clock = useMemo(() => now ?? (() => new Date().toISOString()), [now]);
  const store = useStudyStore();
  const stored = useStudy(bbl);
  const storeStudy = stored?.study ?? null;
  const propStudy = studyProp ?? null;
  const [local, setLocal] = useState<LotSiteSource | null>(null);
  const [status, setStatus] = useState<PanelStatus | null>(null);
  const [reload, setReload] = useState(0);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    // A study (store first, then an explicit prop) drives directly; the store study is read live
    // below, and a prop study seeds a working copy. Only with neither do we fetch the setup.
    if (storeStudy) {
      setLocal(null);
      setStatus(null);
      return;
    }
    if (propStudy) {
      setLocal(sourceFromStudy(propStudy));
      setStatus(null);
      return;
    }
    let cancelled = false;
    setStatus(null);
    setLocal(null);
    void (async () => {
      const outcome = await fetchStudySetup(bbl, { fetchImpl });
      if (cancelled) return;
      if (outcome.kind === "setup") {
        setLocal(sourceFromSetup(outcome.setup));
        return;
      }
      if (outcome.kind === "aborted") return; // superseded; the live request owns the surface
      if (outcome.kind === "not_available") {
        setStatus({ kind: "empty" });
        return;
      }
      const model = studySetupFailureNotice(outcome);
      setStatus(model ? { kind: "error", model } : { kind: "empty" });
    })();
    return () => {
      cancelled = true;
    };
  }, [bbl, storeStudy, propStudy, fetchImpl, reload]);

  const source = storeStudy ? sourceFromStudy(storeStudy) : local;

  const retry = useCallback(() => setReload((value) => value + 1), []);

  const editFact = useCallback(
    (fact: SiteFact, raw: string): string | null => {
      const parsed = validateFactInput(fact, raw);
      if (!parsed.ok) return parsed.reason;
      if (stored) {
        const result = store.update(bbl, (entry) =>
          enterSiteFactValue(entry, { factId: fact.fact_id, value: parsed.value }, clock()),
        );
        return result.ok ? null : "That value could not be recorded.";
      }
      if (local) {
        const next = applyEnteredFactToSource(local, fact.fact_id, parsed.value, clock());
        if (!next.ok) return next.reason;
        setLocal(next.source);
        return null;
      }
      return "That value could not be recorded.";
    },
    [stored, store, bbl, local, clock],
  );

  const repick = useCallback(
    async (selected: readonly string[]): Promise<void> => {
      setBusy(true);
      try {
        if (stored) {
          // The store (B-07 through repickLots) decides the lots and the combination; a
          // fetch_failed leaves the study unchanged, and the store notifies on success.
          await repickLots(store, bbl, selected, clock(), { fetchImpl });
          return;
        }
        const outcome = await fetchStudySetup(bbl, { selected, fetchImpl });
        if (outcome.kind === "setup") {
          setLocal(sourceFromSetup(outcome.setup));
          return;
        }
        if (outcome.kind === "aborted") return;
        const model = studySetupFailureNotice(outcome);
        if (model) setStatus({ kind: "error", model });
      } finally {
        setBusy(false);
      }
    },
    [stored, store, bbl, fetchImpl, clock],
  );

  return { status, source, busy, retry, editFact, repick };
}

function LoadingCard() {
  return (
    <section className="card architect-empty" role="status" aria-busy="true" data-testid="lot-site-loading">
      <p className="architect-eyebrow">Lot &amp; site setup</p>
      <p>Loading the lots and site facts…</p>
    </section>
  );
}

function NotConnectedCard() {
  return (
    <section className="card architect-empty" data-testid="lot-site-unavailable">
      <p className="architect-eyebrow">Lot &amp; site setup</p>
      <h2>Site setup is not connected yet</h2>
      <p>
        The lots that make up this site and their pre-filled measurements are prepared by the
        site-facts service. That data is not connected to this screen yet, so there is nothing to
        show here. No measurements are guessed.
      </p>
    </section>
  );
}

/** "Use all (default), or pick": the architect's selection is sent to the server, which (B-07)
 * decides the lots and whether the combination is offered. The web computes no adjacency. */
function LotRepick({
  lots,
  busy,
  onRepick,
}: {
  lots: LotRow[];
  busy: boolean;
  onRepick: (selected: readonly string[]) => void;
}) {
  const [selected, setSelected] = useState<ReadonlySet<string>>(
    () => new Set(lots.filter((lot) => lot.selected).map((lot) => lot.bbl)),
  );
  const signature = lots.map((lot) => `${lot.bbl}:${lot.selected ? 1 : 0}`).join(",");
  useEffect(() => {
    setSelected(new Set(lots.filter((lot) => lot.selected).map((lot) => lot.bbl)));
    // Re-sync when the server returns a new lot set after a re-pick.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature]);

  function toggle(bbl: string) {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(bbl)) next.delete(bbl);
      else next.add(bbl);
      return next;
    });
  }

  return (
    <fieldset className="lot-site-repick" data-testid="lot-site-repick" disabled={busy}>
      <legend>Choose the lots that make up the site</legend>
      <ul className="lot-site-repick__list">
        {lots.map((lot) => (
          <li key={lot.bbl}>
            <label>
              <input
                type="checkbox"
                checked={selected.has(lot.bbl)}
                onChange={() => toggle(lot.bbl)}
                data-testid={`lot-pick-${lot.bbl}`}
              />
              {lot.lotLabel} · {lot.sizeText}
            </label>
          </li>
        ))}
      </ul>
      <div className="lot-site-repick__actions">
        <button
          type="button"
          className="secondary-button"
          data-testid="lot-repick-apply"
          onClick={() => onRepick([...selected])}
        >
          Update the site lots
        </button>
        <button
          type="button"
          className="architect-text-button"
          data-testid="lot-repick-all"
          onClick={() => onRepick([])}
        >
          Use all lots
        </button>
      </div>
      {busy ? (
        <p className="section-note" role="status" data-testid="lot-repick-busy">
          Updating the lots…
        </p>
      ) : null}
    </fieldset>
  );
}

/** One fact group: the city/original value, the architect's "Entered" value beside it when one was
 * recorded, the source on tap, and the per-fact edit. */
function SiteFactGroupRow({
  group,
  fact,
  onEdit,
}: {
  group: SiteFactGroup;
  fact: SiteFact | undefined;
  onEdit: (fact: SiteFact, raw: string) => string | null;
}) {
  const { primary, entered } = group;
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  function open() {
    setEditing(true);
    setError(null);
    setValue("");
  }

  function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!fact) {
      setError("That value could not be recorded.");
      return;
    }
    const reason = onEdit(fact, value);
    if (reason) {
      setError(reason);
      return;
    }
    setEditing(false);
    setValue("");
    setError(null);
  }

  return (
    <div data-testid={`site-fact-${primary.factId}`} data-fact-key={primary.key} className="lot-site-fact">
      <dt>{primary.label}</dt>
      <dd>
        <span
          className={`lot-site-fact__value${primary.isUnknown ? " lot-site-fact__value--unknown" : ""}`}
        >
          {primary.valueText}
        </span>
        <span className="lot-site-fact__source">{primary.sourceLabel}</span>
        {entered ? (
          <span className="lot-site-fact__entered" data-testid={`site-fact-entered-${primary.factId}`}>
            {entered.sourceLabel}: {entered.valueText}
          </span>
        ) : null}
        {primary.isUnknown && primary.blocks.length ? (
          <p className="lot-site-fact__blocks">Needed for: {primary.blocks.join(", ")}.</p>
        ) : null}
        <details className="lot-site-fact__detail">
          <summary>Source</summary>
          <ul>
            {primary.sourceLines.map((line, index) => (
              <li key={index}>{line}</li>
            ))}
          </ul>
        </details>
        {primary.editable ? (
          editing ? (
            <form className="lot-site-fact__edit" onSubmit={save}>
              <label>
                New value for {primary.label}
                <input
                  type="text"
                  inputMode="text"
                  value={value}
                  onChange={(event) => setValue(event.target.value)}
                  data-testid={`site-fact-input-${primary.factId}`}
                  autoFocus
                />
              </label>
              <button type="submit" className="secondary-button" data-testid={`site-fact-save-${primary.factId}`}>
                Save
              </button>
              <button
                type="button"
                className="architect-text-button"
                onClick={() => {
                  setEditing(false);
                  setError(null);
                }}
              >
                Cancel
              </button>
              {error ? (
                <p className="lot-site-fact__error" role="alert" data-testid={`site-fact-error-${primary.factId}`}>
                  {error}
                </p>
              ) : null}
            </form>
          ) : (
            <button
              type="button"
              className="architect-text-button"
              data-testid={`site-fact-edit-${primary.factId}`}
              aria-label={`${entered ? "Change" : "Enter"} the value for ${primary.label}`}
              onClick={open}
            >
              {entered ? "Change value" : "Enter a value"}
            </button>
          )
        ) : null}
      </dd>
    </div>
  );
}

export function LotSiteSetup({ bbl, study, fetchImpl, now }: LotSiteSetupProps) {
  const { status, source, busy, retry, editFact, repick } = useLotSiteSetup({ bbl, study, fetchImpl, now });

  if (status?.kind === "error") {
    return <FailureNoticeCard model={status.model} onRetry={retry} testId="lot-site-failure" focusTitle />;
  }
  if (status?.kind === "empty") return <NotConnectedCard />;
  if (!source) return <LoadingCard />;

  const choice = lotChoiceViewOf(source);
  const groups = groupSiteFactRows(siteFactRowsOf(source.siteFacts));
  const factById = new Map(source.siteFacts.map((fact): [string, SiteFact] => [fact.fact_id, fact]));

  return (
    <div data-testid="lot-site-setup" className="lot-site-setup">
      <section className="card" aria-label="Lot choice">
        <h2>{choice.heading}</h2>
        <p className="section-note">{choice.pickLine}</p>
        <ul className="lot-site-list">
          {choice.lots.map((lot) => (
            <li key={lot.bbl} data-testid={`lot-row-${lot.bbl}`} className="lot-site-row">
              <span className="lot-site-row__main">
                {lot.lotLabel} · {lot.sizeText}
              </span>
              <span className="lot-site-row__source">{lot.sourceLabel}</span>
              <span className="lot-site-row__pick">{lot.selected ? "In the site" : "Not selected"}</span>
            </li>
          ))}
        </ul>
        {choice.count > 1 ? <LotRepick lots={choice.lots} busy={busy} onRepick={repick} /> : null}
        <div
          className={`lot-site-combination${choice.combination.refused ? " lot-site-combination--refused" : ""}`}
          role={choice.combination.refused ? "note" : undefined}
          data-testid={choice.combination.refused ? "lot-combination-refusal" : "lot-combination"}
        >
          <p className="lot-site-combination__heading">{choice.combination.heading}</p>
          {choice.combination.detail ? <p>{choice.combination.detail}</p> : null}
        </div>
        <p className="lot-site-statement" role="note" data-testid="lot-site-statement">
          {choice.statement}
        </p>
      </section>

      <section className="card" aria-label="Site facts">
        <h2>Site facts</h2>
        <p className="section-note">
          Each value shows where it came from. Enter your own value for any fact — it is recorded as
          &ldquo;Entered&rdquo; and the city value stays on file beside it. Nothing here has to be
          typed when a city value is on file.
        </p>
        <dl className="lot-site-facts">
          {groups.map((group) => (
            <SiteFactGroupRow
              key={group.primary.factId}
              group={group}
              fact={factById.get(group.primary.factId)}
              onEdit={editFact}
            />
          ))}
        </dl>
      </section>
    </div>
  );
}
