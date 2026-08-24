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

async function checkLeadsColumns() {
  const { supabaseAdmin } = await import("../src/lib/leads.server.js");
  const { data, error } = await supabaseAdmin.from("leads").select("*").limit(1).single();
  if (error) return console.error(error);
  console.log("Available columns in leads table:");
  console.log(Object.keys(data).join(", "));
  console.log("\nColumn values for first row:");
  for (const [k, v] of Object.entries(data)) {
    if (v !== null && v !== undefined && v !== "") {
      console.log(`  ${k}: ${JSON.stringify(v)?.slice(0, 80)}`);
    }
  }
}

checkLeadsColumns();
