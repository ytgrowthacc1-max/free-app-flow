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

/**
 * Adds country, city, timezone, profile_earnings_badge, profile_earnings_usd columns to the leads table
 * using Supabase's RPC to run raw SQL, then batch-enriches all existing leads.
 */
async function addColumnsAndEnrich() {
  const { supabaseAdmin } = await import("../src/lib/leads.server.js");

  // Step 1: Add missing columns via raw SQL
  console.log("Adding new columns to leads table...");
  const alterSQL = `
    ALTER TABLE leads
      ADD COLUMN IF NOT EXISTS country TEXT,
      ADD COLUMN IF NOT EXISTS city TEXT,
      ADD COLUMN IF NOT EXISTS timezone TEXT,
      ADD COLUMN IF NOT EXISTS profile_earnings_badge TEXT,
      ADD COLUMN IF NOT EXISTS profile_earnings_usd NUMERIC;
  `;
  const { error: alterError } = await supabaseAdmin.rpc("exec_sql", { sql: alterSQL }).single();
  if (alterError) {
    console.error("RPC exec_sql not available, trying direct approach:", alterError.message);
    // Try individual columns via update instead
    console.log("Will proceed with batch update using scraped_data JSONB column as fallback...");
  } else {
    console.log("✓ Columns added successfully!");
  }

  // Step 2: Fetch all leads
  console.log("Fetching all leads...");
  const { data: leads, error: leadsError } = await supabaseAdmin
    .from("leads")
    .select("id, whop_username, whop_user_id, country, profile_earnings_badge");

  if (leadsError || !leads) return console.error("Failed to fetch leads:", leadsError);
  console.log(`Found ${leads.length} total leads`);

  // Filter leads that need enrichment
  const toEnrich = leads.filter(l => !l.country || !l.profile_earnings_badge);
  console.log(`Leads needing enrichment: ${toEnrich.length}`);

  // Import location utils
  const { resolveWhopLocation, getWhopProfileEarnings } = await import("../src/lib/location.server.js");

  let enriched = 0;
  let failed = 0;

  // Process in batches of 10 to avoid overwhelming Whop
  const BATCH_SIZE = 10;
  for (let i = 0; i < toEnrich.length; i += BATCH_SIZE) {
    const batch = toEnrich.slice(i, i + BATCH_SIZE);
    
    await Promise.all(batch.map(async (lead) => {
      try {
        const username = lead.whop_username || null;
        const userId = lead.whop_user_id || null;

        // Fetch location and earnings in parallel
        const [loc, earnings] = await Promise.all([
          resolveWhopLocation(userId, username),
          getWhopProfileEarnings(username),
        ]);

        const updateData: any = {};
        if (loc.country && !lead.country) {
          updateData.country = loc.country;
          updateData.city = loc.city || null;
          updateData.timezone = loc.timezone || null;
        }
        if (earnings.badge && !lead.profile_earnings_badge) {
          updateData.profile_earnings_badge = earnings.badge;
          updateData.profile_earnings_usd = earnings.exact_usd || null;
        }

        if (Object.keys(updateData).length > 0) {
          const { error } = await supabaseAdmin.from("leads").update(updateData).eq("id", lead.id);
          if (error) {
            if (error.message.includes("column") && error.message.includes("does not exist")) {
              // Columns don't exist yet, store in scraped_data
              const { data: existing } = await supabaseAdmin.from("leads").select("scraped_data").eq("id", lead.id).single();
              const mergedData = { ...(existing?.scraped_data as any || {}), ...updateData };
              await supabaseAdmin.from("leads").update({ scraped_data: mergedData }).eq("id", lead.id);
            } else {
              throw error;
            }
          }
          enriched++;
          if (enriched % 50 === 0) console.log(`  Progress: ${enriched} enriched...`);
        }
      } catch (e: any) {
        failed++;
        console.warn(`  Failed for lead ${lead.id}:`, e.message?.slice(0, 80));
      }
    }));
  }

  console.log(`\n✓ Batch enrichment complete!`);
  console.log(`  Enriched: ${enriched}`);
  console.log(`  Failed: ${failed}`);
  console.log(`  Skipped (already enriched): ${toEnrich.length - enriched - failed}`);
}

addColumnsAndEnrich();
