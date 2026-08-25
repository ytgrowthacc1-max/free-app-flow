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

async function enrichSupportChannels() {
  const whopApiKey = process.env.WHOP_API_KEY;
  const whopCompanyId = process.env.WHOP_COMPANY_ID;

  if (!whopApiKey || !whopCompanyId) {
    console.error("Missing WHOP_API_KEY or WHOP_COMPANY_ID in env.");
    return;
  }

  console.log("=== Enriching Database Leads with Whop Support Channel IDs ===");

  let allLeads: any[] = [];
  let page = 0;
  const pageSize = 1000;

  while (true) {
    const { data, error } = await supabaseAdmin
      .from("leads")
      .select("id, whop_user_id, whop_username, scraped_data")
      .not("whop_user_id", "is", null)
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

  console.log(`Total leads with whop_user_id: ${allLeads.length}`);

  let updatedCount = 0;
  let skippedCount = 0;

  const CONCURRENCY = 10;
  for (let i = 0; i < allLeads.length; i += CONCURRENCY) {
    const chunk = allLeads.slice(i, i + CONCURRENCY);

    await Promise.all(
      chunk.map(async (lead) => {
        const existingData = typeof lead.scraped_data === "object" && lead.scraped_data !== null ? lead.scraped_data : {};
        if (existingData.support_channel_id) {
          skippedCount++;
          return;
        }

        try {
          const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${whopApiKey}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              company_id: whopCompanyId,
              user_id: lead.whop_user_id,
            }),
          });

          if (channelRes.ok) {
            const channelData = await channelRes.json();
            const channelId = channelData.id;
            if (channelId) {
              const updatedData = { ...existingData, support_channel_id: channelId };
              await supabaseAdmin
                .from("leads")
                .update({ scraped_data: updatedData })
                .eq("id", lead.id);
              updatedCount++;
            }
          }
        } catch (e: any) {
          console.error(`Failed channel lookup for @${lead.whop_username}:`, e.message);
        }
      })
    );

    if ((i + CONCURRENCY) % 50 === 0 || i + CONCURRENCY >= allLeads.length) {
      console.log(`Processed ${Math.min(i + CONCURRENCY, allLeads.length)} / ${allLeads.length} leads... (Updated: ${updatedCount}, Skipped: ${skippedCount})`);
    }
  }

  console.log(`\n=== Support Channel ID Enrichment Complete ===`);
  console.log(`Updated: ${updatedCount} | Skipped: ${skippedCount} | Total: ${allLeads.length}`);
}

enrichSupportChannels().catch(console.error);
