Here is the comprehensive technical documentation for your Loan Schedule Engine. This document outlines the mathematical principles, algorithms, and reconciliation logic used to generate the data in `loan_data.db`.

-----

# **Loan Schedule Calculation Methodology**

## **1. Overview**

This system generates day-accurate amortization schedules for fixed-term loan contracts. It solves the **"Flat Rate vs. Reducing Balance"** discrepancy by reverse-engineering the effective interest rate (APR) required to satisfy the contractual monthly payment, ensuring the final schedule aligns exactly with the legal contract totals.

**Input Data:**

  * Principal (Finance Amount)
  * Term (Months)
  * Contract Date
  * Fixed Monthly Repayment (Derived from Flat Rate)

**Output Data:**

  * Daily Accrual Amortization Schedule
  * Effective APR (Nominal)
  * XIRR (Effective Annual Cost)

-----

## **2. Calculation Standard**

### **2.1 Day Count Convention**

The schedule uses the **Actual/365** day count convention, which is standard for UK/EU consumer credit.

  * **Daily Rate:** Calculated as $\frac{APR}{365}$.
  * **Days in Period:** Calculated as the actual number of days between payment dates (e.g., 28, 30, or 31 days).
  * **Leap Years:** Treated as 365 days in the denominator (standard) but count 29 days in the numerator.

### **2.2 Rounding Principles**

To prevent "Hidden Decimal Drift" (where the sum of the database rows differs from the calculated total), **Intermediate Rounding** is applied.

  * **Principle:** All monetary values are rounded to **2 decimal places** immediately after calculation.
  * **Logic:**
    $$Interest = Round(Balance \times DailyRate \times Days, 2)$$
    $$ClosingBalance = Round(Opening + Interest - Repayment, 2)$$
  * **Effect:** The schedule reflects the exact "Penny Perfect" ledger seen by the customer and the bank.

-----

## **3. The "Reverse Solver" Algorithm**

Because the monthly repayment is fixed by the Flat Rate contract, we cannot simply guess an interest rate. We use a numerical root-finding algorithm to determine the precise **Implied APR**.

### **Method: Brent’s Method (`scipy.optimize.brentq`)**

We use Brent's Method to find the root of the amortization equation.

1.  **Objective Function:**
    $$f(APR) = RemainingBalance(APR) - 0$$
    *We simulate the full loan term using a specific APR. The goal is to find the APR where the Final Balance is exactly 0.00.*

2.  **Solver Bounds:**

      * Lower Bound: 0.0%
      * Upper Bound: 100.0%
      * Tolerance: `1e-6` (High precision convergence)

3.  **Why this is necessary:**
    Standard financial formulas (`PMT`, `RATE`) assume 12 equal months (30/360). Since we use actual calendar days (Act/365), a standard formula would leave a residual balance of £10–£50 at the end of the term. The Solver eliminates this drift.

-----

## **4. Reconciliation Logic (The "Final Month" Fix)**

To ensure strict compliance with the **Total Amount Payable (TAP)** stated in the contract, the final month is not calculated; it is **derived**.

### **The "Double Check" Approach**

We track the cumulative sum of Interest and Repayments for months 1 to $N-1$. In the final month ($N$):

1.  **Interest Reconciliation:**
    $$FinalInterest = TotalContractInterest - \sum_{i=1}^{N-1} Interest_i$$
    *Ensures the sum of the 'Interest' column equals the Contract Total exactly.*

2.  **Repayment Reconciliation:**
    $$FinalRepayment = TotalContractPayable - \sum_{i=1}^{N-1} Repayment_i$$
    *Ensures the sum of the 'Repayment' column equals the Contract Total exactly.*

3.  **Closing Balance:** Forced to **0.00**.

-----

## **5. Metrics Defined**

### **Flat Rate (Sales Rate)**

  * **Formula:** $\frac{Total Interest}{Principal \times Years} \times 100$
  * **Usage:** Used only to determine the fixed monthly repayment. It ignores the time value of money and the reducing balance.

### **Nominal APR (The "Solver" Result)**

  * **Definition:** The annualized rate that, when applied to the daily reducing balance, results in the fixed monthly repayment clearing the debt.
  * **Usage:** Used to calculate the daily interest accrual in the schedule.

### **XIRR (Extended Internal Rate of Return)**

  * **Definition:** The exact effective annual rate of return, accounting for the irregular gaps between dates (e.g., varying days in months).
  * **Formula:** Solves for $r$ in:
    $$\sum \frac{Payment_i}{(1+r)^{(d_i-d_0)/365}} = 0$$
  * **Usage:** The truest measure of loan cost. It will usually be slightly higher than the Nominal APR because it accounts for the compounding effect of 31-day months vs 28-day months.

-----

## **6. External References**

  * **Day Count Conventions (Act/365):** [ISDA Definitions](https://www.isda.org/2008/12/22/30-360-day-count-conventions/)
  * **Brent's Method (Root Finding):** [SciPy Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html)
  * **XIRR vs. IRR:** [Investopedia Explanation](https://www.google.com/search?q=https://www.investopedia.com/terms/x/xirr.asp)
  * **Consumer Credit Act (Total Payable):** [UK Legislation (Example)](https://www.legislation.gov.uk/ukpga/1974/39/contents)

-----

## **7. Python Implementation Summary**

| Component | Library | Function Used | Purpose |
| :--- | :--- | :--- | :--- |
| **Data Storage** | `sqlite3` | `to_sql` | Efficient local storage of relational data. |
| **Date Logic** | `pandas` | `Timestamp`, `DateOffset` | Handling date iteration and formatting. |
| **Solver** | `scipy` | `optimize.brentq` | Finding the precise APR (Goal Seek). |
| **Validation** | `pyxirr` | `xirr` | verifying the effective cost of the schedule. |