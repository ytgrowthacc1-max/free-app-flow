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
  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;
  console.log("Testing Whop API key:", Boolean(apiKey), "Company ID:", companyId);

  const res = await fetch(`https://api.whop.com/api/v1/people?company_id=${companyId}&first=50`, {
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    console.error("Whop API error:", res.status, await res.text());
    return;
  }

  const json = await res.json();
  const people = json.data || [];
  console.log("Fetched people from Whop API:", people.length);
  
  const peopleWithLoc = people.filter(p => p.location?.country || p.location?.city);
  console.log("People with location in Whop:", peopleWithLoc.length);
  if (peopleWithLoc.length > 0) {
    console.log("Sample Whop location data:", peopleWithLoc.slice(0, 3).map(p => ({ id: p.id, user_id: p.user?.id, username: p.user?.username, loc: p.location })));
  }
}

run();
