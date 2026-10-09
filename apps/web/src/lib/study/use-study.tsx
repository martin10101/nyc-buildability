"use client";

/**
 * React binding for the shared study store (task C-05, plan M1-10). Two
 * components on the same page that call `useStudy(bbl)` read the same entry and
 * re-render together when it changes (useSyncExternalStore), so the overview,
 * the dashboard tools and any other surface cannot disagree.
 *
 * `StudyStoreProvider` scopes a store to a subtree (tests inject one); without a
 * provider the page's default store is used. On the server the hook always
 * reads "no study", so nothing is shared between requests; write to the store
 * from event handlers or effects, never during render.
 */

import { createContext, useCallback, useContext, useState, useSyncExternalStore, type ReactNode } from "react";
import type { StudyEntry } from "./study-entry";
import { createStudyStore, defaultStudyStore, type StudyStore } from "./study-store";

const StudyStoreContext = createContext<StudyStore | null>(null);

export function StudyStoreProvider({ store, children }: { store?: StudyStore; children: ReactNode }) {
  const [owned] = useState<StudyStore>(() => store ?? createStudyStore());
  return <StudyStoreContext.Provider value={store ?? owned}>{children}</StudyStoreContext.Provider>;
}

export function useStudyStore(): StudyStore {
  return useContext(StudyStoreContext) ?? defaultStudyStore();
}

const NO_UNSUBSCRIBE = (): void => undefined;
const SERVER_SNAPSHOT = (): StudyEntry | null => null;

/** The shared study of the property `bbl` (null when none exists yet or `bbl` is null). */
export function useStudy(bbl: string | null): StudyEntry | null {
  const store = useStudyStore();
  const subscribe = useCallback(
    (listener: () => void) => (bbl === null ? NO_UNSUBSCRIBE : store.subscribe(bbl, listener)),
    [store, bbl],
  );
  const getSnapshot = useCallback(() => (bbl === null ? null : store.get(bbl)), [store, bbl]);
  return useSyncExternalStore(subscribe, getSnapshot, SERVER_SNAPSHOT);
}
