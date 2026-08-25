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

async function run() {
  const apiKey = process.env.WHOP_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;
  if (!apiKey || !companyId) return;

  const { data: rows } = await supabaseAdmin
    .from("leads")
    .select("id, whop_user_id, scraped_data")
    .not("whop_user_id", "is", null);

  console.log(`Checking ${rows?.length ?? 0} leads for support channels...`);
  let count = 0;

  for (const r of rows ?? []) {
    const existing = typeof r.scraped_data === "object" && r.scraped_data !== null ? r.scraped_data : {};
    if ((existing as any).support_channel_id) continue;

    try {
      const res = await fetch("https://api.whop.com/api/v1/support_channels", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ company_id: companyId, user_id: r.whop_user_id }),
      });
      if (res.ok) {
        const d = await res.json();
        if (d.id) {
          await supabaseAdmin
            .from("leads")
            .update({ scraped_data: { ...existing, support_channel_id: d.id } })
            .eq("id", r.id);
          count++;
        }
      }
    } catch {
      // ignore
    }
    // Small delay to prevent rate limits
    await new Promise((res) => setTimeout(res, 50));
  }

  console.log(`Enriched ${count} additional leads with support channels.`);
}

run().catch(console.error);
