import { NextRequest, NextResponse } from "next/server";
import { getAccessUser, getDb } from "@/db";

async function admin(req: NextRequest) {
  const email=req.headers.get("oai-authenticated-user-email")?.toLowerCase();
  return email ? (await getAccessUser(email))?.role === "admin" : false;
}
export async function GET(req: NextRequest){if(!await admin(req))return NextResponse.json({error:"Forbidden"},{status:403});const db=await getDb();const {results}=await db.prepare("SELECT email, role FROM access_users ORDER BY role, email").all();return NextResponse.json(results)}
export async function POST(req: NextRequest){if(!await admin(req))return NextResponse.json({error:"Forbidden"},{status:403});const {email}=await req.json();const normalized=String(email).trim().toLowerCase();if(!/^\S+@\S+\.\S+$/.test(normalized))return NextResponse.json({error:"Invalid email"},{status:400});const db=await getDb();await db.prepare("INSERT INTO access_users (email,role,created_at) VALUES (?,'user',?) ON CONFLICT(email) DO NOTHING").bind(normalized,new Date().toISOString()).run();return NextResponse.json({ok:true},{status:201})}
export async function DELETE(req: NextRequest){if(!await admin(req))return NextResponse.json({error:"Forbidden"},{status:403});const email=req.nextUrl.searchParams.get("email")?.toLowerCase();const db=await getDb();const result=await db.prepare("DELETE FROM access_users WHERE email=? AND role<>'admin'").bind(email).run();return NextResponse.json({ok:result.meta.changes===1},{status:result.meta.changes===1?200:400})}
