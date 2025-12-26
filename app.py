# -----------------------------------------------------------------
@st.cache_data(ttl=86_400)   # cache for 24 h (refresh daily)
def load_data() -> pd.DataFrame:
    """Read demo_nsfw_personal.csv in chunks and keep only needed columns."""
    """Read demo_nsfw_personal.csv in chunks, keep only needed columns,
       and add any missing columns with safe default values."""
    if not DATA_PATH.is_file():
        st.error(f"❌ Data file not found at `{DATA_PATH}`")
        st.stop()
@@ -111,7 +112,9 @@ def load_data() -> pd.DataFrame:
            ),
            desc="Reading CSV",
        ):
            # Cast boolean columns (if they exist in this chunk)
            # -------------------------------------------------
            # Cast known boolean columns (if they exist in this chunk)
            # -------------------------------------------------
            for col in [
                "risk_flag_email",
                "flag_nsfw",
@@ -124,7 +127,9 @@ def load_data() -> pd.DataFrame:
                if col in chunk.columns:
                    chunk[col] = chunk[col].astype(bool)

            # -------------------------------------------------
            # Convert timestamp column (if present)
            # -------------------------------------------------
            if "ts" in chunk.columns:
                chunk["ts"] = pd.to_datetime(chunk["ts"], utc=True, errors="coerce")

@@ -135,7 +140,36 @@ def load_data() -> pd.DataFrame:
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
            # Boolean columns → default False
            df[col] = False
        elif col in {"email_sentiment", "chat_sentiment"}:
            # Sentiment scores → default 0.0 (neutral)
            df[col] = 0.0
        else:
            # All other missing columns → empty string (or 0 for numeric)
            if col in {"amt_usd"}:
                df[col] = 0.0
            else:
                df[col] = ""

    # -------------------------------------------------
    # Success message in the sidebar
    # -------------------------------------------------
    st.sidebar.success(f"✅ Loaded {len(df):,} rows")
    print(f"[INFO] CSV loaded – rows: {len(df):,}, cols: {len(df.columns)}")
    return df.copy()
@@ -243,14 +277,15 @@ def load_data() -> pd.DataFrame:
        value=f"{df['exec_id'].nunique():,}"
    )
with col_b:
    # Use .get() to avoid KeyError if the column is missing
    st.metric(
        label="Risky e‑mail execs",
        value=f"{df['risk_flag_email'].sum():,}"
        value=f"{df.get('risk_flag_email', pd.Series([False])).sum():,}"
    )
with col_c:
    st.metric(
        label="NSFW chats",
        value=f"{df['flag_nsfw'].sum():,}"
        value=f"{df.get('flag_nsfw', pd.Series([False])).sum():,}"
    )
st.markdown("---")
