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
  const companyId = process.env.WHOP_COMPANY_ID;

  // GET /api/v1/users?company_id={company_id}
  const uRes = await fetch(`https://api.whop.com/api/v1/users?company_id=${companyId}&first=5`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });

  console.log("Users API status:", uRes.status);
  if (uRes.ok) {
    const json = await uRes.json();
    console.log("Users sample:", JSON.stringify(json.data?.[0], null, 2));
  } else {
    console.log("Users API error:", await uRes.text());
  }
}

run();
