// Server-only helpers for leads — scrape + AI blueprint generation.
import { supabaseAdmin } from "@/integrations/supabase/client.server";

export const WHOP_PAID_PRODUCT_URL =
  "https://whop.com/joined/app-builders-f882/products/fast-track-app-build-3-days-or-less/";
export const CALENDLY_BASE_URL = "https://calendly.com/vilius-vaitkus/30min";

export function getCalendlyUrl(whopUsername?: string | null): string {
  const raw = (whopUsername || "").trim();
  const isGeneric = !raw || ["unknown", "anonymous", "null", "undefined", "@username"].includes(raw.toLowerCase());
  if (isGeneric) {
    return CALENDLY_BASE_URL;
  }
  const handle = raw.startsWith("@") ? raw : `@${raw}`;
  return `${CALENDLY_BASE_URL}?a1=https%3A%2F%2Fwhop.com%2F${handle}`;
}

export const CALENDLY_URL = CALENDLY_BASE_URL;
export const FREE_SPOTS_LEFT = 2;
export const FREE_SPOTS_TOTAL = 10;
export const FREE_WAIT_WEEKS = 4;

export interface ScrapeResult {
  status: "Success" | "Failed" | "Partial";
  title?: string;
  description?: string;
  raw_excerpt?: string;
}

export async function lightweightScrape(url: string): Promise<ScrapeResult> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 5000);
    const res = await fetch(url, {
      signal: controller.signal,
      headers: { "User-Agent": "Mozilla/5.0 WOPAppLabBot/1.0" },
    });
    clearTimeout(timer);
    if (!res.ok) return { status: "Failed" };
    const html = await res.text();
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
    const descMatch = html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["']/i)
      || html.match(/<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']+)["']/i);
    return {
      status: "Success",
      title: titleMatch?.[1]?.trim().slice(0, 200),
      description: descMatch?.[1]?.trim().slice(0, 400),
      raw_excerpt: html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 800),
    };
  } catch {
    return { status: "Failed" };
  }
}

export function calcLeadScore(memberCount: number | null, monthlyPrice: number | null, timeline: string) {
  const mrr = (memberCount ?? 0) * (monthlyPrice ?? 0);
  let score = 0;
  if (mrr >= 10000) score += 50;
  else if (mrr >= 3000) score += 35;
  else if (mrr >= 1000) score += 20;
  else if (mrr >= 300) score += 10;
  if (timeline === "ASAP / within 1 week") score += 35;
  else if (timeline === "Within a month") score += 20;
  else score += 5;
  if ((memberCount ?? 0) >= 500) score += 15;
  else if ((memberCount ?? 0) >= 100) score += 8;
  let tag: "HOT" | "WARM" | "COLD" = "COLD";
  if (score >= 70) tag = "HOT";
  else if (score >= 40) tag = "WARM";
  return { mrr, score, tag };
}

interface LeadInput {
  whop_url: string;
  niche: string;
  member_count: number;
  monthly_price: number;
  ideal_app: string;
  timeline: string;
  first_name: string;
}

function claudePrompt(lead: LeadInput, scraped: ScrapeResult): string {
  const annual = Math.round((lead.member_count * lead.monthly_price) * 3);
  return `You are a senior product strategist helping a Whop community owner reduce churn.

Owner profile:
- First name: ${lead.first_name}
- Whop URL: ${lead.whop_url}
- Niche: ${lead.niche}
- Active members: ${lead.member_count}
- Monthly price/member: $${lead.monthly_price}
- Estimated revenue at risk to churn: ~$${annual.toLocaleString()}/year
- Launch timeline: ${lead.timeline}
- Their ideal app idea (may be blank): ${lead.ideal_app || "(none)"}

Scrape from their Whop page:
- Title: ${scraped.title || "n/a"}
- Description: ${scraped.description || "n/a"}
- Excerpt: ${scraped.raw_excerpt?.slice(0, 400) || "n/a"}

Propose THREE distinct concept options that take DIFFERENT angles on stopping churn.
If the owner described their ideal version, ONE concept MUST clearly build on their idea (reference it in fits_because). Keep each option simple and shippable in ~2 weeks, tightly fitted to THIS community.

DO NOT mention pricing, cost, hosting, fees, deposits, or money the owner would pay.
Only describe what the apps DO and what they GAIN.

Respond ONLY with valid JSON in this EXACT structure (no markdown, no fences):
{
  "concepts": [
    { "name": "...", "tagline": "...", "benefits": ["...","...","..."], "fits_because": "..." },
    { "name": "...", "tagline": "...", "benefits": ["...","...","..."], "fits_because": "..." },
    { "name": "...", "tagline": "...", "benefits": ["...","...","..."], "fits_because": "..." }
  ],
  "estimated_value_add": "concrete framing of revenue protected by reducing churn"
}`;
}

function extractJson(text: string): unknown {
  let t = text.trim();
  if (t.startsWith("```")) t = t.replace(/^```(?:json)?/i, "").replace(/```\s*$/, "").trim();
  const m = t.match(/\{[\s\S]*\}/);
  if (m) t = m[0];
  return JSON.parse(t);
}

export function buildFallbackBlueprint(lead: LeadInput): { concepts: any[]; estimated_value_add: string } {
  const nicheName = lead.niche ? lead.niche.charAt(0).toUpperCase() + lead.niche.slice(1) : "Community";
  const annual = Math.round((lead.member_count || 0) * (lead.monthly_price || 0) * 3);
  const memberText = lead.member_count > 0 ? `your ${lead.member_count} members` : "your future members";

  let concept1Name = `${nicheName} Pro Command Hub`;
  let concept1Tagline = `A custom experience tailored specifically to your ${nicheName} members.`;
  let concept1Fits = `Built directly for ${nicheName} communities to maximize daily engagement.`;

  if (lead.ideal_app && lead.ideal_app.trim()) {
    const rawIdea = lead.ideal_app.trim();
    const shortIdea = rawIdea.length > 50 ? rawIdea.slice(0, 47) + "..." : rawIdea;
    const cleanIdeaTitle = shortIdea.replace(/^(a|an|the)\s+/i, "");
    concept1Name = `${nicheName} ${cleanIdeaTitle.charAt(0).toUpperCase() + cleanIdeaTitle.slice(1)}`;
    concept1Tagline = `Your custom vision ("${shortIdea}") built into a high-retention app.`;
    concept1Fits = `Directly builds on your idea: "${shortIdea}" to maximize member satisfaction.`;
  }

  const concept1 = {
    name: concept1Name,
    tagline: concept1Tagline,
    benefits: [
      `Cuts noise for ${memberText}`,
      "Members see immediate value within their first 7 days",
      "Delivers an exclusive experience members cannot get elsewhere",
    ],
    fits_because: concept1Fits,
  };

  const concept2 = {
    name: `${nicheName} Habit & Streak Engine`,
    tagline: "A gamified streak system that rewards sticky daily engagement.",
    benefits: [
      "Members log in daily to protect their progress streaks",
      "Creates friendly competition with community leaderboards",
      "Turns passive lurkers into active daily users",
    ],
    fits_because: "Gamification is proven to cut cancellation rates in active membership communities.",
  };

  const concept3 = {
    name: `${nicheName} Quick-Win & ROI Tracker`,
    tagline: "Shows members clear proof of the value and results they gain every week.",
    benefits: [
      "Makes member progress visible from week 1",
      annual > 0 
        ? `Protects ~$${annual.toLocaleString()}/year currently lost to preventable churn`
        : "Builds instant trust and social proof for your upcoming launch",
      "Reduces cancel-button regret by proving clear member outcomes",
    ],
    fits_because: "Members who can see their progress cancel 30-50% less.",
  };

  const estimatedValue = annual > 0
    ? `Your community is losing an estimated $${annual.toLocaleString()}/year to preventable churn — this blueprint protects it.`
    : `Tailored launch architecture to convert early interest into high-retention paying members.`;

  return {
    concepts: [concept1, concept2, concept3],
    estimated_value_add: estimatedValue,
  };
}

export async function generateBlueprint(lead: LeadInput, scraped: ScrapeResult): Promise<unknown> {
  try {
    const { generateCortexResponse } = await import("./cortex.server");
    const systemPrompt =
      "You design retention apps for Whop community owners. Always respond with valid JSON only — no prose, no markdown fences.";
    const userPrompt = claudePrompt(lead, scraped);
    
    const text = await generateCortexResponse(systemPrompt, userPrompt);
    const parsed = extractJson(text) as any;
    if (parsed && Array.isArray(parsed.concepts) && parsed.concepts.length > 0) {
      return parsed;
    }
    console.warn("[generateBlueprint] AI returned JSON without valid concepts array, using fallback.");
    return buildFallbackBlueprint(lead);
  } catch (err) {
    console.error("[generateBlueprint] fallback triggered due to AI error:", err);
    return buildFallbackBlueprint(lead);
  }
}

export { supabaseAdmin };

interface NotifyPayload {
  id: string;
  first_name: string;
  email: string;
  niche: string;
  whop_url: string;
  member_count: number;
  monthly_price: number;
  mrr: number;
  lead_tag: "HOT" | "WARM" | "COLD";
  lead_score: number;
  timeline: string;
  social_handle: string;
  ideal_app: string;
  whop_username?: string | null;
  whop_user_id?: string | null;
  willing_to_invest?: string | null;
  social_type?: string | null;
  primary_goal?: string | null;
  country?: string | null;
  city?: string | null;
  timezone?: string | null;
}

export async function notifyTelegram(p: NotifyPayload): Promise<void> {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) {
    console.warn("[notifyTelegram] missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID");
    return;
  }

  // Attempt to resolve location & LTV spend info
  let locLine = "";
  let spendLine = "";
  try {
    const { resolveWhopLocation, getCountryFlag, getCountryName } = await import("./location.server");
    const loc = await resolveWhopLocation(p.whop_user_id, p.whop_username, p.country);
    
    const countryCode = loc?.country || p.country || null;
    const countryFlag = loc?.country_flag || (countryCode ? getCountryFlag(countryCode) : "🌐");
    const countryName = loc?.country_name || (countryCode ? getCountryName(countryCode) : null);
    const city = loc?.city || p.city || null;

    const locParts = [];
    if (city) locParts.push(city);
    if (countryName) locParts.push(`${countryName}${countryCode ? ` (${countryCode})` : ''}`);
    else if (countryCode) locParts.push(countryCode);

    if (locParts.length > 0) {
      locLine = `Country: ${countryFlag} <b>${esc(locParts.join(", "))}</b>\n`;
    } else if (countryFlag !== "🌐") {
      locLine = `Country: ${countryFlag}\n`;
    }

    const ltv = loc?.ltv ?? 0;
    const purchases = loc?.purchase_count ?? 0;
    spendLine = `Whop Spend (LTV): <b>$${ltv.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</b>${purchases > 0 ? ` (${purchases} ${purchases === 1 ? 'purchase' : 'purchases'})` : ''}\n`;
  } catch (locErr) {
    console.warn("[notifyTelegram] location resolution error:", locErr);
  }

  // Attempt to resolve support chat channel ID
  let supportChatLink = "";
  if (p.whop_user_id && process.env.WHOP_API_KEY && process.env.WHOP_COMPANY_ID) {
    try {
      const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${process.env.WHOP_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_id: process.env.WHOP_COMPANY_ID,
          user_id: p.whop_user_id,
        }),
      });
      if (channelRes.ok) {
        const channelData = await channelRes.json();
        const channelId = channelData.id;
        if (channelId) {
          supportChatLink = `https://whop.com/messages/?chat=${channelId}`;
        }
      }
    } catch (e) {
      console.error("[notifyTelegram] failed to resolve support channel link:", e);
    }
  }

  const emoji = p.lead_tag === "HOT" ? "🔥" : p.lead_tag === "WARM" ? "🌤️" : "❄️";
  const esc = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  
  let text =
    `${emoji} <b>New ${p.lead_tag} Lead</b> (score ${p.lead_score})\n` +
    `<b>${esc(p.first_name)}</b> — ${esc(p.email)}\n`;

  if (locLine) {
    text += locLine;
  }
  if (spendLine) {
    text += spendLine;
  }

  text +=
    `Niche: ${esc(p.niche)}\n` +
    `Members: ${p.member_count} × $${p.monthly_price} = <b>$${p.mrr.toLocaleString()} MRR</b>\n` +
    `Timeline: ${esc(p.timeline)}\n`;

  if (p.willing_to_invest) {
    text += `Willing to Invest: ${esc(p.willing_to_invest)}\n`;
  }

  if (p.whop_username) {
    text += `Whop Profile: <a href="https://whop.com/@${esc(p.whop_username)}">@${esc(p.whop_username)}</a>\n`;
  }
  
  if (p.social_handle) {
    const platform = p.social_type
      ? p.social_type.charAt(0).toUpperCase() + p.social_type.slice(1)
      : "Social";
    text += `${platform}: ${esc(p.social_handle)}\n`;
  }
  
  if (p.ideal_app) {
    text += `Idea: ${esc(p.ideal_app).slice(0, 200)}\n`;
  }

  if (p.primary_goal) {
    text += `Goal: <b>${esc(p.primary_goal)}</b>\n`;
  }

  if (supportChatLink) {
    text += `Support Chat: <a href="${supportChatLink}">Open Chat</a>\n`;
  }

  text +=
    `Whop: ${esc(p.whop_url)}\n` +
    `Lead ID: <code>${p.id}</code>`;

  try {
    const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: "HTML",
        disable_web_page_preview: true,
      }),
    });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      console.error(`[notifyTelegram] ${res.status}: ${body.slice(0, 200)}`);
    }
  } catch (e) {
    console.error("[notifyTelegram] fetch failed:", e);
  }
}

