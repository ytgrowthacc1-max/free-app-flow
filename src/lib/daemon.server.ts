import { generateCortexResponse } from "./cortex.server";

// -------------------------------------------------------------
// Database-backed Logging & Settings
// -------------------------------------------------------------
export async function logToDb(level: "INFO" | "ERROR", message: string) {
  const ts = new Date().toISOString();
  if (level === "INFO") {
    console.log(`[${ts}] [INFO] ${message}`);
  } else {
    console.error(`[${ts}] [ERROR] ${message}`);
  }

  try {
    const { supabaseAdmin } = await import("./leads.server");
    await supabaseAdmin.from("daemon_logs").insert({ level, message });
  } catch (e) {
    console.error("Failed to write log to Supabase:", e);
  }
}

async function getSetting(key: string, defaultValue: string): Promise<string> {
  try {
    const { supabaseAdmin } = await import("./leads.server");
    const { data, error } = await supabaseAdmin
      .from("settings")
      .select("value")
      .eq("key", key)
      .maybeSingle();
    if (error || !data) return defaultValue;
    return data.value;
  } catch (e) {
    return defaultValue;
  }
}

async function setSetting(key: string, value: string): Promise<void> {
  try {
    const { supabaseAdmin } = await import("./leads.server");
    await supabaseAdmin.from("settings").upsert({ key, value });
  } catch (e) {
    console.error(`Failed to write setting ${key}:`, e);
  }
}

async function getProcessedMessageIds(): Promise<Set<string>> {
  try {
    const { supabaseAdmin } = await import("./leads.server");
    const { data, error } = await supabaseAdmin
      .from("processed_messages")
      .select("id");
    if (error) {
      await logToDb("ERROR", `Failed to fetch processed messages: ${error.message}`);
      return new Set();
    }
    return new Set((data || []).map((row: any) => row.id));
  } catch (e: any) {
    await logToDb("ERROR", `Exception fetching processed messages: ${e.message || e}`);
    return new Set();
  }
}

async function saveProcessedMessageId(id: string): Promise<void> {
  try {
    const { supabaseAdmin } = await import("./leads.server");
    await supabaseAdmin.from("processed_messages").upsert({ id });
  } catch (e: any) {
    await logToDb("ERROR", `Failed to save processed message ID ${id}: ${e.message || e}`);
  }
}

// -------------------------------------------------------------
// OAuth Token Management & Messaging
// -------------------------------------------------------------
async function refreshOAuthToken(): Promise<string | null> {
  const refreshToken = await getSetting("whop_refresh_token", process.env.WHOP_REFRESH_TOKEN || "");
  if (!refreshToken) {
    await logToDb("ERROR", "[OAUTH] No refresh token found. Cannot refresh OAuth token.");
    return null;
  }

  const oauthClientId = process.env.WHOP_OAUTH_CLIENT_ID || "app_oPIxXnyEJ8uxNK";
  const oauthClientSecret = process.env.WHOP_OAUTH_CLIENT_SECRET || "apik_hSkxM70uiNnlc_A2053881_C_29013dc002510430177cb2c8683af179d845fe8ed7ba0f659caaa9a8a98790";

  try {
    const res = await fetch("https://api.whop.com/oauth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        grant_type: "refresh_token",
        client_id: oauthClientId,
        client_secret: oauthClientSecret,
        refresh_token: refreshToken,
      }),
    });

    if (!res.ok) {
      await logToDb("ERROR", `[OAUTH] Refresh token request failed: ${await res.text()}`);
      return null;
    }

    const data = await res.json();
    const newAccessToken = data.access_token;
    const newRefreshToken = data.refresh_token;

    if (newAccessToken && newRefreshToken) {
      await logToDb("INFO", "[OAUTH] OAuth token refreshed successfully.");
      await setSetting("whop_oauth_token", newAccessToken);
      await setSetting("whop_refresh_token", newRefreshToken);
      return newAccessToken;
    }
  } catch (e: any) {
    await logToDb("ERROR", `[OAUTH] Exception during token refresh: ${e.message || e}`);
  }

  return null;
}

async function sendSupportMessageWithApiKey(channelId: string, content: string): Promise<any> {
  const whopApiKey = process.env.WHOP_API_KEY;
  await logToDb("INFO", `[DAEMON] Sending message using Developer Key fallback to channel ${channelId}...`);
  const res = await fetch("https://api.whop.com/api/v1/messages", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${whopApiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      channel_id: channelId,
      content,
    }),
  });

  if (!res.ok) {
    throw new Error(`Whop API returned status ${res.status}: ${await res.text()}`);
  }

  return res.json();
}

async function sendSupportMessage(channelId: string, content: string): Promise<any> {
  let oauthToken = await getSetting("whop_oauth_token", process.env.WHOP_OAUTH_TOKEN || "");
  if (!oauthToken) {
    return sendSupportMessageWithApiKey(channelId, content);
  }

  await logToDb("INFO", `[DAEMON] Sending message using OAuth token to channel ${channelId}...`);
  let res = await fetch("https://api.whop.com/api/v1/messages", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${oauthToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      channel_id: channelId,
      content,
    }),
  });

  if (res.status === 401) {
    await logToDb("INFO", "[OAUTH] OAuth token expired (401). Attempting token refresh...");
    const refreshed = await refreshOAuthToken();
    if (refreshed) {
      await logToDb("INFO", "[OAUTH] Retrying message sending with refreshed OAuth token...");
      res = await fetch("https://api.whop.com/api/v1/messages", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${refreshed}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel_id: channelId,
          content,
        }),
      });
    }
  }

  if (!res.ok) {
    const errText = await res.text();
    await logToDb("ERROR", `[OAUTH] Failed to send message using OAuth token: ${errText}`);
    return sendSupportMessageWithApiKey(channelId, content);
  }

  return res.json();
}

// -------------------------------------------------------------
// STEP 1: Poll & Send Abandoned Outreach Messages
// -------------------------------------------------------------
export async function checkAndSendAbandonedOutreach() {
  await logToDb("INFO", "[OUTREACH] Checking for abandoned leads...");
  const timeoutMs = process.env.OUTREACH_TIMEOUT_MS ? parseInt(process.env.OUTREACH_TIMEOUT_MS) : 5 * 60 * 1000;
  const timeLimit = new Date(Date.now() - timeoutMs).toISOString();

  const { supabaseAdmin } = await import("./leads.server");
  const { data: leads, error } = await supabaseAdmin
    .from("leads")
    .select("*")
    .eq("completed", false)
    .eq("abandoned_message_sent", false)
    .not("whop_user_id", "is", null)
    .lt("created_at", timeLimit);

  if (error) {
    await logToDb("ERROR", `[OUTREACH] Error fetching abandoned leads: ${error.message}`);
    return;
  }

  if (!leads || leads.length === 0) {
    await logToDb("INFO", "[OUTREACH] No new abandoned leads to message.");
    return;
  }

  await logToDb("INFO", `[OUTREACH] Found ${leads.length} leads to reach out to.`);

  const whopApiKey = process.env.WHOP_API_KEY;
  const whopCompanyId = process.env.WHOP_COMPANY_ID;

  for (const lead of leads) {
    await logToDb("INFO", `[OUTREACH] Processing lead ${lead.id} (@${lead.whop_username})...`);
    try {
      // Create support/DM channel
      const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${whopApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_id: whopCompanyId,
          user_id: lead.whop_user_id,
        }),
      });

      if (!channelRes.ok) {
        const errText = await channelRes.text();
        await logToDb("ERROR", `[OUTREACH] Whop API error opening channel for ${lead.whop_username}: ${errText}`);
        continue;
      }

      const channelData = await channelRes.json();
      const channelId = channelData.id;
      if (!channelId) {
        await logToDb("ERROR", `[OUTREACH] No channel ID in response: ${JSON.stringify(channelData)}`);
        continue;
      }

      // Outreach message
      const text = `hey ${lead.first_name || "there"}, saw you started setting up your custom whop app blueprint but didn't finish. did you get stuck on anything, or did you just want to check how the free custom app build works?`;

      let msgData;
      try {
        msgData = await sendSupportMessage(channelId, text);
      } catch (sendErr: any) {
        await logToDb("ERROR", `[OUTREACH] Failed to send message to channel ${channelId}: ${sendErr.message || sendErr}`);
        continue;
      }

      if (msgData && msgData.id) {
        await saveProcessedMessageId(msgData.id);
      }

      // Update Database
      const { error: updateError } = await supabaseAdmin
        .from("leads")
        .update({ abandoned_message_sent: true })
        .eq("id", lead.id);

      if (updateError) {
        await logToDb("ERROR", `[OUTREACH] DB update failed for lead ${lead.id}: ${updateError.message}`);
      } else {
        await logToDb("INFO", `Success: DM outreach sent to @${lead.whop_username}`);
      }
    } catch (e: any) {
      await logToDb("ERROR", `[OUTREACH] Exception processing lead ${lead.id}: ${e.message || e}`);
    }
  }
}

// -------------------------------------------------------------
// STEP 2: Poll & Handle Incoming User Replies (Chatbot)
// -------------------------------------------------------------
export async function handleChatbotReplies() {
  await logToDb("INFO", "[CHATBOT] Polling support channels...");
  const processedIds = await getProcessedMessageIds();
  const whopApiKey = process.env.WHOP_API_KEY;
  const botUserId = process.env.BOT_USER_ID || "user_tFompFhTYu2xr";

  const channelsUrl = `https://api.whop.com/api/v1/dm_channels?first=50`;
  try {
    const res = await fetch(channelsUrl, {
      headers: {
        "Authorization": `Bearer ${whopApiKey}`,
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      await logToDb("ERROR", `[CHATBOT] Failed to fetch channels: ${res.status}`);
      return;
    }

    const channelsData = await res.json();
    const channels = channelsData.data || [];

    const { supabaseAdmin } = await import("./leads.server");

    for (const chan of channels) {
      const channelId = chan.id;
      const channelName = chan.name || "";
      const isSupport = channelName.toLowerCase().includes("support chat") || channelName === "";

      if (!isSupport) continue;

      // Fetch messages in this channel
      const msgUrl = `https://api.whop.com/api/v1/messages?channel_id=${channelId}&first=10&direction=desc`;
      const msgRes = await fetch(msgUrl, {
        headers: {
          "Authorization": `Bearer ${whopApiKey}`,
          "Content-Type": "application/json",
        },
      });

      if (!msgRes.ok) continue;

      const msgsData = await msgRes.json();
      const messages = msgsData.data || [];
      if (messages.length === 0) continue;

      const latestMsg = messages[0];
      const sender = latestMsg.user || {};
      const senderId = sender.id;
      const senderName = sender.username || sender.name || "User";

      // Skip if the latest message was sent by the bot or system users
      if (senderId === botUserId || ["teamwhop", "emailsapp", "whop", "system"].includes(senderName.toLowerCase())) {
        continue;
      }

      // Check if message was already processed
      if (processedIds.has(latestMsg.id)) {
        continue;
      }

      await logToDb("INFO", `[CHATBOT] New message in channel ${channelId} from @${senderName}: "${latestMsg.content}"`);

      // Find the corresponding lead in Supabase
      const { data: lead, error: leadError } = await supabaseAdmin
        .from("leads")
        .select("*")
        .eq("whop_user_id", senderId)
        .maybeSingle();

      if (leadError) {
        await logToDb("ERROR", `[CHATBOT] DB Error looking up lead for user ${senderId}: ${leadError.message}`);
        continue;
      }

      if (!lead) {
        await logToDb("INFO", `[CHATBOT] No lead found in DB for user ${senderId} (@${senderName}). Skipping.`);
        await saveProcessedMessageId(latestMsg.id);
        continue;
      }

      if (lead.completed) {
        await logToDb("INFO", `[CHATBOT] Lead is already completed for @${senderName}. Skipping chatbot response.`);
        await saveProcessedMessageId(latestMsg.id);
        continue;
      }

      // We have an incomplete lead! Let's process the conversation state.
      await processLeadOnboardingChat(lead, latestMsg, messages, channelId, botUserId);
    }
  } catch (e: any) {
    await logToDb("ERROR", `[CHATBOT] Exception polling channels: ${e.message || e}`);
  }
}

// State transition and AI execution
async function processLeadOnboardingChat(lead: any, latestMsg: any, messages: any[], channelId: string, botUserId: string) {
  const chatHistory = messages
    .slice()
    .reverse()
    .map((m: any) => {
      const isBot = m.user?.id === botUserId;
      return `${isBot ? "Assistant" : "User"}: ${m.content}`;
    })
    .join("\n");

  const leadState = {
    first_name: lead.first_name,
    whop_url: lead.whop_url,
    niche: lead.niche,
    member_count: lead.member_count,
    monthly_price: lead.monthly_price,
    ideal_app: lead.ideal_app,
    timeline: lead.timeline,
    email: lead.email,
  };

  const systemPrompt = `You are a friendly, expert Whop App Builder assistant. Your job is to collect missing details from the user to complete their custom app blueprint.

Here is the current lead database state:
${JSON.stringify(leadState, null, 2)}

Missing fields to collect (in logical order):
1. Whop Community URL (must contain whop.com)
2. Niche (e.g. trading, sports betting, fitness, ecommerce, reselling, or other)
3. Member Count (number)
4. Monthly Price/MRR (number)
5. Ideal app description (what do they want the app to do)
6. Launch Timeline (ASAP, within a month, or just exploring)
7. Email address

Please analyze the user's latest reply and full chat history.
If the user has provided any of the missing fields in their latest message(s), parse and extract them.
Then, formulate the next conversational message to ask for the next missing field in the list, OR confirm details.

CRITICAL RULES:
- Keep the response text very human, casual, and brief. Use lowercase letters mostly, dropped punctuation, and natural spacing. No emojis.
- Never mention prices, hosting fees, setup fees, or deposits. The service is free (we build it free, they only cover hosting when live).
- Return ONLY a valid JSON object with the keys "extracted_fields" and "next_message". Do not write any markdown blocks or fences.

Example JSON output structure:
{
  "extracted_fields": {
    "niche": "sports betting"
  },
  "next_message": "got it, sports betting is huge right now. how many active members do you currently have in your group?"
}`;

  await logToDb("INFO", `[CHATBOT] Calling Cortex AI to process reply for @${lead.whop_username}...`);
  try {
    const userPrompt = `Here is the conversation history:\n${chatHistory}\n\nPlease parse and reply.`;
    const text = await generateCortexResponse(systemPrompt, userPrompt);

    let cleanedText = text.trim();
    if (cleanedText.startsWith("```")) {
      cleanedText = cleanedText.replace(/^```(?:json)?/i, "").replace(/```\s*$/, "").trim();
    }

    const parsed = JSON.parse(cleanedText);
    await logToDb("INFO", `[CHATBOT] AI parsed data: ${JSON.stringify(parsed)}`);

    const updates = parsed.extracted_fields || {};
    const replyText = parsed.next_message;

    const updatedState = { ...leadState, ...updates };
    let shouldComplete = false;

    if (
      updatedState.whop_url &&
      updatedState.niche &&
      updatedState.member_count &&
      updatedState.monthly_price &&
      updatedState.timeline &&
      updatedState.email
    ) {
      shouldComplete = true;
    }

    const { supabaseAdmin } = await import("./leads.server");

    // Update database row
    const { error: dbUpdateError } = await supabaseAdmin
      .from("leads")
      .update(updates)
      .eq("id", lead.id);

    if (dbUpdateError) {
      await logToDb("ERROR", `[CHATBOT] Failed to update lead in DB: ${dbUpdateError.message}`);
    } else {
      await logToDb("INFO", `[CHATBOT] Successfully updated lead fields in DB: ${JSON.stringify(updates)}`);
    }

    if (shouldComplete) {
      await logToDb("INFO", `[CHATBOT] Lead ${lead.id} is now complete! Generating blueprint...`);
      
      const { calcLeadScore, lightweightScrape, generateBlueprint, notifyTelegram } = await import("./leads.server");
      
      const score = calcLeadScore(Number(updatedState.member_count), Number(updatedState.monthly_price), updatedState.timeline);
      const scraped = await lightweightScrape(updatedState.whop_url);
      const ai_plan = await generateBlueprint({
        whop_url: updatedState.whop_url,
        niche: updatedState.niche,
        member_count: Number(updatedState.member_count),
        monthly_price: Number(updatedState.monthly_price),
        ideal_app: updatedState.ideal_app || "",
        timeline: updatedState.timeline,
        first_name: updatedState.first_name || lead.first_name,
      }, scraped);

      await supabaseAdmin
        .from("leads")
        .update({
          whop_url: updatedState.whop_url,
          niche: updatedState.niche,
          member_count: Number(updatedState.member_count),
          monthly_price: Number(updatedState.monthly_price),
          mrr: score.mrr,
          ideal_app: updatedState.ideal_app || "",
          timeline: updatedState.timeline,
          first_name: updatedState.first_name || lead.first_name,
          email: updatedState.email,
          lead_score: score.score,
          lead_tag: score.tag,
          scrape_status: scraped.status,
          scraped_data: scraped as any,
          ai_plan: ai_plan as any,
          completed: true,
        })
        .eq("id", lead.id);

      await notifyTelegram({
        id: lead.id,
        first_name: updatedState.first_name || lead.first_name,
        email: updatedState.email,
        niche: updatedState.niche,
        whop_url: updatedState.whop_url,
        member_count: Number(updatedState.member_count),
        monthly_price: Number(updatedState.monthly_price),
        mrr: score.mrr,
        lead_tag: score.tag,
        lead_score: score.score,
        timeline: updatedState.timeline,
        social_handle: lead.social_handle || "",
        ideal_app: updatedState.ideal_app || "",
        whop_username: lead.whop_username,
        whop_user_id: lead.whop_user_id,
      }).catch(tgErr => console.error("Telegram notify failed:", tgErr));

      // Send blueprint link to user
      const hostUrl = process.env.APP_URL || "https://free-app-flow.vercel.app";
      const finalMsg = `awesome, i have everything i need! I just finished generating your custom app blueprints. you can view them here: ${hostUrl}/blueprint/${lead.id}\n\nlet me know what you think!`;
      
      try {
        await sendSupportMessage(channelId, finalMsg);
        await logToDb("INFO", `[CHATBOT] Outreach successfully completed. Sent blueprint URL to @${lead.whop_username}`);
      } catch (sendErr: any) {
        await logToDb("ERROR", `[CHATBOT] Failed to send blueprint URL: ${sendErr.message || sendErr}`);
      }
    } else {
      // Send the next question from AI
      try {
        const msgData = await sendSupportMessage(channelId, replyText);
        if (msgData && msgData.id) await saveProcessedMessageId(msgData.id);
        await logToDb("INFO", `[CHATBOT] Sent follow-up to @${lead.whop_username}: "${replyText}"`);
      } catch (sendErr: any) {
        await logToDb("ERROR", `[CHATBOT] Failed to send next question: ${sendErr.message || sendErr}`);
      }
    }

    // Mark user's message as processed
    await saveProcessedMessageId(latestMsg.id);

  } catch (e: any) {
    await logToDb("ERROR", `[CHATBOT] Error processing chat onboarding for ${lead.whop_username}: ${e.message || e}`);
  }
}

// -------------------------------------------------------------
// Unified Cron Tick Trigger (Invoked by Serverless Route)
// -------------------------------------------------------------
export async function tickCron() {
  await logToDb("INFO", "[DAEMON] Beginning Cron Tick execution...");
  try {
    await checkAndSendAbandonedOutreach();
    await handleChatbotReplies();
    await logToDb("INFO", "[DAEMON] Cron Tick completed successfully.");
  } catch (e: any) {
    await logToDb("ERROR", `[DAEMON] Error during Cron Tick: ${e.message || e}`);
    throw e;
  }
}
