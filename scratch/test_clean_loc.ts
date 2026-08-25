function extractLocationFromProfileHtml(html: string, username: string) {
  const unameStr = `\\"username\\":\\"${username.toLowerCase()}\\"`;
  let idx = html.toLowerCase().indexOf(unameStr);
  if (idx === -1) {
    // try unescaped
    const unameStr2 = `"username":"${username.toLowerCase()}"`;
    idx = html.toLowerCase().indexOf(unameStr2);
  }
  if (idx === -1) return { country: null, city: null };

  const snippet = html.slice(idx, idx + 500);

  const countryMatch = snippet.match(/\\?"country\\?"\s*:\s*\\?"([A-Z]{2})\\?"/);
  const cityMatch = snippet.match(/\\?"city\\?"\s*:\s*\\?"([^\\"]+)\\?"/);

  const country = countryMatch ? countryMatch[1] : null;
  let city = cityMatch ? cityMatch[1] : null;
  if (city === "null" || city === "undefined") city = null;

  return { country, city };
}

async function testUser(username: string) {
  const res = await fetch(`https://whop.com/@${username}`, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  if (!res.ok) return null;
  const html = await res.text();
  return extractLocationFromProfileHtml(html, username);
}

async function main() {
  const users = ["dwave6f", "townhall", "gtron", "iamrohit7", "founder-cca", "matteoriva", "shnayderman", "harviee"];
  for (const u of users) {
    const loc = await testUser(u);
    console.log(`@${u.padEnd(15)} -> Country: ${loc?.country || 'NONE'} | City: ${loc?.city || 'NONE'}`);
  }
}

main().catch(console.error);
