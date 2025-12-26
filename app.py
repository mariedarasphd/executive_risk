import streamlit as st
import pandas as pd
import re

# ------------------------------------------------------------------
# 1️⃣  Tiny CSS block – adds top padding/margin for the whole page
# ------------------------------------------------------------------
# Streamlit lets us inject raw HTML/CSS via st.markdown(..., unsafe_allow_html=True).
# The selector ".main" targets the main content area.
# Adjust the pixel value (e.g., 30px, 50px) to get the amount of space you like.
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        padding-top: 40px;      /* space above everything */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 2️⃣  Helper: simple profanity masker (replace with a library if you wish)
# ------------------------------------------------------------------
def mask_profanity(text: str) -> str:
    profanity_words = [
        "fuck", "shit", "shitty", "cunt", "bitch",
        "ass", "damn", "crap", "piss", "dick"
    ]

    def _replace(match):
        return "*" * len(match.group())

    pattern = re.compile(r"\b(" + "|".join(profanity_words) + r")\b", flags=re.I)
    return pattern.sub(_replace, text)


# ------------------------------------------------------------------
# 3️⃣  Sample data – replace with your real data source
# ------------------------------------------------------------------
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
# 4️⃣  Streamlit page configuration & title
# ------------------------------------------------------------------
st.set_page_config(page_title="Executive Risk Dashboard", layout="wide")
st.title("🚦 Executive Risk Dashboard – NSFW / Harassment Monitor")


# ------------------------------------------------------------------
# 5️⃣  Sidebar controls
# ------------------------------------------------------------------
st.sidebar.header("Filters")
show_raw = st.sidebar.checkbox(
    "Show raw messages (requires authorization)", value=False
)


# ------------------------------------------------------------------
# 6️⃣  Main table – masked vs. raw
# ------------------------------------------------------------------
if show_raw:
    st.subheader("🔎 Messages – RAW (un‑masked)")
    st.dataframe(df_raw[["message"]])
else:
    st.subheader("🔎 Messages – Masked")
    st.dataframe(df_raw[["masked_message"]])


# ------------------------------------------------------------------
# 7️⃣  CSV export (full dataset)
# ------------------------------------------------------------------
def convert_df_to_csv(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")


csv_bytes = convert_df_to_csv(df_raw)

st.download_button(
    label="💾 Download full dataset (raw + masked)",
    data=csv_bytes,
    file_name="executive_risk_dashboard.csv",
    mime="text/csv",
)


# ------------------------------------------------------------------
# 8️⃣  Optional per‑row “Show raw” expander
# ------------------------------------------------------------------
st.subheader("🗂 Detailed view")
for idx, row in df_raw.iterrows():
    with st.expander(f"Message {idx + 1}"):
        st.write("**Masked:**", row["masked_message"])
        if st.checkbox(f"Reveal raw (Message {idx + 1})", key=f"reveal_{idx}"):
            st.write("**Raw:**", row["message"])
