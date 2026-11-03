"""
Colab code to reorganize Zenodo dataset into simplified train/val/test structure.

⚠️  IMPORTANT: This script MOVES files (doesn't copy them) for speed.
   Your original Part1/Part2/Part3 structure will be modified!
   Make a backup if you need to keep the original structure.

Copy and paste this entire cell into a Colab notebook.
"""

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

import os
import shutil
import random
from pathlib import Path
from tqdm import tqdm

# ========== CONFIGURATION ==========
SOURCE_BASE = "/content/drive/MyDrive/oil_spill"  # Your current structure
DEST_BASE = "/content/drive/MyDrive/oil_spill_reorganized"  # New simplified structure

# Split Part1+Part2 into train/val (Part3 will be test set)
TRAIN_SPLIT = 0.9  # 90% for training (from Part1+Part2)
VAL_SPLIT = 0.1    # 10% for validation (from Part1+Part2)
# Part3 will be used as test set (respects dataset creators' intention)
USE_PART3_AS_TEST = True  # Set False if you want to split Part1+Part2 into train/val/test

RANDOM_SEED = 42   # For reproducibility

# ========== HELPER FUNCTIONS ==========
def find_image_mask_pairs(image_dir, mask_dir):
    """Find all matching image-mask pairs, handling subdirectories."""
    pairs = []
    
    if not os.path.exists(image_dir) or not os.path.exists(mask_dir):
        return pairs
    
    # Support multiple extensions
    img_extensions = ['.tif', '.tiff', '.TIF', '.TIFF', '.jpg', '.jpeg', '.png', '.JPG', '.PNG']
    
    # Build a map of all masks by their base name (for fast lookup)
    mask_map = {}  # {base_name: full_path}
    for mask_root, _, mask_files in os.walk(mask_dir):
        for mask_file in mask_files:
            mask_name_no_ext = os.path.splitext(mask_file)[0]
            mask_path = os.path.join(mask_root, mask_file)
            # Store multiple masks with same base name (shouldn't happen, but handle it)
            if mask_name_no_ext not in mask_map:
                mask_map[mask_name_no_ext] = []
            mask_map[mask_name_no_ext].append(mask_path)
    
    # Search recursively for images
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in img_extensions):
                img_path = os.path.join(root, file)
                img_name_no_ext = os.path.splitext(file)[0]
                
                # Find corresponding mask by base name
                mask_path = None
                if img_name_no_ext in mask_map:
                    # Use first matching mask (should only be one)
                    mask_path = mask_map[img_name_no_ext][0]
                
                if mask_path and os.path.exists(mask_path):
                    pairs.append((img_path, mask_path))
    
    return pairs

def move_pairs(pairs, dest_split_dir):
    """Move image-mask pairs to destination split directory.
    Uses unique names (prefix index) so files from Part1/Oil and Part2/Lookalike
    with the same filename don't overwrite each other.
    """
    dest_img_dir = os.path.join(dest_split_dir, 'images')
    dest_mask_dir = os.path.join(dest_split_dir, 'masks')
    
    os.makedirs(dest_img_dir, exist_ok=True)
    os.makedirs(dest_mask_dir, exist_ok=True)
    
    moved = 0
    for idx, (img_path, mask_path) in enumerate(tqdm(pairs, desc=f"Moving to {os.path.basename(dest_split_dir)}")):
        img_name = os.path.basename(img_path)
        mask_name = os.path.basename(mask_path)
        img_base, img_ext = os.path.splitext(img_name)
        mask_ext = os.path.splitext(mask_name)[1] or '.png'
        
        # Unique name: index + original base (avoids overwrites across Part1/Part2/Part3)
        unique_base = f"{idx:06d}_{img_base}"
        final_img_name = unique_base + img_ext
        final_mask_name = unique_base + mask_ext
        
        dest_img = os.path.join(dest_img_dir, final_img_name)
        dest_mask = os.path.join(dest_mask_dir, final_mask_name)
        
        try:
            shutil.move(img_path, dest_img)
            shutil.move(mask_path, dest_mask)
            moved += 1
        except Exception as e:
            print(f"  Error moving {img_name}: {e}")
    
    return moved

# ========== MAIN REORGANIZATION ==========
print("=" * 60)
print("Reorganizing Zenodo Dataset")
print("=" * 60)
print(f"Source: {SOURCE_BASE}")
print(f"Destination: {DEST_BASE}")
print(f"Train split: {TRAIN_SPLIT*100:.0f}% | Val split: {VAL_SPLIT*100:.0f}%")
print("=" * 60)

# Check if destination already exists and has files
if os.path.exists(DEST_BASE):
    train_img_dir = os.path.join(DEST_BASE, 'train', 'images')
    if os.path.exists(train_img_dir):
        existing_files = len([f for f in os.listdir(train_img_dir) if os.path.isfile(os.path.join(train_img_dir, f))])
        if existing_files > 0:
            print(f"\n⚠️  WARNING: Destination already exists with {existing_files} files!")
            print(f"   The reorganization may have already been completed.")
            print(f"   Files in source directories may have already been moved.")
            print(f"\n   To re-run:")
            print(f"   1. Delete or rename: {DEST_BASE}")
            print(f"   2. Re-extract Part1/Part2/Part3 archives")
            print(f"   3. Run this script again")
            print(f"\n   Or use the existing reorganized structure at: {DEST_BASE}")
            print("=" * 60)

all_pairs = []
test_pairs = []

# Part1: Oil Spill (train/val) - has Oil/ and Mask_oil/ subdirectories
print("\n📁 Processing Part1 (Oil Spill)...")
part1_img_dir = os.path.join(SOURCE_BASE, "Part1", "01_Train_Val_Oil_Spill_images")
part1_mask_dir = os.path.join(SOURCE_BASE, "Part1", "01_Train_Val_Oil_Spill_mask")
pairs = find_image_mask_pairs(part1_img_dir, part1_mask_dir)
if len(pairs) == 0:
    # Try subdirectory explicitly
    part1_img_subdir = os.path.join(part1_img_dir, "Oil")
    part1_mask_subdir = os.path.join(part1_mask_dir, "Mask_oil")
    if os.path.exists(part1_img_subdir) and os.path.exists(part1_mask_subdir):
        pairs = find_image_mask_pairs(part1_img_subdir, part1_mask_subdir)
all_pairs.extend(pairs)
print(f"   ✅ Found {len(pairs)} pairs")

# Part2: Lookalike (train/val) - has Lookalike/ and Mask_lookalike/ subdirectories
print("\n📁 Processing Part2 (Lookalike)...")
part2_lookalike_img = os.path.join(SOURCE_BASE, "Part2", "01_Train_Val_Lookalike_images")
part2_lookalike_mask = os.path.join(SOURCE_BASE, "Part2", "01_Train_Val_Lookalike_mask")
pairs = find_image_mask_pairs(part2_lookalike_img, part2_lookalike_mask)
if len(pairs) == 0:
    # Try subdirectory explicitly
    part2_lookalike_img_subdir = os.path.join(part2_lookalike_img, "Lookalike")
    part2_lookalike_mask_subdir = os.path.join(part2_lookalike_mask, "Mask_lookalike")
    if os.path.exists(part2_lookalike_img_subdir) and os.path.exists(part2_lookalike_mask_subdir):
        pairs = find_image_mask_pairs(part2_lookalike_img_subdir, part2_lookalike_mask_subdir)
all_pairs.extend(pairs)
print(f"   ✅ Found {len(pairs)} pairs")

# Part2: No Oil (train/val) - has No_oil/ and Mask_no_oil/ subdirectories
print("\n📁 Processing Part2 (No Oil)...")
part2_nooil_img = os.path.join(SOURCE_BASE, "Part2", "01_Train_Val_No_Oil_Images")
part2_nooil_mask = os.path.join(SOURCE_BASE, "Part2", "01_Train_Val_No_Oil_mask")
pairs = find_image_mask_pairs(part2_nooil_img, part2_nooil_mask)
if len(pairs) == 0:
    # Try subdirectory explicitly
    part2_nooil_img_subdir = os.path.join(part2_nooil_img, "No_oil")
    part2_nooil_mask_subdir = os.path.join(part2_nooil_mask, "Mask_no_oil")
    if os.path.exists(part2_nooil_img_subdir) and os.path.exists(part2_nooil_mask_subdir):
        pairs = find_image_mask_pairs(part2_nooil_img_subdir, part2_nooil_mask_subdir)
all_pairs.extend(pairs)
print(f"   ✅ Found {len(pairs)} pairs")

# Part3: Test set (has subdirectories: Lookalike/, No oil/, Oil/)
print("\n📁 Processing Part3 (Test set)...")
part3_base = os.path.join(SOURCE_BASE, "Part3", "02_Test_images_and_ground_truth")
part3_img_dir = os.path.join(part3_base, "Images")
part3_mask_dir = os.path.join(part3_base, "Mask")

# Try both "Mask" and "mask" (case sensitivity)
if not os.path.exists(part3_mask_dir):
    part3_mask_dir_alt = os.path.join(part3_base, "mask")
    if os.path.exists(part3_mask_dir_alt):
        part3_mask_dir = part3_mask_dir_alt
        print(f"   Using lowercase 'mask' directory")

test_pairs = find_image_mask_pairs(part3_img_dir, part3_mask_dir)

# If no pairs found, try processing each subdirectory separately
if len(test_pairs) == 0 and os.path.exists(part3_img_dir):
    print("   No pairs found with recursive search, trying subdirectories...")
    for subdir in ["Oil", "Lookalike", "No oil"]:
        sub_img_dir = os.path.join(part3_img_dir, subdir)
        sub_mask_dir = os.path.join(part3_mask_dir, subdir)
        if os.path.exists(sub_img_dir) and os.path.exists(sub_mask_dir):
            sub_pairs = find_image_mask_pairs(sub_img_dir, sub_mask_dir)
            test_pairs.extend(sub_pairs)
            print(f"   {subdir}: Found {len(sub_pairs)} pairs")
        else:
            # Try case variations
            for case_variant in [subdir.lower(), subdir.upper(), subdir.title()]:
                sub_img_dir_var = os.path.join(part3_img_dir, case_variant)
                sub_mask_dir_var = os.path.join(part3_mask_dir, case_variant)
                if os.path.exists(sub_img_dir_var) and os.path.exists(sub_mask_dir_var):
                    sub_pairs = find_image_mask_pairs(sub_img_dir_var, sub_mask_dir_var)
                    test_pairs.extend(sub_pairs)
                    print(f"   {case_variant}: Found {len(sub_pairs)} pairs")
                    break

print(f"   ✅ Total Part3 pairs found: {len(test_pairs)}")

# Check if we found any pairs
if len(all_pairs) == 0 and len(test_pairs) == 0:
    print("\n❌ ERROR: No image-mask pairs found!")
    print("\nPossible reasons:")
    print("   1. Files were already moved in a previous run")
    print("   2. Source path is incorrect")
    print("   3. Files don't exist or are in unexpected locations")
    print(f"\n   Check source: {SOURCE_BASE}")
    print(f"   Check if reorganized structure exists: {DEST_BASE}")
    print("\n   If files were already moved, you can:")
    print(f"   - Use the existing structure at: {DEST_BASE}")
    print("   - Or restore from backup/re-extract archives to re-run")
    exit(1)

# Shuffle training/validation pairs
if len(all_pairs) > 0:
    print(f"\n🔄 Shuffling {len(all_pairs)} training/validation pairs...")
    random.seed(RANDOM_SEED)
    random.shuffle(all_pairs)

# Split train/val from Part1+Part2
if USE_PART3_AS_TEST and len(test_pairs) > 0:
    # Respect dataset creators' intention: Part3 is test set
    # Split Part1+Part2 into train/val only
    n_train = int(len(all_pairs) * TRAIN_SPLIT)
    n_val = len(all_pairs) - n_train  # Remaining goes to val
    
    train_pairs = all_pairs[:n_train]
    val_pairs = all_pairs[n_train:]
    
    print(f"\n📊 Split Summary (respecting Part3 as test set):")
    print(f"   Train: {len(train_pairs)} pairs (from Part1+Part2)")
    print(f"   Val:   {len(val_pairs)} pairs (from Part1+Part2)")
    print(f"   Test:  {len(test_pairs)} pairs (from Part3 - original test set)")
else:
    # Fallback: split Part1+Part2 into train/val/test if Part3 not found
    n_train = int(len(all_pairs) * TRAIN_SPLIT)
    n_val = int(len(all_pairs) * VAL_SPLIT)
    
    train_pairs = all_pairs[:n_train]
    val_pairs = all_pairs[n_train:n_train + n_val]
    test_pairs = all_pairs[n_train + n_val:] if len(test_pairs) == 0 else test_pairs
    
    print(f"\n📊 Split Summary (Part3 not found, using Part1+Part2 for all splits):")
    print(f"   Train: {len(train_pairs)} pairs")
    print(f"   Val:   {len(val_pairs)} pairs")
    print(f"   Test:  {len(test_pairs)} pairs")

# Create destination directories
os.makedirs(DEST_BASE, exist_ok=True)

# Move files (much faster than copying for 90GB dataset!)
print(f"\n📦 Moving files to {DEST_BASE}...")
print("⚠️  Note: Files will be MOVED (not copied) - original structure will be modified!")
print("-" * 60)

if train_pairs:
    train_dir = os.path.join(DEST_BASE, 'train')
    moved = move_pairs(train_pairs, train_dir)
    print(f"✅ Train: {moved}/{len(train_pairs)} pairs moved")

if val_pairs:
    val_dir = os.path.join(DEST_BASE, 'val')
    moved = move_pairs(val_pairs, val_dir)
    print(f"✅ Val:   {moved}/{len(val_pairs)} pairs moved")

if test_pairs:
    test_dir = os.path.join(DEST_BASE, 'test')
    moved = move_pairs(test_pairs, test_dir)
    print(f"✅ Test:  {moved}/{len(test_pairs)} pairs moved")
elif len(all_pairs) > n_train + n_val:
    # Use remaining as test
    test_pairs = all_pairs[n_train + n_val:]
    test_dir = os.path.join(DEST_BASE, 'test')
    moved = move_pairs(test_pairs, test_dir)
    print(f"✅ Test:  {moved}/{len(test_pairs)} pairs moved (from remaining data)")

print("\n" + "=" * 60)
print("✅ Reorganization Complete!")
print("=" * 60)
print(f"\nNew structure created at: {DEST_BASE}")
print("\nStructure:")
print(f"  {DEST_BASE}/")
print(f"    train/")
print(f"      images/ ({len(train_pairs)} files)")
print(f"      masks/  ({len(train_pairs)} files)")
print(f"    val/")
print(f"      images/ ({len(val_pairs)} files)")
print(f"      masks/  ({len(val_pairs)} files)")
print(f"    test/")
print(f"      images/ ({len(test_pairs) if test_pairs else len(all_pairs) - n_train - n_val} files)")
print(f"      masks/  ({len(test_pairs) if test_pairs else len(all_pairs) - n_train - n_val} files)")

print("\n💡 Next steps:")
print("   1. Update your notebook: USE_SIMPLIFIED_STRUCTURE = True")
print(f"   2. Set _BASE = '{DEST_BASE}'")
print("   3. Run the data loading cell!")
print("\n⚠️  Important: Original Part1/Part2/Part3 folders have been modified (files moved).")
print("   If you need the original structure, restore from backup or re-extract the archives.")
