async function testProfileDataExtraction(username: string) {
  const res = await fetch(`https://whop.com/@${username}`, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  if (!res.ok) return null;
  const html = await res.text();

  // 1. Extract Country & City from JSON: "country":"AE","city":"Dubai" or "country":"US"
  const countryMatch = html.match(/"username"\s*:\s*"[^"]+"\s*,\s*"bio"\s*:[^}]*?"country"\s*:\s*"(?:null|([A-Z]{2}))"\s*,\s*"city"\s*:\s*"(?:null|([^"]+))"/);
  
  // Or general regex for country and city near username
  const countryMatch2 = html.match(/"country"\s*:\s*"(?:null|([A-Z]{2}))"\s*,\s*"city"\s*:\s*"(?:null|([^"]+))"/);
  const countryMatch3 = html.match(/"country"\s*:\s*"([A-Z]{2})"/);
  const cityMatch3 = html.match(/"city"\s*:\s*"([^"]+)"/);

  // 2. Extract Earnings Badge
  const badgeMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--[\s\S]*?-->\s*)*Earned/i);
  const usdMatch = html.match(/totalEarningsWithTransfersInUsd:"([\d\.]+)"/);

  const country = countryMatch3 ? countryMatch3[1] : null;
  const city = cityMatch3 && cityMatch3[1] !== "null" ? cityMatch3[1] : null;
  const badge = badgeMatch ? badgeMatch[1] : (usdMatch ? `$${parseFloat(usdMatch[1]).toLocaleString("en-US", { minimumFractionDigits: 2 })}` : null);

  return { username, country, city, badge };
}

async function main() {
  const users = ["dwave6f", "townhall", "gtron", "iamrohit7", "founder-cca", "matteoriva"];
  for (const u of users) {
    const res = await testProfileDataExtraction(u);
    console.log(res);
  }
}

main().catch(console.error);
