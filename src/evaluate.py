import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"

INPUT_FILE = DATA_DIR / "human_reviewed_tickets_v2.csv"
OUTPUT_FILE = REPORT_DIR / "evaluation_report_v2.csv"

REPORT_DIR.mkdir(exist_ok=True)

# Load human-reviewed data
df = pd.read_csv(INPUT_FILE)

# Labels to evaluate
label_pairs = {
    "sentiment": ("sentiment", "human_sentiment"),
    "topic": ("topic", "human_topic"),
    "intent": ("intent", "human_intent"),
    "emotion": ("emotion", "human_emotion"),
}

results = []

for label_name, (llm_col, human_col) in label_pairs.items():
    # Remove empty human labels
    temp_df = df.dropna(subset=[llm_col, human_col])

    # Skip if no reviewed data
    if temp_df.empty:
        continue

    y_true = temp_df[human_col].astype(str)
    y_pred = temp_df[llm_col].astype(str)

    accuracy = accuracy_score(y_true, y_pred)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    results.append(
        {
            "label_type": label_name,
            "total_reviewed": len(temp_df),
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
        }
    )

# Save report
report_df = pd.DataFrame(results)
report_df.to_csv(OUTPUT_FILE, index=False)

print("Step 5 complete!")
print(f"Input file: {INPUT_FILE}")
print(f"Output file: {OUTPUT_FILE}")
print(report_df)
