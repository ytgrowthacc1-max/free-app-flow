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

import { supabaseAdmin, calcLeadScore } from "../src/lib/leads.server.js";
import { getPeopleCache, getWhopProfileEarnings, getCountryFlag, getCountryName } from "../src/lib/location.server.js";

async function backfill() {
  console.log("=== Backfilling Missing Country, Earnings & Scores ===");
  const cache = await getPeopleCache();
  console.log(`Loaded Whop People cache: ${cache.byUserId.size} user IDs, ${cache.byUsername.size} usernames.`);

  // Get leads with missing country or missing earnings
  let allLeads: any[] = [];
  let page = 0;
  const pageSize = 1000;

  while (true) {
    const { data, error } = await supabaseAdmin
      .from("leads")
      .select("*")
      .range(page * pageSize, (page + 1) * pageSize - 1);

    if (error) {
      console.error("Select error:", error);
      break;
    }
    if (!data || data.length === 0) break;
    allLeads = allLeads.concat(data);
    if (data.length < pageSize) break;
    page++;
  }

  console.log(`Total leads to evaluate: ${allLeads.length}`);
  let updatedCount = 0;

  for (let i = 0; i < allLeads.length; i++) {
    const l = allLeads[i];
    let country = l.country || null;
    let city = l.city || null;
    let timezone = l.timezone || null;
    let badge = l.profile_earnings_badge || null;
    let usd = l.profile_earnings_usd !== null && l.profile_earnings_usd !== undefined ? Number(l.profile_earnings_usd) : null;

    const uid = l.whop_user_id;
    const uname = l.whop_username ? String(l.whop_username).toLowerCase().replace(/^@/, "").trim() : "";

    // 1. Resolve Location if missing
    if (!country) {
      let loc = null;
      if (uid && cache.byUserId.has(uid)) loc = cache.byUserId.get(uid);
      else if (uname && uname !== "anonymous" && uname !== "unknown" && cache.byUsername.has(uname)) loc = cache.byUsername.get(uname);
      
      if (loc && loc.country) {
        country = loc.country;
        if (loc.city) city = loc.city;
        if (loc.timezone) timezone = loc.timezone;
      }
    }

    // 2. Resolve Profile Earnings if missing and valid username
    if (!badge && usd === null && uname && uname !== "anonymous" && uname !== "unknown") {
      try {
        const intel = await getWhopProfileEarnings(uname);
        if (intel.badge) badge = intel.badge;
        if (intel.exact_usd !== null && intel.exact_usd !== undefined) usd = intel.exact_usd;
        if (!country && intel.country) {
          country = intel.country.toUpperCase();
          if (intel.city) city = intel.city;
        }
      } catch {
        // ignore
      }
    }

    // 3. Recalculate lead score with updated country & profile earnings
    const newScore = calcLeadScore(
      l.member_count,
      l.monthly_price,
      l.timeline,
      l.community_status,
      l.willing_to_invest,
      usd,
      badge,
      country
    );

    const updates: Record<string, any> = {};
    if (country !== l.country) updates.country = country;
    if (city !== l.city) updates.city = city;
    if (timezone !== l.timezone) updates.timezone = timezone;
    if (badge !== l.profile_earnings_badge) updates.profile_earnings_badge = badge;
    if (usd !== l.profile_earnings_usd) updates.profile_earnings_usd = usd;
    if (newScore.score !== l.lead_score) updates.lead_score = newScore.score;
    if (newScore.tag !== l.lead_tag) updates.lead_tag = newScore.tag;

    if (Object.keys(updates).length > 0) {
      const { error: updateErr } = await supabaseAdmin
        .from("leads")
        .update(updates)
        .eq("id", l.id);

      if (!updateErr) {
        updatedCount++;
      } else {
        console.error(`Failed to update lead ${l.id}:`, updateErr.message);
      }
    }

    if ((i + 1) % 250 === 0 || i + 1 === allLeads.length) {
      console.log(`Evaluated ${i + 1} / ${allLeads.length} leads... Updated: ${updatedCount}`);
    }
  }

  console.log(`\n=== Backfill Complete ===`);
  console.log(`Updated ${updatedCount} leads in Supabase.`);
}

backfill().catch(console.error);
