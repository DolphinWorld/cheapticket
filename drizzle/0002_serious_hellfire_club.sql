CREATE TABLE `access_users` (
	`email` text PRIMARY KEY NOT NULL,
	`role` text DEFAULT 'user' NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
INSERT INTO `access_users` (`email`, `role`, `created_at`) VALUES ('jacksuyu@gmail.com', 'admin', CURRENT_TIMESTAMP);
--> statement-breakpoint
INSERT INTO `access_users` (`email`, `role`, `created_at`) VALUES ('danielsuhang@gmail.com', 'user', CURRENT_TIMESTAMP);
