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

async function inspectWhopPeople() {
  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;
  console.log("Using companyId:", companyId);

  const res = await fetch(`https://api.whop.com/api/v1/people?company_id=${companyId}&first=50`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  const json = await res.json();
  const people = json.data || [];
  console.log(`Fetched ${people.length} people from Whop API`);
  
  const peopleWithLtv = people.filter(p => (p.ltv > 0 || (p.member && p.member.usd_total_spend > 0)));
  console.log(`People with spend > 0: ${peopleWithLtv.length}`);
  if (peopleWithLtv.length > 0) {
    console.log("Sample person with spend:", JSON.stringify(peopleWithLtv[0], null, 2));
  } else {
    console.log("Sample person object structure:", JSON.stringify(people[0], null, 2));
  }

  // Also check Payments API
  const payRes = await fetch(`https://api.whop.com/api/v1/payments?company_id=${companyId}&first=50`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  const payJson = await payRes.json();
  const payments = payJson.data || [];
  console.log(`Fetched ${payments.length} payments from Whop API`);
  if (payments.length > 0) {
    console.log("Sample payment:", JSON.stringify(payments[0], null, 2));
  }
}

inspectWhopPeople();
