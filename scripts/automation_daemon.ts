import fs from "fs";
import path from "path";

// Manually load env variables from .env file if it exists
try {
  const envPath = path.join(process.cwd(), ".env");
  if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, "utf-8");
    const lines = content.split(/\r?\n/);
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const index = trimmed.indexOf("=");
      if (index > 0) {
        const key = trimmed.slice(0, index).trim();
        let val = trimmed.slice(index + 1).trim();
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
          val = val.slice(1, -1);
        }
        process.env[key] = val;
      }
    }
  }
} catch (e) {
  console.error("Failed to load .env file manually:", e);
}

const logFilePath = path.join(process.cwd(), "daemon_logs.txt");

// Override console methods to write logs to local file
const originalLog = console.log;
const originalError = console.error;

console.log = (...args: any[]) => {
  originalLog.apply(console, args);
  const msg = args.map(arg => typeof arg === "object" ? JSON.stringify(arg) : String(arg)).join(" ");
  const line = `[${new Date().toISOString()}] [INFO] ${msg}\n`;
  try {
    fs.appendFileSync(logFilePath, line, "utf-8");
  } catch (e) {}
};

console.error = (...args: any[]) => {
  originalError.apply(console, args);
  const msg = args.map(arg => typeof arg === "object" ? JSON.stringify(arg) : String(arg)).join(" ");
  const line = `[${new Date().toISOString()}] [ERROR] ${msg}\n`;
  try {
    fs.appendFileSync(logFilePath, line, "utf-8");
  } catch (e) {}
};

async function main() {
  console.log("====================================================");
  console.log("  Whop Lead Funnel Automation Daemon");
  console.log("====================================================");
  console.log(`Supabase Target: ${process.env.SUPABASE_URL}`);
  console.log(`Whop Company ID: ${process.env.WHOP_COMPANY_ID}`);
  console.log(`Bot User ID:     ${process.env.BOT_USER_ID || "user_tFompFhTYu2xr"}`);
  console.log("----------------------------------------------------");

  const { tickCron, logToDb } = await import("../src/lib/daemon.server");

  let isRunning = false;
  async function tick() {
    if (isRunning) {
      console.log("[DAEMON] Previous tick still executing. Skipping interval.");
      return;
    }
    isRunning = true;
    try {
      await tickCron();
    } catch (e: any) {
      console.error("[DAEMON] Exception during tick:", e.message || e);
      await logToDb("ERROR", `[DAEMON] Exception during local daemon tick: ${e.message || e}`);
    } finally {
      isRunning = false;
    }
  }

  // Initial tick
  await tick();

  // Tick every 30 seconds
  const INTERVAL = 30000;
  setInterval(tick, INTERVAL);
}

main().catch(err => {
  console.error("[CRITICAL] Daemon crashed:", err);
  process.exit(1);
});
