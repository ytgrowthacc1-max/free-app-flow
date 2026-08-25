import fs from "fs";

async function inspectProfileHtml(username: string) {
  const res = await fetch(`https://whop.com/@${username}`, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  const html = await res.text();
  console.log(`=== HTML for @${username} (Length: ${html.length}) ===`);
  
  // Save html snippet around Earned
  const idx = html.indexOf("Earned");
  if (idx !== -1) {
    console.log("Snippet around 'Earned':");
    console.log(html.slice(Math.max(0, idx - 200), Math.min(html.length, idx + 200)));
  } else {
    console.log("'Earned' not found in HTML.");
  }

  // Look for totalEarnings
  const eIdx = html.indexOf("totalEarnings");
  if (eIdx !== -1) {
    console.log("Snippet around 'totalEarnings':");
    console.log(html.slice(Math.max(0, eIdx - 100), Math.min(html.length, eIdx + 200)));
  } else {
    console.log("'totalEarnings' not found in HTML.");
  }
}

async function main() {
  await inspectProfileHtml("townhall");
  await inspectProfileHtml("amirjandm");
}

main().catch(console.error);
