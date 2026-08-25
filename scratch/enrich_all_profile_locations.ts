import fs from "fs";
import path from "path";

// Load .env
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
import { getWhopProfileEarnings } from "../src/lib/location.server.js";

function extractUsernameFromUrl(url?: string | null): string | null {
  if (!url) return null;
  const m = url.match(/whop\.com\/@([a-zA-Z0-9_\-\.]+)/i);
  return m ? m[1].toLowerCase() : null;
}

async function enrichProfileLocations() {
  console.log("=== Starting Profile Location & Country Batch Rescan ===");

  let allLeads: any[] = [];
  let page = 0;
  const pageSize = 1000;

  while (true) {
    const { data, error } = await supabaseAdmin
      .from("leads")
      .select("id, whop_username, whop_url, country, city, profile_earnings_badge")
      .range(page * pageSize, (page + 1) * pageSize - 1)
      .order("created_at", { ascending: false });

    if (error || !data || data.length === 0) break;
    allLeads = allLeads.concat(data);
    if (data.length < pageSize) break;
    page++;
  }

  console.log(`Total leads retrieved from DB: ${allLeads.length}`);

  const validLeads = allLeads.filter((l) => {
    const rawUname = l.whop_username || extractUsernameFromUrl(l.whop_url);
    const uname = rawUname ? String(rawUname).toLowerCase().replace(/^@/, "").trim() : "";
    return uname && uname !== "anonymous" && uname !== "unknown";
  });

  console.log(`Leads with resolvable usernames: ${validLeads.length}`);

  let updatedLocationCount = 0;
  let updatedEarningsCount = 0;
  let errors = 0;

  const CONCURRENCY = 10;
  for (let i = 0; i < validLeads.length; i += CONCURRENCY) {
    const chunk = validLeads.slice(i, i + CONCURRENCY);

    await Promise.all(
      chunk.map(async (lead) => {
        try {
          const rawUname = lead.whop_username || extractUsernameFromUrl(lead.whop_url);
          const username = rawUname ? String(rawUname).toLowerCase().replace(/^@/, "").trim() : null;

          const intel = await getWhopProfileEarnings(username);
          const updatePayload: Record<string, any> = {};

          if (intel.country && (!lead.country || lead.country !== intel.country)) {
            updatePayload.country = intel.country;
            if (intel.city) updatePayload.city = intel.city;
            updatedLocationCount++;
          } else if (intel.city && (!lead.city || lead.city !== intel.city)) {
            updatePayload.city = intel.city;
            updatedLocationCount++;
          }

          if (intel.badge && !lead.profile_earnings_badge) {
            updatePayload.profile_earnings_badge = intel.badge;
            if (intel.exact_usd !== null) updatePayload.profile_earnings_usd = intel.exact_usd;
            updatedEarningsCount++;
          }

          if (Object.keys(updatePayload).length > 0) {
            const { error: updateErr } = await supabaseAdmin
              .from("leads")
              .update(updatePayload)
              .eq("id", lead.id);

            if (updateErr) {
              errors++;
            }
          }
        } catch {
          errors++;
        }
      })
    );

    if ((i + CONCURRENCY) % 200 === 0 || i + CONCURRENCY >= validLeads.length) {
      console.log(`Processed ${Math.min(i + CONCURRENCY, validLeads.length)} / ${validLeads.length} leads (New Locations: ${updatedLocationCount}, New Badges: ${updatedEarningsCount})`);
    }
  }

  console.log(`\n=== Rescan Complete ===`);
  console.log(`New Profile Locations Found: ${updatedLocationCount}`);
  console.log(`New Profile Earnings Found: ${updatedEarningsCount}`);
}

enrichProfileLocations().catch(console.error);
