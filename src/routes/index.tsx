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
import { createLead, getOAuthUrl, exchangeOAuthCode, handleIframeToken, completeLead, registerAnonymousLead } from "@/lib/leads.functions";
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

const TOTAL = 8;

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

const stepVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export function Onboarding() {
  const navigate = useNavigate();
  const [started, setStarted] = useState(false);
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
  });

  // Detect if running inside Whop iframe (proxied subdomain)
  const isInsideWhop = typeof window !== "undefined" &&
    (window.location.hostname.endsWith(".apps.whop.com") ||
     window.location.pathname.startsWith("/experiences/") ||
     window !== window.top);

  useEffect(() => {
    const handleAuth = async () => {
      if (typeof window === "undefined") return;
      
      const searchParams = new URLSearchParams(window.location.search);
      const code = searchParams.get("code");
      // Whop injects the user token via query params when embedded
      const whopUserToken = searchParams.get("whop-user-token") || searchParams.get("whop-dev-user-token");
      
      if (code) {
        setLoading(true);
        try {
          const verifier = sessionStorage.getItem("whop_verifier") || "";
          const res = await exchangeOAuthCode({
            data: {
              code,
              codeVerifier: verifier,
              // Always use the canonical Vercel origin for OAuth redirect
              origin: "https://free-app-flow.vercel.app",
            }
          });
          
          setLeadId(res.leadId);
          sessionStorage.setItem("lead_id", res.leadId);
          
          setForm((f) => ({
            ...f,
            first_name: res.name,
            email: res.email,
          }));
          setStarted(true);
          
          window.history.replaceState({}, document.title, window.location.pathname);
        } catch (e) {
          console.error("OAuth exchange failed:", e);
          setError("Whop authentication failed. Please try again.");
        } finally {
          setLoading(false);
        }
      } else if (whopUserToken) {
        setLoading(true);
        try {
          const res = await handleIframeToken({ data: { token: whopUserToken } });
          setLeadId(res.leadId);
          sessionStorage.setItem("lead_id", res.leadId);
          setForm((f) => ({
            ...f,
            first_name: res.name,
            email: res.email,
          }));
          // Auto-start funnel when inside Whop iframe with a valid token
          setStarted(true);
          
          window.history.replaceState({}, document.title, window.location.pathname);
        } catch (e) {
          console.error("Iframe token handler failed:", e);
        } finally {
          setLoading(false);
        }
      } else if (isInsideWhop && !leadId) {
        // Auto-register inside iframe on page load
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
  }, [isInsideWhop, leadId]);

  const update = <K extends keyof typeof form>(key: K, val: (typeof form)[K]) => setForm((f) => ({ ...f, [key]: val }));

  const mrr = useMemo(
    () => Math.max(0, form.member_count) * Math.max(0, form.monthly_price),
    [form.member_count, form.monthly_price],
  );
  const annualLoss = useMemo(() => Math.round(mrr * 3), [mrr]);
  const monthlyLoss = useMemo(() => Math.round(mrr * 0.25), [mrr]);

  const urlValid = useMemo(() => /whop\.com/i.test(form.whop_url), [form.whop_url]);
  const emailValid = useMemo(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email), [form.email]);

  const canAdvance = (() => {
    switch (step) {
      case 1:
        return urlValid;
      case 2:
        return !!form.niche;
      case 3:
        return form.member_count > 0;
      case 4:
        return form.monthly_price > 0;
      case 5:
        return true;
      case 6:
        return true;
      case 7:
        return !!form.timeline;
      case 8:
        return !!form.first_name && emailValid;
      default:
        return true;
    }
  })();

  const startOAuthFlow = async () => {
    // If inside Whop iframe, OAuth redirect is blocked — go directly to the funnel
    // Immediately register an anonymous lead so it shows in admin right away
    if (isInsideWhop) {
      setError(null);
      if (leadId) {
        setStarted(true);
        return;
      }
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

  const submit = async () => {
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

  const next = () => {
    if (!canAdvance) return;
    if (step < TOTAL) setStep((s) => s + 1);
    else void submit();
  };
  const back = () => step > 1 && setStep((s) => s - 1);

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

  return (
    <div className="relative min-h-screen bg-glow">
      <StepProgress step={step} total={TOTAL} />

      <header className="relative z-10 flex items-center justify-between px-6 sm:px-10 pt-8">
        <div className="flex items-center gap-2 font-display font-semibold">
          <img src={logoAsset.url} alt="App Builders" className="h-8 w-8 rounded-md" />
          <span className="tracking-tight">App Builders</span>
        </div>
        <div className="text-[11px] uppercase tracking-[0.25em] text-whop-mute">Custom Apps for Whop Creators</div>
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
              {step === 1 && (
                <Step
                  title="Paste your Whop community link."
                  subtitle="We'll analyze it and design a custom retention app for you — built free."
                >
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
                </Step>
              )}

              {step === 2 && (
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

              {step === 3 && (
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

              {step === 4 && (
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

              {step === 5 && (
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

              {step === 6 && (
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

              {step === 7 && (
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

              {step === 8 && (
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
                    <Field label="Discord or Telegram (optional)">
                      <input
                        value={form.social_handle}
                        onChange={(e) => update("social_handle", e.target.value)}
                        className="wop-input"
                        placeholder="@jordan"
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
              {step === TOTAL ? "Get My Free MVP Blueprint" : step === 5 ? "Continue" : "Next"}
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
