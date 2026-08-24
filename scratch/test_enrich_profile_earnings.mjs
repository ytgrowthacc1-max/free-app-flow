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

async function testEnrich() {
  const { supabaseAdmin } = await import("../src/lib/leads.server.js");
  const { data: leads } = await supabaseAdmin.from("leads").select("*").limit(20);

  const { enrichLeadsWithLocation } = await import("../src/lib/location.server.js");
  const enriched = await enrichLeadsWithLocation(leads);

  console.log("Enriched leads sample:");
  for (const l of enriched) {
    if (l.whop_username) {
      console.log(`@${l.whop_username}: MRR=$${l.mrr}, Profile Earnings Badge=${l.profile_earnings_badge || 'None'}, USD=${l.profile_earnings_usd}`);
    }
  }
}

testEnrich();
