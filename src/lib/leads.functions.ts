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
  community_status: "ACTIVE" | "PRE_LAUNCH" | "NO_COMMUNITY";
  social_type: string | null;
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
  .inputValidator((input: { session_id: string }) => input)
  .handler(async ({ data }): Promise<{ id: string; name: string; email: string }> => {
    const { supabaseAdmin } = await import("./leads.server");
    const { getRequest } = await import("@tanstack/react-start/server");
    const request = getRequest();

    console.log("[registerAnonymousLead] Started. Session ID:", data.session_id);
    if (request) {
      const headersMap = Object.fromEntries(request.headers.entries());
      console.log("[registerAnonymousLead] Request headers keys:", Object.keys(headersMap));
      console.log("[registerAnonymousLead] x-whop-user-token exists:", !!headersMap["x-whop-user-token"]);
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
    const query = supabaseAdmin.from("leads").select("id, email, first_name, whop_username, whop_user_id");
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

      if (Object.keys(updates).length > 0) {
        console.log("[registerAnonymousLead] Updating existing lead with resolved info:", updates);
        await supabaseAdmin.from("leads").update(updates).eq("id", existingLead.id);
      }

      return { id: existingLead.id, name: finalName, email: finalEmail };
    }

    // --- Insert new COLD lead ---
    console.log("[registerAnonymousLead] Inserting new lead. Username:", whopUsername);
    const { data: row, error } = await supabaseAdmin
      .from("leads")
      .insert({
        session_id: data.session_id,
        whop_user_id: whopUserId,
        whop_username: whopUsername,
        first_name: firstName,
        email,
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
  }) => {
    if (!/whop\.com/i.test(input.whop_url)) throw new Error("Invalid Whop URL");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email)) throw new Error("Invalid email");
    if (!input.first_name?.trim()) throw new Error("First name required");
    if (!input.niche || !input.timeline) throw new Error("Missing required fields");
    return input;
  })
  .handler(async ({ data }): Promise<{ id: string }> => {
    const { supabaseAdmin, lightweightScrape, calcLeadScore, generateBlueprint } = await import("./leads.server");
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

export const adminAccess = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string }) => input)
  .handler(async ({ data }): Promise<{ ok: boolean }> => {
    const target = process.env.ADMIN_PASSWORD;
    if (!target) throw new Error("Admin password not configured on server");
    return { ok: data.password === target };
  });

export const adminListLeads = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string }) => input)
  .handler(async ({ data }) => {
    const target = process.env.ADMIN_PASSWORD;
    if (!target || data.password !== target) throw new Error("Unauthorized");
    const { supabaseAdmin } = await import("./leads.server");
    const { data: rows, error } = await supabaseAdmin
      .from("leads")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(500);
    if (error) throw new Error(error.message);
    const leads = (rows ?? []) as unknown as Lead[];
    const stats = {
      total: leads.length,
      hot: leads.filter((l) => l.lead_tag === "HOT").length,
      warm: leads.filter((l) => l.lead_tag === "WARM").length,
      cold: leads.filter((l) => l.lead_tag === "COLD").length,
    };
    return { leads, stats };
  });

export const adminDeleteLead = createServerFn({ method: "POST" })
  .inputValidator((input: { password: string; id: string }) => input)
  .handler(async ({ data }) => {
    const target = process.env.ADMIN_PASSWORD;
    if (!target || data.password !== target) throw new Error("Unauthorized");
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
    
    const scope = "email openid company:basic:read";
    const redirectUri = `${data.origin}/`;
    
    const url = `https://whop.com/oauth/authorize?client_id=${appId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&scope=${encodeURIComponent(scope)}&code_challenge=${codeChallenge}&code_challenge_method=S256&state=funnel`;
    
    return { url, codeVerifier };
  });

export const exchangeOAuthCode = createServerFn({ method: "POST" })
  .inputValidator((input: { code: string; codeVerifier: string; origin: string }) => input)
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
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
      .select("id, email, first_name")
      .eq("whop_user_id", whopUserId)
      .maybeSingle();
      
    if (findError) console.error("[exchangeOAuthCode] error looking up existing:", findError);
    
    if (existing) {
      const updates: any = {};
      if (email && !existing.email) updates.email = email;
      if (firstName && firstName !== "Anonymous" && (!existing.first_name || existing.first_name === "Anonymous")) {
        updates.first_name = firstName;
      }
      if (companies && companies.length > 0) {
        updates.oauth_companies = companies;
      }
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
  .inputValidator((input: { token: string }) => input)
  .handler(async ({ data }) => {
    const { supabaseAdmin } = await import("./leads.server");
    
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
    
    const { data: existing, error: findError } = await supabaseAdmin
      .from("leads")
      .select("id, email, first_name")
      .eq("whop_user_id", whopUserId)
      .maybeSingle();
      
    if (findError) console.error("[handleIframeToken] lookup failed:", findError);
    
    if (existing) {
      const updates: any = {};
      if (email && !existing.email) updates.email = email;
      if (firstName && firstName !== "Anonymous" && (!existing.first_name || existing.first_name === "Anonymous")) {
        updates.first_name = firstName;
      }
      if (Object.keys(updates).length > 0) {
        console.log("[handleIframeToken] Updating existing lead with resolved info:", updates);
        await supabaseAdmin.from("leads").update(updates).eq("id", existing.id);
      }
      return { 
        leadId: existing.id, 
        username: whopUsername, 
        email: existing.email || email, 
        name: existing.first_name && existing.first_name !== "Anonymous" ? existing.first_name : firstName 
      };
    }
    
    const { data: newRow, error: insertError } = await supabaseAdmin
      .from("leads")
      .insert({
        whop_user_id: whopUserId,
        whop_username: whopUsername,
        first_name: firstName,
        email: email,
        completed: false,
        abandoned_message_sent: false,
      })
      .select("id")
      .single();
      
    if (insertError || !newRow) {
      console.error("[handleIframeToken] insert failed:", insertError);
      throw new Error("Failed to register lead via token");
    }
    
    return { leadId: newRow.id, username: whopUsername, email, name: firstName };
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
    community_status?: string;
    social_type?: string;
  }) => {
    if (!/whop\.com/i.test(input.whop_url)) throw new Error("Invalid Whop URL");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email)) throw new Error("Invalid email");
    if (!input.first_name?.trim()) throw new Error("First name required");
    return input;
  })
  .handler(async ({ data }): Promise<{ id: string }> => {
    const { supabaseAdmin, lightweightScrape, calcLeadScore, generateBlueprint } = await import("./leads.server");
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

    const { error } = await supabaseAdmin
      .from("leads")
      .update({
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
        lead_score: score.score,
        lead_tag: score.tag,
        scrape_status: scraped.status,
        scraped_data: scraped as unknown as Json,
        ai_plan: (ai_plan ?? null) as Json,
        completed: true,
        community_status: (data.community_status ?? "ACTIVE"),
        social_type: (data.social_type ?? 'discord'),
      } as any)
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
    willing_to_invest?: string;
  }) => {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email)) throw new Error("Invalid email");
    if (!input.first_name?.trim()) throw new Error("First name required");
    if (!input.niche) throw new Error("Niche required");
    return input;
  })
  .handler(async ({ data }): Promise<{ id: string }> => {
    const { supabaseAdmin, generateBlueprint } = await import("./leads.server");

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

    const { error } = await supabaseAdmin
      .from("leads")
      .update({
        niche: data.niche,
        ideal_app: data.ideal_app,
        timeline: data.timeline,
        first_name: data.first_name,
        email: data.email,
        social_handle: data.social_handle,
        lead_score: 10,
        lead_tag: "COLD",
        community_status: "PRE_LAUNCH",
        ai_plan: (ai_plan ?? null) as Json,
        completed: true,
        willing_to_invest: (data.willing_to_invest ?? null) as any,
      } as any)
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
    const target = process.env.ADMIN_PASSWORD;
    if (!target || data.password !== target) throw new Error("Unauthorized");

    const fs = await import("fs");
    const path = await import("path");

    const logPath = path.join(process.cwd(), "daemon_logs.txt");
    if (!fs.existsSync(logPath)) {
      return { logs: "[INFO] No daemon logs found. Make sure the background daemon is running." };
    }

    try {
      const content = fs.readFileSync(logPath, "utf-8");
      const lines = content.split("\n");
      const lastLines = lines.slice(-200).join("\n");
      return { logs: lastLines };
    } catch (e: any) {
      return { logs: `[ERROR] Failed to read daemon logs: ${e.message || e}` };
    }
  });
