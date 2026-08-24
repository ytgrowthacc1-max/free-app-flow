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

async function check(url) {
  try {
    const res = await fetch(url, {
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      }
    });
    const text = await res.text();
    let parsed;
    try { parsed = JSON.parse(text); } catch (e) {}
    console.log(`[${res.status}] ${url}`);
    if (parsed) {
      if (parsed.data) {
        console.log(`  -> Count: ${parsed.data.length}, Pagination:`, parsed.pagination);
        if (parsed.data.length > 0) {
          console.log(`  -> First item sample: id=${parsed.data[0].id}, status=${parsed.data[0].status}, email=${parsed.data[0].user_email}`);
        }
      } else {
        console.log(`  -> Response keys:`, Object.keys(parsed), parsed.error || parsed.message || "");
      }
    } else {
      console.log(`  -> Non-JSON:`, text.slice(0, 100));
    }
  } catch (err) {
    console.error(`Error ${url}:`, err.message);
  }
}

async function run() {
  // Test base endpoint without trailing slash vs with trailing slash vs various query formats
  await check("https://api.whop.com/api/v5/payments");
  await check("https://api.whop.com/api/v5/payments/");
  await check("https://api.whop.com/api/v5/payments?page=1");
  await check("https://api.whop.com/api/v5/payments/?page=1");
  await check("https://api.whop.com/api/v5/payments/?substatuses[]=incomplete&substatuses[]=failed");
  await check("https://api.whop.com/api/v5/payments?substatuses%5B%5D=incomplete&substatuses%5B%5D=failed");
  await check("https://api.whop.com/api/v5/payments?substatuses=incomplete,failed");
  await check("https://api.whop.com/api/v5/payments?substatuses=incomplete");
  await check("https://api.whop.com/api/v5/payments?substatuses=failed");
  await check("https://api.whop.com/api/v5/payments?status=failed");
  await check("https://api.whop.com/api/v5/payments?status=incomplete");

  // Also check developer docs endpoint: https://api.whop.com/api/v5/company/payments or similar
  await check("https://api.whop.com/payments");
  await check("https://api.whop.com/payments?substatuses[]=incomplete");
}

run();
