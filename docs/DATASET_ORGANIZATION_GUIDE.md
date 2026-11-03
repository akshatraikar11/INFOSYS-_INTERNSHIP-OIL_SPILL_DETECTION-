# Zenodo Dataset Organization - Best Practices

## Should You Reorganize?

### ✅ **YES, reorganize if:**
- You want a simpler structure for easier loading
- You're doing standard ML training workflows
- You don't need to track which part each file came from
- You want to use standard train/val/test splits

### ⚠️ **Consider keeping original structure if:**
- You need to reference back to original dataset organization
- You're doing research that requires citing specific parts
- You want to preserve the dataset creators' original split
- You're sharing/reproducing published results

## Recommended Approach

### Option 1: Respect Original Split (Recommended)
```
Part1 + Part2 → train/val (e.g., 80/20 or 90/10)
Part3 → test (keep as-is, don't split)
```

**Why?**
- Part3 is explicitly labeled "Test" by dataset creators
- Maintains dataset integrity
- Better for reproducibility
- Follows ML best practices (test set should be separate)

### Option 2: Custom Split
```
Part1 + Part2 + Part3 → train/val/test (e.g., 80/10/10)
```

**When to use:**
- If Part3 is too small
- If you want more control over splits
- If you're doing cross-validation

## Current Script Behavior

The current script does:
- Part1 + Part2 → shuffled → split into train (80%), val (10%), test (10%)
- Part3 → test (if found)

**Issue:** This mixes Part1+Part2 into test set, which may not be ideal.

## Better Approach

Update the script to:
1. **Part1 + Part2** → Split into **train/val only** (e.g., 90/10 or 80/20)
2. **Part3** → Use as **test set** (don't split it)

This respects the dataset creators' intention that Part3 is the test set.
