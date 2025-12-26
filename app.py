# --------------------------------------------------------------
# app.py – Executive Risk Dashboard (masking + risk flags)
# --------------------------------------------------------------

import streamlit as st
import pandas as pd
import re
from typing import Tuple

# ------------------------------------------------------------------
# 1️⃣  Page configuration – must be the first Streamlit call
# ------------------------------------------------------------------
st.set_page_config(page_title="Executive Risk Dashboard", layout="wide")

# ------------------------------------------------------------------
# 2️⃣  CSS – adds vertical space above the title
# ------------------------------------------------------------------
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
# 3️⃣  Simple profanity masker (you can swap this for a library)
# ------------------------------------------------------------------
def mask_profanity(text: str) -> str:
    profanity_words = [
        "fuck", "shit", "shitty", "cunt", "bitch",
        "ass", "damn", "crap", "piss", "dick"
    ]

    def _replace(m):
        return "*" * len(m.group())

    pattern = re.compile(r"\b(" + "|".join(profanity_words) + r")\b", flags=re.I)
    return pattern.sub(_replace, text)


# ------------------------------------------------------------------
# 4️⃣  Helper: very light‑weight sentiment estimator
# ------------------------------------------------------------------
def simple_sentiment(text: str) -> str:
    """
    Returns 'positive', 'negative', or 'neutral' based on a few
    keyword lists.  This is *not* a production‑grade sentiment
    model, but it avoids pulling in heavy dependencies.
    """
    positive_words = {"good", "great", "awesome", "nice", "love", "happy"}
    negative_words = {"bad", "terrible", "hate", "angry", "sad", "worst"}

    # Normalise
    tokens = re.findall(r"\w+", text.lower())
    pos = sum(tok in positive_words for tok in tokens)
    neg = sum(tok in negative_words for tok in tokens)

    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    else:
        return "neutral"


# ------------------------------------------------------------------
# 5️⃣  Keyword‑based flag detectors
# ------------------------------------------------------------------
def detect_personal_use(text: str) -> bool:
    """True if the message hints at personal (non‑business) usage."""
    personal_cues = {
        "my wife", "my kid", "my family", "personal", "home", "outside work",
        "private", "vacation", "holiday", "weekend", "after hours"
    }
    return any(cue in text.lower() for cue in personal_cues)


def detect_credit_card_use(text: str) -> bool:
    """True if credit‑card or expense terminology appears."""
    cc_cues = {
        "credit card", "visa", "mastercard", "amex", "expense", "receipt",
        "billing", "charge", "purchase", "buy", "order"
    }
    return any(cue in text.lower() for cue in cc_cues)


def detect_large_spending(text: str) -> bool:
    """
    Looks for monetary amounts that are relatively large.
    Adjust the threshold (e.g., 1000) to suit your policy.
    """
    # Find numbers that look like money: $123, €1,200, £5000, 3000USD, etc.
    money_patterns = re.findall(r"[\$€£]\s?\d{1,3}(?:[,\.\d]*\d)?|\d+\s?(?:usd|eur|gbp)", text, flags=re.I)
    # Convert to plain numbers (strip symbols/comma)
    amounts = []
    for m in money_patterns:
        num = re.sub(r"[^\d\.]", "", m)  # keep digits & dot
        try:
            amounts.append(float(num))
        except ValueError:
            continue
    # Threshold – you can tune this
    return any(val >= 1000 for val in amounts)


def detect_nsfw(text: str) -> bool:
    """Reuse the profanity list – if any profanity is present, flag NSFW."""
    profanity_words = [
        "fuck", "shit", "shitty", "cunt", "bitch",
        "ass", "damn", "crap", "piss", "dick"
    ]
    pattern = re.compile(r"\b(" + "|".join(profanity_words) + r")\b", flags=re.I)
    return bool(pattern.search(text))


# ------------------------------------------------------------------
# 6️⃣  Combine all detectors into a single row‑wise function
# ------------------------------------------------------------------
def enrich_row(text: str) -> Tuple[str, bool, bool, bool, bool, str]:
    """
    Returns:
        masked_text,
        nsfw_flag,
        personal_use_flag,
        credit_card_flag,
        large_spending_flag,
        sentiment
    """
    masked = mask_profanity(text)
    nsfw = detect_nsfw(text)
    personal = detect_personal_use(text)
    cc = detect_credit_card_use(text)
    spend = detect_large_spending(text)
    sentiment = simple_sentiment(text)
    return masked, nsfw, personal, cc, spend, sentiment


# ------------------------------------------------------------------
# 7️⃣  Load / build your data
# ------------------------------------------------------------------
sample_messages = [
    "My question still stands. What the fuck is that?",
    "There is loads of tea in my house but I hate it",
    "I woulda stuck with the swapped gender just for Rp purposes but like psssh if you're gonna have bandits rape a player have em take some dude's booty if you wanna be edgy",
    "@Reichtangle I've seen a pic of you. You're white as fuck",
    "and lately, his team said that there is a small group of people who know covfefe's meaning\\nthey blew it out of proportion and made it worse than it was\\nand I hate myself for knowing that much on that shitty ass joke",
    "Bought a $1500 gaming laptop with the corporate Visa last night – totally personal use!",
    "My wife and I went on a weekend trip, paid with the company credit card.  Should we flag it?",
    "Great job on the Q3 results! Love the numbers."
]

# Build a DataFrame and enrich each row
df_raw = pd.DataFrame({"message": sample_messages})

# Apply enrichment – creates new columns
(
    df_raw["masked_message"],
    df_raw["nsfw_flag"],
    df_raw["personal_use_flag"],
    df_raw["credit_card_flag"],
    df_raw["large_spending_flag"],
    df_raw["sentiment"]
) = zip(*df_raw["message"].apply(enrich_row))

# ------------------------------------------------------------------
# 8️⃣  Page title (now fully visible)
# ------------------------------------------------------------------
st.title("🚦 Executive Risk Dashboard – NSFW / Harassment & Policy Flags")

# ------------------------------------------------------------------
# 9️⃣  Sidebar filters (you can extend these later)
# ------------------------------------------------------------------
st.sidebar.header("Filters")
show_raw = st.sidebar.checkbox(
    "Show raw messages (requires authorization)", value=False
)

# Optional filter toggles – useful for a quick demo
filter_nsfw = st.sidebar.checkbox("Only show NSFW flagged", value=False)
filter_personal = st.sidebar.checkbox("Only show Personal‑use flagged", value=False)
filter_cc = st.sidebar.checkbox("Only show Credit‑Card flagged", value=False)
filter_spend = st.sidebar.checkbox("Only show Large‑spending flagged", value=False)

# ------------------------------------------------------------------
# 10️⃣  Apply filters to the displayed dataframe
# ------------------------------------------------------------------
df_display = df_raw.copy()

if filter_nsfw:
    df_display = df_display[df_display["nsfw_flag"]]
if filter_personal:
    df_display = df_display[df_display["personal_use_flag"]]
if filter_cc:
    df_display = df_display[df_display["credit_card_flag"]]
if filter_spend:
    df_display = df_display[df_display["large_spending_flag"]]

# ------------------------------------------------------------------
# 11️⃣  Main table – masked vs. raw based on sidebar toggle
# ------------------------------------------------------------------
if show_raw:
    st.subheader("🔎 Messages – RAW (un‑masked)")
    st.dataframe(df_display[["message", "nsfw_flag", "personal_use_flag",
                             "credit_card_flag", "large_spending_flag",
                             "sentiment"]])
else:
    st.subheader("🔎 Messages – Masked")
    st.dataframe(df_display[["masked_message", "nsfw_flag", "personal_use_flag",
                             "credit_card_flag", "large_spending_flag",
                             "sentiment"]])

# ------------------------------------------------------------------
# 12️⃣  CSV export – includes every column (raw + masked)
# ------------------------------------------------------------------
def convert_df_to_csv(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")

csv_bytes = convert_df_to_csv(df_raw)  # export the *full* dataset, not just filtered view

st.download_button(
    label="💾 Download full dataset (raw + masked + flags)",
    data=csv_bytes,
    file_name="executive_risk_dashboard_full.csv",
    mime="text/csv",
)

# ------------------------------------------------------------------
# 13️⃣  Detailed per‑row expander (optional)
# ------------------------------------------------------------------
st.subheader("🗂 Detailed view")
for idx, row in df_display.iterrows():
    with st.expander(f"Message {idx + 1}"):
        # Show masked text always
        st.write("**Masked:**", row["masked_message"])

        # Reveal raw only if user explicitly asks
        if st.checkbox(f"Reveal raw (Message {idx + 1})", key=f"reveal_{idx}"):
            st.write("**Raw:**", row["message"])

        # Show the flag breakdown
        st.write("**Flags & Sentiment**")
        st.write({
            "NSFW": row["nsfw_flag"],
            "Personal‑use": row["personal_use_flag"],
            "Credit‑Card usage": row["credit_card_flag"],
            "Large spending": row["large_spending_flag"],
            "Sentiment": row["sentiment"]
        })
