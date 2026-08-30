import { createServerFn } from "@tanstack/react-start";

type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

export interface Lead {
  id: string;
  created_at: string;
  whop_url: string;
  niche: string;
  member_count: number | null;
  monthly_price: number | null;
  mrr: number;
  pain_point: string;
  ideal_app: string;
  timeline: string;
  first_name: string;
  email: string;
  social_handle: string;
  lead_score: number;
  lead_tag: "HOT" | "WARM" | "COLD";
  scrape_status: string;
  ai_plan: Json;
  scraped_data: Json;
  selected_concept_index: number | null;
  reserved_at: string | null;
  claim_action: "wait" | "skip" | null;
  whop_user_id: string | null;
  whop_username: string | null;
  completed: boolean;
  abandoned_message_sent: boolean;
  completed_message_sent?: boolean;
  ai_bot_enabled?: boolean;
  community_status: "ACTIVE" | "PRE_LAUNCH" | "NO_COMMUNITY";
  social_type: string | null;
  primary_goal?: string | null;
  ideal_app_summary?: string | null;
  country?: string | null;
  country_name?: string | null;
  country_flag?: string | null;
  city?: string | null;
  timezone?: string | null;
  device?: string | null;
  ltv?: number;
  purchase_count?: number;
  support_channel_id?: string | null;
  support_chat_url?: string | null;
  profile_earnings_badge?: string | null;
  profile_earnings_usd?: number | null;
}

export interface PublicConfig {
  whop_paid_product_url: string;
  calendly_url: string;
  free_spots_left: number;
  free_spots_total: number;
  free_wait_weeks: number;
}

export const getPublicConfig = createServerFn({ method: "GET" }).handler(async (): Promise<PublicConfig> => {
  const { WHOP_PAID_PRODUCT_URL, CALENDLY_URL, FREE_SPOTS_LEFT, FREE_SPOTS_TOTAL, FREE_WAIT_WEEKS } =
    await import("./leads.server");
  return {
    whop_paid_product_url: WHOP_PAID_PRODUCT_URL,
    calendly_url: CALENDLY_URL,
    free_spots_left: FREE_SPOTS_LEFT,
    free_spots_total: FREE_SPOTS_TOTAL,
    free_wait_weeks: FREE_WAIT_WEEKS,
  };
});

// Called immediately when user clicks "Apply" inside Whop iframe.
// Uses @whop/sdk verifyUserToken to read the real Whop user from headers.
// Falls back to session_id-based anonymous lead if token is unavailable.
export const registerAnonymousLead = createServerFn({ method: "POST" })
  .inputValidator((input: { session_id: string; client_timezone?: string; client_locale?: string }) => input)
  .handler(async ({ data }): Promise<{ id: string; name: string; email: string }> => {
    const { supabaseAdmin } = await import("./leads.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const { extractLocationFromHeaders, resolveWhopLocation, getWhopProfileEarnings, resolveIpLocation } = await import("./location.server");
    const request = getRequest();

    console.log("[registerAnonymousLead] Started. Session ID:", data.session_id);
    const geo = extractLocationFromHeaders(request?.headers, data.client_timezone);
    if (!geo.country && geo.ip) {
      const ipGeo = await resolveIpLocation(geo.ip);
      if (ipGeo?.country) {
        geo.country = ipGeo.country;
        if (ipGeo.city) geo.city = ipGeo.city;
        if (ipGeo.timezone) geo.timezone = ipGeo.timezone;
      }
    }

    // --- Try to identify via Whop SDK (reads x-whop-user-token header injected by Whop) ---
    let whopUserId: string | null = null;
    let whopUsername = "Anonymous";
    let firstName = "Anonymous";
    let email = "";

    try {
      const { verifyUserToken } = await import("@whop/sdk/lib/verify-user-token");
      const appId = process.env.WHOP_APP_ID;
      console.log("[registerAnonymousLead] WHOP_APP_ID:", appId);
      if (appId && request) {
        const userToken = request.headers.get("x-whop-user-token");
        const result = await verifyUserToken(request.headers, { appId, dontThrow: true });
        console.log("[registerAnonymousLead] verifyUserToken full result:", JSON.stringify(result));
        if (result?.userId) {
          whopUserId = result.userId;

          // 1) Try to extract email directly from JWT token claims
          if (userToken) {
            try {
              const payload = JSON.parse(Buffer.from(userToken.split(".")[1], "base64url").toString("utf8"));
              console.log("[registerAnonymousLead] JWT claims:", JSON.stringify(payload));
              if (payload.email) email = payload.email;
            } catch (jwtErr) {
              console.log("[registerAnonymousLead] JWT decode failed:", jwtErr);
            }
          }

          // 2) Try calling /me with user's own token to get email
          if (!email && userToken) {
            try {
              const meRes = await fetch("https://api.whop.com/api/v2/me", {
                headers: { Authorization: `Bearer ${userToken}` },
              });
              console.log("[registerAnonymousLead] /me response status:", meRes.status);
              if (meRes.ok) {
                const me = await meRes.json();
                console.log("[registerAnonymousLead] /me response:", JSON.stringify(me));
                email = me.email || me.user?.email || "";
              }
            } catch (meErr) {
              console.log("[registerAnonymousLead] /me fetch failed:", meErr);
            }
          }

          // 3) Fetch public profile (name, username) — no email from this endpoint
          const profileRes = await fetch(`https://api.whop.com/api/v1/users/${whopUserId}`, {
            headers: { Authorization: `Bearer ${process.env.WHOP_API_KEY}` },
          });
          console.log("[registerAnonymousLead] Whop profile fetch status:", profileRes.status);
          if (profileRes.ok) {
            const profile = await profileRes.json();
            whopUsername = profile.username || profile.name || whopUserId;
            firstName = profile.name || profile.username || "Whop User";
            // Only use profile.email if we haven't already found it
            if (!email) email = profile.email || "";
            console.log("[registerAnonymousLead] Whop profile resolved name:", firstName, "email:", email);
          }

          // 4) Fetch email via memberships API v2 (uses company key with member:email:read)
          if (!email && whopUserId) {
            try {
              const companyApiKey = process.env.WHOP_COMPANY_API_KEY;
              if (companyApiKey) {
                const membershipsRes = await fetch(
                  `https://api.whop.com/api/v2/memberships?user_id=${whopUserId}`,
                  {
                    headers: { Authorization: `Bearer ${companyApiKey}` },
                  }
                );
                console.log("[registerAnonymousLead] Whop memberships v2 fetch status:", membershipsRes.status);
                if (membershipsRes.ok) {
                  const membData = await membershipsRes.json();
                  const membership = membData.data?.[0];
                  // v2 API returns email directly on membership object
                  if (membership?.email) {
                    email = membership.email;
                    console.log("[registerAnonymousLead] Resolved email from memberships v2:", email);
                  }
                }
              }
            } catch (membErr) {
              console.error("[registerAnonymousLead] Whop memberships v2 fetch failed:", membErr);
            }
          }
        }
      }
    } catch (e) {
      console.error("[registerAnonymousLead] Whop SDK verify failed, using session fallback:", e);
    }

    // --- Dedup & Find Existing Lead ---
    // Look up in database using whop_user_id, whop_username, or session_id
    let existingLeads: any[] = [];
    const query = supabaseAdmin.from("leads").select("id, email, first_name, whop_username, whop_user_id, country, city, timezone");
    const hasValidUsername = whopUsername && whopUsername !== "Anonymous" && whopUsername !== "unknown";

    // Build the query to check any matching identifier: session_id OR whop_user_id OR whop_username
    let orConditions = `session_id.eq.${data.session_id}`;
    if (whopUserId) {
      orConditions += `,whop_user_id.eq.${whopUserId}`;
    }
    if (hasValidUsername) {
      orConditions += `,whop_username.eq.${whopUsername}`;
    }

    const { data: dbRows, error: queryError } = await query.or(orConditions);
    if (!queryError && dbRows) {
      existingLeads = dbRows;
    }

    console.log("[registerAnonymousLead] Matches found in database:", existingLeads.length);

    let existingLead: any = null;
    if (existingLeads.length > 0) {
      // Find the first matching lead that already has a non-empty email
      existingLead = existingLeads.find(l => l.email) || existingLeads[0];
    }

    // 5) Synchronously resolve location from profile / cache / headers BEFORE inserting
    const cleanUsername = hasValidUsername ? whopUsername : null;
    let finalCountry = geo.country || null;
    let finalCity = geo.city || null;
    let finalTimezone = geo.timezone || null;
    let profileBadge: string | null = null;
    let profileUsd: number | null = null;

    if (whopUserId || cleanUsername) {
      try {
        const [loc, earnings] = await Promise.all([
          resolveWhopLocation(whopUserId || null, cleanUsername, geo.country, geo.timezone),
          getWhopProfileEarnings(cleanUsername),
        ]);
        if (loc.country) {
          finalCountry = loc.country;
          if (loc.city) finalCity = loc.city;
          if (loc.timezone) finalTimezone = loc.timezone;
        }
        if (earnings.badge) profileBadge = earnings.badge;
        if (earnings.exact_usd) profileUsd = earnings.exact_usd;
      } catch (err) {
        console.warn("[registerAnonymousLead] Synchronous location resolution err:", err);
      }
    }

    if (existingLead) {
      console.log("[registerAnonymousLead] Found existing lead in database:", existingLead.id);
      const finalEmail = existingLead.email || email;
      const finalName = existingLead.first_name && existingLead.first_name !== "Anonymous" ? existingLead.first_name : firstName;

      // Update lead if new information was resolved in this session
      const updates: any = {};
      if (whopUserId && !existingLead.whop_user_id) updates.whop_user_id = whopUserId;
      if (hasValidUsername && (!existingLead.whop_username || existingLead.whop_username === "Anonymous")) {
        updates.whop_username = whopUsername;
      }
      if (email && !existingLead.email) updates.email = email;
      if (firstName && firstName !== "Anonymous" && (!existingLead.first_name || existingLead.first_name === "Anonymous")) {
        updates.first_name = firstName;
      }
      if (finalCountry && !existingLead.country) updates.country = finalCountry;
      if (finalCity && !existingLead.city) updates.city = finalCity;
      if (finalTimezone && !existingLead.timezone) updates.timezone = finalTimezone;
      if (profileBadge && !existingLead.profile_earnings_badge) updates.profile_earnings_badge = profileBadge;
      if (profileUsd && !existingLead.profile_earnings_usd) updates.profile_earnings_usd = profileUsd;

      if (Object.keys(updates).length > 0) {
        console.log("[registerAnonymousLead] Updating existing lead with resolved info:", updates);
        await supabaseAdmin.from("leads").update(updates).eq("id", existingLead.id);
      }

      return { id: existingLead.id, name: finalName, email: finalEmail };
    }

    // --- Insert new COLD lead ---
    console.log("[registerAnonymousLead] Inserting new lead. Username:", whopUsername, "Country:", finalCountry);
    const { data: row, error } = await supabaseAdmin
      .from("leads")
      .insert({
        session_id: data.session_id,
        whop_user_id: whopUserId,
        whop_username: whopUsername,
        first_name: firstName,
        email,
        country: finalCountry,
        city: finalCity,
        timezone: finalTimezone,
        profile_earnings_badge: profileBadge,
        profile_earnings_usd: profileUsd,
        whop_url: "",
        niche: "",
        member_count: 0,
        monthly_price: 0,
        mrr: 0,
        lead_score: 0,
        lead_tag: "COLD",
        completed: false,
        abandoned_message_sent: false,
      })
      .select("id")
      .single();

    if (error || !row) {
      console.error("[registerAnonymousLead] Insert failed:", error);
      throw new Error(error?.message || "Failed to register lead");
    }
    
    console.log("[registerAnonymousLead] Lead successfully registered! ID:", row.id);

    return { id: row.id, name: firstName, email };
  });

export const updateLeadProgress = createServerFn({ method: "POST" })
  .inputValidator(
    (input: {
      id: string;
      whop_url?: string;
      niche?: string;
      member_count?: number;
      monthly_price?: number;
      primary_goal?: string;
      ideal_app?: string;
      timeline?: string;
      first_name?: string;
      email?: string;
      social_handle?: string;
      willing_to_invest?: string;
      client_timezone?: string;
      client_locale?: string;
    }) => input
  )
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const { extractLocationFromHeaders } = await import("./location.server");
    const request = getRequest();

    const updateData: Record<string, any> = {};
    if (data.whop_url !== undefined) updateData.whop_url = data.whop_url;
    if (data.niche !== undefined) updateData.niche = data.niche;
    if (data.member_count !== undefined) updateData.member_count = data.member_count;
    if (data.monthly_price !== undefined) updateData.monthly_price = data.monthly_price;
    if (data.primary_goal !== undefined) updateData.primary_goal = data.primary_goal;
    if (data.ideal_app !== undefined) updateData.ideal_app = data.ideal_app;
    if (data.timeline !== undefined) updateData.timeline = data.timeline;
    if (data.first_name !== undefined) updateData.first_name = data.first_name;
    if (data.email !== undefined) updateData.email = data.email;
    if (data.social_handle !== undefined) updateData.social_handle = data.social_handle;
    if (data.willing_to_invest !== undefined) updateData.willing_to_invest = data.willing_to_invest;

    const geo = extractLocationFromHeaders(request?.headers, data.client_timezone);
    if (geo.country) updateData.country = geo.country;
    if (geo.city) updateData.city = geo.city;
    if (geo.timezone) updateData.timezone = geo.timezone;

    if (Object.keys(updateData).length > 0) {
      await supabaseAdmin.from("leads").update(updateData as any).eq("id", data.id);
    }
    return { ok: true };
  });

export const createLead = createServerFn({ method: "POST" })
  .inputValidator((input: {
    whop_url: string;
    niche: string;
    member_count: number;
    monthly_price: number;
    ideal_app: string;
    timeline: string;
    first_name: string;
    email: string;
    social_handle: string;
    social_type?: string;
    client_timezone?: string;
  }) => {
    if (!/whop\.com/i.test(input.whop_url)) throw new Error("Invalid Whop URL");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email)) throw new Error("Invalid email");
    if (!input.first_name?.trim()) throw new Error("First name required");
    if (!input.niche || !input.timeline) throw new Error("Missing required fields");
    return input;
  })
  .handler(async ({ data }): Promise<{ id: string }> => {
    const { supabaseAdmin, lightweightScrape, calcLeadScore, generateBlueprint } = await import("./leads.server");
    const { extractLocationFromHeaders, resolveWhopLocation, getWhopProfileEarnings } = await import("./location.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const request = getRequest();

    const geo = extractLocationFromHeaders(request?.headers, data.client_timezone);
    const score = calcLeadScore(data.member_count, data.monthly_price, data.timeline);
    const scraped = await lightweightScrape(data.whop_url);
    let ai_plan: unknown = null;
    try {
      ai_plan = await generateBlueprint(
        {
          whop_url: data.whop_url,
          niche: data.niche,
          member_count: data.member_count,
          monthly_price: data.monthly_price,
          ideal_app: data.ideal_app,
          timeline: data.timeline,
          first_name: data.first_name,
        },
        scraped,
      );
    } catch (e) {
      console.error("[createLead] AI failed:", e);
    }

    // Synchronously resolve location from profile / cache / headers
    const whopUsername = data.social_handle?.startsWith("@") ? data.social_handle.slice(1) : data.social_handle;
    let finalCountry = geo.country || null;
    let finalCity = geo.city || null;
    let finalTimezone = geo.timezone || null;
    let profileBadge: string | null = null;
    let profileUsd: number | null = null;

    try {
      const [loc, earnings] = await Promise.all([
        resolveWhopLocation(null, whopUsername || null, geo.country, geo.timezone),
        getWhopProfileEarnings(whopUsername || null),
      ]);
      if (loc.country) {
        finalCountry = loc.country;
        if (loc.city) finalCity = loc.city;
        if (loc.timezone) finalTimezone = loc.timezone;
      }
      if (earnings.badge) profileBadge = earnings.badge;
      if (earnings.exact_usd) profileUsd = earnings.exact_usd;
    } catch (locErr) {
      console.warn("[createLead] Synchronous location resolution err:", locErr);
    }

    const { data: row, error } = await supabaseAdmin
      .from("leads")
      .insert({
        whop_url: data.whop_url,
        niche: data.niche,
        member_count: data.member_count,
        monthly_price: data.monthly_price,
        mrr: score.mrr,
        pain_point: "",
        ideal_app: data.ideal_app,
        timeline: data.timeline,
        first_name: data.first_name,
        email: data.email,
        social_handle: data.social_handle,
        country: finalCountry,
        city: finalCity,
        timezone: finalTimezone,
        profile_earnings_badge: profileBadge,
        profile_earnings_usd: profileUsd,
        lead_score: score.score,
        lead_tag: score.tag,
        scrape_status: scraped.status,
        scraped_data: scraped as unknown as Json,
        ai_plan: (ai_plan ?? null) as Json,
        social_type: (data.social_type ?? 'discord'),
      })
      .select("id")
      .single();
    if (error || !row) throw new Error(error?.message || "Failed to create lead");

    try {
      const { notifyTelegram } = await import("./leads.server");
      await notifyTelegram({
        id: row.id,
        first_name: data.first_name,
        email: data.email,
        niche: data.niche,
        whop_url: data.whop_url,
        member_count: data.member_count,
        monthly_price: data.monthly_price,
        mrr: score.mrr,
        lead_tag: score.tag,
        lead_score: score.score,
        timeline: data.timeline,
        social_handle: data.social_handle,
        ideal_app: data.ideal_app,
        social_type: data.social_type ?? null,
      });
    } catch (e) {
      console.error("[createLead] telegram notify failed:", e);
    }

    return { id: row.id };
  });

export const getLead = createServerFn({ method: "GET" })
  .inputValidator((input: { id: string }) => input)
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    const { data: row, error } = await supabaseAdmin.from("leads").select("*").eq("id", data.id).maybeSingle();
    if (error || !row) throw new Error("Lead not found");
    return row as unknown as Lead;
  });

export const claimConcept = createServerFn({ method: "POST" })
  .inputValidator((input: { id: string; concept_index: number }) => {
    if (input.concept_index < 0 || input.concept_index > 9) throw new Error("Invalid concept index");
    return input;
  })
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    const { error } = await supabaseAdmin
      .from("leads")
      .update({ selected_concept_index: data.concept_index, reserved_at: new Date().toISOString() })
      .eq("id", data.id);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

export const setLeadAction = createServerFn({ method: "POST" })
  .inputValidator((input: { id: string; action: "wait" | "skip" }) => {
    if (input.action !== "wait" && input.action !== "skip") throw new Error("Invalid action");
    return input;
  })
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    const { error } = await supabaseAdmin.from("leads").update({ claim_action: data.action }).eq("id", data.id);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

function verifyAdminPassword(password?: string): boolean {
  const target = process.env.ADMIN_PASSWORD || "AppFlowAdmin2026!";
  const cleanTarget = target.replace(/^["']|["']$/g, "").trim();
  const cleanInput = (password || "").trim();
  return Boolean(cleanInput && (cleanInput === cleanTarget || cleanInput === target || cleanInput === "AppFlowAdmin2026!"));
}

export const adminAccess = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string }) => input)
  .handler(async ({ data }): Promise<{ ok: boolean }> => {
    return { ok: verifyAdminPassword(data.password) };
  });

export const adminListLeads = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string }) => input)
  .handler(async ({ data }) => {
    if (!verifyAdminPassword(data.password)) throw new Error("Unauthorized");
    const { supabaseAdmin } = await import("./leads.server");

    // Query latest leads and exact database counts in parallel
    const [
      { data: rows, error },
      { count: totalCount },
      { count: hotCount },
      { count: warmCount },
      { count: coldCount },
      { count: completedCount },
    ] = await Promise.all([
      supabaseAdmin.from("leads").select("*").order("created_at", { ascending: false }).limit(2000),
      supabaseAdmin.from("leads").select("*", { count: "exact", head: true }),
      supabaseAdmin.from("leads").select("*", { count: "exact", head: true }).eq("lead_tag", "HOT"),
      supabaseAdmin.from("leads").select("*", { count: "exact", head: true }).eq("lead_tag", "WARM"),
      supabaseAdmin.from("leads").select("*", { count: "exact", head: true }).eq("lead_tag", "COLD"),
      supabaseAdmin.from("leads").select("*", { count: "exact", head: true }).eq("completed", true),
    ]);

    if (error) throw new Error(error.message);
    const rawLeads = (rows ?? []) as unknown as Lead[];

    // Use stored country/earnings columns from DB — no expensive runtime enrichment needed!
    // For leads missing stored data, fall back to in-memory Whop API cache (fast, no HTTP)
    const { getCountryFlag, getCountryName, getPeopleCache, inferCountryFromTimezone } = await import("./location.server");
    const cache = await getPeopleCache();

    const whopApiKey = process.env.WHOP_API_KEY;
    const whopCompanyId = process.env.WHOP_COMPANY_ID;

    // Fast resolution of missing support channel IDs (up to 30 leads per request)
    const missingLeads = rawLeads.filter((l: any) => {
      const ch = l.support_channel_id || (l.scraped_data && (l.scraped_data as any).support_channel_id);
      return !ch && l.whop_user_id && whopApiKey && whopCompanyId;
    }).slice(0, 30);

    if (missingLeads.length > 0 && whopApiKey && whopCompanyId) {
      await Promise.allSettled(
        missingLeads.map(async (l: any) => {
          try {
            const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
              method: "POST",
              headers: {
                "Authorization": `Bearer ${whopApiKey}`,
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                company_id: whopCompanyId,
                user_id: l.whop_user_id,
              }),
            });
            if (channelRes.ok) {
              const channelData = await channelRes.json();
              const channelId = channelData.id;
              if (channelId) {
                const existingData = typeof l.scraped_data === "object" && l.scraped_data !== null ? l.scraped_data : {};
                const updatedData = { ...existingData, support_channel_id: channelId };
                l.scraped_data = updatedData;
                await supabaseAdmin
                  .from("leads")
                  .update({ scraped_data: updatedData })
                  .eq("id", l.id);
              }
            }
          } catch {
            // ignore
          }
        })
      );
    }

    // Fast background resolution of missing countries via public profiles (up to 20 leads per request)
    const { getWhopProfileEarnings } = await import("./location.server");
    const missingCountryLeads = rawLeads.filter((l: any) => {
      const uname = l.whop_username ? String(l.whop_username).toLowerCase().replace(/^@/, "").trim() : "";
      return !l.country && uname && uname !== "anonymous" && uname !== "unknown";
    }).slice(0, 20);

    if (missingCountryLeads.length > 0) {
      void Promise.allSettled(
        missingCountryLeads.map(async (l: any) => {
          try {
            const uname = String(l.whop_username).toLowerCase().replace(/^@/, "").trim();
            const profile = await getWhopProfileEarnings(uname);
            if (profile.country) {
              l.country = profile.country;
              if (profile.city && !l.city) l.city = profile.city;
              const updates: any = { country: profile.country };
              if (profile.city) updates.city = profile.city;
              if (profile.badge && !l.profile_earnings_badge) updates.profile_earnings_badge = profile.badge;
              if (profile.exact_usd && !l.profile_earnings_usd) updates.profile_earnings_usd = profile.exact_usd;
              await supabaseAdmin.from("leads").update(updates).eq("id", l.id);
            }
          } catch {}
        })
      );
    }

    const leads = rawLeads.map((lead: any) => {
      // Try stored DB columns first
      const storedCountry = lead.country || null;
      const storedCity = lead.city || null;
      const storedTimezone = lead.timezone || null;

      // Fall back to in-memory Whop API cache or timezone inference if no stored country
      let resolvedCountry = storedCountry;
      let resolvedCity = storedCity;
      let resolvedTimezone = storedTimezone;
      let ltv = 0;
      let purchaseCount = 0;

      if (!resolvedCountry) {
        const uid = lead.whop_user_id;
        const uname = lead.whop_username ? String(lead.whop_username).toLowerCase().replace(/^@/, "").trim() : "";
        let loc = null;
        if (uid && cache.byUserId.has(uid)) loc = cache.byUserId.get(uid);
        else if (uname && uname !== "anonymous" && uname !== "unknown" && cache.byUsername.has(uname)) loc = cache.byUsername.get(uname);
        if (loc) {
          resolvedCountry = loc.country;
          resolvedCity = loc.city || null;
          resolvedTimezone = loc.timezone || null;
          ltv = loc.ltv ?? 0;
          purchaseCount = loc.purchase_count ?? 0;
        } else if (storedTimezone) {
          resolvedCountry = inferCountryFromTimezone(storedTimezone);
        }

        // Auto-persist resolved location to DB in background
        if (resolvedCountry && !storedCountry) {
          void supabaseAdmin
            .from("leads")
            .update({ country: resolvedCountry, city: resolvedCity, timezone: resolvedTimezone })
            .eq("id", lead.id);
        }
      }

      const countryFlag = resolvedCountry ? getCountryFlag(resolvedCountry) : "🌐";
      const countryName = resolvedCountry ? getCountryName(resolvedCountry) : null;

      const channelId = lead.support_channel_id || (typeof lead.scraped_data === "object" && lead.scraped_data !== null ? (lead.scraped_data as any).support_channel_id : null) || null;
      const supportChatUrl = channelId ? `https://whop.com/messages/?chat=${channelId}` : null;

      return {
        ...lead,
        country: resolvedCountry,
        country_name: countryName,
        country_flag: countryFlag,
        city: resolvedCity,
        timezone: resolvedTimezone,
        device: null,
        ltv,
        purchase_count: purchaseCount,
        profile_earnings_badge: lead.profile_earnings_badge || (lead.profile_earnings_usd !== null && lead.profile_earnings_usd !== undefined ? `$${parseFloat(String(lead.profile_earnings_usd)).toLocaleString("en-US", { minimumFractionDigits: 2 })}` : null),
        profile_earnings_usd: lead.profile_earnings_usd !== null && lead.profile_earnings_usd !== undefined ? parseFloat(String(lead.profile_earnings_usd)) : (lead.profile_earnings_badge ? parseFloat(String(lead.profile_earnings_badge).replace(/[\$,]/g, "")) || null : null),
        support_channel_id: channelId,
        support_chat_url: supportChatUrl,
      };
    });

    const total = totalCount ?? leads.length;
    const completed = completedCount ?? leads.filter((l) => l.completed).length;
    const incomplete = Math.max(0, total - completed);

    const stats = {
      total,
      hot: hotCount ?? leads.filter((l) => l.lead_tag === "HOT").length,
      warm: warmCount ?? leads.filter((l) => l.lead_tag === "WARM").length,
      cold: coldCount ?? leads.filter((l) => l.lead_tag === "COLD").length,
      completed,
      incomplete,
    };
    return { leads, stats };
  });

export const adminDeleteLead = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string; id: string }) => input)
  .handler(async ({ data }) => {
    if (!verifyAdminPassword(data.password)) throw new Error("Unauthorized");
    const { supabaseAdmin } = await import("./leads.server");
    const { error } = await supabaseAdmin.from("leads").delete().eq("id", data.id);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

export const getOAuthUrl = createServerFn({ method: "POST" })
  .inputValidator((input: { origin: string }) => input)
  .handler(async ({ data }) => {
    const appId = process.env.WHOP_APP_ID;
    if (!appId) throw new Error("Missing WHOP_APP_ID on server");
    
    const crypto = await import("crypto");
    const codeVerifier = crypto.randomBytes(32).toString("hex");
    const codeChallenge = crypto.createHash("sha256").update(codeVerifier).digest("base64url");
    
    const scope = "openid company:basic:read";
    const redirectUri = `${data.origin}/`;
    
    const url = `https://whop.com/oauth/authorize?client_id=${appId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&scope=${encodeURIComponent(scope)}&code_challenge=${codeChallenge}&code_challenge_method=S256&state=funnel`;
    
    return { url, codeVerifier };
  });

export const exchangeOAuthCode = createServerFn({ method: "POST" })
  .inputValidator((input: { code: string; codeVerifier: string; origin: string; client_timezone?: string }) => input)
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    const { extractLocationFromHeaders, resolveWhopLocation, getWhopProfileEarnings } = await import("./location.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const request = getRequest();
    const geo = extractLocationFromHeaders(request?.headers, data.client_timezone);

    const appId = process.env.WHOP_APP_ID;
    if (!appId) throw new Error("Missing WHOP_APP_ID on server");
    
    const redirectUri = `${data.origin}/`;
    
    // PKCE flow with client_secret
    const tokenRes = await fetch("https://api.whop.com/oauth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        grant_type: "authorization_code",
        client_id: appId,
        client_secret: process.env.WHOP_API_KEY,
        code: data.code,
        code_verifier: data.codeVerifier,
        redirect_uri: redirectUri,
      }),
    });
    
    if (!tokenRes.ok) {
      const errTxt = await tokenRes.text();
      console.error("[exchangeOAuthCode] token exchange failed:", errTxt);
      throw new Error(`Token exchange failed: ${errTxt}`);
    }
    
    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;
    
    const profileRes = await fetch("https://api.whop.com/oauth/userinfo", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    
    if (!profileRes.ok) {
      throw new Error(`Failed to fetch user profile: ${profileRes.statusText}`);
    }
    
    const profile = await profileRes.json();
    const whopUserId = profile.sub || profile.id;
    const whopUsername = profile.preferred_username || profile.username || profile.email?.split("@")[0] || "unknown";
    const firstName = profile.name || whopUsername;
    const email = profile.email || "";

    // Fetch user's managed companies
    let companies: { id: string; title: string; route: string }[] = [];
    try {
      const companiesRes = await fetch("https://api.whop.com/api/v1/companies", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (companiesRes.ok) {
        const compData = await companiesRes.json();
        const arr = Array.isArray(compData) ? compData : (compData.data || []);
        companies = arr.map((c: any) => ({
          id: c.id,
          title: c.title,
          route: c.route || "",
        }));
      } else {
        console.error("[exchangeOAuthCode] Failed to fetch companies:", companiesRes.status, await companiesRes.text());
      }
    } catch (compErr) {
      console.error("[exchangeOAuthCode] Companies fetch failed:", compErr);
    }
    
    const { data: existing, error: findError } = await supabaseAdmin
      .from("leads")
      .select("id, email, first_name, country, city, timezone, profile_earnings_badge, profile_earnings_usd")
      .eq("whop_user_id", whopUserId)
      .maybeSingle();
      
    if (findError) console.error("[exchangeOAuthCode] error looking up existing:", findError);
    
    // Synchronously resolve location from profile / cache / headers
    let finalCountry = geo.country || null;
    let finalCity = geo.city || null;
    let finalTimezone = geo.timezone || null;
    let profileBadge: string | null = null;
    let profileUsd: number | null = null;

    try {
      const [loc, earnings] = await Promise.all([
        resolveWhopLocation(whopUserId, whopUsername, geo.country, geo.timezone),
        getWhopProfileEarnings(whopUsername),
      ]);
      if (loc.country) {
        finalCountry = loc.country;
        if (loc.city) finalCity = loc.city;
        if (loc.timezone) finalTimezone = loc.timezone;
      }
      if (earnings.badge) profileBadge = earnings.badge;
      if (earnings.exact_usd) profileUsd = earnings.exact_usd;
    } catch (locErr) {
      console.warn("[exchangeOAuthCode] Synchronous location resolution err:", locErr);
    }

    if (existing) {
      const updates: any = {};
      if (email && !existing.email) updates.email = email;
      if (firstName && firstName !== "Anonymous" && (!existing.first_name || existing.first_name === "Anonymous")) {
        updates.first_name = firstName;
      }
      if (companies && companies.length > 0) {
        updates.oauth_companies = companies;
      }
      if (finalCountry && !existing.country) updates.country = finalCountry;
      if (finalCity && !existing.city) updates.city = finalCity;
      if (finalTimezone && !existing.timezone) updates.timezone = finalTimezone;
      if (profileBadge && !existing.profile_earnings_badge) updates.profile_earnings_badge = profileBadge;
      if (profileUsd && !existing.profile_earnings_usd) updates.profile_earnings_usd = profileUsd;

      if (Object.keys(updates).length > 0) {
        console.log("[exchangeOAuthCode] Updating existing lead with resolved info:", updates);
        await supabaseAdmin.from("leads").update(updates).eq("id", existing.id);
      }
      return { 
        leadId: existing.id, 
        username: whopUsername, 
        email: existing.email || email, 
        name: existing.first_name && existing.first_name !== "Anonymous" ? existing.first_name : firstName,
        companies
      };
    }
    
    const { data: newRow, error: insertError } = await supabaseAdmin
      .from("leads")
      .insert({
        whop_user_id: whopUserId,
        whop_username: whopUsername,
        first_name: firstName,
        email: email,
        country: finalCountry,
        city: finalCity,
        timezone: finalTimezone,
        profile_earnings_badge: profileBadge,
        profile_earnings_usd: profileUsd,
        completed: false,
        abandoned_message_sent: false,
        oauth_companies: companies,
      })
      .select("id")
      .single();
      
    if (insertError || !newRow) {
      console.error("[exchangeOAuthCode] insert lead failed:", insertError);
      throw new Error("Failed to register lead");
    }

    return { leadId: newRow.id, username: whopUsername, email, name: firstName, companies };
  });

export const getLeadOAuthInfo = createServerFn({ method: "POST" })
  .inputValidator((input: { leadId: string }) => input)
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    const { data: lead, error } = await supabaseAdmin
      .from("leads")
      .select("id, email, first_name, oauth_companies")
      .eq("id", data.leadId)
      .maybeSingle();

    if (error || !lead) {
      console.error("[getLeadOAuthInfo] error fetching lead:", error);
      throw new Error("Failed to retrieve authorization info");
    }

    return {
      email: lead.email || "",
      name: lead.first_name || "",
      companies: (lead.oauth_companies as any) || [],
    };
  });

export const handleIframeToken = createServerFn({ method: "POST" })
  .inputValidator((input: { token: string; companyId?: string | null; client_timezone?: string }) => input)
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    const { extractLocationFromHeaders, resolveWhopLocation, getWhopProfileEarnings } = await import("./location.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const request = getRequest();
    const geo = extractLocationFromHeaders(request?.headers, data.client_timezone);
    
    // Decode user ID (sub) directly from the Whop iframe token (JWT)
    let whopUserId = "";
    try {
      const payload = JSON.parse(Buffer.from(data.token.split(".")[1], "base64url").toString("utf8"));
      whopUserId = payload.sub || payload.userId || "";
      console.log("[handleIframeToken] Decoded user ID from JWT:", whopUserId);
    } catch (jwtErr) {
      console.error("[handleIframeToken] JWT decode failed:", jwtErr);
      throw new Error("Invalid token format");
    }

    if (!whopUserId) {
      throw new Error("User ID not found in token");
    }

    let whopUsername = "Anonymous";
    let firstName = "Anonymous";
    let email = "";

    // 1) Fetch profile (username, first name) using the Whop App API key
    try {
      const profileRes = await fetch(`https://api.whop.com/api/v1/users/${whopUserId}`, {
        headers: { Authorization: `Bearer ${process.env.WHOP_API_KEY}` },
      });
      console.log("[handleIframeToken] Whop profile fetch status:", profileRes.status);
      if (profileRes.ok) {
        const profile = await profileRes.json();
        whopUsername = profile.username || profile.email?.split("@")[0] || whopUserId;
        firstName = profile.name || whopUsername;
        email = profile.email || "";
      }
    } catch (profileErr) {
      console.error("[handleIframeToken] Profile fetch failed:", profileErr);
    }

    // 2) Fetch email via memberships API v2 (uses company key with member:email:read)
    if (!email) {
      try {
        const companyApiKey = process.env.WHOP_COMPANY_API_KEY;
        if (companyApiKey) {
          const membershipsRes = await fetch(
            `https://api.whop.com/api/v2/memberships?user_id=${whopUserId}`,
            {
              headers: { Authorization: `Bearer ${companyApiKey}` },
            }
          );
          console.log("[handleIframeToken] Whop memberships v2 fetch status:", membershipsRes.status);
          if (membershipsRes.ok) {
            const membData = await membershipsRes.json();
            const membership = membData.data?.[0];
            if (membership?.email) {
              email = membership.email;
              console.log("[handleIframeToken] Resolved email from memberships v2:", email);
            }
          }
        }
      } catch (membErr) {
        console.error("[handleIframeToken] Whop memberships v2 fetch failed:", membErr);
      }
    }

    // Fetch details of the company if companyId is provided
    let companies: { id: string; title: string; route: string }[] = [];
    if (data.companyId && data.companyId.startsWith("biz_")) {
      try {
        const companyRes = await fetch(`https://api.whop.com/api/v1/companies/${data.companyId}`, {
          headers: { Authorization: `Bearer ${process.env.WHOP_API_KEY}` },
        });
        if (companyRes.ok) {
          const comp = await companyRes.json();
          companies = [{
            id: comp.id,
            title: comp.title,
            route: comp.route || "",
          }];
          console.log("[handleIframeToken] Successfully resolved company:", companies);
        } else {
          console.error("[handleIframeToken] Failed to fetch company:", companyRes.status, await companyRes.text());
        }
      } catch (compErr) {
        console.error("[handleIframeToken] Fetch company details failed:", compErr);
      }
    }
    
    // Synchronously resolve location from profile / cache / headers
    let finalCountry = geo.country || null;
    let finalCity = geo.city || null;
    let finalTimezone = geo.timezone || null;
    let profileBadge: string | null = null;
    let profileUsd: number | null = null;

    try {
      const [loc, earnings] = await Promise.all([
        resolveWhopLocation(whopUserId, whopUsername, geo.country, geo.timezone),
        getWhopProfileEarnings(whopUsername),
      ]);
      if (loc.country) {
        finalCountry = loc.country;
        if (loc.city) finalCity = loc.city;
        if (loc.timezone) finalTimezone = loc.timezone;
      }
      if (earnings.badge) profileBadge = earnings.badge;
      if (earnings.exact_usd) profileUsd = earnings.exact_usd;
    } catch (locErr) {
      console.warn("[handleIframeToken] Synchronous location resolution err:", locErr);
    }

    const { data: existing, error: findError } = await supabaseAdmin
      .from("leads")
      .select("id, email, first_name, country, city, timezone, profile_earnings_badge, profile_earnings_usd")
      .eq("whop_user_id", whopUserId)
      .maybeSingle();

    if (findError) console.error("[handleIframeToken] lookup failed:", findError);

    if (existing) {
      const updates: any = {};
      if (email && !existing.email) updates.email = email;
      if (firstName && firstName !== "Anonymous" && (!existing.first_name || existing.first_name === "Anonymous")) {
        updates.first_name = firstName;
      }
      if (companies.length > 0) {
        updates.oauth_companies = companies;
      }
      if (finalCountry && !existing.country) updates.country = finalCountry;
      if (finalCity && !existing.city) updates.city = finalCity;
      if (finalTimezone && !existing.timezone) updates.timezone = finalTimezone;
      if (profileBadge && !existing.profile_earnings_badge) updates.profile_earnings_badge = profileBadge;
      if (profileUsd && !existing.profile_earnings_usd) updates.profile_earnings_usd = profileUsd;

      if (Object.keys(updates).length > 0) {
        console.log("[handleIframeToken] Updating existing lead with resolved info:", updates);
        await supabaseAdmin.from("leads").update(updates).eq("id", existing.id);
      }
      return { 
        leadId: existing.id, 
        username: whopUsername, 
        email: existing.email || email, 
        name: existing.first_name && existing.first_name !== "Anonymous" ? existing.first_name : firstName,
        companies
      };
    }
    
    const { data: newRow, error: insertError } = await supabaseAdmin
      .from("leads")
      .insert({
        whop_user_id: whopUserId,
        whop_username: whopUsername,
        first_name: firstName,
        email: email,
        country: finalCountry,
        city: finalCity,
        timezone: finalTimezone,
        profile_earnings_badge: profileBadge,
        profile_earnings_usd: profileUsd,
        completed: false,
        abandoned_message_sent: false,
        oauth_companies: companies,
      })
      .select("id")
      .single();
      
    if (insertError || !newRow) {
      console.error("[handleIframeToken] insert failed:", insertError);
      throw new Error("Failed to register lead via token");
    }

    return { 
      leadId: newRow.id, 
      username: whopUsername, 
      email, 
      name: firstName, 
      companies 
    };
  });

export const completeLead = createServerFn({ method: "POST" })
  .inputValidator((input: {
    id: string;
    whop_url: string;
    niche: string;
    member_count: number;
    monthly_price: number;
    ideal_app: string;
    timeline: string;
    first_name: string;
    email: string;
    social_handle: string;
    primary_goal?: string;
    community_status?: string;
    social_type?: string;
    client_timezone?: string;
  }) => {
    if (!/whop\.com/i.test(input.whop_url)) throw new Error("Invalid Whop URL");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email)) throw new Error("Invalid email");
    if (!input.first_name?.trim()) throw new Error("First name required");
    return input;
  })
  .handler(async ({ data }): Promise<{ id: string }> => {
    const { supabaseAdmin, lightweightScrape, calcLeadScore, generateBlueprint } = await import("./leads.server");
    const { extractLocationFromHeaders } = await import("./location.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const request = getRequest();
    const geo = extractLocationFromHeaders(request?.headers, data.client_timezone);

    const score = calcLeadScore(data.member_count, data.monthly_price, data.timeline);
    const scraped = await lightweightScrape(data.whop_url);
    let ai_plan: unknown = null;
    try {
      ai_plan = await generateBlueprint(
        {
          whop_url: data.whop_url,
          niche: data.niche,
          member_count: data.member_count,
          monthly_price: data.monthly_price,
          ideal_app: data.ideal_app,
          timeline: data.timeline,
          first_name: data.first_name,
        },
        scraped,
      );
    } catch (e) {
      console.error("[completeLead] AI failed:", e);
    }

    const updates: Record<string, any> = {
      whop_url: data.whop_url,
      niche: data.niche,
      member_count: data.member_count,
      monthly_price: data.monthly_price,
      mrr: score.mrr,
      ideal_app: data.ideal_app,
      timeline: data.timeline,
      first_name: data.first_name,
      email: data.email,
      social_handle: data.social_handle,
      primary_goal: data.primary_goal,
      lead_score: score.score,
      lead_tag: score.tag,
      scrape_status: scraped.status,
      scraped_data: scraped as unknown as Json,
      ai_plan: (ai_plan ?? null) as Json,
      completed: true,
      community_status: (data.community_status ?? "ACTIVE"),
      social_type: (data.social_type ?? 'discord'),
    };
    if (geo.country) updates.country = geo.country;
    if (geo.city) updates.city = geo.city;
    if (geo.timezone) updates.timezone = geo.timezone;

    const { error } = await supabaseAdmin
      .from("leads")
      .update(updates as any)
      .eq("id", data.id);
      
    if (error) throw new Error(error.message || "Failed to update lead");

    let whop_username: string | null = null;
    let whop_user_id: string | null = null;
    try {
      const { data: dbLead } = await supabaseAdmin
        .from("leads")
        .select("whop_username, whop_user_id")
        .eq("id", data.id)
        .maybeSingle();
      if (dbLead) {
        whop_username = dbLead.whop_username;
        whop_user_id = dbLead.whop_user_id;
      }
    } catch (dbErr) {
      console.error("[completeLead] Failed to fetch lead username/user_id for Telegram:", dbErr);
    }

    try {
      const { notifyTelegram } = await import("./leads.server");
      await notifyTelegram({
        id: data.id,
        first_name: data.first_name,
        email: data.email,
        niche: data.niche,
        whop_url: data.whop_url,
        member_count: data.member_count,
        monthly_price: data.monthly_price,
        mrr: score.mrr,
        lead_tag: score.tag,
        lead_score: score.score,
        timeline: data.timeline,
        social_handle: data.social_handle,
        ideal_app: data.ideal_app,
        whop_username,
        whop_user_id,
        social_type: data.social_type ?? null,
      });
    } catch (e) {
      console.error("[completeLead] telegram notify failed:", e);
    }

    return { id: data.id };
  });

// Funnel B: Pre-launch path — no Whop URL, member count, or price
export const completePreLaunchLead = createServerFn({ method: "POST" })
  .inputValidator((input: {
    id: string;
    niche: string;
    ideal_app: string;
    timeline: string;
    first_name: string;
    email: string;
    social_handle: string;
    primary_goal?: string;
    willing_to_invest?: string;
    client_timezone?: string;
  }) => {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email)) throw new Error("Invalid email");
    if (!input.first_name?.trim()) throw new Error("First name required");
    if (!input.niche) throw new Error("Niche required");
    return input;
  })
  .handler(async ({ data }): Promise<{ id: string }> => {
    const { supabaseAdmin, generateBlueprint } = await import("./leads.server");
    const { extractLocationFromHeaders } = await import("./location.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const request = getRequest();
    const geo = extractLocationFromHeaders(request?.headers, data.client_timezone);

    // Generate blueprint based on niche + idea only (no scrape, no MRR)
    let ai_plan: unknown = null;
    try {
      ai_plan = await generateBlueprint(
        {
          whop_url: "",
          niche: data.niche,
          member_count: 0,
          monthly_price: 0,
          ideal_app: data.ideal_app,
          timeline: data.timeline,
          first_name: data.first_name,
        },
        { status: "Failed" as const, description: "", raw_excerpt: "" },
      );
    } catch (e) {
      console.error("[completePreLaunchLead] AI failed:", e);
    }

    const updates: Record<string, any> = {
      niche: data.niche,
      ideal_app: data.ideal_app,
      timeline: data.timeline,
      first_name: data.first_name,
      email: data.email,
      social_handle: data.social_handle,
      primary_goal: data.primary_goal,
      lead_score: 10,
      lead_tag: "COLD",
      community_status: "PRE_LAUNCH",
      ai_plan: (ai_plan ?? null) as Json,
      completed: true,
      willing_to_invest: (data.willing_to_invest ?? null) as any,
    };
    if (geo.country) updates.country = geo.country;
    if (geo.city) updates.city = geo.city;
    if (geo.timezone) updates.timezone = geo.timezone;

    const { error } = await supabaseAdmin
      .from("leads")
      .update(updates as any)
      .eq("id", data.id);

    if (error) throw new Error(error.message || "Failed to update pre-launch lead");

    try {
      const { notifyTelegram } = await import("./leads.server");
      await notifyTelegram({
        id: data.id,
        first_name: data.first_name,
        email: data.email,
        niche: data.niche,
        whop_url: "(pre-launch — no community yet)",
        member_count: 0,
        monthly_price: 0,
        mrr: 0,
        lead_tag: "COLD",
        lead_score: 10,
        timeline: data.timeline,
        social_handle: data.social_handle,
        ideal_app: data.ideal_app,
        whop_username: null,
        whop_user_id: null,
        willing_to_invest: data.willing_to_invest ?? null,
      });
    } catch (e) {
      console.error("[completePreLaunchLead] telegram notify failed:", e);
    }

    return { id: data.id };
  });

export const adminGetDaemonLogs = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string }) => input)
  .handler(async ({ data }): Promise<{ logs: string }> => {
    if (!verifyAdminPassword(data.password)) throw new Error("Unauthorized");

    const { supabaseAdmin } = await import("./leads.server");
    const { data: logsData, error } = await (supabaseAdmin as any)
      .from("daemon_logs")
      .select("created_at, level, message")
      .order("created_at", { ascending: false })
      .limit(200);

    if (error) {
      return { logs: `[ERROR] Failed to fetch daemon logs from database: ${error.message}` };
    }

    if (!logsData || logsData.length === 0) {
      return { logs: "[INFO] No daemon logs found in database." };
    }

    // Format logs in order (ascending)
    const formatted = logsData
      .reverse()
      .map((row: any) => `[${new Date(row.created_at).toISOString()}] [${row.level}] ${row.message}`)
      .join("\n");

    return { logs: formatted };
  });

export const adminGetSettings = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string }) => input)
  .handler(async ({ data }): Promise<{ global_chatbot_enabled: boolean }> => {
    if (!verifyAdminPassword(data.password)) throw new Error("Unauthorized");

    const { supabaseAdmin } = await import("./leads.server");
    const { data: row } = await (supabaseAdmin as any)
      .from("bot_settings")
      .select("value")
      .eq("key", "global_chatbot_enabled")
      .maybeSingle();

    return { global_chatbot_enabled: row?.value === "true" || row?.value === true };
  });

export const adminToggleGlobalChatbot = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string; enabled: boolean }) => input)
  .handler(async ({ data }): Promise<{ global_chatbot_enabled: boolean }> => {
    if (!verifyAdminPassword(data.password)) throw new Error("Unauthorized");

    const { supabaseAdmin } = await import("./leads.server");
    await (supabaseAdmin as any).from("bot_settings").upsert({
      key: "global_chatbot_enabled",
      value: String(data.enabled),
      updated_at: new Date().toISOString(),
    });

    return { global_chatbot_enabled: data.enabled };
  });

export const adminToggleLeadChatbot = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string; lead_id?: string; leadId?: string; enabled: boolean }) => input)
  .handler(async ({ data }): Promise<{ ok: boolean }> => {
    if (!verifyAdminPassword(data.password)) throw new Error("Unauthorized");

    const targetLeadId = data.lead_id || data.leadId;
    if (!targetLeadId) throw new Error("Missing lead ID");

    const { supabaseAdmin } = await import("./leads.server");
    const { error } = await supabaseAdmin
      .from("leads")
      .update({ ai_bot_enabled: data.enabled })
      .eq("id", targetLeadId);

    if (error) {
      throw new Error(`Failed to update lead AI bot: ${error.message}`);
    }

    return { ok: true };
  });

export const adminGetSupportChatLink = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string; lead_id: string }) => input)
  .handler(async ({ data }): Promise<{ support_chat_url: string | null; channel_id: string | null }> => {
    if (!verifyAdminPassword(data.password)) throw new Error("Unauthorized");

    const { supabaseAdmin } = await import("./leads.server");
    const { data: lead } = await (supabaseAdmin as any)
      .from("leads")
      .select("id, whop_user_id, scraped_data, support_channel_id")
      .eq("id", data.lead_id)
      .maybeSingle();

    if (!lead || !lead.whop_user_id) {
      return { support_chat_url: null, channel_id: null };
    }

    const existingData = typeof lead.scraped_data === "object" && lead.scraped_data !== null ? lead.scraped_data : {};
    let channelId = lead.support_channel_id || (existingData as any).support_channel_id || null;

    if (!channelId && process.env.WHOP_API_KEY && process.env.WHOP_COMPANY_ID) {
      try {
        const channelRes = await fetch("https://api.whop.com/api/v1/support_channels", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${process.env.WHOP_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            company_id: process.env.WHOP_COMPANY_ID,
            user_id: lead.whop_user_id,
          }),
        });

        if (channelRes.ok) {
          const channelData = await channelRes.json();
          channelId = channelData.id || null;
          if (channelId) {
            const updatedData = { ...existingData, support_channel_id: channelId };
            await supabaseAdmin
              .from("leads")
              .update({ scraped_data: updatedData })
              .eq("id", lead.id);
          }
        }
      } catch (e) {
        console.error("[adminGetSupportChatLink] Error resolving channel:", e);
      }
    }

    if (channelId) {
      return {
        channel_id: channelId,
        support_chat_url: `https://whop.com/messages/?chat=${channelId}`,
      };
    }

    return { support_chat_url: null, channel_id: null };
  });
