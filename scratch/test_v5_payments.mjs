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

async function checkV5Payments() {
  const res = await fetch(`https://api.whop.com/api/v5/company/payments?per=5`, {
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
  });
  console.log("V5 Payments Status:", res.status);
  const json = await res.json();
  if (json.data && json.data.length > 0) {
    console.log("Sample Payment Keys:", Object.keys(json.data[0]));
    console.log("Sample Payment Billing / Country info:", {
      id: json.data[0].id,
      user_id: json.data[0].user_id,
      user_username: json.data[0].user_username,
      user_email: json.data[0].user_email,
      billing_address: json.data[0].billing_address,
      country: json.data[0].country || json.data[0].billing_address?.country,
      card_country: json.data[0].card_country,
      ip_country: json.data[0].ip_country,
      payment_method: json.data[0].payment_method,
    });
  }
}

checkV5Payments();
