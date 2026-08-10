/**
 * `SurveyReviewClient` backed by the in-memory mock backend, for component
 * tests ONLY (task M2-T016). Wraps the REAL HTTP client with a store-backed
 * `fetch` so the client's decode/validation path is exercised. The stateful
 * reducer lives in ./mockBackend.ts (which is also imported by Playwright e2e
 * without a runtime `@/` alias). Not shipped.
 */

import { createHttpSurveyReviewClient } from "@/lib/surveyReview/api";
import type { SurveyReviewClient } from "@/lib/surveyReview/types";
import { createStoreFetch, seedStore, type MockStore } from "./mockBackend";

export { seedStore } from "./mockBackend";
export type { MockStore } from "./mockBackend";

export function createMockSurveyReviewClient(store: MockStore = seedStore()): SurveyReviewClient {
  const http = createHttpSurveyReviewClient();
  const fetchImpl = createStoreFetch(store);
  return {
    readDocument: (id, o = {}) => http.readDocument(id, { fetchImpl, ...o }),
    listInbox: (state, o = {}) => http.listInbox(state, { fetchImpl, ...o }),
    acceptFact: (req, o = {}) => http.acceptFact(req, { fetchImpl, ...o }),
    correctFact: (req, o = {}) => http.correctFact(req, { fetchImpl, ...o }),
    rejectFact: (req, o = {}) => http.rejectFact(req, { fetchImpl, ...o }),
    rejectDocument: (req, o = {}) => http.rejectDocument(req, { fetchImpl, ...o }),
    confirmDocument: (req, o = {}) => http.confirmDocument(req, { fetchImpl, ...o }),
    requestReExtraction: (req, o = {}) => http.requestReExtraction(req, { fetchImpl, ...o }),
  };
}
