import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"

INPUT_FILE = DATA_DIR / "human_reviewed_tickets.csv"
OUTPUT_FILE = REPORT_DIR / "error_report.csv"

REPORT_DIR.mkdir(exist_ok=True)

# Load data
df = pd.read_csv(INPUT_FILE)

error_rows = []

for _, row in df.iterrows():
    errors = []

    # Compare each label
    if str(row["sentiment"]) != str(row["human_sentiment"]):
        errors.append("wrong_sentiment")

    if str(row["topic"]) != str(row["human_topic"]):
        errors.append("wrong_topic")

    if str(row["intent"]) != str(row["human_intent"]):
        errors.append("wrong_intent")

    if str(row["emotion"]) != str(row["human_emotion"]):
        errors.append("wrong_emotion")

    # Only keep rows with errors
    if errors:
        error_rows.append(
            {
                "ticket_id": row["ticket_id"],
                "ticket_description": row["ticket_description"],
                "llm_sentiment": row["sentiment"],
                "human_sentiment": row["human_sentiment"],
                "llm_topic": row["topic"],
                "human_topic": row["human_topic"],
                "llm_intent": row["intent"],
                "human_intent": row["human_intent"],
                "llm_emotion": row["emotion"],
                "human_emotion": row["human_emotion"],
                "confidence": row["confidence"],
                "error_type": ", ".join(errors),
                "llm_reason": row["reason"],
            }
        )

# Save error report
error_df = pd.DataFrame(error_rows)
error_df.to_csv(OUTPUT_FILE, index=False)

print("Step 6 complete!")
print(f"Total errors found: {len(error_df)}")
print(f"Saved to: {OUTPUT_FILE}")
print(error_df.head())

print("\nError type counts:")
print(error_df["error_type"].value_counts())
