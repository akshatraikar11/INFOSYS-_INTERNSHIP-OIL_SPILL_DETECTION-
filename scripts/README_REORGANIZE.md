# Reorganizing Zenodo Dataset

This guide helps you reorganize the 90GB Zenodo dataset into a simpler structure that's easier to use in the notebook.

## Why Reorganize?

The original Zenodo dataset has a complex nested structure:
```
Part1/01_Train_Val_Oil_Spill_images/Oil/
Part2/01_Train_Val_Lookalike_images/Lookalike/
Part2/01_Train_Val_No_Oil_Images/No_oil/
Part3/02_Test_images_and_ground_truth/Images/
```

After reorganization, you get a clean structure:
```
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
```

This makes it much easier to load data in the notebook!

## Step 1: Run the Reorganization Script

```bash
python scripts/reorganize_zenodo_dataset.py \
    --source "C:/path/to/original/zenodo_dataset" \
    --dest "C:/path/to/reorganized/oil_spill" \
    --train-split 0.8 \
    --val-split 0.1
```

**Parameters:**
- `--source`: Path to your original dataset containing `Part1/`, `Part2/`, `Part3/`
- `--dest`: Where to create the new simplified structure
- `--train-split`: Fraction for training (default: 0.8 = 80%)
- `--val-split`: Fraction for validation (default: 0.1 = 10%)
- `--seed`: Random seed for reproducibility (default: 42)

**Example (Windows):**
```bash
python scripts/reorganize_zenodo_dataset.py \
    --source "C:\Users\Akshat\Downloads\zenodo_dataset" \
    --dest "C:\Users\Akshat\OneDrive\Documents\DeepSpill\oil_spill" \
    --train-split 0.8 \
    --val-split 0.1
```

**Example (Linux/Mac):**
```bash
python scripts/reorganize_zenodo_dataset.py \
    --source "/home/user/datasets/zenodo_dataset" \
    --dest "/home/user/datasets/oil_spill" \
    --train-split 0.8 \
    --val-split 0.1
```

## Step 2: Update Notebook Settings

After reorganization, update `Oil_Spill_Detection.ipynb`:

1. Set `USE_SIMPLIFIED_STRUCTURE = True`
2. Update `_BASE` to point to your reorganized dataset:
   ```python
   _BASE = r"C:\Users\Akshat\OneDrive\Documents\DeepSpill\oil_spill"
   ```

That's it! The notebook will automatically load from the simplified structure.

## What the Script Does

1. **Finds all image-mask pairs** from Part1, Part2, and Part3
2. **Splits them** into train (80%), val (10%), and test (10%) sets
3. **Copies files** to the new structure, ensuring masks match image names
4. **Preserves file formats** (TIFF, PNG, etc.)

## Notes

- The script **copies** files (doesn't move), so your original dataset remains intact
- Part3 test set is kept separate if it exists
- If Part3 doesn't exist, remaining data after train/val split becomes test set
- All files are shuffled before splitting for better distribution

## Troubleshooting

**"No image-mask pairs found"**
- Check that your `--source` path contains `Part1/`, `Part2/`, `Part3/` folders
- Verify the folder structure matches the expected layout

**"Permission denied"**
- Make sure you have write permissions to the `--dest` directory
- On Windows, run as administrator if needed

**Out of disk space**
- The script copies files, so you need ~90GB free space for the destination
- Consider using `--train-split 0.9` to reduce test set size if needed
