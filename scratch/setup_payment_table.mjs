import { createClient } from "@supabase/supabase-js";
import fs from "fs";
import path from "path";

// Load .env
const envPath = path.resolve(".env");
if (fs.existsSync(envPath)) {
  const content = fs.readFileSync(envPath, "utf-8");
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf("=");
    if (idx > 0) {
      const k = trimmed.slice(0, idx).trim();
      let v = trimmed.slice(idx + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      process.env[k] = v;
    }
  }
}

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: { persistSession: false },
});

async function setup() {
  console.log("Creating payment_recovery table in Supabase...");
  const sql = `
    CREATE TABLE IF NOT EXISTS public.payment_recoveries (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      payment_id text UNIQUE NOT NULL,
      whop_user_id text NOT NULL,
      whop_username text,
      email text,
      amount numeric,
      currency text,
      failure_mode text,
      status text,
      channel_id text,
      message_sent boolean DEFAULT false,
      message_content text,
      created_at timestamptz DEFAULT now(),
      notified_at timestamptz
    );
    CREATE INDEX IF NOT EXISTS idx_payment_recoveries_payment_id ON public.payment_recoveries(payment_id);
    CREATE INDEX IF NOT EXISTS idx_payment_recoveries_user_id ON public.payment_recoveries(whop_user_id);
  `;

  const { data, error } = await supabase.rpc("exec_sql", { sql });
  if (error) {
    console.error("RPC exec_sql error:", error);
  } else {
    console.log("Table setup successful via RPC exec_sql:", data);
  }
}

setup();
