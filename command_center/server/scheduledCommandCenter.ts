import type { Request, Response } from "express";
import { and, eq } from "drizzle-orm";
import { z } from "zod";
import { activityEvents, automationConfigs, industries, notifications, productionBatches } from "../drizzle/schema";
import { getDb } from "./db";
import { sdk } from "./_core/sdk";

const scheduledPayload = z.object({
  batchCode: z.string().min(4).max(100),
  industryCode: z.string().min(2).max(64),
  scheduledAt: z.string().datetime(),
  completedAt: z.string().datetime().optional(),
  status: z.enum(["Queued", "Researching", "Generating", "Quality review", "Publishing", "Complete", "Failed"]),
  proposalCount: z.number().int().min(0).max(1000).default(0),
  documentCount: z.number().int().min(0).max(5000).default(0),
  videoConceptCount: z.number().int().min(0).max(1000).default(0),
  driveSyncStatus: z.enum(["Pending", "Synced", "Failed", "Not configured"]),
  githubSyncStatus: z.enum(["Pending", "Synced", "Failed", "Not configured"]),
  syncRetryStatus: z.enum(["Not needed", "Retry scheduled", "Retrying", "Exhausted"]).default("Not needed"),
  driveSyncedAt: z.string().datetime().optional(),
  githubSyncedAt: z.string().datetime().optional(),
  lastRetryAt: z.string().datetime().optional(),
  driveFolderUrl: z.string().url().max(1024).optional(),
  githubUrl: z.string().url().max(1024).optional(),
  githubCommit: z.string().max(128).optional(),
  errorSummary: z.string().max(5000).optional(),
});

export async function commandCenterSyncHandler(req: Request, res: Response) {
  try {
    const user = await sdk.authenticateRequest(req);
    if (!user.isCron || !user.taskUid) return res.status(403).json({ error: "cron-only" });
    const body = scheduledPayload.safeParse(req.body);
    if (!body.success) return res.status(400).json({ error: "invalid-payload", detail: body.error.flatten() });
    const db = await getDb();
    if (!db) return res.status(503).json({ error: "database-unavailable" });
    const config = (await db.select().from(automationConfigs).where(eq(automationConfigs.scheduleCronTaskUid, user.taskUid)).limit(1))[0];
    if (!config || !config.isEnabled) return res.json({ ok: true, skipped: "orphan-or-disabled" });
    const industry = (await db.select().from(industries).where(eq(industries.code, body.data.industryCode)).limit(1))[0];
    if (!industry) return res.status(422).json({ error: "unknown-industry-code" });
    const existing = (await db.select().from(productionBatches).where(eq(productionBatches.batchCode, body.data.batchCode)).limit(1))[0];
    const isFailure = body.data.status === "Failed" || body.data.driveSyncStatus === "Failed" || body.data.githubSyncStatus === "Failed";
    const values = {
      industryId: industry.id,
      scheduledAt: new Date(body.data.scheduledAt),
      completedAt: body.data.completedAt ? new Date(body.data.completedAt) : null,
      status: body.data.status,
      proposalCount: body.data.proposalCount,
      documentCount: body.data.documentCount,
      videoConceptCount: body.data.videoConceptCount,
      driveSyncStatus: body.data.driveSyncStatus,
      githubSyncStatus: body.data.githubSyncStatus,
      syncRetryStatus: body.data.syncRetryStatus,
      driveSyncedAt: body.data.driveSyncedAt ? new Date(body.data.driveSyncedAt) : body.data.driveSyncStatus === "Synced" ? new Date() : null,
      githubSyncedAt: body.data.githubSyncedAt ? new Date(body.data.githubSyncedAt) : body.data.githubSyncStatus === "Synced" ? new Date() : null,
      lastRetryAt: body.data.lastRetryAt ? new Date(body.data.lastRetryAt) : body.data.syncRetryStatus !== "Not needed" ? new Date() : null,
      syncFailedAt: isFailure ? new Date() : null,
      driveFolderUrl: body.data.driveFolderUrl ?? null,
      githubUrl: body.data.githubUrl ?? null,
      githubCommit: body.data.githubCommit ?? null,
      errorSummary: body.data.errorSummary ?? null,
    } as const;
    if (existing) await db.update(productionBatches).set(values).where(eq(productionBatches.id, existing.id));
    else await db.insert(productionBatches).values({ batchCode: body.data.batchCode, ...values });
    await db.update(automationConfigs).set({ lastRunAt: new Date(), lastStatus: body.data.status, lastError: body.data.errorSummary ?? null }).where(eq(automationConfigs.id, config.id));
    if (!existing || existing.status !== body.data.status) {
      await db.insert(activityEvents).values({ entityType: "batch", entityId: existing?.id, title: `Production batch ${body.data.status}`, detail: `${body.data.batchCode}: ${body.data.proposalCount} proposals, ${body.data.documentCount} documents, Drive ${body.data.driveSyncStatus}, GitHub ${body.data.githubSyncStatus}, retry ${body.data.syncRetryStatus}.`, priority: isFailure ? "High" : body.data.status === "Complete" ? "Normal" : "Low", actor: "ZYNTH Two-Hour Cycle" });
    }
    if (isFailure) await db.insert(notifications).values({ type: "sync_or_batch_failure", title: `Production attention: ${body.data.batchCode}`, detail: body.data.errorSummary || `Drive is ${body.data.driveSyncStatus}; GitHub is ${body.data.githubSyncStatus}.`, priority: "High", isRead: 0 });
    else if (body.data.status === "Complete" && (!existing || existing.status !== "Complete")) await db.insert(notifications).values({ type: "batch_published", title: `New proposal batch published: ${industry.name}`, detail: `${body.data.proposalCount} proposals and ${body.data.documentCount} documents reported complete with Drive and GitHub status recorded.`, priority: "Normal", isRead: 0 });
    return res.json({ ok: true, batchCode: body.data.batchCode });
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    return res.status(500).json({ error: "command-center-sync-failed", detail, timestamp: new Date().toISOString() });
  }
}
