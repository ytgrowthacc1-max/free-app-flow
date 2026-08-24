import os
import sys
import requests
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

app_builders_key = "apik_sOHFFQbgZP82T_A2060239_C_f334e3d0b0c93ecc38a05aae8841163a296df059c1f0298cc53d959252a708"
company_id = "biz_78VckYvrZN8g34" # Pick City
target_user_id = "user_fdWsHxrBCGa62"

headers = {
    "Authorization": f"Bearer {app_builders_key}",
    "Content-Type": "application/json"
}

# 1. Create support channel using app_builders key
url_chan = "https://api.whop.com/api/v1/support_channels"
payload_chan = {
    "company_id": company_id,
    "user_id": target_user_id
}

print(f"=== Creating Support Channel for Pick City via app_builders key (app_8hnbfm1jmFsDa2) ===")
res_chan = requests.post(url_chan, headers=headers, json=payload_chan, timeout=10)
print(f"Channel Creation HTTP Status {res_chan.status_code}: {res_chan.text}")

if res_chan.status_code in [200, 201]:
    chan_id = res_chan.json().get("id")
    print(f"\n[SUCCESS] Support Channel ready for app_builders: {chan_id}")
    
    # 2. Send message
    message_text = (
        "Most betting groups are quiet when they lose and loud when they win. Pick City is the opposite — we post everything.\n\n"
        "That's why 3,300+ bettors moved here and never left. Funniest chat, realest numbers, perfect 5.0 rating from 1,200+ people who don't give charity reviews.\n\n"
        "One week, $19.99. You'll see why:\n"
        "https://whop.com/pickcity/weekly-95/?a=bigwlt\n\n"
        "Thank me later."
    )
    
    url_msg = "https://api.whop.com/api/v1/messages"
    payload_msg = {"channel_id": chan_id, "content": message_text}
    
    res_msg = requests.post(url_msg, headers=headers, json=payload_msg, timeout=10)
    print(f"Message Send HTTP Status {res_msg.status_code}: {res_msg.text}")
    if res_msg.status_code in [200, 201]:
        data = res_msg.json()
        uinfo = data.get("user") or {}
        print(f"\n🎉 SUCCESS! Delivered via app_builders Support App!")
        print(f"   Message ID: {data.get('id')}")
        print(f"   Sender User ID: {uinfo.get('id')}")
        print(f"   Sender Name/Username: {uinfo.get('name')} (@{uinfo.get('username')})")
