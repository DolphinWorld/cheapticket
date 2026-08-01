import { env } from "cloudflare:workers";

type RuntimeEnv = { DB: D1Database; MONITOR_API_KEY?: string };
export const runtime = env as unknown as RuntimeEnv;

const schema = `CREATE TABLE IF NOT EXISTS monitors (id INTEGER PRIMARY KEY AUTOINCREMENT, departure TEXT NOT NULL, arrival TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, target_price INTEGER NOT NULL, threshold INTEGER NOT NULL, email TEXT NOT NULL, owner_email TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL)`;

export async function getDb() {
  await runtime.DB.prepare(schema).run();
  return runtime.DB;
}
