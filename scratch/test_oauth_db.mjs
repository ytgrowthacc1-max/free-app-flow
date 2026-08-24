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
const WHOP_OAUTH_CLIENT_ID = process.env.WHOP_OAUTH_CLIENT_ID || "app_oPIxXnyEJ8uxNK";
const WHOP_OAUTH_CLIENT_SECRET = process.env.WHOP_OAUTH_CLIENT_SECRET || "apik_hSkxM70uiNnlc_A2053881_C_29013dc002510430177cb2c8683af179d845fe8ed7ba0f659caaa9a8a98790";

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false },
});

async function testOAuthFromDb() {
  const { data: dbSettings } = await supabase.from("settings").select("*");
  const settingsMap = {};
  for (const s of dbSettings || []) settingsMap[s.key] = s.value;

  console.log("Current DB tokens:");
  console.log("whop_oauth_token starts with:", settingsMap.whop_oauth_token?.slice(0, 30));
  console.log("whop_refresh_token:", settingsMap.whop_refresh_token);

  // Test refreshing the token
  console.log("\nAttempting refresh token request to Whop OAuth...");
  const res = await fetch("https://api.whop.com/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      grant_type: "refresh_token",
      client_id: WHOP_OAUTH_CLIENT_ID,
      client_secret: WHOP_OAUTH_CLIENT_SECRET,
      refresh_token: settingsMap.whop_refresh_token,
    }),
  });

  console.log("Refresh response status:", res.status, res.statusText);
  const text = await res.text();
  console.log("Refresh response:", text);

  if (res.ok) {
    const data = JSON.parse(text);
    console.log("New Access Token:", data.access_token?.slice(0, 30));
    console.log("New Refresh Token:", data.refresh_token);

    // Save back to DB
    await supabase.from("settings").upsert([
      { key: "whop_oauth_token", value: data.access_token },
      { key: "whop_refresh_token", value: data.refresh_token },
    ]);
    console.log("Saved refreshed tokens to Supabase settings table!");

    // Also update .env
    let envContent = fs.readFileSync(".env", "utf-8");
    envContent = envContent.replace(/WHOP_OAUTH_TOKEN=.*/, `WHOP_OAUTH_TOKEN=${data.access_token}`);
    envContent = envContent.replace(/WHOP_REFRESH_TOKEN=.*/, `WHOP_REFRESH_TOKEN=${data.refresh_token}`);
    fs.writeFileSync(".env", envContent, "utf-8");
    console.log("Updated .env file with active OAuth tokens!");
  }
}

testOAuthFromDb();
