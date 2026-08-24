import os

tmp_dir = ".tmp"
if os.path.exists(tmp_dir):
    print("Files in .tmp:")
    for file in os.listdir(tmp_dir):
        path = os.path.join(tmp_dir, file)
        if os.path.isfile(path):
            print(f"  {file} ({os.path.getsize(path)} bytes)")
        else:
            print(f"  {file} [DIR]")
else:
    print(".tmp directory does not exist.")
