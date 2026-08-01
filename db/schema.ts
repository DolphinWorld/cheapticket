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
  active: integer("active").notNull().default(1),
  updatedAt: text("updated_at").notNull(),
});
