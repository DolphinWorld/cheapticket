import { headers } from "next/headers";
import { redirect } from "next/navigation";
export async function getUserEmail() { return (await headers()).get("oai-authenticated-user-email"); }
export async function requireUser() { const email = await getUserEmail(); if (!email) redirect("/signin-with-chatgpt?return_to=%2F"); return email; }
