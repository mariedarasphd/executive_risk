#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Executive Risk Dashboard – Absolute Minimal Version
"""

import pathlib
import streamlit as st
import pandas as pd

# Paths
ROOT_DIR = pathlib.Path(__file__).parent
DATA_PATH = ROOT_DIR / "demo_nsfw_personal.csv"
LOGO_PATH = ROOT_DIR / "logo.png"

# Page Config
st.set_page_config(page_title="Dashboard", page_icon="🔍", layout="wide")

# CSS
st.markdown("<style>body{background:#0ABAB5;color:#fff}.stDataFrame{overflow-x:auto}</style>", unsafe_allow_html=True)

# Logo
if LOGO_PATH.is_file():
    st.sidebar.image(str(LOGO_PATH), width=120)

# Load Data - NO CACHE, SIMPLE READ
try:
    df = pd.read_csv(DATA_PATH, encoding="utf-8")
    st.sidebar.success(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
except Exception as e:
    st.error(f"❌ Failed to load: {e}")
    st.stop()

# Show available columns
st.title("🔎 Executive Risk Dashboard")
st.write(f"**Columns ({len(df.columns)}):** {', '.join(df.columns.tolist())}")

st.markdown("---")

# Simple metrics
col_a, col_b = st.columns(2)
with col_a:
    st.metric("Total Rows", f"{len(df):,}")
with col_b:
    if "exec_id" in df.columns:
        st.metric("Unique Executives", f"{df['exec_id'].nunique():,}")

st.markdown("---")

# Show ALL data with scrollbar
st.subheader("🗂️ Data View")
try:
    st.dataframe(df, use_container_width=True, height=400)
    st.success("Table rendered successfully!")
except Exception as e:
    st.error(f"❌ Table failed: {e}")
    st.write(df.head().to_html())  # Fallback HTML display

# Download
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button("💾 Download CSV", data=csv_bytes, file_name="data.csv", mime="text/csv")

