const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '..', '.env');
if (!fs.existsSync(envPath)) {
  console.error('.env file not found');
  process.exit(1);
}

const content = fs.readFileSync(envPath, 'utf-8');
const lines = content.split(/\r?\n/);

const envs = ['production', 'preview', 'development'];

function setEnv(key, val, env) {
  return new Promise((resolve, reject) => {
    const child = spawn('npx', ['vercel', 'env', 'add', key, env, '--yes', '--force'], {
      shell: true
    });
    
    child.stdin.write(val);
    child.stdin.end();
    
    let errData = '';
    child.stderr.on('data', (data) => {
      errData += data.toString();
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(errData || `Exit code ${code}`));
      }
    });
  });
}

async function run() {
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const index = trimmed.indexOf('=');
    if (index > 0) {
      const key = trimmed.slice(0, index).trim();
      let val = trimmed.slice(index + 1).trim();
      
      // Unquote value
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      
      console.log(`Setting environment variable: ${key}...`);
      // Run environments in parallel for this key
      await Promise.all(envs.map(async (env) => {
        try {
          await setEnv(key, val, env);
          console.log(`  ✓ ${env}`);
        } catch (err) {
          console.error(`  ✗ ${env}:`, err.message);
        }
      }));
    }
  }
  console.log('All environment variables synchronized to Vercel!');
}

run();
