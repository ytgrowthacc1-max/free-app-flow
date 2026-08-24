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

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const WHOP_API_KEY = process.env.WHOP_API_KEY;
const WHOP_COMPANY_ID = process.env.WHOP_COMPANY_ID;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false },
});

async function dryRunPaymentRecovery() {
  console.log("Starting dry-run check of payment recovery...");
  const res = await fetch(`https://api.whop.com/api/v5/company/payments?per=50`, {
    headers: {
      "Authorization": `Bearer ${WHOP_API_KEY}`,
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    console.error("Failed to fetch payments:", res.status);
    return;
  }

  const json = await res.json();
  const payments = json.data || [];
  const timeoutMs = 5 * 60 * 1000;
  const cutoffTime = Date.now() - timeoutMs;

  const candidatePayments = payments.filter((p) => {
    const isFailedOrIncomplete = p.status !== "paid" || p.payments_failed > 0 || p.paid_at === null;
    const hasUser = !!p.user_id;
    const createdAtMs = (p.created_at || 0) * 1000;
    const passedGracePeriod = createdAtMs < cutoffTime;
    return isFailedOrIncomplete && hasUser && passedGracePeriod;
  });

  console.log(`Found ${candidatePayments.length} candidate payment(s) in latest page:`);
  for (const payment of candidatePayments) {
    const isCardDecline = payment.payments_failed > 0 || payment.payment_method_type === "card";
    const failureMode = isCardDecline ? "failed_card" : (payment.payment_method_type === "crypto" ? "crypto_pending" : "incomplete_checkout");
    
    const displayName = payment.billing_address?.name 
      ? payment.billing_address.name.split(" ")[0]
      : (payment.user_username || "there");
    
    const amountStr = payment.final_amount > 0 ? `$${payment.final_amount}` : (payment.subtotal > 0 ? `$${payment.subtotal}` : "");
    
    let text = "";
    if (failureMode === "failed_card") {
      text = `hey ${displayName}, noticed your recent payment${amountStr ? ` of ${amountStr}` : ""} had an issue going through. did your card get declined or did you run into any errors at checkout?`;
    } else {
      text = `hey ${displayName}, saw you started checking out${amountStr ? ` for ${amountStr}` : ""} but didn't finish. did you get stuck on anything or have any questions?`;
    }

    console.log(`\n[Candidate Payment]`);
    console.log(`- ID: ${payment.id}`);
    console.log(`- User: @${payment.user_username} (${payment.user_id})`);
    console.log(`- Email: ${payment.user_email}`);
    console.log(`- Failure Mode: ${failureMode}`);
    console.log(`- Proposed Support Message:\n  "${text}"`);
  }

  // Test reading from Supabase payment_recoveries table
  const { data: dbRecords, error: dbErr } = await supabase
    .from("payment_recoveries")
    .select("*")
    .limit(5);

  if (dbErr) {
    console.error("Supabase payment_recoveries query error:", dbErr);
  } else {
    console.log("\nSupabase payment_recoveries table connectivity confirmed. Current records:", dbRecords.length);
  }
}

dryRunPaymentRecovery();
