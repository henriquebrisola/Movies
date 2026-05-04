import os
import shutil
from pathlib import Path

source_dir = r"E:\Videos\Kill la Kill [1080] - Copy"
files = sorted([f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))])

for i, filename in enumerate(files, 1):
    
    # Create subfolder
    subfolder = os.path.join(source_dir, f"{i:02d}")
    os.makedirs(subfolder, exist_ok=True)
    
    # Move file
    src_path = os.path.join(source_dir, filename)
    dst_path = os.path.join(subfolder, filename)
    shutil.move(src_path, dst_path)
    print(f"Moved {filename} to folder {i}")

print("Done!")
