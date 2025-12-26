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
# 2️⃣  Inject Tiffany‑blue CSS (this is the ONLY line that matters)
# -----------------------------------------------------------------
CUSTOM_CSS = """
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
/* .block-container wraps the whole page content */
.block-container {
    padding-top: 40px;   /* push the title down so it isn’t cut off */
    padding-bottom: 0rem;
}

/* ---------- Logo image sizing (used in the sidebar) ---------- */
.logo-img {
    max-height: 60px;
    margin-right: 12px;
}
"""
# IMPORTANT: we actually pass the CSS string to markdown
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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
    """Read demo_nsfw_personal.csv in chunks, keep only needed columns,
    add any missing columns with safe defaults, and create masked text columns."""
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
            # -------------------------------------------------
            # Cast known boolean columns (if they exist in this chunk)
            # -------------------------------------------------
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

            # -------------------------------------------------
            # Convert timestamp column (if present)
            # -------------------------------------------------
            if "ts" in chunk.columns:
                chunk["ts"] = pd.to_datetime(chunk["ts"], utc=True, errors="coerce")

            chunks.append(chunk)

    # -------------------------------------------------
    # Concatenate all chunks into a single DataFrame
    # -------------------------------------------------
    df = pd.concat(chunks, ignore_index=True)

    # -------------------------------------------------
    # Add any missing columns with safe defaults
    # -------------------------------------------------
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
            df[col] = False                     # Boolean columns → default False
        elif col in {"email_sentiment", "chat_sentiment"}:
            df[col] = 0.0                       # Sentiment scores → neutral
        else:
            if col == "amt_usd":
                df[col] = 0.0
            else:
                df[col] = ""

    # -------------------------------------------------
    # ---------- PROFANITY MASKING ----------
    # -------------------------------------------------
    def mask_profanity(text: str) -> str:
        """Replace a short list of profane words with asterisks."""
        profanity_words = [
            "fuck", "shit", "shitty", "cunt", "bitch",
            "ass", "damn", "crap", "piss", "dick"
        ]
        pattern = re.compile(r"\b(" + "|".join(profanity_words) + r")\b", flags=re.I)

        def _replace(m):
            return "*" * len(m.group())

        return pattern.sub(_replace, text)

    # Create masked copies – keep originals for export if needed later
    df["email_message_masked"] = df["email_message"].astype(str).apply(mask_profanity)
    df["message_masked"]       = df["message"].astype(str).apply(mask_profanity)

    # -------------------------------------------------
    # Success message in the sidebar
    # -------------------------------------------------
    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
    print(f"[INFO] CSV loaded – rows: {len(df):,}, cols: {len(df.columns)}")
    return df.copy()


# -----------------------------------------------------------------
# Load the data (cached)
# -----------------------------------------------------------------
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

# 6.1 Executive selector (multi‑select)
exec_options = sorted(df["exec_id"].unique())
selected_execs = st.sidebar.multiselect(
    "👤 Executive(s)",
    options=exec_options,
    default=exec_options[:5],
    help="Select one or more employee IDs."
)

# 6.2 Risk‑flag toggles
show_risky_email = st.sidebar.checkbox(
    "🚩 Show only risky e‑mail rows",
    value=False,
    help="Filters to rows where `risk_flag_email` is True."
)

show_nsfw_chat = st.sidebar.checkbox(
    "🔞 Show only NSFW chat rows",
    value=False,
    help="Filters to rows where `flag_nsfw` is True."
)

# 6.3 Transaction category filter (if column exists)
if "category" in df.columns:
    cat_options = sorted(df["category"].dropna().unique())
    selected_cats = st.sidebar.multiselect(
        "💳 Transaction category",
        options=cat_options,
        default=cat_options,
        help="Filter synthetic credit‑card transactions by category."
    )
else:
    selected_cats = []   # no category column → no filtering on it

# 6.4 Over‑limit toggle
show_over_limit = st.sidebar.checkbox(
    "⚠️ Show only over‑limit transactions",
    value=False,
    help="Filters to rows where `over_limit` is True."
)

# 6.5 Personal‑use toggle
show_personal_use = st.sidebar.checkbox(
    "🧾 Show only personal‑use transactions",
    value=False,
    help="Filters to rows where `personal_use` is True."
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
    st.metric(
        label="Total Employees",
        value=f"{df['exec_id'].nunique():,}"
    )
with col_b:
    # Use .get() to avoid KeyError if the column is missing
    st.metric(
        label="Risky e‑mail execs",
        value=f"{df.get('risk_flag_email', pd.Series([False])).sum():,}"
    )
with col_c:
    st.metric(
        label="NSFW chats",
        value=f"{df.get('flag_nsfw', pd.Series([False])).sum():,}"
    )
st.markdown("---")

# -----------------------------------------------------------------
# 9️⃣  Show the filtered dataframe
# -----------------------------------------------------------------
st.subheader("🗂️ Filtered data")

display_cols = [
    "exec_id",
    "email_message_masked",   # masked version
    "email_sentiment",
    "risk_flag_email",
    "message_masked",         # masked version
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

st.dataframe(
    filtered[display_cols],
    use_container_width=True,
    height=500,
)

# -----------------------------------------------------------------
# 🔟  Download button – export filtered view as CSV
# -----------------------------------------------------------------
def convert_df_to_csv(df_: pd.DataFrame) -> bytes:
    """Return CSV bytes for Streamlit download button."""
    return df_.to_csv(index=False).encode("utf-8")

csv_bytes = convert_df_to_csv(filtered[display_cols])

st.download_button(
    label="💾 Download filtered view as CSV",
    data=csv_bytes,
    file_name="filtered_executive_risk.csv",
    mime="text/csv",
    help="Download the rows currently displayed in the table.",
)

# -----------------------------------------------------------------
# 🔚  Footer / disclaimer
# -----------------------------------------------------------------
st.caption(
    "© 2025 Your Company – Internal risk dashboard. "
    "Data is synthetic except for the Enron e‑mail sample."
)
