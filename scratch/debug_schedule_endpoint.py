import sys
import os

sys.path.append(os.getcwd())
os.environ["WHOP_COMPANY_ID"] = "biz_6rZTzRAkLrBt6H"

import datetime
import json
import traceback

try:
    from execution.dashboard_server import get_scheduler_today_schedule, app
    with app.test_request_context():
        res = get_scheduler_today_schedule()
        print("Response Code:", res.status_code)
        print("Response Body:", res.get_data(as_text=True))
except Exception as e:
    traceback.print_exc()
