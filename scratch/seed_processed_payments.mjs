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

async function seedProcessedHistoricalPayments() {
  console.log("Fetching existing payments to mark past historical transactions...");
  let page = 1;
  const pastPaymentIds = [];

  while (true) {
    const res = await fetch(`https://api.whop.com/api/v5/company/payments?per=50&page=${page}`, {
      headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
    });
    if (!res.ok) break;
    const json = await res.json();
    const list = json.data || [];
    if (list.length === 0) break;
    for (const p of list) {
      pastPaymentIds.push(p.id);
    }
    if (page >= json.pagination.total_pages) break;
    page++;
  }

  console.log(`Fetched ${pastPaymentIds.length} historical payments.`);
  
  // Save to local processed_payments.json
  const PROCESSED_PAYMENTS_FILE = path.join(process.cwd(), ".tmp", "processed_payments.json");
  fs.mkdirSync(path.dirname(PROCESSED_PAYMENTS_FILE), { recursive: true });
  fs.writeFileSync(PROCESSED_PAYMENTS_FILE, JSON.stringify(pastPaymentIds, null, 2), "utf-8");
  console.log(`Saved ${pastPaymentIds.length} IDs to ${PROCESSED_PAYMENTS_FILE}`);
}

seedProcessedHistoricalPayments();
