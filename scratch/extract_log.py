import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
brain_dir = r"C:\Users\Eridas\.gemini\antigravity\brain"
for conv_id in os.listdir(brain_dir):
    conv_path = os.path.join(brain_dir, conv_id, ".system_generated", "logs", "overview.txt")
    if os.path.exists(conv_path):
        with open(conv_path, "r", encoding="utf-8") as f:
            for line in f:
                if ".env" in line and "CodeContent" in line:
                    try:
                        data = json.loads(line)
                        calls = data.get("tool_calls", [])
                        for call in calls:
                            if call.get("name") in ["write_to_file", "replace_file_content", "multi_replace_file_content"]:
                                args = call.get("args", {})
                                if ".env" in args.get("TargetFile", "") or ".env" in args.get("TargetContent", ""):
                                    print(f"Conv {conv_id} step {data.get('step_index')}:")
                                    print(args)
                                    print("-" * 50)
                    except Exception:
                        pass
