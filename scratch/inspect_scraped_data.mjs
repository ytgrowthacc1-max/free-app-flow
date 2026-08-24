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

async function inspectScrapedData() {
  const { supabaseAdmin } = await import("../src/lib/leads.server.js");
  const { data: leads, error } = await supabaseAdmin.from("leads").select("*");
  if (error) return console.error(error);

  let scrapedWithLtv = 0;
  let scrapedWithLoc = 0;

  for (const l of leads) {
    if (l.scraped_data) {
      if (l.scraped_data.ltv || l.scraped_data.earnings || l.scraped_data.usd_total_spend) scrapedWithLtv++;
      if (l.scraped_data.location || l.scraped_data.country) scrapedWithLoc++;
    }
  }

  console.log(`Leads with scraped_data.ltv/earnings: ${scrapedWithLtv}`);
  console.log(`Leads with scraped_data.location: ${scrapedWithLoc}`);
}

inspectScrapedData();
