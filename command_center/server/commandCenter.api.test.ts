import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

function createContext(): TrpcContext {
  return {
    user: {
      id: 1,
      openId: "zynth-command-test",
      email: "test@zynth.local",
      name: "ZYNTH Test",
      loginMethod: "manus",
      role: "admin",
      createdAt: new Date(),
      updatedAt: new Date(),
      lastSignedIn: new Date(),
    },
    req: { protocol: "https", headers: {} } as TrpcContext["req"],
    res: { clearCookie: () => undefined } as TrpcContext["res"],
  };
}

describe("commandCenter.dashboard", () => {
  it("returns the seeded industry, proposal and prompt records", async () => {
    const caller = appRouter.createCaller(createContext());
    const result = await caller.commandCenter.dashboard();

    expect(result.industries.length).toBeGreaterThanOrEqual(20);
    expect(result.proposals).toHaveLength(10);
    expect(result.prompts[0]?.name).toContain("ZYNTH");
    expect(result.metrics.proposalCount).toBe(10);
    expect(result.batches[0]?.batch.driveFolderUrl).toContain("drive.google.com");
    expect(result.batches[0]?.batch.githubUrl).toContain("github.com");
    expect(result.batches[0]?.batch.syncRetryStatus).toBe("Not needed");
    expect(result.batches[0]?.batch.driveSyncedAt).toBeTruthy();
    expect(result.batches[0]?.batch.githubSyncedAt).toBeTruthy();
  }, 30_000);
});
