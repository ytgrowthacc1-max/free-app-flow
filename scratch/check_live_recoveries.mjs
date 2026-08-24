import { createClient } from "@supabase/supabase-js";
import fs from "fs";
import path from "path";

// Load .env
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

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const WHOP_API_KEY = process.env.WHOP_API_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false },
});

async function checkLiveStatus() {
  console.log("=== 1. Checking Supabase payment_recoveries records ===");
  const { data: recoveries, error } = await supabase
    .from("payment_recoveries")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(10);

  if (error) {
    console.error("DB error:", error);
  } else {
    console.log(`Found ${recoveries?.length || 0} recovery record(s):`);
    for (const r of recoveries || []) {
      console.log(`- [${r.created_at}] User: @${r.whop_username} (${r.whop_user_id}) | Payment: ${r.payment_id} | Status: ${r.status} | Mode: ${r.failure_mode} | Sent: ${r.message_sent}`);
      console.log(`  Message: "${r.message_content}"`);
    }
  }

  console.log("\n=== 2. Checking Whop API for latest payments ===");
  const res = await fetch(`https://api.whop.com/api/v5/company/payments?per=10`, {
    headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
  });
  if (res.ok) {
    const data = await res.json();
    const payments = data.data || [];
    console.log(`Latest ${payments.length} payment(s) from Whop API:`);
    for (const p of payments) {
      console.log(`- ID: ${p.id} | User: @${p.user_username} (${p.user_id}) | Email: ${p.user_email} | Status: ${p.status} | Failed Attempts: ${p.payments_failed} | Paid: ${!!p.paid_at} | Created: ${new Date(p.created_at * 1000).toISOString()}`);
    }
  } else {
    console.error("Whop API error:", res.status);
  }
}

checkLiveStatus();
