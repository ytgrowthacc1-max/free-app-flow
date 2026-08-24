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
const WHOP_COMPANY_ID = process.env.WHOP_COMPANY_ID;

// Usage: node scratch/send_test_dm.mjs [whop_user_id]
async function testSendSupportMessage(targetUserId) {
  if (!targetUserId) {
    console.log("Usage: node scratch/send_test_dm.mjs <user_id>");
    console.log("Example: node scratch/send_test_dm.mjs user_JdQZQK7P9FWME");
    return;
  }

  console.log(`1. Opening support channel with user ${targetUserId}...`);
  const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${WHOP_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      company_id: WHOP_COMPANY_ID,
      user_id: targetUserId,
    }),
  });

  if (!channelRes.ok) {
    console.error("Error creating channel:", channelRes.status, await channelRes.text());
    return;
  }

  const channelData = await channelRes.json();
  const channelId = channelData.id;
  console.log(`Channel resolved successfully! Channel ID: ${channelId}`);

  const testMessage = `[TEST] hey there, this is a test payment recovery message from your App Builders automated bot.`;
  console.log(`2. Sending test message: "${testMessage}"...`);

  const msgRes = await fetch("https://api.whop.com/api/v1/messages", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${WHOP_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      channel_id: channelId,
      content: testMessage,
    }),
  });

  if (!msgRes.ok) {
    console.error("Error sending message:", msgRes.status, await msgRes.text());
    return;
  }

  const msgData = await msgRes.json();
  console.log(`Success! Message delivered. Message ID: ${msgData.id}`);
}

const target = process.argv[2];
testSendSupportMessage(target);
