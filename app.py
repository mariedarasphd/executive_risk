# --------------------------------------------------------------
# app.py – Executive Risk Dashboard (with safe header spacing)
# --------------------------------------------------------------

import streamlit as st
import pandas as pd
import re

# ------------------------------------------------------------------
# 1️⃣  Page configuration – MUST be the FIRST Streamlit call!
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Executive Risk Dashboard",
    layout="wide"
)

# ------------------------------------------------------------------
# 2️⃣  Small CSS block – adds vertical space above the title/header
# ------------------------------------------------------------------
# The selector ".main" targets the main content area of a Streamlit page.
# Adjust the pixel value if you need more/less space.
st.markdown(
    """
    <style>
    .main {
        padding-top: 40px;   /* space above everything */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 3️⃣  Helper: very simple profanity masker
# ------------------------------------------------------------------
def mask_profanity(text: str) -> str:
    """Replace known profanity words with asterisks."""
    profanity_words = [
        "fuck", "shit", "shitty", "cunt", "bitch",
        "ass", "damn", "crap", "piss", "dick"
    ]

    def _replace(match):
        return "*" * len(match.group())

    pattern = re.compile(r"\b(" + "|".join(profanity_words) + r")\b", flags=re.I)
    return pattern.sub(_replace, text)


# ------------------------------------------------------------------
# 4️⃣  Load / build your data
# ------------------------------------------------------------------
# Replace this placeholder list with your real data source
sample_messages = [
    "My question still stands. What the fuck is that?",
    "There is loads of tea in my house but I hate it",
    "I woulda stuck with the swapped gender just for Rp purposes but like psssh if you're gonna have bandits rape a player have em take some dude's booty if you wanna be edgy",
    "@Reichtangle I've seen a pic of you. You're white as fuck",
    "and lately, his team said that there is a small group of people who know covfefe's meaning\\nthey blew it out of proportion and made it worse than it was\\nand I hate myself for knowing that much on that shitty ass joke"
]

df_raw = pd.DataFrame({"message": sample_messages})
df_raw["masked_message"] = df_raw["message"].apply(mask_profanity)


# ------------------------------------------------------------------
# 5️⃣  Page title (now fully visible thanks to the CSS padding)
# ------------------------------------------------------------------
st.title("🚦 Executive Risk Dashboard – NSFW / Harassment Monitor")

# ------------------------------------------------------------------
# 6️⃣  Sidebar controls
# ------------------------------------------------------------------
st.sidebar.header("Filters")
show_raw = st.sidebar.checkbox(
    "Show raw messages (requires authorization)", value=False
)

# ------------------------------------------------------------------
# 7️⃣  Main table – either masked or raw depending on the toggle
# ------------------------------------------------------------------
if show_raw:
    st.subheader("🔎 Messages – RAW (un‑masked)")
    st.dataframe(df_raw[["message"]])
else:
    st.subheader("🔎 Messages – Masked")
    st.dataframe(df_raw[["masked_message"]])

# ------------------------------------------------------------------
# 8️⃣  CSV export (full dataset, both columns)
# ------------------------------------------------------------------
def convert_df_to_csv(dataframe: pd.DataFrame) -> bytes:
    """Return CSV bytes for the download button."""
    return dataframe.to_csv(index=False).encode("utf-8")

csv_bytes = convert_df_to_csv(df_raw)

st.download_button(
    label="💾 Download full dataset (raw + masked)",
    data=csv_bytes,
    file_name="executive_risk_dashboard.csv",
    mime="text/csv",
)

# ------------------------------------------------------------------
# 9️⃣  Optional per‑row “Show raw” expander
# ------------------------------------------------------------------
st.subheader("🗂 Detailed view")
for idx, row in df_raw.iterrows():
    with st.expander(f"Message {idx + 1}"):
        st.write("**Masked:**", row["masked_message"])
        if st.checkbox(f"Reveal raw (Message {idx + 1})", key=f"reveal_{idx}"):
            st.write("**Raw:**", row["message"])
