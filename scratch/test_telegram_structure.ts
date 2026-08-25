import fs from "fs";
import path from "path";

// Load .env
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

import { notifyTelegram } from "../src/lib/leads.server.js";

async function testStructure() {
  await notifyTelegram({
    id: "1d726c08-84bd-4c9a-b8e6-db3efe406e76",
    first_name: "Will Vaitkus",
    email: "hibridas117@gmail.com",
    niche: "Reselling",
    member_count: 150,
    monthly_price: 30,
    mrr: 4500,
    timeline: "Within a month",
    whop_url: "https://whop.com/app-builders-f882/exp_rJQzFOett73ntx/app/",
    whop_username: "bigwlt",
    whop_user_id: "user_ImMeqYlxMpCgP",
    lead_score: 63,
    lead_tag: "WARM",
    country: "AE",
    city: "Dubai",
    profile_earnings_badge: "$100",
  });

  console.log("Telegram notification sent!");
}

testStructure().catch(console.error);
