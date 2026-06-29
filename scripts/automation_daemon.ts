import { createClient } from "@supabase/supabase-js";
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

// Load environment variables
const SUPABASE_URL = process.env.SUPABASE_URL || "https://zlmvccewxwimiyuakfeh.supabase.co";
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const WHOP_API_KEY = process.env.WHOP_API_KEY;
const WHOP_COMPANY_ID = process.env.WHOP_COMPANY_ID;
const LOVABLE_API_KEY = process.env.LOVABLE_API_KEY;
const BOT_USER_ID = process.env.BOT_USER_ID || "user_FLtuSxu5Uetoy";

if (!SUPABASE_SERVICE_ROLE_KEY || !WHOP_API_KEY || !WHOP_COMPANY_ID || !LOVABLE_API_KEY) {
  console.error("Missing environment variables. Make sure .env contains:");
  console.error("- SUPABASE_SERVICE_ROLE_KEY");
  console.error("- WHOP_API_KEY");
  console.error("- WHOP_COMPANY_ID");
  console.error("- LOVABLE_API_KEY");
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: {
    persistSession: false,
  },
});

const PROCESSED_MSG_FILE = path.join(process.cwd(), ".tmp", "processed_messages.json");
fs.mkdirSync(path.dirname(PROCESSED_MSG_FILE), { recursive: true });

function getProcessedMessageIds(): Set<string> {
  try {
    if (fs.existsSync(PROCESSED_MSG_FILE)) {
      const data = JSON.parse(fs.readFileSync(PROCESSED_MSG_FILE, "utf-8"));
      return new Set(data);
    }
  } catch (e) {
    console.error("Failed to read processed messages file:", e);
  }
  return new Set();
}

function saveProcessedMessageId(id: string) {
  try {
    const ids = getProcessedMessageIds();
    ids.add(id);
    fs.writeFileSync(PROCESSED_MSG_FILE, JSON.stringify(Array.from(ids), null, 2), "utf-8");
  } catch (e) {
    console.error("Failed to save processed message ID:", e);
  }
}

// -------------------------------------------------------------
// STEP 1: Poll & Send Abandoned Outreach Messages
// -------------------------------------------------------------
async function checkAndSendAbandonedOutreach() {
  console.log("[OUTREACH] Checking for abandoned leads...");
  // 5 minutes ago
  const timeLimit = new Date(Date.now() - 5 * 60 * 1000).toISOString();

  const { data: leads, error } = await supabase
    .from("leads")
    .select("*")
    .eq("completed", false)
    .eq("abandoned_message_sent", false)
    .not("whop_user_id", "is", null)
    .lt("created_at", timeLimit);

  if (error) {
    console.error("[OUTREACH] Error fetching abandoned leads:", error);
    return;
  }

  if (!leads || leads.length === 0) {
    console.log("[OUTREACH] No new abandoned leads to message.");
    return;
  }

  console.log(`[OUTREACH] Found ${leads.length} leads to reach out to.`);

  for (const lead of leads) {
    console.log(`[OUTREACH] Processing lead ${lead.id} (@${lead.whop_username})...`);
    try {
      // Create support/DM channel
      const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${WHOP_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_id: WHOP_COMPANY_ID,
          user_id: lead.whop_user_id,
        }),
      });

      if (!channelRes.ok) {
        const errText = await channelRes.text();
        console.error(`[OUTREACH] Whop API error opening channel for ${lead.whop_username}:`, errText);
        continue;
      }

      const channelData = await channelRes.json();
      const channelId = channelData.id;
      if (!channelId) {
        console.error(`[OUTREACH] No channel ID in response:`, channelData);
        continue;
      }

      // Outreach message
      const text = `hey ${lead.first_name || "there"}, saw you started setting up your custom whop app blueprint but didn't finish. did you get stuck on anything, or did you just want to check how the free custom app build works?`;

      const msgRes = await fetch("https://api.whop.com/api/v1/messages", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${WHOP_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel_id: channelId,
          content: text,
        }),
      });

      if (!msgRes.ok) {
        const errText = await msgRes.text();
        console.error(`[OUTREACH] Failed to send message to channel ${channelId}:`, errText);
        continue;
      }

      const msgData = await msgRes.json();
      if (msgData.id) {
        saveProcessedMessageId(msgData.id);
      }

      // Update Database
      const { error: updateError } = await supabase
        .from("leads")
        .update({ abandoned_message_sent: true })
        .eq("id", lead.id);

      if (updateError) {
        console.error(`[OUTREACH] DB update failed for lead ${lead.id}:`, updateError);
      } else {
        console.log(`[OUTREACH] Success: DM outreach sent to @${lead.whop_username}`);
      }
    } catch (e) {
      console.error(`[OUTREACH] Exception processing lead ${lead.id}:`, e);
    }
  }
}

// -------------------------------------------------------------
// STEP 2: Poll & Handle Incoming User Replies (Chatbot)
// -------------------------------------------------------------
async function handleChatbotReplies() {
  console.log("[CHATBOT] Polling support channels...");
  const processedIds = getProcessedMessageIds();

  // Fetch support channels
  const channelsUrl = `https://api.whop.com/api/v1/dm_channels?first=50`;
  try {
    const res = await fetch(channelsUrl, {
      headers: {
        "Authorization": `Bearer ${WHOP_API_KEY}`,
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      console.error(`[CHATBOT] Failed to fetch channels: ${res.status}`);
      return;
    }

    const channelsData = await res.json();
    const channels = channelsData.data || [];

    for (const chan of channels) {
      const channelId = chan.id;
      const channelName = chan.name || "";
      const isSupport = channelName.toLowerCase().includes("support chat") || channelName === "";

      if (!isSupport) continue;

      // Fetch messages in this channel
      const msgUrl = `https://api.whop.com/api/v1/messages?channel_id=${channelId}&first=10&direction=desc`;
      const msgRes = await fetch(msgUrl, {
        headers: {
          "Authorization": `Bearer ${WHOP_API_KEY}`,
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
      if (senderId === BOT_USER_ID || ["teamwhop", "emailsapp", "whop", "system"].includes(senderName.toLowerCase())) {
        continue;
      }

      // Check if message was already processed
      if (processedIds.has(latestMsg.id)) {
        continue;
      }

      console.log(`[CHATBOT] New message in channel ${channelId} from @${senderName}: "${latestMsg.content}"`);

      // Find the corresponding lead in Supabase
      const { data: lead, error: leadError } = await supabase
        .from("leads")
        .select("*")
        .eq("whop_user_id", senderId)
        .maybeSingle();

      if (leadError) {
        console.error(`[CHATBOT] DB Error looking up lead for user ${senderId}:`, leadError);
        continue;
      }

      if (!lead) {
        console.log(`[CHATBOT] No lead found in DB for user ${senderId} (@${senderName}). Skipping.`);
        saveProcessedMessageId(latestMsg.id);
        continue;
      }

      if (lead.completed) {
        console.log(`[CHATBOT] Lead is already completed for @${senderName}. Skipping chatbot response.`);
        saveProcessedMessageId(latestMsg.id);
        continue;
      }

      // We have an incomplete lead! Let's process the conversation state.
      await processLeadOnboardingChat(lead, latestMsg, messages, channelId);
    }
  } catch (e) {
    console.error("[CHATBOT] Exception polling channels:", e);
  }
}

// State transition and AI execution
async function processLeadOnboardingChat(lead: any, latestMsg: any, messages: any[], channelId: string) {
  // Format message history for AI context
  const chatHistory = messages
    .slice()
    .reverse()
    .map((m: any) => {
      const isBot = m.user?.id === BOT_USER_ID;
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

  console.log(`[CHATBOT] Calling Lovable AI Gateway to process reply for @${lead.whop_username}...`);
  try {
    const aiRes = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Lovable-API-Key": LOVABLE_API_KEY,
      },
      body: JSON.stringify({
        model: "google/gemini-3-flash-preview",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: `Here is the conversation history:\n${chatHistory}\n\nPlease parse and reply.` },
        ],
      }),
    });

    if (!aiRes.ok) {
      console.error(`[CHATBOT] Lovable AI Gateway returned error status: ${aiRes.status}`);
      return;
    }

    const aiData = await aiRes.json();
    let text = aiData?.choices?.[0]?.message?.content || "";
    text = text.trim();
    if (text.startsWith("```")) {
      text = text.replace(/^```(?:json)?/i, "").replace(/```\s*$/, "").trim();
    }

    const parsed = JSON.parse(text);
    console.log(`[CHATBOT] AI parsed data:`, parsed);

    const updates = parsed.extracted_fields || {};
    const replyText = parsed.next_message;

    // Apply updates to database if any
    const updatedState = { ...leadState, ...updates };
    let shouldComplete = false;

    // Validate if we have collected all required fields to complete the lead
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

    // Update database row
    const { error: dbUpdateError } = await supabase
      .from("leads")
      .update({
        ...updates,
      })
      .eq("id", lead.id);

    if (dbUpdateError) {
      console.error(`[CHATBOT] Failed to update lead in DB:`, dbUpdateError);
    } else {
      console.log(`[CHATBOT] Successfully updated lead fields in DB:`, updates);
    }

    if (shouldComplete) {
      console.log(`[CHATBOT] Lead ${lead.id} is now complete! Generating blueprint...`);
      
      // Perform blueprint generation and notifications
      const completeRes = await fetch(`${process.env.APP_URL || "http://localhost:5173"}/api/leads/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: lead.id,
          whop_url: updatedState.whop_url,
          niche: updatedState.niche,
          member_count: Number(updatedState.member_count),
          monthly_price: Number(updatedState.monthly_price),
          ideal_app: updatedState.ideal_app || "Engagement Dashboard",
          timeline: updatedState.timeline,
          first_name: updatedState.first_name || lead.first_name,
          email: updatedState.email,
          social_handle: lead.social_handle || "",
        }),
      }).catch(async (e) => {
        // Fallback: manually trigger completion locally if server API is down/inaccessible
        console.warn(`[CHATBOT] Server API completion call failed, running completion fallback locally.`, e);
        const { calcLeadScore, lightweightScrape, generateBlueprint, notifyTelegram } = await import("../src/lib/leads.server");
        
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

        await supabase
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
        }).catch(tgErr => console.error("Telegram fallback notify failed:", tgErr));

        return { ok: true };
      });

      // Send blueprint link to user
      const hostUrl = process.env.APP_URL || "https://freeappflow.com";
      const finalMsg = `awesome, i have everything i need! I just finished generating your custom app blueprints. you can view them here: ${hostUrl}/blueprint/${lead.id}\n\nlet me know what you think!`;
      
      await fetch("https://api.whop.com/api/v1/messages", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${WHOP_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel_id: channelId,
          content: finalMsg,
        }),
      });

      console.log(`[CHATBOT] Outreach successfully completed. Sent blueprint URL to @${lead.whop_username}`);
    } else {
      // Send the next question from AI
      const postMsgRes = await fetch("https://api.whop.com/api/v1/messages", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${WHOP_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel_id: channelId,
          content: replyText,
        }),
      });

      if (!postMsgRes.ok) {
        console.error(`[CHATBOT] Failed to send next question:`, await postMsgRes.text());
      } else {
        const msgData = await postMsgRes.json();
        if (msgData.id) saveProcessedMessageId(msgData.id);
        console.log(`[CHATBOT] Sent follow-up to @${lead.whop_username}: "${replyText}"`);
      }
    }

    // Mark user's message as processed
    saveProcessedMessageId(latestMsg.id);

  } catch (e) {
    console.error(`[CHATBOT] Error processing chat onboarding for ${lead.whop_username}:`, e);
  }
}

// -------------------------------------------------------------
// Orchestration Daemon Poller Loop
// -------------------------------------------------------------
async function main() {
  console.log("====================================================");
  console.log("  Whop Lead Funnel Background Automation Daemon");
  console.log("====================================================");
  console.log(`Supabase Target: ${SUPABASE_URL}`);
  console.log(`Whop Company ID: ${WHOP_COMPANY_ID}`);
  console.log(`Bot User ID:     ${BOT_USER_ID}`);
  console.log("----------------------------------------------------");

  async function tick() {
    try {
      await checkAndSendAbandonedOutreach();
      await handleChatbotReplies();
    } catch (e) {
      console.error("[DAEMON] Error during tick:", e);
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
