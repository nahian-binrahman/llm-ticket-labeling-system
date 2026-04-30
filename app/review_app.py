import streamlit as st
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "review_queue_v2.csv"
OUTPUT_FILE = DATA_DIR / "human_reviewed_tickets_v2.csv"

st.set_page_config(page_title="LLM Ticket Review", page_icon="🧠", layout="wide")

st.markdown(
    """
<style>
.main {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background: white;
    padding: 1.4rem;
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
}

.metric-card {
    background: linear-gradient(135deg, #111827, #374151);
    color: white;
    padding: 1.2rem;
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.12);
}

.badge {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    background: #eef2ff;
    color: #3730a3;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

.badge-red {
    background: #fee2e2;
    color: #991b1b;
}

.badge-green {
    background: #dcfce7;
    color: #166534;
}

.badge-yellow {
    background: #fef3c7;
    color: #92400e;
}

.title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #111827;
}

.subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}

.ticket-text {
    font-size: 1.05rem;
    line-height: 1.7;
    color: #111827;
}

.small-muted {
    color: #6b7280;
    font-size: 0.9rem;
}
</style>
""",
    unsafe_allow_html=True,
)


def safe_index(options, value):
    return options.index(value) if value in options else 0


def confidence_badge(confidence):
    try:
        confidence = float(confidence)
    except Exception:
        return '<span class="badge badge-red">Missing confidence</span>'

    if confidence >= 0.85:
        return f'<span class="badge badge-green">Confidence: {confidence:.2f}</span>'
    elif confidence >= 0.60:
        return f'<span class="badge badge-yellow">Confidence: {confidence:.2f}</span>'
    else:
        return f'<span class="badge badge-red">Confidence: {confidence:.2f}</span>'


# Load queue
df = pd.read_csv(INPUT_FILE)

if df.empty:
    st.success("🎉 No tickets need review.")
    st.stop()

# Reviewed count
reviewed_count = 0
if OUTPUT_FILE.exists():
    reviewed_df_existing = pd.read_csv(OUTPUT_FILE)
    reviewed_count = len(reviewed_df_existing)

pending_count = len(df)
total_count = reviewed_count + pending_count
progress = reviewed_count / total_count if total_count > 0 else 0

# Sidebar
with st.sidebar:
    st.title("🧠 Review Panel")
    st.write("LLM-Based Ticket Label Review")

    st.divider()

    st.metric("Pending Tickets", pending_count)
    st.metric("Reviewed Tickets", reviewed_count)

    st.progress(min(progress, 1.0))
    st.caption(f"Progress: {progress * 100:.1f}%")

    st.divider()

    ticket_index = st.number_input(
        "Ticket Number",
        min_value=0,
        max_value=len(df) - 1,
        value=0,
        step=1,
    )

    st.caption("After saving, this ticket will be removed from the queue.")

# Current row
row = df.iloc[ticket_index]

# Header
st.markdown('<div class="title">LLM Ticket Human Review</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Check AI-generated labels, correct mistakes, and build a cleaner dataset.</div>',
    unsafe_allow_html=True,
)

# Top metric cards
top1, top2, top3 = st.columns(3)

with top1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="small-muted" style="color:#d1d5db;">Current Queue Position</div>
            <h2>#{ticket_index}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="small-muted" style="color:#d1d5db;">Ticket ID</div>
            <h2>{row["ticket_id"]}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="small-muted" style="color:#d1d5db;">Status</div>
            <h2>Pending Review</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

left, right = st.columns([1.2, 1])

# Left section
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Ticket Description")
    st.markdown(
        f'<div class="ticket-text">{row["ticket_description"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 LLM Prediction")

    st.markdown(
        f"""
        <span class="badge">Sentiment: {row["sentiment"]}</span>
        <span class="badge">Topic: {row["topic"]}</span>
        <span class="badge">Intent: {row["intent"]}</span>
        <span class="badge">Emotion: {row["emotion"]}</span>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(confidence_badge(row["confidence"]), unsafe_allow_html=True)

    st.write("")
    st.markdown("**LLM Reason**")
    st.info(row["reason"])

    st.markdown("**Why this needs review**")
    st.warning(row["review_reason"])

    st.markdown("</div>", unsafe_allow_html=True)

# Right section
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Human Correction")

    sentiment_options = ["positive", "negative", "neutral", "mixed"]

    topic_options = [
        "product_quality",
        "delivery",
        "pricing",
        "customer_support",
        "refund",
        "technical_issue",
        "account_issue",
        "billing_issue",
        "other",
    ]

    intent_options = [
        "complaint",
        "question",
        "refund_request",
        "technical_help",
        "account_help",
        "billing_help",
        "feature_request",
        "praise",
        "other",
    ]

    emotion_options = [
        "happy",
        "angry",
        "frustrated",
        "confused",
        "disappointed",
        "neutral",
    ]

    with st.form("review_form"):
        human_sentiment = st.selectbox(
            "Correct Sentiment",
            sentiment_options,
            index=safe_index(sentiment_options, row["sentiment"]),
        )

        human_topic = st.selectbox(
            "Correct Topic",
            topic_options,
            index=safe_index(topic_options, row["topic"]),
        )

        human_intent = st.selectbox(
            "Correct Intent",
            intent_options,
            index=safe_index(intent_options, row["intent"]),
        )

        human_emotion = st.selectbox(
            "Correct Emotion",
            emotion_options,
            index=safe_index(emotion_options, row["emotion"]),
        )

        human_notes = st.text_area(
            "Human Notes",
            placeholder="Example: AI chose mixed, but text is clearly negative.",
        )

        submitted = st.form_submit_button("💾 Save Review", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Save logic
if submitted:
    reviewed_row = row.to_dict()

    reviewed_row["human_sentiment"] = human_sentiment
    reviewed_row["human_topic"] = human_topic
    reviewed_row["human_intent"] = human_intent
    reviewed_row["human_emotion"] = human_emotion
    reviewed_row["human_notes"] = human_notes
    reviewed_row["review_status"] = "reviewed"

    reviewed_df = pd.DataFrame([reviewed_row])

    # Save reviewed ticket
    if OUTPUT_FILE.exists():
        old_df = pd.read_csv(OUTPUT_FILE)

        # Avoid duplicate saved reviews for same ticket
        old_df = old_df[old_df["ticket_id"] != row["ticket_id"]]

        final_df = pd.concat([old_df, reviewed_df], ignore_index=True)
    else:
        final_df = reviewed_df

    final_df.to_csv(OUTPUT_FILE, index=False)

    # Remove reviewed ticket from review queue
    updated_queue = df[df["ticket_id"] != row["ticket_id"]]
    updated_queue.to_csv(INPUT_FILE, index=False)

    st.success("Review saved successfully! Ticket removed from queue.")
    st.balloons()

    st.rerun()
