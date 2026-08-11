"use client";

/**
 * Survey-review client CONTEXT (task M2-T016).
 *
 * Components read the `SurveyReviewClient` from this context instead of
 * importing the HTTP client directly. Production trees get the default
 * HTTP-backed client; component tests inject a spec-shaped mock; Playwright
 * e2e uses the real HTTP client with route interception. This is the single
 * seam that keeps the backend contract reconcilable in one place.
 */

import { createContext, useContext, useMemo, type ReactNode } from "react";
import { createHttpSurveyReviewClient } from "./api";
import type { SurveyReviewClient } from "./types";

const SurveyReviewClientContext = createContext<SurveyReviewClient | null>(null);

export function SurveyReviewClientProvider({
  client,
  children,
}: {
  /** Injected client (tests/e2e). Omit to use the default HTTP client. */
  client?: SurveyReviewClient;
  children: ReactNode;
}) {
  const value = useMemo(() => client ?? createHttpSurveyReviewClient(), [client]);
  return (
    <SurveyReviewClientContext.Provider value={value}>
      {children}
    </SurveyReviewClientContext.Provider>
  );
}

export function useSurveyReviewClient(): SurveyReviewClient {
  const client = useContext(SurveyReviewClientContext);
  if (!client) {
    throw new Error("useSurveyReviewClient must be used within a SurveyReviewClientProvider");
  }
  return client;
}
