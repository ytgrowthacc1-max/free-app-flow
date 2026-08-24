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

async function testAdmin() {
  try {
    const { supabaseAdmin } = await import("../src/lib/leads.server");
    const { data: rows, error } = await supabaseAdmin.from("leads").select("*").order("created_at", { ascending: false }).limit(50);
    console.log("Supabase error:", error);
    console.log("Leads count:", rows?.length);

    const { enrichLeadsWithLocation } = await import("../src/lib/location.server");
    console.log("Enriching leads...");
    const enriched = await enrichLeadsWithLocation(rows || []);
    console.log("Enriched sample lead keys:", Object.keys(enriched[0] || {}));
    console.log("Sample lead LTV & Country:", enriched[0]?.country, enriched[0]?.ltv);
  } catch (err) {
    console.error("EXPLICIT TEST ERROR TRACE:", err);
  }
}

testAdmin();
