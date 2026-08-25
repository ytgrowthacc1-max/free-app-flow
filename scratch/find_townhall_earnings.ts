import fs from "fs";

async function inspectTownhall() {
  const res = await fetch("https://whop.com/@townhall", {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  const html = await res.text();

  // Find all matches for numbers with dollar signs or earnings
  const dollarMatches = html.match(/\$[\d,]+(?:\.\d+)?/g);
  console.log("Dollar matches in html:", [...new Set(dollarMatches)]);

  // Look for next data or script tags with json
  const scripts = html.match(/<script[^>]*>([\s\S]*?)<\/script>/gi) || [];
  console.log(`Found ${scripts.length} script tags`);

  for (let i = 0; i < scripts.length; i++) {
    const s = scripts[i];
    if (s.includes("2,719") || s.includes("2719") || s.includes("totalEarnings") || s.includes("badge") || s.includes("Earned")) {
      console.log(`\nScript #${i} matching keywords:`);
      // Find 200 chars around match
      const m = s.match(/(?:2,719|2719|totalEarnings|badge|Earned)/);
      if (m && m.index !== undefined) {
        console.log(s.slice(Math.max(0, m.index - 100), Math.min(s.length, m.index + 200)));
      }
    }
  }
}

inspectTownhall().catch(console.error);
