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

async function fetchAll(endpoint) {
  let page = 1;
  const all = [];
  const statusCounts = {};
  const substatusCounts = {};
  
  while (page <= 10) { // check first 10 pages (e.g. 500 payments)
    const res = await fetch(`${endpoint}?per=50&page=${page}`, {
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      }
    });
    if (!res.ok) {
      console.error(`Page ${page} failed: ${res.status}`);
      break;
    }
    const json = await res.json();
    const data = json.data || [];
    if (data.length === 0) break;
    
    for (const p of data) {
      all.push(p);
      statusCounts[p.status] = (statusCounts[p.status] || 0) + 1;
      if (p.substatus || p.substatuses) {
        substatusCounts[p.substatus || p.substatuses] = (substatusCounts[p.substatus || p.substatuses] || 0) + 1;
      }
    }
    
    if (page >= json.pagination.total_pages) break;
    page++;
  }
  
  return { all, statusCounts, substatusCounts };
}

async function run() {
  console.log("Fetching company payments (up to 500 items)...");
  const comp = await fetchAll("https://api.whop.com/api/v5/company/payments");
  console.log(`Fetched ${comp.all.length} company payments.`);
  console.log("Status distribution:", comp.statusCounts);
  console.log("Substatus distribution:", comp.substatusCounts);

  const nonPaid = comp.all.filter(p => p.status !== "paid");
  console.log(`Non-paid payments count: ${nonPaid.length}`);
  if (nonPaid.length > 0) {
    console.log("Non-paid payments:", JSON.stringify(nonPaid, null, 2));
  } else {
    console.log("Sample of recent payments:", comp.all.slice(0, 3).map(p => ({
      id: p.id,
      user: p.user_username,
      email: p.user_email,
      status: p.status,
      final_amount: p.final_amount,
      payments_failed: p.payments_failed,
      created_at: new Date(p.created_at * 1000).toISOString()
    })));
  }

  // Also check if there are any failed payments in app/payments
  console.log("\nFetching app payments (up to 500 items)...");
  const app = await fetchAll("https://api.whop.com/api/v5/app/payments");
  console.log(`Fetched ${app.all.length} app payments.`);
  console.log("Status distribution:", app.statusCounts);
  const appNonPaid = app.all.filter(p => p.status !== "paid");
  console.log(`App Non-paid payments count: ${appNonPaid.length}`);
  if (appNonPaid.length > 0) {
    console.log("App non-paid payments:", JSON.stringify(appNonPaid.slice(0, 5), null, 2));
  }
}

run();
