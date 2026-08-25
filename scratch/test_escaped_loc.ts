async function testEscapedProfileLocation(username: string) {
  const res = await fetch(`https://whop.com/@${username}`, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  if (!res.ok) return null;
  const html = await res.text();

  // Match escaped or unescaped country and city near user object
  const countryMatch = html.match(/\\?"country\\?"\s*:\s*\\?"([A-Z]{2})\\?"/);
  const cityMatch = html.match(/\\?"city\\?"\s*:\s*\\?"([^\\"]+)\\?"/);

  const country = countryMatch ? countryMatch[1] : null;
  const city = cityMatch && cityMatch[1] !== "null" ? cityMatch[1] : null;

  return { username, country, city };
}

async function main() {
  const users = ["dwave6f", "townhall", "gtron", "iamrohit7", "founder-cca", "matteoriva", "shnayderman", "harviee"];
  for (const u of users) {
    const res = await testEscapedProfileLocation(u);
    console.log(res);
  }
}

main().catch(console.error);
