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

const WHOP_API_KEY = process.env.WHOP_API_KEY;

async function checkProducts() {
  const urls = [
    "https://api.whop.com/api/v5/company/products",
    "https://api.whop.com/api/v5/app/products",
    "https://api.whop.com/api/v2/products",
  ];

  for (const u of urls) {
    try {
      const res = await fetch(u, {
        headers: {
          "Authorization": `Bearer ${WHOP_API_KEY}`,
          "Content-Type": "application/json",
        },
      });
      console.log(`[${res.status}] ${u}`);
      if (res.ok) {
        const data = await res.json();
        console.log("Products:", JSON.stringify(data.data?.map(p => ({ id: p.id, title: p.title || p.name })), null, 2));
      }
    } catch (e) {
      console.error(e);
    }
  }
}

checkProducts();
