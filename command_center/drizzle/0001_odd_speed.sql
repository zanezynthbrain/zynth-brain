CREATE TABLE `activity_events` (
	`id` int AUTO_INCREMENT NOT NULL,
	`entity_type` varchar(64) NOT NULL,
	`entity_id` int,
	`title` varchar(255) NOT NULL,
	`detail` text NOT NULL,
	`priority` enum('Critical','High','Normal','Low') NOT NULL DEFAULT 'Normal',
	`actor` varchar(160) NOT NULL DEFAULT 'ZYNTH System',
	`occurred_at` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `activity_events_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `business_targets` (
	`id` int AUTO_INCREMENT NOT NULL,
	`industry_id` int NOT NULL,
	`name` varchar(255) NOT NULL,
	`name_myanmar` varchar(255),
	`target_class` varchar(120) NOT NULL,
	`opportunity_score` int NOT NULL,
	`pitch_angle` text NOT NULL,
	`source_url` varchar(1024) NOT NULL,
	`verification_status` varchar(80) NOT NULL,
	`next_action` varchar(255) NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `business_targets_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `industries` (
	`id` int AUTO_INCREMENT NOT NULL,
	`code` varchar(64) NOT NULL,
	`name` varchar(160) NOT NULL,
	`name_myanmar` varchar(255),
	`industry_tier` enum('Tier 1','Tier 2','Tier 3','Tier 4') NOT NULL,
	`market_potential_score` int NOT NULL,
	`pitch_readiness_score` int NOT NULL,
	`digital_readiness_score` int NOT NULL,
	`operational_risk_score` int NOT NULL,
	`opportunity_summary` text NOT NULL,
	`campaign_fit` text NOT NULL,
	`source_url` varchar(1024) NOT NULL,
	`source_note` text NOT NULL,
	`last_reviewed_at` timestamp NOT NULL DEFAULT (now()),
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `industries_id` PRIMARY KEY(`id`),
	CONSTRAINT `industries_code_unique` UNIQUE(`code`)
);
--> statement-breakpoint
CREATE TABLE `notifications` (
	`id` int AUTO_INCREMENT NOT NULL,
	`type` varchar(100) NOT NULL,
	`title` varchar(255) NOT NULL,
	`detail` text NOT NULL,
	`priority` enum('Critical','High','Normal','Low') NOT NULL DEFAULT 'Normal',
	`is_read` int NOT NULL DEFAULT 0,
	`due_at` timestamp,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `notifications_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `production_batches` (
	`id` int AUTO_INCREMENT NOT NULL,
	`batch_code` varchar(100) NOT NULL,
	`industry_id` int NOT NULL,
	`scheduled_at` timestamp NOT NULL,
	`completed_at` timestamp,
	`batch_status` enum('Queued','Researching','Generating','Quality review','Publishing','Complete','Failed') NOT NULL DEFAULT 'Queued',
	`proposal_count` int NOT NULL DEFAULT 0,
	`document_count` int NOT NULL DEFAULT 0,
	`video_concept_count` int NOT NULL DEFAULT 0,
	`drive_sync_status` enum('Pending','Synced','Failed','Not configured') NOT NULL DEFAULT 'Pending',
	`github_sync_status` enum('Pending','Synced','Failed','Not configured') NOT NULL DEFAULT 'Pending',
	`drive_folder_url` varchar(1024),
	`github_commit` varchar(128),
	`error_summary` text,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `production_batches_id` PRIMARY KEY(`id`),
	CONSTRAINT `production_batches_batch_code_unique` UNIQUE(`batch_code`)
);
--> statement-breakpoint
CREATE TABLE `prompt_versions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(255) NOT NULL,
	`version` varchar(32) NOT NULL,
	`content` text NOT NULL,
	`change_note` text NOT NULL,
	`is_active` int NOT NULL DEFAULT 1,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `prompt_versions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `proposals` (
	`id` int AUTO_INCREMENT NOT NULL,
	`batch_id` int,
	`industry_id` int NOT NULL,
	`proposal_code` varchar(100) NOT NULL,
	`title` varchar(255) NOT NULL,
	`title_myanmar` varchar(255),
	`campaign_type` varchar(160) NOT NULL,
	`seasonal_window` varchar(255),
	`language_status` enum('English','English–Myanmar hybrid','Both') NOT NULL DEFAULT 'Both',
	`proposal_stage` enum('Draft','Review','Pitched','Negotiating','Won','Lost','On Hold') NOT NULL DEFAULT 'Draft',
	`budget_lean_mmk` int,
	`budget_recommended_mmk` int,
	`budget_flagship_mmk` int,
	`roi_conservative` varchar(64),
	`roi_base` varchar(64),
	`roi_upside` varchar(64),
	`seasonal_rationale` text NOT NULL,
	`concept_summary` text NOT NULL,
	`document_english_url` varchar(1024),
	`document_hybrid_url` varchar(1024),
	`owner` varchar(160) NOT NULL DEFAULT 'ZYNTH Strategy',
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `proposals_id` PRIMARY KEY(`id`),
	CONSTRAINT `proposals_proposal_code_unique` UNIQUE(`proposal_code`)
);
--> statement-breakpoint
CREATE TABLE `video_projects` (
	`id` int AUTO_INCREMENT NOT NULL,
	`industry_id` int NOT NULL,
	`proposal_id` int,
	`project_code` varchar(100) NOT NULL,
	`title` varchar(255) NOT NULL,
	`title_myanmar` varchar(255),
	`tagline` varchar(255) NOT NULL,
	`client_name` varchar(255) NOT NULL,
	`production_house` varchar(255) NOT NULL,
	`talent_plan` text NOT NULL,
	`production_stage` enum('Storyboard','Pre-production','Production','Post-production','Delivery') NOT NULL DEFAULT 'Storyboard',
	`timeline_start` timestamp,
	`timeline_due` timestamp,
	`storyboard_status` varchar(120) NOT NULL,
	`storyline` text NOT NULL,
	`budget_mmk` int,
	`deliverables` text NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `video_projects_id` PRIMARY KEY(`id`),
	CONSTRAINT `video_projects_project_code_unique` UNIQUE(`project_code`)
);
--> statement-breakpoint
CREATE INDEX `activity_events_occurred_idx` ON `activity_events` (`occurred_at`);--> statement-breakpoint
CREATE INDEX `business_targets_industry_idx` ON `business_targets` (`industry_id`);--> statement-breakpoint
CREATE INDEX `industries_tier_idx` ON `industries` (`industry_tier`);--> statement-breakpoint
CREATE INDEX `notifications_read_priority_idx` ON `notifications` (`is_read`,`priority`);--> statement-breakpoint
CREATE INDEX `production_batches_industry_status_idx` ON `production_batches` (`industry_id`,`batch_status`);--> statement-breakpoint
CREATE INDEX `prompt_versions_active_idx` ON `prompt_versions` (`is_active`);--> statement-breakpoint
CREATE INDEX `proposals_industry_stage_idx` ON `proposals` (`industry_id`,`proposal_stage`);--> statement-breakpoint
CREATE INDEX `proposals_batch_idx` ON `proposals` (`batch_id`);--> statement-breakpoint
CREATE INDEX `video_projects_industry_stage_idx` ON `video_projects` (`industry_id`,`production_stage`);