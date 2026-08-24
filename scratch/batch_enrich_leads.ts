/**
 * One-time batch enrichment: adds country/city/timezone/profile_earnings columns
 * to the leads table and backfills all existing leads.
 */
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

async function addColumnsViaSQL() {
  // Use supabase rpc or direct DDL via the service role client
  // Supabase JS client doesn't support DDL directly, so we use the REST API
  const supabaseUrl = process.env.SUPABASE_URL || "";
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || "";
  
  if (!supabaseUrl || !serviceKey) {
    console.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
    return false;
  }

  const columns = [
    "ADD COLUMN IF NOT EXISTS country TEXT",
    "ADD COLUMN IF NOT EXISTS city TEXT",
    "ADD COLUMN IF NOT EXISTS timezone TEXT",
    "ADD COLUMN IF NOT EXISTS profile_earnings_badge TEXT",
    "ADD COLUMN IF NOT EXISTS profile_earnings_usd NUMERIC",
  ];

  // Try using PostgREST RPC with a custom function, or just test if columns exist first
  const { data: testRow } = await supabaseAdmin
    .from("leads")
    .select("country, city, timezone, profile_earnings_badge, profile_earnings_usd")
    .limit(1);

  if (testRow !== null) {
    console.log("✓ Columns already exist in leads table");
    return true;
  }

  console.log("Columns not found, creating them via SQL API...");
  const sql = `ALTER TABLE leads ${columns.join(",\n  ")};`;
  
  const res = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
    method: "POST",
    headers: {
      "apikey": serviceKey,
      "Authorization": `Bearer ${serviceKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ sql }),
  });

  if (!res.ok) {
    const body = await res.text();
    console.error("SQL exec failed:", body);
    return false;
  }

  console.log("✓ Columns created successfully!");
  return true;
}

async function batchEnrich() {
  const ok = await addColumnsViaSQL();
  if (!ok) {
    console.log("Proceeding with enrichment anyway (will store in scraped_data if columns missing)");
  }

  // Fetch all leads
  const { data: leads, error } = await supabaseAdmin
    .from("leads")
    .select("id, whop_username, whop_user_id, country, profile_earnings_badge")
    .order("created_at", { ascending: false });

  if (error || !leads) {
    return console.error("Failed to fetch leads:", error);
  }

  console.log(`\nTotal leads: ${leads.length}`);

  // Only enrich those missing country OR earnings
  const toEnrich = leads.filter(l => !l.country || !l.profile_earnings_badge);
  console.log(`Needs enrichment: ${toEnrich.length}`);

  if (toEnrich.length === 0) {
    console.log("All leads already enriched! ✓");
    return;
  }

  let enriched = 0;
  let failed = 0;
  const BATCH_SIZE = 5;

  for (let i = 0; i < toEnrich.length; i += BATCH_SIZE) {
    const batch = toEnrich.slice(i, i + BATCH_SIZE);
    
    await Promise.all(batch.map(async (lead) => {
      try {
        const username = lead.whop_username || null;
        const userId = lead.whop_user_id || null;

        if (!username && !userId) return;

        const [loc, earnings] = await Promise.all([
          resolveWhopLocation(userId, username, lead.country),
          getWhopProfileEarnings(username),
        ]);

        const updateData: Record<string, any> = {};
        if (loc.country && !lead.country) updateData.country = loc.country;
        if (loc.city) updateData.city = loc.city;
        if (loc.timezone) updateData.timezone = loc.timezone;
        if (earnings.badge && !lead.profile_earnings_badge) {
          updateData.profile_earnings_badge = earnings.badge;
          if (earnings.exact_usd) updateData.profile_earnings_usd = earnings.exact_usd;
        }

        if (Object.keys(updateData).length > 0) {
          const { error: updateError } = await supabaseAdmin
            .from("leads")
            .update(updateData)
            .eq("id", lead.id);

          if (updateError) {
            if (updateError.message.includes("does not exist")) {
              // Columns don't exist — store in scraped_data.enrichment
              const { data: row } = await supabaseAdmin
                .from("leads")
                .select("scraped_data")
                .eq("id", lead.id)
                .single();
              const existing = (row?.scraped_data as any) || {};
              const merged = { ...existing, enrichment: updateData };
              await supabaseAdmin
                .from("leads")
                .update({ scraped_data: merged })
                .eq("id", lead.id);
              console.log(`  [${lead.id}] Stored in scraped_data (columns missing)`);
            } else {
              throw updateError;
            }
          }
          enriched++;
          if (enriched % 25 === 0) console.log(`  Progress: ${enriched}/${toEnrich.length}`);
        }
      } catch (e: any) {
        failed++;
        if (failed <= 5) console.warn(`  ✗ ${lead.id}: ${String(e?.message).slice(0, 80)}`);
      }
    }));

    // Small delay between batches to avoid rate limiting
    if (i + BATCH_SIZE < toEnrich.length) {
      await new Promise(r => setTimeout(r, 300));
    }
  }

  console.log(`\n✓ Done!`);
  console.log(`  Enriched: ${enriched}`);
  console.log(`  Failed/skipped: ${failed}`);
  console.log(`  Already had data: ${leads.length - toEnrich.length}`);
}

batchEnrich().catch(console.error);
