import urllib.request
import os

url = "https://i.pinimg.com/736x/63/28/72/632872572a42b592a342ae2488f49c73.jpg"
os.makedirs(".tmp", exist_ok=True)
dest = os.path.abspath(".tmp/profile_pic.jpg")

req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
    out_file.write(response.read())

print("Downloaded profile picture to:", dest, "Size:", os.path.getsize(dest))
