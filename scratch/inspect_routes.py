import inspect
import sys
import os

sys.path.append(os.path.abspath("execution"))
import dashboard_server

fname = "import_bot_and_companies"
if hasattr(dashboard_server, fname):
    print(inspect.getsource(getattr(dashboard_server, fname)))
else:
    print(f"Function {fname} not found")
