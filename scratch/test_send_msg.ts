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

async function testWhopMessageSend() {
  const apiKey = process.env.WHOP_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;
  console.log("API Key:", apiKey?.slice(0, 10));
  console.log("Company ID:", companyId);

  // 1. Create/Get support channel for user_ImMeqYlxMpCgP
  const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      company_id: companyId,
      user_id: "user_ImMeqYlxMpCgP",
    }),
  });

  const channelData = await channelRes.json();
  console.log("Channel ID:", channelData.id);

  if (channelData.id) {
    // 2. Try sending message with API key
    const msgRes = await fetch("https://api.whop.com/api/v1/messages", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        channel_id: channelData.id,
        content: "Test message from API diagnostic script",
      }),
    });

    console.log("Message send status with API Key:", msgRes.status);
    const msgText = await msgRes.text();
    console.log("Message response:", msgText.slice(0, 300));
  }
}

testWhopMessageSend().catch(console.error);
