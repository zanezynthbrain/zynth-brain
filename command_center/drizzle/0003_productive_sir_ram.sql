ALTER TABLE `production_batches` ADD `sync_retry_status` enum('Not needed','Retry scheduled','Retrying','Exhausted') DEFAULT 'Not needed' NOT NULL;--> statement-breakpoint
ALTER TABLE `production_batches` ADD `github_url` varchar(1024);--> statement-breakpoint
ALTER TABLE `video_projects` ADD `video_approval_status` enum('Not started','Client review','Approved','Changes requested') DEFAULT 'Not started' NOT NULL;--> statement-breakpoint
ALTER TABLE `video_projects` ADD `approval_notes` text;