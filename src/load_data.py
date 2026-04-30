import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "customer_support_tickets.csv"
OUTPUT_FILE = DATA_DIR / "sample_input.csv"

# Load dataset
df = pd.read_csv(INPUT_FILE)

# Check required columns
required_columns = ["Ticket ID", "Ticket Description"]

for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

# Select only needed columns
sample_df = df[["Ticket ID", "Ticket Description"]].copy()

# Rename columns for cleaner project use
sample_df = sample_df.rename(
    columns={"Ticket ID": "ticket_id", "Ticket Description": "ticket_description"}
)

# Remove empty ticket descriptions
sample_df = sample_df.dropna(subset=["ticket_description"])

# Remove duplicate descriptions
sample_df = sample_df.drop_duplicates(subset=["ticket_description"])

# Optional: take first 100 rows for testing
sample_df = sample_df.head(100)

# Save clean sample file
sample_df.to_csv(OUTPUT_FILE, index=False)

print("Step 1 complete!")
print(f"Input file: {INPUT_FILE}")
print(f"Output file: {OUTPUT_FILE}")
print(f"Total rows saved: {len(sample_df)}")
print(sample_df.head())
