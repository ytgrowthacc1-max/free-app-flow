import os, json

base = 'profiles'
found = []
for root, dirs, files in os.walk(base):
    if 'company.json' in files:
        fp = os.path.join(root, 'company.json')
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        found.append((data.get('company_id', ''), data.get('company_name', ''), data.get('route', 'NO_ROUTE'), fp))

for cid, cname, route, fp in sorted(found, key=lambda x: x[1]):
    print(f"{cid:<22} | {cname:<25} | {route:<20} | {fp}")
