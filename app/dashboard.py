import streamlit as st
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FINAL_FILE = DATA_DIR / "final_labeled_tickets.csv"

st.set_page_config(page_title="LLM Ticket Labeling Dashboard", layout="wide")

st.title("LLM-Based Customer Support Ticket Labeling Dashboard")

df = pd.read_csv(FINAL_FILE)

st.write("This dashboard shows the final labeled customer support tickets.")

# Summary cards
total_tickets = len(df)
llm_count = len(df[df["label_source"] == "llm"])
human_count = len(df[df["label_source"] == "human_reviewed"])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Tickets", total_tickets)

with col2:
    st.metric("LLM-Only Labels", llm_count)

with col3:
    st.metric("Human Reviewed Labels", human_count)

st.divider()

# Label distributions
st.subheader("Label Distributions")

col1, col2 = st.columns(2)

with col1:
    st.write("Sentiment Distribution")
    st.bar_chart(df["final_sentiment"].value_counts())

with col2:
    st.write("Topic Distribution")
    st.bar_chart(df["final_topic"].value_counts())

col3, col4 = st.columns(2)

with col3:
    st.write("Intent Distribution")
    st.bar_chart(df["final_intent"].value_counts())

with col4:
    st.write("Emotion Distribution")
    st.bar_chart(df["final_emotion"].value_counts())

st.divider()

# Confidence
st.subheader("Confidence Analysis")

st.write("Average confidence:", round(df["confidence"].mean(), 3))

st.bar_chart(df["confidence"])

low_confidence_df = df[df["confidence"] < 0.85]

st.write("Low-confidence tickets:", len(low_confidence_df))

with st.expander("View Low-Confidence Tickets"):
    st.dataframe(
        low_confidence_df[
            [
                "ticket_id",
                "ticket_description",
                "final_sentiment",
                "final_topic",
                "final_intent",
                "final_emotion",
                "confidence",
                "label_source",
            ]
        ],
        use_container_width=True,
    )

st.divider()

# Final dataset table
st.subheader("Final Labeled Dataset")

st.dataframe(df, use_container_width=True)
