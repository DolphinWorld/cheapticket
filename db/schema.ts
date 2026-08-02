import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const monitors = sqliteTable("monitors", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  departure: text("departure").notNull(),
  arrival: text("arrival").notNull(),
  tripType: text("trip_type").notNull().default("one-way"),
  startDate: text("start_date").notNull(),
  startTime: text("start_time").notNull().default("00:00"),
  endDate: text("end_date").notNull(),
  endTime: text("end_time").notNull().default("23:59"),
  returnStartDate: text("return_start_date").notNull().default(""),
  returnStartTime: text("return_start_time").notNull().default("00:00"),
  returnEndDate: text("return_end_date").notNull().default(""),
  returnEndTime: text("return_end_time").notNull().default("23:59"),
  airline: text("airline").notNull().default(""),
  targetPrice: integer("target_price").notNull(),
  threshold: integer("threshold").notNull(),
  airlineTargetPrice: integer("airline_target_price").notNull().default(550),
  airlineThreshold: integer("airline_threshold").notNull().default(550),
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
