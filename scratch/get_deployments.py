import subprocess

def get_deployments():
    cmd = ["npx", "wrangler", "pages", "deployment", "list", "--project-name=health-app-whop"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=r"c:\Python\WHOP AUTOMATION AGENTIC", shell=True, encoding="utf-8")
    with open("scratch/deployments.txt", "w", encoding="utf-8") as f:
        f.write(res.stdout)
    print("Done")

if __name__ == "__main__":
    get_deployments()
