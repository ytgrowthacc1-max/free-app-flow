import os
import shutil

def migrate():
    source_files = [
        "pending_actions.json",
        "dashboard_chats_cache.json",
        "processed_messages.json",
        "followup_state.json",
        "reactivation_log.json",
        "posted_forum_history.json"
    ]
    
    app_builders_id = "biz_Vwsite2gfnFBU2"
    
    for filename in source_files:
        src_path = os.path.join(".tmp", filename)
        if os.path.exists(src_path):
            base, ext = os.path.splitext(filename)
            dest_path = os.path.join(".tmp", f"{base}_{app_builders_id}{ext}")
            shutil.copy(src_path, dest_path)
            print(f"[SUCCESS] Copied {src_path} -> {dest_path}")
        else:
            print(f"[INFO] Source file {src_path} does not exist. Skipping.")

if __name__ == "__main__":
    migrate()
