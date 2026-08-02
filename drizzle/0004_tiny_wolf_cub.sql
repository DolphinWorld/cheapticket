ALTER TABLE `monitors` ADD `trip_type` text DEFAULT 'one-way' NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `return_start_date` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `return_start_time` text DEFAULT '00:00' NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `return_end_date` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `return_end_time` text DEFAULT '23:59' NOT NULL;