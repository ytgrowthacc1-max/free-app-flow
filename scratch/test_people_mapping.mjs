import { createClient } from "@supabase/supabase-js";
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

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function run() {
  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;

  // Fetch all Whop people (up to 300)
  const byUserId = new Map();
  const byUsername = new Map();

  let after = null;
  let pageCount = 0;
  while (true) {
    let url = `https://api.whop.com/api/v1/people?company_id=${companyId}&first=100`;
    if (after) url += `&after=${after}`;
    const res = await fetch(url, { headers: { Authorization: `Bearer ${apiKey}` } });
    if (!res.ok) break;
    const json = await res.json();
    for (const p of json.data || []) {
      const loc = p.location;
      if (p.user?.id) byUserId.set(p.user.id, loc);
      if (p.id) byUserId.set(p.id, loc);
      if (p.user?.username) byUsername.set(p.user.username.toLowerCase().replace(/^@/, "").trim(), loc);
      if (p.name) byUsername.set(p.name.toLowerCase().replace(/^@/, "").trim(), loc);
    }
    if (!json.page_info?.has_next_page || !json.page_info?.end_cursor) break;
    after = json.page_info.end_cursor;
    pageCount++;
  }

  console.log(`Indexed ${byUserId.size} Whop user IDs and ${byUsername.size} usernames.`);

  const { data: leads, error: leadsErr } = await supabase.from("leads").select("id, first_name, email, whop_username, whop_user_id, scraped_data").order("created_at", { ascending: false }).limit(50);
  if (leadsErr) {
    console.error("Supabase leads error:", leadsErr);
    return;
  }
  let matched = 0;
  let missing = 0;
  const leadsList = leads || [];
  for (const l of leadsList) {
    const uid = l.whop_user_id;
    const uname = l.whop_username ? l.whop_username.toLowerCase().replace(/^@/, "").trim() : "";
    
    let loc = null;
    if (uid && byUserId.has(uid)) loc = byUserId.get(uid);
    else if (uname && uname !== "unknown" && uname !== "anonymous" && byUsername.has(uname)) loc = byUsername.get(uname);

    if (loc?.country) {
      matched++;
      console.log(`✅ MATCH: ${l.first_name} (@${l.whop_username || l.whop_user_id}) -> ${loc.country} ${loc.city || ''}`);
    } else {
      missing++;
      console.log(`❌ NO MATCH: ${l.first_name} (Username: "${l.whop_username}", UserID: "${l.whop_user_id}")`);
    }
  }

  console.log(`\nSummary: Matched ${matched}/${leads.length} leads to real-time Whop location data.`);
}

run();
