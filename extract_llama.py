import sys
import zipfile
import os

zip_path = sys.argv[1]
dest_dir = sys.argv[2]

z = zipfile.ZipFile(zip_path)
for name in z.namelist():
    if "llama-cli.exe" in name.lower():
        z.extract(name, dest_dir)
        src = os.path.join(dest_dir, name)
        dst = os.path.join(dest_dir, "llama-cli.exe")
        os.replace(src, dst)
        print("Extracted llama-cli.exe")
        break
