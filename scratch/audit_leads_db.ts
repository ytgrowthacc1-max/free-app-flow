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

async function auditLeads() {
  const { count: totalLeads } = await supabaseAdmin.from("leads").select("*", { count: "exact", head: true });
  console.log("Total leads in DB:", totalLeads);

  // Fetch all leads (paginate past 1000 limit)
  let allLeads: any[] = [];
  let page = 0;
  const pageSize = 1000;
  while (true) {
    const { data, error } = await supabaseAdmin
      .from("leads")
      .select("id, whop_username, whop_user_id, whop_url, country, profile_earnings_badge, profile_earnings_usd, scraped_data")
      .range(page * pageSize, (page + 1) * pageSize - 1);

    if (error || !data || data.length === 0) break;
    allLeads = allLeads.concat(data);
    if (data.length < pageSize) break;
    page++;
  }

  console.log("Total fetched leads:", allLeads.length);

  const withUsername = allLeads.filter(l => l.whop_username && l.whop_username !== "Anonymous" && l.whop_username !== "unknown");
  console.log("Leads with valid whop_username:", withUsername.length);

  const withWhopUrl = allLeads.filter(l => l.whop_url && l.whop_url.includes("whop.com"));
  console.log("Leads with valid whop_url:", withWhopUrl.length);

  const withCountry = allLeads.filter(l => l.country);
  console.log("Leads with country in DB:", withCountry.length);

  const withBadge = allLeads.filter(l => l.profile_earnings_badge);
  console.log("Leads with profile_earnings_badge in DB:", withBadge.length);

  const withUsd = allLeads.filter(l => l.profile_earnings_usd !== null && l.profile_earnings_usd !== undefined && Number(l.profile_earnings_usd) > 0);
  console.log("Leads with profile_earnings_usd > 0 in DB:", withUsd.length);

  // Print sample leads with earnings or badges
  if (withBadge.length > 0) {
    console.log("\nSample leads with badge:");
    console.log(withBadge.slice(0, 5).map(l => ({ username: l.whop_username, badge: l.profile_earnings_badge, usd: l.profile_earnings_usd })));
  }
}

auditLeads().catch(console.error);
