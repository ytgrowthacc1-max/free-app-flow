import os

execution_dir = 'execution'
for fn in os.listdir(execution_dir):
    if fn.endswith('.py'):
        path = os.path.join(execution_dir, fn)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if 'playwright' in content.lower() or 'selenium' in content.lower() or 'webdriver' in content.lower():
            print(f"File {fn} uses browser automation!")
