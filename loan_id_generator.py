import pandas as pd
import sqlite3
import random
import datetime
import os

# --- CONFIGURATION ---
CSV_FILE = 'gemini_car_loans.csv'
DB_FILE = 'loan_data.db'
TABLE_NAME = 'loans'

def clean_column_names(df):
    """
    Pure Function: Renames columns to be SQL-friendly (snake_case).
    'Car Make' -> 'car_make', 'Flat Rate (%)' -> 'flat_rate_percent'
    """
    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(' ', '_')
                  .str.replace('(', '', regex=False)
                  .str.replace(')', '', regex=False)
                  .str.replace('%', 'percent')
                  )
    return df

def generate_loan_id(date_str, existing_ids_set):
    """
    Pure Function: Generates a unique ID for a specific date.
    Retries recursively if a collision occurs (though rare).
    """
    # Generate random 4-digit suffix (e.g., '0492')
    suffix = f"{random.randint(0, 9999):04d}"
    new_id = f"LOAN-{date_str}-{suffix}"

    # Simple collision check
    if new_id in existing_ids_set:
        return generate_loan_id(date_str, existing_ids_set)
    return new_id


def process_loans(df, existing_ids):
    """
    Adds an 'id' column to the dataframe.
    """
    # Get today's date string once for the batch
    today_str = datetime.datetime.now().strftime("%y%m%d")

    # Create a local copy of the set to track IDs generated within this batch
    current_ids = existing_ids.copy()

    new_ids = []
    for i in range(len(df)):
        unique_id = generate_loan_id(today_str, current_ids)
        current_ids.add(unique_id) #Add to the existing set of IDs
        new_ids.append(unique_id) #Add to the new IDs

    # Assign the new list to the DataFrame
    df['loan_id'] = new_ids
    return df


def get_existing_ids(db_path, table_name):
    """
    Reads all existing loan IDs from the database to prevent duplicates.
    """
    if not os.path.exists(db_path):
        return set()

    try:
        with sqlite3.connect(db_path) as conn:
            # Check if table exists first
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
            if not conn.execute(query).fetchone():
                return set()

            # Fetch existing IDs
            cursor = conn.execute(f"SELECT loan_id FROM {table_name}")
            return {row[0] for row in cursor.fetchall()}
    except Exception as e:
        print(f"Warning: Could not fetch existing IDs ({e}). Starting fresh.")
        return set()


def main():
    # 1. Load Data
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Loaded {len(df)} records from {CSV_FILE}")
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found.")
        return

    # 2. Clean Columns (NEW STEP)
    # This prevents "Car Make" vs "car_make" errors
    df = clean_column_names(df)

    # 3. Load History
    existing_ids = get_existing_ids(DB_FILE, TABLE_NAME)

    # 4. Process Data
    df_processed = process_loans(df, existing_ids)

    # 5. Save to Database
    with sqlite3.connect(DB_FILE) as conn:
        df_processed.to_sql(TABLE_NAME, conn, if_exists='append', index=False)

    print(f"Success! Saved to '{DB_FILE}' in table '{TABLE_NAME}'.")
    print("\nPreview of new data:")
    # Note: Columns are now snake_case in the preview
    print(df_processed[['loan_id', 'car_make', 'finance_amount']].head())


if __name__ == "__main__":
    main()