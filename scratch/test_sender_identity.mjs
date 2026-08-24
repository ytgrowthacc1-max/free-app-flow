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

async function checkOAuthUser() {
  const { data: dbSettings } = await supabase.from("settings").select("*");
  const settingsMap = {};
  for (const s of dbSettings || []) settingsMap[s.key] = s.value;

  const token = settingsMap.whop_oauth_token;
  console.log("Testing token with GET https://api.whop.com/api/v1/users/me or oauth userinfo...");

  // Check OAuth user info endpoint
  const userinfoRes = await fetch("https://api.whop.com/oauth/userinfo", {
    headers: { "Authorization": `Bearer ${token}` },
  });

  console.log("Userinfo status:", userinfoRes.status);
  if (userinfoRes.ok) {
    const userinfo = await userinfoRes.json();
    console.log("OAuth Token Identity Confirmed:");
    console.log(`- Username: @${userinfo.preferred_username || userinfo.username}`);
    console.log(`- Display Name: ${userinfo.name}`);
    console.log(`- User ID: ${userinfo.sub || userinfo.id}`);
    console.log(`- Email: ${userinfo.email}`);
  } else {
    console.log("Userinfo response:", await userinfoRes.text());
  }
}

checkOAuthUser();
