import os

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = "bigwlt"
    
    print(f"[INFO] Scanning workspace directory '{root_dir}' for '{target}'...")
    
    for root, dirs, files in os.walk(root_dir):
        # Skip directories we don't care about
        if any(d in root for d in [".git", "__pycache__", ".venv", "node_modules"]):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if target.lower() in content.lower():
                        # Find matching line numbers
                        lines = content.splitlines()
                        for idx, line in enumerate(lines):
                            if target.lower() in line.lower():
                                print(f"[MATCH] {os.path.relpath(file_path, root_dir)}:L{idx+1} -> {line.strip()}")
            except Exception as e:
                pass

if __name__ == "__main__":
    main()
