## Usage of the Cooperator Share Increase Loan Module

### Prerequisites

1. Configure the share products with:
   - Loan interest rate
   - Loan journal
   - Minimum loan periods
   - Required accounts (short term, long term, interest expenses)

### Creating Share Increase with Loan

1. Access Cooperatives > Cooperators menu
2. Select a cooperator
3. Create a new subscription request:
   - Type: Select "Increase"
   - Share Product: Select the configured share product
   - Number of shares to increase
   - The loan parameters will be automatically filled from the share product

### Process Flow

1. Validate the subscription request
   - System creates an invoice for the share increase

2. Pay the invoice
   - When the invoice is paid, the system automatically:
     * Creates a permanent loan
     * Links the invoice with the loan
     * Sets up loan payment schedule

### Viewing Loan Details

1. Go to Accounting > Loans > Loans
2. Find the loan created from the share increase
3. You can view:
   - Loan payment schedule
   - Related invoice
   - Interest calculations
   - Account movements

Note: The loan is automatically configured using the accounts from the share
product and the invoice. No additional configuration is needed after the
initial share product setup.
