#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Executive Risk Dashboard – Streamlit app
---------------------------------------
* Theme (Tiffany blue) and logo are defined directly in this file.
* Data source: demo_nsfw_personal.csv (must be in the repo root).
"""

import pathlib
import pandas as pd
import streamlit as st
from tqdm import tqdm  # optional – provides a progress bar while reading chunks

# -----------------------------------------------------------------
# 0️⃣  Paths & constants
# -----------------------------------------------------------------
ROOT_DIR   = pathlib.Path(__file__).parent          # folder where app.py lives
DATA_PATH  = ROOT_DIR / "demo_nsfw_personal.csv"
LOGO_PATH  = ROOT_DIR / "logo.png"

# -----------------------------------------------------------------
# 1️⃣  Page configuration (title, icon, layout)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Executive Risk Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------
# 2️⃣  Inject Tiffany‑blue CSS (no config.toml needed)
# -----------------------------------------------------------------
CUSTOM_CSS = """
/* Global page styling */
body {
    background-color: #0ABAB5;   /* Tiffany blue */
    color: #ffffff;              /* White text */
}

/* Sidebar, header & footer */
[data-testid="stSidebar"] { background-color: #0ABAB5; }
section[data-testid="stHeader"] { background-color: #0ABAB5; }
footer { background-color: #0ABAB5; }

/* Reduce vertical padding */
.block-container { padding-top: 0rem; padding-bottom: 0rem; }

/* Logo image sizing (used in the sidebar) */
.logo-img { max-height: 60px; margin-right: 12px; }
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# -----------------------------------------------------------------
# 3️⃣  Show the logo in the sidebar
# -----------------------------------------------------------------
if LOGO_PATH.is_file():
    st.sidebar.image(str(LOGO_PATH), width=120)   # adjust width if you like
else:
    st.sidebar.warning(
        "⚠️ logo.png not found – please add it to the repository root."
    )

# -----------------------------------------------------------------
# 4️⃣  Load the CSV (cached – runs only once per session)
# -----------------------------------------------------------------
@st.cache_data(ttl=86_400)   # cache for 24 h (refresh daily)
def load_data() -> pd.DataFrame:
    """Read demo_nsfw_personal.csv in chunks, keep only needed columns."""
    if not DATA_PATH.is_file():
        st.error(f"❌ Data file not found at `{DATA_PATH}`")
        st.stop()

    # -------------------------------------------------
    # Columns we actually need for the dashboard
    # -------------------------------------------------
    needed_cols = [
        "exec_id",
        "email_message",
        "email_sentiment",
        "risk_flag_email",
        "message",
        "flag_nsfw",
        "flag_fin",
        "flag_compliance",
        "chat_sentiment",
        "ts",
        "category",
        "amt_usd",
        "over_limit",
        "personal_use",
        "flag_compliance_txn",
    ]

    # -------------------------------------------------
    # Chunked read – 200 k rows per chunk (adjust if you wish)
    # -------------------------------------------------
    CHUNK_SIZE = 200_000
    chunks = []

    with st.spinner("⏳ Loading CSV in chunks…"):
        # tqdm gives a nice progress bar in the UI
        for chunk in tqdm(
            pd.read_csv(
                DATA_PATH,
                engine="python",
                encoding="utf-8",
                usecols=lambda c: c in needed_cols,   # keep only needed columns
                chunksize=CHUNK_SIZE,
            ),
            desc="Reading CSV",
        ):
            # Cast boolean columns (if they exist in this chunk)
            for col in [
                "risk_flag_email",
                "flag_nsfw",
                "flag_fin",
                "flag_compliance",
                "over_limit",
                "personal_use",
                "flag_compliance_txn",
            ]:
                if col in chunk.columns:
                    chunk[col] = chunk[col].astype(bool)

            # Convert timestamp column (if present)
            if "ts" in chunk.columns:
                chunk["ts"] = pd.to_datetime(
                    chunk["ts"], utc=True, errors="coerce"
                )

            chunks.append(chunk)

    # -------------------------------------------------
    # Concatenate all chunks into a single DataFrame
    # -------------------------------------------------
    df = pd.concat(chunks, ignore_index=True)

    # Success message in the sidebar
    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
    print(f"[INFO] CSV loaded – rows: {len(df):,}, cols: {len(df.columns)}")
    return df.copy()

# Load the data (cached)
df = load_data()

# -----------------------------------------------------------------
# 5️⃣  Title & description
# -----------------------------------------------------------------
st.title("🔎 Executive Risk Dashboard")
st.markdown(
    """
    A lightweight demo that joins **customer remarks**, **sentiment analysis**, 
    and **synthetic transaction data**, then highlights high‑value, 
    negative‑sentiment cases.
    """
)

# -------------------------------------------------------
