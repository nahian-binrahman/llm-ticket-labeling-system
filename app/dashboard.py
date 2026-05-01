import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FINAL_FILE = DATA_DIR / "final_labeled_tickets.csv"

st.set_page_config(
    page_title="LLM Ticket Labeling Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(99,102,241,0.18), transparent 34rem),
        radial-gradient(circle at top right, rgba(14,165,233,0.14), transparent 32rem),
        linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

.hero-card {
    padding: 2rem;
    border-radius: 1.6rem;
    background: linear-gradient(135deg, #111827 0%, #1e293b 52%, #2563eb 100%);
    color: white;
    box-shadow: 0 25px 60px rgba(15, 23, 42, 0.25);
    margin-bottom: 1.3rem;
}

.hero-card h1 {
    color: white;
    font-size: 2.4rem;
    margin-bottom: 0.55rem;
    letter-spacing: -0.04em;
}

.hero-card p {
    color: #cbd5e1;
    font-size: 1.02rem;
    margin-bottom: 0;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
    margin: 1rem 0 0.25rem 0;
}

.section-subtitle {
    color: #64748b;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: rgba(255,255,255,0.85);
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 1.35rem;
    padding: 1.25rem 1.35rem;
    box-shadow: 0 15px 40px rgba(15, 23, 42, 0.08);
    min-height: 140px;
}

.metric-label {
    color: #64748b;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.metric-value {
    color: #0f172a;
    font-size: 2.35rem;
    font-weight: 850;
    letter-spacing: -0.05em;
    margin-top: 0.45rem;
}

.metric-help {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 0.35rem;
}

.chart-card {
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 1.35rem;
    padding: 1.15rem;
    box-shadow: 0 15px 40px rgba(15, 23, 42, 0.07);
    margin-bottom: 1rem;
}

.chart-card h3 {
    color: #0f172a;
    font-size: 1rem;
    font-weight: 800;
    margin: 0 0 0.7rem 0;
}

div[data-testid="stDataFrame"] {
    border-radius: 1.1rem;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.24);
    box-shadow: 0 15px 40px rgba(15, 23, 42, 0.06);
}
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    data["confidence"] = pd.to_numeric(data["confidence"], errors="coerce")
    return data


def metric_card(label: str, value: str, help_text: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def distribution_chart(data: pd.DataFrame, column: str, title: str) -> None:
    counts = data[column].fillna("Unknown").astype(str).value_counts().reset_index()
    counts.columns = [column, "tickets"]

    chart = (
        alt.Chart(counts)
        .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8)
        .encode(
            x=alt.X("tickets:Q", title="Tickets"),
            y=alt.Y(f"{column}:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip(f"{column}:N", title="Label"),
                alt.Tooltip("tickets:Q", title="Tickets"),
            ],
        )
        .properties(height=280)
    )

    st.markdown(f'<div class="chart-card"><h3>{title}</h3>', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


try:
    df = load_data(FINAL_FILE)
except FileNotFoundError:
    st.error(f"Could not find the dataset at: {FINAL_FILE}")
    st.stop()


required_columns = [
    "ticket_id",
    "ticket_description",
    "final_sentiment",
    "final_topic",
    "final_intent",
    "final_emotion",
    "confidence",
    "label_source",
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error("Missing columns: " + ", ".join(missing_columns))
    st.stop()


st.markdown(
    """
    <div class="hero-card">
        <h1>LLM Ticket Labeling Command Center</h1>
        <p>
            Monitor customer support labels, review confidence quality,
            and quickly find tickets that need human attention.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("### Dashboard Controls")
    st.caption("Use these filters to focus the dashboard.")

    label_sources = sorted(df["label_source"].dropna().astype(str).unique())
    sentiments = sorted(df["final_sentiment"].dropna().astype(str).unique())
    topics = sorted(df["final_topic"].dropna().astype(str).unique())
    intents = sorted(df["final_intent"].dropna().astype(str).unique())
    emotions = sorted(df["final_emotion"].dropna().astype(str).unique())

    selected_sources = st.multiselect(
        "Label source", label_sources, default=label_sources
    )
    selected_sentiments = st.multiselect("Sentiment", sentiments, default=sentiments)
    selected_topics = st.multiselect("Topic", topics, default=topics)
    selected_intents = st.multiselect("Intent", intents, default=intents)
    selected_emotions = st.multiselect("Emotion", emotions, default=emotions)

    confidence_range = st.slider(
        "Confidence range",
        min_value=float(df["confidence"].min()),
        max_value=float(df["confidence"].max()),
        value=(float(df["confidence"].min()), float(df["confidence"].max())),
        step=0.01,
    )

    search_text = st.text_input(
        "Search ticket text",
        placeholder="Example: refund, login, delivery",
    )


filtered_df = df[
    df["label_source"].astype(str).isin(selected_sources)
    & df["final_sentiment"].astype(str).isin(selected_sentiments)
    & df["final_topic"].astype(str).isin(selected_topics)
    & df["final_intent"].astype(str).isin(selected_intents)
    & df["final_emotion"].astype(str).isin(selected_emotions)
    & df["confidence"].between(confidence_range[0], confidence_range[1])
].copy()

if search_text:
    filtered_df = filtered_df[
        filtered_df["ticket_description"]
        .astype(str)
        .str.contains(search_text, case=False, na=False)
    ]


total_tickets = len(filtered_df)
llm_count = int((filtered_df["label_source"] == "llm").sum())
human_count = int((filtered_df["label_source"] == "human_reviewed").sum())
avg_confidence = filtered_df["confidence"].mean() if total_tickets else 0

low_confidence_df = filtered_df[filtered_df["confidence"] < 0.85].sort_values(
    "confidence"
)
low_confidence_count = len(low_confidence_df)


st.markdown(
    '<div class="section-title">Executive Summary</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">A quick read on volume, automation, review effort, and confidence health.</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card(
        "Total Tickets", f"{total_tickets:,}", "Tickets matching current filters"
    )

with col2:
    metric_card("LLM-Only", f"{llm_count:,}", "Automatically labeled tickets")

with col3:
    metric_card("Human Reviewed", f"{human_count:,}", "Tickets checked by reviewers")

with col4:
    metric_card(
        "Avg Confidence", f"{avg_confidence:.1%}", f"{low_confidence_count:,} below 85%"
    )


st.markdown(
    '<div class="section-title">Label Distribution</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">See how labels are spread across sentiment, topic, intent, and emotion.</div>',
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    distribution_chart(filtered_df, "final_sentiment", "Sentiment Distribution")

with chart_col2:
    distribution_chart(filtered_df, "final_topic", "Topic Distribution")

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    distribution_chart(filtered_df, "final_intent", "Intent Distribution")

with chart_col4:
    distribution_chart(filtered_df, "final_emotion", "Emotion Distribution")


st.markdown(
    '<div class="section-title">Confidence Analysis</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">Find weak predictions and prioritize tickets for manual review.</div>',
    unsafe_allow_html=True,
)

conf_col1, conf_col2 = st.columns([2, 1])

with conf_col1:
    confidence_chart_data = filtered_df.reset_index().rename(
        columns={"index": "row_number"}
    )

    confidence_chart = (
        alt.Chart(confidence_chart_data)
        .mark_area(line=True, opacity=0.35)
        .encode(
            x=alt.X("row_number:Q", title="Ticket row"),
            y=alt.Y("confidence:Q", title="Confidence", scale=alt.Scale(domain=[0, 1])),
            tooltip=[
                alt.Tooltip("ticket_id:N", title="Ticket ID"),
                alt.Tooltip("confidence:Q", title="Confidence", format=".2%"),
                alt.Tooltip("label_source:N", title="Source"),
            ],
        )
        .properties(height=310)
    )

    st.markdown(
        '<div class="chart-card"><h3>Confidence Trend</h3>', unsafe_allow_html=True
    )
    st.altair_chart(confidence_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with conf_col2:
    source_counts = (
        filtered_df["label_source"].value_counts(normalize=True).mul(100).reset_index()
    )
    source_counts.columns = ["label_source", "share"]

    source_chart = (
        alt.Chart(source_counts)
        .mark_arc(innerRadius=65, outerRadius=112)
        .encode(
            theta=alt.Theta("share:Q"),
            color=alt.Color("label_source:N", legend=alt.Legend(title="Source")),
            tooltip=[
                alt.Tooltip("label_source:N", title="Source"),
                alt.Tooltip("share:Q", title="Share", format=".1f"),
            ],
        )
        .properties(height=310)
    )

    st.markdown(
        '<div class="chart-card"><h3>Label Source Mix</h3>', unsafe_allow_html=True
    )
    st.altair_chart(source_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


review_columns = [
    "ticket_id",
    "ticket_description",
    "final_sentiment",
    "final_topic",
    "final_intent",
    "final_emotion",
    "confidence",
    "label_source",
]

tab1, tab2 = st.tabs(["Review Queue", "Final Dataset"])

with tab1:
    st.markdown(
        '<div class="section-title">Low-Confidence Review Queue</div>',
        unsafe_allow_html=True,
    )
    st.caption("Tickets under 85% confidence are listed first.")

    st.dataframe(
        low_confidence_df[review_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "confidence": st.column_config.ProgressColumn(
                "Confidence",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
            "ticket_description": st.column_config.TextColumn(
                "Ticket Description",
                width="large",
            ),
        },
    )

with tab2:
    st.markdown(
        '<div class="section-title">Final Labeled Dataset</div>', unsafe_allow_html=True
    )
    st.caption("Full filtered dataset with final labels and confidence scores.")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "confidence": st.column_config.ProgressColumn(
                "Confidence",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
            "ticket_description": st.column_config.TextColumn(
                "Ticket Description",
                width="large",
            ),
        },
    )


csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download filtered dataset",
    csv,
    file_name="filtered_labeled_tickets.csv",
    mime="text/csv",
    use_container_width=True,
)
