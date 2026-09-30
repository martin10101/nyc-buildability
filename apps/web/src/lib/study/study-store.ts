/**
 * The study store: ONE shared study per property, keyed by the property BBL
 * (task C-05, plan M1-10; plan section 9). Every surface on a page that reads the
 * same BBL reads the same entry, so they cannot disagree. Framework-free: React
 * binds to it through ./use-study (useSyncExternalStore).
 *
 * Writes go through the pure operations (./study-operations,
 * ./parcel-study-adapter): `ensure` creates the study only when the property
 * has none yet (a second surface gets the first one's study), `update` applies
 * one operation, `replace` installs a study built elsewhere (for example one
 * started from a file with ./study-import startStudyFromImport, which copies
 * inputs only). A failed operation changes nothing and notifies nobody.
 *
 * Browser memory only: no storage, no network. Saved revisions are C-06 / B-001.
 */

import { studyFailure, type StudyEntry, type StudyResult } from "./study-entry";

export interface StudyStore {
  get(bbl: string): StudyEntry | null;
  subscribe(bbl: string, listener: () => void): () => void;
  /** The property's study; `create` runs only when there is none yet. */
  ensure(bbl: string, create: () => StudyResult): StudyResult;
  /** Apply one operation to the property's study. */
  update(bbl: string, change: (entry: StudyEntry) => StudyResult): StudyResult;
  /** Install a study for its property, replacing any current one. */
  replace(result: StudyResult): StudyResult;
  remove(bbl: string): void;
}

export function createStudyStore(): StudyStore {
  const entries = new Map<string, StudyEntry>();
  const listeners = new Map<string, Set<() => void>>();

  function notify(bbl: string): void {
    const set = listeners.get(bbl);
    if (!set) return;
    for (const listener of [...set]) listener();
  }

  function commit(bbl: string, result: StudyResult): StudyResult {
    if (!result.ok) return result;
    if (result.entry.study.property.bbl !== bbl) {
      return studyFailure("wrong_property", "This study belongs to another property; nothing was changed.");
    }
    if (entries.get(bbl) !== result.entry) {
      entries.set(bbl, result.entry);
      notify(bbl);
    }
    return result;
  }

  return {
    get: (bbl) => entries.get(bbl) ?? null,
    subscribe(bbl, listener) {
      const set = listeners.get(bbl) ?? new Set<() => void>();
      set.add(listener);
      listeners.set(bbl, set);
      return () => {
        set.delete(listener);
        if (set.size === 0 && listeners.get(bbl) === set) listeners.delete(bbl);
      };
    },
    ensure(bbl, create) {
      const current = entries.get(bbl);
      if (current) return { ok: true, entry: current };
      return commit(bbl, create());
    },
    update(bbl, change) {
      const current = entries.get(bbl);
      if (!current) return studyFailure("no_study", "There is no study for this property yet.");
      return commit(bbl, change(current));
    },
    replace(result) {
      return result.ok ? commit(result.entry.study.property.bbl, result) : result;
    },
    remove(bbl) {
      if (entries.delete(bbl)) notify(bbl);
    },
  };
}

/** The ISO time of a change, for the operations' `at` argument. */
export function studyTimestamp(): string {
  return new Date().toISOString();
}

let browserStore: StudyStore | null = null;

/**
 * The page's store when no StudyStoreProvider supplies one. In the browser it is
 * one store per page load. On the server every call gets a new, empty store, so
 * no study is ever shared between requests (the React hook also reads nothing
 * on the server).
 */
export function defaultStudyStore(): StudyStore {
  if (typeof window === "undefined") return createStudyStore();
  if (!browserStore) browserStore = createStudyStore();
  return browserStore;
}
