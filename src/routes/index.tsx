import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState, useEffect, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Link2,
  TrendingUp,
  Trophy,
  Repeat,
  Code2,
  GraduationCap,
  Gamepad2,
  Sparkles,
  Users,
  DollarSign,
  Gift,
} from "lucide-react";
import SelectCards from "@/components/wop/SelectCards";
import StepProgress from "@/components/wop/StepProgress";
import LoadingScreen from "@/components/wop/LoadingScreen";
import { createLead, getOAuthUrl, exchangeOAuthCode, handleIframeToken, completeLead, registerAnonymousLead, completePreLaunchLead, getLeadOAuthInfo } from "@/lib/leads.functions";
import { createSdk } from "@whop/iframe";
import logoAsset from "@/assets/app-builders-logo.png.asset.json";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "App Builders — Free custom retention app for your Whop community" },
      {
        name: "description",
        content:
          "Tell us about your Whop community and we'll design (and build) a custom retention app for you — free.",
      },
      { property: "og:title", content: "App Builders — Free custom retention app" },
      {
        property: "og:description",
        content: "We design and build a custom retention app for your Whop community, free.",
      },
    ],
  }),
  component: Onboarding,
});

const TOTAL_A = 8; // Funnel A: active community
const TOTAL_B = 5; // Funnel B: pre-launch
const WHOP_COMMUNITY_URL = "https://whop.com/joined/app-builders-f882/";

const NICHES = [
  { value: "Trading/Finance", label: "Trading / Finance", icon: <TrendingUp className="h-5 w-5" /> },
  { value: "Sports Betting", label: "Sports Betting", icon: <Trophy className="h-5 w-5" /> },
  { value: "Reselling", label: "Reselling", icon: <Repeat className="h-5 w-5" /> },
  { value: "SaaS/Tech/AI", label: "SaaS / Tech / AI", icon: <Code2 className="h-5 w-5" /> },
  { value: "Coaching/Agency", label: "Coaching / Agency", icon: <GraduationCap className="h-5 w-5" /> },
  { value: "Gaming/Other", label: "Gaming / Other", icon: <Gamepad2 className="h-5 w-5" /> },
];

const TIMELINES = [
  { value: "ASAP / within 1 week", label: "ASAP / within 1 week", hint: "Ready to move now" },
  { value: "Within a month", label: "Within a month", hint: "Planning now" },
  { value: "2 months+", label: "2 months+", hint: "Q3+ maybe" },
];

const INVEST_OPTIONS = [
  { value: "Yes", label: "Yes, I am willing to invest", hint: "I understand hosting has monthly costs" },
  { value: "No", label: "No, I need a 100% free solution", hint: "Looking to build without budget" },
];

const stepVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export function Onboarding() {
  const navigate = useNavigate();
  const [started, setStarted] = useState(false);
  const [communityStatus, setCommunityStatus] = useState<"UNSET" | "ACTIVE" | "PRE_LAUNCH" | "NO_COMMUNITY">("UNSET");
  const [funnelTrack, setFunnelTrack] = useState<"A" | "B">("A");
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [leadId, setLeadId] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem("lead_id");
    }
    return null;
  });
  const [form, setForm] = useState({
    whop_url: "",
    niche: "",
    member_count: 150,
    monthly_price: 30,
    ideal_app: "",
    timeline: "",
    first_name: "",
    email: "",
    social_handle: "",
    willing_to_invest: "",
    social_type: "discord",
  });
  const [companies, setCompanies] = useState<{ id: string; title: string; route: string }[]>([]);
  const [whopInputMode, setWhopInputMode] = useState<"UNSET" | "AUTO" | "MANUAL">("UNSET");
  const [oauthConnecting, setOauthConnecting] = useState(false);
  const [isOAuthCallback, setIsOAuthCallback] = useState(false);
  const [callbackStatus, setCallbackStatus] = useState<"loading" | "success" | "error">("loading");
  const [callbackRedirectUrl, setCallbackRedirectUrl] = useState("");

  // Detect if running inside Whop iframe (proxied subdomain)
  const isInsideWhop = typeof window !== "undefined" &&
    (window.location.hostname.endsWith(".apps.whop.com") ||
     window.location.pathname.startsWith("/experiences/") ||
     window !== window.top);

  const iframeSdk = useMemo(() => {
    if (typeof window === "undefined") return null;
    const appId = import.meta.env.VITE_WHOP_APP_ID || "";
    return createSdk({ appId });
  }, []);

  useEffect(() => {
    const handleOAuthSuccess = (data: any) => {
      const { leadId: userLeadId, name, email, companies: userCompanies } = data;
      setLeadId(userLeadId);
      sessionStorage.setItem("lead_id", userLeadId);
      setForm((f) => ({
        ...f,
        first_name: name || f.first_name,
        email: email || f.email,
      }));
      if (userCompanies && userCompanies.length > 0) {
        setCompanies(userCompanies);
        setWhopInputMode("AUTO");
      } else {
        setWhopInputMode("MANUAL");
      }
      setCommunityStatus("ACTIVE");
      setStarted(true);
      setOauthConnecting(false);
    };

    const handleMessage = (e: MessageEvent) => {
      const originMatch = e.origin.includes("localhost") || e.origin === "https://free-app-flow.vercel.app";
      if (!originMatch) return;
      if (e.data?.type === "WHOP_OAUTH_SUCCESS") {
        handleOAuthSuccess(e.data);
      }
    };
    window.addEventListener("message", handleMessage);

    // BroadcastChannel listener
    let channel: BroadcastChannel | null = null;
    try {
      channel = new BroadcastChannel("whop_oauth_channel");
      channel.onmessage = (event) => {
        if (event.data && event.data.type === "WHOP_OAUTH_SUCCESS") {
          handleOAuthSuccess(event.data);
        }
      };
    } catch (err) {
      console.error("BroadcastChannel failed to initialize:", err);
    }

    // LocalStorage listener fallback
    const handleStorage = (event: StorageEvent) => {
      if (event.key === "whop_oauth_result" && event.newValue) {
        try {
          const data = JSON.parse(event.newValue);
          if (data.type === "WHOP_OAUTH_SUCCESS") {
            handleOAuthSuccess(data);
            localStorage.removeItem("whop_oauth_result");
          }
        } catch (e) {
          console.error("Failed to parse storage oauth result:", e);
        }
      }
    };
    window.addEventListener("storage", handleStorage);

    return () => {
      window.removeEventListener("message", handleMessage);
      window.removeEventListener("storage", handleStorage);
      if (channel) {
        channel.close();
      }
    };
  }, []);

  const connectWhopOauth = async () => {
    setOauthConnecting(true);
    try {
      const appId = import.meta.env.VITE_WHOP_APP_ID;
      if (!appId) throw new Error("Missing VITE_WHOP_APP_ID");

      // PKCE: generate fully client-side using Web Crypto API
      function base64url(bytes: Uint8Array) {
        return btoa(String.fromCharCode(...bytes))
          .replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
      }
      function randomString(len: number) {
        return base64url(crypto.getRandomValues(new Uint8Array(len)));
      }
      async function sha256b64url(str: string) {
        return base64url(
          new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str)))
        );
      }

      const codeVerifier = randomString(32);
      const codeChallenge = await sha256b64url(codeVerifier);
      const nonce = randomString(16);

      // Encode the verifier and original host in state so we can recover them from the redirect URL
      const statePayload = btoa(JSON.stringify({ v: codeVerifier, n: nonce, h: window.location.host }));

      const redirectUri = window.location.origin.includes("localhost")
        ? `${window.location.origin}/`
        : window.location.origin.includes("whop.com")
          ? `${window.location.origin}/`
          : "https://free-app-flow.vercel.app/";

      const params = new URLSearchParams({
        response_type: "code",
        client_id: appId,
        redirect_uri: redirectUri,
        scope: "openid profile email company:basic:read",
        state: statePayload,
        nonce,
        code_challenge: codeChallenge,
        code_challenge_method: "S256",
      });

      const url = `https://api.whop.com/oauth/authorize?${params}`;

      // Detect if we should use redirect instead of popup (e.g., mobile device or inside Whop WebView)
      const isMobile = typeof window !== "undefined" && (
        /iPhone|iPad|iPod|Android/i.test(navigator.userAgent) ||
        isInsideWhop
      );

      if (isMobile) {
        window.location.href = url;
        return;
      }

      const w = 600;
      const h = 750;
      const left = window.screen.width / 2 - w / 2;
      const top = window.screen.height / 2 - h / 2;

      const popup = window.open(
        url,
        "whop-oauth",
        `width=${w},height=${h},top=${top},left=${left},status=no,resizable=yes`
      );

      const timer = setInterval(() => {
        if (popup?.closed) {
          clearInterval(timer);
          setOauthConnecting(false);
        }
      }, 1000);
    } catch (err) {
      console.error("Failed to start OAuth popup:", err);

      setOauthConnecting(false);
      setError("Failed to open Whop authentication window.");
    }
  };

  useEffect(() => {
    const handleAuth = async () => {
      if (typeof window === "undefined") return;
      
      const searchParams = new URLSearchParams(window.location.search);
      const code = searchParams.get("code");
      const errorParam = searchParams.get("error");
      const whopAuthSuccess = searchParams.get("whop_auth_success") === "1";
      const queryLeadId = searchParams.get("lead_id");
      
      // Whop injects the user token via query params when embedded
      const whopUserToken = searchParams.get("whop-user-token") || searchParams.get("whop-dev-user-token");
      
      if (errorParam) {
        window.history.replaceState({}, document.title, window.location.pathname);
        setCommunityStatus("ACTIVE");
        setStarted(true);
        setOauthConnecting(false);
        return;
      }
      
      if (whopAuthSuccess && queryLeadId) {
        setLoading(true);
        try {
          const leadInfo = await getLeadOAuthInfo({ data: { leadId: queryLeadId } });
          setLeadId(queryLeadId);
          sessionStorage.setItem("lead_id", queryLeadId);
          setForm((f) => ({
            ...f,
            first_name: leadInfo.name,
            email: leadInfo.email,
          }));
          if (leadInfo.companies && leadInfo.companies.length > 0) {
            setCompanies(leadInfo.companies);
            setWhopInputMode("AUTO");
          }
          setCommunityStatus("ACTIVE");
          setStarted(true);
          
          window.history.replaceState({}, document.title, window.location.pathname);
        } catch (getErr) {
          console.error("Failed to retrieve deep-linked lead data:", getErr);
          setError("Failed to retrieve authentication details.");
        } finally {
          setLoading(false);
        }
        return;
      }
      
      if (code) {
        setIsOAuthCallback(true);
        setCallbackStatus("loading");
        setLoading(true);
        try {
          // Extract the code_verifier and original host from the state parameter
          let codeVerifier = "";
          let originalHost = "";
          const stateParam = searchParams.get("state") || "";
          try {
            const decoded = JSON.parse(atob(stateParam));
            codeVerifier = decoded.v || "";
            originalHost = decoded.h || "";
          } catch {
            // Fallback: try legacy sessionStorage path
            codeVerifier = sessionStorage.getItem("whop_verifier") || "";
          }

          const targetOrigin = window.location.origin.includes("localhost")
            ? window.location.origin
            : window.location.origin.includes("whop.com")
              ? window.location.origin
              : "https://free-app-flow.vercel.app";

          const res = await exchangeOAuthCode({
            data: {
              code,
              codeVerifier,
              origin: targetOrigin,
            }
          });

          if (window.opener) {
            try {
              window.opener.postMessage({
                type: "WHOP_OAUTH_SUCCESS",
                leadId: res.leadId,
                name: res.name,
                email: res.email,
                companies: res.companies,
              }, "*"); // Post to wildcard since parent may be on apps.whop.com subdomain
            } catch (msgErr) {
              console.error("Failed to post message to opener:", msgErr);
            }
          }

          // Broadcast to the channel for same-origin iframe sync
          try {
            const channel = new BroadcastChannel("whop_oauth_channel");
            channel.postMessage({
              type: "WHOP_OAUTH_SUCCESS",
              leadId: res.leadId,
              name: res.name,
              email: res.email,
              companies: res.companies,
            });
            channel.close();
          } catch (chErr) {
            console.error("Broadcast failed:", chErr);
          }

          // Write to localStorage for cross-context storage fallback
          try {
            localStorage.setItem("whop_oauth_result", JSON.stringify({
              type: "WHOP_OAUTH_SUCCESS",
              leadId: res.leadId,
              name: res.name,
              email: res.email,
              companies: res.companies,
              timestamp: Date.now()
            }));
          } catch (stErr) {
            console.error("Failed to save result to localStorage:", stErr);
          }

          let redirectUrl = "";
          if (originalHost) {
            const protocol = originalHost.includes("localhost") ? "http" : "https";
            redirectUrl = `${protocol}://${originalHost}/?lead_id=${res.leadId}&whop_auth_success=1`;
            setCallbackRedirectUrl(redirectUrl);
          }

          // If we are on mobile or not in a popup, redirect instantly without showing any success page
          const isSameWindow = typeof window !== "undefined" && (!window.opener || isInsideWhop);
          if (isSameWindow && redirectUrl) {
            window.location.replace(redirectUrl);
            return;
          }

          setCallbackStatus("success");

          // Attempt to close the window automatically
          setTimeout(() => {
            try {
              window.close();
            } catch (closeErr) {
              console.error("window.close failed:", closeErr);
            }
          }, 1200);

          // Mobile / standalone fallback deep-linking redirect
          if (redirectUrl) {
            setTimeout(() => {
              window.location.href = redirectUrl;
            }, 2500);
          }
        } catch (e) {
          console.error("OAuth exchange failed:", e);
          setCallbackStatus("error");
          setError("Whop authentication failed. Please try again.");
        } finally {
          setLoading(false);
        }
      } else if (whopUserToken) {
        setLoading(true);
        try {
          const companyId = searchParams.get("company_id") || 
                            searchParams.get("company-id") || 
                            searchParams.get("companyId") || 
                            searchParams.get("biz_id") || 
                            searchParams.get("biz-id") || 
                            searchParams.get("bizId");
          const res = await handleIframeToken({ data: { token: whopUserToken, companyId } });
          setLeadId(res.leadId);
          sessionStorage.setItem("lead_id", res.leadId);
          setForm((f) => ({
            ...f,
            first_name: res.name,
            email: res.email,
          }));
          if (res.companies && res.companies.length > 0) {
            setCompanies(res.companies);
            setWhopInputMode("AUTO");
            const firstComp = res.companies[0];
            if (firstComp.route) {
              setForm((f) => ({
                ...f,
                whop_url: `https://whop.com/${firstComp.route}`,
              }));
            }
          }
          // Auto-start funnel when inside Whop iframe with a valid token
          setCommunityStatus("ACTIVE");
          setStarted(true);
          
          window.history.replaceState({}, document.title, window.location.pathname);
        } catch (e) {
          console.error("Iframe token handler failed:", e);
        } finally {
          setLoading(false);
        }
      } else if (isInsideWhop) {
        // Auto-register/verify inside iframe on page load
        try {
          let sid = sessionStorage.getItem("whop_session_id");
          if (!sid) {
            try {
              sid = crypto.randomUUID();
            } catch {
              sid = "fallback-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now();
            }
            sessionStorage.setItem("whop_session_id", sid);
          }
          const res = await registerAnonymousLead({ data: { session_id: sid } });
          setLeadId(res.id);
          sessionStorage.setItem("lead_id", res.id);
          setForm((f) => ({
            ...f,
            first_name: (res.name && res.name !== "Anonymous") ? res.name : f.first_name,
            email: res.email || f.email,
          }));
        } catch (e) {
          console.error("Auto registration failed:", e);
        }
      }
    };
    
    void handleAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isInsideWhop]);

  const update = <K extends keyof typeof form>(key: K, val: (typeof form)[K]) => setForm((f) => ({ ...f, [key]: val }));

  const TOTAL = funnelTrack === "A" ? TOTAL_A : TOTAL_B;

  const mrr = useMemo(
    () => Math.max(0, form.member_count) * Math.max(0, form.monthly_price),
    [form.member_count, form.monthly_price],
  );
  const annualLoss = useMemo(() => Math.round(mrr * 3), [mrr]);
  const monthlyLoss = useMemo(() => Math.round(mrr * 0.25), [mrr]);

  const urlValid = useMemo(() => /whop\.com/i.test(form.whop_url), [form.whop_url]);
  const emailValid = useMemo(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email), [form.email]);

  const canAdvance = (() => {
    if (funnelTrack === "B") {
      switch (step) {
        case 1: return !!form.niche;
        case 2: return true;
        case 3: return !!form.willing_to_invest;
        case 4: return !!form.timeline;
        case 5: return !!form.first_name && emailValid;
        default: return true;
      }
    }
    // Funnel A
    switch (step) {
      case 1: return urlValid;
      case 2: return !!form.niche;
      case 3: return form.member_count > 0;
      case 4: return form.monthly_price > 0;
      case 5: return true;
      case 6: return true;
      case 7: return !!form.timeline;
      case 8: return !!form.first_name && emailValid;
      default: return true;
    }
  })();

  const startOAuthFlow = async () => {
    // If inside Whop iframe, OAuth redirect is blocked — go directly to the funnel
    // Immediately register an anonymous lead so it shows in admin right away
    if (isInsideWhop) {
      setError(null);
      setLoading(true);
      try {
        // Generate a stable session ID for this browser session
        let sid = sessionStorage.getItem("whop_session_id");
        if (!sid) {
          try {
            sid = crypto.randomUUID();
          } catch {
            sid = "fallback-" + Math.random().toString(36).substring(2, 15) + "-" + Date.now();
          }
          sessionStorage.setItem("whop_session_id", sid);
        }
        const res = await registerAnonymousLead({ data: { session_id: sid } });
        setLeadId(res.id);
        sessionStorage.setItem("lead_id", res.id);
        // Pre-fill name and email if resolved
        setForm((f) => ({
          ...f,
          first_name: (res.name && res.name !== "Anonymous") ? res.name : f.first_name,
          email: res.email || f.email,
        }));
        setStarted(true);
      } catch (e) {
        console.error("Failed to register anonymous lead:", e);
        setError("Failed to register lead inside iframe: " + (e instanceof Error ? e.message : String(e)));
      } finally {
        setLoading(false);
      }
      return;
    }
    setLoading(true);
    try {
      // Always use the canonical Vercel URL as the OAuth redirect origin
      const res = await getOAuthUrl({ data: { origin: "https://free-app-flow.vercel.app" } });
      sessionStorage.setItem("whop_verifier", res.codeVerifier);
      window.location.href = res.url;
    } catch (e) {
      console.error("Failed to generate OAuth URL:", e);
      setError("Failed to initialize Whop authentication. Please try again.");
      setLoading(false);
    }
  };

  const submitFunnelA = async () => {
    setLoading(true);
    setError(null);
    try {
      let finalId = leadId;
      if (finalId) {
        await completeLead({
          data: {
            id: finalId,
            whop_url: form.whop_url,
            niche: form.niche,
            member_count: form.member_count,
            monthly_price: form.monthly_price,
            ideal_app: form.ideal_app,
            timeline: form.timeline,
            first_name: form.first_name,
            email: form.email,
            social_handle: form.social_handle,
            community_status: "ACTIVE",
            social_type: form.social_type,
          }
        });
      } else {
        const lead = await createLead({ data: form });
        finalId = lead.id;
      }
      sessionStorage.removeItem("lead_id");
      await new Promise((r) => setTimeout(r, 800));
      navigate({ to: "/blueprint/$id", params: { id: finalId } });
    } catch (e) {
      console.error(e);
      setError("Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  const submitFunnelB = async () => {
    setLoading(true);
    setError(null);
    try {
      const finalId = leadId;
      if (!finalId) throw new Error("No lead ID found");
      await completePreLaunchLead({
        data: {
          id: finalId,
          niche: form.niche,
          ideal_app: form.ideal_app,
          timeline: form.timeline,
          first_name: form.first_name,
          email: form.email,
          social_handle: form.social_handle,
          willing_to_invest: form.willing_to_invest,
        }
      });
      sessionStorage.removeItem("lead_id");
      await new Promise((r) => setTimeout(r, 800));
      navigate({ to: "/blueprint/$id", params: { id: finalId } });
    } catch (e) {
      console.error(e);
      setError("Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  const submit = funnelTrack === "B" ? submitFunnelB : submitFunnelA;

  const next = () => {
    if (!canAdvance) return;
    if (step < TOTAL) setStep((s) => s + 1);
    else void submit();
  };
  const back = () => step > 1 && setStep((s) => s - 1);

  // Gate: select community status before entering the funnel
  const selectCommunityStatus = (status: "ACTIVE" | "PRE_LAUNCH" | "NO_COMMUNITY") => {
    setCommunityStatus(status);
    if (status === "NO_COMMUNITY") {
      // Still mark the anonymous lead as NO_COMMUNITY in DB before redirecting
      window.location.href = WHOP_COMMUNITY_URL;
      return;
    }
    setFunnelTrack(status === "ACTIVE" ? "A" : "B");
    setStep(1);
  };

  if (isOAuthCallback) {
    return (
      <div className="relative min-h-screen bg-glow flex items-center justify-center p-6 text-center">
        <div className="max-w-md w-full rounded-2xl border border-whop-border bg-whop-surface p-8 shadow-2xl space-y-6">
          {callbackStatus === "loading" && (
            <>
              <div className="flex justify-center">
                <span className="animate-spin rounded-full h-12 w-12 border-4 border-whop-orange border-t-transparent" />
              </div>
              <h2 className="text-xl font-display font-semibold text-white">Connecting with Whop...</h2>
              <p className="text-sm text-whop-text">Please wait while we verify your community details.</p>
            </>
          )}

          {callbackStatus === "success" && (
            <>
              <div className="flex justify-center text-5xl">
                🎉
              </div>
              <h2 className="text-xl font-display font-semibold text-white">Connection Successful!</h2>
              <p className="text-sm text-whop-text">
                Your community details have been connected. Click the button below to return to the Whop App.
              </p>
              {callbackRedirectUrl ? (
                <a
                  href={callbackRedirectUrl}
                  className="block text-center w-full py-3.5 px-4 rounded-xl bg-whop-orange text-white font-semibold hover:bg-whop-orange-hover transition-colors"
                >
                  Return to Whop App
                </a>
              ) : (
                <button
                  onClick={() => {
                    try {
                      window.close();
                    } catch (e) {
                      console.error("Manual close failed:", e);
                    }
                  }}
                  className="w-full py-3.5 px-4 rounded-xl bg-whop-orange text-white font-semibold hover:bg-whop-orange-hover transition-colors"
                >
                  Close Window
                </button>
              )}
            </>
          )}

          {callbackStatus === "error" && (
            <>
              <div className="flex justify-center text-5xl text-red-500">
                ❌
              </div>
              <h2 className="text-xl font-display font-semibold text-white">Connection Failed</h2>
              <p className="text-sm text-whop-text">{error || "Something went wrong during authentication."}</p>
              <button
                onClick={() => {
                  try {
                    window.close();
                  } catch (e) {
                    console.error("Manual close failed:", e);
                  }
                }}
                className="w-full py-3.5 px-4 rounded-xl border border-whop-border bg-whop-surface text-white font-semibold hover:border-zinc-700 transition-colors"
              >
                Close Window
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  if (!started) {
    return (
      <Landing
        onStart={startOAuthFlow}
        spotsLeft={2}
        spotsTotal={10}
        error={error}
      />
    );
  }

  // Gate — shown after OAuth, before the funnel
  if (communityStatus === "UNSET") {
    return (
      <div className="relative min-h-screen bg-glow">
        <header className="relative z-10 flex items-center justify-between px-6 sm:px-10 pt-8">
          <div className="flex items-center gap-2 font-display font-semibold">
            <img src={logoAsset.url} alt="App Builders" className="h-8 w-8 rounded-md" />
            <span className="tracking-tight">App Builders</span>
          </div>
        </header>
        <main className="relative z-10 mx-auto flex min-h-[calc(100vh-80px)] max-w-2xl items-center px-6 py-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="w-full"
          >
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-whop-border bg-whop-surface px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-whop-text">
              <Sparkles className="h-3 w-3 text-whop-orange" />
              <span>Quick question first</span>
            </div>
            <h1 className="mt-4 font-display text-3xl sm:text-5xl font-semibold tracking-tight text-white">
              Do you have an active paid Whop community?
            </h1>
            <p className="mt-3 text-base sm:text-lg text-whop-text leading-relaxed">
              This helps us match you with the right build track.
            </p>
            <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Active */}
              <button
                onClick={() => selectCommunityStatus("ACTIVE")}
                className="group flex flex-col items-start gap-3 rounded-2xl border-2 border-whop-border bg-whop-surface p-6 text-left transition-all hover:border-whop-orange hover:bg-[#FF4F00]/5 hover:-translate-y-1"
              >
                <span className="text-2xl">✅</span>
                <div>
                  <div className="font-display font-semibold text-white">Yes, it's live</div>
                  <div className="mt-1 text-sm text-whop-text">I have paying members on Whop right now</div>
                </div>
              </button>
              {/* Pre-launch */}
              <button
                onClick={() => selectCommunityStatus("PRE_LAUNCH")}
                className="group flex flex-col items-start gap-3 rounded-2xl border-2 border-whop-border bg-whop-surface p-6 text-left transition-all hover:border-whop-orange hover:bg-[#FF4F00]/5 hover:-translate-y-1"
              >
                <span className="text-2xl">🚀</span>
                <div>
                  <div className="font-display font-semibold text-white">Not yet — I'm planning to launch</div>
                  <div className="mt-1 text-sm text-whop-text">I'm building toward launching on Whop</div>
                </div>
              </button>
              {/* No community */}
              <button
                onClick={() => selectCommunityStatus("NO_COMMUNITY")}
                className="group flex flex-col items-start gap-3 rounded-2xl border-2 border-whop-border bg-whop-surface p-6 text-left transition-all hover:border-zinc-600 hover:bg-zinc-900/50 hover:-translate-y-1"
              >
                <span className="text-2xl">👀</span>
                <div>
                  <div className="font-display font-semibold text-white">Just exploring</div>
                  <div className="mt-1 text-sm text-whop-text">I don't have a community yet</div>
                </div>
              </button>
            </div>
          </motion.div>
        </main>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-glow">
      <StepProgress step={step} total={TOTAL} />

      <header className="relative z-10 flex items-center justify-between px-6 sm:px-10 pt-8">
        <div className="flex items-center gap-2 font-display font-semibold">
          <img src={logoAsset.url} alt="App Builders" className="h-8 w-8 rounded-md" />
          <span className="tracking-tight">App Builders</span>
        </div>
        <div className="text-[11px] uppercase tracking-[0.25em] text-whop-mute">
          {funnelTrack === "B" ? "Pre-Launch Track" : "Custom Apps for Whop Creators"}
        </div>
      </header>

      <main className="relative z-10 mx-auto flex min-h-[calc(100vh-80px)] max-w-2xl items-center px-6 py-16">
        <div className="w-full">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-whop-border bg-whop-surface px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-whop-text">
            <Sparkles className="h-3 w-3 text-whop-orange" />
            <span>
              Step {step} / {TOTAL}
            </span>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              variants={stepVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.4, ease: "easeOut" }}
            >
              {/* ── FUNNEL B (Pre-Launch) ── */}
              {funnelTrack === "B" && step === 1 && (
                <Step
                  title="What kind of community are you building?"
                  subtitle="Pick the niche that best describes your vision."
                >
                  <SelectCards
                    options={NICHES}
                    value={form.niche}
                    onChange={(v) => update("niche", v)}
                    testIdPrefix="niche-card"
                    columns={2}
                  />
                </Step>
              )}

              {funnelTrack === "B" && step === 2 && (
                <Step
                  title="What kind of app do you have in mind?"
                  subtitle="Describe what you'd want your members to use. Skip if you'd rather we surprise you."
                >
                  <Field label="Your idea (optional)">
                    <textarea
                      value={form.ideal_app}
                      onChange={(e) => update("ideal_app", e.target.value)}
                      rows={5}
                      className="wop-input resize-none"
                      placeholder="e.g. A daily signals feed where members get trade alerts and track their P&L..."
                    />
                  </Field>
                  <div className="mt-6 rounded-xl border border-whop-border bg-whop-surface/60 p-4 flex items-start gap-3">
                    <span className="mt-0.5 text-lg">💡</span>
                    <p className="text-sm text-whop-text leading-relaxed">
                      <span className="text-white font-medium">Building your app is completely free.</span>{" "}
                      Once it's live, there's a small monthly hosting fee to keep it running. No contract — cancel anytime.
                    </p>
                  </div>
                </Step>
              )}

              {funnelTrack === "B" && step === 3 && (
                <Step
                  title="Are you willing to invest in hosting your app?"
                  subtitle="While designing & building your app is 100% free, running it live requires cloud hosting."
                >
                  <SelectCards
                    options={INVEST_OPTIONS}
                    value={form.willing_to_invest}
                    onChange={(v) => update("willing_to_invest", v)}
                    testIdPrefix="invest-card"
                    columns={2}
                  />
                </Step>
              )}

              {funnelTrack === "B" && step === 4 && (
                <Step
                  title="When are you planning to launch your community?"
                  subtitle="This sets your position in our pre-launch build queue."
                >
                  <SelectCards
                    options={[
                      { value: "Within 1 month", label: "Within 1 month", hint: "Ready to move fast" },
                      { value: "1–3 months", label: "1–3 months", hint: "Still preparing" },
                      { value: "3+ months", label: "3+ months out", hint: "Early planning stage" },
                    ]}
                    value={form.timeline}
                    onChange={(v) => update("timeline", v)}
                    testIdPrefix="timeline-card"
                    columns={3}
                  />
                </Step>
              )}

              {funnelTrack === "B" && step === 5 && (
                <Step
                  title="Where should we send your app concepts?"
                  subtitle="We'll design ideas around your niche and reach out directly when your app is ready."
                >
                  <div className="space-y-4">
                    <Field label="First name">
                      <input
                        autoFocus
                        value={form.first_name}
                        onChange={(e) => update("first_name", e.target.value)}
                        className="wop-input"
                        placeholder="Jordan"
                      />
                    </Field>
                    <Field label="Email">
                      <input
                        type="email"
                        value={form.email}
                        onChange={(e) => update("email", e.target.value)}
                        className="wop-input"
                        placeholder="jordan@example.com"
                      />
                    </Field>
                    <Field label="Preferred contact method">
                      <div className="flex gap-2 mt-1">
                        <button
                          type="button"
                          onClick={() => update("social_type", "discord")}
                          className={`flex-1 py-3 px-4 rounded-xl border text-center font-medium transition-all ${
                            form.social_type === "discord"
                              ? "border-whop-orange bg-[#FF4F00]/5 text-white"
                              : "border-whop-border bg-whop-surface text-whop-text hover:border-zinc-700"
                          }`}
                        >
                          Discord
                        </button>
                        <button
                          type="button"
                          onClick={() => update("social_type", "telegram")}
                          className={`flex-1 py-3 px-4 rounded-xl border text-center font-medium transition-all ${
                            form.social_type === "telegram"
                              ? "border-whop-orange bg-[#FF4F00]/5 text-white"
                              : "border-whop-border bg-whop-surface text-whop-text hover:border-zinc-700"
                          }`}
                        >
                          Telegram
                        </button>
                      </div>
                    </Field>
                    <Field label={form.social_type === "telegram" ? "Telegram username (optional)" : "Discord username (optional)"}>
                      <input
                        value={form.social_handle}
                        onChange={(e) => update("social_handle", e.target.value)}
                        className="wop-input"
                        placeholder={form.social_type === "telegram" ? "@jordan" : "jordan_dev"}
                      />
                    </Field>
                  </div>
                </Step>
              )}

              {/* ── FUNNEL A (Active Community) ── */}
              {funnelTrack === "A" && step === 1 && (
                <Step
                  title="Import your Whop community"
                  subtitle="We'll analyze your community's name and branding to automatically customize the color schemes, layout, and assets for your custom mobile app."
                >
                  {whopInputMode === "UNSET" && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <button
                          type="button"
                          disabled={oauthConnecting}
                          onClick={() => {
                            if (companies.length > 0) {
                              setWhopInputMode("AUTO");
                            } else {
                              connectWhopOauth();
                            }
                          }}
                          className="flex flex-col items-center justify-center p-6 rounded-2xl border border-whop-border bg-whop-surface/60 text-center transition-all hover:border-whop-orange hover:bg-whop-surface group disabled:opacity-50"
                        >
                          <Sparkles className="h-8 w-8 text-whop-orange mb-3 transition-transform group-hover:scale-110" />
                          <span className="font-semibold text-white text-base">Import Automatically</span>
                          <span className="text-xs text-whop-text mt-1.5 leading-relaxed">
                            Sign in with Whop to choose from your existing communities
                          </span>
                        </button>

                        <button
                          type="button"
                          onClick={() => setWhopInputMode("MANUAL")}
                          className="flex flex-col items-center justify-center p-6 rounded-2xl border border-whop-border bg-whop-surface/60 text-center transition-all hover:border-zinc-500 hover:bg-whop-surface group"
                        >
                          <Link2 className="h-8 w-8 text-whop-text mb-3 transition-transform group-hover:scale-110" />
                          <span className="font-semibold text-white text-base">Enter URL Manually</span>
                          <span className="text-xs text-whop-text mt-1.5 leading-relaxed">
                            Type or paste your Whop community store link manually
                          </span>
                        </button>
                      </div>
                      {oauthConnecting && (
                        <div className="flex items-center justify-center gap-2 text-sm text-whop-text mt-4">
                          <span className="animate-spin rounded-full h-4 w-4 border-2 border-whop-orange border-t-transparent" />
                          Waiting for Whop sign in...
                        </div>
                      )}
                    </div>
                  )}

                  {whopInputMode === "AUTO" && (
                    <div className="space-y-6">
                      {companies.length === 0 ? (
                        <div className="rounded-2xl border border-whop-border bg-whop-surface/60 p-6 text-center">
                          <p className="text-sm text-whop-text">
                            No owned or managed communities were found under this Whop account.
                          </p>
                          <button
                            type="button"
                            onClick={() => setWhopInputMode("MANUAL")}
                            className="mt-4 text-xs font-semibold text-whop-orange hover:underline"
                          >
                            Paste link manually instead
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <Field label="Select your community">
                            <select
                              value={companies.find(c => `https://whop.com/${c.route}` === form.whop_url || c.route === form.whop_url)?.route || ""}
                              onChange={(e) => {
                                const route = e.target.value;
                                update("whop_url", route ? `https://whop.com/${route}` : "");
                              }}
                              className="w-full rounded-xl border border-whop-border bg-whop-surface p-4 text-white font-medium focus:border-whop-orange focus:outline-none"
                            >
                              <option value="">-- Choose a community --</option>
                              {companies.map((c) => (
                                <option key={c.id} value={c.route}>
                                  {c.title} (whop.com/{c.route})
                                </option>
                              ))}
                            </select>
                          </Field>

                          <div className="flex justify-between items-center mt-6">
                            <button
                              type="button"
                              onClick={() => {
                                connectWhopOauth();
                              }}
                              className="text-xs text-whop-mute hover:text-white transition-colors"
                            >
                              Sync/Refresh accounts
                            </button>
                            <button
                              type="button"
                              onClick={() => setWhopInputMode("MANUAL")}
                              className="text-xs text-whop-orange hover:underline"
                            >
                              Use manual URL entry
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {whopInputMode === "MANUAL" && (
                    <div className="space-y-6">
                      <div className="relative">
                        <Link2 className="absolute left-0 top-1/2 h-5 w-5 -translate-y-1/2 text-whop-mute" />
                        <input
                          autoFocus
                          type="url"
                          placeholder="https://whop.com/your-community"
                          value={form.whop_url}
                          onChange={(e) => update("whop_url", e.target.value)}
                          className="w-full rounded-none border-0 border-b-2 border-whop-border bg-transparent py-4 pl-8 pr-10 font-display text-xl sm:text-2xl text-white placeholder-zinc-700 focus:border-whop-orange focus:outline-none transition-colors"
                        />
                        {urlValid && (
                          <CheckCircle2 className="absolute right-1 top-1/2 h-6 w-6 -translate-y-1/2 text-green-500 drop-shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                        )}
                      </div>

                      <div className="flex justify-end mt-4">
                        <button
                          type="button"
                          onClick={() => {
                            if (companies.length > 0) {
                              setWhopInputMode("AUTO");
                            } else {
                              setWhopInputMode("UNSET");
                            }
                          }}
                          className="text-xs text-whop-orange hover:underline"
                        >
                          Use automatic connection
                        </button>
                      </div>
                    </div>
                  )}
                </Step>
              )}

              {funnelTrack === "A" && step === 2 && (
                <Step title="What's your community about?" subtitle="Pick the niche that best describes your members.">
                  <SelectCards
                    options={NICHES}
                    value={form.niche}
                    onChange={(v) => update("niche", v)}
                    testIdPrefix="niche-card"
                    columns={2}
                  />
                </Step>
              )}

              {funnelTrack === "A" && step === 3 && (
                <Step
                  title="How many active paying members do you have?"
                  subtitle="A rough estimate is fine — we'll use this to size your app."
                >
                  <div className="rounded-2xl border border-whop-border bg-whop-surface p-8">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-2 text-xs uppercase tracking-[0.2em] text-whop-mute">
                        <Users className="h-3.5 w-3.5 text-whop-orange" />
                        Active Members
                      </div>
                      <div className="mt-2 font-display text-6xl sm:text-7xl font-semibold text-white tracking-tight">
                        {form.member_count.toLocaleString()}
                        {form.member_count >= 1000 && <span className="text-whop-orange">+</span>}
                      </div>
                    </div>
                    <div className="mt-8 px-1">
                      <input
                        type="range"
                        min={10}
                        max={1000}
                        step={10}
                        value={form.member_count}
                        onChange={(e) => update("member_count", Number(e.target.value))}
                        className="wop-slider"
                        style={
                          { ["--val" as string]: `${((form.member_count - 10) / 990) * 100}%` } as React.CSSProperties
                        }
                      />
                      <div className="mt-3 flex justify-between text-xs text-whop-mute">
                        <span>10</span>
                        <span>1,000+</span>
                      </div>
                    </div>
                  </div>
                </Step>
              )}

              {funnelTrack === "A" && step === 4 && (
                <Step title="What's the average monthly price per member?" subtitle="Just the typical subscription.">
                  <div className="rounded-2xl border border-whop-border bg-whop-surface p-8">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-2 text-xs uppercase tracking-[0.2em] text-whop-mute">
                        <DollarSign className="h-3.5 w-3.5 text-whop-orange" />
                        Monthly Price / Member
                      </div>
                      <div className="mt-2 font-display text-6xl sm:text-7xl font-semibold text-white tracking-tight">
                        ${form.monthly_price}
                        {form.monthly_price >= 100 && <span className="text-whop-orange">+</span>}
                        <span className="text-3xl sm:text-4xl text-whop-mute font-medium">/mo</span>
                      </div>
                    </div>
                    <div className="mt-8 px-1">
                      <input
                        type="range"
                        min={5}
                        max={100}
                        step={5}
                        value={form.monthly_price}
                        onChange={(e) => update("monthly_price", Number(e.target.value))}
                        className="wop-slider"
                        style={
                          { ["--val" as string]: `${((form.monthly_price - 5) / 95) * 100}%` } as React.CSSProperties
                        }
                      />
                      <div className="mt-3 flex justify-between text-xs text-whop-mute">
                        <span>$5</span>
                        <span>$100+</span>
                      </div>
                    </div>
                  </div>
                </Step>
              )}

              {funnelTrack === "A" && step === 5 && (
                <Step
                  title="Here's what churn is costing you."
                  subtitle="A quick estimate, based on what you just told us."
                >
                  <div className="space-y-4">
                    <div className="rounded-2xl border border-whop-orange/40 bg-gradient-to-br from-[#FF4F00]/15 via-[#FF4F00]/5 to-transparent p-8 shadow-[0_0_32px_rgba(255,79,0,0.18)]">
                      <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.2em] text-whop-orange font-bold">
                        <Sparkles className="h-3.5 w-3.5" />
                        You&apos;re losing roughly
                      </div>
                      <div className="mt-3 font-display text-5xl sm:text-7xl font-bold tracking-tight text-white">
                        ${annualLoss.toLocaleString()}
                        <span className="text-whop-text text-2xl sm:text-3xl font-medium"> / year</span>
                      </div>
                      <p className="mt-3 text-base text-whop-text leading-relaxed">
                        That&apos;s revenue walking out the door every month because members cancel before they get
                        hooked. Roughly{" "}
                        <span className="text-white font-semibold">${monthlyLoss.toLocaleString()}/mo</span> leaving
                        your community.
                      </p>
                    </div>
                    <div className="rounded-2xl border border-whop-border bg-whop-surface p-6">
                      <div className="flex items-start gap-3">
                        <span className="mt-0.5 inline-flex h-8 w-8 items-center justify-center rounded-full bg-[#FF4F00]/15 text-whop-orange flex-shrink-0">
                          <Gift className="h-4 w-4" />
                        </span>
                        <div>
                          <div className="font-display text-base font-medium text-white">
                            We build the first version for you, free.
                          </div>
                          <div className="mt-1 text-sm text-whop-text leading-relaxed">
                            Custom-designed for your community. No contract, no upfront commitment.
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Step>
              )}

              {funnelTrack === "A" && step === 6 && (
                <Step
                  title="Have an idea? Describe your ideal version."
                  subtitle="Skip this if you'd rather we surprise you with options."
                >
                  <Field label="Your idea (optional)">
                    <textarea
                      value={form.ideal_app}
                      onChange={(e) => update("ideal_app", e.target.value)}
                      rows={6}
                      className="wop-input resize-none"
                      placeholder="e.g. A weekly leaderboard showing top traders so members can compete and learn from each other..."
                    />
                  </Field>
                  <div className="mt-3 text-xs text-whop-mute leading-relaxed">
                    The more specific, the better we can tailor one of the three concepts to YOUR idea.
                  </div>
                </Step>
              )}

              {funnelTrack === "A" && step === 7 && (
                <Step title="When are you looking to launch?" subtitle="Sets your priority in our build queue.">
                  <SelectCards
                    options={TIMELINES}
                    value={form.timeline}
                    onChange={(v) => update("timeline", v)}
                    testIdPrefix="timeline-card"
                    columns={3}
                  />
                </Step>
              )}

              {funnelTrack === "A" && step === 8 && (
                <Step
                  title="Where should we send your blueprint?"
                  subtitle="We'll generate your custom concepts in the next 30 seconds."
                >
                  <div className="space-y-4">
                    <Field label="First name">
                      <input
                        autoFocus
                        value={form.first_name}
                        onChange={(e) => update("first_name", e.target.value)}
                        className="wop-input"
                        placeholder="Jordan"
                      />
                    </Field>
                    <Field label="Business email">
                      <input
                        type="email"
                        value={form.email}
                        onChange={(e) => update("email", e.target.value)}
                        className="wop-input"
                        placeholder="jordan@yourcommunity.com"
                      />
                    </Field>
                    <Field label="Preferred contact method">
                      <div className="flex gap-2 mt-1">
                        <button
                          type="button"
                          onClick={() => update("social_type", "discord")}
                          className={`flex-1 py-3 px-4 rounded-xl border text-center font-medium transition-all ${
                            form.social_type === "discord"
                              ? "border-whop-orange bg-[#FF4F00]/5 text-white"
                              : "border-whop-border bg-whop-surface text-whop-text hover:border-zinc-700"
                          }`}
                        >
                          Discord
                        </button>
                        <button
                          type="button"
                          onClick={() => update("social_type", "telegram")}
                          className={`flex-1 py-3 px-4 rounded-xl border text-center font-medium transition-all ${
                            form.social_type === "telegram"
                              ? "border-whop-orange bg-[#FF4F00]/5 text-white"
                              : "border-whop-border bg-whop-surface text-whop-text hover:border-zinc-700"
                          }`}
                        >
                          Telegram
                        </button>
                      </div>
                    </Field>
                    <Field label={form.social_type === "telegram" ? "Telegram username (optional)" : "Discord username (optional)"}>
                      <input
                        value={form.social_handle}
                        onChange={(e) => update("social_handle", e.target.value)}
                        className="wop-input"
                        placeholder={form.social_type === "telegram" ? "@jordan" : "jordan_dev"}
                      />
                    </Field>
                  </div>
                </Step>
              )}
            </motion.div>
          </AnimatePresence>

          {error && <div className="mt-4 text-sm text-red-400">{error}</div>}

          <div className="mt-10 flex items-center justify-between">
            <button
              onClick={back}
              disabled={step === 1}
              className="inline-flex items-center gap-2 rounded-xl border border-whop-border bg-whop-surface px-5 py-3 text-sm text-white transition-all hover:border-zinc-500 disabled:cursor-not-allowed disabled:opacity-30"
            >
              <ArrowLeft className="h-4 w-4" /> Back
            </button>
            <button
              onClick={next}
              disabled={!canAdvance}
              className="group inline-flex items-center gap-2 rounded-xl bg-whop-orange px-7 py-3.5 font-display font-semibold text-white transition-all hover:bg-whop-orangeDark hover:shadow-[0_0_28px_rgba(255,79,0,0.45)] hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0 disabled:hover:shadow-none"
            >
              {step === TOTAL ? (funnelTrack === "B" ? "Get My Pre-Launch Blueprint" : "Get My Free MVP Blueprint") : step === 5 && funnelTrack === "A" ? "Continue" : "Next"}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>
      </main>

      {loading && <LoadingScreen />}
    </div>
  );
}

function Step({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div>
      <h1 className="font-display text-3xl sm:text-5xl font-semibold tracking-tight text-white">{title}</h1>
      {subtitle && <p className="mt-3 text-base sm:text-lg text-whop-text leading-relaxed">{subtitle}</p>}
      <div className="mt-10">{children}</div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-2 block text-[11px] uppercase tracking-[0.2em] text-whop-mute">{label}</span>
      {children}
    </label>
  );
}

function Landing({
  onStart,
  spotsLeft,
  spotsTotal,
  error,
}: {
  onStart: () => void;
  spotsLeft: number;
  spotsTotal: number;
  error?: string | null;
}) {
  const taken = spotsTotal - spotsLeft;
  const pct = (taken / spotsTotal) * 100;
  return (
    <div className="relative min-h-screen bg-glow overflow-hidden">
      <header className="relative z-10 flex items-center justify-between px-6 sm:px-10 pt-8">
        <div className="flex items-center gap-2 font-display font-semibold">
          <img src={logoAsset.url} alt="App Builders" className="h-8 w-8 rounded-md" />
          <span className="tracking-tight">App Builders</span>
        </div>
        <div className="text-[11px] uppercase tracking-[0.25em] text-whop-mute hidden sm:block">
          Custom Apps for Whop Creators
        </div>
      </header>

      <main className="relative z-10 mx-auto flex min-h-[calc(100vh-80px)] max-w-3xl flex-col items-center justify-center px-6 py-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 rounded-full border border-whop-orange/40 bg-whop-orange/10 px-4 py-1.5 text-[11px] uppercase tracking-[0.25em] text-whop-orange"
        >
          <Sparkles className="h-3 w-3" />
          Free MVP Program · Limited Spots
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mt-6 font-display text-4xl sm:text-6xl font-semibold tracking-tight text-white"
        >
          Get <span className="text-whop-orange">FREE</span> custom app for your Whop community
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-5 max-w-xl text-base sm:text-lg text-whop-text leading-relaxed"
        >
          Tell us about your community in 60 seconds. We'll design 3 custom app concepts and build the first version of
          your favorite — at no cost. No contract, no catch.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 w-full max-w-md rounded-2xl border border-whop-border bg-whop-surface p-5"
        >
          <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em]">
            <div className="flex items-center gap-2 text-whop-mute">
              <span className="relative flex h-2.5 w-2.5">
                <motion.span
                  className="absolute inline-flex h-full w-full rounded-full bg-whop-orange opacity-75"
                  animate={{ scale: [1, 2.2, 1], opacity: [0.75, 0, 0.75] }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: "easeOut" }}
                />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-whop-orange" />
              </span>
              Live
            </div>
            <div className="text-white font-semibold">
              <span className="text-whop-orange">{spotsLeft}</span>
              <span className="text-whop-mute"> / {spotsTotal} spots left</span>
            </div>
          </div>
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-[#27272A]">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 1.2, ease: "easeOut", delay: 0.4 }}
              className="h-full rounded-full bg-gradient-to-r from-[#00F2FE] to-[#FF4F00]"
              style={{ boxShadow: "0 0 12px rgba(255,79,0,0.5)" }}
            />
          </div>
          <div className="mt-3 text-[11px] text-whop-mute">
            {taken} creators already claimed this month's build queue.
          </div>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          onClick={onStart}
          className="group mt-10 inline-flex items-center gap-2 rounded-xl bg-whop-orange px-8 py-4 font-display font-semibold text-white transition-all hover:bg-whop-orangeDark hover:shadow-[0_0_32px_rgba(255,79,0,0.5)] hover:-translate-y-0.5"
        >
          Apply for a Free Build
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </motion.button>

        <div className="mt-4 text-xs text-whop-mute">Takes ~60 seconds · No credit card </div>

        {error && (
          <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}
      </main>
    </div>
  );
}
