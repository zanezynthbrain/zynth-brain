import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import SyncAuditPanel from "./SyncAuditPanel";

describe("SyncAuditPanel UI", () => {
  it("renders both publication destinations, retry state, destination timestamps, and failure detail", () => {
    const html = renderToStaticMarkup(createElement(SyncAuditPanel, {
      batches: [{
        industry: { name: "Food & Beverage / FMCG" },
        batch: {
          id: 1,
          batchCode: "ZYNTH-FNB-001",
          status: "Failed",
          driveSyncStatus: "Synced",
          githubSyncStatus: "Failed",
          syncRetryStatus: "Retry scheduled",
          driveSyncedAt: new Date("2026-08-20T10:00:00.000Z"),
          githubSyncedAt: null,
          lastRetryAt: new Date("2026-08-20T10:02:00.000Z"),
          syncFailedAt: new Date("2026-08-20T10:01:00.000Z"),
          completedAt: null,
          errorSummary: "GitHub push rejected; retry scheduled.",
          driveFolderUrl: "https://drive.google.com/drive/folders/example",
          githubUrl: "https://github.com/zanezynthbrain/zynth-brain/tree/main/command_center",
          githubCommit: "734229d",
        },
      }],
    }));

    expect(html).toContain("https://drive.google.com/drive/folders/example");
    expect(html).toContain("https://github.com/zanezynthbrain/zynth-brain/tree/main/command_center");
    expect(html).toContain("Retry scheduled");
    expect(html).toContain("GitHub push rejected; retry scheduled.");
    expect(html).toContain("Failure:");
    expect(html).toContain("Drive:");
    expect(html).toContain("GitHub:");
  });
});
