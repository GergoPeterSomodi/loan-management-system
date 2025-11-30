from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Dict, Any
from models import Borrower, Loan
from calculations import calculate_monthly_payment

# Define the global structure type for clarity
LoanBookSystem = Dict[str, Dict[str, Any]]


def initialize_loan_book() -> LoanBookSystem:
    # [ ... content unchanged ... ]
    """Initializes and returns an empty loan book system dictionary."""
    return {
        "loans": {},
        "borrowers": {}
    }


def add_borrower(system: LoanBookSystem, b_id: str, first: str, last: str, score: int) -> Dict[str, Any]:
    # [ ... content unchanged ... ]
    """Validates borrower data and adds it to the system."""
    # 1. Validate data using Pydantic model (and convert back to dict)
    # .model_dump() is used to get the clean dictionary representation
    borrower_data = Borrower(id=b_id, first_name=first, last_name=last, credit_score=score).model_dump()

    # 2. Store it
    system["borrowers"][b_id] = borrower_data
    return borrower_data


def create_loan(system: LoanBookSystem, l_id: str, b_id: str, principal: float, apr: float, months: int) -> Dict[
    str, Any]:
    """
    Creates a new Loan record, calculates the payment, and adds it to the system.
    Sets the contract date (start_date) and calculates the maturity_date.
    """
    # 1. Calculate Payment
    payment = calculate_monthly_payment(principal, apr, months)

    # 2. Calculate Dates
    start_date = date.today()
    # Maturity date is the start date plus the term in months
    maturity_date = start_date + relativedelta(months=months)

    # 3. Prepare loan data dictionary
    loan_data = {
        "id": l_id,
        "borrower_id": b_id,
        "principal": principal,
        "apr": apr,
        "term_months": months,
        "start_date": start_date,
        "maturity_date": maturity_date,  # NEW
        "monthly_payment": payment,
        # Set outstanding balance based on principal
        "outstanding_balance": principal,
        "status": "active"
        # Optional fields like termination_date remain None by default
    }

    # 4. Final Validation (Pydantic is still used to check the structure)
    Loan(**loan_data)

    # 5. Store it
    system["loans"][l_id] = loan_data
    return loan_data


def get_loan(system: LoanBookSystem, l_id: str) -> Dict[str, Any] | None:
    # [ ... content unchanged ... ]
    """Retrieves a loan dictionary by its ID."""
    return system["loans"].get(l_id)


# --- STATUS CHANGE FUNCTIONS ---

def default_loan(system: LoanBookSystem, l_id: str, reason: str = "Failure to pay") -> bool:
    """Marks a loan as defaulted and records the termination date."""
    loan = get_loan(system, l_id)
    if not loan:
        # [ ... content unchanged ... ]
        print(f"Error: Loan {l_id} not found.")
        return False

    if loan["status"] in ["paid_off", "settled"]:
        # [ ... content unchanged ... ]
        print(f"Loan {l_id} cannot be defaulted. Current status: {loan['status']}")
        return False

    loan["status"] = "default"
    loan["termination_date"] = date.today()  # NEW: Record the default date
    print(f"Loan {l_id} is now set to DEFAULT. Reason: {reason}")
    return True


def settle_loan(system: LoanBookSystem, l_id: str) -> bool:
    """Marks a loan as fully settled, reducing the outstanding balance to zero, and records the settlement date."""
    loan = get_loan(system, l_id)
    if not loan:
        # [ ... content unchanged ... ]
        print(f"Error: Loan {l_id} not found.")
        return False

    if loan["status"] == "paid_off" or loan["status"] == "settled":
        print(f"Loan {l_id} is already paid off/settled.")
        return True

    if loan["outstanding_balance"] > 0:
        # [ ... content unchanged ... ]
        print(
            f"Warning: Settling loan {l_id} while balance is {loan['outstanding_balance']:,.2f}. Balance is being set to 0.0.")

    loan["outstanding_balance"] = 0.0
    loan["status"] = "settled"
    loan["settlement_date"] = date.today()  # NEW: Record the settlement date
    print(f"Loan {l_id} is now fully SETTLED. Outstanding balance is zero.")
    return True


def partial_settle_loan(system: LoanBookSystem, l_id: str, settlement_amount: float) -> bool:
    """
    Processes a lump-sum payment. Records the settlement date if the payment
    results in a full payoff.
    """
    loan = get_loan(system, l_id)
    if not loan:
        # [ ... content unchanged ... ]
        print(f"Error: Loan {l_id} not found.")
        return False

    if loan["status"] != "active":
        # [ ... content unchanged ... ]
        print(f"Error: Cannot partially settle loan {l_id}. Status is {loan['status']}")
        return False

    if settlement_amount <= 0:
        # [ ... content unchanged ... ]
        print("Error: Settlement amount must be positive.")
        return False

    if settlement_amount > loan["outstanding_balance"]:
        settlement_amount = loan["outstanding_balance"]
        # [ ... content unchanged ... ]
        print("Warning: Settlement amount exceeds outstanding balance. Using full balance amount.")

    # Update the balance
    loan["outstanding_balance"] -= settlement_amount

    print(f"Recorded Partial Settlement of ${settlement_amount:,.2f} on {l_id}.")
    print(f"New Outstanding Balance: ${loan['outstanding_balance']:,.2f}")

    # Check for full payoff after settlement
    if loan["outstanding_balance"] <= 0.01:
        loan["outstanding_balance"] = 0.0
        loan["status"] = "paid_off"
        loan["settlement_date"] = date.today()  # NEW: Record the settlement date
        print(f"Partial settlement resulted in full payoff. Loan {l_id} is now PAID OFF.")

    return True