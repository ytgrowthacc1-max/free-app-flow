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

const WHOP_API_KEY = process.env.WHOP_API_KEY;

const KNOWN_PRODUCTS = {
  "prod_8p51S4qc6L7Da": "Fast Track app build",
  "prod_0riDXemoZeWWR": "Fast Track app build",
  "prod_BxpjVVFgfadDd": "custom app build",
  "prod_SawduYlhOrXM4": "App Maintenance & Hosting",
  "prod_vAnUY9ZouLS6Q": "App Builders Community",
  "prod_WNwq6UKQBDc6t": "Free App Build",
};

function resolveProductName(payment, productsMap = {}) {
  if (payment.product_id && KNOWN_PRODUCTS[payment.product_id]) {
    return KNOWN_PRODUCTS[payment.product_id];
  }
  if (payment.product_id && productsMap[payment.product_id]) {
    const raw = productsMap[payment.product_id];
    let title = raw.replace(/\[.*?\]/g, "").replace(/\+.*$/g, "").trim();
    if (title.toLowerCase().includes("fast track")) return "Fast Track app build";
    if (title.toLowerCase().includes("custom app")) return "custom app build";
    return title;
  }
  return "custom app build";
}

async function run() {
  // 1. Fetch products map
  const prodRes = await fetch("https://api.whop.com/api/v5/company/products", {
    headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
  });
  const prodJson = await prodRes.json();
  const productsMap = {};
  for (const p of prodJson.data || []) {
    productsMap[p.id] = p.title || p.name;
  }

  // 2. Fetch payments
  const payRes = await fetch("https://api.whop.com/api/v5/company/payments?per=50", {
    headers: { "Authorization": `Bearer ${WHOP_API_KEY}` },
  });
  const payJson = await payRes.json();
  const payments = payJson.data || [];

  const timeoutMs = 5 * 60 * 1000;
  const cutoffTime = Date.now() - timeoutMs;

  const candidates = payments.filter((p) => {
    const isFailedOrIncomplete = p.status !== "paid" || p.payments_failed > 0 || p.paid_at === null;
    const hasUser = !!p.user_id;
    const createdAtMs = (p.created_at || 0) * 1000;
    const passedGracePeriod = createdAtMs < cutoffTime;
    return isFailedOrIncomplete && hasUser && passedGracePeriod;
  });

  console.log(`Found ${candidates.length} candidate payment(s):`);
  for (const payment of candidates) {
    const isCardDecline = payment.payments_failed > 0 || payment.payment_method_type === "card";
    const failureMode = isCardDecline ? "failed_card" : "incomplete_checkout";
    
    const displayName = payment.billing_address?.name 
      ? payment.billing_address.name.split(" ")[0]
      : (payment.user_username || "there");
    
    const productName = resolveProductName(payment, productsMap);

    let text = "";
    if (failureMode === "failed_card") {
      text = `hey ${displayName}, noticed your payment for the ${productName} had an issue going through. did your card get declined or did you run into any errors at checkout?`;
    } else {
      text = `hey ${displayName}, saw you started checking out for the ${productName} but didn't finish. did you get stuck on anything or have any questions?`;
    }

    console.log("\n------------------------------------------------");
    console.log(`User: @${payment.user_username} (${payment.user_id}) | Product: ${productName} | Mode: ${failureMode}`);
    console.log(`Message: "${text}"`);
  }
}

run();
