async function testWhopProfileEarnings(username) {
  const cleanUser = username.replace(/^@/, "").trim();
  const url = `https://whop.com/@${cleanUser}`;
  try {
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      }
    });
    if (!res.ok) return { username: cleanUser, status: res.status };
    const html = await res.text();
    
    // 1. Badge match: ($X,XXX Earned)
    const badgeMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i);
    // 2. Exact USD match
    const usdMatch = html.match(/totalEarningsWithTransfersInUsd:"([\d\.]+)"/);
    
    return {
      username: cleanUser,
      badge: badgeMatch ? badgeMatch[1] : null,
      exact_usd: usdMatch ? parseFloat(usdMatch[1]) : null,
    };
  } catch (e) {
    return { username: cleanUser, error: e.message };
  }
}

async function main() {
  const users = ["townhall", "cuguyever", "lonewolf1956", "swaruppande", "appdevelopment"];
  for (const u of users) {
    const res = await testWhopProfileEarnings(u);
    console.log(`User @${u}:`, res);
  }
}

main();
