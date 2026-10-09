import { describe, expect, it } from "vitest";
import { PROPOSAL_EDITOR_FLAG, proposalEditorEnabled } from "@/lib/architect/proposal-editor-flag";

/**
 * D-01 (plan §7): the set-aside proposal editor is gated by the non-public,
 * server-read INTERNAL_PROPOSAL_EDITOR_ENABLED. Fail safe: absent, empty or any
 * unknown value keeps it OFF; only an explicit true token turns it on.
 */
describe("proposalEditorEnabled — default-off, fail-safe server flag", () => {
  it("reads the canonical, non-public variable name", () => {
    expect(PROPOSAL_EDITOR_FLAG).toBe("INTERNAL_PROPOSAL_EDITOR_ENABLED");
    expect(PROPOSAL_EDITOR_FLAG.startsWith("NEXT_PUBLIC_")).toBe(false);
  });

  it("is OFF when the variable is absent", () => {
    expect(proposalEditorEnabled({})).toBe(false);
  });

  it.each(["", " ", "0", "false", "off", "no", "enabled", "2", "tru"])("is OFF for %j", (raw) => {
    expect(proposalEditorEnabled({ [PROPOSAL_EDITOR_FLAG]: raw })).toBe(false);
  });

  it.each(["1", "true", "TRUE", " yes ", "on", "On"])("is ON only for the explicit true token %j", (raw) => {
    expect(proposalEditorEnabled({ [PROPOSAL_EDITOR_FLAG]: raw })).toBe(true);
  });

  it("ignores a different variable of a similar name", () => {
    expect(proposalEditorEnabled({ INTERNAL_RULE_EVAL_ENABLED: "1", NEXT_PUBLIC_INTERNAL_PROPOSAL_EDITOR_ENABLED: "1" })).toBe(false);
  });
});
