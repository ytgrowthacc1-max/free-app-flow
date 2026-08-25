async function debugJson(username: string) {
  const res = await fetch(`https://whop.com/@${username}`, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  const html = await res.text();
  const idx = html.indexOf(`"username":"${username}"`);
  if (idx !== -1) {
    console.log(`Found unescaped JSON at index ${idx}:`);
    console.log(html.slice(idx, idx + 250));
  } else {
    console.log(`Unescaped JSON not found.`);
  }

  const escIdx = html.indexOf(`\\"username\\":\\"${username}\\"`);
  if (escIdx !== -1) {
    console.log(`Found escaped JSON at index ${escIdx}:`);
    console.log(html.slice(escIdx, escIdx + 250));
  } else {
    console.log(`Escaped JSON not found.`);
  }
}

debugJson("dwave6f").catch(console.error);
