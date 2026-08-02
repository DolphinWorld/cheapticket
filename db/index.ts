import { env } from "cloudflare:workers";

type RuntimeEnv = { DB: D1Database; MONITOR_API_KEY?: string; GITHUB_ACTIONS_TOKEN?: string };
export const runtime = env as unknown as RuntimeEnv;

const monitorSchema = `CREATE TABLE IF NOT EXISTS monitors (id INTEGER PRIMARY KEY AUTOINCREMENT, departure TEXT NOT NULL, arrival TEXT NOT NULL, trip_type TEXT NOT NULL DEFAULT 'one-way', start_date TEXT NOT NULL, start_time TEXT NOT NULL DEFAULT '00:00', end_date TEXT NOT NULL, end_time TEXT NOT NULL DEFAULT '23:59', return_start_date TEXT NOT NULL DEFAULT '', return_start_time TEXT NOT NULL DEFAULT '00:00', return_end_date TEXT NOT NULL DEFAULT '', return_end_time TEXT NOT NULL DEFAULT '23:59', airline TEXT NOT NULL DEFAULT '', target_price INTEGER NOT NULL, threshold INTEGER NOT NULL, airline_target_price INTEGER NOT NULL DEFAULT 550, airline_threshold INTEGER NOT NULL DEFAULT 550, email TEXT NOT NULL, owner_email TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL)`;
const accessSchema = `CREATE TABLE IF NOT EXISTS access_users (email TEXT PRIMARY KEY NOT NULL, role TEXT NOT NULL DEFAULT 'user', created_at TEXT NOT NULL)`;

export async function getDb() {
  await runtime.DB.batch([
    runtime.DB.prepare(monitorSchema),
    runtime.DB.prepare(accessSchema),
  ]);
  return runtime.DB;
}

export async function getAccessUser(email: string) {
  const db = await getDb();
  return db.prepare("SELECT email, role FROM access_users WHERE email=?")
    .bind(email.toLowerCase()).first<{ email: string; role: string }>();
}
