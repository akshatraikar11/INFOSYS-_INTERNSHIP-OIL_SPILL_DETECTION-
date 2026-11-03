# Zenodo SAR Oil Spill Dataset – Folder Structure

After downloading and extracting the Zenodo Sentinel-1 SAR dataset (Parts I, II, III), the folder structure should be:

## Local Windows/Linux Setup

If you've downloaded the 90GB dataset locally (Parts I, II, III), extract the `.7z` archives and organize them as follows:

```
zenodo_dataset/  (or your chosen base directory)
  Part1/
    01_Train_Val_Oil_Spill_images/
      Oil/
    01_Train_Val_Oil_Spill_mask/
      Mask_oil/
  Part2/
    01_Train_Val_Lookalike_images/
      Lookalike/
    01_Train_Val_Lookalike_mask/
      Mask_lookalike/
    01_Train_Val_No_Oil_Images/
      No_oil/
    01_Train_Val_No_Oil_mask/
      Mask_no_oil/
  Part3/
    02_Test_images_and_ground_truth/
      Images/
        Lookalike/
        No oil/
        Oil/
      Mask/
        Lookalike/
        No oil/
        Oil/
```

## Google Colab Setup

After downloading and extracting the Zenodo Sentinel-1 SAR dataset (Parts I, II, III) via the Colab notebook, the layout on Google Drive is:

```
My Drive/
  oil_spill/
    Part1/
      01_Train_Val_Oil_Spill_images/
        Oil/
      01_Train_Val_Oil_Spill_mask/
        Mask_oil/
    Part2/
      01_Train_Val_Lookalike_images/
        Lookalike/
      01_Train_Val_Lookalike_mask/
        Mask_lookalike/
      01_Train_Val_No_Oil_Images/
        No_oil/
      01_Train_Val_No_Oil_mask/
        Mask_no_oil/
    Part3/
      02_Test_images_and_ground_truth/
        Images/
          Lookalike/
          No oil/
          Oil/
        Mask/
          Lookalike/
          No oil/
          Oil/
```

## Paths for Training

### Local Windows/Linux

1. **Extract the dataset**: Extract all three parts (Part1, Part2, Part3) from the `.7z` archives into a single base directory (e.g., `zenodo_dataset/`).

2. **Update the notebook**: In `Oil_Spill_Detection.ipynb`, find the Zenodo SAR cell and:
   - Set `USE_ZENODO_SAR = True`
   - Update `_BASE` to point to your extracted dataset location:
     ```python
     _BASE = r"C:\Users\YourName\Downloads\zenodo_dataset"  # Windows
     # or
     _BASE = "/home/user/datasets/zenodo_dataset"  # Linux/Mac
     ```

3. **The notebook will automatically detect** whether you're running locally or on Colab and use the appropriate paths.

### Google Colab

With Drive mounted at `/content/drive` and base folder `oil_spill`:

| Part | Image dir | Mask dir |
|------|-----------|----------|
| Part1 | `.../oil_spill/Part1/01_Train_Val_Oil_Spill_images` | `.../oil_spill/Part1/01_Train_Val_Oil_Spill_mask` |
| Part2 (Lookalike) | `.../oil_spill/Part2/01_Train_Val_Lookalike_images` | `.../oil_spill/Part2/01_Train_Val_Lookalike_mask` |
| Part2 (No oil) | `.../oil_spill/Part2/01_Train_Val_No_Oil_Images` | `.../oil_spill/Part2/01_Train_Val_No_Oil_mask` |
| Part3 (test) | `.../oil_spill/Part3/02_Test_images_and_ground_truth/Images` | `.../oil_spill/Part3/02_Test_images_and_ground_truth/Mask` |

The notebook automatically detects Colab environment and uses `/content/drive/MyDrive/oil_spill` as the base path.

## Loading the Dataset

The `scripts/load_zenodo_sar.py` script handles:
- Loading TIFF images (SAR format)
- Finding corresponding mask files
- Resizing to target dimensions
- Normalizing SAR data (16-bit to [0,1] range)
- Handling multiple subdirectories (Oil/, Lookalike/, No_oil/, etc.)

The script is automatically imported when `USE_ZENODO_SAR = True` in the notebook.

## Dataset Size

- **Total size**: ~90GB (Parts I, II, III combined)
- **Part1**: Oil spill training/validation images and masks
- **Part2**: Lookalike and No-oil training/validation images and masks
- **Part3**: Test images and masks (optional, commented out by default)

## Troubleshooting

1. **"No valid image-mask pairs found"**: 
   - Check that your `_BASE` path is correct
   - Verify the folder structure matches the expected layout
   - Ensure `.tif`/`.tiff` files are present in the image directories

2. **Memory issues with 90GB dataset**:
   - Consider loading subsets by uncommenting specific parts
   - Use `max_samples` parameter in `load_zenodo_sar()` to limit dataset size
   - Process in batches if needed

3. **Path issues on Windows**:
   - Use raw strings: `r"C:\path\to\dataset"`
   - Or forward slashes: `"C:/path/to/dataset"`
   - Avoid trailing slashes in `_BASE`
