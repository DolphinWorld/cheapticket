import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const monitors = sqliteTable("monitors", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  departure: text("departure").notNull(),
  arrival: text("arrival").notNull(),
  startDate: text("start_date").notNull(),
  endDate: text("end_date").notNull(),
  targetPrice: integer("target_price").notNull(),
  threshold: integer("threshold").notNull(),
  email: text("email").notNull(),
  ownerEmail: text("owner_email").notNull().default(""),
  active: integer("active").notNull().default(1),
  updatedAt: text("updated_at").notNull(),
});

export const accessUsers = sqliteTable("access_users", {
  email: text("email").primaryKey(),
  role: text("role").notNull().default("user"),
  createdAt: text("created_at").notNull(),
});
