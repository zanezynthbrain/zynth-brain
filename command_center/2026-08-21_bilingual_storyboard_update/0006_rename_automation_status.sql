ALTER TABLE `automation_configs` CHANGE `batch_status` `last_status` enum('Queued','Researching','Generating','Quality review','Publishing','Complete','Failed') NOT NULL DEFAULT 'Queued';
