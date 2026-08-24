import os
import sys
import json
import time

try:
    from execution.create_company import create_company
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execution.create_company import create_company

communities = [
    {
        "title": "Whop Gamification Hub",
        "description": "Gamify your Whop community with the Whop Engagement Leaderboard App. Reward active members with real-time XP for posting, commenting, and daily check-in streaks."
    },
    {
        "title": "Community Retention Secrets",
        "description": "Stop member churn and increase monthly retention! Learn how daily check-in streaks and XP leaderboards keep paid subscribers active month after month."
    },
    {
        "title": "Trading Engagement XP",
        "description": "Keep your trading signals group active! Reward members with level cards and daily return streaks when they chat, engage, and complete courses."
    },
    {
        "title": "Betting Leaderboard Hub",
        "description": "Boost sports betting community retention! Use automated XP leaderboards and daily login streaks to reward your top handicappers and active bettors."
    },
    {
        "title": "Course Creators Growth",
        "description": "Triple your course completion rates! Reward students with level-up cards and XP badges for completing lessons, asking questions, and checking in daily."
    },
    {
        "title": "Daily Checkin Streaks",
        "description": "Give members a reason to open your Whop community every day! Implement daily check-in streaks and level multipliers to drive maximum DAU."
    },
    {
        "title": "Reselling Cook Groups",
        "description": "Turn your reselling cook group into a competitive arena! Reward members for posting win flips, chatting, and returning daily with real-time XP ranks."
    },
    {
        "title": "Crypto XP System",
        "description": "Gamify your crypto and Web3 hub. Reward active holders and community members with dynamic rank cards, level progression, and engagement leaderboards."
    },
    {
        "title": "Skool Alternative Growth",
        "description": "Moving from Skool to Whop? Get the exact gamification features, level-up cards, and engagement leaderboards your members loved on Skool right inside Whop."
    },
    {
        "title": "Fitness Challenge Leaderboard",
        "description": "Keep your fitness and coaching clients accountable! Track daily check-in streaks, award workout XP, and highlight top members on dynamic leaderboards."
    },
    {
        "title": "App Builders Network",
        "description": "Connect with top Whop app builders and learn how to integrate engagement leaderboards, XP systems, and custom gamification plugins into your products."
    },
    {
        "title": "Discord Activity Gamification",
        "description": "Maximize activity across Whop and Discord! Reward active chatters, forum posters, and course learners with automated XP and leaderboard rankings."
    },
    {
        "title": "Subscriber Retention Hub",
        "description": "Increase your Daily Active Users (DAU) effortlessly. Harness leaderboard competition and streak multipliers to turn casual members into superfans."
    },
    {
        "title": "VIP Fan Leaderboard",
        "description": "Give your VIP fans an interactive experience! Reward superfans with exclusive ranks, level progression, and leaderboard recognition for supporting your content."
    },
    {
        "title": "Mastermind Accountability Hub",
        "description": "Drive high-ticket client success and accountability! Implement structured check-in streaks, level milestones, and engagement leaderboards for your mastermind."
    },
    {
        "title": "AI Automation Network",
        "description": "Scale your AI and automation community with automated gamification! Award member XP for sharing prompts, workflow tips, and completing daily check-ins."
    },
    {
        "title": "Superfan Rewards Hub",
        "description": "Empower your community moderators and top contributors! Use custom XP values to reward constructive posts, answers, and daily active participation."
    },
    {
        "title": "Affiliate Growth Leaderboard",
        "description": "Motivate your affiliates and promoters! Display real-time activity leaderboards and reward top advocates for bringing in new members and driving engagement."
    },
    {
        "title": "Real Estate Leaderboards",
        "description": "Activate your real estate deal-finding network! Reward investors and wholesalers for submitting deal flow, commenting on listings, and daily check-ins."
    },
    {
        "title": "Whop Leaderboard App",
        "description": "Explore the official Whop Engagement Leaderboard App! Learn how to install, configure XP points, and turn your Whop community into a gamified ecosystem."
    }
]

def main():
    print(f"Starting batch creation of {len(communities)} communities for @dawnmuros...\n")
    results = []
    
    os.makedirs(".tmp", exist_ok=True)

    bot_user_id = "user_lO14mFc5tBKN3"

    for idx, c in enumerate(communities, 1):
        print(f"[{idx}/{len(communities)}] Creating: '{c['title']}'...")
        res = create_company(title=c["title"], description=c["description"], bot_user_id=bot_user_id)
        
        if res.get("success"):
            print(f"   [SUCCESS] Company ID: {res.get('company_id')} | Route: {res.get('route')}")
            results.append({"status": "success", "title": c["title"], "company_id": res.get("company_id"), "route": res.get("route")})
        else:
            print(f"   [FAILED] Error: {res.get('error')}")
            results.append({"status": "failed", "title": c["title"], "error": res.get("error")})
            
        time.sleep(0.5)

    print("\n--- Summary Report ---")
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"Successfully Created: {success_count}/{len(communities)}")
    
    with open(".tmp/created_communities_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
