"use client";
import { FormEvent, useEffect, useState } from "react";

type Monitor = { id: number; departure: string; arrival: string; startDate: string; endDate: string; targetPrice: number; threshold: number; email: string; active: number };
type AccessUser = { email: string; role: string };
const initialFor = (email: string) => ({ departure: "NYC", arrival: "SEA", startDate: "2026-12-20", endDate: "2026-12-24", targetPrice: "550", email });

export default function Dashboard({ signedInEmail, isAdmin }: { signedInEmail: string; isAdmin: boolean }) {
  const [form, setForm] = useState(initialFor(signedInEmail)); const [items, setItems] = useState<Monitor[]>([]); const [status, setStatus] = useState(""); const [editingId, setEditingId] = useState<number|null>(null);
  async function refresh() { const r = await fetch("/api/monitors"); if (r.ok) setItems(await r.json()); }
  useEffect(() => { refresh(); }, []);
  async function submit(e: FormEvent) { e.preventDefault(); setStatus("Saving…"); const r = await fetch("/api/monitors", { method: editingId ? "PUT" : "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ ...form, id: editingId, targetPrice: Number(form.targetPrice) }) }); setStatus(r.ok ? (editingId ? "Watch updated" : "Monitor active") : "Could not save"); if (r.ok) { setEditingId(null); setForm(initialFor(signedInEmail)); refresh(); } }
  function edit(m: Monitor) { setEditingId(m.id); setForm({departure:m.departure,arrival:m.arrival,startDate:m.startDate,endDate:m.endDate,targetPrice:String(m.targetPrice),email:m.email}); setStatus("Editing watch"); document.querySelector(".workspace")?.scrollIntoView({behavior:"smooth"}); }
  function cancelEdit() { setEditingId(null); setForm(initialFor(signedInEmail)); setStatus(""); }
  async function remove(id: number) { await fetch(`/api/monitors?id=${id}`, { method: "DELETE" }); refresh(); }
  return <main>
    <header><a className="brand" href="#">farewatch<span>°</span></a><div className="user"><i />{signedInEmail}{isAdmin&&<a href="#admin">Admin</a>}<a href="/signout-with-chatgpt?return_to=%2F">Sign out</a></div></header>
    <section className="hero"><div><p className="eyebrow">FLIGHT PRICE MONITOR</p><h1>Tell us where.<br/><em>We’ll watch the fare.</em></h1><p className="lede">Set your route, travel window, and target. We check every two hours and email only when the price drops below your threshold.</p></div><div className="orb"><span>Every</span><strong>2h</strong><small>quietly checking</small></div></section>
    <section className="workspace">
      <form onSubmit={submit}><div className="formHead"><span>01</span><div><h2>{editingId ? "Update your watch" : "Create a monitor"}</h2><p>Nearby airports are included for metro codes such as NYC and SEA.</p></div></div>
        <div className="route"><label>Leaving from<input required maxLength={3} value={form.departure} onChange={e=>setForm({...form,departure:e.target.value.toUpperCase()})}/><small>City or airport code</small></label><b>→</b><label>Going to<input required maxLength={3} value={form.arrival} onChange={e=>setForm({...form,arrival:e.target.value.toUpperCase()})}/><small>City or airport code</small></label></div>
        <div className="grid"><label>Earliest departure<input type="date" required value={form.startDate} onChange={e=>setForm({...form,startDate:e.target.value})}/></label><label>Latest departure<input type="date" required value={form.endDate} onChange={e=>setForm({...form,endDate:e.target.value})}/></label><label>Target price<div className="money"><span>$</span><input type="number" min="1" required value={form.targetPrice} onChange={e=>setForm({...form,targetPrice:e.target.value})}/></div></label><label>Alert email<input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label></div>
        <button type="submit">{editingId ? "Save changes" : "Start watching"} <span>↗</span></button>{editingId&&<button type="button" className="cancel" onClick={cancelEdit}>Cancel editing</button>}<p className="status" aria-live="polite">{status}</p>
      </form>
      <aside><div className="asideHead"><span>02</span><div><h2>Active watches</h2><p>{items.length} route{items.length===1?"":"s"} on your radar</p></div></div>
        <div className="watches">{items.length===0?<p className="empty">Your saved watches will appear here.</p>:items.map(m=><article key={m.id}><div className="codes"><strong>{m.departure}</strong><span>··· ✈ ···</span><strong>{m.arrival}</strong></div><div className="watchMeta"><span>{m.startDate}<br/>to {m.endDate}</span><span>Current threshold<br/><b>${m.threshold}</b></span></div><div className="watchFoot"><span><i/>Checking every 2 hours</span><div className="actions"><button onClick={()=>edit(m)} aria-label="Edit monitor">Edit</button><button onClick={()=>remove(m.id)} aria-label="Delete monitor">Remove</button></div></div></article>)}</div>
        <div className="note"><span>i</span><p><b>Main Cabin note</b>The free fare source reports economy pricing. Always confirm the final booking page says Main or Main Cabin—not Basic Economy.</p></div>
      </aside>
    </section>
    {isAdmin&&<AdminPanel />}
    <footer><span>Powered by a patient little robot.</span><span>Prices change. Thresholds only move down.</span></footer>
  </main>;
}

function AdminPanel() {
  const [users,setUsers]=useState<AccessUser[]>([]); const [email,setEmail]=useState(""); const [message,setMessage]=useState("");
  async function refresh(){const r=await fetch("/api/admin/users");if(r.ok)setUsers(await r.json())}
  useEffect(()=>{refresh()},[]);
  async function add(e:FormEvent){e.preventDefault();setMessage("Adding…");const r=await fetch("/api/admin/users",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({email})});setMessage(r.ok?"Access granted":"Could not add email");if(r.ok){setEmail("");refresh()}}
  async function remove(userEmail:string){const r=await fetch(`/api/admin/users?email=${encodeURIComponent(userEmail)}`,{method:"DELETE"});if(r.ok)refresh();else setMessage("Could not remove email")}
  return <section className="adminPanel" id="admin"><div className="asideHead"><span>03</span><div><h2>Access administration</h2><p>Add or remove people who can sign in to Farewatch.</p></div></div><form onSubmit={add}><label>Approved email<input type="email" required placeholder="person@example.com" value={email} onChange={e=>setEmail(e.target.value)}/></label><button type="submit">Grant access <span>↗</span></button></form><p className="status">{message}</p><div className="userList">{users.map(u=><div key={u.email}><span><b>{u.email}</b><small>{u.role}</small></span>{u.role!=="admin"&&<button onClick={()=>remove(u.email)}>Remove</button>}</div>)}</div></section>;
}
