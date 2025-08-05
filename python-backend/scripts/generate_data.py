# scripts/generate_data.py

import os
import csv
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

# --- Configuration ---

# Load environment variables from .env file at the project root
# This assumes you run the script from the root directory, e.g., `python scripts/generate_data.py`
load_dotenv()

# Ensure your OPENAI_API_KEY is set in your environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please create a .env file in the project root.")

client = OpenAI(api_key=api_key)

OUTPUT_FILE = "backend/data/feedback_corpus.csv"
NUM_RECORDS_TO_GENERATE = 250 # Generate large dataset

# Define recurring themes for the LLM to use to ensure data diversity and relevance
RECURRING_THEMES = [
    "complaints about the new dashboard being confusing",
    "requests for a dark mode feature",
    "praise for the 'quick add' task functionality",
    "bugs related to calendar integration syncing",
    "feedback on slow loading times on the analytics page",
    "suggestions for more advanced reporting templates",
    "positive comments on the helpfulness of the support team",
    "issues with billing and subscription management",
    "requests for a mobile app version",
    "confusion about the user permissions settings",
    "problems with password reset functionality",
    "praise for the improved search feature",
    "requests for bulk operations and batch processing",
    "issues with data export functionality",
    "feedback on notification system being too noisy",
    "suggestions for integration with Slack/Teams",
    "complaints about missing keyboard shortcuts",
    "positive feedback on the new onboarding process",
    "requests for API documentation improvements",
    "issues with file upload size limits",
    "feedback on the color scheme and accessibility",
    "suggestions for automated backup features",
    "complaints about the email notification frequency",
    "praise for the responsive customer support",
    "requests for advanced filtering options",
    "issues with browser compatibility (Safari/Firefox)",
    "feedback on the mobile web interface",
    "suggestions for collaboration features",
    "complaints about session timeout being too short",
    "positive comments on the performance improvements"
]

# --- Helper Functions ---

def generate_random_date(start_date="2024-01-01", end_date="2025-07-30"):
    """Generates a random date string between two dates."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

def create_generation_prompt(num_records: int) -> str:
    """Creates the main prompt for the LLM to generate synthetic data."""
    
    # Randomly select a few themes to ensure variety in each batch
    themes_to_include = random.sample(RECURRING_THEMES, k=min(len(RECURRING_THEMES), 5))
    
    prompt = f"""
    You are a data generation assistant for a project management SaaS product.
    Your task is to generate {num_records} realistic pieces of user feedback.

    Please adhere to the following rules:
    1.  The feedback should be varied in tone (Positive, Negative, Neutral) and length (from one short sentence to a few sentences).
    2.  Incorporate some of the following specific themes into your feedback: {', '.join(themes_to_include)}.
    3.  Each piece of feedback must be on a new line.
    4.  The output format for each line must be a pipe-separated string with exactly three parts: SOURCE|FEEDBACK_TEXT|SENTIMENT
    5.  Valid sources are: Support Ticket, App Store Review, Survey, Twitter Mention.
    6.  Valid sentiments are: Positive, Negative, Neutral.

    Here is an example of the required output format for two records:
    Support Ticket|The new dashboard UI is incredibly confusing. I can't find the reporting feature anywhere.|Negative
    App Store Review|Love the new 'quick add' task feature! It saves me so much time. However, I wish there was a dark mode available.|Positive

    Now, please generate {num_records} new, unique records following these instructions precisely.
    """
    return prompt.strip()

# --- Main Execution Block ---

if __name__ == "__main__":
    print(f"Starting synthetic data generation for {NUM_RECORDS_TO_GENERATE} records...")

    # Ensure the data directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    prompt = create_generation_prompt(NUM_RECORDS_TO_GENERATE)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful data generation assistant that strictly follows formatting instructions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=3000,
        )
        
        generated_text = response.choices[0].message.content
        feedback_lines = generated_text.strip().split('\n')
        
        print(f"Successfully received {len(feedback_lines)} lines of feedback from the LLM.")

        # Write data to CSV
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['feedback_id', 'source', 'date', 'user_id', 'feedback_text', 'sentiment'])
            
            feedback_count = 0
            for i, line in enumerate(feedback_lines):
                parts = line.split('|')
                if len(parts) == 3:
                    source, feedback_text, sentiment = parts
                    writer.writerow([
                        f'FB-{i+1:03}',
                        source.strip(),
                        generate_random_date(),
                        f'user-{random.randint(100, 999)}',
                        feedback_text.strip(),
                        sentiment.strip()
                    ])
                    feedback_count += 1
                else:
                    print(f"Warning: Skipping malformed line {i+1}: '{line}'")

        print(f"✅ Successfully generated and saved {feedback_count} records to {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ An error occurred during data generation: {e}")