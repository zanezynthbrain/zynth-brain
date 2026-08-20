ALTER TABLE `production_batches` ADD `drive_synced_at` timestamp;--> statement-breakpoint
ALTER TABLE `production_batches` ADD `github_synced_at` timestamp;--> statement-breakpoint
ALTER TABLE `production_batches` ADD `last_retry_at` timestamp;