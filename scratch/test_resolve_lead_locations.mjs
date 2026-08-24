import { createClient } from "@supabase/supabase-js";
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

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function run() {
  const { data: leads } = await supabase.from("leads").select("*").order("created_at", { ascending: false }).limit(50);
  console.log("Total leads fetched:", leads?.length);
  
  let withLocation = 0;
  let withoutLocation = 0;
  let noWhopInfo = 0;

  for (const lead of leads) {
    const loc = lead.scraped_data?.location;
    const hasScrapedLoc = Boolean(loc?.country);
    const hasLeadCountry = Boolean(lead.country);
    const hasWhopUser = Boolean(lead.whop_user_id || (lead.whop_username && !['unknown', 'anonymous', '@username'].includes(lead.whop_username.toLowerCase())));

    if (hasScrapedLoc || hasLeadCountry) {
      withLocation++;
    } else if (!hasWhopUser) {
      noWhopInfo++;
      withoutLocation++;
    } else {
      withoutLocation++;
    }
  }

  console.log("Leads with stored/scraped location:", withLocation);
  console.log("Leads without location:", withoutLocation);
  console.log("Leads without any Whop account info:", noWhopInfo);
}

run();
