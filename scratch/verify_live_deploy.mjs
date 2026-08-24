async function checkLiveDeploy() {
  const res = await fetch("https://free-app-flow.vercel.app/admin", {
    headers: { "User-Agent": "Mozilla/5.0" }
  });
  console.log("Status:", res.status, res.statusText);
  const html = await res.text();
  
  // Look for the bundle script tags
  const scripts = html.match(/\/assets\/[a-zA-Z0-9_\-\.]+\.js/g) || [];
  console.log("Live assets referenced in HTML:", scripts);

  for (const s of scripts.slice(0, 3)) {
    const sRes = await fetch(`https://free-app-flow.vercel.app${s}`);
    const text = await sRes.text();
    const hasLocation = text.includes("Name / Location") || text.includes("Location & Demographics") || text.includes("country_flag");
    console.log(`Checking script ${s} -> Contains Location code:`, hasLocation);
  }
}

checkLiveDeploy();
