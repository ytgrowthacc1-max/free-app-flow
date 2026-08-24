import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import { Flame, Snowflake, ThermometerSun, Users, ChevronDown, ChevronRight, ExternalLink, Lock, Terminal, BadgeCheck, CheckCircle2, DollarSign, Globe, Search, Filter, X, Check } from "lucide-react";
import { adminAccess, adminListLeads, adminDeleteLead, adminGetDaemonLogs, adminGetSettings, adminToggleGlobalChatbot, adminToggleLeadChatbot, type Lead } from "@/lib/leads.functions";
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

function isCommunityVerified(l: Lead): boolean {
  if (!l.whop_url) return false;
  const companies = (l as any).oauth_companies;
  if (Array.isArray(companies) && companies.length > 0) {
    const isMatch = companies.some((c: any) => c.route && l.whop_url.toLowerCase().includes(c.route.toLowerCase()));
    if (isMatch) return true;
  }
  if (l.scrape_status === "SUCCESS" && l.scraped_data) {
    return true;
  }
  return false;
}

function AdminPage() {
  const [pw, setPw] = useState("");
  const [authed, setAuthed] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState({ total: 0, hot: 0, warm: 0, cold: 0, completed: 0, incomplete: 0 });
  const [openId, setOpenId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"ALL" | "HOT" | "WARM" | "COLD">("ALL");
  const [search, setSearch] = useState("");
  const [completionFilter, setCompletionFilter] = useState<"ALL" | "COMPLETED" | "ABANDONED">("ALL");
  
  // Money filter state
  const [moneyField, setMoneyField] = useState<"MRR" | "PROFILE_EARNINGS" | "PRICE" | "LTV">("MRR");
  const [moneyOp, setMoneyOp] = useState<"MIN" | "MAX">("MIN");
  const [moneyVal, setMoneyVal] = useState<string>("");

  // Country checkbox filter state
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [countrySearch, setCountrySearch] = useState<string>("");
  const [countryDropdownOpen, setCountryDropdownOpen] = useState(false);

  // Pagination state
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(15);

  const [logs, setLogs] = useState("");
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [activeTab, setActiveTab] = useState<"leads" | "logs">("leads");
  const [logSearch, setLogSearch] = useState("");

  const [globalChatbotEnabled, setGlobalChatbotEnabled] = useState(false);
  const [togglingGlobal, setTogglingGlobal] = useState(false);

  const loadSettings = async (password: string) => {
    try {
      const res = await adminGetSettings({ data: { password: password.trim() } });
      setGlobalChatbotEnabled(res.global_chatbot_enabled ?? (res as any).globalChatbotEnabled ?? false);
    } catch {
      // ignore
    }
  };

  const loadLogs = async (password: string) => {
    setLoadingLogs(true);
    try {
      const r = await adminGetDaemonLogs({ data: { password: password.trim() } });
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
      const cleanPw = password.trim();
      const r = await adminListLeads({ data: { password: cleanPw } });
      setLeads(r.leads);
      setStats(r.stats);
      setAuthed(true);
      sessionStorage.setItem(STORAGE_KEY, cleanPw);
      void loadSettings(cleanPw);
    } catch (err: any) {
      const msg = err?.message || String(err);
      if (msg.includes("Unauthorized")) {
        setError("Wrong password.");
      } else {
        setError("Error loading leads: " + msg);
      }
      setAuthed(false);
      sessionStorage.removeItem(STORAGE_KEY);
    } finally {
      setBusy(false);
    }
  };

  const handleToggleGlobalChatbot = async () => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (!saved) return;
    setTogglingGlobal(true);
    const nextVal = !globalChatbotEnabled;
    try {
      await adminToggleGlobalChatbot({ data: { password: saved.trim(), enabled: nextVal } });
      setGlobalChatbotEnabled(nextVal);
    } catch (e) {
      alert("Failed to toggle chatbot setting: " + (e instanceof Error ? e.message : String(e)));
    } finally {
      setTogglingGlobal(false);
    }
  };

  const handleToggleLeadChatbot = async (leadId: string, currentVal: boolean) => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (!saved) return;
    const nextVal = !currentVal;
    try {
      await adminToggleLeadChatbot({ data: { password: saved.trim(), leadId, enabled: nextVal } });
      setLeads((prev) =>
        prev.map((l) => (l.id === leadId ? ({ ...l, ai_bot_enabled: nextVal } as any) : l))
      );
    } catch (e) {
      alert("Failed to toggle lead chatbot setting: " + (e instanceof Error ? e.message : String(e)));
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
  }, []);

  useEffect(() => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved && activeTab === "logs") {
      void loadLogs(saved);
      const interval = setInterval(() => {
        void loadLogs(saved);
      }, 5000);
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authed, activeTab]);

  // Reset page when any filter changes (Must be placed before early returns to satisfy React Rules of Hooks)
  useEffect(() => {
    setPage(1);
  }, [filter, completionFilter, search, moneyField, moneyOp, moneyVal, selectedCountries, pageSize]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanPw = pw.trim();
    if (!cleanPw) return;
    setBusy(true);
    setError("");
    try {
      const r = await adminAccess({ data: { password: cleanPw } });
      if (!r || !r.ok) {
        setError("Wrong password.");
        return;
      }
      await load(cleanPw);
    } catch (err: any) {
      const msg = err?.message || String(err);
      if (msg.includes("Unauthorized") || msg.includes("password")) {
        setError("Wrong password.");
      } else {
        // Still attempt to load directly in case adminAccess had a transient RPC issue
        await load(cleanPw);
      }
    } finally {
      setBusy(false);
    }
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

  const safeLeads = Array.isArray(leads) ? leads : [];
  const completedCount = safeLeads.filter((l) => l && l.completed).length;
  const partialCount = safeLeads.filter((l) => l && !l.completed).length;

  // Extract unique countries from leads dataset for checkbox options
  const countryMap = new Map<string, { code: string; name: string; flag: string; count: number }>();
  safeLeads.forEach((l) => {
    if (!l) return;
    const code = l.country ? String(l.country).toUpperCase() : "UNKNOWN";
    const name = l.country_name || (code !== "UNKNOWN" ? code : "Unknown Location");
    const flag = l.country_flag || "🌐";
    if (!countryMap.has(code)) {
      countryMap.set(code, { code, name, flag, count: 0 });
    }
    countryMap.get(code)!.count += 1;
  });

  const countryOptions = Array.from(countryMap.values()).sort((a, b) => b.count - a.count);
  const filteredCountryOptions = countryOptions.filter(
    (c) =>
      String(c.name || "").toLowerCase().includes(String(countrySearch || "").toLowerCase()) ||
      String(c.code || "").toLowerCase().includes(String(countrySearch || "").toLowerCase())
  );

  const filtered = safeLeads.filter((l) => {
    if (!l) return false;
    
    // 1. Tag Filter
    if (filter !== "ALL" && l.lead_tag !== filter) return false;
    
    // 2. Completion Filter
    if (completionFilter === "COMPLETED" && !l.completed) return false;
    if (completionFilter === "ABANDONED" && l.completed) return false;
    
    // 3. Money Filter (MRR / Profile Earnings / Monthly Price / LTV Spend)
    if (moneyVal.trim() !== "") {
      const num = parseFloat(moneyVal);
      if (!isNaN(num)) {
        let target = 0;
        if (moneyField === "MRR") target = typeof l.mrr === "number" ? l.mrr : 0;
        else if (moneyField === "PROFILE_EARNINGS") target = typeof l.profile_earnings_usd === "number" ? l.profile_earnings_usd : 0;
        else if (moneyField === "PRICE") target = typeof l.monthly_price === "number" ? l.monthly_price : 0;
        else if (moneyField === "LTV") target = typeof l.ltv === "number" ? l.ltv : 0;

        if (moneyOp === "MIN" && target < num) return false;
        if (moneyOp === "MAX" && target > num) return false;
      }
    }

    // 4. Country Checkboxes Filter
    if (selectedCountries.length > 0) {
      const leadCode = l.country ? String(l.country).toUpperCase() : "UNKNOWN";
      if (!selectedCountries.includes(leadCode)) return false;
    }

    // 5. Search Text Filter
    if (search.trim()) {
      const q = search.toLowerCase();
      const nameMatch = String(l.first_name || "").toLowerCase().includes(q);
      const emailMatch = String(l.email || "").toLowerCase().includes(q);
      const nicheMatch = String(l.niche || "").toLowerCase().includes(q);
      const userMatch = String(l.whop_username || "").toLowerCase().includes(q);
      const countryMatch = String(l.country || "").toLowerCase().includes(q) || String(l.country_name || "").toLowerCase().includes(q) || String(l.city || "").toLowerCase().includes(q);
      return nameMatch || emailMatch || nicheMatch || userMatch || countryMatch;
    }
    
    return true;
  });

  // Pagination Slice
  const totalPages = Math.max(1, Math.ceil(filtered.length / Math.max(1, pageSize)));
  const safePage = Math.min(Math.max(1, page), totalPages);
  const paginatedLeads = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);

  // Parse the raw logs string into filterable lines safely
  const parsedLogs = typeof logs === "string"
    ? logs
        .split("\n")
        .map((l) => l.trim())
        .filter((l) => l.length > 0)
        .filter((l) => !logSearch.trim() || l.toLowerCase().includes(logSearch.toLowerCase()))
    : [];

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
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">Admin Dashboard</h1>
            <p className="mt-1 text-sm text-whop-text">Manage onboarding leads and background automation processes.</p>
          </div>
          <button
            onClick={() => {
              const saved = sessionStorage.getItem(STORAGE_KEY);
              if (saved) {
                if (activeTab === "leads") void load(saved);
                if (activeTab === "logs") void loadLogs(saved);
              }
            }}
            disabled={busy || loadingLogs}
            className="rounded-xl border border-whop-border bg-whop-surface px-4 py-2.5 text-xs uppercase tracking-[0.1em] text-white hover:border-zinc-500 transition-colors disabled:opacity-50"
          >
            {busy || loadingLogs ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-whop-border/60 mb-8">
          <button
            onClick={() => setActiveTab("leads")}
            className={`pb-4 px-2 text-xs uppercase tracking-[0.2em] font-semibold transition-all relative ${
              activeTab === "leads"
                ? "text-whop-orange font-bold border-b-2 border-whop-orange"
                : "text-whop-mute hover:text-white"
            }`}
          >
            Leads Management
          </button>
          <button
            onClick={() => setActiveTab("logs")}
            className={`pb-4 px-2 ml-6 text-xs uppercase tracking-[0.2em] font-semibold transition-all relative ${
              activeTab === "logs"
                ? "text-whop-orange font-bold border-b-2 border-whop-orange"
                : "text-whop-mute hover:text-white"
            }`}
          >
            Automation Logs
          </button>
        </div>

        {activeTab === "leads" ? (
          <>
            {/* Master AI Chatbot Control Banner */}
            <div className="mb-6 rounded-2xl border border-whop-border bg-whop-surface p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 font-display text-base font-semibold text-white">
                  <span>AI Chatbot Auto-Replies</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    globalChatbotEnabled
                      ? "bg-green-500/20 text-green-400 border border-green-500/40"
                      : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                  }`}>
                    {globalChatbotEnabled ? "Globally ACTIVE" : "OFF (Manual Operator Mode)"}
                  </span>
                </div>
                <p className="mt-1 text-xs text-whop-mute max-w-2xl">
                  Initial outreach DMs and blueprint links are ALWAYS sent automatically. When replies arrive, Telegram alerts you so you can answer manually unless AI bot is enabled.
                </p>
              </div>
              <button
                onClick={handleToggleGlobalChatbot}
                disabled={togglingGlobal}
                className={`px-4 py-2 rounded-xl text-xs font-semibold uppercase tracking-[0.1em] transition-all disabled:opacity-50 ${
                  globalChatbotEnabled
                    ? "bg-red-500/20 text-red-400 border border-red-500/40 hover:bg-red-500/30"
                    : "bg-whop-orange text-white hover:bg-whop-orangeDark shadow-lg shadow-whop-orange/20"
                }`}
              >
                {togglingGlobal ? "Updating..." : globalChatbotEnabled ? "Disable Globally" : "Enable Globally"}
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <Stat label="Total Leads" value={stats.total} icon={<Users />} />
              <Stat label="Completed" value={stats.completed} icon={<Flame />} accent="text-green-400" />
              <Stat label="Incomplete / Abandoned" value={stats.incomplete} icon={<Snowflake />} accent="text-whop-orange" />
              <Stat label="Hot (Tag)" value={stats.hot} icon={<ThermometerSun />} accent="text-yellow-400" />
            </div>

            <div className="mt-8 flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-whop-surface/60 border border-whop-border p-4 rounded-2xl">
              <div className="flex flex-wrap items-center gap-3">
                {/* Completion Status Radios */}
                <div role="radiogroup" aria-label="Completion Status Filter" className="flex rounded-lg border border-whop-border bg-[#121214] p-1">
                  {(["ALL", "COMPLETED", "ABANDONED"] as const).map((cf) => (
                    <button
                      key={cf}
                      type="button"
                      role="radio"
                      aria-checked={completionFilter === cf}
                      onClick={() => setCompletionFilter(cf)}
                      className={`rounded-md px-2.5 py-1.5 text-[11px] font-bold uppercase tracking-[0.1em] transition ${
                        completionFilter === cf ? "bg-whop-orange text-white" : "text-whop-text hover:text-white"
                      }`}
                    >
                      {cf === "ALL" ? "All" : cf === "COMPLETED" ? "Completed" : "Abandoned"}
                    </button>
                  ))}
                </div>

                {/* Tag Radios */}
                <div role="radiogroup" aria-label="Lead Tag Filter" className="flex rounded-lg border border-whop-border bg-[#121214] p-1">
                  {(["ALL", "HOT", "WARM", "COLD"] as const).map((f) => (
                    <button
                      key={f}
                      type="button"
                      role="radio"
                      aria-checked={filter === f}
                      onClick={() => setFilter(f)}
                      className={`rounded-md px-2.5 py-1.5 text-[11px] font-bold uppercase tracking-[0.1em] transition ${
                        filter === f ? "bg-zinc-800 text-white" : "text-whop-text hover:text-white"
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>

                {/* Money Filter (MRR / LTV / Monthly Price) */}
                <div className="flex items-center rounded-lg border border-whop-border bg-[#121214] p-1 gap-1">
                  <select
                    value={moneyField}
                    onChange={(e) => setMoneyField(e.target.value as any)}
                    className="bg-[#18181B] text-white border-0 rounded px-2 py-1 text-[11px] font-semibold focus:outline-none focus:ring-1 focus:ring-whop-orange"
                  >
                    <option value="MRR">MRR (Form Input)</option>
                    <option value="PROFILE_EARNINGS">Profile Earnings (Badge)</option>
                    <option value="PRICE">Price</option>
                    <option value="LTV">Whop Spend (LTV)</option>
                  </select>
                  <select
                    value={moneyOp}
                    onChange={(e) => setMoneyOp(e.target.value as any)}
                    className="bg-[#18181B] text-white border-0 rounded px-1.5 py-1 text-[11px] font-semibold focus:outline-none focus:ring-1 focus:ring-whop-orange"
                  >
                    <option value="MIN">≥ Min</option>
                    <option value="MAX">≤ Max</option>
                  </select>
                  <div className="relative flex items-center">
                    <span className="absolute left-2 text-xs text-zinc-400">$</span>
                    <input
                      type="number"
                      placeholder="Amount"
                      value={moneyVal}
                      onChange={(e) => setMoneyVal(e.target.value)}
                      className="w-20 bg-[#18181B] text-white border-0 rounded pl-5 pr-2 py-1 text-[11px] focus:outline-none focus:ring-1 focus:ring-whop-orange placeholder-zinc-600"
                    />
                  </div>
                  {moneyVal && (
                    <button
                      onClick={() => setMoneyVal("")}
                      className="p-1 text-zinc-400 hover:text-white rounded"
                      title="Clear money filter"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>

                {/* Country Filter Checkbox Dropdown with Search */}
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setCountryDropdownOpen(!countryDropdownOpen)}
                    className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-[11px] font-bold transition focus:outline-none ${
                      selectedCountries.length > 0
                        ? "border-whop-orange bg-whop-orange/15 text-white"
                        : "border-whop-border bg-[#121214] text-whop-text hover:text-white"
                    }`}
                  >
                    <Globe className="h-3.5 w-3.5 text-whop-orange" />
                    <span>
                      {selectedCountries.length === 0
                        ? "All Countries"
                        : `${selectedCountries.length} Country Selected`}
                    </span>
                    <ChevronDown className="h-3.5 w-3.5 opacity-60" />
                  </button>

                  {countryDropdownOpen && (
                    <>
                      <div
                        className="fixed inset-0 z-20"
                        onClick={() => setCountryDropdownOpen(false)}
                      />
                      <div className="absolute right-0 sm:left-0 z-30 mt-2 w-72 rounded-xl border border-whop-border bg-[#121214] p-3 shadow-2xl backdrop-blur-xl">
                        <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                          <span className="text-xs font-semibold text-white">Filter by Country</span>
                          {selectedCountries.length > 0 && (
                            <button
                              onClick={() => setSelectedCountries([])}
                              className="text-[10px] text-whop-orange hover:underline font-semibold"
                            >
                              Clear Selection
                            </button>
                          )}
                        </div>

                        {/* Search input inside country dropdown */}
                        <div className="relative my-2">
                          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-zinc-500" />
                          <input
                            type="text"
                            placeholder="Search country..."
                            value={countrySearch}
                            onChange={(e) => setCountrySearch(e.target.value)}
                            className="w-full bg-[#18181B] text-white border border-zinc-800 rounded-lg pl-8 pr-3 py-1 text-xs focus:outline-none focus:border-whop-orange"
                          />
                        </div>

                        {/* Country Checkboxes List */}
                        <div className="max-h-52 overflow-y-auto space-y-1 pr-1">
                          {filteredCountryOptions.length === 0 ? (
                            <div className="py-3 text-center text-xs text-zinc-500">No countries match "{countrySearch}"</div>
                          ) : (
                            filteredCountryOptions.map((c) => {
                              const isChecked = selectedCountries.includes(c.code);
                              return (
                                <label
                                  key={c.code}
                                  className="flex items-center justify-between p-1.5 rounded-lg hover:bg-zinc-800/60 cursor-pointer text-xs transition"
                                >
                                  <div className="flex items-center gap-2">
                                    <input
                                      type="checkbox"
                                      checked={isChecked}
                                      onChange={(e) => {
                                        if (e.target.checked) {
                                          setSelectedCountries((prev) => [...prev, c.code]);
                                        } else {
                                          setSelectedCountries((prev) => prev.filter((x) => x !== c.code));
                                        }
                                      }}
                                      className="rounded border-zinc-700 bg-zinc-900 text-whop-orange focus:ring-0"
                                    />
                                    <span className="text-base leading-none">{c.flag}</span>
                                    <span className="font-medium text-zinc-200">{c.name}</span>
                                  </div>
                                  <span className="text-[10px] font-bold text-zinc-500 px-1.5 py-0.5 rounded bg-zinc-900">
                                    {c.count}
                                  </span>
                                </label>
                              );
                            })
                          )}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Text Search Box */}
              <div className="w-full lg:max-w-xs relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
                <input
                  type="text"
                  placeholder="Search leads..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  aria-label="Search leads by name, email, niche, or username"
                  className="w-full rounded-lg border border-whop-border bg-[#121214] pl-9 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:border-whop-orange focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div className="mt-6 rounded-2xl border border-whop-border bg-whop-surface overflow-hidden">
              <div className="grid grid-cols-12 px-5 py-3 text-[10px] uppercase tracking-[0.2em] text-whop-mute border-b border-whop-border">
                <div className="col-span-3">Name / Location</div>
                <div className="col-span-3">Whop User / Link</div>
                <div className="col-span-2">Niche</div>
                <div className="col-span-2">MRR / Spend (LTV)</div>
                <div className="col-span-2 text-right">Tag · Score</div>
              </div>

              {filtered.length === 0 && (
                <div className="px-5 py-12 text-center text-whop-text">No leads found matching your criteria.</div>
              )}

              {paginatedLeads.map((l) => {
                const open = openId === l.id;
                const tag = TAG_STYLES[l.lead_tag] || TAG_STYLES.COLD;
                const cleanUsername = l.whop_username ? l.whop_username.replace(/^@/, "") : "";
                const verifiedComm = isCommunityVerified(l);

                return (
                  <div key={l.id} className="border-b border-whop-border last:border-b-0">
                    <button
                      type="button"
                      aria-expanded={open}
                      aria-controls={`lead-details-${l.id}`}
                      onClick={() => setOpenId(open ? null : l.id)}
                      className="grid grid-cols-12 items-center w-full px-5 py-4 text-left hover:bg-[#FF4F00]/5 transition-colors focus-visible:ring-2 focus-visible:ring-whop-orange focus-visible:outline-none"
                    >
                      <div className="col-span-3">
                        <div className="flex items-center gap-1.5 font-display font-medium text-white">
                          <span className="truncate">{l.first_name || "Guest User"}</span>
                          {l.country && (
                            <span
                              className="inline-flex items-center gap-1 rounded bg-[#18181B] px-1.5 py-0.5 text-[10px] font-semibold text-zinc-300 border border-zinc-700/60 shrink-0"
                              title={`${l.city ? `${l.city}, ` : ""}${l.country_name || l.country}`}
                            >
                              <span>{l.country_flag || "🌐"}</span>
                              <span>{l.country}</span>
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-whop-text truncate">{l.email || "(no email captured)"}</div>
                      </div>
                      <div className="col-span-3">
                        <div className="text-sm font-semibold text-whop-cyan truncate">
                          {cleanUsername && cleanUsername !== "anonymous" ? (
                            <a
                              href={`https://whop.com/@${cleanUsername}`}
                              target="_blank"
                              rel="noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="hover:underline inline-flex items-center gap-1 text-whop-cyan font-semibold"
                            >
                              @{cleanUsername}
                              <ExternalLink className="h-3 w-3 opacity-60 shrink-0" />
                            </a>
                          ) : (
                            <span className="text-whop-mute">@anonymous</span>
                          )}
                        </div>
                        <div className="text-xs text-whop-mute truncate flex items-center gap-1">
                          <span>{l.whop_url ? l.whop_url.replace("https://whop.com/", "") : "(no link)"}</span>
                          {verifiedComm && (
                            <span title="Auto-Verified Community Link (Selected from Whop dropdown)" className="inline-flex items-center text-green-400">
                              <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-green-400" />
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="col-span-2 text-sm text-white flex flex-col justify-center">
                        <div className="font-bold text-white">
                          ${(l.mrr ?? 0).toLocaleString()}
                          <span className="text-whop-mute text-xs font-normal">/mo MRR</span>
                        </div>
                        {l.profile_earnings_badge ? (
                          <div className="text-[11px] font-bold text-green-400 mt-0.5" title="Public Whop Profile Earnings">
                            {l.profile_earnings_badge} Earned
                          </div>
                        ) : typeof l.ltv === "number" && l.ltv > 0 ? (
                          <div className="text-[10px] text-zinc-400 font-medium mt-0.5">
                            Whop Spend: ${l.ltv.toLocaleString()}
                          </div>
                        ) : null}
                      </div>
                      <div className="col-span-2 flex items-center justify-end gap-2">
                        <span className={`inline-flex items-center gap-1 border px-2 py-0.5 rounded-full text-[10px] uppercase tracking-[0.15em] font-bold ${tag.cls}`}>
                          {tag.icon} {l.lead_tag} · {l.lead_score}
                        </span>
                        {open ? <ChevronDown className="h-4 w-4 text-whop-mute" /> : <ChevronRight className="h-4 w-4 text-whop-mute" />}
                      </div>
                    </button>

                    {open && (
                      <div id={`lead-details-${l.id}`} className="px-5 pb-6 pt-1 bg-[#0F0F11]/40">
                        <div className="grid gap-4 md:grid-cols-2">
                          <Detail label="Location & Demographics">
                            {l.country || l.city ? (
                              <div className="flex flex-col gap-0.5">
                                <span className="inline-flex items-center gap-1.5 font-semibold text-white text-xs">
                                  <span>{l.country_flag || "🌐"}</span>
                                  <span>{l.city ? `${l.city}, ` : ""}{l.country_name || l.country}</span>
                                  <span className="text-[10px] uppercase font-bold text-zinc-300 px-1 py-0.2 rounded bg-zinc-800 border border-zinc-700">
                                    {l.country}
                                  </span>
                                </span>
                                {l.timezone && (
                                  <span className="text-[11px] text-whop-mute">
                                    Timezone: <span className="text-zinc-300">{l.timezone}</span>
                                  </span>
                                )}
                                {l.device && (
                                  <span className="text-[11px] text-whop-mute">
                                    Device: <span className="text-zinc-300">{l.device}</span>
                                  </span>
                                )}
                              </div>
                            ) : (
                              <span className="text-zinc-400 text-xs">Pending interaction</span>
                            )}
                          </Detail>
                          <Detail label="Community Link Verification">
                            {verifiedComm ? (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-green-500/10 text-green-400 border border-green-500/30">
                                <CheckCircle2 className="h-4 w-4 text-green-400" /> Auto-Verified Community (Selected via Whop)
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">
                                Manual Link (Pasted Manually)
                              </span>
                            )}
                          </Detail>
                          <Detail label="Whop User ID">{l.whop_user_id || "—"}</Detail>
                          <Detail label="Whop Username">
                            {cleanUsername && cleanUsername !== "anonymous" ? (
                              <a
                                href={`https://whop.com/@${cleanUsername}`}
                                target="_blank"
                                rel="noreferrer"
                                className="text-whop-cyan hover:underline inline-flex items-center gap-1 font-semibold"
                              >
                                @{cleanUsername} <ExternalLink className="h-3 w-3" />
                              </a>
                            ) : (
                              "—"
                            )}
                          </Detail>
                          <Detail label="Whop Lifetime Spend (LTV)">
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-green-400 text-xs px-2 py-0.5 rounded bg-green-500/10 border border-green-500/30">
                                ${(l.ltv ?? 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD
                              </span>
                              {typeof l.purchase_count === "number" && l.purchase_count > 0 && (
                                <span className="text-[11px] text-zinc-400">
                                  ({l.purchase_count} {l.purchase_count === 1 ? "purchase" : "purchases"})
                                </span>
                              )}
                            </div>
                          </Detail>
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
                          <Detail label="Primary App Goal">{l.primary_goal || "—"}</Detail>
                          <Detail label="AI App Summary">{l.ideal_app_summary || "—"}</Detail>
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
                          <Detail label="AI Chatbot Auto-Reply">
                            <span className={l.ai_bot_enabled || globalChatbotEnabled ? "text-green-400 font-semibold" : "text-amber-400 font-semibold"}>
                              {l.ai_bot_enabled ? "ON (Lead Override)" : globalChatbotEnabled ? "ON (Global Master)" : "OFF (Operator Replies Manually)"}
                            </span>
                          </Detail>
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
                          <div className="flex items-center gap-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                void handleToggleLeadChatbot(l.id, l.ai_bot_enabled ?? false);
                              }}
                              className={`rounded-lg px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.15em] border transition-colors ${
                                l.ai_bot_enabled
                                  ? "bg-green-500/20 text-green-400 border-green-500/40 hover:bg-green-500/30"
                                  : "bg-whop-surface text-whop-text border-whop-border hover:text-white"
                              }`}
                            >
                              {l.ai_bot_enabled ? "AI Bot: ON" : "AI Bot: OFF"}
                            </button>
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
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Pagination Controls Bar */}
            {filtered.length > 0 && (
              <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-4 py-3 bg-whop-surface/60 border border-whop-border rounded-xl">
                <div className="text-xs text-whop-mute flex flex-wrap items-center gap-2">
                  <span>
                    Showing <strong className="text-white">{(safePage - 1) * pageSize + 1}</strong> to <strong className="text-white">{Math.min(safePage * pageSize, filtered.length)}</strong> of <strong className="text-white">{filtered.length}</strong> leads
                  </span>
                  <span className="text-zinc-700">|</span>
                  <span className="text-zinc-400">Leads per page:</span>
                  <select
                    value={pageSize}
                    onChange={(e) => setPageSize(Number(e.target.value))}
                    className="bg-[#18181B] text-white border border-zinc-700 rounded px-2 py-1 text-xs focus:outline-none focus:border-whop-orange"
                  >
                    <option value={10}>10 per page</option>
                    <option value={15}>15 per page</option>
                    <option value={25}>25 per page</option>
                    <option value={50}>50 per page</option>
                    <option value={100}>100 per page</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    disabled={safePage <= 1}
                    onClick={() => {
                      setPage((p) => Math.max(1, p - 1));
                      window.scrollTo({ top: 300, behavior: "smooth" });
                    }}
                    className="px-3.5 py-1.5 rounded-lg border border-whop-border bg-[#18181B] text-xs font-semibold text-white hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    Previous
                  </button>

                  <div className="flex items-center gap-1">
                    {Array.from({ length: totalPages }, (_, i) => i + 1)
                      .filter((pNum) => pNum === 1 || pNum === totalPages || Math.abs(pNum - safePage) <= 1)
                      .map((pNum, idx, arr) => {
                        const prevNum = arr[idx - 1];
                        const showEllipsis = prevNum && pNum - prevNum > 1;
                        return (
                          <div key={pNum} className="flex items-center gap-1">
                            {showEllipsis && <span className="px-1 text-xs text-zinc-600">…</span>}
                            <button
                              onClick={() => {
                                setPage(pNum);
                                window.scrollTo({ top: 300, behavior: "smooth" });
                              }}
                              className={`h-7 w-7 rounded-lg text-xs font-bold transition ${
                                safePage === pNum
                                  ? "bg-whop-orange text-white"
                                  : "bg-[#18181B] text-zinc-300 hover:bg-zinc-800 border border-whop-border"
                              }`}
                            >
                              {pNum}
                            </button>
                          </div>
                        );
                      })}
                  </div>

                  <button
                    disabled={safePage >= totalPages}
                    onClick={() => {
                      setPage((p) => Math.min(totalPages, p + 1));
                      window.scrollTo({ top: 300, behavior: "smooth" });
                    }}
                    className="px-3.5 py-1.5 rounded-lg border border-whop-border bg-[#18181B] text-xs font-semibold text-white hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="font-display text-xl font-semibold text-white">Live Automation Terminal</h2>
                <p className="text-xs text-whop-mute mt-1">
                  Real-time activity of Whop Bot, outreach actions, and client chatbot processing.
                </p>
              </div>
              <div className="w-full sm:max-w-xs">
                <input
                  type="text"
                  placeholder="Filter terminal output..."
                  value={logSearch}
                  onChange={(e) => setLogSearch(e.target.value)}
                  className="w-full rounded-lg border border-whop-border bg-whop-surface px-4 py-2 text-sm text-white placeholder-zinc-500 focus:border-whop-orange focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div className="rounded-2xl border border-whop-border bg-[#0B0B0C] overflow-hidden flex flex-col">
              {/* Terminal Title Bar */}
              <div className="flex items-center justify-between px-5 py-3.5 bg-[#0F0F11] border-b border-whop-border">
                <div className="flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-whop-orange" />
                  <span className="font-mono text-xs text-white font-semibold">whop-bot-daemon</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[9px] uppercase tracking-wider font-bold bg-green-500/10 text-green-400 border border-green-500/20">
                    <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" /> Live Polling
                  </span>
                  <span className="text-[10px] text-whop-mute font-mono hidden sm:inline">
                    Refreshes every 5s · showing {parsedLogs.length} entries
                  </span>
                </div>
              </div>

              {/* Terminal Viewport */}
              <div className="p-5 font-mono text-[11px] leading-relaxed max-h-[500px] overflow-y-auto bg-[#070708] space-y-1.5 min-h-[300px]">
                {parsedLogs.length === 0 ? (
                  <div className="text-center text-whop-mute py-12">
                    {loadingLogs ? "Loading bot streams..." : "No logs found matching your filter."}
                  </div>
                ) : (
                  parsedLogs.map((line, idx) => {
                    let colorCls = "text-zinc-300";
                    if (line.includes("[ERROR]")) {
                      colorCls = "text-red-400 bg-red-950/20 px-1.5 py-0.5 rounded border border-red-950/40";
                    } else if (line.includes("Success:")) {
                      colorCls = "text-emerald-400 font-medium bg-emerald-950/20 px-1.5 py-0.5 rounded border border-emerald-950/40";
                    } else if (line.includes("[OUTREACH]")) {
                      colorCls = "text-amber-400 bg-amber-950/15 px-1.5 py-0.5 rounded border border-amber-950/30";
                    } else if (line.includes("[CHATBOT]")) {
                      colorCls = "text-cyan-400 bg-cyan-950/10 px-1.5 py-0.5 rounded border border-cyan-950/20";
                    } else if (line.includes("[OAUTH]")) {
                      colorCls = "text-violet-400 bg-violet-950/10 px-1.5 py-0.5 rounded border border-violet-950/20";
                    } else if (line.includes("[DAEMON]")) {
                      colorCls = "text-zinc-400 bg-zinc-950/10 px-1.5 py-0.5 rounded border border-zinc-950/20";
                    }

                    return (
                      <div key={idx} className={`${colorCls} break-all font-mono whitespace-pre-wrap`}>
                        {line}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        )}
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
