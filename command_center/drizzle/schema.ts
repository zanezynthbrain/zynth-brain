import { index, int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

export const industryTierEnum = mysqlEnum("industry_tier", ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]);
export const proposalStageEnum = mysqlEnum("proposal_stage", ["Draft", "Review", "Pitched", "Negotiating", "Won", "Lost", "On Hold"]);
export const productionStageEnum = mysqlEnum("production_stage", ["Storyboard", "Pre-production", "Production", "Post-production", "Delivery"]);
export const driveSyncStatusEnum = mysqlEnum("drive_sync_status", ["Pending", "Synced", "Failed", "Not configured"]);
export const githubSyncStatusEnum = mysqlEnum("github_sync_status", ["Pending", "Synced", "Failed", "Not configured"]);
export const syncRetryStatusEnum = mysqlEnum("sync_retry_status", ["Not needed", "Retry scheduled", "Retrying", "Exhausted"]);
export const videoApprovalStatusEnum = mysqlEnum("video_approval_status", ["Not started", "Client review", "Approved", "Changes requested"]);
export const batchStatusEnum = mysqlEnum("batch_status", ["Queued", "Researching", "Generating", "Quality review", "Publishing", "Complete", "Failed"]);
export const languageStatusEnum = mysqlEnum("language_status", ["English", "English–Myanmar hybrid", "Both"]);
export const priorityEnum = mysqlEnum("priority", ["Critical", "High", "Normal", "Low"]);

export const industries = mysqlTable("industries", {
  id: int("id").autoincrement().primaryKey(),
  code: varchar("code", { length: 64 }).notNull().unique(),
  name: varchar("name", { length: 160 }).notNull(),
  nameMyanmar: varchar("name_myanmar", { length: 255 }),
  tier: industryTierEnum.notNull(),
  marketPotentialScore: int("market_potential_score").notNull(),
  pitchReadinessScore: int("pitch_readiness_score").notNull(),
  digitalReadinessScore: int("digital_readiness_score").notNull(),
  operationalRiskScore: int("operational_risk_score").notNull(),
  opportunitySummary: text("opportunity_summary").notNull(),
  campaignFit: text("campaign_fit").notNull(),
  sourceUrl: varchar("source_url", { length: 1024 }).notNull(),
  sourceNote: text("source_note").notNull(),
  lastReviewedAt: timestamp("last_reviewed_at").defaultNow().notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, table => [index("industries_tier_idx").on(table.tier)]);

export const businessTargets = mysqlTable("business_targets", {
  id: int("id").autoincrement().primaryKey(),
  industryId: int("industry_id").notNull(),
  name: varchar("name", { length: 255 }).notNull(),
  nameMyanmar: varchar("name_myanmar", { length: 255 }),
  targetClass: varchar("target_class", { length: 120 }).notNull(),
  opportunityScore: int("opportunity_score").notNull(),
  pitchAngle: text("pitch_angle").notNull(),
  sourceUrl: varchar("source_url", { length: 1024 }).notNull(),
  verificationStatus: varchar("verification_status", { length: 80 }).notNull(),
  nextAction: varchar("next_action", { length: 255 }).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, table => [index("business_targets_industry_idx").on(table.industryId)]);

export const proposals = mysqlTable("proposals", {
  id: int("id").autoincrement().primaryKey(),
  batchId: int("batch_id"),
  industryId: int("industry_id").notNull(),
  proposalCode: varchar("proposal_code", { length: 100 }).notNull().unique(),
  title: varchar("title", { length: 255 }).notNull(),
  titleMyanmar: varchar("title_myanmar", { length: 255 }),
  campaignType: varchar("campaign_type", { length: 160 }).notNull(),
  seasonalWindow: varchar("seasonal_window", { length: 255 }),
  languageStatus: languageStatusEnum.notNull().default("Both"),
  stage: proposalStageEnum.notNull().default("Draft"),
  budgetLeanMmk: int("budget_lean_mmk"),
  budgetRecommendedMmk: int("budget_recommended_mmk"),
  budgetFlagshipMmk: int("budget_flagship_mmk"),
  roiConservative: varchar("roi_conservative", { length: 64 }),
  roiBase: varchar("roi_base", { length: 64 }),
  roiUpside: varchar("roi_upside", { length: 64 }),
  seasonalRationale: text("seasonal_rationale").notNull(),
  conceptSummary: text("concept_summary").notNull(),
  documentEnglishUrl: varchar("document_english_url", { length: 1024 }),
  documentHybridUrl: varchar("document_hybrid_url", { length: 1024 }),
  owner: varchar("owner", { length: 160 }).notNull().default("ZYNTH Strategy"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, table => [index("proposals_industry_stage_idx").on(table.industryId, table.stage), index("proposals_batch_idx").on(table.batchId)]);

export const videoProjects = mysqlTable("video_projects", {
  id: int("id").autoincrement().primaryKey(),
  industryId: int("industry_id").notNull(),
  proposalId: int("proposal_id"),
  projectCode: varchar("project_code", { length: 100 }).notNull().unique(),
  title: varchar("title", { length: 255 }).notNull(),
  titleMyanmar: varchar("title_myanmar", { length: 255 }),
  tagline: varchar("tagline", { length: 255 }).notNull(),
  clientName: varchar("client_name", { length: 255 }).notNull(),
  productionHouse: varchar("production_house", { length: 255 }).notNull(),
  talentPlan: text("talent_plan").notNull(),
  stage: productionStageEnum.notNull().default("Storyboard"),
  timelineStart: timestamp("timeline_start"),
  timelineDue: timestamp("timeline_due"),
  storyboardStatus: varchar("storyboard_status", { length: 120 }).notNull(),
  approvalStatus: videoApprovalStatusEnum.notNull().default("Not started"),
  approvalNotes: text("approval_notes"),
  storyline: text("storyline").notNull(),
  budgetMmk: int("budget_mmk"),
  deliverables: text("deliverables").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, table => [index("video_projects_industry_stage_idx").on(table.industryId, table.stage)]);

export const productionBatches = mysqlTable("production_batches", {
  id: int("id").autoincrement().primaryKey(),
  batchCode: varchar("batch_code", { length: 100 }).notNull().unique(),
  industryId: int("industry_id").notNull(),
  scheduledAt: timestamp("scheduled_at").notNull(),
  completedAt: timestamp("completed_at"),
  status: batchStatusEnum.notNull().default("Queued"),
  proposalCount: int("proposal_count").notNull().default(0),
  documentCount: int("document_count").notNull().default(0),
  videoConceptCount: int("video_concept_count").notNull().default(0),
  driveSyncStatus: driveSyncStatusEnum.notNull().default("Pending"),
  githubSyncStatus: githubSyncStatusEnum.notNull().default("Pending"),
  syncRetryStatus: syncRetryStatusEnum.notNull().default("Not needed"),
  driveSyncedAt: timestamp("drive_synced_at"),
  githubSyncedAt: timestamp("github_synced_at"),
  lastRetryAt: timestamp("last_retry_at"),
  syncFailedAt: timestamp("sync_failed_at"),
  driveFolderUrl: varchar("drive_folder_url", { length: 1024 }),
  githubUrl: varchar("github_url", { length: 1024 }),
  githubCommit: varchar("github_commit", { length: 128 }),
  errorSummary: text("error_summary"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, table => [index("production_batches_industry_status_idx").on(table.industryId, table.status)]);

export const activityEvents = mysqlTable("activity_events", {
  id: int("id").autoincrement().primaryKey(),
  entityType: varchar("entity_type", { length: 64 }).notNull(),
  entityId: int("entity_id"),
  title: varchar("title", { length: 255 }).notNull(),
  detail: text("detail").notNull(),
  priority: priorityEnum.notNull().default("Normal"),
  actor: varchar("actor", { length: 160 }).notNull().default("ZYNTH System"),
  occurredAt: timestamp("occurred_at").defaultNow().notNull(),
}, table => [index("activity_events_occurred_idx").on(table.occurredAt)]);

export const notifications = mysqlTable("notifications", {
  id: int("id").autoincrement().primaryKey(),
  type: varchar("type", { length: 100 }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  detail: text("detail").notNull(),
  priority: priorityEnum.notNull().default("Normal"),
  isRead: int("is_read").notNull().default(0),
  dueAt: timestamp("due_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
}, table => [index("notifications_read_priority_idx").on(table.isRead, table.priority)]);

export const promptVersions = mysqlTable("prompt_versions", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  version: varchar("version", { length: 32 }).notNull(),
  content: text("content").notNull(),
  changeNote: text("change_note").notNull(),
  isActive: int("is_active").notNull().default(1),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, table => [index("prompt_versions_active_idx").on(table.isActive)]);

export const automationConfigs = mysqlTable("automation_configs", {
  id: int("id").autoincrement().primaryKey(),
  code: varchar("code", { length: 100 }).notNull().unique(),
  scheduleCronTaskUid: varchar("schedule_cron_task_uid", { length: 65 }),
  cronExpression: varchar("cron_expression", { length: 120 }).notNull(),
  isEnabled: int("is_enabled").notNull().default(1),
  lastRunAt: timestamp("last_run_at"),
  lastStatus: batchStatusEnum.notNull().default("Queued"),
  lastError: text("last_error"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, table => [index("automation_configs_task_uid_idx").on(table.scheduleCronTaskUid)]);

export type Industry = typeof industries.$inferSelect;
export type BusinessTarget = typeof businessTargets.$inferSelect;
export type Proposal = typeof proposals.$inferSelect;
export type VideoProject = typeof videoProjects.$inferSelect;
export type ProductionBatch = typeof productionBatches.$inferSelect;
export type ActivityEvent = typeof activityEvents.$inferSelect;
export type Notification = typeof notifications.$inferSelect;
export type PromptVersion = typeof promptVersions.$inferSelect;
export type AutomationConfig = typeof automationConfigs.$inferSelect;
