// Server-side Whop location & demographics resolver
// Queries Whop GeoIP telemetry from /api/v1/people and /api/v5/company/payments with in-memory caching.

export interface WhopLocationInfo {
  country: string | null; // 2-letter ISO (e.g. "US", "IN", "GB")
  country_name: string | null; // Full name (e.g. "United States", "India")
  country_flag: string; // Emoji flag (e.g. "🇺🇸", "🇮🇳")
  timezone: string | null; // e.g. "America/Chicago", "Asia/Calcutta"
  device: string | null; // e.g. "Android · Chrome (mobile)"
  ltv?: number; // Lifetime spend in USD
  purchase_count?: number; // Total purchases count
  public_earnings_badge?: string | null; // e.g. "$2,719.35" from whop.com/@username
  display: string; // Formatted summary string
}

interface PublicProfileData {
  country: string | null;
  city: string | null;
  public_earnings_badge: string | null;
}

const _publicProfileCache = new Map<string, PublicProfileData>();

export async function scrapePublicWhopProfile(username?: string | null): Promise<PublicProfileData | null> {
  if (!username) return null;
  const clean = username.replace(/^@/, "").trim().toLowerCase();
  if (!clean || ["anonymous", "unknown", "null", "undefined"].includes(clean)) return null;

  if (_publicProfileCache.has(clean)) {
    return _publicProfileCache.get(clean)!;
  }

  try {
    const url = `https://whop.com/@${clean}`;
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
    });

    if (!res.ok) return null;
    const html = await res.text();

    const countryMatch = html.match(/"country":\s*"([A-Z]{2})"/i) || html.match(/\\"country\\":\s*\\"([A-Z]{2})\\"/i) || html.match(/country["']?\s*:\s*["']?([A-Z]{2})["']?/i);
    const cityMatch = html.match(/"city":\s*"([^"]+)"/i) || html.match(/\\"city\\":\s*\\"([^\\"]+)\\"/i);
    const earnedMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i);

    const country = countryMatch ? countryMatch[1].toUpperCase() : null;
    const rawCity = cityMatch ? cityMatch[1] : null;
    const city = rawCity && rawCity !== "City" ? rawCity : null;
    const public_earnings_badge = earnedMatch ? earnedMatch[1] : null;

    const result = { country, city, public_earnings_badge };
    _publicProfileCache.set(clean, result);
    return result;
  } catch {
    return null;
  }
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
    // Fetch up to 3,000 recent visitors/members from /api/v1/people
    let after: string | null = null;
    let pageCount = 0;
    const maxPages = 30;

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

/**
 * Enriches a list of lead records with real-time location demographics
 */
export async function enrichLeadsWithLocation<T extends Record<string, any>>(leads: T[]): Promise<T[]> {
  const cache = await getPeopleCache();

  return Promise.all(
    leads.map(async (lead) => {
      let loc: WhopLocationInfo | null = null;
      let publicEarningsBadge: string | null = lead.public_earnings_badge || null;

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

      // Otherwise resolve from Whop cache
      if (!loc) {
        if (uid && cache.byUserId.has(uid)) {
          loc = cache.byUserId.get(uid)!;
        } else if (uname && uname !== "anonymous" && uname !== "unknown" && cache.byUsername.has(uname)) {
          loc = cache.byUsername.get(uname)!;
        }
      }

      // Public profile scraping fallback (resolves country & public creator earnings badge from whop.com/@username)
      if (uname && uname !== "anonymous" && uname !== "unknown") {
        const pub = await scrapePublicWhopProfile(uname);
        if (pub) {
          if (pub.public_earnings_badge) {
            publicEarningsBadge = pub.public_earnings_badge;
          }
          if (!loc?.country && pub.country) {
            const country = pub.country;
            loc = {
              country,
              country_name: getCountryName(country),
              country_flag: getCountryFlag(country),
              city: pub.city || loc?.city || null,
              timezone: loc?.timezone || null,
              device: loc?.device || null,
              display: `${getCountryFlag(country)} ${pub.city ? `${pub.city}, ` : ""}${getCountryName(country)}`,
            };
          }
        }
      }

      const finalCountry = loc?.country || lead.country || null;
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
        public_earnings_badge: publicEarningsBadge,
      };
    })
  );
}
