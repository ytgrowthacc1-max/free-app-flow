import subprocess
import sys

def main():
    message_text = (
        "Your activity reward!\n"
        "ToolSuite is giving acces to 50+ premium ecommerce, AI, design, and creator tools for $29.95/mo. "
        "If you’re paying for tools like Pipiads, PPSpy, HeyGen, Captions.ai, or Canva Pro separately (full list bellow), this can cut a lot of monthly cost.\n"
        "Grab your exclusive deal here (available 24h):\n"
        "https://whop.com/toolsuite/buy-vip?a=bigwlt"
    )
    
    cmd = [
        "python",
        "execution/bulk_outreach.py",
        "--members", ".tmp/test_member_bigw.json",
        "--single-bubble",
        "--image-url", "https://img-v2-prod.whop.com/unsafe/rs:fit:3840:0/plain/https%3A%2F%2Fassets-2-prod.whop.com%2Fpublic%2Fuploads%2Fuser_18307343%2Fimage%2Fbots%2F2026-07-04%2F1478690a-92c5-449e-b4ec-0bc5e044a495.png@avif?w=3840&q=75",
        "--message", message_text,
        "--no-typos",
        "--send"
    ]
    
    print("[INFO] Launching bulk_outreach.py programmatically...")
    # Run and print output live
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    for line in p.stdout:
        print(line.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'), end="")
    p.wait()
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
