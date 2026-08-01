CREATE TABLE `monitors` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`departure` text NOT NULL,
	`arrival` text NOT NULL,
	`start_date` text NOT NULL,
	`end_date` text NOT NULL,
	`target_price` integer NOT NULL,
	`threshold` integer NOT NULL,
	`email` text NOT NULL,
	`active` integer DEFAULT 1 NOT NULL,
	`updated_at` text NOT NULL
);
