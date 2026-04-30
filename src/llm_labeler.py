import os
import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROMPT_DIR = BASE_DIR / "prompts"

INPUT_FILE = DATA_DIR / "sample_input.csv"
OUTPUT_FILE = DATA_DIR / "llm_labeled_tickets_v2.csv"
PROMPT_FILE = PROMPT_DIR / "prompt_v2.txt"

# Load API key
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key == "your_api_key_here":
    raise ValueError("API key missing. Fix your .env file.")

client = OpenAI(api_key=api_key)

# Load data
df = pd.read_csv(INPUT_FILE)

# Load prompt
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt_template = f.read()


def label_ticket(ticket_text):
    prompt = prompt_template.replace("{text}", str(ticket_text))

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a careful data labeling assistant. Return only valid JSON.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    try:
        label = json.loads(content)
    except json.JSONDecodeError:
        label = {
            "sentiment": "unknown",
            "topic": "unknown",
            "intent": "unknown",
            "emotion": "unknown",
            "confidence": 0.0,
            "reason": "Invalid JSON returned by model",
        }

    return label


results = []

for _, row in tqdm(df.iterrows(), total=len(df)):
    ticket_id = row["ticket_id"]
    ticket_description = row["ticket_description"]

    label = label_ticket(ticket_description)

    results.append(
        {
            "ticket_id": ticket_id,
            "ticket_description": ticket_description,
            "sentiment": label.get("sentiment"),
            "topic": label.get("topic"),
            "intent": label.get("intent"),
            "emotion": label.get("emotion"),
            "confidence": label.get("confidence"),
            "reason": label.get("reason"),
        }
    )

output_df = pd.DataFrame(results)
output_df.to_csv(OUTPUT_FILE, index=False)

print("Step 2 complete!")
print(f"Input file: {INPUT_FILE}")
print(f"Output file: {OUTPUT_FILE}")
print(f"Total labeled rows: {len(output_df)}")
print(output_df.head())
