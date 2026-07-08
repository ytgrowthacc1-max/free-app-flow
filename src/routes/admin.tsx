import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import { Flame, Snowflake, ThermometerSun, Users, ChevronDown, ChevronRight, ExternalLink, Lock, Terminal } from "lucide-react";
import { adminAccess, adminListLeads, adminDeleteLead, adminGetDaemonLogs, type Lead } from "@/lib/leads.functions";
import logoAsset from "@/assets/app-builders-logo.png.asset.json";

export const Route = createFileRoute("/admin")({
  head: () => ({ meta: [{ title: "Admin · App Builders" }, { name: "robots", content: "noindex" }] }),
  component: AdminPage,
});

const STORAGE_KEY = "wop_admin_pw";

const TAG_STYLES: Record<string, { cls: string; icon: ReactNode }> = {
  HOT: { cls: "bg-[#FF4F00]/10 text-whop-orange border-whop-orange/30", icon: <Flame className="h-3 w-3" /> },
  WARM: { cls: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30", icon: <ThermometerSun className="h-3 w-3" /> },
  COLD: { cls: "bg-zinc-500/10 text-zinc-300 border-zinc-500/30", icon: <Snowflake className="h-3 w-3" /> },
};

function AdminPage() {
  const [pw, setPw] = useState("");
  const [authed, setAuthed] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState({ total: 0, hot: 0, warm: 0, cold: 0 });
  const [openId, setOpenId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"ALL" | "HOT" | "WARM" | "COLD">("ALL");
  const [search, setSearch] = useState("");
  const [completionFilter, setCompletionFilter] = useState<"ALL" | "COMPLETED" | "ABANDONED">("ALL");
  const [logs, setLogs] = useState("");
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const loadLogs = async (password: string) => {
    setLoadingLogs(true);
    try {
      const r = await adminGetDaemonLogs({ data: { password } });
      setLogs(r.logs);
    } catch {
      setLogs("[ERROR] Failed to fetch daemon logs.");
    } finally {
      setLoadingLogs(false);
    }
  };

  const load = async (password: string) => {
    setBusy(true);
    setError("");
    try {
      const r = await adminListLeads({ data: { password } });
      setLeads(r.leads);
      setStats(r.stats);
      setAuthed(true);
      sessionStorage.setItem(STORAGE_KEY, password);
    } catch {
      setError("Wrong password.");
      setAuthed(false);
      sessionStorage.removeItem(STORAGE_KEY);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved) {
      void load(saved);
      const interval = setInterval(() => {
        void load(saved);
      }, 10000);
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authed]);

  useEffect(() => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved && showLogs) {
      void loadLogs(saved);
      const interval = setInterval(() => {
        void loadLogs(saved);
      }, 5000);
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authed, showLogs]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pw) return;
    const r = await adminAccess({ data: { password: pw } }).catch(() => ({ ok: false }));
    if (!r.ok) { setError("Wrong password."); return; }
    await load(pw);
  };

  if (!authed) {
    return (
      <div className="min-h-screen bg-glow flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-sm rounded-2xl border border-whop-border bg-whop-surface p-6">
          <div className="flex items-center gap-2 font-display font-semibold mb-4">
            <img src={logoAsset.url} alt="App Builders" className="h-8 w-8 rounded-md" />
            <span>App Builders Admin</span>
          </div>
          <label className="block text-[11px] uppercase tracking-[0.2em] text-whop-mute mb-2">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-whop-mute" />
            <input
              autoFocus
              type="password"
              value={pw}
              onChange={(e) => setPw(e.target.value)}
              className="wop-input pl-10"
              placeholder="••••••••"
            />
          </div>
          {error && <div className="mt-3 text-sm text-red-400">{error}</div>}
          <button
            type="submit"
            disabled={busy}
            className="mt-4 w-full rounded-xl bg-whop-orange px-5 py-3 font-display font-semibold text-white transition hover:bg-whop-orangeDark disabled:opacity-50"
          >
            {busy ? "Checking…" : "Enter"}
          </button>
        </form>
      </div>
    );
  }

  const completedCount = leads.filter((l) => l.completed).length;
  const partialCount = leads.filter((l) => !l.completed).length;

  const filtered = leads.filter((l) => {
    // 1. Tag Filter
    if (filter !== "ALL" && l.lead_tag !== filter) return false;
    
    // 2. Completion Filter
    if (completionFilter === "COMPLETED" && !l.completed) return false;
    if (completionFilter === "ABANDONED" && l.completed) return false;
    
    // 3. Search Filter
    if (search.trim()) {
      const q = search.toLowerCase();
      const nameMatch = l.first_name?.toLowerCase().includes(q) || false;
      const emailMatch = l.email?.toLowerCase().includes(q) || false;
      const nicheMatch = l.niche?.toLowerCase().includes(q) || false;
      const userMatch = l.whop_username?.toLowerCase().includes(q) || false;
      return nameMatch || emailMatch || nicheMatch || userMatch;
    }
    
    return true;
  });

  return (
    <div className="relative min-h-screen bg-glow">
      <header className="relative z-10 flex items-center justify-between px-6 sm:px-10 pt-8">
        <Link to="/" className="flex items-center gap-2 font-display font-semibold">
          <img src={logoAsset.url} alt="App Builders" className="h-8 w-8 rounded-md" />
          <span>App Builders</span>
          <span className="ml-2 text-[10px] uppercase tracking-[0.25em] text-whop-mute">Admin</span>
        </Link>
        <button
          onClick={() => { sessionStorage.removeItem(STORAGE_KEY); setAuthed(false); setPw(""); }}
          className="text-xs uppercase tracking-[0.2em] text-whop-text hover:text-whop-orange transition"
        >
          Sign out →
        </button>
      </header>

      <main className="relative z-10 mx-auto max-w-6xl px-6 py-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">Leads Dashboard</h1>
            <p className="mt-1 text-whop-text">All onboarding submissions.</p>
          </div>
          <button
            onClick={() => {
              const saved = sessionStorage.getItem(STORAGE_KEY);
              if (saved) {
                void load(saved);
                if (showLogs) void loadLogs(saved);
              }
            }}
            disabled={busy || loadingLogs}
            className="rounded-xl border border-whop-border bg-whop-surface px-4 py-2.5 text-xs uppercase tracking-[0.1em] text-white hover:border-zinc-500 transition-colors disabled:opacity-50"
          >
            {busy || loadingLogs ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
          <Stat label="Total Leads" value={leads.length} icon={<Users />} />
          <Stat label="Completed" value={completedCount} icon={<Flame />} accent="text-green-400" />
          <Stat label="Incomplete / Abandoned" value={partialCount} icon={<Snowflake />} accent="text-whop-orange" />
          <Stat label="Hot (Tag)" value={stats.hot} icon={<ThermometerSun />} accent="text-yellow-400" />
        </div>

        <div className="mt-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap gap-2">
            <div className="flex rounded-lg border border-whop-border bg-whop-surface p-1">
              {(["ALL", "COMPLETED", "ABANDONED"] as const).map((cf) => (
                <button
                  key={cf}
                  onClick={() => setCompletionFilter(cf)}
                  className={`rounded-md px-3 py-1.5 text-xs uppercase tracking-[0.1em] transition ${
                    completionFilter === cf ? "bg-whop-orange text-white" : "text-whop-text hover:text-white"
                  }`}
                >
                  {cf === "ALL" ? "All Statuses" : cf === "COMPLETED" ? "Completed" : "Abandoned"}
                </button>
              ))}
            </div>

            <div className="flex rounded-lg border border-whop-border bg-whop-surface p-1">
              {(["ALL", "HOT", "WARM", "COLD"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`rounded-md px-3 py-1.5 text-xs uppercase tracking-[0.15em] transition ${
                    filter === f ? "bg-zinc-800 text-white" : "text-whop-text hover:text-white"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="w-full md:max-w-xs">
            <input
              type="text"
              placeholder="Search leads..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-whop-border bg-whop-surface px-4 py-2 text-sm text-white placeholder-zinc-500 focus:border-whop-orange focus:outline-none transition-colors"
            />
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-whop-border bg-whop-surface overflow-hidden">
          <div className="grid grid-cols-12 px-5 py-3 text-[10px] uppercase tracking-[0.2em] text-whop-mute border-b border-whop-border">
            <div className="col-span-3">Name / Email</div>
            <div className="col-span-3">Whop User / Link</div>
            <div className="col-span-2">Niche</div>
            <div className="col-span-2">MRR</div>
            <div className="col-span-2 text-right">Tag · Score</div>
          </div>

          {filtered.length === 0 && (
            <div className="px-5 py-12 text-center text-whop-text">No leads found matching your criteria.</div>
          )}

          {filtered.map((l) => {
            const open = openId === l.id;
            const tag = TAG_STYLES[l.lead_tag] || TAG_STYLES.COLD;
            return (
              <div key={l.id} className="border-b border-whop-border last:border-b-0">
                <button
                  onClick={() => setOpenId(open ? null : l.id)}
                  className="grid grid-cols-12 items-center w-full px-5 py-4 text-left hover:bg-[#FF4F00]/5 transition-colors"
                >
                  <div className="col-span-3">
                    <div className="font-display font-medium text-white">{l.first_name || "Guest User"}</div>
                    <div className="text-xs text-whop-text truncate">{l.email || "(no email captured)"}</div>
                  </div>
                  <div className="col-span-3">
                    <div className="text-sm font-semibold text-whop-cyan truncate">@{l.whop_username || "anonymous"}</div>
                    <div className="text-xs text-whop-mute truncate">{l.whop_url ? l.whop_url.replace("https://whop.com/", "") : "(no link)"}</div>
                  </div>
                  <div className="col-span-2 text-sm text-whop-text">{l.niche || "—"}</div>
                  <div className="col-span-2 text-sm text-white">
                    {l.completed ? (
                      <>
                        ${(l.mrr ?? 0).toLocaleString()}
                        <span className="text-whop-mute text-xs">/mo</span>
                      </>
                    ) : (
                      <span className="text-xs text-whop-orange font-semibold uppercase tracking-wider">Incomplete</span>
                    )}
                  </div>
                  <div className="col-span-2 flex items-center justify-end gap-2">
                    <span className={`inline-flex items-center gap-1 border px-2 py-0.5 rounded-full text-[10px] uppercase tracking-[0.15em] font-bold ${tag.cls}`}>
                      {tag.icon} {l.lead_tag} · {l.lead_score}
                    </span>
                    {open ? <ChevronDown className="h-4 w-4 text-whop-mute" /> : <ChevronRight className="h-4 w-4 text-whop-mute" />}
                  </div>
                </button>

                {open && (
                  <div className="px-5 pb-6 pt-1 bg-[#0F0F11]/40">
                    <div className="grid gap-4 md:grid-cols-2">
                      <Detail label="Whop User ID">{l.whop_user_id || "—"}</Detail>
                      <Detail label="Whop Username">@{l.whop_username || "—"}</Detail>
                      <Detail label="Whop URL">
                        {l.whop_url ? (
                          <a href={l.whop_url} target="_blank" rel="noreferrer" className="text-whop-cyan hover:underline inline-flex items-center gap-1">
                            {l.whop_url} <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : (
                          "—"
                        )}
                      </Detail>
                      <Detail label="Niche / Niche Selection">{l.niche || "—"}</Detail>
                      <Detail label="Members Count">{l.member_count?.toLocaleString() || "—"}</Detail>
                      <Detail label="Monthly Price">${l.monthly_price || "—"}</Detail>
                      <Detail label="Ideal app Idea">{l.ideal_app || "—"}</Detail>
                      <Detail label="Outreach Status">
                        {l.completed ? (
                          <span className="text-green-400 font-semibold">Completed web flow</span>
                        ) : l.abandoned_message_sent ? (
                          <span className="text-yellow-400 font-semibold">Outreach DM sent</span>
                        ) : (
                          <span className="text-zinc-400">Waiting in queue / no DM sent yet</span>
                        )}
                      </Detail>
                      <Detail label="Timeline">{l.timeline || "—"}</Detail>
                      <Detail label="Social Handle">{l.social_handle || "—"}</Detail>
                      <Detail label="Submitted">{new Date(l.created_at).toLocaleString()}</Detail>
                    </div>
                    <div className="mt-6 flex items-center justify-between border-t border-whop-border/60 pt-4">
                      {l.completed ? (
                        <Link
                          to="/blueprint/$id"
                          params={{ id: l.id }}
                          className="inline-flex items-center gap-1 text-xs uppercase tracking-[0.15em] text-whop-orange hover:underline font-semibold"
                        >
                          Open Full Blueprint <ExternalLink className="h-3 w-3" />
                        </Link>
                      ) : (
                        <div />
                      )}
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (confirm("Are you sure you want to delete this lead?")) {
                            try {
                              const saved = sessionStorage.getItem(STORAGE_KEY);
                              if (saved) {
                                await adminDeleteLead({ data: { password: saved, id: l.id } });
                                void load(saved);
                              }
                            } catch (e) {
                              alert("Failed to delete lead: " + (e instanceof Error ? e.message : String(e)));
                            }
                          }
                        }}
                        className="rounded-lg bg-red-500/10 border border-red-500/30 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.15em] text-red-400 hover:bg-red-500/20 hover:border-red-500/50 transition-colors"
                      >
                        Delete Lead
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Daemon Logs Terminal Section */}
        <div className="mt-12 rounded-2xl border border-whop-border bg-whop-surface overflow-hidden">
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="flex items-center justify-between w-full px-6 py-4 hover:bg-[#FF4F00]/5 transition-colors"
          >
            <div className="flex items-center gap-2 font-display font-medium text-white">
              <Terminal className="h-4 w-4 text-whop-orange" />
              <span>Background Automation Daemon Logs</span>
            </div>
            <div className="flex items-center gap-3">
              {showLogs && (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[9px] uppercase tracking-wider font-bold bg-green-500/10 text-green-400 border border-green-500/20">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" /> Live Polling
                </span>
              )}
              {showLogs ? <ChevronDown className="h-4 w-4 text-whop-mute" /> : <ChevronRight className="h-4 w-4 text-whop-mute" />}
            </div>
          </button>

          {showLogs && (
            <div className="border-t border-whop-border bg-[#0B0B0C] p-4 font-mono text-xs text-zinc-300 leading-relaxed">
              <div className="flex justify-between items-center mb-3 text-[10px] uppercase tracking-[0.2em] text-whop-mute border-b border-whop-border/50 pb-2">
                <span>Console Output (stdout/stderr)</span>
                <span>Ticks every 30s · UI refreshes every 5s</span>
              </div>
              <pre className="max-h-80 overflow-y-auto whitespace-pre-wrap rounded-lg bg-[#070708] p-4 text-[11px] leading-relaxed border border-whop-border/40 text-emerald-400">
                {logs || "Waiting for logs..."}
              </pre>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function Stat({ label, value, icon, accent = "text-white" }: { label: string; value: number; icon: ReactNode; accent?: string }) {
  return (
    <div className="rounded-2xl border border-whop-border bg-whop-surface p-5">
      <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-whop-mute">
        <span className={`[&>svg]:h-3.5 [&>svg]:w-3.5 ${accent}`}>{icon}</span>{label}
      </div>
      <div className={`mt-2 font-display text-3xl font-semibold ${accent}`}>{value}</div>
    </div>
  );
}

function Detail({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-[0.2em] text-whop-mute">{label}</div>
      <div className="mt-1 text-sm text-white break-words">{children}</div>
    </div>
  );
}
