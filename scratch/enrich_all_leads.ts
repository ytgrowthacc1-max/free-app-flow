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
import { resolveWhopLocation, getWhopProfileEarnings } from "../src/lib/location.server.js";

function extractUsernameFromUrl(url?: string | null): string | null {
  if (!url) return null;
  const m = url.match(/whop\.com\/@([a-zA-Z0-9_\-\.]+)/i);
  return m ? m[1].toLowerCase() : null;
}

async function enrichAllLeads() {
  console.log("=== Starting Full Database Lead Enrichment ===");

  // 1. Paginate and load ALL leads from Supabase
  let allLeads: any[] = [];
  let page = 0;
  const pageSize = 1000;

  while (true) {
    const { data, error } = await supabaseAdmin
      .from("leads")
      .select("id, whop_username, whop_user_id, whop_url, country, profile_earnings_badge, profile_earnings_usd")
      .range(page * pageSize, (page + 1) * pageSize - 1)
      .order("created_at", { ascending: false });

    if (error || !data || data.length === 0) break;
    allLeads = allLeads.concat(data);
    console.log(`Loaded page ${page + 1}: ${data.length} leads (Total so far: ${allLeads.length})`);
    if (data.length < pageSize) break;
    page++;
  }

  console.log(`\nTotal leads retrieved from DB: ${allLeads.length}`);

  // 2. Filter leads that have usernames or user_ids
  const validLeads = allLeads.filter((l) => {
    const uname = l.whop_username || extractUsernameFromUrl(l.whop_url);
    const uid = l.whop_user_id;
    const cleanUname = uname ? String(uname).toLowerCase().replace(/^@/, "").trim() : "";
    return (cleanUname && cleanUname !== "anonymous" && cleanUname !== "unknown") || Boolean(uid);
  });

  console.log(`Leads with resolvable username/user_id: ${validLeads.length}`);

  let enrichedCount = 0;
  let earningsBadgeCount = 0;
  let errorCount = 0;

  // 3. Process in batches of 10 in parallel
  const CONCURRENCY = 10;
  for (let i = 0; i < validLeads.length; i += CONCURRENCY) {
    const chunk = validLeads.slice(i, i + CONCURRENCY);

    await Promise.all(
      chunk.map(async (lead) => {
        try {
          const rawUname = lead.whop_username || extractUsernameFromUrl(lead.whop_url);
          const username = rawUname ? String(rawUname).toLowerCase().replace(/^@/, "").trim() : null;
          const userId = lead.whop_user_id || null;

          const [loc, earnings] = await Promise.all([
            resolveWhopLocation(userId, username, lead.country),
            getWhopProfileEarnings(username),
          ]);

          const updatePayload: Record<string, any> = {};

          if (loc.country && loc.country !== lead.country) {
            updatePayload.country = loc.country;
          }
          if (loc.city && loc.city !== lead.city) {
            updatePayload.city = loc.city;
          }
          if (loc.timezone && loc.timezone !== lead.timezone) {
            updatePayload.timezone = loc.timezone;
          }

          if (earnings.badge) {
            updatePayload.profile_earnings_badge = earnings.badge;
            if (earnings.exact_usd !== null) {
              updatePayload.profile_earnings_usd = earnings.exact_usd;
            }
            earningsBadgeCount++;
          }

          if (Object.keys(updatePayload).length > 0) {
            const { error: updateErr } = await supabaseAdmin
              .from("leads")
              .update(updatePayload)
              .eq("id", lead.id);

            if (updateErr) {
              console.error(`Failed update lead ${lead.id}:`, updateErr.message);
              errorCount++;
            } else {
              enrichedCount++;
            }
          }
        } catch (err: any) {
          errorCount++;
        }
      })
    );

    if ((i + CONCURRENCY) % 100 === 0 || i + CONCURRENCY >= validLeads.length) {
      console.log(`Processed ${Math.min(i + CONCURRENCY, validLeads.length)} / ${validLeads.length} leads (Enriched DB: ${enrichedCount}, Earnings Badges Found: ${earningsBadgeCount})`);
    }
  }

  console.log(`\n=== Full Enrichment Complete ===`);
  console.log(`Total Leads Processed: ${validLeads.length}`);
  console.log(`Successfully Enriched DB: ${enrichedCount}`);
  console.log(`Profile Earnings Badges Found: ${earningsBadgeCount}`);
  console.log(`Errors: ${errorCount}`);
}

enrichAllLeads().catch(console.error);
