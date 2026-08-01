import { requireUser } from "./chatgpt-auth";
import Dashboard from "./dashboard";
export const dynamic = "force-dynamic";
export default async function Page() { const email = await requireUser(); return <Dashboard signedInEmail={email} />; }
