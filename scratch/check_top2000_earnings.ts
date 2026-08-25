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

async function checkLeadingDates() {
  const { data: top2000 } = await supabaseAdmin
    .from("leads")
    .select("id, whop_username, profile_earnings_badge, profile_earnings_usd, created_at")
    .order("created_at", { ascending: false })
    .limit(2000);

  if (!top2000) return;

  const top2000WithEarnings = top2000.filter(l => {
    const badgeVal = l.profile_earnings_badge ? parseFloat(String(l.profile_earnings_badge).replace(/[\$,]/g, "")) : 0;
    const usdVal = l.profile_earnings_usd ? parseFloat(String(l.profile_earnings_usd)) : 0;
    return badgeVal > 0 || usdVal > 0;
  });

  console.log(`In the latest 2000 leads returned to Admin UI:`);
  console.log(`Leads with profile_earnings > 0: ${top2000WithEarnings.length}`);

  if (top2000WithEarnings.length > 0) {
    console.log("Sample from latest 2000:");
    console.log(top2000WithEarnings.slice(0, 10).map(l => ({ username: l.whop_username, badge: l.profile_earnings_badge, usd: l.profile_earnings_usd, created_at: l.created_at })));
  }
}

checkLeadingDates().catch(console.error);
