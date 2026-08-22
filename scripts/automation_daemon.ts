import fs from "fs";
import path from "path";

// Load .env
try {
  const envPath = path.join(process.cwd(), ".env");
  if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, "utf-8");
    for (const line of content.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const idx = trimmed.indexOf("=");
      if (idx > 0) {
        const key = trimmed.slice(0, idx).trim();
        let val = trimmed.slice(idx + 1).trim();
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && v.endsWith("'"))) {
          val = val.slice(1, -1);
        }
        process.env[key] = val;
      }
    }
  }
} catch (e) {
  console.error("Failed to load .env file manually:", e);
}

import { tickCron } from "../src/lib/daemon.server";

async function main() {
  console.log("====================================================");
  console.log("  Whop Automation Unified Background Daemon");
  console.log("====================================================");
  console.log(`Whop Company ID: ${process.env.WHOP_COMPANY_ID}`);
  console.log(`Bot User ID:     ${process.env.BOT_USER_ID}`);
  console.log("----------------------------------------------------");

  async function tick() {
    try {
      await tickCron();
    } catch (e: any) {
      console.error("[DAEMON] Error during tick:", e.message || e);
    }
  }

  // Initial tick
  await tick();

  // Tick every 30 seconds
  const INTERVAL = 30000;
  setInterval(tick, INTERVAL);
}

main().catch((err) => {
  console.error("[CRITICAL] Daemon crashed:", err);
  process.exit(1);
});
