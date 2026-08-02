import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";
import "./actions.css";
import "./admin.css";

export async function generateMetadata(): Promise<Metadata> {
  const h = await headers();
  const host = h.get("x-forwarded-host") ?? h.get("host") ?? "localhost:3000";
  const protocol = h.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const image = `${protocol}://${host}/og.png`;
  return { title: "Farewatch", description: "A quiet flight-price monitor for the routes that matter.", openGraph: { title: "Farewatch", description: "Tell us where. We’ll watch the fare.", images: [image] }, twitter: { card: "summary_large_image", images: [image] } };
}
export default function Layout({ children }: { children: React.ReactNode }) { return <html lang="en"><body>{children}</body></html>; }
