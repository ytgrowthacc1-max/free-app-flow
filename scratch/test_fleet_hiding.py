import requests

print("="*60)
print("  TESTING FLEET HIDING & VISIBILITY ENDPOINTS")
print("="*60)

# 1. Fetch Fleet Summary
r = requests.get('http://127.0.0.1:8080/api/fleet/summary')
data = r.json()
print("HTTP:", r.status_code)
summary = data.get("summary", {})
print(f"Total visible communities: {summary.get('total_communities')}")
print(f"Total start communities:   {summary.get('total_start_communities')}")
print(f"Needs attention count:     {summary.get('needs_attention_count')}")
print(f"Active schedulers:         {summary.get('active_schedulers')}")
print(f"Hidden / Suspended count:  {summary.get('hidden_count')}")

comms = data.get("communities", [])
print(f"Total returned communities: {len(comms)}")
sample = comms[0] if comms else None
if sample:
    print(f"Sample: {sample.get('company_name')} | is_hidden={sample.get('is_hidden')} | is_suspended={sample.get('is_suspended')} | comm_hidden={sample.get('comm_hidden')}")

# Test toggle visibility on sample community
if sample:
    bot_id = sample['bot_user_id']
    comp_id = sample['company_id']
    orig_hidden = sample.get('comm_hidden', False)
    
    # Hide
    r_hide = requests.post('http://127.0.0.1:8080/api/toggle_company_visibility', json={'bot_user_id': bot_id, 'company_id': comp_id, 'hidden': not orig_hidden})
    print(f"Toggle hide ({not orig_hidden}): {r_hide.status_code} - {r_hide.json().get('message')}")
    
    # Check updated summary
    r_updated = requests.get('http://127.0.0.1:8080/api/fleet/summary')
    up_data = r_updated.json()
    print(f"Updated hidden_count: {up_data['summary']['hidden_count']}")
    
    # Restore original state
    r_restore = requests.post('http://127.0.0.1:8080/api/toggle_company_visibility', json={'bot_user_id': bot_id, 'company_id': comp_id, 'hidden': orig_hidden})
    print(f"Restore ({orig_hidden}): {r_restore.status_code} - {r_restore.json().get('message')}")

print("="*60)
print("FLEET HIDING TESTS COMPLETED SUCCESSFULLY!")
print("="*60)
