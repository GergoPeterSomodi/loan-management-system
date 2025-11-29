import pandas as pd
import os
import json
from google import genai
from google.genai import types


# Retrieve the string from the OS environment
API_KEY = os.getenv('GEMINI_API_KEY')


def generate_car_loan_data(num_records=10):
    """
    Generates a synthetic dataset for car financing loans using Google Gemini.
    """

    # Check if API_KEY is present
    if not API_KEY:
        print("Error: API_KEY is missing. Please set GEMINI_API_KEY environment variable or hardcode it in the script.")
        return pd.DataFrame()

    try:
        # 1. Initialise the client with the explicit API Key
        client = genai.Client(api_key=API_KEY)

        # 2. Configure the model request to force JSON output
        config = types.GenerateContentConfig(
            response_mime_type='application/json'
        )

        user_prompt = f"""
                Generate a JSON list of {num_records} synthetic car financing loan records.

                Each record must differ and include:
                - "Car Make": A variety of brands (luxury, economy, EVs).
                - "Car Value": A realistic price for that specific make/model (float).
                - "Car Age (Months)": A realistic age for that specific make/model (float).
                - "Car Mileage": A realistic age for that specific make/model and car age. (integer).
                - "Finance Amount": A realistic loan amount, usually less than the car value (float).
                - "Flat Rate (%)": A realistic interest rate between 2% and 15% (float).
                - "Term (Months)": Standard terms like 12, 24, 36, 48, 60, 72, or 84.

                Example format:
                [
                    {{"Car Make": "Toyota", "Car Value": 25000, "Finance Amount": 20000, "Flat Rate (%)": 4.5, "Term (Months)": 60}}
                ]
                """

        print(f"--- Sending Prompt to Model ---\nPrompt: {user_prompt}\n")

        # 3. Call the model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=config,
        )

        # Parse JSON
        data = json.loads(response.text)

        # Create DataFrame
        df = pd.DataFrame(data)
        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()


def calculate_repayments(df):
    """
    Calculates monthly payments based on a Flat Rate formula.
    Total Interest =  Finance amount * Flat Rate * Term (Years)
    Total Amount Payable (TAP) = Finance Amount + Total Interest
    Monthly Repayment (CMI) = Total Amount Payable (TAP) / Term (Months)
    """
    if df.empty:
        return df

    # Calculate years from months
    df['Term (Years)'] = df['Term (Months)'] / 12

    # Calculate Total Interest
    df['Total Interest'] = df['Finance Amount'] * (df['Flat Rate (%)'] / 100) * df['Term (Years)']

    # Calculate Total Amount Payable
    df['Total Amount Payable'] = df['Finance Amount'] + df['Total Interest']

    # Calculate Monthly Payment
    df['Monthly Repayment'] = df['Total Amount Payable'] / df['Term (Months)']

    # Round monetary values
    df['Total Interest'] = df['Total Interest'].round(2)
    df['Total Amount Payable'] = df['Total Amount Payable'].round(2)
    df['Monthly Repayment'] = df['Monthly Repayment'].round(2)

    return df


if __name__ == "__main__":
    loan_df = generate_car_loan_data(10)

    if not loan_df.empty:
        # --- FIXED: This line must be uncommented for the print statement below to work ---
        loan_df = calculate_repayments(loan_df)

        print("\nPreview of Gemini-generated data with calculations:")
        # Adjust column width for nicer printing
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)

        # This will now work because 'Monthly Payment' exists
        print(loan_df[['Car Make', 'Finance Amount', 'Flat Rate (%)', 'Monthly Repayment']].head())

        output_file = "gemini_car_loans.csv"
        loan_df.to_csv(output_file, index=False)
        print(f"\nData saved successfully to '{output_file}'")
    else:
        print("Failed to generate data.")