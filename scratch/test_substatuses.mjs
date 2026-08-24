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

async function checkEndpoint(url) {
  try {
    const res = await fetch(url, {
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      }
    });
    console.log(`[${res.status}] ${url}`);
    if (res.ok) {
      const data = await res.json();
      console.log(`  -> Pagination:`, data.pagination, `Count in page:`, data.data?.length);
      return data;
    } else {
      console.log(`  -> Error:`, await res.text());
    }
  } catch (err) {
    console.error(`Error calling ${url}:`, err.message);
  }
  return null;
}

async function run() {
  console.log("=== Testing Company Payments & Substatuses ===");
  
  // 1. Check company payments pagination & substatus filter
  await checkEndpoint("https://api.whop.com/api/v5/company/payments?per=20");
  await checkEndpoint("https://api.whop.com/api/v5/company/payments?substatuses[]=incomplete&substatuses[]=failed");
  await checkEndpoint("https://api.whop.com/api/v5/company/payments?substatuses[]=incomplete");
  await checkEndpoint("https://api.whop.com/api/v5/company/payments?substatuses[]=failed");
  await checkEndpoint("https://api.whop.com/api/v5/company/payments?substatuses[]=past_due");

  console.log("\n=== Testing App Payments & Substatuses ===");
  await checkEndpoint("https://api.whop.com/api/v5/app/payments?per=20");
  await checkEndpoint("https://api.whop.com/api/v5/app/payments?substatuses[]=incomplete&substatuses[]=failed");
  await checkEndpoint("https://api.whop.com/api/v5/app/payments?substatuses[]=incomplete");
  await checkEndpoint("https://api.whop.com/api/v5/app/payments?substatuses[]=failed");
}

run();
