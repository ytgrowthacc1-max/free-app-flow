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

async function testSupportChannel() {
  const whopApiKey = process.env.WHOP_API_KEY;
  const whopCompanyId = process.env.WHOP_COMPANY_ID;

  console.log("Testing support channel API...", { hasApiKey: !!whopApiKey, companyId: whopCompanyId });

  // Get a lead with whop_user_id
  const { data: leads } = await supabaseAdmin
    .from("leads")
    .select("id, whop_username, whop_user_id, scraped_data")
    .not("whop_user_id", "is", null)
    .limit(3);

  console.log(`Found ${leads?.length || 0} leads with whop_user_id`);

  for (const lead of leads || []) {
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

      console.log(`Lead @${lead.whop_username} (${lead.whop_user_id}) -> Status ${channelRes.status}`);
      if (channelRes.ok) {
        const channelData = await channelRes.json();
        console.log(`  Support Channel ID: ${channelData.id} -> https://whop.com/messages/?chat=${channelData.id}`);
      } else {
        const errText = await channelRes.text();
        console.log(`  Error: ${errText}`);
      }
    } catch (e: any) {
      console.error("  Exception:", e.message);
    }
  }
}

testSupportChannel().catch(console.error);
