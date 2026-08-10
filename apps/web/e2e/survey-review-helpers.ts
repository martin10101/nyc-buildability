import type { Page } from "@playwright/test";
import {
  handleRequest,
  seedStore,
  DIGEST_PRO,
  DIGEST_USER,
  DIGEST_UPLOADED,
  type MockStore,
} from "../src/test-support/survey-review/mockBackend";

export { DIGEST_PRO, DIGEST_USER, DIGEST_UPLOADED };

/**
 * Install the stateful survey-review mock (task M2-T016 rework). Intercepts the
 * digest-keyed review API and serves the same reducer used by the component
 * tests, with closure-held store state persisting across intercepted requests
 * within a test — so the full journey (correct → recalc → confirm) runs without
 * a live backend. The reducer uses only type imports from the app plus a
 * relative fingerprint import, so no runtime `@/` alias is needed here.
 */
export async function installSurveyReviewMock(
  page: Page,
  store: MockStore = seedStore(),
): Promise<MockStore> {
  await page.route("**/api/v1/documents/**", async (route) => {
    const request = route.request();
    let body: unknown = null;
    const post = request.postData();
    if (post) {
      try {
        body = JSON.parse(post);
      } catch {
        body = null;
      }
    }
    const result = handleRequest(store, request.method(), request.url(), body);
    await route.fulfill({
      status: result.status,
      contentType: "application/json",
      headers: { "X-Correlation-ID": "e2e-mock-1" },
      body: JSON.stringify(result.body),
    });
  });
  return store;
}
