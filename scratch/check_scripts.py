import os
import sys
import json

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
scripts = [
    "create_deal_gains_network.py",
    "create_deal_soldier_network.py",
    "create_poke_alerts_network.py",
    "create_pokepings_network.py",
    "create_crystal_academy_network.py",
    "create_official_picks_network.py",
    "create_shocked_vip_network.py",
    "create_divine_network.py",
    "create_tools_pack_network.py",
    "replicate_starred_networks.py"
]

for s in scripts:
    spath = os.path.join(base_dir, "execution", s)
    if os.path.exists(spath):
        print(f"Found {s} ({os.path.getsize(spath)} bytes)")
