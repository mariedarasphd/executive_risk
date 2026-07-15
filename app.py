#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic Script - Finds exact crash point
"""

import pathlib
import sys

print("=== STEP 1: Imports ===")
try:
    import pandas as pd
    print("✓ pandas imported")
except Exception as e:
    print(f"✗ pandas failed: {e}")
    sys.exit(1)

try:
    import streamlit as st
    print("✓ streamlit imported")
except Exception as e:
    print(f"✗ streamlit failed: {e}")
    sys.exit(1)

# Paths
ROOT_DIR = pathlib.Path(__file__).parent
DATA_PATH = ROOT_DIR / "demo_nsfw_personal.csv"

print(f"\n=== STEP 2: Paths ===")
print(f"Script location: {ROOT_DIR}")
print(f"Data path: {DATA_PATH}")

# Check if file exists
print(f"\n=== STEP 3: File Exists? ===")
print(f"File exists: {DATA_PATH.exists()}")
print(f"Is file: {DATA_PATH.is_file()}")

if DATA_PATH.is_file():
    print(f"File size: {DATA_PATH.stat().st_size / 1024:.2f} KB")
else:
    print("FILE NOT FOUND - Check your directory structure!")
    sys.exit(1)

print("\n=== STEP 4: Page Config ===")
st.set_page_config(page_title="Test Dashboard", page_icon="🔍", layout="wide")
print("✓ Page config set")

print("\n=== STEP 5: Load CSV ===")
try:
    df = pd.read_csv(DATA_PATH)
    print(f"✓ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
except Exception as e:
    print(f"✗ CSV load failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== STEP 6: Render Content ===")
st.title("🔍 Diagnostic Dashboard")
st.write(f"**Rows:** {len(df)}")
st.write(f"**Columns:** {df.columns.tolist()}")
st.dataframe(df.head())

print("✓ Dashboard rendered successfully")
