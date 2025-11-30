import numpy_financial as npf
import pandas as pd
from datetime import date
# Import relativedelta for date calculations
from dateutil.relativedelta import relativedelta
from typing import Dict, Any


def calculate_monthly_payment(principal: float, apr: float, term_months: int) -> float:
    """Calculates fixed monthly payment using numpy-financial."""
    # [ ... content unchanged ... ]
    if apr == 0:
        return round(principal / term_months, 2)

    monthly_rate = (apr / 100) / 12
    # pmt returns a negative value (cash outflow), so we flip it
    payment = npf.pmt(monthly_rate, term_months, -principal)
    return round(payment, 2)


def generate_amortization_schedule(loan: Dict[str, Any]) -> pd.DataFrame:
    # [ ... content unchanged ... ]
    """
    Returns a Pandas DataFrame showing the full payment schedule for a loan dictionary.
    """
    schedule = []
    # Access properties using dictionary keys instead of attributes
    balance = loan['principal']
    monthly_rate = (loan['apr'] / 100) / 12
    current_date = loan['start_date']
    term = loan['term_months']
    monthly_payment = loan['monthly_payment']

    for period in range(1, term + 1):
        interest_payment = round(balance * monthly_rate, 2)
        principal_payment = round(monthly_payment - interest_payment, 2)

        # Handle the final month precision
        if period == term:
            # Ensure the last principal payment covers the remaining balance
            principal_payment = balance

        balance = round(balance - principal_payment, 2)
        current_date += relativedelta(months=1)

        schedule.append({
            "Period": period,
            "Date": current_date,
            "Payment": monthly_payment,
            "Principal": principal_payment,
            "Interest": interest_payment,
            "Balance": abs(balance)  # abs handles -0.00 cases
        })

    return pd.DataFrame(schedule)