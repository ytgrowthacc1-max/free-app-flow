import re

def main():
    with open(".tmp/full_rsc_payload.txt", "r", encoding="utf-8") as f:
        payload = f.read()
        
    pos = payload.find('"memberCount":1082')
    if pos != -1:
        start = max(0, pos - 150)
        end = min(len(payload), pos + 500)
        print("Context around memberCount 1082:")
        print(payload[start:end])
    else:
        print("Not found")

if __name__ == "__main__":
    main()
