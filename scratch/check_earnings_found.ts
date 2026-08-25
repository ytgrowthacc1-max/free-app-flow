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

async function checkEarningsResults() {
  // Query leads where profile_earnings_badge is not null
  let allEarningsLeads: any[] = [];
  let page = 0;
  const pageSize = 1000;

  while (true) {
    const { data, error } = await supabaseAdmin
      .from("leads")
      .select("id, whop_username, first_name, country, profile_earnings_badge, profile_earnings_usd")
      .not("profile_earnings_badge", "is", null)
      .range(page * pageSize, (page + 1) * pageSize - 1);

    if (error || !data || data.length === 0) break;
    allEarningsLeads = allEarningsLeads.concat(data);
    if (data.length < pageSize) break;
    page++;
  }

  console.log(`\nTotal leads with profile_earnings_badge in DB: ${allEarningsLeads.length}`);

  // Leads with profile_earnings_usd > 0
  const positiveEarnings = allEarningsLeads.filter((l) => {
    const badgeVal = l.profile_earnings_badge ? parseFloat(String(l.profile_earnings_badge).replace(/[\$,]/g, "")) : 0;
    const usdVal = l.profile_earnings_usd ? parseFloat(String(l.profile_earnings_usd)) : 0;
    return badgeVal > 0 || usdVal > 0;
  });

  console.log(`Leads with Earnings > $0 found: ${positiveEarnings.length}`);

  if (positiveEarnings.length > 0) {
    console.log("\n=== Top Leads with Public Profile Earnings Found in DB ===");
    const sorted = positiveEarnings.sort((a, b) => {
      const valA = parseFloat(String(a.profile_earnings_usd || a.profile_earnings_badge).replace(/[\$,]/g, "")) || 0;
      const valB = parseFloat(String(b.profile_earnings_usd || b.profile_earnings_badge).replace(/[\$,]/g, "")) || 0;
      return valB - valA;
    });

    for (const l of sorted.slice(0, 30)) {
      const badge = l.profile_earnings_badge || (l.profile_earnings_usd ? `$${l.profile_earnings_usd}` : "N/A");
      console.log(`• @${(l.whop_username || "unknown").padEnd(20)} | Badge: ${badge.padEnd(12)} | Name: ${(l.first_name || "").slice(0, 20)}`);
    }
  }
}

checkEarningsResults().catch(console.error);
