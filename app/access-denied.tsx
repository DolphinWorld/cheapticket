export default function AccessDenied({ email }: { email: string }) {
  return <main className="gate"><section><a className="brand" href="#">farewatch<span>°</span></a><p className="eyebrow">ACCESS REQUIRED</p><h1>This account isn’t on the list.</h1><p>You signed in as <b>{email}</b>. Ask the Farewatch administrator to add this exact email address.</p><a className="gateButton" href="/signout-with-chatgpt?return_to=%2F">Use another account</a></section></main>;
}
