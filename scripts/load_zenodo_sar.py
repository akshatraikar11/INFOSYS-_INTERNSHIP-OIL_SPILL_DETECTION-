"""
Load Zenodo Sentinel-1 SAR oil spill dataset.

This script supports two folder structures:

1. SIMPLIFIED STRUCTURE (recommended):
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

2. ORIGINAL STRUCTURE (Parts I, II, III):
   oil_spill/
     Part1/01_Train_Val_Oil_Spill_images/
     Part1/01_Train_Val_Oil_Spill_mask/
     Part2/01_Train_Val_Lookalike_images/
     ...

Supports both Colab (Linux paths) and local Windows paths.
"""

import os
import numpy as np
from PIL import Image
import glob
from tqdm import tqdm


def load_from_simple_structure(base_dir, split='train', target_size=(256, 256), channels=1, 
                                normalize_sar=True, max_samples=None, verbose=True):
    """
    Load from simplified train/val/test structure.
    
    Args:
        base_dir: Base directory containing train/, val/, test/ subdirectories
        split: Which split to load ('train', 'val', or 'test')
        target_size: Tuple (height, width) for resizing images
        channels: Number of channels (1 for grayscale SAR)
        normalize_sar: If True, normalize SAR values to [0, 1] range
        max_samples: Maximum number of samples to load (None for all)
        verbose: Print progress information
        
    Returns:
        X: numpy array of images (n_samples, height, width, channels)
        Y: numpy array of masks (n_samples, height, width, 1)
    """
    img_dir = os.path.join(base_dir, split, 'images')
    mask_dir = os.path.join(base_dir, split, 'masks')
    
    if not os.path.exists(img_dir):
        raise ValueError(f"Image directory not found: {img_dir}")
    if not os.path.exists(mask_dir):
        raise ValueError(f"Mask directory not found: {mask_dir}")
    
    return load_zenodo_sar(
        image_dirs=[img_dir],
        mask_dirs=[mask_dir],
        target_size=target_size,
        channels=channels,
        normalize_sar=normalize_sar,
        max_samples=max_samples,
        verbose=verbose
    )


def load_zenodo_sar(
    image_dirs,
    mask_dirs,
    target_size=(256, 256),
    channels=1,
    normalize_sar=True,
    max_samples=None,
    verbose=True
):
    """
    Load Zenodo SAR dataset from multiple directories.
    
    Args:
        image_dirs: List of directories containing SAR images (TIFF files)
        mask_dirs: List of directories containing masks (TIFF/PNG files)
        target_size: Tuple (height, width) for resizing images
        channels: Number of channels (1 for grayscale SAR)
        normalize_sar: If True, normalize SAR values to [0, 1] range
        max_samples: Maximum number of samples to load (None for all)
        verbose: Print progress information
        
    Returns:
        X: numpy array of images (n_samples, height, width, channels)
        Y: numpy array of masks (n_samples, height, width, 1)
    """
    images = []
    masks = []
    
    if len(image_dirs) != len(mask_dirs):
        raise ValueError(f"Number of image dirs ({len(image_dirs)}) must match mask dirs ({len(mask_dirs)})")
    
    for img_dir, mask_dir in zip(image_dirs, mask_dirs):
        if not os.path.exists(img_dir):
            if verbose:
                print(f"Warning: Image directory not found: {img_dir}")
            continue
        if not os.path.exists(mask_dir):
            if verbose:
                print(f"Warning: Mask directory not found: {mask_dir}")
            continue
            
        if verbose:
            print(f"Loading from:\n  Images: {img_dir}\n  Masks: {mask_dir}")
        
        # Find all image files (support .tif, .tiff, .jpg, .png)
        img_extensions = ['*.tif', '*.tiff', '*.TIF', '*.TIFF', '*.jpg', '*.jpeg', '*.png']
        img_files = []
        for ext in img_extensions:
            img_files.extend(glob.glob(os.path.join(img_dir, '**', ext), recursive=True))
            # Also check direct files (not recursive)
            img_files.extend(glob.glob(os.path.join(img_dir, ext)))
        
        # Remove duplicates and sort
        img_files = sorted(list(set(img_files)))
        
        if verbose:
            print(f"  Found {len(img_files)} image files")
        
        # Process each image-mask pair
        for img_path in tqdm(img_files, desc=f"Loading {os.path.basename(img_dir)}", disable=not verbose):
            if max_samples and len(images) >= max_samples:
                break
                
            # Find corresponding mask file
            img_basename = os.path.basename(img_path)
            img_name_no_ext = os.path.splitext(img_basename)[0]
            
            # Try different mask file locations and extensions
            mask_path = None
            mask_candidates = [
                os.path.join(mask_dir, img_basename),
                os.path.join(mask_dir, img_name_no_ext + '.png'),
                os.path.join(mask_dir, img_name_no_ext + '.tif'),
                os.path.join(mask_dir, img_name_no_ext + '.tiff'),
                # Check subdirectories (e.g., Mask_oil/, Mask_lookalike/, etc.)
                os.path.join(mask_dir, '**', img_basename),
                os.path.join(mask_dir, '**', img_name_no_ext + '.png'),
                os.path.join(mask_dir, '**', img_name_no_ext + '.tif'),
            ]
            
            for candidate in mask_candidates:
                if '*' in candidate:
                    # Use glob for recursive search
                    matches = glob.glob(candidate, recursive=True)
                    if matches:
                        mask_path = matches[0]
                        break
                elif os.path.exists(candidate):
                    mask_path = candidate
                    break
            
            if mask_path is None or not os.path.exists(mask_path):
                if verbose:
                    print(f"  Warning: No mask found for {img_basename}, skipping...")
                continue
            
            try:
                # Load and preprocess image
                img = Image.open(img_path)
                
                # Handle SAR TIFF files (may have multiple bands)
                if hasattr(img, 'n_frames') and img.n_frames > 1:
                    # Multi-page TIFF, use first page
                    img.seek(0)
                
                # Convert to grayscale if needed
                if img.mode != 'L':
                    img = img.convert('L')
                
                # Resize
                img = img.resize(target_size, Image.LANCZOS)
                img_array = np.array(img, dtype=np.float32)
                
                # Normalize SAR data (typically 16-bit, range 0-65535)
                if normalize_sar:
                    if img_array.max() > 1.0:
                        img_array = img_array / 65535.0  # Normalize 16-bit SAR
                    else:
                        img_array = img_array / 255.0  # Normalize 8-bit
                else:
                    img_array = img_array / 255.0
                
                # Add channel dimension
                if channels == 1:
                    img_array = np.expand_dims(img_array, axis=-1)
                elif channels == 2:
                    # Duplicate for 2-channel input
                    img_array = np.stack([img_array, img_array], axis=-1)
                
                # Load and preprocess mask
                mask = Image.open(mask_path)
                if mask.mode != 'L':
                    mask = mask.convert('L')
                mask = mask.resize(target_size, Image.LANCZOS)
                mask_array = np.array(mask, dtype=np.float32)
                
                # Normalize mask to [0, 1]
                if mask_array.max() > 1.0:
                    mask_array = mask_array / 255.0
                
                # Binarize mask (threshold at 0.5)
                mask_array = (mask_array > 0.5).astype(np.float32)
                mask_array = np.expand_dims(mask_array, axis=-1)
                
                images.append(img_array)
                masks.append(mask_array)
                
            except Exception as e:
                if verbose:
                    print(f"  Error loading {img_basename}: {e}")
                continue
    
    if len(images) == 0:
        raise ValueError("No valid image-mask pairs found. Check your paths and file structure.")
    
    X = np.array(images)
    Y = np.array(masks)
    
    if verbose:
        print(f"\nLoaded {len(X)} image-mask pairs")
        print(f"Image shape: {X.shape}")
        print(f"Mask shape: {Y.shape}")
    
    return X, Y


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python load_zenodo_sar.py <image_dir1> <mask_dir1> [image_dir2] [mask_dir2] ...")
        sys.exit(1)
    
    image_dirs = sys.argv[1::2]
    mask_dirs = sys.argv[2::2]
    
    X, Y = load_zenodo_sar(
        image_dirs=image_dirs,
        mask_dirs=mask_dirs,
        target_size=(256, 256),
        channels=1,
        normalize_sar=True
    )
    
    print(f"Successfully loaded {len(X)} samples")
