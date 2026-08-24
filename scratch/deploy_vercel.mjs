import { spawn } from "child_process";

function runCmd(cmd, args) {
  return new Promise((resolve, reject) => {
    console.log(`\nExecuting: ${cmd} ${args.join(" ")}`);
    const child = spawn(cmd, args, { shell: true });
    child.stdout.on("data", (data) => process.stdout.write(data.toString()));
    child.stderr.on("data", (data) => process.stderr.write(data.toString()));
    child.on("close", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`Command exited with code ${code}`));
    });
  });
}

async function main() {
  try {
    console.log("Step 1: Running vercel build --prod --yes...");
    await runCmd("npx", ["vercel", "build", "--prod", "--yes"]);
    
    console.log("Step 2: Deploying prebuilt bundle to production...");
    await runCmd("npx", ["vercel", "deploy", "--prebuilt", "--prod", "--yes"]);
    
    console.log("🎉 SUCCESS: Deployed to Vercel production successfully!");
  } catch (err) {
    console.error("❌ Deploy error:", err.message);
  }
}

main();
