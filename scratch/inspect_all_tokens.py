import os
import json
import base64

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bots_dir = os.path.join(base_dir, "profiles", "bots")

def decode_jwt_payload(token):
    try:
        parts = token.split('.')
        if len(parts) == 3:
            payload_b64 = parts[1]
            # Add padding if necessary
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            return json.loads(payload_bytes.decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}
    return None

if os.path.exists(bots_dir):
    for bot_id in os.listdir(bots_dir):
        bot_path = os.path.join(bots_dir, bot_id)
        if not os.path.isdir(bot_path):
            continue
        pfile = os.path.join(bot_path, "profile.json")
        if os.path.exists(pfile):
            with open(pfile, "r", encoding="utf-8") as f:
                pdata = json.load(f)
            token = pdata.get("oauth_token", "")
            username = pdata.get("bot_username", bot_id)
            if token:
                payload = decode_jwt_payload(token)
                if payload:
                    print(f"Bot: @{username}")
                    print(f"  Scopes: {payload.get('scope')}")
                else:
                    print(f"Bot: @{username} | Token decode failed")
else:
    print("No bots folder found.")
