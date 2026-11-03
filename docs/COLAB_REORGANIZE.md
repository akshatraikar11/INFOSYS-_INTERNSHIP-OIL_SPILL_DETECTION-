# Reorganize Zenodo Dataset in Google Colab

This guide shows you how to reorganize your Zenodo dataset from the complex Part1/Part2/Part3 structure into a simple `train/val/test` structure directly in Colab.

## Quick Start

### Step 1: Create a New Colab Cell

Create a new code cell in your Colab notebook and paste the code from `scripts/reorganize_zenodo_colab.py`.

### Step 2: Run the Cell

The script will:
1. Mount your Google Drive
2. Find all image-mask pairs from Part1, Part2, Part3
3. Split them into train (80%), val (10%), and test (10%)
4. Copy files to the new simplified structure at `/content/drive/MyDrive/oil_spill_reorganized`

### Step 3: Update Your Notebook

After reorganization, update your `Oil_Spill_Detection.ipynb`:

```python
USE_ZENODO_SAR = True
USE_SIMPLIFIED_STRUCTURE = True
_BASE = "/content/drive/MyDrive/oil_spill_reorganized"
```

## Customization

You can modify these variables at the top of the Colab cell:

```python
SOURCE_BASE = "/content/drive/MyDrive/oil_spill"  # Your current structure
DEST_BASE = "/content/drive/MyDrive/oil_spill_reorganized"  # New location
TRAIN_SPLIT = 0.8  # 80% for training
VAL_SPLIT = 0.1    # 10% for validation
RANDOM_SEED = 42   # For reproducibility
```

## What Gets Created

After running, you'll have:

```
/content/drive/MyDrive/oil_spill_reorganized/
  train/
    images/  (all training images)
    masks/   (all training masks)
  val/
    images/  (all validation images)
    masks/   (all validation masks)
  test/
    images/  (all test images)
    masks/   (all test masks)
```

## Notes

- **Original files are preserved** - the script copies files, doesn't move them
- **Part3 test set** is kept separate if it exists
- **If Part3 doesn't exist**, remaining data after train/val split becomes test set
- **All files are shuffled** before splitting for better distribution
- **Progress bars** show copying progress for each split

## Troubleshooting

**"No image-mask pairs found"**
- Check that `SOURCE_BASE` points to `/content/drive/MyDrive/oil_spill`
- Verify Drive is mounted correctly
- Make sure Part1/, Part2/, Part3/ folders exist

**"Permission denied"**
- Make sure Google Drive is mounted
- Check that you have write access to the destination folder

**Out of space**
- The script copies files, so you need ~90GB free space
- Consider using a different `DEST_BASE` location if needed

## Example Output

When you run the script, you'll see:

```
============================================================
Reorganizing Zenodo Dataset
============================================================
Source: /content/drive/MyDrive/oil_spill
Destination: /content/drive/MyDrive/oil_spill_reorganized
Train split: 80% | Val split: 10%
============================================================

📁 Processing Part1 (Oil Spill)...
   ✅ Found 1234 pairs

📁 Processing Part2 (Lookalike)...
   ✅ Found 567 pairs

📁 Processing Part2 (No Oil)...
   ✅ Found 890 pairs

📁 Processing Part3 (Test set)...
   ✅ Found 234 pairs

🔄 Shuffling 2691 training/validation pairs...

📊 Split Summary:
   Train: 2152 pairs
   Val:   269 pairs
   Test:  234 pairs

📦 Copying files to /content/drive/MyDrive/oil_spill_reorganized...
------------------------------------------------------------
Copying to train: 100%|████████| 2152/2152 [05:23<00:00]
✅ Train: 2152/2152 pairs copied
Copying to val: 100%|████████| 269/269 [00:42<00:00]
✅ Val:   269/269 pairs copied
Copying to test: 100%|████████| 234/234 [00:37<00:00]
✅ Test:  234/234 pairs copied

============================================================
✅ Reorganization Complete!
============================================================
```
