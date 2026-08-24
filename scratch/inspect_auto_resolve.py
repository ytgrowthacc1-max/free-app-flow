import inspect
import sys
import os

sys.path.append(os.path.abspath("execution"))
import dashboard_server

print(inspect.getsource(dashboard_server.auto_resolve_active_profile))
