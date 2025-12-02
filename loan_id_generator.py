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
    Recursively generates a unique loan ID in the format LOAN-YYMMDD-0000.
    The YYMMDD segment represents the loan’s contract date, followed by a 5-digit random value.
    """
    # Generate random 5-digit suffix (e.g., '05492')
    suffix = f"{random.randint(0, 99999):05d}"
    new_id = f"LOAN-{date_str}-{suffix}"

    # Simple collision check
    if new_id in existing_ids_set:
        return generate_loan_id(date_str, existing_ids_set)
    return new_id


def process_loans(df, existing_ids):
    """
    Adds a 'loan_id' column using the 'contract_date' from each row.
    """
    # 1. Ensure contract_date is a datetime object so we can format it
    # errors='coerce' turns invalid dates into NaT (Not a Time)
    df['contract_date'] = pd.to_datetime(df['contract_date'], errors='coerce')

    # 2. Fill missing dates with today's date (just in case)
    df['contract_date'] = df['contract_date'].fillna(pd.Timestamp.now())

    current_ids = existing_ids.copy()
    new_ids = []

    # 3. Iterate through every row to get that specific car's date
    for index, row in df.iterrows():
        # Extract the date object from the row
        c_date = row['contract_date']

        # Format it as YYMMDD (e.g., 2025-11-29 becomes 251129)
        row_date_str = c_date.strftime("%y%m%d")

        unique_id = generate_loan_id(row_date_str, current_ids)
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
    print(df_processed.head())


if __name__ == "__main__":
    main()