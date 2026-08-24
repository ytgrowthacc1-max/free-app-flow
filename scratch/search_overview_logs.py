import os
import json

log_path = r"C:\Users\Eridas\.gemini\antigravity\brain\e466a01f-64cb-449e-9a2b-12a59f5a9d75\.system_generated\logs\overview.txt"

if os.path.exists(log_path):
    print("Parsing logs...")
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                obj = json.loads(line)
                # Print user input or model tools/outputs if they mention "outreach" or "bigwlt"
                text = str(obj.get("content", "")) + str(obj.get("tool_calls", ""))
                if "python" in text.lower() and "bulk" in text.lower():
                    print(f"Step {obj.get('step_index')}: {text[:150]}")
                # If there are command outputs
                if obj.get("type") == "COMMAND_EXECUTION_RESULT":
                    output = obj.get("output", "")
                    if "outreach" in output.lower() or "successful" in output.lower():
                        print(f"Output of Step {obj.get('step_index')}: {output[:200]}")
            except Exception:
                pass
