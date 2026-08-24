import fs from "fs";
import path from "path";

const envPath = path.resolve(process.cwd(), ".env");
if (fs.existsSync(envPath)) {
  const content = fs.readFileSync(envPath, "utf8");
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx > 0) {
      const key = trimmed.slice(0, eqIdx).trim();
      const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, "");
      if (!process.env[key]) process.env[key] = val;
    }
  }
}

async function run() {
  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  
  // Test payments endpoint
  const payRes = await fetch("https://api.whop.com/api/v5/company/payments?first=10", {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  console.log("Payments API status:", payRes.status);
  if (payRes.ok) {
    const json = await payRes.json();
    console.log("Payments sample:", json.data?.slice(0, 2));
  }

  // Test members endpoint
  const memRes = await fetch("https://api.whop.com/api/v5/company/members?first=10", {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  console.log("Members API status:", memRes.status);
  if (memRes.ok) {
    const json = await memRes.json();
    console.log("Members sample:", json.data?.slice(0, 2));
  }
}

run();
