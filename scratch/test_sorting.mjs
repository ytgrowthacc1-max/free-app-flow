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

async function testSorting() {
  const urls = [
    "https://api.whop.com/api/v5/company/payments?per=5",
    "https://api.whop.com/api/v5/company/payments?per=5&direction=desc",
    "https://api.whop.com/api/v5/company/payments?per=5&order=desc",
    "https://api.whop.com/api/v5/company/payments?per=5&sort=created_at_desc",
  ];

  for (const u of urls) {
    const res = await fetch(u, { headers: { "Authorization": `Bearer ${WHOP_API_KEY}` } });
    if (res.ok) {
      const json = await res.json();
      console.log(`\nURL: ${u}`);
      console.log("Total count:", json.pagination?.total_count);
      for (const p of json.data || []) {
        console.log(`- ID: ${p.id} | User: @${p.user_username} | Created: ${new Date(p.created_at * 1000).toISOString()}`);
      }
    }
  }
}

testSorting();
