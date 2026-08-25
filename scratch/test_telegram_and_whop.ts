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

import { notifyTelegram, sendSupportMessage } from "../src/lib/leads.server.js";

async function testTelegramAndWhop() {
  console.log("=== Testing Telegram Notification ===");
  console.log("TELEGRAM_BOT_TOKEN:", process.env.TELEGRAM_BOT_TOKEN ? "SET (" + process.env.TELEGRAM_BOT_TOKEN.slice(0, 10) + "...)" : "MISSING!");
  console.log("TELEGRAM_CHAT_ID:", process.env.TELEGRAM_CHAT_ID || "MISSING!");

  try {
    await notifyTelegram({
      id: "test-id-12345",
      first_name: "Test User",
      email: "test@example.com",
      niche: "Fitness",
      member_count: 500,
      monthly_price: 20,
      mrr: 10000,
      timeline: "ASAP",
      ideal_app: "Custom retention app",
      whop_url: "https://whop.com/@dwave6f",
      whop_username: "dwave6f",
      whop_user_id: "user_test",
      lead_score: 95,
      lead_tag: "HOT",
      country: "AE",
    });
    console.log("Telegram notification call finished cleanly.");
  } catch (e: any) {
    console.error("Telegram notification error:", e);
  }

  console.log("\n=== Testing Whop Support API Credentials ===");
  console.log("WHOP_API_KEY:", process.env.WHOP_API_KEY ? "SET (" + process.env.WHOP_API_KEY.slice(0, 10) + "...)" : "MISSING!");
  console.log("WHOP_COMPANY_ID:", process.env.WHOP_COMPANY_ID || "MISSING!");

  // Test creating support channel or fetching support channels
  if (process.env.WHOP_API_KEY && process.env.WHOP_COMPANY_ID) {
    try {
      const res = await fetch("https://api.whop.com/api/v1/support_channels", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${process.env.WHOP_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_id: process.env.WHOP_COMPANY_ID,
          user_id: "user_ImMeqYlxMpCgP", // townhall user id
        }),
      });
      console.log("Whop support channel creation status:", res.status);
      const text = await res.text();
      console.log("Whop response body:", text.slice(0, 300));
    } catch (e: any) {
      console.error("Whop API error:", e);
    }
  }
}

testTelegramAndWhop().catch(console.error);
