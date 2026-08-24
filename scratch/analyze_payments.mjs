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

async function fetchPayments(queryParams = "") {
  const url = `https://api.whop.com/api/v5/payments${queryParams ? `?${queryParams}` : ""}`;
  const res = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    }
  });
  if (!res.ok) {
    console.error(`Failed ${url}: ${res.status} ${await res.text()}`);
    return null;
  }
  return await res.json();
}

async function analyze() {
  console.log("=== 1. ALL PAYMENTS (recent) ===");
  const allPayments = await fetchPayments("per=50");
  if (allPayments) {
    console.log(`Total returned in first page: ${allPayments.data?.length || 0}`);
    console.log("Pagination info:", allPayments.pagination);
    const statusCounts = {};
    for (const p of allPayments.data || []) {
      const st = p.status || "unknown";
      statusCounts[st] = (statusCounts[st] || 0) + 1;
    }
    console.log("Status distribution:", statusCounts);
    console.log("\nSample payments (summary):");
    for (const p of (allPayments.data || []).slice(0, 10)) {
      console.log(`- ID: ${p.id} | User: @${p.user_username || "N/A"} (${p.user_id}) | Email: ${p.user_email} | Status: ${p.status} | Amount: ${p.final_amount} | Created: ${new Date(p.created_at * 1000).toISOString()}`);
    }
  }

  console.log("\n=== 2. QUERYING INCOMPLETE / FAILED PAYMENTS ===");
  const substatusQuery = "substatuses[]=incomplete&substatuses[]=failed";
  const substatusPayments = await fetchPayments(substatusQuery);
  if (substatusPayments) {
    console.log(`Results for ${substatusQuery}: ${substatusPayments.data?.length || 0} payments`);
    for (const p of substatusPayments.data || []) {
      console.log(`- ID: ${p.id} | User: @${p.user_username} (${p.user_id}) | Email: ${p.user_email} | Status: ${p.status} | Reason: ${p.billing_reason} | Failed Count: ${p.payments_failed} | Created: ${new Date(p.created_at * 1000).toISOString()}`);
    }
  }

  console.log("\n=== 3. QUERYING EACH STATUS SEPARATELY ===");
  const testSubstatuses = ["incomplete", "failed", "past_due", "trialing", "paid", "refunded", "voided", "unpaid"];
  for (const s of testSubstatuses) {
    const res = await fetchPayments(`substatuses[]=${s}`);
    console.log(`substatuses[]=${s} -> ${res?.data?.length ?? "ERR"} payments`);
    if (res?.data?.length > 0 && s !== "paid") {
      console.log(`Details for ${s}:`, JSON.stringify(res.data.map(p => ({
        id: p.id,
        user_id: p.user_id,
        username: p.user_username,
        email: p.user_email,
        status: p.status,
        created_at: new Date(p.created_at * 1000).toISOString()
      })), null, 2));
    }
  }
}

analyze();
