// Server-side Whop location & demographics resolver
// Queries Whop GeoIP telemetry from /api/v1/people and /api/v5/company/payments with in-memory caching.

export interface WhopLocationInfo {
  country: string | null; // 2-letter ISO (e.g. "US", "IN", "GB")
  country_name: string | null; // Full name (e.g. "United States", "India")
  country_flag: string; // Emoji flag (e.g. "🇺🇸", "🇮🇳")
  city?: string | null;
  timezone: string | null; // e.g. "America/Chicago", "Asia/Calcutta"
  device: string | null; // e.g. "Android · Chrome (mobile)"
  ltv?: number; // Lifetime spend in USD
  purchase_count?: number; // Total purchases count
  profile_earnings_badge?: string | null; // Public profile badge e.g. "$2,719.35"
  profile_earnings_usd?: number | null; // Public profile USD number e.g. 2719.35
  display: string; // Formatted summary string
}

// Convert 2-letter ISO country code to flag emoji
export function getCountryFlag(countryCode?: string | null): string {
  if (!countryCode || countryCode.trim().length !== 2) return "🌐";
  const upper = countryCode.trim().toUpperCase();
  if (!/^[A-Z]{2}$/.test(upper)) return "🌐";
  const codePoints = upper.split("").map((char) => 127397 + char.charCodeAt(0));
  try {
    return String.fromCodePoint(...codePoints);
  } catch {
    return "🌐";
  }
}

// Convert 2-letter ISO country code to English country name
export function getCountryName(countryCode?: string | null): string {
  if (!countryCode || countryCode.trim().length !== 2) return "";
  const upper = countryCode.trim().toUpperCase();
  try {
    const regionNames = new Intl.DisplayNames(["en"], { type: "region" });
    return regionNames.of(upper) || upper;
  } catch {
    return upper;
  }
}

interface CachedPeopleCache {
  timestamp: number;
  byUserId: Map<string, WhopLocationInfo>;
  byUsername: Map<string, WhopLocationInfo>;
}

let _peopleCache: CachedPeopleCache | null = null;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes cache

async function refreshPeopleCache(): Promise<CachedPeopleCache> {
  const apiKey = process.env.WHOP_API_KEY || process.env.WHOP_COMPANY_API_KEY;
  const companyId = process.env.WHOP_COMPANY_ID;

  const byUserId = new Map<string, WhopLocationInfo>();
  const byUsername = new Map<string, WhopLocationInfo>();

  if (!apiKey || !companyId) {
    return { timestamp: Date.now(), byUserId, byUsername };
  }

  try {
    // Fetch top 200 recent visitors/members from /api/v1/people (< 500ms response time)
    let after: string | null = null;
    let pageCount = 0;
    const maxPages = 2;

    while (pageCount < maxPages) {
      let url = `https://api.whop.com/api/v1/people?company_id=${companyId}&first=100`;
      if (after) url += `&after=${after}`;

      const res = await fetch(url, {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
      });

      if (!res.ok) {
        console.warn(`[WhopLocation] People API returned status ${res.status}`);
        break;
      }

      const json = await res.json();
      const people = json.data || [];

      for (const p of people) {
        const country = p.location?.country ? String(p.location.country).toUpperCase() : null;
        const city = p.location?.city ? String(p.location.city) : null;
        const timezone = p.timezone ? String(p.timezone) : null;
        const country_name = country ? getCountryName(country) : null;
        const country_flag = getCountryFlag(country);

        let device: string | null = null;
        if (p.device) {
          const parts = [p.device.os, p.device.browser, p.device.device].filter(Boolean);
          if (parts.length > 0) device = parts.join(" · ");
        }

        const displayParts: string[] = [];
        if (country_flag) displayParts.push(country_flag);
        if (city) displayParts.push(city);
        if (country_name) displayParts.push(country_name);
        else if (country) displayParts.push(country);

        const ltv = typeof p.ltv === "number" ? p.ltv : typeof p.member?.usd_total_spend === "number" ? p.member.usd_total_spend : 0;
        const purchase_count = typeof p.purchase_count === "number" ? p.purchase_count : 0;

        const locInfo: WhopLocationInfo = {
          country,
          country_name,
          country_flag,
          city,
          timezone,
          device,
          ltv,
          purchase_count,
          display: displayParts.join(" ") || "Unknown",
        };

        const uid = p.user?.id || p.id;
        const uname = p.user?.username || p.name;

        if (uid) byUserId.set(uid, locInfo);
        if (uname) byUsername.set(uname.toLowerCase().replace(/^@/, "").trim(), locInfo);
      }

      if (!json.page_info?.has_next_page || !json.page_info?.end_cursor) {
        break;
      }
      after = json.page_info.end_cursor;
      pageCount++;
    }
  } catch (err) {
    console.error("[WhopLocation] Failed to refresh people cache:", err);
  }

  const cache = { timestamp: Date.now(), byUserId, byUsername };
  _peopleCache = cache;
  return cache;
}

async function getPeopleCache(): Promise<CachedPeopleCache> {
  if (_peopleCache && Date.now() - _peopleCache.timestamp < CACHE_TTL_MS) {
    return _peopleCache;
  }
  return refreshPeopleCache();
}

/**
 * Resolves location info for a given Whop user_id or username
 */
export async function resolveWhopLocation(
  whopUserId?: string | null,
  whopUsername?: string | null,
  fallbackCountry?: string | null
): Promise<WhopLocationInfo> {
  const cache = await getPeopleCache();

  if (whopUserId && cache.byUserId.has(whopUserId)) {
    return cache.byUserId.get(whopUserId)!;
  }

  if (whopUsername) {
    const clean = whopUsername.toLowerCase().replace(/^@/, "").trim();
    if (clean && clean !== "anonymous" && clean !== "unknown" && cache.byUsername.has(clean)) {
      return cache.byUsername.get(clean)!;
    }
  }

  // Fallback to provided country (e.g. from Cloudflare / Vercel request headers)
  if (fallbackCountry && fallbackCountry.length === 2) {
    const country = fallbackCountry.toUpperCase();
    const country_name = getCountryName(country);
    const country_flag = getCountryFlag(country);
    return {
      country,
      country_name,
      country_flag,
      city: null,
      timezone: null,
      device: null,
      display: `${country_flag} ${country_name || country}`,
    };
  }

  return {
    country: null,
    country_name: null,
    country_flag: "🌐",
    city: null,
    timezone: null,
    device: null,
    display: "Unknown",
  };
}

const _profileEarningsCache = new Map<string, { badge: string | null; exact_usd: number | null }>();

export async function getWhopProfileEarnings(username?: string | null): Promise<{ badge: string | null; exact_usd: number | null }> {
  if (!username) return { badge: null, exact_usd: null };
  const clean = username.toLowerCase().replace(/^@/, "").trim();
  if (!clean || clean === "anonymous" || clean === "unknown") return { badge: null, exact_usd: null };

  if (_profileEarningsCache.has(clean)) {
    return _profileEarningsCache.get(clean)!;
  }

  try {
    const res = await fetch(`https://whop.com/@${clean}`, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      },
      signal: AbortSignal.timeout(2000),
    });
    if (res.ok) {
      const html = await res.text();
      const badgeMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i);
      const usdMatch = html.match(/totalEarningsWithTransfersInUsd:"([\d\.]+)"/);

      let badge = badgeMatch ? badgeMatch[1] : null;
      let exact_usd: number | null = null;
      if (badge) {
        exact_usd = parseFloat(badge.replace(/[\$,]/g, ""));
      } else if (usdMatch) {
        exact_usd = parseFloat(usdMatch[1]);
        badge = `$${exact_usd.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
      }

      const result = { badge, exact_usd };
      _profileEarningsCache.set(clean, result);
      return result;
    }
  } catch {
    // Silent catch for network/timeout errors
  }

  const fallback = { badge: null, exact_usd: null };
  _profileEarningsCache.set(clean, fallback);
  return fallback;
}

/**
 * Enriches a list of lead records with real-time location demographics and public profile earnings
 */
export async function enrichLeadsWithLocation<T extends Record<string, any>>(leads: T[]): Promise<T[]> {
  const cache = await getPeopleCache();

  // Fetch profile earnings in parallel for leads with usernames
  const earningsPromises = leads.map((l) => getWhopProfileEarnings(l.whop_username));
  const earningsResults = await Promise.all(earningsPromises);

  return leads.map((lead, idx) => {
    let loc: WhopLocationInfo | null = null;

    // Check if lead already has location stored in scraped_data
    const savedLoc = lead.scraped_data?.location;
    if (savedLoc?.country) {
      const country = String(savedLoc.country).toUpperCase();
      loc = {
        country,
        country_name: savedLoc.country_name || getCountryName(country),
        country_flag: savedLoc.country_flag || getCountryFlag(country),
        city: savedLoc.city || null,
        timezone: savedLoc.timezone || null,
        device: savedLoc.device || null,
        display: `${getCountryFlag(country)} ${savedLoc.city ? `${savedLoc.city}, ` : ""}${getCountryName(country)}`,
      };
    }

    const uid = lead.whop_user_id;
    const uname = lead.whop_username ? String(lead.whop_username).toLowerCase().replace(/^@/, "").trim() : "";

    // Otherwise resolve from Whop API cache
    if (!loc) {
      if (uid && cache.byUserId.has(uid)) {
        loc = cache.byUserId.get(uid)!;
      } else if (uname && uname !== "anonymous" && uname !== "unknown" && cache.byUsername.has(uname)) {
        loc = cache.byUsername.get(uname)!;
      }
    }

    const finalCountry = loc?.country || lead.country || null;
    const profileEarnings = earningsResults[idx] || { badge: null, exact_usd: null };

    return {
      ...lead,
      country: finalCountry,
      country_name: loc?.country_name || (finalCountry ? getCountryName(finalCountry) : null),
      country_flag: loc?.country_flag || (finalCountry ? getCountryFlag(finalCountry) : "🌐"),
      city: loc?.city || lead.city || null,
      timezone: loc?.timezone || lead.timezone || null,
      device: loc?.device || null,
      ltv: loc?.ltv ?? 0,
      purchase_count: loc?.purchase_count ?? 0,
      profile_earnings_badge: profileEarnings.badge,
      profile_earnings_usd: profileEarnings.exact_usd,
    };
  });
}
