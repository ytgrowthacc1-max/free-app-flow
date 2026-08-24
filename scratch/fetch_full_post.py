import os
import sys
import requests
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))
from whop_auth import get_fresh_token

load_dotenv()

def main():
    token = get_fresh_token() # get current token
    headers = {"Authorization": f"Bearer {token}"}
    
    posts = ["post_1Ccw72vtpnGLTJmrtyoxUT", "post_1Ccw7Z3hZDrv8izt7rJThh"]
    exp_id = "exp_KgzMrM89tl4khe"
    
    for pid in posts:
        url = f"https://api.whop.com/api/v1/forum_posts/{pid}"
        params = {"experience_id": exp_id}
        
        print(f"\n================ Fetching {pid} ================")
        r = requests.get(url, headers=headers, params=params)
        print("Status:", r.status_code)
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print("Error:", r.text)

if __name__ == "__main__":
    main()
