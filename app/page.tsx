import { requireUser } from "./chatgpt-auth";
import Dashboard from "./dashboard";
import AccessDenied from "./access-denied";
import { getAccessUser } from "@/db";
export const dynamic = "force-dynamic";
export default async function Page() { const email = (await requireUser()).toLowerCase(); const access = await getAccessUser(email); if (!access) return <AccessDenied email={email}/>; return <Dashboard signedInEmail={email} isAdmin={access.role==="admin"} />; }
