import random
from models import Borrower  # Still useful for internal validation
from loan_system import initialize_loan_book, add_borrower, create_loan, LoanBookSystem

# --- Sample Data for Realistic Generation ---

_SAMPLE_FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "James",
    "Isabella", "Oliver", "Charlotte", "Benjamin", "Amelia", "Lucas", "Mia",
    "Henry", "Harper", "Alexander", "Evelyn", "Michael", "Abigail", "Daniel"
]

_SAMPLE_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
]


# --- Helper Functions ---

def _generate_apr_for_score(credit_score: int) -> float:
    """Generates a realistic APR based on credit score."""
    if credit_score >= 780:
        # Excellent credit
        apr = random.uniform(2.5, 5.0)
    elif credit_score >= 700:
        # Good credit
        apr = random.uniform(5.1, 8.5)
    elif credit_score >= 620:
        # Fair credit
        apr = random.uniform(8.6, 12.0)
    else:
        # Poor credit
        apr = random.uniform(12.1, 19.5)
    return round(apr, 2)


def _generate_random_borrower_data(borrower_id: str) -> dict:
    """Creates a single random borrower dictionary (for internal use before validation)."""
    return {
        "id": borrower_id,
        "first_name": random.choice(_SAMPLE_FIRST_NAMES),
        "last_name": random.choice(_SAMPLE_LAST_NAMES),
        "credit_score": random.randint(550, 850)
    }


# --- Main Public Function ---

def populate_loanbook(num_to_create: int) -> LoanBookSystem:
    """
    Creates and returns a loan book system dictionary populated with random loans.
    """
    system = initialize_loan_book()

    print(f"Generating {num_to_create} random loans...")
    for i in range(1, num_to_create + 1):
        # 1. Create Borrower Data
        b_id = f"CUST-{i:04d}"  # e.g., CUST-0001
        borrower_data = _generate_random_borrower_data(b_id)

        # Add borrower via the system function
        add_borrower(
            system=system,
            b_id=b_id,
            first=borrower_data['first_name'],
            last=borrower_data['last_name'],
            score=borrower_data['credit_score']
        )

        # 2. Generate Loan Parameters
        l_id = f"LOAN-{i:04d}"  # e.g., LOAN-0001
        principal = round(random.uniform(8000.00, 45000.00), 2)
        term = random.choice([24, 36, 48, 60, 72])
        apr = _generate_apr_for_score(borrower_data['credit_score'])

        # 3. Create Loan in the System
        create_loan(
            system=system,
            l_id=l_id,
            b_id=b_id,
            principal=principal,
            apr=apr,
            months=term
        )

    print(f"Successfully populated system with {len(system['loans'])} loans.")
    return system