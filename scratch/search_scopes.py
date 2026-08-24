import os

for root, dirs, files in os.walk("execution"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "scope" in content or "SCOPE" in content:
                print(f"File: {path}")
                # print matching lines
                for line in content.splitlines():
                    if "scope" in line or "SCOPE" in line:
                        print(f"  {line.strip()}")
