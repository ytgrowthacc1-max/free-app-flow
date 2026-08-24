import fs from "fs";
import path from "path";
import { createClient } from "@supabase/supabase-js";

const envPath = path.resolve(".env");
if (fs.existsSync(envPath)) {
  const content = fs.readFileSync(envPath, "utf-8");
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf("=");
    if (idx > 0) {
      const k = trimmed.slice(0, idx).trim();
      let v = trimmed.slice(idx + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      process.env[k] = v;
    }
  }
}

const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function testFullFlow() {
  const { enrichLeadsWithLocation } = await import("../src/lib/location.server.js").catch(async () => {
    // In ESM .ts, dynamically load or test
    return await import("../dist/server/index.js").catch(() => ({}));
  });

  const { data: rows } = await supabase.from("leads").select("*").order("created_at", { ascending: false }).limit(10);
  console.log(`Fetched ${rows?.length} leads from Supabase.`);

  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;

  const res = await fetch(`https://api.whop.com/api/v1/people?company_id=${companyId}&first=100`, {
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" }
  });
  const people = (await res.json()).data || [];

  const byUname = new Map();
  const byUid = new Map();
  for (const p of people) {
    const loc = {
      country: p.location?.country,
      city: p.location?.city,
      timezone: p.timezone
    };
    if (p.user?.id) byUid.set(p.user.id, loc);
    if (p.user?.username) byUname.set(p.user.username.toLowerCase(), loc);
  }

  console.log("\nEnriched Dashboard Leads Preview:");
  for (const lead of rows || []) {
    const uname = (lead.whop_username || "").toLowerCase().replace(/^@/, "").trim();
    const loc = byUid.get(lead.whop_user_id) || byUname.get(uname);
    const countryCode = loc?.country || "—";
    const city = loc?.city || "";
    console.log(`- [${lead.lead_tag}] ${lead.first_name} (@${lead.whop_username}) | Country: ${countryCode} | City: ${city} | MRR: $${lead.mrr}`);
  }
}

testFullFlow();
