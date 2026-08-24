import requests

def main():
    try:
        res = requests.get('http://localhost:8080/api/profiles').json()
        print(f"Loaded {len(res)} profiles from API:")
        print("-" * 60)
        for b in res:
            print(f"Bot: {b['bot_username']} ({b['bot_user_id']})")
            print(f"  Status: {b['status']}")
            print(f"  Credentials Valid: {b['credentials_valid']}")
            print(f"  Active for Interactions: {b['interaction_active']}")
            print(f"  Is Main: {b['is_main_account']}")
            print("-" * 60)
    except Exception as e:
        print(f"Error fetching profiles: {e}")

if __name__ == "__main__":
    main()
