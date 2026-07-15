#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Executive Risk Dashboard – With Vectorized Profanity Masking
"""

import pathlib
import pandas as pd
import streamlit as st

# Paths
ROOT_DIR = pathlib.Path(__file__).parent
DATA_PATH = ROOT_DIR / "demo_nsfw_personal.csv"
LOGO_PATH = ROOT_DIR / "logo.png"

# Page Config
st.set_page_config(
    page_title="Executive Risk Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""
<style>
body { background-color: #0ABAB5; color: #ffffff; }
[data-testid="stSidebar"] { background-color: #0ABAB5; }
section[data-testid="stHeader"] { background-color: #0ABAB5; }
footer { background-color: #0ABAB5; }
.block-container { padding-top: 40px; }
</style>
""", unsafe_allow_html=True)

# Logo
if LOGO_PATH.is_file():
    st.sidebar.image(str(LOGO_PATH), width=120)
else:
    st.sidebar.warning("⚠️ logo.png not found")

# Load Data
@st.cache_data(ttl=86_400)
def load_data() -> pd.DataFrame:
    if not DATA_PATH.is_file():
        st.error(f"❌ Data file not found at `{DATA_PATH}`")
        st.stop()
    
    df = pd.read_csv(DATA_PATH, encoding="utf-8")

    # Convert timestamp if exists
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Boolean columns
    for col in ["over_limit", "flag_nsfw", "flag_fin", "flag_compliance"]:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    # ===== PROFANITY MASKING USING VECTORIZED OPERATIONS =====
    profanity_words = ["fuck", "shit", "shitty", "cunt", "bitch", "ass", "damn", "crap", "piss", "dick"]

    # Vectorized masking - converts to lowercase, replaces word-by-word
    df["email_message_masked"] = df["email_message"].astype(str).str.lower()
    df["message_masked"] = df["message"].astype(str).str.lower()

    for word in profanity_words:
        replacement = "*" * len(word)
        df["email_message_masked"] = df["email_message_masked"].str.replace(word, replacement, case=False, regex=False)
        df["message_masked"] = df["message_masked"].str.replace(word, replacement, case=False, regex=False)

    # Truncate long messages
    df["email_message_masked"] = df["email_message_masked"].str[:500].apply(lambda x: x + "..." if len(x) == 500 else x)
    df["message_masked"] = df["message_masked"].str[:500].apply(lambda x: x + "..." if len(x) == 500 else x)

    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
    return df.copy()

df = load_data()

# Title
st.title("🔎 Executive Risk Dashboard")
st.markdown("Risk monitoring dashboard for executive communications.")

# Sidebar Filters
st.sidebar.header("🔧 Filters")

exec_options = sorted(df["exec_id"].unique()) if "exec_id" in df.columns else []
selected_execs = st.sidebar.multiselect("👤 Executive(s)", options=exec_options, default=[], help="Select employee IDs")

show_nsfw = st.sidebar.checkbox("🔞 NSFW chats only", value=False, help="Filter where flag_nsfw = True")
show_over_limit = st.sidebar.checkbox("⚠️ Over-limit only", value=False, help="Filter where over_limit = True")

# Apply Filters
filtered = df.copy()
if selected_execs:
    filtered = filtered[filtered["exec_id"].isin(selected_execs)]
if show_nsfw and "flag_nsfw" in filtered.columns:
    filtered = filtered[filtered["flag_nsfw"] == True]
if show_over_limit and "over_limit" in filtered.columns:
    filtered = filtered[filtered["over_limit"] == True]

# Metrics
st.subheader("📊 Overview")
col_a, col_b, col_c = st.columns(3)
with col_a:
    val = f"{df['exec_id'].nunique():,}" if "exec_id" in df.columns else "N/A"
    st.metric(label="Total Employees", value=val)
with col_b:
    val = f"{int(df['flag_nsfw'].sum()):,}" if "flag_nsfw" in df.columns else "N/A"
    st.metric(label="NSFW Chats", value=val)
with col_c:
    val = f"{int(df['over_limit'].sum()):,}" if "over_limit" in df.columns else "N/A"
    st.metric(label="Over Limit", value=val)
st.markdown("---")

# Display Table
st.subheader("🗂️ Filtered Data")
st.dataframe(filtered, use_container_width=True, height=500, hide_index=True)

# Download
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Download CSV",
    data=csv_bytes,
    file_name="filtered_executive_risk.csv",
    mime="text/csv",
)

st.caption("© 2025 Your Company – Internal risk dashboard.")
