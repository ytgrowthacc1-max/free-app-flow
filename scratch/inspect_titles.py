import os
import sys
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"

# Let's inspect the titles in each creation script
scripts = {
    "deal_gains": "create_deal_gains_network.py",
    "deal_soldier": "create_deal_soldier_network.py",
    "poke_alerts": "create_poke_alerts_network.py",
    "pokepings": "create_pokepings_network.py",
    "crystal_academy": "create_crystal_academy_network.py",
    "official_picks": "create_official_picks_network.py",
    "shocked_vip": "create_shocked_vip_network.py",
    "divine": "create_divine_network.py",
    "tools_pack": "create_tools_pack_network.py",
    "replicate_starred": "replicate_starred_networks.py"
}

for name, sfile in scripts.items():
    spath = os.path.join(base_dir, "execution", sfile)
    if os.path.exists(spath):
        content = open(spath, encoding="utf-8").read()
        # count occurrences of titles
        print(f"--- {name} ({sfile}) ---")
        lines = [line.strip() for line in content.splitlines() if "TITLES" in line or "SECONDARY_TITLES" in line or "TITLES_BY_NICHE" in line]
        for l in lines[:5]:
            print("  ", l)
