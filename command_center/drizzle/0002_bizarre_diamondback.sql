CREATE TABLE `automation_configs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`code` varchar(100) NOT NULL,
	`schedule_cron_task_uid` varchar(65),
	`cron_expression` varchar(120) NOT NULL,
	`is_enabled` int NOT NULL DEFAULT 1,
	`last_run_at` timestamp,
	`batch_status` enum('Queued','Researching','Generating','Quality review','Publishing','Complete','Failed') NOT NULL DEFAULT 'Queued',
	`last_error` text,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `automation_configs_id` PRIMARY KEY(`id`),
	CONSTRAINT `automation_configs_code_unique` UNIQUE(`code`)
);
--> statement-breakpoint
CREATE INDEX `automation_configs_task_uid_idx` ON `automation_configs` (`schedule_cron_task_uid`);