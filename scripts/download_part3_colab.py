"""
========================================
COLAB: Download, unzip Part 3, delete archive
========================================

Copy this entire cell into Colab. Mount Drive first.
Extracts to /content/drive/MyDrive/Oil_Spill (creates Images/ and Mask/ from Part3)
"""

from google.colab import drive
drive.mount('/content/drive')

import os
import shutil
import requests
import subprocess

# ========== CONFIG ==========
ZENODO_RECORD = "13761290"  # Part 3
DEST_BASE = "/content/drive/MyDrive/Oil_Spill"
WORK_DIR = "/content/part3_temp"

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(DEST_BASE, exist_ok=True)

# 1. Get download URL from Zenodo API
print("Fetching Part 3 file info from Zenodo...")
r = requests.get(f"https://zenodo.org/api/records/{ZENODO_RECORD}")
r.raise_for_status()
data = r.json()
files = data.get("files", [])
if not files:
    print("No files in record. Check Zenodo record ID.")
else:
    # Use first file (usually the main archive)
    f = files[0]
    url = f["links"]["self"]
    fname = f["key"]
    size_gb = f.get("size", 0) / (1024**3)
    print(f"File: {fname} ({size_gb:.1f} GB)")
    print(f"URL: {url}")

    # 2. Download
    archive_path = os.path.join(WORK_DIR, fname)
    print("\nDownloading (this may take a while)...")
    cmd = ["wget", "-O", archive_path, "-q", "--show-progress", url]
    subprocess.run(cmd, check=True)

    # 3. Extract
    print("\nExtracting...")
    if fname.endswith(".7z"):
        subprocess.run(["pip", "install", "-q", "py7zr"], check=True)
        import py7zr
        with py7zr.SevenZipFile(archive_path, "r") as z:
            z.extractall(path=WORK_DIR)
    elif fname.endswith(".zip"):
        subprocess.run(["unzip", "-o", archive_path, "-d", WORK_DIR], check=True)
    else:
        print("Unsupported format. Extract manually.")
        exit(1)

    # 4. Find Images/ and Mask/ in extracted tree, move to Oil_Spill
    dest_img = os.path.join(DEST_BASE, "Images")
    dest_msk = os.path.join(DEST_BASE, "Mask")
    if os.path.exists(dest_img):
        shutil.rmtree(dest_img)
    if os.path.exists(dest_msk):
        shutil.rmtree(dest_msk)
    # Try known Part3 layouts
    candidates = [
        os.path.join(WORK_DIR, "02_Test_images_and_ground_truth"),
        os.path.join(WORK_DIR, "Part3", "02_Test_images_and_ground_truth"),
        WORK_DIR,
    ]
    src_img = src_msk = None
    for cand in candidates:
        pi = os.path.join(cand, "Images")
        pm = os.path.join(cand, "Mask")
        if os.path.isdir(pi) and os.path.isdir(pm):
            src_img, src_msk = pi, pm
            break
    if src_img:
        shutil.move(src_img, dest_img)
        shutil.move(src_msk, dest_msk)
        print(f"Moved Part3 Images & Mask -> {DEST_BASE}")
    else:
        print("Extracted layout unknown. Contents:", os.listdir(WORK_DIR))

    # 5. Delete archive
    os.remove(archive_path)
    print("Deleted archive.")

# 6. Cleanup temp
shutil.rmtree(WORK_DIR, ignore_errors=True)
print("Done.")
