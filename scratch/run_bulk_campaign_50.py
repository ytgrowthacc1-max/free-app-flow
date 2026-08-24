import subprocess
import sys
import os
from dotenv import load_dotenv

def main():
    # Load .env variables
    load_dotenv(override=True)
    
    # Lock company ID to Best Offers (biz_R3lCX4ljztxERk) as instructed
    company_id = "biz_R3lCX4ljztxERk"
    api_key = os.getenv("WHOP_COMPANY_API_KEY") or os.getenv("WHOP_API_KEY")
    
    if not api_key:
        print("[ERROR] WHOP_COMPANY_API_KEY/WHOP_API_KEY not found in .env")
        sys.exit(1)
        
    print(f"[INFO] Using Sending Company ID: {company_id}")

    # Exact user copy with "only $29.95/mo."
    message_text = (
        "Your activity reward!\n"
        "ToolSuite is giving acces to 50+ premium ecommerce, AI, design, and creator tools only $29.95/mo. "
        "If you’re paying for tools like Pipiads, PPSpy, HeyGen, Captions.ai, or Canva Pro separately (full list bellow), this can cut a lot of monthly cost.\n"
        "Grab your exclusive deal here (available 24h):\n"
        "https://whop.com/toolsuite/buy-vip?a=bigwlt"
    )
    
    cmd = [
        "python",
        "execution/member_outreach_pipeline.py",
        "--target", "studydropshipping",
        "--limit-scrape", "600",
        "--limit-outreach", "50",
        "--single-bubble",
        "--no-typos",
        "--image-url", "https://img-v2-prod.whop.com/unsafe/rs:fit:3840:0/plain/https%3A%2F%2Fassets-2-prod.whop.com%2Fpublic%2Fuploads%2Fuser_18307343%2Fimage%2Fbots%2F2026-07-04%2F1478690a-92c5-449e-b4ec-0bc5e044a495.png@avif?w=3840&q=75",
        "--message", message_text,
        "--company-id", company_id,
        "--api-key", api_key,
        "--send"
    ]
    
    print("[INFO] Launching member outreach pipeline for 50 more users...")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    for line in p.stdout:
        print(line.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'), end="")
    p.wait()
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
