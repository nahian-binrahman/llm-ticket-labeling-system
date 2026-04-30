import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

LLM_FILE = DATA_DIR / "llm_labeled_tickets_v2.csv"
HUMAN_FILE = DATA_DIR / "human_reviewed_tickets_v2.csv"
OUTPUT_FILE = DATA_DIR / "final_labeled_tickets.csv"

# Load files
llm_df = pd.read_csv(LLM_FILE)

try:
    human_df = pd.read_csv(HUMAN_FILE)
except FileNotFoundError:
    human_df = pd.DataFrame()

# Add final label columns
llm_df["final_sentiment"] = llm_df["sentiment"]
llm_df["final_topic"] = llm_df["topic"]
llm_df["final_intent"] = llm_df["intent"]
llm_df["final_emotion"] = llm_df["emotion"]
llm_df["label_source"] = "llm"

# Replace LLM labels with human labels where reviewed
if not human_df.empty:
    for _, row in human_df.iterrows():
        ticket_id = row["ticket_id"]

        mask = llm_df["ticket_id"] == ticket_id

        llm_df.loc[mask, "final_sentiment"] = row["human_sentiment"]
        llm_df.loc[mask, "final_topic"] = row["human_topic"]
        llm_df.loc[mask, "final_intent"] = row["human_intent"]
        llm_df.loc[mask, "final_emotion"] = row["human_emotion"]
        llm_df.loc[mask, "label_source"] = "human_reviewed"

# Select clean final columns
final_df = llm_df[
    [
        "ticket_id",
        "ticket_description",
        "final_sentiment",
        "final_topic",
        "final_intent",
        "final_emotion",
        "confidence",
        "reason",
        "label_source",
    ]
]

# Save final dataset
final_df.to_csv(OUTPUT_FILE, index=False)

print("Step 8 complete!")
print(f"Final dataset saved to: {OUTPUT_FILE}")
print(f"Total rows: {len(final_df)}")
print(final_df["label_source"].value_counts())
print(final_df.head())
