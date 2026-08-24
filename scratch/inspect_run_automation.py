import inspect
import sys
import os

sys.path.append(os.path.abspath("execution"))
import run_automation

print(inspect.getsource(run_automation.get_active_profiles))
