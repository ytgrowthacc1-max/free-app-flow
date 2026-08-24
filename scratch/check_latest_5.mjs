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

const WHOP_API_KEY = process.env.WHOP_API_KEY;

async function checkRecentWhopPayments() {
  const res = await fetch("https://api.whop.com/api/v5/company/payments?per=50", {
    headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
  });
  const json = await res.json();
  const totalPages = json.pagination?.total_pages || 1;
  
  const lastPageRes = await fetch(`https://api.whop.com/api/v5/company/payments?per=50&page=${totalPages}`, {
    headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
  });
  const lastJson = await lastPageRes.json();
  const payments = lastJson.data || [];

  console.log(`Total count: ${lastJson.pagination?.total_count}`);
  console.log("Latest 5 payments on Whop:");
  for (const p of payments.slice(-5)) {
    console.log(`- ID: ${p.id} | User: @${p.user_username} (${p.user_id}) | Status: ${p.status} | Failed Attempts: ${p.payments_failed} | Created: ${new Date(p.created_at * 1000).toISOString()}`);
  }
}

checkRecentWhopPayments();
