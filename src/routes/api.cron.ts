import { createFileRoute } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";

export const runCron = createServerFn({ method: "GET" }).handler(async () => {
  try {
    const { tickCron } = await import("@/lib/daemon.server");
    await tickCron();
    return { ok: true, message: "Cron tick completed successfully" };
  } catch (e: any) {
    console.error("[/api/cron] Cron execution error:", e);
    return { ok: false, error: e.message || String(e) };
  }
});

export const Route = createFileRoute("/api/cron")({
  loader: async () => {
    return await runCron();
  },
  component: () => null,
});
