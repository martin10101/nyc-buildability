import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { selectedOption } from "../study-entry";
import { addOption, renameOption, selectOption } from "../study-operations";
import { createStudyStore, defaultStudyStore, type StudyStore } from "../study-store";
import { StudyStoreProvider, useStudy, useStudyStore } from "../use-study";
import { SYNTHETIC_BBL, T1, T2, expectOk, newStudyResult, optionInputs } from "./study-test-data";

afterEach(cleanup);

/** A read-only surface, standing in for the overview or a dashboard tool. */
function StudySummary({ testId }: { testId: string }) {
  const entry = useStudy(SYNTHETIC_BBL);
  const option = entry ? selectedOption(entry) : null;
  return (
    <p data-testid={testId}>
      {entry && option ? `${option.name} · revision ${entry.study.revision.number}` : "No study"}
    </p>
  );
}

/** A surface that edits through the store. */
function RenameButton() {
  const store = useStudyStore();
  return (
    <button
      type="button"
      onClick={() => store.update(SYNTHETIC_BBL, (entry) => renameOption(entry, "option-a", "Option A (edited)", T1))}
    >
      Rename
    </button>
  );
}

function twoSurfaces(store: StudyStore) {
  return render(
    <StudyStoreProvider store={store}>
      <StudySummary testId="overview" />
      <StudySummary testId="dashboard" />
      <RenameButton />
    </StudyStoreProvider>,
  );
}

describe("one study store for every surface", () => {
  it("two components on the same page read the same study and change together", () => {
    const store = createStudyStore();
    twoSurfaces(store);
    expect(screen.getByTestId("overview")).toHaveTextContent("No study");
    expect(screen.getByTestId("dashboard")).toHaveTextContent("No study");

    act(() => {
      store.ensure(SYNTHETIC_BBL, newStudyResult);
    });
    expect(screen.getByTestId("overview")).toHaveTextContent("Option A · revision 1");
    expect(screen.getByTestId("dashboard")).toHaveTextContent("Option A · revision 1");

    act(() => {
      expectOk(store.update(SYNTHETIC_BBL, (entry) => addOption(entry, { name: "Option B", inputs: optionInputs() }, T1)));
      expectOk(store.update(SYNTHETIC_BBL, (entry) => selectOption(entry, "option-2", T2)));
    });
    expect(screen.getByTestId("overview")).toHaveTextContent("Option B · revision 3");
    expect(screen.getByTestId("dashboard")).toHaveTextContent("Option B · revision 3");
  });

  it("an edit made on one surface shows on the other", () => {
    const store = createStudyStore();
    expectOk(store.ensure(SYNTHETIC_BBL, newStudyResult));
    twoSurfaces(store);
    fireEvent.click(screen.getByRole("button", { name: "Rename" }));
    expect(screen.getByTestId("overview")).toHaveTextContent("Option A (edited) · revision 2");
    expect(screen.getByTestId("dashboard")).toHaveTextContent("Option A (edited) · revision 2");
  });

  it("without a provider, surfaces share the page's default store", () => {
    const store = defaultStudyStore();
    render(
      <>
        <StudySummary testId="overview" />
        <StudySummary testId="dashboard" />
      </>,
    );
    act(() => {
      store.ensure(SYNTHETIC_BBL, newStudyResult);
    });
    expect(screen.getByTestId("overview")).toHaveTextContent("Option A · revision 1");
    expect(screen.getByTestId("dashboard")).toHaveTextContent("Option A · revision 1");
    act(() => store.remove(SYNTHETIC_BBL));
    expect(screen.getByTestId("overview")).toHaveTextContent("No study");
  });
});

describe("study store", () => {
  it("creates a property's study once: a second surface gets the first one's study", () => {
    const store = createStudyStore();
    const first = expectOk(store.ensure(SYNTHETIC_BBL, newStudyResult));
    const create = vi.fn(newStudyResult);
    const second = expectOk(store.ensure(SYNTHETIC_BBL, create));
    expect(second).toBe(first);
    expect(create).not.toHaveBeenCalled();
  });

  it("a failed operation changes nothing and notifies nobody", () => {
    const store = createStudyStore();
    const entry = expectOk(store.ensure(SYNTHETIC_BBL, newStudyResult));
    const listener = vi.fn();
    const unsubscribe = store.subscribe(SYNTHETIC_BBL, listener);
    const result = store.update(SYNTHETIC_BBL, (current) => renameOption(current, "option-a", "", T1));
    expect(result).toMatchObject({ ok: false, code: "invalid_document" });
    expect(store.get(SYNTHETIC_BBL)).toBe(entry);
    expect(listener).not.toHaveBeenCalled();
    store.update(SYNTHETIC_BBL, (current) => renameOption(current, "option-a", "Renamed", T1));
    expect(listener).toHaveBeenCalledTimes(1);
    unsubscribe();
    store.update(SYNTHETIC_BBL, (current) => renameOption(current, "option-a", "Renamed again", T2));
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it("keys studies by property and refuses a study for another property", () => {
    const store = createStudyStore();
    expect(store.update(SYNTHETIC_BBL, (entry) => ({ ok: true, entry }))).toMatchObject({ ok: false, code: "no_study" });
    expect(store.ensure(SYNTHETIC_BBL, () => newStudyResult("5999999998"))).toMatchObject({
      ok: false,
      code: "wrong_property",
    });
    expect(store.get(SYNTHETIC_BBL)).toBeNull();
    expectOk(store.replace(newStudyResult("5999999998")));
    expect(store.get("5999999998")?.study.property.bbl).toBe("5999999998");
    expect(store.get(SYNTHETIC_BBL)).toBeNull();
  });
});
