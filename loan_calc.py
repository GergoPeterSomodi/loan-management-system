import sqlite3
import pandas as pd
from scipy import optimize
from datetime import datetime, date

# --- CONFIGURATION ---
DB_FILE = 'loan_data.db'
SOURCE_TABLE = 'loans'
TARGET_TABLE = 'repayment_schedules'


def calculate_final_balance(apr, principal, pmt, start_date, months):
    """
    Objective function for the Solver.
    """
    balance = principal
    current_date = start_date
    for period in range(1, months + 1):
        next_month_date = (pd.to_datetime(start_date) + pd.DateOffset(months=period)).date()
        days_in_period = (next_month_date - current_date).days
        daily_rate = (apr / 100) / 365
        interest = balance * daily_rate * days_in_period
        balance = balance + interest - pmt
        current_date = next_month_date
    return balance


def generate_reconciled_schedule(loan):
    loan_id = loan['loan_id']
    principal = float(loan['finance_amount'])
    term_months = int(loan['term_months'])
    monthly_payment = float(loan['monthly_repayment'])
    flat_rate = float(loan['flat_rate_percent'])

    # --- STEP 1: DEFINE THE TARGETS ---
    # These are the "Immutable Truths" from the contract
    target_total_interest = round(principal * (flat_rate / 100) * (term_months / 12), 2)
    target_total_payable = round(principal + target_total_interest, 2)

    try:
        start_date = pd.to_datetime(loan['contract_date']).date()
    except:
        start_date = datetime.now().date()

    # --- STEP 2: SOLVE FOR APR ---
    try:
        precise_apr = optimize.brentq(
            calculate_final_balance, 0.0, 100.0,
            args=(principal, monthly_payment, start_date, term_months),
            xtol=1e-6
        )
    except ValueError:
        precise_apr = 0.0

    # --- STEP 3: GENERATE SCHEDULE WITH DOUBLE CHECK ---
    schedule = []
    balance = principal
    current_date = start_date

    # Accumulators
    sum_interest_so_far = 0.0
    sum_repayment_so_far = 0.0

    for period in range(1, term_months + 1):
        opening_balance = balance

        # Date Logic
        next_month_date = (pd.to_datetime(start_date) + pd.DateOffset(months=period)).date()
        days_in_period = (next_month_date - current_date).days

        # --- LOGIC BRANCH ---
        if period == term_months:
            # === FINAL MONTH (THE FIX) ===
            # Instead of calculating, we SUBTRACT.

            # 1. Force Interest to match Target
            interest_amount = round(target_total_interest - sum_interest_so_far, 2)

            # 2. Force Repayment to match Target
            repayment_amount = round(target_total_payable - sum_repayment_so_far, 2)

            # 3. Principal is the difference
            principal_portion = repayment_amount - interest_amount

            # 4. Close the loan
            closing_balance = 0.0

        else:
            # === STANDARD MONTH ===
            daily_rate = (precise_apr / 100) / 365
            raw_interest = opening_balance * daily_rate * days_in_period

            # IMPORTANT: Round HERE so the accumulator matches the visible data
            interest_amount = round(raw_interest, 2)
            repayment_amount = monthly_payment

            principal_portion = repayment_amount - interest_amount
            closing_balance = round(opening_balance - principal_portion, 2)

        # Update Accumulators
        sum_interest_so_far += interest_amount
        sum_repayment_so_far += repayment_amount

        schedule.append({
            'loan_id': loan_id,
            'period': period,
            'payment_date': next_month_date,
            'days_in_period': days_in_period,
            'nominal_apr': round(precise_apr, 6),
            'opening_balance': opening_balance,
            'interest_amount': interest_amount,
            'repayment_amount': repayment_amount,
            'closing_balance': closing_balance,
            'xirr_percent': 0.0
        })

        balance = closing_balance
        current_date = next_month_date

    return schedule, target_total_interest, sum_interest_so_far


def main():
    conn = sqlite3.connect(DB_FILE)
    try:
        loans_df = pd.read_sql(f"SELECT * FROM {SOURCE_TABLE}", conn)
    except Exception as e:
        print(e)
        return

    print(f"Reconciling {len(loans_df)} loans (Fixing Interest & Payables)...")

    all_schedules = []

    # For reporting
    debug_diffs = []

    for index, row in loans_df.iterrows():
        if pd.isna(row['monthly_repayment']): continue

        # Unpack the return values to check accuracy
        sched, target_int, actual_int = generate_reconciled_schedule(row)
        all_schedules.extend(sched)

        if abs(target_int - actual_int) > 0.01:
            debug_diffs.append((row['loan_id'], target_int, actual_int))

    schedule_df = pd.DataFrame(all_schedules)
    schedule_df.to_sql(TARGET_TABLE, conn, if_exists='replace', index=False)
    conn.close()

    # --- VERIFICATION REPORT ---
    if not schedule_df.empty:
        print("\n--- Final Month Reconciliation Example ---")
        last_id = schedule_df.iloc[-1]['loan_id']
        loan_rows = schedule_df[schedule_df['loan_id'] == last_id]

        total_int_sched = loan_rows['interest_amount'].sum()
        total_pay_sched = loan_rows['repayment_amount'].sum()

        print(f"Loan ID:             {last_id}")
        print(f"Sum of Interest Col: {total_int_sched}")
        print(f"Sum of Repay Col:    {total_pay_sched}")
        print("Note: These sums should now match your Contract Totals exactly.")

    if debug_diffs:
        print(f"\nWarning: {len(debug_diffs)} loans had large interest discrepancies.")


if __name__ == "__main__":
    main()