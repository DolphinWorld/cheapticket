import { requireUser } from "./chatgpt-auth";
import Dashboard from "./dashboard";
export default async function Page() { const email = await requireUser(); return <Dashboard signedInEmail={email} />; }
