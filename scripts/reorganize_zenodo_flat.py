"""
Reorganize the flat Oil_Spill structure into train/val/test.

Your flat structure:
  Oil/, Mask_oil/           → Part 1 (train+val)
  Lookalike/, Mask_lookalike/ → Part 2 (train+val)
  No_oil/, Mask_no_oil/     → Part 2 (train+val)
  Images/, Mask/            → Part 3 (test; Images/ and Mask/ have Oil/, Lookalike/, No oil/ subdirs)

Output:
  train/images/, train/masks/
  val/images/, val/masks/
  test/images/, test/masks/

Usage:
  # Local ( copies files - keeps original intact, needs ~90GB free for dest)
  python scripts/reorganize_zenodo_flat.py --source "C:/path/to/Oil_Spill" --dest "C:/path/to/oil_spill_reorganized"

  # Colab / Google Drive ( --move saves space, modifies source)
  python scripts/reorganize_zenodo_flat.py --source "/content/drive/MyDrive/Oil_Spill" --dest "/content/drive/MyDrive/oil_spill_reorganized" --move
"""

import os
import shutil
import random
import argparse
from pathlib import Path

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    def tqdm(iterable, **kwargs):
        return iterable


def find_image_mask_pairs(image_dir, mask_dir):
    """Find all matching image-mask pairs, handling subdirectories."""
    pairs = []
    if not os.path.exists(image_dir) or not os.path.exists(mask_dir):
        return pairs

    img_extensions = ('.tif', '.tiff', '.jpg', '.jpeg', '.png')
    mask_map = {}
    for mask_root, _, mask_files in os.walk(mask_dir):
        for mask_file in mask_files:
            if any(mask_file.lower().endswith(ext) for ext in img_extensions):
                mask_name_no_ext = os.path.splitext(mask_file)[0]
                mask_path = os.path.join(mask_root, mask_file)
                if mask_name_no_ext not in mask_map:
                    mask_map[mask_name_no_ext] = []
                mask_map[mask_name_no_ext].append(mask_path)

    for root, _, files in os.walk(image_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in img_extensions):
                img_path = os.path.join(root, file)
                img_name_no_ext = os.path.splitext(file)[0]
                mask_path = None
                if img_name_no_ext in mask_map:
                    mask_path = mask_map[img_name_no_ext][0]
                if mask_path and os.path.exists(mask_path):
                    pairs.append((img_path, mask_path))
    return pairs


def transfer_pairs(pairs, dest_split_dir, use_move=False):
    """Copy or move image-mask pairs to destination split directory."""
    dest_img_dir = os.path.join(dest_split_dir, 'images')
    dest_mask_dir = os.path.join(dest_split_dir, 'masks')
    os.makedirs(dest_img_dir, exist_ok=True)
    os.makedirs(dest_mask_dir, exist_ok=True)

    transfer_fn = shutil.move if use_move else shutil.copy2
    transferred = 0
    for idx, (img_path, mask_path) in enumerate(tqdm(pairs, desc=os.path.basename(dest_split_dir), disable=not HAS_TQDM)):
        img_base, img_ext = os.path.splitext(os.path.basename(img_path))
        mask_ext = os.path.splitext(os.path.basename(mask_path))[1] or '.png'
        unique_base = f"{idx:06d}_{img_base}"
        final_img_name = unique_base + img_ext
        final_mask_name = unique_base + mask_ext
        dest_img = os.path.join(dest_img_dir, final_img_name)
        dest_mask = os.path.join(dest_mask_dir, final_mask_name)
        try:
            transfer_fn(img_path, dest_img)
            transfer_fn(mask_path, dest_mask)
            transferred += 1
        except Exception as e:
            print(f"  Error: {e}")
    return transferred


def main():
    parser = argparse.ArgumentParser(description="Reorganize flat Oil_Spill structure into train/val/test")
    parser.add_argument("--source", required=True, help="Path to Oil_Spill folder (flat structure)")
    parser.add_argument("--dest", required=True, help="Output path for train/val/test structure")
    parser.add_argument("--train-split", type=float, default=0.9, help="Train fraction from Part1+2 (default: 0.9)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--move", action="store_true", help="Move files instead of copy (saves space, modifies source)")
    args = parser.parse_args()

    src = os.path.normpath(args.source)
    dst = os.path.normpath(args.dest)
    if not os.path.exists(src):
        print(f"Error: Source not found: {src}")
        return 1

    # Part1+2: direct image/mask folders
    part12_pairs = []
    for img_name, mask_name in [
        ("Oil", "Mask_oil"),
        ("Lookalike", "Mask_lookalike"),
        ("No_oil", "Mask_no_oil"),
    ]:
        img_dir = os.path.join(src, img_name)
        mask_dir = os.path.join(src, mask_name)
        pairs = find_image_mask_pairs(img_dir, mask_dir)
        part12_pairs.extend(pairs)
        print(f"  {img_name}: {len(pairs)} pairs")

    # Part3: Images/ and Mask/ with subdirs (Oil, Lookalike, No oil)
    part3_img = os.path.join(src, "Images")
    part3_mask = os.path.join(src, "Mask")
    if not os.path.exists(part3_mask):
        part3_mask = os.path.join(src, "mask")
    test_pairs = find_image_mask_pairs(part3_img, part3_mask)
    print(f"  Part3 (Images/Mask): {len(test_pairs)} pairs")

    if not part12_pairs and not test_pairs:
        print("Error: No image-mask pairs found. Check --source path and folder names.")
        return 1

    random.seed(args.seed)
    random.shuffle(part12_pairs)
    n_train = int(len(part12_pairs) * args.train_split)
    train_pairs = part12_pairs[:n_train]
    val_pairs = part12_pairs[n_train:]

    mode = "Moving" if args.move else "Copying"
    print(f"\n{mode} files to {dst}")
    print(f"  Train: {len(train_pairs)} | Val: {len(val_pairs)} | Test: {len(test_pairs)}")
    print("-" * 50)

    os.makedirs(dst, exist_ok=True)
    if train_pairs:
        transfer_pairs(train_pairs, os.path.join(dst, "train"), use_move=args.move)
    if val_pairs:
        transfer_pairs(val_pairs, os.path.join(dst, "val"), use_move=args.move)
    if test_pairs:
        transfer_pairs(test_pairs, os.path.join(dst, "test"), use_move=args.move)

    print("\nDone. Structure:")
    print(f"  {dst}/")
    print(f"    train/images/  train/masks/")
    print(f"    val/images/    val/masks/")
    print(f"    test/images/   test/masks/")
    print("\nNext: In notebook set USE_SIMPLIFIED_STRUCTURE = True and _BASE =", repr(dst))
    return 0


if __name__ == "__main__":
    exit(main())
