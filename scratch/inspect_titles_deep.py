import os
import sys
import json
import re

base_dir = r"c:\Python\WHOP AUTOMATION AGENTIC"
exec_dir = os.path.join(base_dir, "execution")

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
    spath = os.path.join(exec_dir, s)
    with open(spath, "r", encoding="utf-8") as f:
        code = f.read()
    
    # search for lists of titles
    match = re.findall(r'(\w+TITLES\w*|\w+BY_NICHE)\s*=\s*(\[.*?\]|\{.*?\})', code, re.DOTALL)
    print(f"=== {s} ===")
    for varname, val in match:
        print(f"  Var: {varname} (length in chars: {len(val)})")
