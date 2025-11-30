from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


# These models are used solely to define the required structure and types for our loan/borrower dictionaries.

class Borrower(BaseModel):
    id: str
    first_name: str
    last_name: str
    credit_score: int = Field(gt=300, lt=850)


class Loan(BaseModel):
    id: str
    borrower_id: str
    principal: float = Field(gt=0)
    apr: float = Field(gt=0, lt=100)  # Annual Percentage Rate (e.g., 5.0)
    term_months: int = Field(gt=0)

    # Fundamental Dates (MANDATORY)
    start_date: date  # The contract date
    maturity_date: date  # The final contractual payment date

    status: str = "active"

    # Financial fields
    monthly_payment: float
    outstanding_balance: float

    # Termination/Settlement Dates (OPTIONAL)
    termination_date: Optional[date] = None  # Date of default or other termination
    settlement_date: Optional[date] = None  # Date loan balance went to zero