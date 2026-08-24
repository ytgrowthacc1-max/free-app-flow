import fs from "fs";
import path from "path";

const envPath = path.resolve(process.cwd(), ".env");
if (fs.existsSync(envPath)) {
  const content = fs.readFileSync(envPath, "utf8");
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx > 0) {
      const key = trimmed.slice(0, eqIdx).trim();
      const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, "");
      if (!process.env[key]) process.env[key] = val;
    }
  }
}

async function scrapeProfileEarningsForLeads() {
  const { supabaseAdmin } = await import("../src/lib/leads.server.js");
  const { data: leads, error } = await supabaseAdmin.from("leads").select("id, whop_username, first_name").not("whop_username", "is", null).limit(100);
  if (error) return console.error(error);

  console.log(`Testing profile earnings scrape for ${leads.length} leads with usernames...`);

  let countWithBadge = 0;
  const results = [];

  const promises = leads.map(async (l) => {
    const username = (l.whop_username || "").replace(/^@/, "").trim();
    if (!username || username === "anonymous" || username === "unknown") return;

    try {
      const res = await fetch(`https://whop.com/@${username}`, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
      });
      if (res.ok) {
        const html = await res.text();
        const badgeMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i);
        const usdMatch = html.match(/totalEarningsWithTransfersInUsd:"([\d\.]+)"/);
        
        let numVal = null;
        if (badgeMatch) {
          numVal = parseFloat(badgeMatch[1].replace(/[\$,]/g, ""));
        } else if (usdMatch) {
          numVal = parseFloat(usdMatch[1]);
        }

        if (badgeMatch || usdMatch) {
          countWithBadge++;
          results.push({ name: l.first_name, username, badge: badgeMatch ? badgeMatch[1] : null, numVal });
        }
      }
    } catch (e) {
      // ignore
    }
  });

  await Promise.all(promises);
  console.log(`Leads with profile earnings badge: ${countWithBadge}`);
  console.log("Sample results with profile earnings:", results.slice(0, 10));
}

scrapeProfileEarningsForLeads();
