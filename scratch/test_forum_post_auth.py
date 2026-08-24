import sys
sys.path.insert(0, r"c:\Python\WHOP AUTOMATION AGENTIC\execution")
from post_to_forum import post_to_forum

bot_id = "user_gAkQk98I3AyP4" # @donnajacksona7
exp_id = "exp_JKTV9iWwQSkA9P" # One of the 40 new public forums

print("Testing post creation on new forum experience...")
res = post_to_forum(
    experience_id=exp_id,
    content="This is a test broadcast post for the new SaaS Tool Bundle Hub community.",
    title="[TEST] Shared Tool Pass Update",
    bot_user_id=bot_id
)

if res:
    print(f"POST CREATION SUCCESS! Post ID: {res.get('id')}")
else:
    print("POST CREATION FAILED")
