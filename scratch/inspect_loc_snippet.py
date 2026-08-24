import requests
import re
import sys

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
r = requests.get("https://whop.com/@bonnielau", headers=headers)
html = r.text

match = re.search(r'.{0,60}Shah Alam.{0,60}', html)
if match:
    print("Found snippet:", match.group(0))
else:
    print("Not found")

r2 = requests.get("https://whop.com/@dariuslewis32", headers=headers)
match2 = re.search(r'.{0,60}New Caney.{0,60}', r2.text)
if match2:
    print("Found snippet 2:", match2.group(0))
