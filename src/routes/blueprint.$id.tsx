import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles, CheckCircle2, ArrowRight, Zap, Lock, Loader2, Flame, Clock, Mail, Hourglass,
} from "lucide-react";
import { getLead, getPublicConfig, claimConcept, setLeadAction, type Lead, type PublicConfig } from "@/lib/leads.functions";
import logoAsset from "@/assets/app-builders-logo.png.asset.json";

export const Route = createFileRoute("/blueprint/$id")({
  head: () => ({
    meta: [
      { title: "Your Custom App Blueprint — App Builders" },
      { name: "description", content: "Pick the retention app concept we build for you, free." },
    ],
  }),
  component: BlueprintPage,
  errorComponent: ({ error }) => (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="text-center">
        <div className="text-whop-text">{error.message || "We couldn't find this blueprint."}</div>
        <Link to="/" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-whop-orange px-6 py-3 font-medium text-white">
          Start Over <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  ),
  notFoundComponent: () => (
    <div className="min-h-screen flex items-center justify-center text-whop-text">Blueprint not found.</div>
  ),
});

const STAGE = {
  IDLE: "idle",
  CHECKING_SPOT: "checking-spot",
  SPOT_FOUND: "spot-found",
  CHECKING_QUEUE: "checking-queue",
  QUEUE_RESULT: "queue-result",
  WAIT_CONFIRMED: "wait-confirmed",
  SKIP_REDIRECTING: "skip-redirecting",
} as const;
type Stage = (typeof STAGE)[keyof typeof STAGE];

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

type Concept = { name: string; tagline?: string; benefits?: string[]; fits_because?: string };

function extractConcepts(plan: Lead["ai_plan"]): { concepts: Concept[]; valueAdd?: string } {
  if (plan && typeof plan === "object" && !Array.isArray(plan)) {
    const p = plan as Record<string, unknown>;
    const concepts = Array.isArray(p.concepts) ? (p.concepts as Concept[]) : [];
    const valueAdd = typeof p.estimated_value_add === "string" ? p.estimated_value_add : undefined;
    return { concepts, valueAdd };
  }
  return { concepts: [] };
}

function BlueprintPage() {
  const { id } = Route.useParams();
  const [lead, setLead] = useState<Lead | null>(null);
  const [cfg, setCfg] = useState<PublicConfig>({
    calendly_url: "", whop_paid_product_url: "",
    free_spots_left: 2, free_spots_total: 10, free_wait_weeks: 4,
  });
  const [err, setErr] = useState("");
  const [claimedIndex, setClaimedIndex] = useState<number | null>(null);
  const [stage, setStage] = useState<Stage>(STAGE.IDLE);
  

  useEffect(() => {
    (async () => {
      try {
        const [l, c] = await Promise.all([getLead({ data: { id } }), getPublicConfig()]);
        setLead(l);
        setCfg(c);
        if (typeof l.selected_concept_index === "number") {
          setClaimedIndex(l.selected_concept_index);
          if (l.claim_action === "wait") setStage(STAGE.WAIT_CONFIRMED);
          else setStage(STAGE.QUEUE_RESULT);
        }
      } catch {
        setErr("We couldn't find this blueprint. Try submitting again.");
      }
    })();
  }, [id]);

  const { concepts, valueAdd } = useMemo(() => extractConcepts(lead?.ai_plan ?? null), [lead]);

  const handleClaim = async (idx: number) => {
    if (claimedIndex !== null) return;
    setClaimedIndex(idx);
    setStage(STAGE.CHECKING_SPOT);
    try {
      await claimConcept({ data: { id, concept_index: idx } });
      console.log("[claimConcept] saved", { id, concept_index: idx, name: concepts[idx]?.name });
    } catch (e) {
      console.error("[claimConcept] failed:", e);
    }
    await sleep(3200);
    setStage(STAGE.SPOT_FOUND);
    await sleep(2200);
    setStage(STAGE.CHECKING_QUEUE);
    await sleep(3200);
    setStage(STAGE.QUEUE_RESULT);
  };

  const handleWait = async () => {
    setStage(STAGE.WAIT_CONFIRMED);
    setLeadAction({ data: { id, action: "wait" } }).catch(console.error);
  };
  const handleSkip = () => {
    const url = cfg.whop_paid_product_url;
    // Open synchronously inside click handler so popup blockers allow it.
    if (url) window.open(url, "_blank", "noopener,noreferrer");
    setLeadAction({ data: { id, action: "skip" } }).catch(console.error);
    // Keep the user on the current view — no redirect, no stage change.
  };

  const closeModal = () => {
    if (
      stage === STAGE.WAIT_CONFIRMED ||
      stage === STAGE.QUEUE_RESULT ||
      stage === STAGE.SKIP_REDIRECTING
    ) {
      setStage(STAGE.IDLE);
    }
  };

  if (err) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center">
          <div className="text-whop-text">{err}</div>
          <Link to="/" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-whop-orange px-6 py-3 font-medium text-white">
            Start Over <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    );
  }
  if (!lead) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-10 w-10 rounded-full border-2 border-whop-border border-t-whop-orange animate-spin" />
      </div>
    );
  }

  const modalOpen = stage !== STAGE.IDLE;

  return (
    <div className="relative min-h-screen bg-glow">
      <header className="relative z-10 flex items-center justify-between px-6 sm:px-10 pt-8">
        <Link to="/" className="flex items-center gap-2 font-display font-semibold">
          <img src={logoAsset.url} alt="App Builders" className="h-8 w-8 rounded-md" />
          <span>App Builders</span>
        </Link>
        <div className="inline-flex items-center gap-2 rounded-full border border-whop-orange/30 bg-[#FF4F00]/10 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-whop-orange font-bold">
          <Flame className="h-3 w-3" /> {cfg.free_spots_left} / {cfg.free_spots_total} free spots left
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-3xl px-6 py-12">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-whop-border bg-whop-surface px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-whop-text">
            <Sparkles className="h-3 w-3 text-whop-orange" /> Your Custom Blueprint
          </div>
          <h1 className="font-display text-3xl sm:text-5xl font-semibold tracking-tight text-white">
            Pick the version we build for you, {lead.first_name}.
          </h1>
          <p className="mt-3 text-base sm:text-lg text-whop-text max-w-2xl leading-relaxed">
            Three custom options tailored to your <span className="text-white">{lead.niche}</span> community. Pick one — we build it for you, free.
          </p>

          {valueAdd && (
            <div className="mt-5 rounded-xl border border-whop-orange/30 bg-[#FF4F00]/5 px-4 py-3 text-sm text-white">
              <span className="text-whop-orange font-semibold uppercase tracking-[0.15em] text-[10px] mr-2">Why it matters</span>
              {valueAdd}
            </div>
          )}

          <div className="mt-8 space-y-4">
            {concepts.map((c, i) => (
              <ConceptCard key={i} index={i} concept={c} claimedIndex={claimedIndex} onClaim={handleClaim} />
            ))}
            {concepts.length === 0 && (
              <div className="rounded-xl border border-whop-border bg-whop-surface p-6 text-whop-text">
                We&apos;re still preparing your concepts. Refresh in a moment.
              </div>
            )}
          </div>
        </motion.div>
      </main>

      <AnimatePresence>
        {modalOpen && (
          <motion.div
            key="overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4"
            onClick={closeModal}
          >
            <motion.div
              key="modal"
              initial={{ opacity: 0, scale: 0.94, y: 16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.94, y: 16 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-xl"
            >
              <ClaimReveal stage={stage} cfg={cfg} lead={lead} concepts={concepts} claimedIndex={claimedIndex} onWait={handleWait} onSkip={handleSkip} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ClaimReveal({ stage, cfg, lead, concepts, claimedIndex, onWait, onSkip }: {
  stage: Stage; cfg: PublicConfig; lead: Lead; concepts: Concept[]; claimedIndex: number | null;
  onWait: () => void; onSkip: () => void;
}) {
  const conceptName = (claimedIndex !== null ? concepts[claimedIndex]?.name : "") || "your concept";
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className="relative overflow-hidden rounded-3xl border border-whop-orange/40 bg-gradient-to-br from-[#FF4F00]/10 via-whop-surface to-whop-surface p-8 sm:p-12 shadow-[0_0_60px_rgba(255,79,0,0.18)]"
    >
      <div className="pointer-events-none absolute inset-0 bg-glow opacity-60" />
      <div className="relative">
        <AnimatePresence mode="wait">
          {stage === STAGE.CHECKING_SPOT && (
            <Stage key="s1"><LoadingPulse /><StageTitle>Checking for a free spot…</StageTitle><StageSub>Looking for an open build slot for <Bold>{conceptName}</Bold></StageSub></Stage>
          )}
          {stage === STAGE.SPOT_FOUND && (
            <Stage key="s2"><SuccessPulse /><StageTitle>Free spot is here — and still available.</StageTitle><StageSub>We can build <Bold>{conceptName}</Bold> for you.</StageSub></Stage>
          )}
          {stage === STAGE.CHECKING_QUEUE && (
            <Stage key="s3"><LoadingPulse /><StageTitle>Checking the current queue…</StageTitle><StageSub>Estimating when we can start your build.</StageSub></Stage>
          )}
          {stage === STAGE.QUEUE_RESULT && (
            <motion.div key="s4" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} transition={{ duration: 0.4 }}>
              <div className="flex items-center justify-center gap-2 text-[11px] uppercase tracking-[0.25em] text-whop-orange font-bold">
                <Clock className="h-3.5 w-3.5" /> Current Build Queue
              </div>
              <div className="mt-4 text-center font-display text-5xl sm:text-7xl font-bold tracking-tight text-white">
                ~{cfg.free_wait_weeks} weeks
              </div>
              <div className="mt-2 text-center text-whop-text">until your free build can start.</div>

              <div className="mt-8 grid gap-3 sm:grid-cols-2">
                <button
                  onClick={onWait}
                  className="group flex items-center justify-center gap-2 rounded-xl border border-whop-border bg-whop-surface px-5 py-4 font-display text-white transition-all hover:border-zinc-500"
                >
                  <Hourglass className="h-4 w-4 text-whop-cyan" />
                  I'll wait — keep my free spot
                </button>
                <button
                  onClick={onSkip}
                  className="group flex items-center justify-center gap-2 rounded-xl bg-whop-orange px-5 py-4 font-display font-semibold text-white transition-all hover:bg-whop-orangeDark hover:shadow-[0_0_28px_rgba(255,79,0,0.45)] hover:-translate-y-0.5"
                >
                  <Zap className="h-4 w-4" /> Skip the line <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </button>
              </div>
              <div className="mt-5 text-center text-xs text-whop-mute">Skip the line and we start building this week.</div>
            </motion.div>
          )}
          {stage === STAGE.WAIT_CONFIRMED && (
            <Stage key="s5">
              <SuccessPulse />
              <StageTitle>Got it — you&apos;re on the list.</StageTitle>
              <StageSub>We&apos;ll message <Bold>{lead.email}</Bold> the moment your build slot opens up. No further action needed from you.</StageSub>
              <div className="mt-6 inline-flex items-center gap-2 rounded-full border border-whop-border bg-[#0F0F11]/60 px-4 py-2 text-xs text-whop-text">
                <Mail className="h-3.5 w-3.5 text-whop-cyan" /> Watch your inbox for our update.
              </div>
              <a
                href="https://whop.com/joined/app-builders-f882/products/app-builders-community/"
                target="_blank"
                rel="noopener noreferrer"
                className="group mt-6 inline-flex items-center gap-2 rounded-xl bg-whop-orange px-5 py-3 font-display font-semibold text-white transition-all hover:bg-whop-orangeDark hover:shadow-[0_0_28px_rgba(255,79,0,0.45)] hover:-translate-y-0.5"
              >
                Join our free community while you wait
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </a>
            </Stage>
          )}
          {stage === STAGE.SKIP_REDIRECTING && (
            <Stage key="s6"><LoadingPulse /><StageTitle>Setting up your priority access…</StageTitle><StageSub>Taking you to your fast-track product now.</StageSub></Stage>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

function Stage({ children }: { children: ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} transition={{ duration: 0.4 }} className="flex flex-col items-center text-center">
      {children}
    </motion.div>
  );
}
function StageTitle({ children }: { children: ReactNode }) {
  return <div className="mt-6 font-display text-2xl sm:text-3xl font-semibold tracking-tight text-white">{children}</div>;
}
function StageSub({ children }: { children: ReactNode }) {
  return <div className="mt-2 max-w-md text-whop-text leading-relaxed">{children}</div>;
}
function Bold({ children }: { children: ReactNode }) {
  return <span className="text-white font-semibold">{children}</span>;
}
function LoadingPulse() {
  return (
    <div className="relative">
      <div className="absolute inset-0 rounded-full bg-[#FF4F00]/30 blur-2xl animate-pulse-glow" />
      <div className="relative h-14 w-14 rounded-full border-2 border-whop-border border-t-whop-orange animate-spin" />
    </div>
  );
}
function SuccessPulse() {
  return (
    <div className="relative">
      <div className="absolute inset-0 rounded-full bg-green-500/30 blur-2xl" />
      <div className="relative h-14 w-14 rounded-full border-2 border-green-500/40 bg-green-500/10 flex items-center justify-center">
        <CheckCircle2 className="h-7 w-7 text-green-400" strokeWidth={2.5} />
      </div>
    </div>
  );
}

function ConceptCard({ index, concept, claimedIndex, onClaim }: {
  index: number; concept: Concept; claimedIndex: number | null; onClaim: (i: number) => void;
}) {
  const isClaimed = claimedIndex === index;
  const isOtherClaimed = claimedIndex !== null && claimedIndex !== index;
  return (
    <motion.div
      whileHover={!isOtherClaimed && claimedIndex === null ? { y: -2 } : {}}
      transition={{ duration: 0.2 }}
      className={`relative rounded-2xl border p-6 transition-all ${
        isClaimed
          ? "border-whop-orange bg-[#FF4F00]/10 shadow-[0_0_24px_rgba(255,79,0,0.25)]"
          : isOtherClaimed
            ? "border-whop-border bg-whop-surface opacity-40"
            : "border-whop-border bg-whop-surface hover:border-[#FF4F00]/40"
      }`}
    >
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="inline-flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-whop-mute">
          <span className={`inline-flex h-5 w-5 items-center justify-center rounded-md font-bold text-[10px] ${
            isClaimed ? "bg-whop-orange text-white" : "bg-whop-bg border border-whop-border text-whop-orange"
          }`}>
            {String.fromCharCode(65 + index)}
          </span>
          Option {String.fromCharCode(65 + index)}
        </div>
        {isClaimed && (
          <div className="inline-flex items-center gap-1 rounded-full border border-green-500/30 bg-green-500/10 px-2.5 py-0.5 text-[10px] uppercase tracking-[0.2em] text-green-400 font-bold">
            <CheckCircle2 className="h-3 w-3" /> Reserved
          </div>
        )}
      </div>

      <h3 className="font-display text-xl sm:text-2xl font-semibold tracking-tight text-white">{concept.name}</h3>
      {concept.tagline && <p className="mt-1 text-sm text-whop-text leading-relaxed">{concept.tagline}</p>}

      {Array.isArray(concept.benefits) && concept.benefits.length > 0 && (
        <ul className="mt-4 space-y-2">
          {concept.benefits.slice(0, 3).map((b, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-white/90">
              <CheckCircle2 className="h-4 w-4 text-whop-orange mt-0.5 flex-shrink-0" />
              <span>{b}</span>
            </li>
          ))}
        </ul>
      )}

      {concept.fits_because && (
        <div className="mt-4 rounded-lg border border-whop-border bg-[#0F0F11]/50 px-3 py-2 text-xs text-whop-text leading-relaxed">
          <span className="text-whop-orange font-semibold uppercase tracking-[0.15em] mr-1">Why this fits ·</span>
          {concept.fits_because}
        </div>
      )}

      <div className="mt-5">
        <button
          onClick={() => onClaim(index)}
          disabled={claimedIndex !== null}
          className={`group inline-flex items-center gap-2 rounded-xl px-5 py-2.5 font-display text-sm font-semibold transition-all ${
            isClaimed
              ? "bg-green-500/20 text-green-400 border border-green-500/40 cursor-default"
              : isOtherClaimed
                ? "bg-whop-surface border border-whop-border text-whop-mute cursor-not-allowed"
                : "bg-whop-orange text-white hover:bg-whop-orangeDark hover:shadow-[0_0_24px_rgba(255,79,0,0.4)] hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
          }`}
        >
          {isClaimed ? (
            <><CheckCircle2 className="h-4 w-4" /> You picked this</>
          ) : isOtherClaimed ? (
            <><Lock className="h-4 w-4" /> Locked</>
          ) : (
            <>Start building this <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" /></>
          )}
        </button>
      </div>
    </motion.div>
  );
}
