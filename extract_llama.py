import sys
import zipfile
import os

zip_path = sys.argv[1]
dest_dir = sys.argv[2]

z = zipfile.ZipFile(zip_path)
z.extractall(dest_dir)

# Check that llama-cli.exe ended up somewhere
exe_path = os.path.join(dest_dir, "llama-cli.exe")
if not os.path.exists(exe_path):
    # Might be in a subfolder
    for root, dirs, files in os.walk(dest_dir):
        for f in files:
            if f.lower() == "llama-cli.exe":
                src = os.path.join(root, f)
                os.replace(src, exe_path)
                break

if os.path.exists(exe_path):
    print("Extracted llama-cli.exe with DLLs")
else:
    print("ERROR: llama-cli.exe not found in archive")
    sys.exit(1)
