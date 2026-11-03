"""
========================================
COPY THIS ENTIRE FILE INTO A COLAB CELL
========================================

Reorganizes your flat Oil_Spill structure on Google Drive into train/val/test.
"""

# 1. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

import os
import shutil
import random
from tqdm import tqdm

# ========== CONFIGURATION ==========
SOURCE = "/content/drive/MyDrive/Oil_Spill"   # Your flat Oil_Spill folder
DEST = "/content/drive/MyDrive/oil_spill_reorganized"
TRAIN_SPLIT = 0.9  # 90% train, 10% val from Part1+2
SEED = 42

# ========== HELPER ==========
def find_pairs(img_dir, mask_dir, debug=False, mask_suffix=None):
    """mask_suffix: e.g. '_segmentation' for Part3 where masks are 00000_segmentation.tif"""
    pairs = []
    exts = ('.tif', '.tiff', '.jpg', '.jpeg', '.png')
    if not os.path.exists(img_dir):
        if debug:
            print(f"    [DEBUG] Image dir missing: {img_dir}")
        return pairs
    if not os.path.exists(mask_dir):
        if debug:
            print(f"    [DEBUG] Mask dir missing: {mask_dir}")
        return pairs
    mask_map = {}
    for r, _, fs in os.walk(mask_dir):
        for f in fs:
            if any(f.lower().endswith(e) for e in exts):
                base = os.path.splitext(f)[0]
                key = base.replace(mask_suffix, "") if mask_suffix and mask_suffix in base else base
                mask_map[key] = os.path.join(r, f)
    n_imgs, n_matched = 0, 0
    for r, _, fs in os.walk(img_dir):
        for f in fs:
            if any(f.lower().endswith(e) for e in exts):
                n_imgs += 1
                name = os.path.splitext(f)[0]
                if name in mask_map:
                    pairs.append((os.path.join(r, f), mask_map[name]))
                    n_matched += 1
    if debug and n_imgs > 0:
        print(f"    [DEBUG] Images found: {n_imgs}, matched: {n_matched}, masks in map: {len(mask_map)}")
    return pairs

def move_pairs(pairs, dest_split):
    dest_img = os.path.join(dest_split, 'images')
    dest_msk = os.path.join(dest_split, 'masks')
    os.makedirs(dest_img, exist_ok=True)
    os.makedirs(dest_msk, exist_ok=True)
    for i, (img, msk) in enumerate(tqdm(pairs, desc=os.path.basename(dest_split))):
        base, ext = os.path.splitext(os.path.basename(img))
        msk_ext = os.path.splitext(os.path.basename(msk))[1] or '.png'
        u = f"{i:06d}_{base}"
        shutil.move(img, os.path.join(dest_img, u + ext))
        shutil.move(msk, os.path.join(dest_msk, u + msk_ext))

# ========== RUN ==========
print("Source:", SOURCE)
print("Dest:  ", DEST)

part12 = []
for img, msk in [("Oil", "Mask_oil"), ("Lookalike", "Mask_lookalike"), ("No_oil", "Mask_no_oil")]:
    p = find_pairs(os.path.join(SOURCE, img), os.path.join(SOURCE, msk))
    part12.extend(p)
    print(f"  {img}: {len(p)} pairs")

# Part3: Images/ + Mask/ (each has Lookalike, No oil, Oil subdirs)
part3_img = os.path.join(SOURCE, "Images")
if not os.path.exists(part3_img):
    part3_img = os.path.join(SOURCE, "images")
part3_mask = os.path.join(SOURCE, "Mask")
if not os.path.exists(part3_mask):
    part3_mask = os.path.join(SOURCE, "mask")
if not os.path.exists(part3_mask):
    part3_mask = os.path.join(SOURCE, "Masks")
print(f"  Part3 paths: Images={os.path.exists(part3_img)}, Mask={os.path.exists(part3_mask)}")
test_pairs = find_pairs(part3_img, part3_mask, debug=True, mask_suffix="_segmentation")
print(f"  Part3 (test): {len(test_pairs)} pairs")

random.seed(SEED)
random.shuffle(part12)
n = int(len(part12) * TRAIN_SPLIT)
train_p, val_p = part12[:n], part12[n:]

os.makedirs(DEST, exist_ok=True)
move_pairs(train_p, os.path.join(DEST, "train"))
move_pairs(val_p, os.path.join(DEST, "val"))
move_pairs(test_pairs, os.path.join(DEST, "test"))

print("\nDone! Structure at", DEST)
print("  train/images  train/masks")
print("  val/images    val/masks")
print("  test/images   test/masks")
print("\nIn notebook: USE_SIMPLIFIED_STRUCTURE = True, _BASE =", repr(DEST))
