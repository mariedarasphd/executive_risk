#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Executive Risk Dashboard – Streamlit app

- Theme (Tiffany blue) and logo are defined directly in this file.
- Data source: demo_nsfw_personal.csv (must be in the repo root).
"""

import pathlib
import re
import pandas as pd
import streamlit as st
from tqdm import tqdm   # optional – provides a progress bar while reading chunks

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
# 2️⃣  Inject Tiffany‑blue CSS (the **only** place we call markdown)
# -----------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ---------- Global page styling ---------- */
body {
    background-color: #0ABAB5;   /* Tiffany blue */
    color: #ffffff;              /* White text */
}

/* ---------- Sidebar, header & footer ---------- */
[data-testid="stSidebar"] { background-color: #0ABAB5; }
section[data-testid="stHeader"] { background-color: #0ABAB5; }
footer { background-color: #0ABAB5; }

/* ---------- Reduce vertical padding & add top space ---------- */
.block-container {
    padding-top: 40px;
    padding-bottom: 0rem;
}

/* ---------- Logo image sizing ---------- */
.logo-img {
    max-height: 60px;
    margin-right: 12px;
}

/* ---------- Table scrolling fix ---------- */
.stDataFrame {
    overflow-x: auto;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 3️⃣  Show the logo in the sidebar
# -----------------------------------------------------------------
if LOGO_PATH.is_file():
    st.sidebar.image(str(LOGO_PATH), width=120)
else:
    st.sidebar.warning(
        "⚠️ logo.png not found – please add it to the repository root."
    )

# -----------------------------------------------------------------
# 4️⃣  Load the CSV (cached – runs only once per session)
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

    CHUNK_SIZE = 200_000
    chunks = []

    with st.spinner("⏳ Loading CSV in chunks…"):
        for chunk in tqdm(
            pd.read_csv(
                DATA_PATH,
                engine="python",
                encoding="utf-8",
                usecols=lambda c: c in needed_cols,
                chunksize=CHUNK_SIZE,
            ),
            desc="Reading CSV",
        ):
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

            if "ts" in chunk.columns:
                chunk["ts"] = pd.to_datetime(chunk["ts"], utc=True, errors="coerce")

            chunks.append(chunk)

    df = pd.concat(chunks, ignore_index=True)

    missing = set(needed_cols) - set(df.columns)

    for col in missing:
        if col in {
            "risk_flag_email",
            "flag_nsfw",
            "flag_fin",
            "flag_compliance",
            "over_limit",
            "personal_use",
            "flag_compliance_txn",
        }:
            df[col] = False
        elif col in {"email_sentiment", "chat_sentiment"}:
            df[col] = 0.0
        else:
            if col == "amt_usd":
                df[col] = 0.0
            else:
                df[col] = ""

    def mask_profanity(text: str) -> str:
        if not isinstance(text, str):
            return ""
        profanity_words = [
            "fuck", "shit", "shitty", "cunt", "bitch",
            "ass", "damn", "crap", "piss", "dick"
        ]
        pattern = re.compile(r"\b(" + "|".join(profanity_words) + r")\b", flags=re.I)

        def _replace(m):
            return "*" * len(m.group())

        return pattern.sub(_replace, text)

    df["email_message_masked"] = df["email_message"].astype(str).apply(mask_profanity)
    df["message_masked"]       = df["message"].astype(str).apply(mask_profanity)

    # Truncate long text columns for display (keeps full data in CSV export)
    df["email_message_masked"] = df["email_message_masked"].apply(lambda x: x[:500] + "..." if len(x) > 500 else x)
    df["message_masked"]       = df["message_masked"].apply(lambda x: x[:500] + "..." if len(x) > 500 else x)

    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
    print(f"[INFO] CSV loaded – rows: {len(df):,}, cols: {len(df.columns)}")
    return df.copy()


df = load_data()

# -----------------------------------------------------------------
# 5️⃣  Title & description
# -----------------------------------------------------------------
st.title("🔎 Executive Risk Dashboard")
st.markdown(
    """
    A lightweight demo that joins **customer remarks**, **sentiment analysis**, and **synthetic transaction data**, 
    then highlights high‑value, negative‑sentiment cases.
    """
)

# -----------------------------------------------------------------
# 6️⃣  Sidebar filters
# -----------------------------------------------------------------
st.sidebar.header("🔧 Filters")

exec_options = sorted(df["exec_id"].unique())
selected_execs = st.sidebar.multiselect(
    "👤 Executive(s)",
    options=exec_options,
    default=[],
    help="Select one or more employee IDs."
)

show_risky_email = st.sidebar.checkbox(
    "🚩 Show only risky e‑mail rows",
    value=False,
)

show_nsfw_chat = st.sidebar.checkbox(
    "🔞 Show only NSFW chat rows",
    value=False,
)

if "category" in df.columns:
    cat_options = sorted(df["category"].dropna().unique())
    selected_cats = st.sidebar.multiselect(
        "💳 Transaction category",
        options=cat_options,
        default=[],
        help="Filter synthetic credit‑card transactions by category."
    )
else:
    selected_cats = []

show_over_limit = st.sidebar.checkbox(
    "⚠️ Show only over‑limit transactions",
    value=False,
)

show_personal_use = st.sidebar.checkbox(
    "🧾 Show only personal‑use transactions",
    value=False,
)

# -----------------------------------------------------------------
# 7️⃣  Apply filters
# -----------------------------------------------------------------
filtered = df.copy()

if selected_execs:
    filtered = filtered[filtered["exec_id"].isin(selected_execs)]

if show_risky_email:
    filtered = filtered[filtered["risk_flag_email"]]

if show_nsfw_chat:
    filtered = filtered[filtered["flag_nsfw"]]

if selected_cats:
    filtered = filtered[filtered["category"].isin(selected_cats)]

if show_over_limit:
    filtered = filtered[filtered["over_limit"]]

if show_personal_use:
    filtered = filtered[filtered["personal_use"]]

# -----------------------------------------------------------------
# 8️⃣  Metrics (overview)
# -----------------------------------------------------------------
st.subheader("📊 Overview")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(label="Total Employees", value=f"{df['exec_id'].nunique():,}")
with col_b:
    st.metric(label="Risky e‑mail execs", value=f"{df.get('risk_flag_email', pd.Series([False])).sum():,}")
with col_c:
    st.metric(label="NSFW chats", value=f"{df.get('flag_nsfw', pd.Series([False])).sum():,}")
st.markdown("---")

# -----------------------------------------------------------------
# 9️⃣  Show the filtered dataframe (improved column display)
# -----------------------------------------------------------------
st.subheader("🗂️ Filtered data")

# Group columns for better organization
tab1, tab2 = st.tabs(["📧 Communications", "💳 Transactions"])

with tab1:
    comm_cols = [
        "exec_id",
        "email_message_masked",
        "email_sentiment",
        "risk_flag_email",
        "message_masked",
        "flag_nsfw",
        "chat_sentiment",
        "ts",
    ]
    
    display_comm = filtered[comm_cols].copy()
    for col in display_comm.columns:
        if display_comm[col].dtype == 'object':
            display_comm[col] = display_comm[col].fillna('')
    
    st.dataframe(display_comm, use_container_width=True, height=400, hide_index=True)

with tab2:
    txn_cols = [
        "exec_id",
        "flag_fin",
        "flag_compliance",
        "category",
        "amt_usd",
        "over_limit",
        "personal_use",
        "flag_compliance_txn",
    ]
    
    display_txn = filtered[txn_cols].copy()
    for col in display_txn.columns:
        if display_txn[col].dtype == 'object':
            display_txn[col] = display_txn[col].fillna('')
    
    st.dataframe(display_txn, use_container_width=True, height=400, hide_index=True)

# -----------------------------------------------------------------
# 🔟  Download button
# -----------------------------------------------------------------
def convert_df_to_csv(df_: pd.DataFrame) -> bytes:
    return df_.to_csv(index=False).encode("utf-8")

csv_bytes = convert_df_to_csv(filtered)

st.download_button(
    label="💾 Download all filtered data as CSV",
    data=csv_bytes,
    file_name="filtered_executive_risk.csv",
    mime="text/csv",
)

# -----------------------------------------------------------------
# 🔚  Footer
# -----------------------------------------------------------------
st.caption(
    "© 2025 Your Company – Internal risk dashboard. "
    "Data is synthetic except for the Enron e‑mail sample."
)
