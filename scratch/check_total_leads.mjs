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

async function checkTotalLeads() {
  const { count, error } = await supabase.from("leads").select("*", { count: "exact", head: true });
  console.log("Total exact leads count in DB:", count, "Error:", error);
  
  const { count: hotCount } = await supabase.from("leads").select("*", { count: "exact", head: true }).eq("lead_tag", "HOT");
  const { count: warmCount } = await supabase.from("leads").select("*", { count: "exact", head: true }).eq("lead_tag", "WARM");
  const { count: coldCount } = await supabase.from("leads").select("*", { count: "exact", head: true }).eq("lead_tag", "COLD");
  const { count: completedCount } = await supabase.from("leads").select("*", { count: "exact", head: true }).eq("completed", true);

  console.log("Stats breakdown:", {
    total: count,
    hot: hotCount,
    warm: warmCount,
    cold: coldCount,
    completed: completedCount,
    incomplete: (count || 0) - (completedCount || 0)
  });
}

checkTotalLeads();
