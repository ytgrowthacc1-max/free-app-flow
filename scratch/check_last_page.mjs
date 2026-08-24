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

async function checkLastPages() {
  // First get total pages
  const initRes = await fetch("https://api.whop.com/api/v5/company/payments?per=50", {
    headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
  });
  const initJson = await initRes.json();
  const totalPages = initJson.pagination?.total_pages || 1;
  console.log(`Total count: ${initJson.pagination?.total_count}, Total pages: ${totalPages}`);

  for (let p = Math.max(1, totalPages - 1); p <= totalPages; p++) {
    const res = await fetch(`https://api.whop.com/api/v5/company/payments?per=50&page=${p}`, {
      headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
    });
    if (res.ok) {
      const json = await res.json();
      console.log(`\n=== PAGE ${p} ===`);
      for (const item of json.data || []) {
        console.log(`- ID: ${item.id} | User: @${item.user_username} (${item.user_id}) | Email: ${item.user_email} | Status: ${item.status} | Created: ${new Date(item.created_at * 1000).toISOString()}`);
      }
    }
  }
}

checkLastPages();
