"""
========================================
RUN THIS IN COLAB TO ADD PART3 (TEST) ONLY
========================================

Use this if you already ran the full script and train/val are done,
but Part3 (test) had 0 pairs. This adds test images from Images/ + Mask/ only.
"""

from google.colab import drive
drive.mount('/content/drive')

import os
import shutil
from tqdm import tqdm

SOURCE = "/content/drive/MyDrive/Oil_Spill"
DEST = "/content/drive/MyDrive/oil_spill_Final"  # Your existing reorganized folder

def find_pairs(img_dir, mask_dir, mask_suffix="_segmentation"):
    """Match images (00000.tif) with masks (00000_segmentation.tif) within same subdir.
    Oil/00082.tif pairs with Mask/Oil/00082_segmentation.tif (not Lookalike or No oil)."""
    pairs = []
    exts = ('.tif', '.tiff', '.jpg', '.jpeg', '.png')
    if not os.path.exists(img_dir) or not os.path.exists(mask_dir):
        return pairs
    mask_map = {}  # key = (subdir, img_base) e.g. ("Oil", "00082")
    for r, _, fs in os.walk(mask_dir):
        rel = os.path.relpath(r, mask_dir)
        if rel == ".":
            rel = ""
        for f in fs:
            if any(f.lower().endswith(e) for e in exts):
                base = os.path.splitext(f)[0]
                img_key = base.replace(mask_suffix, "") if mask_suffix and mask_suffix in base else base
                mask_map[(rel, img_key)] = os.path.join(r, f)
    for r, _, fs in os.walk(img_dir):
        rel = os.path.relpath(r, img_dir)
        if rel == ".":
            rel = ""
        for f in fs:
            if any(f.lower().endswith(e) for e in exts):
                name = os.path.splitext(f)[0]
                key = (rel, name)
                if key in mask_map:
                    pairs.append((os.path.join(r, f), mask_map[key]))
    return pairs

def move_pairs(pairs, dest_split):
    dest_img = os.path.join(dest_split, 'images')
    dest_msk = os.path.join(dest_split, 'masks')
    os.makedirs(dest_img, exist_ok=True)
    os.makedirs(dest_msk, exist_ok=True)
    for i, (img, msk) in enumerate(tqdm(pairs, desc="test")):
        base, ext = os.path.splitext(os.path.basename(img))
        msk_ext = os.path.splitext(os.path.basename(msk))[1] or '.png'
        u = f"{i:06d}_{base}"
        shutil.move(img, os.path.join(dest_img, u + ext))
        shutil.move(msk, os.path.join(dest_msk, u + msk_ext))

part3_img = os.path.join(SOURCE, "Images")
if not os.path.exists(part3_img):
    part3_img = os.path.join(SOURCE, "images")
part3_mask = os.path.join(SOURCE, "Mask")
if not os.path.exists(part3_mask):
    part3_mask = os.path.join(SOURCE, "mask")
if not os.path.exists(part3_mask):
    part3_mask = os.path.join(SOURCE, "Masks")
print("Images exists:", os.path.exists(part3_img), "| Mask exists:", os.path.exists(part3_mask))
# Part3 masks use _segmentation suffix: 00000.tif <-> 00000_segmentation.tif
test_pairs = find_pairs(part3_img, part3_mask, mask_suffix="_segmentation")
print("\nPart3 pairs found:", len(test_pairs))

if test_pairs:
    move_pairs(test_pairs, os.path.join(DEST, "test"))
    print("Done! Test set added.")
else:
    print("No pairs found. Check that Images/ and Mask/ have matching filenames in Oil, Lookalike, No oil subdirs.")
