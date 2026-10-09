/**
 * Loader for the committed `results` contract fixtures, for unit/component tests ONLY (queue
 * D-05). Nothing here is imported by application code.
 *
 * Reads EVERY file in packages/contracts/fixtures/valid/results/ at test time (read-only), so a
 * fixture added to the contract later is rendered by the same tests with no change here. No
 * number is copied out of the fixtures: tests read values from the loaded documents.
 *
 * The directory resolves from the vitest root (apps/web — the CI job's working directory), NOT
 * from import.meta.url: under the jsdom environment vitest serves modules from a non-file
 * scheme, so a URL-relative read throws ERR_INVALID_URL_SCHEME. Same form as the lot_geometry
 * fixture reader in src/components/address/__tests__/lot-outline-map.test.tsx.
 */

import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { Results } from "@/lib/architect/three-answers";

const RESULTS_FIXTURE_ROOT = resolve(
  process.cwd(),
  "../../packages/contracts/fixtures/valid/results",
);

export interface ResultsFixture {
  /** File name without ".json", e.g. "synthetic_all_answers_available". */
  name: string;
  doc: Results;
}

/** Every valid results fixture, sorted by file name; each call returns fresh copies. */
export function loadResultsFixtures(): ResultsFixture[] {
  return readdirSync(RESULTS_FIXTURE_ROOT)
    .filter(file => file.endsWith(".json"))
    .sort()
    .map(file => ({
      name: file.slice(0, -".json".length),
      doc: JSON.parse(readFileSync(resolve(RESULTS_FIXTURE_ROOT, file), "utf8")) as Results,
    }));
}

/** One valid results fixture by name; throws if it is missing so a test never passes vacuously. */
export function loadResultsFixture(name: string): Results {
  const found = loadResultsFixtures().find(fixture => fixture.name === name);
  if (!found) throw new Error(`results fixture not found: ${name}`);
  return found.doc;
}
