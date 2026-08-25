async function locateBadge() {
  const res = await fetch("https://whop.com/@townhall", {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
  });
  const html = await res.text();
  const target = "$2,719.35";
  let pos = 0;
  while ((pos = html.indexOf(target, pos)) !== -1) {
    console.log(`\nMatch for "${target}" at index ${pos}:`);
    console.log(html.slice(Math.max(0, pos - 200), Math.min(html.length, pos + 200)));
    pos += target.length;
  }
}

locateBadge().catch(console.error);
