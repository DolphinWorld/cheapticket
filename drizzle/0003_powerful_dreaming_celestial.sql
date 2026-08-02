ALTER TABLE `monitors` ADD `start_time` text DEFAULT '00:00' NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `end_time` text DEFAULT '23:59' NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `airline` text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `airline_target_price` integer DEFAULT 550 NOT NULL;--> statement-breakpoint
ALTER TABLE `monitors` ADD `airline_threshold` integer DEFAULT 550 NOT NULL;
--> statement-breakpoint
UPDATE `monitors` SET `airline_target_price` = `target_price`, `airline_threshold` = `threshold`;
