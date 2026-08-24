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
  const testUserId = "user_6Y5aYlCERMsfF"; // Wei Shen

  const res = await fetch(`https://api.whop.com/api/v5/users/${testUserId}`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });

  console.log("V5 User endpoint status:", res.status);
  if (res.ok) {
    const json = await res.json();
    console.log("User data:", json);
  } else {
    console.log("Error text:", await res.text());
  }
}

run();
