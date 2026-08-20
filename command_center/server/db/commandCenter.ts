import { and, desc, eq, inArray, sql } from "drizzle-orm";
import { activityEvents, businessTargets, industries, notifications, productionBatches, promptVersions, proposals, videoProjects } from "../../drizzle/schema";
import { getDb } from "../db";
import { ensureCommandCenterSeed } from "../commandCenterSeed";

export type ProposalFilters = { industryId?: number; stage?: "Draft" | "Review" | "Pitched" | "Negotiating" | "Won" | "Lost" | "On Hold"; languageStatus?: "English" | "English–Myanmar hybrid" | "Both"; campaignType?: string; seasonalWindow?: string; owner?: string };

async function database() { await ensureCommandCenterSeed(); return getDb(); }

export async function getDashboardData() {
  const db = await database(); if (!db) throw new Error("Database unavailable");
  const [industryRows, proposalRows, videoRows, batchRows, activityRows, notificationRows, promptRows, targetRows] = await Promise.all([
    db.select().from(industries).orderBy(desc(industries.pitchReadinessScore)),
    db.select({ proposal: proposals, industry: industries }).from(proposals).innerJoin(industries, eq(proposals.industryId, industries.id)).orderBy(desc(proposals.updatedAt)),
    db.select({ project: videoProjects, industry: industries }).from(videoProjects).innerJoin(industries, eq(videoProjects.industryId, industries.id)).orderBy(desc(videoProjects.updatedAt)),
    db.select({ batch: productionBatches, industry: industries }).from(productionBatches).innerJoin(industries, eq(productionBatches.industryId, industries.id)).orderBy(desc(productionBatches.scheduledAt)),
    db.select().from(activityEvents).orderBy(desc(activityEvents.occurredAt)).limit(12),
    db.select().from(notifications).orderBy(desc(notifications.createdAt)).limit(12),
    db.select().from(promptVersions).orderBy(desc(promptVersions.updatedAt)),
    db.select({ target: businessTargets, industry: industries }).from(businessTargets).innerJoin(industries, eq(businessTargets.industryId, industries.id)).orderBy(desc(businessTargets.opportunityScore)).limit(24),
  ]);
  const budgetTotal = proposalRows.reduce((sum, row) => sum + (row.proposal.budgetRecommendedMmk ?? 0), 0);
  const stageCounts = Object.fromEntries(["Draft", "Review", "Pitched", "Negotiating", "Won", "Lost", "On Hold"].map(stage => [stage, proposalRows.filter(row => row.proposal.stage === stage).length]));
  const syncFailures = batchRows.filter(row => row.batch.driveSyncStatus === "Failed" || row.batch.githubSyncStatus === "Failed").length;
  return { industries: industryRows, proposals: proposalRows, videoProjects: videoRows, batches: batchRows, activities: activityRows, notifications: notificationRows, prompts: promptRows, targets: targetRows, metrics: { industryCount: industryRows.length, proposalCount: proposalRows.length, videoProjectCount: videoRows.length, budgetTotal, stageCounts, unreadNotifications: notificationRows.filter(item => !item.isRead).length, syncFailures, completeBatchCount: batchRows.filter(row => row.batch.status === "Complete").length } };
}

export async function listProposals(filters: ProposalFilters) {
  const db = await database(); if (!db) throw new Error("Database unavailable");
  const conditions = [];
  if (filters.industryId) conditions.push(eq(proposals.industryId, filters.industryId));
  if (filters.stage) conditions.push(eq(proposals.stage, filters.stage));
  if (filters.languageStatus) conditions.push(eq(proposals.languageStatus, filters.languageStatus));
  if (filters.campaignType) conditions.push(eq(proposals.campaignType, filters.campaignType));
  if (filters.seasonalWindow) conditions.push(eq(proposals.seasonalWindow, filters.seasonalWindow));
  if (filters.owner) conditions.push(eq(proposals.owner, filters.owner));
  return db.select({ proposal: proposals, industry: industries }).from(proposals).innerJoin(industries, eq(proposals.industryId, industries.id)).where(conditions.length ? and(...conditions) : undefined).orderBy(desc(proposals.updatedAt));
}

export async function updateProposalStage(id: number, stage: ProposalFilters["stage"], actor: string) {
  const db = await database(); if (!db || !stage) throw new Error("Database unavailable");
  await db.update(proposals).set({ stage }).where(eq(proposals.id, id));
  await db.insert(activityEvents).values({ entityType: "proposal", entityId: id, title: `Proposal moved to ${stage}`, detail: `CEO dashboard stage update recorded as ${stage}.`, priority: stage === "Won" || stage === "Lost" ? "High" : "Normal", actor });
  if (["Won", "Lost", "Negotiating"].includes(stage)) await db.insert(notifications).values({ type: "proposal_stage_changed", title: `Proposal stage changed to ${stage}`, detail: `A proposal lifecycle update requires CEO visibility.`, priority: stage === "Negotiating" ? "High" : "Normal", isRead: 0 });
}

export async function markNotificationRead(id: number) { const db = await database(); if (!db) throw new Error("Database unavailable"); await db.update(notifications).set({ isRead: 1 }).where(eq(notifications.id, id)); }

export async function getPrompt(id: number) { const db = await database(); if (!db) throw new Error("Database unavailable"); return (await db.select().from(promptVersions).where(eq(promptVersions.id, id)).limit(1))[0] ?? null; }

export async function createVideoProject(input: { industryId: number; title: string; titleMyanmar?: string; tagline: string; clientName: string; productionHouse: string; talentPlan: string; storyline: string; deliverables: string; storyboardStatus?: string; timelineStart?: Date; timelineDue?: Date; approvalStatus?: "Not started" | "Client review" | "Approved" | "Changes requested"; approvalNotes?: string; budgetMmk?: number; }) {
  const db = await database(); if (!db) throw new Error("Database unavailable");
  const projectCode = `ZYNTH-VID-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${Math.random().toString(36).slice(2, 6).toUpperCase()}`;
  const result = await db.insert(videoProjects).values({ ...input, projectCode, stage: "Storyboard", storyboardStatus: input.storyboardStatus ?? "Brief received · storyboard pending", timelineStart: input.timelineStart ?? new Date(), timelineDue: input.timelineDue ?? null, approvalStatus: input.approvalStatus ?? "Not started", approvalNotes: input.approvalNotes ?? null, budgetMmk: input.budgetMmk ?? null });
  await db.insert(activityEvents).values({ entityType: "video_project", entityId: Number((result as { insertId?: number }).insertId ?? 0), title: "Commercial video project created", detail: `${input.title} entered the storyboard stage for ${input.clientName}.`, priority: "Normal", actor: "ZYNTH CEO Dashboard" });
  return { projectCode };
}

export async function updateVideoStage(id: number, stage: "Storyboard" | "Pre-production" | "Production" | "Post-production" | "Delivery", actor: string) {
  const db = await database(); if (!db) throw new Error("Database unavailable");
  await db.update(videoProjects).set({ stage }).where(eq(videoProjects.id, id));
  await db.insert(activityEvents).values({ entityType: "video_project", entityId: id, title: `Commercial project moved to ${stage}`, detail: `Production lifecycle update recorded as ${stage}.`, priority: stage === "Delivery" ? "High" : "Normal", actor });
}

export async function updateVideoApproval(id: number, approvalStatus: "Not started" | "Client review" | "Approved" | "Changes requested", approvalNotes: string | undefined, actor: string) {
  const db = await database(); if (!db) throw new Error("Database unavailable");
  await db.update(videoProjects).set({ approvalStatus, approvalNotes: approvalNotes ?? null }).where(eq(videoProjects.id, id));
  await db.insert(activityEvents).values({ entityType: "video_project", entityId: id, title: `Commercial approval: ${approvalStatus}`, detail: approvalNotes || "Approval status updated from the CEO production interface.", priority: approvalStatus === "Changes requested" ? "High" : "Normal", actor });
  if (approvalStatus === "Changes requested") await db.insert(notifications).values({ type: "video_approval", title: "Commercial changes requested", detail: approvalNotes || "A commercial project requires revision before approval.", priority: "High", isRead: 0 });
}

export async function updateVideoDetails(id: number, storyboardStatus: string, timelineStart: Date | undefined, timelineDue: Date | undefined, actor: string) {
  const db = await database(); if (!db) throw new Error("Database unavailable");
  await db.update(videoProjects).set({ storyboardStatus, timelineStart: timelineStart ?? null, timelineDue: timelineDue ?? null }).where(eq(videoProjects.id, id));
  await db.insert(activityEvents).values({ entityType: "video_project", entityId: id, title: "Commercial storyboard or timeline updated", detail: `Storyboard state: ${storyboardStatus}.`, priority: "Normal", actor });
}
