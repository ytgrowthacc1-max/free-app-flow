// Server-side Whop location & demographics resolver
// Queries Whop GeoIP telemetry from /api/v1/people, Vercel/Cloudflare headers, and IP geolocation.

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

// Comprehensive IANA Timezone to ISO Country mapping
export const TIMEZONE_TO_COUNTRY: Record<string, string> = {
  // US & Canada & Americas
  "America/New_York": "US", "America/Chicago": "US", "America/Denver": "US", "America/Los_Angeles": "US",
  "America/Phoenix": "US", "America/Detroit": "US", "America/Indiana/Indianapolis": "US", "America/Boise": "US",
  "America/Anchorage": "US", "America/Honolulu": "US", "America/Juneau": "US", "America/Adak": "US",
  "America/Toronto": "CA", "America/Vancouver": "CA", "America/Montreal": "CA", "America/Edmonton": "CA",
  "America/Winnipeg": "CA", "America/Halifax": "CA", "America/St_Johns": "CA", "America/Regina": "CA",
  "America/Mexico_City": "MX", "America/Cancun": "MX", "America/Tijuana": "MX", "America/Monterrey": "MX",
  "America/Sao_Paulo": "BR", "America/Buenos_Aires": "AR", "America/Bogota": "CO", "America/Lima": "PE",
  "America/Santiago": "CL", "America/Caracas": "VE", "America/Panama": "PA", "America/Costa_Rica": "CR",
  "America/Guatemala": "GT", "America/Santo_Domingo": "DO", "America/Puerto_Rico": "PR", "America/Havana": "CU",
  "America/Jamaica": "JM", "America/Port_of_Spain": "TT", "America/Montevideo": "UY", "America/Asuncion": "PY",

  // Europe
  "Europe/London": "GB", "Europe/Belfast": "GB", "Europe/Dublin": "IE", "Europe/Gibraltar": "GI",
  "Europe/Paris": "FR", "Europe/Berlin": "DE", "Europe/Rome": "IT", "Europe/Madrid": "ES",
  "Europe/Amsterdam": "NL", "Europe/Brussels": "BE", "Europe/Vienna": "AT", "Europe/Zurich": "CH",
  "Europe/Stockholm": "SE", "Europe/Oslo": "NO", "Europe/Copenhagen": "DK", "Europe/Helsinki": "FI",
  "Europe/Warsaw": "PL", "Europe/Prague": "CZ", "Europe/Budapest": "HU", "Europe/Bucharest": "RO",
  "Europe/Athens": "GR", "Europe/Lisbon": "PT", "Europe/Istanbul": "TR", "Europe/Kyiv": "UA",
  "Europe/Moscow": "RU", "Europe/Sarajevo": "BA", "Europe/Belgrade": "RS", "Europe/Zagreb": "HR",
  "Europe/Sofia": "BG", "Europe/Bratislava": "SK", "Europe/Ljubljana": "SI", "Europe/Tallinn": "EE",
  "Europe/Riga": "LV", "Europe/Vilnius": "LT", "Europe/Luxembourg": "LU", "Europe/Malta": "MT",
  "Europe/Nicosia": "CY", "Europe/Monaco": "MC", "Europe/Andorra": "AD", "Europe/Tirane": "AL",

  // Asia & Middle East
  "Asia/Calcutta": "IN", "Asia/Kolkata": "IN", "Asia/Karachi": "PK", "Asia/Dhaka": "BD",
  "Asia/Colombo": "LK", "Asia/Kathmandu": "NP", "Asia/Jakarta": "ID", "Asia/Makassar": "ID",
  "Asia/Jayapura": "ID", "Asia/Pontianak": "ID", "Asia/Manila": "PH", "Asia/Bangkok": "TH",
  "Asia/Ho_Chi_Minh": "VN", "Asia/Saigon": "VN", "Asia/Kuala_Lumpur": "MY", "Asia/Kuching": "MY",
  "Asia/Singapore": "SG", "Asia/Tokyo": "JP", "Asia/Seoul": "KR", "Asia/Hong_Kong": "HK",
  "Asia/Taipei": "TW", "Asia/Shanghai": "CN", "Asia/Chongqing": "CN", "Asia/Urumqi": "CN",
  "Asia/Dubai": "AE", "Asia/Riyadh": "SA", "Asia/Jerusalem": "IL", "Asia/Tel_Aviv": "IL",
  "Asia/Beirut": "LB", "Asia/Amman": "JO", "Asia/Kuwait": "KW", "Asia/Qatar": "QA",
  "Asia/Bahrain": "BH", "Asia/Muscat": "OM", "Asia/Baghdad": "IQ", "Asia/Baku": "AZ",
  "Asia/Tbilisi": "GE", "Asia/Yerevan": "AM", "Asia/Almaty": "KZ", "Asia/Tashkent": "UZ",

  // Africa
  "Africa/Casablanca": "MA", "Africa/Cairo": "EG", "Africa/Johannesburg": "ZA", "Africa/Lagos": "NG",
  "Africa/Nairobi": "KE", "Africa/Accra": "GH", "Africa/Tunis": "TN", "Africa/Algiers": "DZ",
  "Africa/Addis_Ababa": "ET", "Africa/Dar_es_Salaam": "TZ", "Africa/Kampala": "UG", "Africa/Kigali": "RW",
  "Africa/Luanda": "AO", "Africa/Maputo": "MZ", "Africa/Harare": "ZW", "Africa/Lusaka": "ZM",
  "Africa/Dakar": "SN", "Africa/Abidjan": "CI", "Africa/Yaounde": "CM", "Africa/Douala": "CM",

  // Oceania
  "Australia/Sydney": "AU", "Australia/Melbourne": "AU", "Australia/Brisbane": "AU",
  "Australia/Perth": "AU", "Australia/Adelaide": "AU", "Australia/Hobart": "AU", "Australia/Darwin": "AU",
  "Pacific/Auckland": "NZ", "Pacific/Chatham": "NZ", "Pacific/Fiji": "FJ", "Pacific/Honolulu": "US",
  "Pacific/Guam": "GU", "Pacific/Port_Moresby": "PG",
};

export function inferCountryFromTimezone(timezone?: string | null): string | null {
  if (!timezone) return null;
  const clean = timezone.trim();
  if (TIMEZONE_TO_COUNTRY[clean]) return TIMEZONE_TO_COUNTRY[clean];
  
  for (const [k, c] of Object.entries(TIMEZONE_TO_COUNTRY)) {
    if (k.toLowerCase() === clean.toLowerCase()) return c;
  }
  return null;
}

export interface RequestLocationData {
  country: string | null;
  country_name: string | null;
  country_flag: string;
  city: string | null;
  region: string | null;
  timezone: string | null;
  ip: string | null;
}

/**
 * Extracts GeoIP location data from incoming HTTP request headers (Vercel / Cloudflare)
 */
export function extractLocationFromHeaders(
  headers: Headers | Record<string, string | string[] | undefined> | null | undefined,
  clientTimezone?: string | null
): RequestLocationData {
  let country: string | null = null;
  let city: string | null = null;
  let region: string | null = null;
  let timezone: string | null = clientTimezone || null;
  let ip: string | null = null;

  if (headers) {
    const getH = (key: string): string | null => {
      if (typeof (headers as Headers).get === "function") {
        return (headers as Headers).get(key) || null;
      }
      const val = (headers as Record<string, any>)[key.toLowerCase()] || (headers as Record<string, any>)[key];
      if (Array.isArray(val)) return val[0] || null;
      return val ? String(val) : null;
    };

    country = getH("x-vercel-ip-country") || getH("cf-ipcountry") || getH("x-country-code") || null;
    city = getH("x-vercel-ip-city") || getH("cf-ipcity") || null;
    region = getH("x-vercel-ip-country-region") || getH("cf-region-code") || null;
    timezone = getH("x-vercel-ip-timezone") || timezone;
    ip = getH("x-real-ip") || getH("x-forwarded-for")?.split(",")[0]?.trim() || null;
  }

  if (country && country.length === 2) {
    country = country.toUpperCase();
  } else {
    country = null;
  }

  // If country is missing but timezone exists, infer country from timezone
  if (!country && timezone) {
    country = inferCountryFromTimezone(timezone);
  }

  const country_name = country ? getCountryName(country) : null;
  const country_flag = country ? getCountryFlag(country) : "🌐";

  return {
    country,
    country_name,
    country_flag,
    city: city ? decodeURIComponent(city) : null,
    region: region ? decodeURIComponent(region) : null,
    timezone,
    ip,
  };
}

/**
 * Fast public IP to country resolver
 */
export async function resolveIpLocation(ip?: string | null): Promise<Partial<RequestLocationData> | null> {
  if (!ip || ip === "127.0.0.1" || ip === "::1" || ip.startsWith("192.168.") || ip.startsWith("10.")) {
    return null;
  }
  try {
    const res = await fetch(`http://ip-api.com/json/${ip}?fields=status,country,countryCode,city,timezone`, {
      signal: AbortSignal.timeout(2000),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.status === "success" && data.countryCode) {
        const country = String(data.countryCode).toUpperCase();
        return {
          country,
          country_name: data.country || getCountryName(country),
          country_flag: getCountryFlag(country),
          city: data.city || null,
          timezone: data.timezone || null,
        };
      }
    }
  } catch {
    // Silent catch
  }
  return null;
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
    // Fetch all recent visitors/members from /api/v1/people (up to 15 pages = 1,500 people)
    let after: string | null = null;
    let pageCount = 0;
    const maxPages = 15;

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

        if (uid && country) byUserId.set(uid, locInfo);
        if (uname && country) byUsername.set(uname.toLowerCase().replace(/^@/, "").trim(), locInfo);
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

export async function getPeopleCache(): Promise<CachedPeopleCache> {
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
  fallbackCountry?: string | null,
  fallbackTimezone?: string | null
): Promise<WhopLocationInfo> {
  const cache = await getPeopleCache();

  if (whopUserId && cache.byUserId.has(whopUserId)) {
    return cache.byUserId.get(whopUserId)!;
  }

  if (whopUsername) {
    const clean = whopUsername.toLowerCase().replace(/^@/, "").trim();
    if (clean && clean !== "anonymous" && clean !== "unknown") {
      if (cache.byUsername.has(clean)) {
        return cache.byUsername.get(clean)!;
      }
      // Fallback: check public profile HTML payload
      const profile = await getWhopProfileEarnings(clean);
      if (profile.country) {
        const country = profile.country.toUpperCase();
        const country_name = getCountryName(country);
        const country_flag = getCountryFlag(country);
        const city = profile.city || null;
        return {
          country,
          country_name,
          country_flag,
          city,
          timezone: fallbackTimezone || null,
          device: null,
          display: `${country_flag} ${city ? `${city}, ` : ""}${country_name || country}`,
        };
      }
    }
  }

  // Fallback to provided country (e.g. from Cloudflare / Vercel request headers)
  let effectiveCountry = fallbackCountry && fallbackCountry.length === 2 ? fallbackCountry.toUpperCase() : null;
  if (!effectiveCountry && fallbackTimezone) {
    effectiveCountry = inferCountryFromTimezone(fallbackTimezone);
  }

  if (effectiveCountry) {
    const country_name = getCountryName(effectiveCountry);
    const country_flag = getCountryFlag(effectiveCountry);
    return {
      country: effectiveCountry,
      country_name,
      country_flag,
      city: null,
      timezone: fallbackTimezone || null,
      device: null,
      display: `${country_flag} ${country_name || effectiveCountry}`,
    };
  }

  return {
    country: null,
    country_name: null,
    country_flag: "🌐",
    city: null,
    timezone: fallbackTimezone || null,
    device: null,
    display: "Unknown",
  };
}

export interface WhopProfileIntel {
  badge: string | null;
  exact_usd: number | null;
  country: string | null;
  city: string | null;
}

const _profileEarningsCache = new Map<string, WhopProfileIntel>();

export async function getWhopProfileEarnings(username?: string | null): Promise<WhopProfileIntel> {
  if (!username) return { badge: null, exact_usd: null, country: null, city: null };
  const clean = username.toLowerCase().replace(/^@/, "").trim();
  if (!clean || clean === "anonymous" || clean === "unknown") return { badge: null, exact_usd: null, country: null, city: null };

  if (_profileEarningsCache.has(clean)) {
    return _profileEarningsCache.get(clean)!;
  }

  try {
    const res = await fetch(`https://whop.com/@${clean}`, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      },
      signal: AbortSignal.timeout(3000),
    });
    if (res.ok) {
      const html = await res.text();
      const badgeMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--[\s\S]*?-->\s*)*Earned/i);
      const usdMatch = html.match(/totalEarningsWithTransfersInUsd:"([\d\.]+)"/);

      let badge = badgeMatch ? badgeMatch[1] : null;
      let exact_usd: number | null = null;
      if (badge) {
        exact_usd = parseFloat(badge.replace(/[\$,]/g, ""));
      } else if (usdMatch) {
        exact_usd = parseFloat(usdMatch[1]);
        badge = `$${exact_usd.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
      }

      // Extract country and city from profile JSON object in HTML
      let country: string | null = null;
      let city: string | null = null;

      const unameStr = `\\"username\\":\\"${clean}\\"`;
      let idx = html.toLowerCase().indexOf(unameStr);
      if (idx === -1) {
        idx = html.toLowerCase().indexOf(`"username":"${clean}"`);
      }

      if (idx !== -1) {
        const snippet = html.slice(idx, idx + 500);
        const countryMatch = snippet.match(/\\?"country\\?"\s*:\s*\\?"([A-Z]{2})\\?"/);
        const cityMatch = snippet.match(/\\?"city\\?"\s*:\s*\\?"([^\\"]+)\\?"/);
        if (countryMatch) country = countryMatch[1];
        if (cityMatch && cityMatch[1] !== "null" && cityMatch[1] !== "undefined") city = cityMatch[1];
      }

      const result = { badge, exact_usd, country, city };
      _profileEarningsCache.set(clean, result);
      return result;
    }
  } catch {
    // Silent catch for network/timeout errors
  }

  const fallback = { badge: null, exact_usd: null, country: null, city: null };
  _profileEarningsCache.set(clean, fallback);
  return fallback;
}
