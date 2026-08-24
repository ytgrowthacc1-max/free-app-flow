import fs from "fs";
import path from "path";

async function scrapeWhopEarnings(username) {
  if (!username) return null;
  const clean = username.replace(/^@/, "").trim();
  if (!clean || ["anonymous", "unknown", "null", "undefined"].includes(clean.toLowerCase())) return null;

  try {
    const url = `https://whop.com/@${clean}`;
    const res = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      },
    });

    if (!res.ok) return null;
    const html = await res.text();

    const badgeMatch = html.match(/(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i);
    const usdMatch = html.match(/totalEarningsWithTransfersInUsd:"([\d\.]+)"/i) || html.match(/"totalEarningsWithTransfersInUsd":\s*"?([\d\.]+)"?/i);

    const badge = badgeMatch ? badgeMatch[1] : null;
    const exactUsd = usdMatch ? parseFloat(usdMatch[1]) : null;

    return {
      username: clean,
      badge,
      exactUsd,
    };
  } catch (err) {
    console.error(`[scrapeWhopEarnings] Error for @${clean}:`, err.message);
    return null;
  }
}

async function main() {
  const sampleUsernames = ["hitman28", "abbasieman", "weishenkan", "dariuslewis32"];
  for (const u of sampleUsernames) {
    const result = await scrapeWhopEarnings(u);
    console.log(`@${u}:`, result);
  }
}

main();
