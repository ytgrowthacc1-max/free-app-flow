async function testProfileLocationScrape(username: string) {
  const res = await fetch(`https://whop.com/@${username}`, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  if (!res.ok) return console.log(`Failed to fetch @${username}: status ${res.status}`);
  const html = await res.text();
  console.log(`Fetched @${username}, HTML length: ${html.length}`);

  // Search for "Dubai", "AE", "United Arab Emirates", "location", "country", "city"
  const keywords = ["Dubai", "United Arab Emirates", "location", "country", "city"];
  for (const kw of keywords) {
    const idx = html.indexOf(kw);
    if (idx !== -1) {
      console.log(`\nFound keyword "${kw}" at index ${idx}:`);
      console.log(html.slice(Math.max(0, idx - 100), Math.min(html.length, idx + 250)));
    } else {
      console.log(`Keyword "${kw}" NOT found.`);
    }
  }
}

testProfileLocationScrape("dwave6f").catch(console.error);
