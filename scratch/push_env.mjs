import fs from "fs";
import { execSync } from "child_process";

const envStr = fs.readFileSync(".env", "utf8");
const lines = envStr.split("\n");

for (const line of lines) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith("#")) continue;
  
  const [key, ...rest] = trimmed.split("=");
  let val = rest.join("=");
  
  // Strip quotes if they exist
  if (val.startsWith('"') && val.endsWith('"')) {
    val = val.slice(1, -1);
  }
  
  try {
    console.log(`Adding ${key}...`);
    // Remove it first just in case
    try {
      execSync(`npx vercel env rm ${key} production preview development --yes`, { stdio: "ignore" });
    } catch {}
    
    // Write value to temp file to avoid echo parsing issues on Windows
    fs.writeFileSync("temp_val.txt", val, "utf8");
    execSync(`npx vercel env add ${key} production preview development < temp_val.txt`, { stdio: "inherit", shell: "cmd.exe" });
  } catch (err) {
    console.error(`Failed to add ${key}:`, err.message);
  }
}
try { fs.unlinkSync("temp_val.txt"); } catch {}
console.log("Done!");
