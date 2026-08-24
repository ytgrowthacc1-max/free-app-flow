async function scrapePublicWhopProfile(username) {
  if (!username) return null;
  const clean = username.replace(/^@/, "").trim().toLowerCase();
  if (!clean || ["anonymous", "unknown", "null", "undefined"].includes(clean)) return null;

  try {
    const url = `https://whop.com/@${clean}`;
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
    });

    if (!res.ok) return null;
    const html = await res.text();

    const countryMatch = html.match(/"country":\s*"([A-Z]{2})"/i) || html.match(/\\"country\\":\s*\\"([A-Z]{2})\\"/i) || html.match(/country["']?\s*:\s*["']?([A-Z]{2})["']?/i);
    const cityMatch = html.match(/"city":\s*"([^"]+)"/i) || html.match(/\\"city\\":\s*\\"([^\\"]+)\\"/i);
    const earnedMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i);

    const country = countryMatch ? countryMatch[1].toUpperCase() : null;
    const city = cityMatch && cityMatch[1] !== "City" ? cityMatch[1] : null;
    const public_earnings_badge = earnedMatch ? earnedMatch[1] : null;

    return {
      username: clean,
      country,
      city,
      public_earnings_badge,
    };
  } catch (err) {
    console.error(`[scrapePublicWhopProfile] Error for @${clean}:`, err);
    return null;
  }
}

async function run() {
  const users = ["bonnielau", "dariuslewis32", "moxyalili", "jack", "townhall", "scalewdreww", "hitman28", "abbasieman"];
  for (const u of users) {
    const data = await scrapePublicWhopProfile(u);
    console.log(`@${u}:`, data);
  }
}

run();
