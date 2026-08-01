ALTER TABLE `monitors` ADD `owner_email` text DEFAULT '' NOT NULL;
--> statement-breakpoint
UPDATE `monitors` SET `owner_email` = `email` WHERE `owner_email` = '';
