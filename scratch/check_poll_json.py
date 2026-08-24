import os
import sys
import requests
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "execution"))
from whop_auth import get_fresh_token

load_dotenv()

def main():
    token = get_fresh_token()
    headers = {"Authorization": f"Bearer {token}"}
    post_id = "post_1Cc8GyP11LHWaXTXFK6Lq1"
    
    # We don't know the exact experience ID it was created in, let's try exp_RpQSciawxkuJlm or public
    exp_ids = ["exp_RpQSciawxkuJlm", os.getenv("WHOP_EXPERIENCE_ID")]
    
    for exp_id in exp_ids:
        if not exp_id:
            continue
        url = f"https://api.whop.com/api/v1/forum_posts/{post_id}"
        params = {"experience_id": exp_id}
        
        print(f"Fetching {post_id} details in {exp_id}...")
        r = requests.get(url, headers=headers, params=params)
        print("Status:", r.status_code)
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
            break
        else:
            print("Error:", r.text)

if __name__ == "__main__":
    main()
