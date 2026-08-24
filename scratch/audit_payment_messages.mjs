import { createClient } from "@supabase/supabase-js";
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

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false },
});

async function checkFailedPaymentMessages() {
  console.log("=== 1. Checking Supabase payment_recoveries table ===");
  const { data: rows, error } = await supabase
    .from("payment_recoveries")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("DB Query error:", error);
  } else {
    console.log(`Total payment recovery messages logged in DB: ${rows ? rows.length : 0}`);
    if (rows && rows.length > 0) {
      for (const r of rows) {
        console.log(`- Payment ID: ${r.payment_id} | User: @${r.whop_username} (${r.whop_user_id}) | Mode: ${r.failure_mode} | Sent: ${r.message_sent} | Date: ${r.created_at}`);
        console.log(`  Message: "${r.message_content}"`);
      }
    }
  }

  console.log("\n=== 2. Checking daemon_logs.txt for PAYMENT_RECOVERY activity ===");
  try {
    const logs = fs.readFileSync("daemon_logs.txt", "utf-8");
    const lines = logs.split(/\r?\n/);
    const recoveryLines = lines.filter(l => l.includes("[PAYMENT_RECOVERY]") && !l.includes("No new failed"));
    console.log(`Total non-empty PAYMENT_RECOVERY log lines: ${recoveryLines.length}`);
    for (const l of recoveryLines.slice(-15)) {
      console.log(" ", l);
    }
  } catch (e) {
    console.error("Failed to read daemon_logs.txt:", e);
  }
}

checkFailedPaymentMessages();
