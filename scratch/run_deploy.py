import subprocess
import os

print("Running deployment in c:/Python/Health_APP_WHOP...")
res = subprocess.run("deploy.bat", cwd="c:/Python/Health_APP_WHOP", shell=True)
print("Finished with exit code:", res.returncode)
if res.returncode != 0:
    exit(res.returncode)
