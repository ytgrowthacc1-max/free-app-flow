import os
import re

def main():
    brain_dir = r"C:\Users\Eridas\.gemini\antigravity\brain"
    found = 0
    for conv_id in os.listdir(brain_dir):
        conv_path = os.path.join(brain_dir, conv_id, ".system_generated", "logs", "overview.txt")
        if os.path.exists(conv_path):
            try:
                with open(conv_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if "WHOP_API_KEY" in line or "CORTEX_API_KEY" in line:
                            # Extract potential keys/env content
                            clean_line = line.strip()
                            # Print matching context
                            print(f"Conv {conv_id} line {i+1}:")
                            print(clean_line[:300])
                            print("-" * 60)
                            found += 1
            except Exception as e:
                pass
    print(f"Total matches found: {found}")

if __name__ == "__main__":
    main()
