#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Executive Risk Dashboard – Tiffany Blue Theme Restored
"""

import pathlib
import re
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------
# Paths
# -----------------------------------------------------------------
ROOT_DIR = pathlib.Path(__file__).parent
DATA_PATH = ROOT_DIR / "demo_nsfw_personal.csv"
LOGO_PATH = ROOT_DIR / "logo.png"

# -----------------------------------------------------------------
# Page Config
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Executive Risk Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------
# CSS Styling – Tiffany Blue Theme
# -----------------------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #0ABAB5;
    color: #ffffff;
}
[data-testid="stSidebar"] { background-color: #0ABAB5; }
section[data-testid="stHeader"] { background-color: #0ABAB5; }
footer { background-color: #0ABAB5; }
.block-container {
    padding-top: 40px;
    padding-bottom: 0rem;
}
.logo-img {
    max-height: 60px;
    margin-right: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------
# Logo
# -----------------------------------------------------------------
if LOGO_PATH.is_file():
    st.sidebar.image(str(LOGO_PATH), width=120)
else:
    st.sidebar.warning("⚠️ logo.png not found")

# -----------------------------------------------------------------
# Load Data
# -----------------------------------------------------------------
@st.cache_data(ttl=86_400)
def load_data() -> pd.DataFrame:
    if not DATA_PATH.is_file():
        st.error(f"❌ Data file not found at `{DATA_PATH}`")
        st.stop()

    needed_cols = [
        "exec_id",
        "email_message",
        "email_sentiment",
        "message",
        "timestamp",
        "category",
        "amt_usd",
        "over_limit",
        "flag_nsfw",
        "flag_fin",
        "flag_compliance",
    ]

    # Load without tqdm to avoid segfault
    with st.spinner("⏳ Loading CSV..."):
        df = pd.read_csv(
            DATA_PATH,
            engine="python",
            encoding="utf-8",
            usecols=lambda c: c in needed_cols,
        )

    # Cast boolean columns
    for col in ["over_limit", "flag_nsfw", "flag_fin", "flag_compliance"]:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Profanity masking
    def mask_profanity(text: str) -> str:
        if not isinstance(text, str):
            return ""
        profanity_words = [
            "fuck", "shit", "shitty", "cunt", "bitch",
            "ass", "damn", "crap", "piss", "dick"
        ]
        pattern = re.compile(r"\b(" + "|".join(profanity_words) + r")\b", flags=re.I)
        return pattern.sub(lambda m: "*" * len(m.group()), text)

    df["email_message_masked"] = df["email_message"].astype(str).apply(mask_profanity)
    df["message_masked"] = df["message"].astype(str).apply(mask_profanity)

    # Truncate long messages
    df["email_message_masked"] = df["email_message_masked"].apply(lambda x: x[:500] + "..." if len(x) > 500 else x)
    df["message_masked"] = df["message_masked"].apply(lambda x: x[:500] + "..." if len(x) > 500 else x)

    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
    return df.copy()

df = load_data()

# -----------------------------------------------------------------
# Title & Description
# -----------------------------------------------------------------
st.title("🔎 Executive Risk Dashboard")
st.markdown(
    """
    A lightweight demo that joins **customer remarks**, **sentiment analysis**, and **synthetic transaction data**,
    then highlights high‑value, negative‑sentiment cases.
    """
)

# -----------------------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------------------
st.sidebar.header("🔧 Filters")

exec_options = sorted(df["exec_id"].unique())
selected_execs = st.sidebar.multiselect(
    "👤 Executive(s)",
    options=exec_options,
    default=[],
    help="Select one or more employee IDs."
)

show_risky_email = st.sidebar.checkbox("🚩 Show risky emails only", value=False)
show_nsfw_chat = st.sidebar.checkbox("🔞 Show NSFW chats only", value=False)

if "category" in df.columns:
    cat_options = sorted(df["category"].dropna().astype(str).unique())
    selected_cats = st.sidebar.multiselect(
        "💳 Transaction category",
        options=cat_options,
        default=[],
        help="Filter by category."
    )
else:
    selected_cats = []

show_over_limit = st.sidebar.checkbox("⚠️ Show over-limit only", value=False)

# -----------------------------------------------------------------
# Apply Filters
# -----------------------------------------------------------------
filtered = df.copy()

if selected_execs:
    filtered = filtered[filtered["exec_id"].isin(selected_execs)]
if show_risky_email:
    filtered = filtered[filtered["email_sentiment"] < 0] if "email_sentiment" in filtered.columns else filtered
if show_nsfw_chat:
    filtered = filtered[filtered["flag_nsfw"]]
if selected_cats:
    filtered = filtered[filtered["category"].isin(selected_cats)]
if show_over_limit:
    filtered = filtered[filtered["over_limit"]]

# -----------------------------------------------------------------
# Metrics
# -----------------------------------------------------------------
st.subheader("📊 Overview")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(label="Total Employees", value=f"{df['exec_id'].nunique():,}")
with col_b:
    st.metric(label="Negative Emails", value=f"{df['email_sentiment'].lt(0).sum():,}" if "email_sentiment" in df.columns else "N/A")
with col_c:
    st.metric(label="NSFW Chats", value=f"{df['flag_nsfw'].sum():,}" if "flag_nsfw" in df.columns else "N/A")
st.markdown("---")

# -----------------------------------------------------------------
# Display Table
# -----------------------------------------------------------------
st.subheader("🗂️ Filtered Data")

display_cols = [
    "exec_id",
    "email_message_masked",
    "email_sentiment",
    "message_masked",
    "flag_nsfw",
    "flag_fin",
    "flag_compliance",
    "timestamp",
    "category",
    "amt_usd",
    "over_limit",
]

display_df = filtered[[col for col in display_cols if col in filtered.columns]].copy()
for col in display_df.columns:
    if display_df[col].dtype == 'object':
        display_df[col] = display_df[col].fillna('')

st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)

# -----------------------------------------------------------------
# Download Button
# -----------------------------------------------------------------
def convert_df_to_csv(df_: pd.DataFrame) -> bytes:
    return df_.to_csv(index=False).encode("utf-8")

csv_bytes = convert_df_to_csv(filtered)

st.download_button(
    label="💾 Download filtered data as CSV",
    data=csv_bytes,
    file_name="filtered_executive_risk.csv",
    mime="text/csv",
)

# -----------------------------------------------------------------
# Footer
# -----------------------------------------------------------------
st.caption("© 2025 Your Company – Internal risk dashboard.")
