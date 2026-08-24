import os
import json
import requests

headers = {'User-Agent': 'Mozilla/5.0'}
base = 'profiles'
for root, dirs, files in os.walk(base):
    if 'company.json' in files:
        fp = os.path.join(root, 'company.json')
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cid = data.get('company_id')
        cname = data.get('company_name', cid)
        if cid:
            try:
                res = requests.get(f'https://api.whop.com/api/v1/companies/{cid}', headers=headers, timeout=8)
                if res.status_code == 200:
                    cinfo = res.json()
                    route = cinfo.get('route')
                    if route:
                        data['route'] = route
                        data['whop_url'] = f'https://whop.com/joined/{route}/'
                        with open(fp, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2)
                        print(f"[OK] {cname:<25} ({cid}) -> Route: {route}")
                    else:
                        print(f"[NO ROUTE FIELD] {cname} ({cid})")
                else:
                    print(f"[HTTP {res.status_code}] {cname} ({cid})")
            except Exception as e:
                print(f"[ERROR] {cname} ({cid}): {e}")
