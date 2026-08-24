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

async function inspectWhopUsersApi() {
  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;
  console.log("Using companyId:", companyId);

  // 1. Test GET /api/v1/users?company_id={companyId}
  const res = await fetch(`https://api.whop.com/api/v1/users?company_id=${companyId}&first=50`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  console.log("Users API status:", res.status);
  if (res.ok) {
    const json = await res.json();
    console.log(`Fetched ${json.data?.length} users from /api/v1/users`);
    if (json.data?.length > 0) {
      console.log("Sample user profile from API:", JSON.stringify(json.data[0], null, 2));
    }
  }

  // 2. Also check if GET /api/v1/people contains user earnings or member spend
  const pRes = await fetch(`https://api.whop.com/api/v1/people?company_id=${companyId}&first=10`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  if (pRes.ok) {
    const pJson = await pRes.json();
    const p0 = pJson.data?.[0];
    console.log("Sample person keys:", Object.keys(p0 || {}));
    if (p0?.user) {
      console.log("Sample person.user keys:", Object.keys(p0.user));
      console.log("Sample person.user data:", JSON.stringify(p0.user, null, 2));
    }
  }
}

inspectWhopUsersApi();
