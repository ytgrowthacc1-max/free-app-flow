import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "execution"))

from provision_batch2_networks import BATCH2_SPECIFICATIONS

all_ok = True

for spec in BATCH2_SPECIFICATIONS:
    idx = spec["index"]
    user = spec["username"]
    master = spec["master_title"]
    secs = spec["secondary_titles"]
    
    print(f"[{idx}] @{user} - Master: '{master}' - {len(secs)} secondaries")
    
    if len(secs) != 40:
        print(f"  [ERROR] Expected 40 secondaries, got {len(secs)}")
        all_ok = False
        
    seen = set([master.lower()])
    for s in secs:
        words = s.split()
        if len(words) > 3:
            print(f"  [ERROR] Title > 3 words: '{s}'")
            all_ok = False
        if s.lower() in seen:
            print(f"  [ERROR] Duplicate title or matches master: '{s}'")
            all_ok = False
        seen.add(s.lower())

if all_ok:
    print("\n[SUCCESS] All titles across all 10 bots in Batch 2 are 100% valid (<= 3 words, strictly unique)!")
