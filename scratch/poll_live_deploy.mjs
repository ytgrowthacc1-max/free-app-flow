async function pollLiveDeploy() {
  for (let i = 1; i <= 6; i++) {
    console.log(`[Attempt ${i}/6] Checking live deployment...`);
    const res = await fetch("https://free-app-flow.vercel.app/admin", {
      headers: { "Cache-Control": "no-cache", "Pragma": "no-cache" }
    });
    const html = await res.text();
    const scripts = html.match(/\/assets\/[a-zA-Z0-9_\-\.]+\.js/g) || [];
    let deployed = false;
    for (const s of scripts) {
      const sRes = await fetch(`https://free-app-flow.vercel.app${s}`);
      const text = await sRes.text();
      if (text.includes("Name / Location") || text.includes("Location & Demographics") || text.includes("country_flag")) {
        deployed = true;
        console.log(`🎉 Live deployment detected! Found new bundle: ${s}`);
        return true;
      }
    }
    if (!deployed) {
      console.log(`Current bundles: ${scripts.join(", ")} (Still building or deploying on Vercel...)`);
      await new Promise(r => setTimeout(r, 10000));
    }
  }
}

pollLiveDeploy();
