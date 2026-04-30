import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "llm_labeled_tickets_v2.csv"
OUTPUT_FILE = DATA_DIR / "review_queue_v2.csv"
print("Looking for file at:", INPUT_FILE)

# Load LLM labeled data
df = pd.read_csv(INPUT_FILE)

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.85

# Make sure confidence is numeric
df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")


# Add review reason
def get_review_reason(row):
    reasons = []

    if pd.isna(row["confidence"]):
        reasons.append("missing_confidence")

    elif row["confidence"] < CONFIDENCE_THRESHOLD:
        reasons.append("low_confidence")

    if row["topic"] == "other":
        reasons.append("topic_other")

    if row["sentiment"] == "unknown":
        reasons.append("invalid_llm_output")

    if row["intent"] == "other":
        reasons.append("intent_other")

    return ", ".join(reasons)


df["review_reason"] = df.apply(get_review_reason, axis=1)

# Keep only rows that need review
review_df = df[df["review_reason"] != ""].copy()

# Add human correction columns
review_df["human_sentiment"] = ""
review_df["human_topic"] = ""
review_df["human_intent"] = ""
review_df["human_emotion"] = ""
review_df["human_notes"] = ""
review_df["review_status"] = "pending"

# Save review queue
review_df.to_csv(OUTPUT_FILE, index=False)

print("Step 3 complete!")
print(f"Input file: {INPUT_FILE}")
print(f"Output file: {OUTPUT_FILE}")
print(f"Total tickets needing review: {len(review_df)}")
print(review_df[["ticket_id", "confidence", "topic", "intent", "review_reason"]].head())
