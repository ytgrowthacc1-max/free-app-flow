import requests

r = requests.get('http://127.0.0.1:8080/api/profiles')
bots = r.json()
first_bot = next((b for b in bots if b.get('companies')), None)
if first_bot:
    bot_id = first_bot['bot_user_id']
    comp_id = first_bot['companies'][0]['company_id']
    print(f'Testing switch to bot {bot_id} and comp {comp_id}...')
    
    resp = requests.post('http://127.0.0.1:8080/api/select_profile', json={'bot_user_id': bot_id, 'company_id': comp_id})
    print('Status:', resp.status_code)
    print('Response:', resp.json())
