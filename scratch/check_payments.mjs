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
const companyId = process.env.WHOP_COMPANY_ID;

console.log("API Key available:", !!apiKey, "Company ID:", companyId);

async function testEndpoint(url, headers = {}) {
  try {
    const res = await fetch(url, {
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        ...headers
      }
    });
    console.log(`\nTesting ${url} -> Status: ${res.status} ${res.statusText}`);
    const text = await res.text();
    try {
      const data = JSON.parse(text);
      console.log("Response summary:", Array.isArray(data.data) ? `data.data length: ${data.data.length}` : (data.pagination ? `pagination: ${JSON.stringify(data.pagination)}, count: ${data.data?.length}` : Object.keys(data)));
      return { status: res.status, data };
    } catch (e) {
      console.log("Response text:", text.slice(0, 500));
      return { status: res.status, text };
    }
  } catch (err) {
    console.error(`Error querying ${url}:`, err.message);
  }
}

async function run() {
  const endpoints = [
    // v5 endpoints
    `https://api.whop.com/api/v5/payments`,
    `https://api.whop.com/api/v5/payments?substatuses[]=incomplete&substatuses[]=failed`,
    `https://api.whop.com/api/v5/payments?substatuses=incomplete&substatuses=failed`,
    `https://api.whop.com/api/v5/app/payments`,
    `https://api.whop.com/api/v5/company/payments`,
    // v2 / v1 endpoints
    `https://api.whop.com/api/v2/payments`,
    `https://api.whop.com/api/v2/payments?substatuses[]=incomplete&substatuses[]=failed`,
    `https://api.whop.com/api/v1/payments`,
  ];

  for (const ep of endpoints) {
    const result = await testEndpoint(ep);
    if (result && result.status === 200) {
      console.log("FULL DATA for", ep, ":", JSON.stringify(result.data, null, 2));
    }
  }
}

run();
