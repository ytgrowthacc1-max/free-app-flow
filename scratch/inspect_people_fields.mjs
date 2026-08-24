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

async function test() {
  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;

  const res = await fetch(`https://api.whop.com/api/v1/people?company_id=${companyId}&first=5`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });

  const json = await res.json();
  console.log("Keys on person object:", Object.keys(json.data?.[0] || {}));
  console.log("Sample person record:", JSON.stringify(json.data?.[0], null, 2));
}

test();
