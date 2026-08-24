import os
import sys
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
bots_dir = os.path.join(base_dir, "profiles", "bots")

# We will collect/build the titles for each of the 10 niches:
# 1. Revenue Apps
# 2. XP Arena
# 3. The Tools Pack
# 4. Flip Empire
# 5. Cash City Picks
# 6. Deal Gains
# 7. Deal Soldier
# 8. Poke Alerts
# 9. Crystal Academy Hub
# 10. Official Picks VIP

NICHE_CONFIGS = {
    "Revenue Apps": {
        "src_bot": "user_eSN5Z4XrLT0ZQ",
        "src_comp": "biz_VHlv37S71ESE1G",
        "master_title": "Revenue Apps VIP",
        "titles": [
            "Revenue App Hub", "Custom App Money", "App Builders Vault", "NoCode Revenue Bot",
            "SaaS Builder Pass", "App Profit Radar", "Micro SaaS Vault", "AI App Money",
            "NoCode App Hub", "Build Free App", "Revenue SaaS Bot", "App Cash Flow",
            "Custom SaaS Pass", "NoCode Profit Hub", "App Builder Alpha", "Zero Code Apps",
            "SaaS Revenue Vault", "App Money Radar", "NoCode Cash Bot", "Custom App Pass",
            "SaaS Profit Radar", "Revenue App Vault", "NoCode SaaS Hub", "App Cash Radar",
            "Custom App Radar", "SaaS Builder Hub", "NoCode Money Bot", "App Revenue Pass",
            "Custom SaaS Hub", "NoCode Builder Vault", "App Profit Vault", "SaaS Cash Bot",
            "Revenue Builder Hub", "NoCode App Vault", "Custom App Cash", "SaaS Money Pass",
            "App Revenue Radar", "NoCode Profit Pass", "Custom SaaS Vault", "SaaS Builder Radar"
        ]
    },
    "XP Arena": {
        "src_bot": "user_lO14mFc5tBKN3",
        "src_comp": "biz_pV1MfpPbaGydou",
        "master_title": "XP Arena VIP",
        "titles": [
            "XP Arena Hub", "Leaderboard XP Pass", "Community Rewards Bot", "Gamified XP Vault",
            "Whop XP Radar", "Member Retention Hub", "XP Rewards Pass", "Gamification Vault",
            "Streak XP Bot", "Leaderboard Alpha", "Whop Retention Radar", "Community XP Hub",
            "Member XP Pass", "Gamified Growth Bot", "XP System Vault", "Whop Rewards Hub",
            "Retention XP Pass", "Leaderboard Vault Bot", "Community Gamification", "XP Growth Hub",
            "Whop XP Pass", "Member Rewards Bot", "Gamified Retention", "XP Leaderboard Hub",
            "Retention Rewards Pass", "Whop Growth Bot", "Community XP Vault", "Gamified Member Hub",
            "XP Retention Bot", "Leaderboard Growth Pass", "Whop Rewards Radar", "Member Gamification",
            "XP System Hub", "Retention Alpha Bot", "Leaderboard XP Vault", "Whop Member Pass",
            "Community Rewards Hub", "Gamified XP Pass", "Whop Retention Hub", "XP Growth Radar"
        ]
    },
    "The Tools Pack": {
        "src_bot": "user_UCUWNo0s132ET",
        "src_comp": "biz_c9ai0lCMJoCw9e",
        "master_title": "The Tools Pack VIP",
        "titles": [
            "Tools Pack Hub", "Tool Suite Pass", "App Bundle Bot", "Software Tool Vault",
            "AI Tool Radar", "SaaS Bundle Pass", "Creator Tools Hub", "Dev Tool Vault",
            "Software Stack Bot", "Tool Suite Radar", "AI Stack Pass", "App Bundle Hub",
            "Creator Stack Vault", "Dev Tool Radar", "SaaS Tool Pass", "Tools Pack Vault",
            "AI Suite Bot", "Software Bundle Hub", "Creator Tool Pass", "Dev Stack Vault",
            "Tool Stack Radar", "App Suite Hub", "SaaS Stack Pass", "Tools Pack Bot",
            "AI Bundle Vault", "Software Suite Pass", "Creator Tool Radar", "Dev Suite Bot",
            "Tool Pack Vault", "App Stack Pass", "SaaS Suite Hub", "Tools Pack Radar",
            "AI Tool Pass", "Software Pack Vault", "Creator Stack Bot", "Dev Tool Hub",
            "Tool Suite Vault", "App Pack Radar", "SaaS Bundle Vault", "Tools Pack Alpha"
        ]
    },
    "Flip Empire": {
        "src_bot": "user_puyTsi9E4vLkP",
        "src_comp": "biz_LK1qoXTov4CsLA",
        "master_title": "Flip Empire VIP",
        "titles": [
            "Flip Empire Hub", "Price Glitch Radar", "Resell Flip Pass", "Divine Free Pass",
            "Bulk Buy Bot", "Retail Glitch Hub", "ACO Bot Vault", "Sneaker Flip Radar",
            "Ticket Resell Pass", "Divine Pro Hub", "Price Error Bot", "Ecom Flip Vault",
            "Retail Arbitrage Pass", "Glitch Sniper Radar", "Divine Trial Pass", "Bulk Buy Vault",
            "Resell Alpha Hub", "Price Glitch Bot", "Flip Profit Pass", "Divine Empire Hub",
            "Retail Glitch Vault", "ACO Flip Radar", "Sneaker Resell Bot", "Ticket Flip Hub",
            "Price Error Pass", "Ecom Glitch Bot", "Divine Signals Vault", "Bulk Buy Pass",
            "Resell Flip Radar", "Glitch Sniper Hub", "Divine Free Vault", "Retail Flip Bot",
            "ACO Pass Radar", "Sneaker Glitch Pass", "Ticket Resell Vault", "Price Glitch Hub",
            "Ecom Profit Radar", "Divine Alpha Pass", "Bulk Deal Vault", "Flip Mastermind Pass"
        ]
    },
    "Cash City Picks": {
        "src_bot": "user_HVCjzjUye5q5I",
        "src_comp": "biz_IR9QwwEFeC199z",
        "master_title": "Cash City VIP",
        "titles": [
            "Cash City Hub", "Sports Picks Pass", "Betting Signal Bot", "Cash Pick Radar",
            "EV Betting Vault", "Arbitrage Picks Pass", "Win Rate Radar", "Vegas Picks Hub",
            "Betting Alpha Pass", "Cash City Radar", "Daily Pick Bot", "EV Sports Hub",
            "Betting Arbitrage Vault", "Win Signal Pass", "Cash City VIP", "Vegas Line Radar",
            "Sports Bet Vault", "EV Pick Radar", "Cash City Pass", "Betting Signal Hub",
            "Win Rate Pass", "Vegas Sports Bot", "Cash City Vault", "EV Betting Hub",
            "Sports Pick Radar", "Betting Alpha Vault", "Cash City Bot", "Vegas Pick Pass",
            "Win Signal Hub", "EV Sports Radar", "Cash City Alpha", "Betting Line Pass",
            "Sports Arbitrage Bot", "Vegas Line Vault", "Cash Pick Pass", "EV Win Radar",
            "Betting Cash Hub", "Vegas Signal Bot", "Sports Win Vault", "Cash City Signals"
        ]
    },
    "Deal Gains": {
        "src_bot": "user_PUpL8cbyE1Zf2",
        "src_comp": "biz_62x0KF1HwUkUd2",
        "master_title": "Deal Gains Pass",
        "titles": [
            "Deal Gains Hub", "Price Error Alerts", "Amazon Glitch Finder", "Target Clearance Bot",
            "Walmart Hidden Deals", "Freebie Alert Radar", "Retail Arbitrage Pass", "Reselling Profit Hub",
            "Flipping Deals Vault", "Daily Bargain Hunter", "Price Mistake Alerts", "Ecom Profit Radar",
            "Deal Sniper Pro", "Discount Glitch Bot", "Penny Items Radar", "Clearance Finders Hub",
            "Hidden Savings Club", "Amazon Promo Codes", "Cashback Stacking VIP", "Fast Flip Signals",
            "Retail Glitch Alerts", "Bargain Hunter VIP", "Secret Deals Radar", "Wholesale Profit Hub",
            "Arbitrage Glitch Bot", "Price Drop Sniper", "Resell Ninja Radar", "Discount Hunters Club",
            "Clearance King Hub", "Retail Savings Pass", "Promo Glitch Finder", "Fast Flip Radar",
            "Penny Deal Alerts", "Flipping Profit Bot", "Deal Gains Radar", "Price Error VIP",
            "Amazon Steals Hub", "Target Glitch Bot", "Walmart Deals Radar", "Hidden Clearance Pass"
        ]
    },
    "Deal Soldier": {
        "src_bot": "user_mnR4EbynVY8UA",
        "src_comp": "biz_Epy3Gq1LkscDbI",
        "master_title": "Deal Soldier Hub",
        "titles": [
            "Deal Soldier Hub", "Price Glitch Alerts", "Retail Arbitrage Pass", "Deal Sniper VIP",
            "Bargain Hunter Bot", "Clearance Finders", "Hidden Deals Vault", "Daily Resell Radar",
            "Amazon Promo Finder", "Target Clearance Pass", "Walmart Glitch Alerts", "Freebie Alerts Pro",
            "Flipping Profits Hub", "Retail Discount Bot", "Price Drop Signals", "Penny Items Hub",
            "Cashback Stacker Pass", "Deal Soldier VIP", "Discount Glitch Radar", "Reseller Signals Bot",
            "Fast Flip Alpha", "Secret Deals Club", "Arbitrage Master Pass", "Price Mistake Radar",
            "Clearance Sniper Bot", "Retail Savings Hub", "Bargain Hunter Pass", "Promo Code VIP",
            "Wholesale Deals Radar", "Ecom Flip Bot", "Deal Soldier Pass", "Price Error Hub",
            "Discount Hunter Pro", "Resell Profit Alerts", "Flipping Deals Hub", "Amazon Steals Radar",
            "Target Glitch Pass", "Walmart Deals Bot", "Hidden Savings Radar", "Fast Cash Deals"
        ]
    },
    "Poke Alerts": {
        "src_bot": "user_VXlrbVwms4laY",
        "src_comp": "biz_3wuSbLPNZb4mU7",
        "master_title": "Poke Alerts Hub",
        "titles": [
            "Poke Alerts Hub", "Pokemon Restock Pass", "TCG Card Radar", "Pokemon Drops Bot",
            "Card Grading Alerts", "Pokemon Card Deals", "TCG Restock Sniper", "Pokemon Booster Pass",
            "Collector Glitch Alerts", "Pokemon Alpha Radar", "TCG Card Hub", "Charizard Restock Bot",
            "Pokemon Card Vault", "TCG Drop Radar", "Pokemon Resell Pass", "Card Flip Alerts",
            "Pokemon Restock VIP", "TCG Deal Sniper", "Poke Drops Pass", "Pokemon Box Radar",
            "TCG Investor Hub", "Pokemon Card VIP", "Restock Sniper Bot", "Poke Card Alerts",
            "TCG Arbitrage Pass", "Pokemon Value Radar", "Collector Drop Bot", "Poke Hunter Hub",
            "Pokemon Restock Bot", "TCG Profit Pass", "Poke Alerts VIP", "Card Sniper Radar",
            "Pokemon Pack Bot", "TCG Restock Hub", "Poke Investor Pass", "Pokemon Drops VIP",
            "Collector Restock Radar", "TCG Card Sniper", "Pokemon Restock Pass", "Poke Alpha Hub"
        ]
    },
    "Crystal Academy Hub": {
        "src_bot": "user_lMrwnvtkSSp6w",
        "src_comp": "biz_wIrZm2C9eZmsFB",
        "master_title": "Crystal Academy Hub",
        "titles": [
            "Crystal Academy Hub", "Daily Crystal Signals", "Crypto Alpha Pass", "Solana Gems Radar",
            "Memecoin Signals Bot", "Whale Tracker VIP", "Crypto Trading Hub", "DeFi Yield Radar",
            "Token Launch Alerts", "Crypto Sniper Bot", "Memecoin Alpha Pass", "Crypto Blueprint Hub",
            "Solana Sniper Radar", "Crypto Signals VIP", "Daily Crypto Locks", "DeFi Alpha Pass",
            "Whale Signals Bot", "Crypto Moonshot Radar", "Token Gems Hub", "Crypto Scalp Pass",
            "Memecoin Sniper VIP", "Solana Profit Bot", "Crypto Alpha Vault", "DeFi Strategy Hub",
            "Daily Token Alerts", "Crypto Wealth Pass", "Whale Buy Radar", "Memecoin Signals Hub",
            "Crypto Trading VIP", "Solana Launch Bot", "Token Alpha Radar", "Crypto Sniper Pass",
            "DeFi Profit Hub", "Memecoin Trade Bot", "Crypto Gains Radar", "Solana Gems Pass",
            "Daily Crypto Alpha", "Whale Tracker Pass", "Token Scalp Bot", "Crystal Crypto VIP"
        ]
    },
    "Official Picks VIP": {
        "src_bot": "user_pdd7UFzVXqlg4",
        "src_comp": "biz_06H1NGZWgkCioO",
        "master_title": "Official Picks Pass",
        "titles": [
            "Official Picks Hub", "Daily Sports Locks", "VIP Parlay Radar", "High Win-Rate Pass",
            "EV Betting Bot", "Sports Handicapper Pass", "Daily Value Bets", "Sharp Money Alerts",
            "Prop Betting Academy", "Bankroll Growth Hub", "Sports Lock Bot", "VIP Lock Channel",
            "Live In-Play Alerts", "Pick City Radar", "NBA Player Props", "NFL Betting Locks",
            "MLB Betting Radar", "NHL Puck Line Pass", "Soccer Match Locks", "Esports Betting Locks",
            "Tennis Bet Radar", "Golf PGA Picks", "College Hoops Radar", "Underdog Fantasy Props",
            "PrizePicks Lock Bot", "Chalkboard Pick Alerts", "Betting Blueprint Pass", "Winning Slip Radar",
            "Live Odds Tracker", "Same Game Parlays", "No-Stress Bankroll Pass", "Daily Parlay Pass",
            "Sports Betting Vault", "Arbitrage Win Bot", "Vegas Line Radar", "Sports Alpha Hub",
            "VIP Match Locks", "Daily Edge Bot", "Handicap Win Pass", "Official Picks VIP"
        ]
    }
}

for niche, cfg in NICHE_CONFIGS.items():
    titles = cfg["titles"]
    print(f"[{niche}] count={len(titles)} titles. Validating word count <= 3:")
    for idx, t in enumerate(titles, 1):
        words = t.split()
        if len(words) > 3:
            print(f"  WARNING: Title too long ({len(words)} words): '{t}' -> trimmed: '{' '.join(words[:3])}'")
            cfg["titles"][idx-1] = " ".join(words[:3])

print("All 10 niche title sets validated successfully!")
