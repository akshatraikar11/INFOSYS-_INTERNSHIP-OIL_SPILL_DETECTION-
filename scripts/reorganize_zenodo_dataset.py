"""
Reorganize Zenodo SAR dataset into a simpler train/val/test structure.

This script consolidates Parts I, II, III into a unified structure:
  oil_spill/
    train/
      images/
      masks/
    val/
      images/
      masks/
    test/
      images/
      masks/

⚠️  IMPORTANT: By default, this script MOVES files (not copies) for speed.
   Use --copy flag if you want to preserve the original structure.

Usage:
    python scripts/reorganize_zenodo_dataset.py --source <original_path> --dest <new_path> [--split 0.8] [--copy]
"""

import os
import shutil
import argparse
from pathlib import Path
from tqdm import tqdm
import random


def find_image_mask_pairs(image_dir, mask_dir):
    """Find all matching image-mask pairs."""
    pairs = []
    
    # Support multiple extensions
    img_extensions = ['.tif', '.tiff', '.TIF', '.TIFF', '.jpg', '.jpeg', '.png']
    
    # Search recursively
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in img_extensions):
                img_path = os.path.join(root, file)
                img_name_no_ext = os.path.splitext(file)[0]
                
                # Try to find corresponding mask
                mask_path = None
                mask_candidates = [
                    os.path.join(mask_dir, file),
                    os.path.join(mask_dir, img_name_no_ext + '.png'),
                    os.path.join(mask_dir, img_name_no_ext + '.tif'),
                    os.path.join(mask_dir, img_name_no_ext + '.tiff'),
                ]
                
                # Also search recursively in mask_dir
                for mask_root, _, mask_files in os.walk(mask_dir):
                    for mask_file in mask_files:
                        mask_name_no_ext = os.path.splitext(mask_file)[0]
                        if mask_name_no_ext == img_name_no_ext:
                            mask_path = os.path.join(mask_root, mask_file)
                            break
                    if mask_path:
                        break
                
                if mask_path and os.path.exists(mask_path):
                    pairs.append((img_path, mask_path))
    
    return pairs


def reorganize_dataset(source_base, dest_base, train_split=0.8, val_split=0.1, seed=42, use_copy=False):
    """
    Reorganize Zenodo dataset from Parts I/II/III structure to train/val/test.
    
    Args:
        source_base: Base directory containing Part1/, Part2/, Part3/
        dest_base: Destination directory for reorganized structure
        train_split: Fraction for training (default 0.8)
        val_split: Fraction for validation (default 0.1, test = 1 - train - val)
        seed: Random seed for reproducibility
    """
    random.seed(seed)
    
    source_base = Path(source_base)
    dest_base = Path(dest_base)
    
    # Create destination directories
    for split in ['train', 'val', 'test']:
        (dest_base / split / 'images').mkdir(parents=True, exist_ok=True)
        (dest_base / split / 'masks').mkdir(parents=True, exist_ok=True)
    
    all_pairs = []
    
    # Part1: Oil Spill (train/val)
    part1_img_dir = source_base / "Part1" / "01_Train_Val_Oil_Spill_images"
    part1_mask_dir = source_base / "Part1" / "01_Train_Val_Oil_Spill_mask"
    if part1_img_dir.exists() and part1_mask_dir.exists():
        print(f"\n📁 Processing Part1 (Oil Spill)...")
        pairs = find_image_mask_pairs(str(part1_img_dir), str(part1_mask_dir))
        all_pairs.extend(pairs)
        print(f"   Found {len(pairs)} pairs")
    
    # Part2: Lookalike (train/val)
    part2_lookalike_img = source_base / "Part2" / "01_Train_Val_Lookalike_images"
    part2_lookalike_mask = source_base / "Part2" / "01_Train_Val_Lookalike_mask"
    if part2_lookalike_img.exists() and part2_lookalike_mask.exists():
        print(f"\n📁 Processing Part2 (Lookalike)...")
        pairs = find_image_mask_pairs(str(part2_lookalike_img), str(part2_lookalike_mask))
        all_pairs.extend(pairs)
        print(f"   Found {len(pairs)} pairs")
    
    # Part2: No Oil (train/val)
    part2_nooil_img = source_base / "Part2" / "01_Train_Val_No_Oil_Images"
    part2_nooil_mask = source_base / "Part2" / "01_Train_Val_No_Oil_mask"
    if part2_nooil_img.exists() and part2_nooil_mask.exists():
        print(f"\n📁 Processing Part2 (No Oil)...")
        pairs = find_image_mask_pairs(str(part2_nooil_img), str(part2_nooil_mask))
        all_pairs.extend(pairs)
        print(f"   Found {len(pairs)} pairs")
    
    # Part3: Test set
    part3_img_dir = source_base / "Part3" / "02_Test_images_and_ground_truth" / "Images"
    part3_mask_dir = source_base / "Part3" / "02_Test_images_and_ground_truth" / "Mask"
    test_pairs = []
    if part3_img_dir.exists() and part3_mask_dir.exists():
        print(f"\n📁 Processing Part3 (Test set)...")
        test_pairs = find_image_mask_pairs(str(part3_img_dir), str(part3_mask_dir))
        print(f"   Found {len(test_pairs)} pairs")
    
    # Shuffle training/validation pairs
    print(f"\n🔄 Shuffling {len(all_pairs)} training/validation pairs...")
    random.shuffle(all_pairs)
    
    # Split train/val
    n_train = int(len(all_pairs) * train_split)
    n_val = int(len(all_pairs) * val_split)
    
    train_pairs = all_pairs[:n_train]
    val_pairs = all_pairs[n_train:n_train + n_val]
    # Remaining goes to test if no Part3, or Part3 is used as test
    
    print(f"\n📊 Split summary:")
    print(f"   Train: {len(train_pairs)} pairs")
    print(f"   Val:   {len(val_pairs)} pairs")
    print(f"   Test:  {len(test_pairs) if test_pairs else len(all_pairs) - n_train - n_val} pairs")
    
    # Move or copy files
    def move_or_copy_pairs(pairs, split_name, use_copy=False):
        """Move or copy image-mask pairs to destination."""
        action = "Copying" if use_copy else "Moving"
        for img_path, mask_path in tqdm(pairs, desc=f"{action} {split_name}"):
            img_name = os.path.basename(img_path)
            mask_name = os.path.basename(mask_path)
            
            # Ensure mask has same base name as image (with .png extension)
            mask_base = os.path.splitext(img_name)[0]
            mask_ext = os.path.splitext(mask_name)[1] or '.png'
            final_mask_name = mask_base + mask_ext
            
            dest_img = dest_base / split_name / 'images' / img_name
            dest_mask = dest_base / split_name / 'masks' / final_mask_name
            
            # Move or copy image
            if use_copy:
                shutil.copy2(img_path, dest_img)
                shutil.copy2(mask_path, dest_mask)
            else:
                shutil.move(str(img_path), str(dest_img))
                shutil.move(str(mask_path), str(dest_mask))
    
    # Move or copy train/val/test sets
    action = "Copying" if use_copy else "Moving"
    print(f"\n📦 {action} files to {dest_base}...")
    if not use_copy:
        print("⚠️  Note: Files will be MOVED (not copied) - original structure will be modified!")
    
    if train_pairs:
        move_or_copy_pairs(train_pairs, 'train', use_copy=use_copy)
    if val_pairs:
        move_or_copy_pairs(val_pairs, 'val', use_copy=use_copy)
    if test_pairs:
        move_or_copy_pairs(test_pairs, 'test', use_copy=use_copy)
    elif len(all_pairs) > n_train + n_val:
        # Use remaining as test
        test_pairs = all_pairs[n_train + n_val:]
        move_or_copy_pairs(test_pairs, 'test', use_copy=use_copy)
    
    print(f"\n✅ Reorganization complete!")
    print(f"   Destination: {dest_base}")
    if not use_copy:
        print(f"   ⚠️  Original Part1/Part2/Part3 folders have been modified (files moved).")
    print(f"\nNew structure:")
    print(f"   {dest_base}/")
    print(f"     train/images/ ({len(train_pairs)} files)")
    print(f"     train/masks/ ({len(train_pairs)} files)")
    print(f"     val/images/ ({len(val_pairs)} files)")
    print(f"     val/masks/ ({len(val_pairs)} files)")
    print(f"     test/images/ ({len(test_pairs) if test_pairs else len(all_pairs) - n_train - n_val} files)")
    print(f"     test/masks/ ({len(test_pairs) if test_pairs else len(all_pairs) - n_train - n_val} files)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorganize Zenodo dataset into train/val/test structure")
    parser.add_argument("--source", required=True, help="Source directory containing Part1/, Part2/, Part3/")
    parser.add_argument("--dest", required=True, help="Destination directory for reorganized structure")
    parser.add_argument("--train-split", type=float, default=0.8, help="Training split ratio (default: 0.8)")
    parser.add_argument("--val-split", type=float, default=0.1, help="Validation split ratio (default: 0.1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--copy", action="store_true", help="Copy files instead of moving (preserves original structure)")
    
    args = parser.parse_args()
    
    # Validate splits
    if args.train_split + args.val_split >= 1.0:
        print("Error: train_split + val_split must be < 1.0")
        exit(1)
    
    reorganize_dataset(
        source_base=args.source,
        dest_base=args.dest,
        train_split=args.train_split,
        val_split=args.val_split,
        seed=args.seed,
        use_copy=args.copy
    )
