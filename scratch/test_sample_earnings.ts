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

import { supabaseAdmin } from "../src/lib/leads.server.js";

async function testEarningsScrape() {
  const { data: leads } = await supabaseAdmin
    .from("leads")
    .select("id, whop_username, whop_url")
    .not("whop_username", "is", null)
    .limit(50);

  if (!leads) return;

  console.log(`Testing 50 leads...`);
  let countWithBadge = 0;

  for (const lead of leads) {
    const username = lead.whop_username?.replace(/^@/, "").trim();
    if (!username || username === "Anonymous" || username === "unknown") continue;

    try {
      const res = await fetch(`https://whop.com/@${username}`, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
      });
      if (!res.ok) {
        console.log(`@${username}: status ${res.status}`);
        continue;
      }
      const html = await res.text();
      
      // Look for any dollar signs or earnings indicators
      const badgeMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i);
      const usdMatch = html.match(/totalEarningsWithTransfersInUsd:"([\d\.]+)"/);
      const anyDollar = html.match(/\$[\d,]+(?:\.\d+)?/g);
      const mentionsEarned = html.includes("Earned");

      if (badgeMatch || usdMatch) {
        countWithBadge++;
        console.log(`[FOUND!] @${username} -> Badge: ${badgeMatch?.[1]}, USD: ${usdMatch?.[1]}`);
      } else {
        if (mentionsEarned || (anyDollar && anyDollar.length > 0)) {
          console.log(`@${username}: mentions Earned=${mentionsEarned}, dollars=${anyDollar?.slice(0, 3).join(", ")}`);
        }
      }
    } catch (e: any) {
      console.log(`@${username}: error ${e.message}`);
    }
  }

  console.log(`\nTotal with badge found in sample: ${countWithBadge}/50`);
}

testEarningsScrape().catch(console.error);
