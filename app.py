#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pre-flight Environment Check
"""

import sys

print("=" * 50)
print("ENVIRONMENT DIAGNOSTIC")
print("=" * 50)

# Check numpy version
try:
    import numpy as np
    print(f"✓ NumPy version: {np.__version__}")
    if np.__version__.startswith("2."):
        print("⚠️ WARNING: NumPy 2.x detected! This causes segfaults.")
        print("Need numpy==1.26.4 in requirements.txt")
    else:
        print("✓ NumPy version is 1.x (stable)")
except Exception as e:
    print(f"✗ NumPy import failed: {e}")
    sys.exit(1)

# Check pandas version
try:
    import pandas as pd
    print(f"✓ Pandas version: {pd.__version__}")
except Exception as e:
    print(f"✗ Pandas import failed: {e}")
    sys.exit(1)

# Check file exists
import pathlib
DATA_PATH = pathlib.Path(__file__).parent / "demo_nsfw_personal.csv"
print(f"\nFile exists: {DATA_PATH.exists()}")
if DATA_PATH.exists():
    print(f"File size: {DATA_PATH.stat().st_size / 1024:.2f} KB")
else:
    print("⚠️ FILE NOT FOUND - Check your path!")
    sys.exit(1)

# Try reading CSV
try:
    df = pd.read_csv(DATA_PATH, nrows=5)  # Just read first 5 rows
    print(f"✓ CSV read successful: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")
except Exception as e:
    print(f"✗ CSV read failed: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("ALL CHECKS PASSED - Safe to run Streamlit")
print("=" * 50)
