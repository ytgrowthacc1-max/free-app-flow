import fs from "fs";
import path from "path";

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

console.log("Using companyId:", companyId);

async function checkPeople() {
  console.log("\n--- Testing GET /api/v1/people ---");
  try {
    const res = await fetch(`https://api.whop.com/api/v1/people?company_id=${companyId}&first=5`, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
    });
    console.log("Status:", res.status);
    const json = await res.json();
    console.log("Sample people item:", JSON.stringify(json.data?.[0], null, 2));
    if (json.data && json.data.length > 0) {
      console.log("Location field present in people?:", json.data.map(p => ({
        name: p.name || p.user?.username,
        country: p.location?.country,
        city: p.location?.city,
        timezone: p.timezone,
        user_id: p.user?.id || p.id
      })));
    }
  } catch (e) {
    console.error("People error:", e);
  }
}

async function checkPayments() {
  console.log("\n--- Testing GET /api/v1/payments ---");
  try {
    const res = await fetch(`https://api.whop.com/api/v1/payments?company_id=${companyId}&first=5`, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
    });
    console.log("Status:", res.status);
    const json = await res.json();
    console.log("Sample payment item:", JSON.stringify(json.data?.[0], null, 2));
  } catch (e) {
    console.error("Payments error:", e);
  }
}

async function run() {
  await checkPeople();
  await checkPayments();
}

run();
