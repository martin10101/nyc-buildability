/**
 * Loader for the committed `results` contract fixtures, for unit/component tests ONLY (queue
 * D-05). Nothing here is imported by application code.
 *
 * Reads EVERY file in packages/contracts/fixtures/valid/results/ at test time (read-only), so a
 * fixture added to the contract later is rendered by the same tests with no change here. No
 * number is copied out of the fixtures: tests read values from the loaded documents.
 */

import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ThreeAnswersResults } from "@/lib/architect/results-document";

// apps/web/src/test-support/ -> repository root -> the valid results fixtures.
const RESULTS_FIXTURE_DIR = fileURLToPath(
  new URL("../../../../packages/contracts/fixtures/valid/results/", import.meta.url).href,
);

export interface ResultsFixture {
  /** File name without ".json", e.g. "synthetic_all_answers_available". */
  name: string;
  doc: ThreeAnswersResults;
}

/** Every valid results fixture, sorted by file name; each call returns fresh copies. */
export function loadResultsFixtures(): ResultsFixture[] {
  return readdirSync(RESULTS_FIXTURE_DIR)
    .filter(file => file.endsWith(".json"))
    .sort()
    .map(file => ({
      name: file.slice(0, -".json".length),
      doc: JSON.parse(readFileSync(join(RESULTS_FIXTURE_DIR, file), "utf8")) as ThreeAnswersResults,
    }));
}

/** One valid results fixture by name; throws if it is missing so a test never passes vacuously. */
export function loadResultsFixture(name: string): ThreeAnswersResults {
  const found = loadResultsFixtures().find(fixture => fixture.name === name);
  if (!found) throw new Error(`results fixture not found: ${name}`);
  return found.doc;
}
