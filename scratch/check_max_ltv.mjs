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

async function inspectAllLeadsData() {
  const { supabaseAdmin } = await import("../src/lib/leads.server.js");
  const { data: leads, error } = await supabaseAdmin.from("leads").select("*");
  if (error) {
    console.error("Supabase error:", error);
    return;
  }

  const { enrichLeadsWithLocation } = await import("../src/lib/location.server.js");
  const enriched = await enrichLeadsWithLocation(leads);

  let maxLtv = 0;
  const ltvLeads = [];

  for (const l of enriched) {
    const ltv = typeof l.ltv === "number" ? l.ltv : 0;
    if (ltv > maxLtv) maxLtv = ltv;
    if (ltv >= 10) ltvLeads.push(l);
  }

  console.log(`Max LTV found: $${maxLtv}`);
  console.log(`Leads with LTV >= 10: ${ltvLeads.length}`);
  if (ltvLeads.length > 0) {
    console.log("Leads with LTV:", ltvLeads.map(l => ({ name: l.first_name, username: l.whop_username, ltv: l.ltv })));
  }
}

inspectAllLeadsData();
