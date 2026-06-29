// Server-only helpers for leads — scrape + AI blueprint generation.
import { supabaseAdmin } from "@/integrations/supabase/client.server";

export const WHOP_PAID_PRODUCT_URL =
  "https://whop.com/joined/app-builders-f882/products/fast-track-app-build-3-days-or-less/";
export const CALENDLY_URL = "";
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

export async function generateBlueprint(lead: LeadInput, scraped: ScrapeResult): Promise<unknown> {
  const key = process.env.LOVABLE_API_KEY;
  if (!key) throw new Error("Missing LOVABLE_API_KEY");
  const annual = Math.round((lead.member_count * lead.monthly_price) * 3);

  try {
    const res = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Lovable-API-Key": key,
      },
      body: JSON.stringify({
        model: "google/gemini-3-flash-preview",
        messages: [
          {
            role: "system",
            content:
              "You design retention apps for Whop community owners. Always respond with valid JSON only — no prose, no markdown fences.",
          },
          { role: "user", content: claudePrompt(lead, scraped) },
        ],
      }),
    });
    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      throw new Error(`AI gateway ${res.status}: ${errText.slice(0, 200)}`);
    }
    const data = await res.json();
    const text: string = data?.choices?.[0]?.message?.content ?? "";
    return extractJson(text);
  } catch (err) {
    console.error("[generateBlueprint] fallback:", err);
    return {
      concepts: [
        {
          name: `${lead.niche} Daily Edge`,
          tagline: "A focused daily digest that surfaces only what each member needs.",
          benefits: [
            `Cuts noise for your ${lead.member_count} members`,
            "Members see value within the first 7 days",
            "Replaces overwhelm with focus",
          ],
          fits_because: "Solves information overload — the #1 churn driver in active communities.",
        },
        {
          name: `${lead.niche} Streaks`,
          tagline: "A gamified streak system that rewards sticky engagement.",
          benefits: [
            "Members compete for streaks instead of churning",
            "Visible progress = perceived value",
            "Drives habit-level engagement",
          ],
          fits_because: "Turns habit formation into a retention engine.",
        },
        {
          name: `${lead.niche} Quick-Win Tracker`,
          tagline: "Shows each member tangible wins from their membership.",
          benefits: [
            "Makes ROI visible in week 1",
            `Protects roughly $${annual.toLocaleString()}/year currently lost to churn`,
            "Reduces cancel-button regret",
          ],
          fits_because: "Members who can SEE their progress cancel 30-50% less.",
        },
      ],
      estimated_value_add: `Your community is losing an estimated $${annual.toLocaleString()}/year to preventable churn — this protects it.`,
    };
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
}

export async function notifyTelegram(p: NotifyPayload): Promise<void> {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) {
    console.warn("[notifyTelegram] missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID");
    return;
  }
  const emoji = p.lead_tag === "HOT" ? "🔥" : p.lead_tag === "WARM" ? "🌤️" : "❄️";
  const esc = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const text =
    `${emoji} <b>New ${p.lead_tag} Lead</b> (score ${p.lead_score})\n` +
    `<b>${esc(p.first_name)}</b> — ${esc(p.email)}\n` +
    `Niche: ${esc(p.niche)}\n` +
    `Members: ${p.member_count} × $${p.monthly_price} = <b>$${p.mrr.toLocaleString()} MRR</b>\n` +
    `Timeline: ${esc(p.timeline)}\n` +
    (p.social_handle ? `Social: ${esc(p.social_handle)}\n` : "") +
    (p.ideal_app ? `Idea: ${esc(p.ideal_app).slice(0, 200)}\n` : "") +
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
