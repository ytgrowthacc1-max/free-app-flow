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

import { supabaseAdmin, calcLeadScore } from "../src/lib/leads.server.js";

async function rescoreAllLeads() {
  console.log("=== Rescoring All Database Leads with New Valuation System ===");

  let allLeads: any[] = [];
  let page = 0;
  const pageSize = 1000;

  while (true) {
    const { data, error } = await supabaseAdmin
      .from("leads")
      .select("id, member_count, monthly_price, timeline, country, profile_earnings_badge, profile_earnings_usd, lead_score, lead_tag")
      .range(page * pageSize, (page + 1) * pageSize - 1);

    if (error) {
      console.error("Supabase select error:", error);
      break;
    }
    if (!data || data.length === 0) break;
    allLeads = allLeads.concat(data);
    if (data.length < pageSize) break;
    page++;
  }

  console.log(`Total leads retrieved: ${allLeads.length}`);

  let updated = 0;
  let hotCount = 0;
  let warmCount = 0;
  let coldCount = 0;

  const CONCURRENCY = 20;
  for (let i = 0; i < allLeads.length; i += CONCURRENCY) {
    const chunk = allLeads.slice(i, i + CONCURRENCY);

    await Promise.all(
      chunk.map(async (lead) => {
        const res = calcLeadScore({
          memberCount: Number(lead.member_count || 0),
          monthlyPrice: Number(lead.monthly_price || 0),
          timeline: lead.timeline,
          country: lead.country,
          profileEarningsBadge: lead.profile_earnings_badge,
          profileEarningsUsd: lead.profile_earnings_usd ? Number(lead.profile_earnings_usd) : null,
          ltv: lead.ltv ? Number(lead.ltv) : null,
        });

        if (res.tag === "HOT") hotCount++;
        else if (res.tag === "WARM") warmCount++;
        else coldCount++;

        if (res.score !== lead.lead_score || res.tag !== lead.lead_tag) {
          await supabaseAdmin
            .from("leads")
            .update({ lead_score: res.score, lead_tag: res.tag })
            .eq("id", lead.id);
          updated++;
        }
      })
    );
  }

  console.log(`\n=== Rescore Complete ===`);
  console.log(`Total Leads Updated: ${updated}`);
  console.log(`Breakdown: HOT: ${hotCount} 🔥 | WARM: ${warmCount} 🌤️ | COLD: ${coldCount} ❄️`);
}

rescoreAllLeads().catch(console.error);
