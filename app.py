#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Executive Risk Dashboard – Simplified Crash-Proof Version
"""

import pathlib
import pandas as pd
import streamlit as st

# Paths
ROOT_DIR = pathlib.Path(__file__).parent
DATA_PATH = ROOT_DIR / "demo_nsfw_personal.csv"
LOGO_PATH = ROOT_DIR / "logo.png"

# Page config
st.set_page_config(page_title="Executive Risk Dashboard", page_icon="🔍", layout="wide")

# Basic CSS
st.markdown("""
<style>
body { background-color: #0ABAB5; color: #ffffff; }
[data-testid="stSidebar"] { background-color: #0ABAB5; }
.block-container { padding-top: 40px; }
</style>
""", unsafe_allow_html=True)

# Logo
if LOGO_PATH.is_file():
    st.sidebar.image(str(LOGO_PATH), width=120)

# Load data
if not DATA_PATH.is_file():
    st.error(f"❌ Data file not found at: {DATA_PATH}")
    st.stop()

try:
    df = pd.read_csv(DATA_PATH)
    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
    print(f"[SUCCESS] CSV loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"[COLUMNS] {df.columns.tolist()}")
except Exception as e:
    st.error(f"❌ Error loading CSV: {e}")
    st.stop()

# Show columns for debugging
st.title("🔎 Executive Risk Dashboard")
st.subheader("📋 Available Columns")
st.write(df.columns.tolist())
st.write(f"**Total columns:** {len(df.columns)}")

st.markdown("---")

# Show first 5 rows
st.subheader("📊 Sample Data (First 5 Rows)")
st.dataframe(df.head(), use_container_width=True, height=300)

# Show basic metrics
st.markdown("---")
st.subheader("📈 Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rows", f"{len(df):,}")
with col2:
    st.metric("Columns", f"{len(df.columns)}")
with col3:
    if 'exec_id' in df.columns:
        st.metric("Unique Executives", f"{df['exec_id'].nunique():,}")
    else:
        st.metric("Unique Executives", "N/A")

# Download button
def to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_bytes = to_csv(df)
st.download_button(
    label="💾 Download Full Dataset as CSV",
    data=csv_bytes,
    file_name="executive_risk_full.csv",
    mime="text/csv",
)

st.caption("© 2025 Your Company – Internal risk dashboard.")
