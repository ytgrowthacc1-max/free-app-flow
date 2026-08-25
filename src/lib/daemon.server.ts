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
    return (data.value as string) ?? defaultValue;
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
  try {
    let oauthToken = await getSetting("whop_oauth_token", process.env.WHOP_OAUTH_TOKEN || "");
    if (!oauthToken) {
      oauthToken = await refreshOAuthToken();
    }

    if (oauthToken) {
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
        await logToDb("INFO", "[OAUTH] OAuth token expired (401). Refreshing token from Supabase settings...");
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

      if (res.ok) {
        return res.json();
      }
    }
  } catch (e: any) {
    await logToDb("ERROR", `[OAUTH] OAuth message attempt error: ${e.message || e}`);
  }

  // Fallback to Whop Developer API Key
  return sendSupportMessageWithApiKey(channelId, content);
}


// -------------------------------------------------------------
// STEP 1: Poll & Send Abandoned Outreach Messages
// -------------------------------------------------------------
// -------------------------------------------------------------
// Helper: LLM-based ideal_app Summarization with Fallback
// -------------------------------------------------------------
export async function summarizeIdealApp(lead: any): Promise<string> {
  if (lead.ideal_app_summary && lead.ideal_app_summary.trim().length > 0) {
    return lead.ideal_app_summary.trim();
  }

  const { supabaseAdmin } = await import("./leads.server");

  // 1. Try Cortex API summarization if ideal_app has text
  if (lead.ideal_app && lead.ideal_app.trim().length >= 5) {
    try {
      const prompt = `Summarize this app idea in 1 punchy English sentence (max 12 words, no quotes, no period at end): "${lead.ideal_app.trim()}"`;
      const response = await generateCortexResponse(
        "You are an expert app product strategist. Be extremely concise and clear.",
        prompt
      );
      const summary = response.trim().replace(/^["']|["']$/g, "").replace(/\.$/, "");
      if (summary && summary.length > 3 && !summary.toLowerCase().includes("error")) {
        await supabaseAdmin
          .from("leads")
          .update({ ideal_app_summary: summary })
          .eq("id", lead.id);
        return summary;
      }
    } catch (e: any) {
      await logToDb("ERROR", `[SUMMARIZE] Cortex summarization failed for lead ${lead.id}: ${e.message || e}`);
    }
  }

  // 2. Fallback: extract concept title from ai_plan
  if (lead.ai_plan && typeof lead.ai_plan === "object") {
    try {
      const concepts = (lead.ai_plan as any).concepts;
      const idx = typeof lead.selected_concept_index === "number" ? lead.selected_concept_index : 0;
      if (Array.isArray(concepts) && concepts[idx] && concepts[idx].title) {
        const title = concepts[idx].title.trim();
        await supabaseAdmin
          .from("leads")
          .update({ ideal_app_summary: title })
          .eq("id", lead.id);
        return title;
      }
    } catch (e) {
      // ignore
    }
  }

  // 3. Fallback: general niche app
  const fallback = `${lead.niche || "community"} app`;
  return fallback;
}

// -------------------------------------------------------------
// STEP 1: Poll & Send Abandoned Outreach Messages
// -------------------------------------------------------------
export async function checkAndSendAbandonedOutreach() {
  await logToDb("INFO", "[OUTREACH] Checking for abandoned leads...");
  // Default: 30 minutes inactivity buffer
  const timeoutMs = process.env.OUTREACH_TIMEOUT_MS ? parseInt(process.env.OUTREACH_TIMEOUT_MS) : 30 * 60 * 1000;
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
  const whopAppBaseUrl = process.env.WHOP_APP_BASE_URL || "https://whop.com/joined/app-builders-f882/get-your-free-app-here-rJQzFOett73ntx/app";

  for (const lead of leads) {
    await logToDb("INFO", `[OUTREACH] Processing lead ${lead.id} (@${lead.whop_username})...`);
    try {
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
      if (!channelId) continue;

      const rawName = (lead.first_name || "").trim();
      const isGenericName = !rawName || ["unknown", "anonymous", "null", "undefined", "there"].includes(rawName.toLowerCase());
      const firstName = isGenericName ? "there" : rawName;
      const communityPhrase = lead.niche ? `your ${lead.niche} community` : "your community";
      const goalText = lead.primary_goal ? lead.primary_goal.toLowerCase() : "grow your community";

      const text = `hey ${firstName}! saw you started building custom app concepts for ${communityPhrase} but didn't finish.\n\ntakes about 60 seconds to complete — want to see what concepts we'd build to help you ${goalText}?\n${whopAppBaseUrl}\n\nor drop your questions here and i'll help directly!`;

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

      await supabaseAdmin
        .from("leads")
        .update({ abandoned_message_sent: true })
        .eq("id", lead.id);

      await logToDb("INFO", `Success: DM outreach sent to abandoned lead @${lead.whop_username}`);
    } catch (e: any) {
      await logToDb("ERROR", `[OUTREACH] Exception processing lead ${lead.id}: ${e.message || e}`);
    }
  }
}

// -------------------------------------------------------------
// STEP 1B: Poll & Send Completed Lead Outreach Messages
// -------------------------------------------------------------
export async function sendCompletedLeadDM(leadId: string): Promise<boolean> {
  const { supabaseAdmin, CALENDLY_URL, WHOP_PAID_PRODUCT_URL } = await import("./leads.server");
  const { data: lead, error } = await supabaseAdmin
    .from("leads")
    .select("*")
    .eq("id", leadId)
    .maybeSingle();

  if (error || !lead || !lead.whop_user_id) {
    await logToDb("ERROR", `[COMPLETED_OUTREACH] Lead ${leadId} not found or missing whop_user_id`);
    return false;
  }

  if (lead.completed_message_sent) {
    await logToDb("INFO", `[COMPLETED_OUTREACH] Lead ${leadId} already sent completed message. Skipping.`);
    return true;
  }

  // --- Smart Delay Buffer Check ---
  // Give users time to browse on site before sending DM
  const createdAtMs = new Date(lead.created_at).getTime();
  const ageMinutes = (Date.now() - createdAtMs) / (1000 * 60);

  let requiredDelayMinutes = 15; // default wait 15m if no concept selected yet
  if (lead.claim_action === "skip" || lead.claim_action === "wait") {
    requiredDelayMinutes = 5; // queue decision made -> 5m delay
  } else if (lead.selected_concept_index !== null) {
    requiredDelayMinutes = 10; // concept chosen -> 10m delay
  }

  if (ageMinutes < requiredDelayMinutes) {
    await logToDb("INFO", `[COMPLETED_OUTREACH] Lead ${leadId} created ${Math.round(ageMinutes)}m ago (requires ${requiredDelayMinutes}m delay). Will retry on next daemon run.`);
    return false; // Will retry on next daemon loop once delay passes
  }

  const whopApiKey = process.env.WHOP_API_KEY;
  const whopCompanyId = process.env.WHOP_COMPANY_ID;
  const whopAppBaseUrl = process.env.WHOP_APP_BASE_URL || "https://whop.com/joined/app-builders-f882/get-your-free-app-here-rJQzFOett73ntx/app";
  const blueprintUrl = `${whopAppBaseUrl}/?blueprintId=${lead.id}`;

  try {
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
      await logToDb("ERROR", `[COMPLETED_OUTREACH] Whop API error opening channel for ${lead.whop_username}: ${errText}`);
      return false;
    }

    const channelData = await channelRes.json();
    const channelId = channelData.id;
    if (!channelId) return false;

    const rawName = (lead.first_name || "").trim();
    const isGenericName = !rawName || ["unknown", "anonymous", "null", "undefined", "there"].includes(rawName.toLowerCase());
    const firstName = isGenericName ? "there" : rawName;

    const nicheName = lead.niche || "your community";
    const summary = await summarizeIdealApp(lead);
    const goalText = lead.primary_goal ? lead.primary_goal.toLowerCase() : "grow your community";
    const mrr = lead.mrr || 0;
    const memberCount = lead.member_count || 0;
    const monthlyPrice = lead.monthly_price || 0;

    const rawUsername = (lead.whop_username || "").trim();
    const isGenericUsername = !rawUsername || ["unknown", "anonymous", "null", "undefined", "@username"].includes(rawUsername.toLowerCase());
    const userHandle = !isGenericUsername
      ? (rawUsername.startsWith("@") ? rawUsername : `@${rawUsername}`)
      : "";
    const calendlyUrl = userHandle
      ? `https://calendly.com/vilius-vaitkus/30min?a1=https%3A%2F%2Fwhop.com%2F${userHandle}`
      : `https://calendly.com/vilius-vaitkus/30min`;
    const fastTrackUrl = WHOP_PAID_PRODUCT_URL || "https://whop.com/joined/app-builders-f882/products/fast-track-app-build-3-days-or-less/";

    let text = "";

    // 1. 🔥 HOT Lead Strategy Call Pitch
    if (lead.lead_tag === "HOT") {
      text = `hey ${firstName}! just saw your blueprint for your ${nicheName} community — ${memberCount} paying members at $${monthlyPrice}/mo is a solid foundation.\n\nloved the concept for ${summary}. with that membership volume, a custom tool like this can directly help you ${goalText}.\n\ni'd love to jump on a quick 10-min call and map out exactly how we'd build & launch this for your group:\n${calendlyUrl}\n\nwhat's your schedule like this week?`;
    }
    // 2. ⚡ Chose "skip" (Fast Track intent shown)
    else if (lead.claim_action === "skip") {
      text = `hey ${firstName}! saw you selected the concept for ${summary} and chose to skip the free queue.\n\nwe have a Fast Track build slot open right now — 72-hour delivery, fully custom built for your idea:\n${fastTrackUrl}\n\nonce you grab your spot, we'll reach out immediately to lock in the build specs with you!`;
    }
    // 3. 🛡️ Chose "wait" (Confirmed free waitlist)
    else if (lead.claim_action === "wait") {
      text = `hey ${firstName}! saw you locked in the concept for ${summary} — great choice.\n\nyou're on the free waitlist right now (~4 weeks out). we actually just freed up a Fast Track build slot this week, so if you want your app live in 72 hours to ${goalText}:\n${fastTrackUrl}\n\notherwise you're all set and we'll reach out when your free slot opens!`;
    }
    // 4. 💡 Selected concept, no queue decision yet
    else if (lead.selected_concept_index !== null) {
      text = `hey ${firstName}! saw you generated your app blueprint and picked a concept for your ${nicheName} community — awesome direction.\n\njust a heads up: our standard free build queue is sitting at ~4 weeks right now. we freed up one Fast Track slot this week, so if you want to launch ${summary} in 72 hours:\n${fastTrackUrl}\n\nlet me know if you'd like to talk through any feature details first!`;
    }
    // 5. 🌐 Blueprint created, no concept selected yet
    else {
      text = `hey ${firstName}! just checking in — your custom app blueprint for your ${nicheName} community is ready to view here:\n${blueprintUrl}\n\nwhich of the concepts fits best with your goal to ${goalText}? let me know if you want help picking the right build option!`;
    }

    const msgData = await sendSupportMessage(channelId, text);
    if (msgData && msgData.id) {
      await saveProcessedMessageId(msgData.id);
    }

    await supabaseAdmin
      .from("leads")
      .update({ completed_message_sent: true })
      .eq("id", lead.id);

    await logToDb("INFO", `[COMPLETED_OUTREACH] Successfully sent tailored DM to completed lead @${lead.whop_username}`);
    return true;
  } catch (e: any) {
    await logToDb("ERROR", `[COMPLETED_OUTREACH] Exception sending DM to lead ${lead.id}: ${e.message || e}`);
    return false;
  }
}

export async function checkAndSendCompletedOutreach() {
  await logToDb("INFO", "[COMPLETED_OUTREACH] Checking for unnotified completed leads...");
  const { supabaseAdmin } = await import("./leads.server");
  const { data: leads, error } = await supabaseAdmin
    .from("leads")
    .select("id, whop_username")
    .eq("completed", true)
    .eq("completed_message_sent", false)
    .not("whop_user_id", "is", null);

  if (error) {
    await logToDb("ERROR", `[COMPLETED_OUTREACH] Error fetching completed leads: ${error.message}`);
    return;
  }

  if (!leads || leads.length === 0) {
    await logToDb("INFO", "[COMPLETED_OUTREACH] No new completed leads to message.");
    return;
  }

  await logToDb("INFO", `[COMPLETED_OUTREACH] Found ${leads.length} completed leads to notify.`);
  for (const lead of leads) {
    await sendCompletedLeadDM(lead.id);
  }
}

// -------------------------------------------------------------
// STEP 3: Poll & Send Payment Recovery Support Messages
// -------------------------------------------------------------
export async function checkAndSendPaymentRecoveryOutreach() {
  await logToDb("INFO", "[PAYMENT_RECOVERY] Checking for incomplete or failed payments...");
  const whopApiKey = process.env.WHOP_API_KEY;
  const whopCompanyId = process.env.WHOP_COMPANY_ID;

  if (!whopApiKey || !whopCompanyId) {
    await logToDb("ERROR", "[PAYMENT_RECOVERY] Missing WHOP_API_KEY or WHOP_COMPANY_ID.");
    return;
  }

  const timeoutMs = process.env.PAYMENT_RECOVERY_TIMEOUT_MS ? parseInt(process.env.PAYMENT_RECOVERY_TIMEOUT_MS) : 60 * 1000;
  const cutoffTime = Date.now() - timeoutMs;

  try {
    // 1. Fetch initial page to determine totalPages (Whop API v5 defaults to oldest-first)
    const initRes = await fetch(`https://api.whop.com/api/v5/company/payments?per=50`, {
      headers: {
        "Authorization": `Bearer ${whopApiKey}`,
        "Content-Type": "application/json",
      },
    });

    if (!initRes.ok) {
      await logToDb("ERROR", `[PAYMENT_RECOVERY] Failed to fetch payments: ${initRes.status} ${await initRes.text()}`);
      return;
    }

    const initJson = await initRes.json();
    const totalPages = initJson.pagination?.total_pages || 1;
    let payments = initJson.data || [];

    // Query the latest page for newest payments
    if (totalPages > 1) {
      const lastPageRes = await fetch(`https://api.whop.com/api/v5/company/payments?per=50&page=${totalPages}`, {
        headers: {
          "Authorization": `Bearer ${whopApiKey}`,
          "Content-Type": "application/json",
        },
      });
      if (lastPageRes.ok) {
        const lastPageJson = await lastPageRes.json();
        payments = lastPageJson.data || [];
      }
    }

    const { supabaseAdmin } = await import("./leads.server");

    // Filter candidate payments
    const candidatePayments = payments.filter((p: any) => {
      const isFailedOrIncomplete = p.status !== "paid" || p.payments_failed > 0 || p.paid_at === null;
      const hasUser = !!p.user_id;
      const createdAtMs = (p.created_at || 0) * 1000;
      const passedGracePeriod = createdAtMs < cutoffTime;
      return isFailedOrIncomplete && hasUser && passedGracePeriod;
    });

    if (candidatePayments.length === 0) {
      await logToDb("INFO", "[PAYMENT_RECOVERY] No new failed or incomplete payments requiring outreach.");
      return;
    }

    await logToDb("INFO", `[PAYMENT_RECOVERY] Found ${candidatePayments.length} candidate payment(s) to process.`);

    for (const payment of candidatePayments) {
      // Check Supabase if already messaged
      const { data: existing, error: checkErr } = await supabaseAdmin
        .from("payment_recoveries")
        .select("id, message_sent")
        .eq("payment_id", payment.id)
        .maybeSingle();

      if (checkErr) {
        await logToDb("ERROR", `[PAYMENT_RECOVERY] DB check error for ${payment.id}: ${checkErr.message}`);
      }

      if (existing && existing.message_sent) {
        continue;
      }

      // Determine failure mode and product name
      const isCardDecline = payment.payments_failed > 0 || payment.payment_method_type === "card";
      const failureMode = isCardDecline ? "failed_card" : (payment.payment_method_type === "crypto" ? "crypto_pending" : "incomplete_checkout");

      const displayName = payment.billing_address?.name 
        ? payment.billing_address.name.split(" ")[0]
        : (payment.user_username || "there");

      const knownProductMap: Record<string, string> = {
        "prod_8p51S4qc6L7Da": "Fast Track app build",
        "prod_0riDXemoZeWWR": "Fast Track app build",
        "prod_BxpjVVFgfadDd": "custom app build",
        "prod_SawduYlhOrXM4": "App Maintenance & Hosting",
        "prod_vAnUY9ZouLS6Q": "App Builders Community",
        "prod_WNwq6UKQBDc6t": "Free App Build",
      };

      const productName = (payment.product_id && knownProductMap[payment.product_id]) 
        ? knownProductMap[payment.product_id] 
        : "custom app build";

      let text = "";
      if (failureMode === "failed_card") {
        text = `hey ${displayName}, noticed your payment for the ${productName} had an issue going through. did your card get declined or did you run into any errors at checkout?`;
      } else {
        text = `hey ${displayName}, saw you started checking out for the ${productName} but didn't finish. did you get stuck on anything or have any questions?`;
      }

      // 1. Open or retrieve support channel
      const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${whopApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_id: whopCompanyId,
          user_id: payment.user_id,
        }),
      });

      if (!channelRes.ok) {
        const errText = await channelRes.text();
        await logToDb("ERROR", `[PAYMENT_RECOVERY] Error creating support channel for ${payment.user_id}: ${errText}`);
        continue;
      }

      const channelData = await channelRes.json();
      const channelId = channelData.id;
      if (!channelId) {
        await logToDb("ERROR", `[PAYMENT_RECOVERY] No channel ID in response for ${payment.id}`);
        continue;
      }

      // 2. Send the support recovery message
      let msgData;
      try {
        msgData = await sendSupportMessage(channelId, text);
      } catch (sendErr: any) {
        await logToDb("ERROR", `[PAYMENT_RECOVERY] Failed to send support message to channel ${channelId}: ${sendErr.message || sendErr}`);
        continue;
      }

      if (msgData && msgData.id) {
        await saveProcessedMessageId(msgData.id);
      }

      // 3. Record in Supabase
      const { error: dbErr } = await supabaseAdmin
        .from("payment_recoveries")
        .upsert({
          payment_id: payment.id,
          whop_user_id: payment.user_id,
          whop_username: payment.user_username || null,
          email: payment.user_email || null,
          amount: payment.final_amount || payment.subtotal || 0,
          currency: payment.currency || "USD",
          failure_mode: failureMode,
          status: payment.status || "open",
          channel_id: channelId,
          message_sent: true,
          message_content: text,
          notified_at: new Date().toISOString(),
        }, { onConflict: "payment_id" });

      if (dbErr) {
        await logToDb("ERROR", `[PAYMENT_RECOVERY] DB upsert failed for payment ${payment.id}: ${dbErr.message}`);
      } else {
        await logToDb("INFO", `[PAYMENT_RECOVERY] Successfully recorded outreach for @${payment.user_username} (${payment.id})`);
      }
    }
  } catch (err: any) {
    await logToDb("ERROR", `[PAYMENT_RECOVERY] Exception during check: ${err.message || err}`);
  }
}

// -------------------------------------------------------------
// STEP 4: Poll & Handle Incoming User Replies (Chatbot)
// -------------------------------------------------------------
export async function handleChatbotReplies() {
  await logToDb("INFO", "[CHATBOT] Polling support channels...");
  const processedIds = await getProcessedMessageIds();
  const whopApiKey = process.env.WHOP_API_KEY;
  const botUserId = process.env.BOT_USER_ID || "user_tFompFhTYu2xr";

  const channelsUrl = `https://api.whop.com/api/v1/dm_channels?first=50`;
  try {
    const { supabaseAdmin } = await import("./leads.server");

    // Gather channels from Whop dm_channels API
    const channelMap = new Map<string, { id: string; name: string }>();
    try {
      const res = await fetch(channelsUrl, {
        headers: {
          "Authorization": `Bearer ${whopApiKey}`,
          "Content-Type": "application/json",
        },
      });

      if (res.ok) {
        const channelsData = await res.json();
        for (const chan of (channelsData.data || [])) {
          if (chan.id) {
            channelMap.set(chan.id, { id: chan.id, name: chan.name || "support chat" });
          }
        }
      }
    } catch (e) {
      await logToDb("ERROR", `[CHATBOT] Failed fetching dm_channels: ${e}`);
    }

    // Gather ALL leads with ai_bot_enabled = true PLUS the 50 most recent incomplete leads
    try {
      const { data: enabledLeads } = await supabaseAdmin
        .from("leads")
        .select("scraped_data")
        .eq("ai_bot_enabled", true)
        .not("scraped_data", "is", null);

      if (enabledLeads) {
        for (const lead of enabledLeads) {
          const chanId = (lead.scraped_data as any)?.support_channel_id;
          if (chanId && !channelMap.has(chanId)) {
            channelMap.set(chanId, { id: chanId, name: "support chat" });
          }
        }
      }

      const { data: incompleteLeads } = await supabaseAdmin
        .from("leads")
        .select("scraped_data")
        .eq("completed", false)
        .not("scraped_data", "is", null)
        .order("created_at", { ascending: false })
        .limit(50);

      if (incompleteLeads) {
        for (const lead of incompleteLeads) {
          const chanId = (lead.scraped_data as any)?.support_channel_id;
          if (chanId && !channelMap.has(chanId)) {
            channelMap.set(chanId, { id: chanId, name: "support chat" });
          }
        }
      }
    } catch (dbChanErr) {
      await logToDb("ERROR", `[CHATBOT] Failed fetching DB lead support channels: ${dbChanErr}`);
    }

    const channels = Array.from(channelMap.values());
    const processedIds = await getProcessedMessageIds();

    // Helper to process a single channel
    const processChannel = async (chan: { id: string; name: string }) => {
      const channelId = chan.id;
      const channelName = chan.name || "";
      const isSupport = channelName.toLowerCase().includes("support chat") || channelName === "";

      if (!isSupport) return;

      // Fetch messages in this channel
      const msgUrl = `https://api.whop.com/api/v1/messages?channel_id=${channelId}&first=10&direction=desc`;
      const msgRes = await fetch(msgUrl, {
        headers: {
          "Authorization": `Bearer ${whopApiKey}`,
          "Content-Type": "application/json",
        },
      });

      if (!msgRes.ok) return;

      const msgsData = await msgRes.json();
      const messages = msgsData.data || [];
      if (messages.length === 0) return;

      const latestMsg = messages[0];
      const sender = latestMsg.user || {};
      const senderId = sender.id;
      const senderName = sender.username || sender.name || "User";

      const botUserIds = new Set([
        botUserId,
        process.env.BOT_USER_ID,
        "user_P5obcMW3vIrZ8",
        "user_tFompFhTYu2xr",
        process.env.WHOP_COMPANY_ID,
      ].filter(Boolean));

      const botNames = [
        "teamwhop",
        "emailsapp",
        "whop",
        "system",
        "app builders",
        "vilius vaitkus",
        "app-developer-will",
        "appdeveloperwill",
        "appdevelopment",
        "app builder",
      ];

      const isBotOrAdmin =
        botUserIds.has(senderId) ||
        botNames.some(name => senderName.toLowerCase().includes(name));

      if (isBotOrAdmin) {
        // Check for 24h inactivity follow-up on bot-activated leads
        try {
          const { data: channelLeads } = await supabaseAdmin
            .from("leads")
            .select("*")
            .eq("scraped_data->>support_channel_id", channelId)
            .order("created_at", { ascending: false })
            .limit(1);

          const lead = channelLeads && channelLeads.length > 0 ? channelLeads[0] : null;
          if (lead) {
            const globalChatbotEnabled = (await getSetting("chatbot_enabled", "false")) === "true";
            const isAiEnabled = lead.ai_bot_enabled || globalChatbotEnabled;

            if (isAiEnabled) {
              const msgCreatedAt = latestMsg.created_at || latestMsg.created_at_date;
              if (msgCreatedAt) {
                const msgTime = new Date(msgCreatedAt).getTime();
                const hoursPassed = (Date.now() - msgTime) / (1000 * 60 * 60);

                if (hoursPassed >= 24) {
                  const scraped = (lead.scraped_data || {}) as any;
                  if (scraped.followup_last_msg_id !== latestMsg.id) {
                    const rawName = (lead.first_name || lead.whop_username || "").trim();
                    const isGenericName = !rawName || ["unknown", "anonymous", "null", "undefined", "there"].includes(rawName.toLowerCase());
                    const nameStr = isGenericName ? "there" : `@${rawName}`;

                    const followUpText = `hey ${nameStr}! just checking in — you still here?`;

                    const msgData = await sendSupportMessage(channelId, followUpText);
                    const newMsgId = msgData?.id || latestMsg.id;
                    if (msgData && msgData.id) {
                      await saveProcessedMessageId(msgData.id);
                    }

                    const updatedScraped = {
                      ...scraped,
                      followup_24h_sent: true,
                      followup_last_msg_id: newMsgId,
                      last_followup_at: new Date().toISOString(),
                    };

                    await supabaseAdmin
                      .from("leads")
                      .update({ scraped_data: updatedScraped })
                      .eq("id", lead.id);

                    await logToDb("INFO", `[CHATBOT] Sent 24h follow-up to @${lead.whop_username || "user"} in channel ${channelId}: "${followUpText}"`);
                  }
                }
              }
            }
          }
        } catch (followupErr: any) {
          console.error(`[CHATBOT] Error evaluating 24h followup for channel ${channelId}:`, followupErr);
        }
        return;
      }

      // Check if message was already processed
      if (processedIds.has(latestMsg.id)) return;

      await logToDb("INFO", `[CHATBOT] New message in channel ${channelId} from @${senderName}: "${latestMsg.content}"`);

      // Find the corresponding lead in Supabase
      const { data: leads, error: leadError } = await supabaseAdmin
        .from("leads")
        .select("*")
        .eq("whop_user_id", senderId)
        .order("created_at", { ascending: false })
        .limit(1);

      const lead = leads && leads.length > 0 ? leads[0] : null;

      if (leadError) {
        await logToDb("ERROR", `[CHATBOT] DB Error looking up lead for user ${senderId}: ${leadError.message}`);
        return;
      }

      if (!lead) {
        await logToDb("INFO", `[CHATBOT] No lead found in DB for user ${senderId} (@${senderName}). Skipping.`);
        await saveProcessedMessageId(latestMsg.id);
        return;
      }

      // Check if AI Bot is enabled for this lead or globally
      const globalChatbotEnabled = (await getSetting("chatbot_enabled", "false")) === "true";
      const isAiEnabled = lead.ai_bot_enabled || globalChatbotEnabled;

      if (!isAiEnabled) {
        await logToDb("INFO", `[CHATBOT] User @${senderName} replied, but AI bot is OFF for lead ${lead.id}.`);
        
        // Telegram notifications for support messages are disabled by default
        const supportNotificationsEnabled = (await getSetting("telegram_support_notifications_enabled", "false")) === "true";
        if (supportNotificationsEnabled) {
          try {
            const supportChatLink = `https://whop.com/messages/?chat=${channelId}`;
            const token = process.env.TELEGRAM_BOT_TOKEN;
            const chatId = process.env.TELEGRAM_CHAT_ID;
            if (token && chatId) {
              let userLocStr = "";
              try {
                const { resolveWhopLocation } = await import("./location.server");
                const loc = await resolveWhopLocation(senderId, senderName);
                if (loc && (loc.country || loc.city)) {
                  const flag = loc.country_flag || "🌐";
                  const locPart = loc.city ? `${loc.city}, ${loc.country_name || loc.country}` : (loc.country_name || loc.country);
                  userLocStr = ` ${flag} (${locPart})`;
                }
              } catch {
                // ignore
              }

              const alertMsg =
                `💬 <b>New Support Chat Reply</b> (AI Bot OFF)\n` +
                `User: <b>@${senderName}</b>${userLocStr} (${lead.first_name || "Lead"})\n` +
                `Status: ${lead.completed ? "Completed Lead" : "Incomplete Lead"}\n` +
                `Message: <i>"${latestMsg.content}"</i>\n\n` +
                `👉 <a href="${supportChatLink}">Open Whop Support Chat</a>`;

              await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  chat_id: chatId,
                  text: alertMsg,
                  parse_mode: "HTML",
                  disable_web_page_preview: true,
                }),
              });
            }
          } catch (tgErr) {
            console.error("[CHATBOT] Telegram reply alert failed:", tgErr);
          }
        }
        return;
      }

      if (lead.completed) {
        await processLeadCompletedChat(lead, latestMsg, messages, channelId, botUserId);
        return;
      }

      // We have an incomplete lead! Let's process the conversation state.
      await processLeadOnboardingChat(lead, latestMsg, messages, channelId, botUserId);
    };

    // Process channels in parallel chunks of 10 for maximum performance
    const chunkSize = 10;
    for (let i = 0; i < channels.length; i += chunkSize) {
      const chunk = channels.slice(i, i + chunkSize);
      await Promise.all(chunk.map(c => processChannel(c)));
    }
  } catch (e: any) {
    await logToDb("ERROR", `[CHATBOT] Exception polling channels: ${e.message || e}`);
  }
}

// Conversation processing for COMPLETED leads (answering questions about concepts, build timing, etc.)
async function processLeadCompletedChat(lead: any, latestMsg: any, messages: any[], channelId: string, botUserId: string) {
  const chatHistory = messages
    .slice()
    .reverse()
    .map((m: any) => {
      const isBot = m.user?.id === botUserId;
      return `${isBot ? "Assistant" : "User"}: ${m.content}`;
    })
    .join("\n");

  const hostUrl = process.env.APP_URL || "https://free-app-flow.vercel.app";
  const blueprintUrl = `${hostUrl}/blueprint/${lead.id}`;

  const systemPrompt = `You are a friendly, expert Whop App Builder consultant. The user (@${lead.whop_username || lead.first_name}) has ALREADY completed their onboarding and received their custom app concepts.

Lead Details:
- Name: ${lead.first_name}
- Niche: ${lead.niche}
- Member Count: ${lead.member_count}
- MRR: $${lead.mrr}
- Lead Tag: ${lead.lead_tag}
- Blueprint URL: ${blueprintUrl}

Generated App Concepts:
${JSON.stringify(lead.ai_plan, null, 2)}

Your goal is to answer their questions, guide them on which concept fits best, explain how the free build process works, or help them pick an option to get started!

CRITICAL RULES:
- Keep the response text very human, casual, and brief (1-3 sentences). Use lowercase letters mostly, dropped punctuation, and natural spacing. No emojis.
- Never mention prices, hosting fees, setup fees, or deposits unless specifically asked. The design and custom development are 100% free.
- If they ask which option is best, recommend Option A or B based on their niche and mention why.
- Always be super helpful, concise, and encourage them to pick their concept on their blueprint link: ${blueprintUrl}`;

  await logToDb("INFO", `[CHATBOT] Responding to completed lead reply from @${lead.whop_username}...`);
  try {
    const userPrompt = `Here is the full conversation history:\n${chatHistory}\n\nPlease respond to the user's latest message naturally as the assistant.`;
    const replyText = await generateCortexResponse(systemPrompt, userPrompt);

    let cleanedReply = replyText.trim();
    if (cleanedReply.startsWith('"') && cleanedReply.endsWith('"')) {
      cleanedReply = cleanedReply.slice(1, -1);
    }

    const msgData = await sendSupportMessage(channelId, cleanedReply);
    if (msgData && msgData.id) {
      await saveProcessedMessageId(msgData.id);
    }
    await saveProcessedMessageId(latestMsg.id);
    await logToDb("INFO", `[CHATBOT] Sent AI reply to completed lead @${lead.whop_username}: "${cleanedReply}"`);
  } catch (e: any) {
    await logToDb("ERROR", `[CHATBOT] Error replying to completed lead ${lead.whop_username}: ${e.message || e}`);
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
    await checkAndSendCompletedOutreach();
    await checkAndSendPaymentRecoveryOutreach();
    await handleChatbotReplies();
    await logToDb("INFO", "[DAEMON] Cron Tick completed successfully.");
  } catch (e: any) {
    await logToDb("ERROR", `[DAEMON] Error during Cron Tick: ${e.message || e}`);
    throw e;
  }
}
