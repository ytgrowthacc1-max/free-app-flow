import os
import re

for root, dirs, files in os.walk("execution"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "def get_active_profiles" in content:
                print(f"Defined in: {path}")
