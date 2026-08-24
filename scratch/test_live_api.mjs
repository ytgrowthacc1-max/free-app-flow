import fs from "fs";
import path from "path";

const envPath = path.resolve(".env");
let adminPw = "";
if (fs.existsSync(envPath)) {
  const content = fs.readFileSync(envPath, "utf-8");
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (trimmed.startsWith("ADMIN_PASSWORD=")) {
      adminPw = trimmed.split("=")[1].trim();
      if ((adminPw.startsWith('"') && adminPw.endsWith('"')) || (adminPw.startsWith("'") && adminPw.endsWith("'"))) {
        adminPw = adminPw.slice(1, -1);
      }
    }
  }
}

async function testLiveApi() {
  console.log("Testing live server function /_server/?_serverFnId=adminListLeads with pw:", adminPw ? "OK" : "MISSING");
  
  // Test both GET and POST to TanStack Start server function
  const res = await fetch("https://free-app-flow.vercel.app/_server/?_serverFnId=adminListLeads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: adminPw })
  });

  console.log("Live API response status:", res.status, res.statusText);
  const text = await res.text();
  console.log("Live API response preview:", text.slice(0, 300));
}

testLiveApi();
