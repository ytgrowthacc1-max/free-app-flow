import { spawn } from "child_process";
import fs from "fs";
import path from "path";

// Load .env
const envPath = path.resolve(process.cwd(), ".env");
if (fs.existsSync(envPath)) {
  const content = fs.readFileSync(envPath, "utf8");
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx > 0) {
      const key = trimmed.slice(0, eqIdx).trim();
      const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, "");
      if (!process.env[key]) process.env[key] = val;
    }
  }
}

function runCmd(cmd, args) {
  return new Promise((resolve, reject) => {
    console.log(`\nExecuting: ${cmd} ${args.join(" ")}`);
    const child = spawn(cmd, args, { shell: true, env: process.env });
    child.stdout.on("data", (data) => process.stdout.write(data.toString()));
    child.stderr.on("data", (data) => process.stdout.write(data.toString()));
    child.on("close", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`Command exited with code ${code}`));
    });
  });
}

async function main() {
  try {
    const tokenArgs = process.env.VERCEL_TOKEN ? ["--token", process.env.VERCEL_TOKEN] : [];

    console.log("Step 1: Running vercel build --prod --yes...");
    await runCmd("npx", ["vercel", "build", "--prod", "--yes", ...tokenArgs]);
    
    console.log("Step 2: Deploying prebuilt bundle to production...");
    await runCmd("npx", ["vercel", "deploy", "--prebuilt", "--prod", "--yes", ...tokenArgs]);
    
    console.log("🎉 SUCCESS: Deployed to Vercel production successfully!");
  } catch (err) {
    console.error("❌ Deploy error:", err.message);
  }
}

main();
