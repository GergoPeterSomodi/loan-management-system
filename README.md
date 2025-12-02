# 🏦 Python Loan Book System

A modular system for managing vehicle financing loans.

## Setup
1. Open this project in PyCharm.
2. Create a virtual environment.
3. Install dependencies:
   `pip install -r requirements.txt`

## How to Run
Run `main.py`
Use `testin.ipynb` to interact with the system.

## Future project plan
#### Application process and credit scoring system 
- [ ]
* Create application data with the help of `AI` for future modelling
   * `Applicant name` `Address` `Income` `Credit Score` and other applicant and application related data
* Use the created application data to internally score the customer `Approve` or `Decline`
  * It should create a `estimated expenses` `disposable income` `maximum finance amount` and 
  * Need an automatic layer to it on a certain scenarios to automatically approve or decline
  * Create a report for manual underwriting which then be reviewed by `AI`
* For approved the application then produce create an `APR`
  * Use `AI` to replicate real life scenarios where the customer has the choice to `Accept` or `Decline` the offer
  * Create a returnable reason why the offer was declined `Better offer from competitor` `Too expensive` etc
* Save the data in a `Customer Data Warehouse` which is specifically for `PII` data
* Create a translator which saved non-PII data into a new `Internal Data Warehouse`
* `CRA reporting` may need PII connection, so need to make a connection in case it's needed to be called.

#### Loan Management System
* Need a module to create loan level data with `Loan Schedule` `Income Schedule`
* `Finance_amount` that's being paid out and `Receivables` that going to be received from the customer 

  1. `Charges` table to keep the customer charges `Loan_ID` `Product` `Created_date` `Due_date` `ID` `Recognised_ID`
  2. `Allocation` table to allocate cash that being received to the charges fallen due. 
     *  `Allocation` should be joint to `Charges` table based on `Recognised_ID`
     * `Cash` that cannot be allocated should go to overpayment
     * This should allow to track `Arrears` 
     * `AI` needed to create payments to replicate customer behaviours 
* `Income` should be recognised twice for accounting purposes once when a charge is fallen due and once at month end.
     * `Income_model` therefore need a daily interest recognition system
     * `Write off` to be allowed in the agreement

* `Status` to given to each loan `Live` `Default` `Settled` 
  * Need `life-changing events` in the system to move the statuses based on triggers.
  * `Rebate calculator` for `Full Settlements` and `Partial Settlements` in order to `rebate` interest from the loan.
  * `AI` to create settlement requests

    
#### Loan Loss Provisioning
* Implement `Loan Loss Provisioning` using `ECL Model`


#### Funding
* Create `funding entities` for `Warehousing` and/or `Securatisation` and the remaining to be financed from `balance sheet` until sold to the entities. 
* Funding entities will be the source of `Cost of Funds`
* Prepare sale monthly and hedge them with `Interest Rate Swaps` OR `Interest Rate Caps`

##### Unit Economics
* Create monitoring of `UE`

##### Portfolio Monitoring
* Monitor portfolio level performance

##### UI ideas for the Loan Management System
* Leverage AI to create a UI for the system
  
  

