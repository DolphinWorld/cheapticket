"use client";
import { FormEvent, useEffect, useState } from "react";

type Monitor = { id: number; departure: string; arrival: string; startDate: string; endDate: string; targetPrice: number; threshold: number; email: string; active: number };
const initial = { departure: "NYC", arrival: "SEA", startDate: "2026-12-20", endDate: "2026-12-24", targetPrice: "550", email: "jacksuyu@gmail.com" };

export default function Dashboard({ signedInEmail }: { signedInEmail: string }) {
  const [form, setForm] = useState(initial); const [items, setItems] = useState<Monitor[]>([]); const [status, setStatus] = useState("");
  async function refresh() { const r = await fetch("/api/monitors"); if (r.ok) setItems(await r.json()); }
  useEffect(() => { refresh(); }, []);
  async function submit(e: FormEvent) { e.preventDefault(); setStatus("Saving…"); const r = await fetch("/api/monitors", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ ...form, targetPrice: Number(form.targetPrice) }) }); setStatus(r.ok ? "Monitor active" : "Could not save"); if (r.ok) refresh(); }
  async function remove(id: number) { await fetch(`/api/monitors?id=${id}`, { method: "DELETE" }); refresh(); }
  return <main>
    <header><a className="brand" href="#">farewatch<span>°</span></a><div className="user"><i />{signedInEmail}</div></header>
    <section className="hero"><div><p className="eyebrow">FLIGHT PRICE MONITOR</p><h1>Tell us where.<br/><em>We’ll watch the fare.</em></h1><p className="lede">Set your route, travel window, and target. We check every two hours and email only when the price drops below your threshold.</p></div><div className="orb"><span>Every</span><strong>2h</strong><small>quietly checking</small></div></section>
    <section className="workspace">
      <form onSubmit={submit}><div className="formHead"><span>01</span><div><h2>Create a monitor</h2><p>Nearby airports are included for metro codes such as NYC and SEA.</p></div></div>
        <div className="route"><label>Leaving from<input required maxLength={3} value={form.departure} onChange={e=>setForm({...form,departure:e.target.value.toUpperCase()})}/><small>City or airport code</small></label><b>→</b><label>Going to<input required maxLength={3} value={form.arrival} onChange={e=>setForm({...form,arrival:e.target.value.toUpperCase()})}/><small>City or airport code</small></label></div>
        <div className="grid"><label>Earliest departure<input type="date" required value={form.startDate} onChange={e=>setForm({...form,startDate:e.target.value})}/></label><label>Latest departure<input type="date" required value={form.endDate} onChange={e=>setForm({...form,endDate:e.target.value})}/></label><label>Target price<div className="money"><span>$</span><input type="number" min="1" required value={form.targetPrice} onChange={e=>setForm({...form,targetPrice:e.target.value})}/></div></label><label>Alert email<input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label></div>
        <button type="submit">Start watching <span>↗</span></button><p className="status" aria-live="polite">{status}</p>
      </form>
      <aside><div className="asideHead"><span>02</span><div><h2>Active watches</h2><p>{items.length} route{items.length===1?"":"s"} on your radar</p></div></div>
        <div className="watches">{items.length===0?<p className="empty">Your saved watches will appear here.</p>:items.map(m=><article key={m.id}><div className="codes"><strong>{m.departure}</strong><span>··· ✈ ···</span><strong>{m.arrival}</strong></div><div className="watchMeta"><span>{m.startDate}<br/>to {m.endDate}</span><span>Alert below<br/><b>${m.threshold}</b></span></div><div className="watchFoot"><span><i/>Checking every 2 hours</span><button onClick={()=>remove(m.id)} aria-label="Delete monitor">×</button></div></article>)}</div>
        <div className="note"><span>i</span><p><b>Main Cabin note</b>The free fare source reports economy pricing. Always confirm the final booking page says Main or Main Cabin—not Basic Economy.</p></div>
      </aside>
    </section>
    <footer><span>Powered by a patient little robot.</span><span>Prices change. Thresholds only move down.</span></footer>
  </main>;
}
