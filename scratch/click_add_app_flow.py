import os
import sys
import time
import json

sys.path.append(r"C:\Python\Browsing Skill Agent\execution")
import profile_db as db
from browser_manager import BrowserManager

profile = None
for p in db.list_profiles(platform="whop"):
    if p.get("account_number") == 54 or "dawnmuros" in str(p).lower():
        profile = p
        break

app_url = "https://whop.com/apps/app_tHhlowWfWKDkIF/"

with BrowserManager(profile, headless=True) as browser:
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("[INFO] Navigating to app store page...")
    page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    
    # Click 'Add' button
    add_btn = page.locator("button:has-text('Add'), a:has-text('Add')").first
    print("[INFO] Clicking 'Add' button...")
    add_btn.click()
    time.sleep(4)
    
    os.makedirs(".tmp/screenshots", exist_ok=True)
    page.screenshot(path=".tmp/screenshots/after_add_click.png")
    
    print("URL after click:", page.url)
    print("Page Title:", page.title())
    
    # Check dialog / modal options
    print("Modal text content:", page.locator("body").inner_text()[:1000])
    
    # Look for company select buttons or options inside modal
    options = page.locator("[role='option'], [role='button'], button, a").all_inner_texts()
    print("Available Interactive Elements:", options[:30])
    
    # If company option exists, click the first company
    company_item = page.locator("div:has-text('biz_'), [role='option'], button:has-text('Whop Leaderboard App'), button:has-text('Select')").first
    if company_item.count() > 0 and company_item.is_visible():
        print("[INFO] Clicking company selection...")
        company_item.click()
        time.sleep(3)
        page.screenshot(path=".tmp/screenshots/after_company_select.png")
        
    # Check for confirm / install button inside modal
    confirm_btn = page.locator("button:has-text('Install'), button:has-text('Add'), button:has-text('Continue'), button:has-text('Authorize')").last
    if confirm_btn.count() > 0 and confirm_btn.is_visible():
        print("[INFO] Clicking confirm/install button...")
        confirm_btn.click()
        time.sleep(5)
        page.screenshot(path=".tmp/screenshots/after_confirm.png")
        print("Final URL:", page.url)
