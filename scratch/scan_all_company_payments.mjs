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

const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;

async function run() {
  let page = 1;
  const allNonPaid = [];
  const statusSummary = {};

  while (true) {
    const res = await fetch(`https://api.whop.com/api/v5/company/payments?per=50&page=${page}`, {
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      }
    });
    if (!res.ok) {
      console.error(`Page ${page} error: ${res.status}`);
      break;
    }
    const json = await res.json();
    const list = json.data || [];
    if (list.length === 0) break;

    for (const p of list) {
      statusSummary[p.status] = (statusSummary[p.status] || 0) + 1;
      if (p.status !== "paid" || p.payments_failed > 0 || p.paid_at === null) {
        allNonPaid.push({
          id: p.id,
          user_id: p.user_id,
          user_username: p.user_username,
          user_email: p.user_email,
          status: p.status,
          paid_at: p.paid_at,
          payments_failed: p.payments_failed,
          final_amount: p.final_amount,
          currency: p.currency,
          payment_method_type: p.payment_method_type,
          billing_reason: p.billing_reason,
          created_at: new Date(p.created_at * 1000).toISOString(),
          last_payment_attempt: p.last_payment_attempt ? new Date(p.last_payment_attempt * 1000).toISOString() : null,
        });
      }
    }

    if (page >= json.pagination.total_pages) break;
    page++;
  }

  console.log("Total Company Payments analyzed across all pages:", Object.values(statusSummary).reduce((a,b)=>a+b, 0));
  console.log("Status distribution:", statusSummary);
  console.log(`Found ${allNonPaid.length} incomplete / failed / open payments:`);
  console.log(JSON.stringify(allNonPaid, null, 2));
}

run();
