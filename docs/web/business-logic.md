# Business Logic Vulnerabilities

Business logic vulnerabilities occur when an application correctly processes a request from a technical perspective but allows the application's intended rules, workflows or assumptions to be violated.

Unlike vulnerabilities such as SQL injection or Cross-Site Scripting, business logic vulnerabilities often do not involve malformed input.

The request may be completely valid.

The problem is that the application allows something that should not be possible according to the business rules.

For example:

```text
Product price: €100
        ↓
Customer changes quantity
        ↓
Application calculates total
        ↓
Checkout
```

A technical security test may ask:

```text
Can the quantity parameter contain SQL syntax?
```

A business logic assessment asks:

```text
Can quantity be negative?

Can the price be changed?

Can the discount be applied repeatedly?

Can checkout occur without payment?

Can the same voucher be reused?

Can a cheaper product be replaced after payment?

Can the workflow be completed out of order?
```

This requires understanding the business process before testing it.

!!! warning "Authorised Security Testing"
    Business logic testing should be based on functionality included in the authorised assessment scope. Avoid actions that cause financial loss, create real orders, consume limited resources or affect other users unless specifically agreed with the system owner.

---

# Business Logic Testing Mindset

Business logic testing should begin with:

```text
What does this functionality do?
```

followed by:

```text
What rules are supposed to govern it?
```

and then:

```text
What happens if those rules are violated?
```

A useful methodology is:

```text
Understand Business Function
          ↓
Identify Business Rules
          ↓
Identify Actors
          ↓
Identify Assets
          ↓
Identify State Transitions
          ↓
Identify Trust Assumptions
          ↓
Create Logic Threat Model
          ↓
Derive Test Cases
          ↓
Test Rules and Transitions
          ↓
Validate Business Impact
```

This makes business logic testing highly dependent on scope.

---

# Scope First

Do not begin business logic testing by searching for generic payloads.

First identify the business functions contained in the application.

For example, an application may contain:

```text
Pricing
Payments
Shopping basket
Discounts
Subscriptions
Account registration
Account recovery
Approvals
Document workflows
Booking
Reservations
Loyalty points
Credits
Refunds
Returns
Invitations
User roles
Resource allocation
```

Each business function creates a different threat model.

For example:

```text
Scope: Pricing
    ↓
Threat Model: Price Manipulation

Scope: Account Recovery
    ↓
Threat Model: Account Takeover

Scope: Approval Workflow
    ↓
Threat Model: Approval Bypass

Scope: Booking
    ↓
Threat Model: Reservation Manipulation

Scope: Subscription
    ↓
Threat Model: Entitlement Manipulation
```

This is more useful than applying the same generic checklist to every application.

---

# Logic Threat Modelling

For each important business function, create a small threat model.

A practical structure is:

```text
BUSINESS FUNCTION

What is being protected?

Who can perform the action?

What rules should apply?

What states exist?

Which transitions are allowed?

Which transitions must never occur?

Which values influence the outcome?

Which values are controlled by the client?

What does the server trust?

What happens if steps are skipped?

What happens if steps are repeated?

What happens if requests arrive in an unexpected order?
```

The answers become your test cases.

---

# Business Logic Threat Model

A useful model is:

```text
Business Function
       ↓
Actors
       ↓
Assets
       ↓
Business Rules
       ↓
State Machine
       ↓
Trust Boundaries
       ↓
Abuse Cases
       ↓
Security Tests
```

For example:

```text
Pricing
   ↓
Customer
   ↓
Product / Money
   ↓
Price must be calculated server-side
   ↓
Basket → Checkout → Payment
   ↓
Browser / Server
   ↓
Price manipulation
   ↓
Modify price-related values
```

---

# Think in Rules Rather Than Payloads

Traditional vulnerability testing often starts with:

```text
Input
 ↓
Payload
 ↓
Response
```

Business logic testing is different.

Think:

```text
Rule
 ↓
Assumption
 ↓
Violation
 ↓
Business Impact
```

For example:

```text
Rule:
A voucher may only be used once.

Assumption:
The application records voucher usage.

Violation:
Submit the voucher repeatedly.

Impact:
Repeated unauthorised discount.
```

This is the essence of business logic testing.

---

# Identify Business Rules

Business rules may come from:

```text
Application behaviour
Requirements
Documentation
User stories
Terms and conditions
API documentation
Help pages
UI restrictions
Error messages
Developer interviews
Business owner interviews
Observed workflows
```

Examples:

```text
A user may only redeem one voucher.

An order must be paid before shipment.

A refund cannot exceed the original payment.

A manager must approve transactions above €10,000.

A booking cannot contain a negative number of guests.

A free trial may only be activated once.

A user cannot approve their own request.

A customer cannot modify an order after shipment.
```

Each statement represents something worth testing.

---

# Convert Rules Into Tests

Take:

```text
Rule:
A voucher can only be used once.
```

Turn it into:

```text
Can the voucher be submitted twice?

Can it be submitted simultaneously?

Can it be applied to multiple baskets?

Can it be applied through the API after the UI rejects it?

Can case changes bypass the restriction?

Can the voucher be removed and re-added?

Can the same voucher be used from another session?
```

This technique is extremely effective.

---

# Example 1: Pricing Logic

Suppose the assessment scope includes an e-commerce application.

The relevant business process is:

```text
Select Product
      ↓
Add to Basket
      ↓
Calculate Price
      ↓
Apply Discount
      ↓
Checkout
      ↓
Payment
      ↓
Order
```

The threat model should focus on:

```text
Price integrity
Quantity integrity
Discount integrity
Currency
Shipping costs
Taxes
Payment amount
Order state
```

---

# Pricing Threat Model

Ask:

```text
Where does the price originate?

Is the price calculated by the server?

Does the browser send the price?

Can the client control the currency?

Can the client control the discount?

Can the quantity become zero?

Can the quantity become negative?

Can the total become negative?

Can shipping costs be modified?

Can tax calculations be influenced?

Can an old price be reused?

Can the price change between basket and checkout?

Does the payment provider amount match the order amount?
```

---

# Inspect the Request

Suppose Burp shows:

```http
POST /api/cart HTTP/1.1
Host: shop.example
Content-Type: application/json

{
    "productId": 1234,
    "quantity": 1,
    "price": 99.95
}
```

The immediately interesting property is:

```json
"price": 99.95
```

Ask:

> Why does the client need to tell the server the price?

The preferred design is:

```text
Client
  ↓
productId = 1234
quantity = 1
  ↓
Server
  ↓
Lookup Product
  ↓
Price = €99.95
  ↓
Calculate Total
```

Not:

```text
Client
  ↓
price = €99.95
  ↓
Server Trusts Price
```

---

# Price Manipulation

During an authorised test, controlled values might include:

```text
99.95
99.94
1.00
0.00
```

The objective is not to obtain products fraudulently.

The objective is to determine:

```text
Does the server independently determine the correct price?
```

Evidence should stop once the behaviour has been demonstrated.

---

# Quantity Manipulation

If the application accepts:

```json
{
    "quantity": 1
}
```

consider business boundaries such as:

```text
0
Negative values
Very large values
Decimal values
Values exceeding stock
Values exceeding account limits
```

The important question is:

```text
What values make sense according to the business process?
```

For most physical products:

```text
quantity > 0
```

should normally be enforced.

---

# Negative Quantity

Consider:

```text
Product A
€100
Quantity: -1
```

If the application calculates:

```text
€100 × -1 = -€100
```

the arithmetic may technically be correct.

The business logic is not.

Expected validation should resemble:

```text
Quantity
   ↓
Integer?
   ↓
Greater Than Zero?
   ↓
Within Stock Limit?
   ↓
Calculate Price
```

---

# Discount Logic

Suppose:

```text
WELCOME10
```

provides:

```text
10% discount
```

The business rules may state:

```text
One use per customer
Cannot combine with other vouchers
Only valid for selected products
Expires on a specific date
Minimum basket value applies
```

Convert each rule into a test.

```text
Can WELCOME10 be reused?

Can WELCOME10 be applied twice?

Can multiple vouchers be stacked?

Can the voucher be applied after expiration?

Can the basket be changed after the voucher is validated?

Can the minimum basket requirement be bypassed?

Can a restricted product receive the discount?
```

---

# Discount Stacking

Expected:

```text
€100
  ↓
WELCOME10
  ↓
€90
```

Potential logic issue:

```text
€100
  ↓
WELCOME10
  ↓
€90
  ↓
WELCOME10
  ↓
€81
  ↓
WELCOME10
  ↓
€72.90
```

The vulnerability is not the mathematical calculation.

The vulnerability is that:

```text
Single-use discount
```

became:

```text
Repeatable discount
```

---

# Basket Manipulation

Test state transitions such as:

```text
Add Product
     ↓
Apply Discount
     ↓
Modify Product
     ↓
Checkout
```

Ask whether security-relevant calculations are performed again after the basket changes.

For example:

```text
Expensive Eligible Product
          ↓
Apply Voucher
          ↓
Replace Product
          ↓
Discount Remains
```

This may reveal a state validation problem.

---

# Currency Logic

Applications supporting multiple currencies introduce additional logic.

Example:

```text
EUR
USD
GBP
```

Questions include:

```text
Who chooses the currency?

Where is conversion performed?

Is the exchange rate trusted from the client?

Can currency change after the price is calculated?

Does the payment provider receive the same currency?

Can currency identifiers and numeric values become mismatched?
```

The threat model is:

```text
Product
  ↓
Base Price
  ↓
Currency Conversion
  ↓
Displayed Price
  ↓
Payment Amount
```

Every transition should preserve value correctly.

---

# Pricing Logic Summary

```text
PRICING
   ↓
Price
Quantity
Discount
Currency
Tax
Shipping
Payment Amount
   ↓
Can Any Client-Controlled Value Alter Financial Outcome?
```

---

# Example 2: Account Recovery Logic

Suppose the application provides:

```text
Forgot Password
      ↓
Enter Email
      ↓
Recovery Token
      ↓
Verify Token
      ↓
Choose New Password
```

The threat model is completely different from pricing.

Assets:

```text
User account
Credentials
Recovery token
Authenticated session
```

Primary threat:

```text
Account takeover
```

---

# Recovery Threat Model

Ask:

```text
Who may initiate recovery?

How is the user identified?

How is the recovery token generated?

How long is the token valid?

Can it be reused?

Is it tied to a specific account?

Is it invalidated after password change?

Does requesting another token invalidate the previous token?

Can recovery steps be skipped?

Can the target account change during the workflow?

Is MFA enforced after recovery where required?
```

---

# Recovery State Machine

Expected:

```text
Unauthenticated
      ↓
Request Recovery
      ↓
Token Issued
      ↓
Token Verified
      ↓
Password Reset Authorised
      ↓
Password Changed
      ↓
Token Invalidated
```

Now identify forbidden transitions:

```text
Unauthenticated
      ↓
Password Changed
```

or:

```text
Token Issued
      ↓
Change Password
```

without:

```text
Token Verified
```

Those forbidden transitions become security tests.

---

# Step Skipping

Suppose the workflow is:

```text
Step 1: Enter email

Step 2: Enter verification code

Step 3: Set new password
```

Do not assume the UI represents server-side enforcement.

Test whether:

```text
Step 1
  ↓
Step 3
```

is accepted directly.

This is a general business logic principle:

> A multi-step user interface does not guarantee a multi-step server-side state machine.

---

# Token Reuse

Expected:

```text
Recovery Token
      ↓
Password Changed
      ↓
Token Invalid
```

Potential vulnerability:

```text
Recovery Token
      ↓
Password Changed
      ↓
Token Still Valid
      ↓
Password Changed Again
```

The security issue is a violation of the token lifecycle.

---

# Account Switching

Consider:

```text
Request reset for Alice
        ↓
Verify Alice's token
        ↓
Change account identifier to Bob
        ↓
Submit new password
```

The server should bind the entire workflow to the same account.

Expected:

```text
Recovery Token
      ↓
Specific User
      ↓
Specific Recovery Transaction
```

---

# Example 3: Approval Workflows

Consider a business application where transactions require approval.

Example:

```text
Employee
   ↓
Creates Request
   ↓
Manager
   ↓
Approves Request
   ↓
Finance
   ↓
Processes Request
```

Business rules might include:

```text
Creator cannot approve own request.

Requests above €10,000 require manager approval.

Requests above €50,000 require director approval.

Finance can only process approved requests.

Rejected requests cannot be processed.
```

These rules directly become tests.

---

# Approval Threat Model

Assets:

```text
Money
Contracts
Purchases
Sensitive changes
Business records
```

Actors:

```text
Requester
Manager
Director
Finance
Administrator
```

State machine:

```text
Draft
  ↓
Submitted
  ↓
Pending Approval
  ↓
Approved
  ↓
Processed
```

Alternative:

```text
Pending Approval
      ↓
Rejected
```

---

# Forbidden State Transitions

Potentially dangerous transitions include:

```text
Draft → Approved

Submitted → Processed

Rejected → Processed

Pending Approval → Processed
```

Also ask:

```text
Can the requester approve their own request?

Can approval level be changed?

Can the amount change after approval?

Can the beneficiary change after approval?

Can an approved request be replayed?

Can an old approval be reused?
```

---

# Modify After Approval

This is an important business logic pattern.

Expected:

```text
Request €5,000
      ↓
Manager Reviews €5,000
      ↓
Approved
      ↓
€5,000 Processed
```

Potential issue:

```text
Request €5,000
      ↓
Approved
      ↓
Change Amount to €50,000
      ↓
Process
```

The problem is:

```text
Approval applies to one state
```

but:

```text
Processing uses another state
```

Security-sensitive changes should invalidate previous approvals.

---

# Separation of Duties

Some business processes require:

```text
Person A performs Action 1

Person B approves Action 1
```

This is separation of duties.

Test whether:

```text
Person A
  ↓
Creates Request
  ↓
Changes Role / Request / Identifier
  ↓
Approves Own Request
```

is possible.

The relevant question is not merely:

```text
Does endpoint /approve require authentication?
```

It is:

```text
Is this authenticated user allowed to approve this particular transaction?
```

---

# Example 4: Booking and Reservation Logic

Consider:

```text
Search
  ↓
Select Availability
  ↓
Reserve
  ↓
Pay
  ↓
Confirmation
```

Assets may include:

```text
Seats
Rooms
Appointments
Tickets
Inventory
Time slots
```

Business rules may include:

```text
A slot can only be booked once.

A reservation expires after 10 minutes.

Payment must occur before confirmation.

Users may only hold a limited number of reservations.

Past dates cannot be booked.

Capacity cannot be exceeded.
```

---

# Booking Threat Model

Ask:

```text
Can unavailable inventory be booked?

Can a reservation be held indefinitely?

Can expired reservations be revived?

Can the date be changed after price calculation?

Can capacity be exceeded?

Can payment be skipped?

Can a reservation be duplicated?

Can the same resource be booked simultaneously?

Can a cheaper booking be changed into an expensive one after payment?
```

---

# Reservation State Machine

Expected:

```text
Available
    ↓
Reserved
    ↓
Payment Pending
    ↓
Paid
    ↓
Confirmed
```

Timeout:

```text
Reserved
    ↓
Expired
    ↓
Available
```

Forbidden transition:

```text
Expired
   ↓
Confirmed
```

without a new valid reservation.

---

# Race Conditions

Booking systems are particularly interesting for race conditions.

Consider one remaining seat:

```text
Available Seats = 1
```

Two simultaneous requests arrive:

```text
Request A ─┐
           ├── Reserve Seat
Request B ─┘
```

The application must ensure:

```text
Only One Request Succeeds
```

rather than:

```text
Request A → Success
Request B → Success
```

Business logic testing therefore often overlaps with race condition testing.

---

# Example 5: Subscription and Entitlement Logic

Consider a SaaS platform:

```text
Free
  ↓
Trial
  ↓
Professional
  ↓
Enterprise
```

Features may depend on subscription level.

Assets include:

```text
Premium features
API usage
Storage
Licences
Credits
Seats
Data exports
Integrations
```

---

# Subscription Threat Model

Ask:

```text
Can premium functionality be called directly?

Does the server enforce subscription level?

Can a free trial be activated repeatedly?

Can the subscription identifier be modified?

Can limits be bypassed through the API?

Can cancelled subscriptions continue using premium features?

Can downgrade and upgrade sequences create incorrect entitlements?

Can multiple accounts share a single entitlement unexpectedly?

Can usage counters be reset?
```

---

# Trial Abuse

Business rule:

```text
One trial per eligible customer.
```

Possible abuse cases:

```text
Create another trial

Cancel and restart trial

Change email address

Change organisation

Use another API endpoint

Replay activation request

Manipulate trial state
```

The exact tests depend on how the application defines:

```text
Customer
```

That itself is an important business rule.

---

# Entitlement Enforcement

The UI might hide:

```text
Export Report
```

for free users.

That does not prove the server enforces the restriction.

Test:

```text
Free User
    ↓
Direct API Request
    ↓
/api/export
```

Expected:

```text
Server Checks Subscription
        ↓
Denied
```

Not:

```text
Button Hidden
     ↓
Assumed Secure
```

---

# From Scope to Threat Model

The general process should therefore be:

```text
Assessment Scope
       ↓
Identify Business Functions
       ↓
Select Important Functions
       ↓
Create Logic Threat Model
       ↓
Identify Rules
       ↓
Identify State Machine
       ↓
Identify Abuse Cases
       ↓
Convert Abuse Cases Into Tests
```

---

# Example Scope Mapping

```text
E-Commerce
    ↓
Pricing
Discounts
Basket
Checkout
Payments
Refunds
    ↓
Financial Logic Threat Model
```

```text
Identity Platform
    ↓
Registration
Authentication
MFA
Password Reset
Account Recovery
    ↓
Identity Logic Threat Model
```

```text
Business Workflow Platform
    ↓
Submission
Approval
Rejection
Processing
    ↓
Workflow Logic Threat Model
```

```text
Booking Platform
    ↓
Availability
Reservation
Payment
Cancellation
    ↓
Resource Logic Threat Model
```

```text
SaaS Platform
    ↓
Trials
Plans
Licences
Entitlements
Usage Limits
    ↓
Subscription Logic Threat Model
```

---

# Identify Actors

For every workflow, identify who participates.

Example:

```text
Anonymous User
Customer
Employee
Manager
Administrator
Support
Finance
External Provider
Background Worker
```

Then ask:

```text
What can each actor do?

What can each actor not do?

What actions require another actor?

Can one actor impersonate another workflow role?

Can one actor perform multiple supposedly separated roles?
```

---

# Identify Assets

Assets are what the business process is protecting.

Examples:

```text
Money
Products
Accounts
Personal data
Documents
Approvals
Reservations
Credits
Discounts
Licences
Premium functionality
Inventory
Orders
Refunds
```

Knowing the asset makes the potential impact clearer.

---

# Identify Trust Boundaries

Business logic vulnerabilities frequently appear when one component trusts another incorrectly.

Example:

```text
Browser
   ↓
API
   ↓
Payment Service
```

Ask:

```text
Does the API trust values from the browser?

Does the application trust payment status from the browser?

Does the payment callback independently identify the order?

Does the order service verify the payment amount?
```

Trust boundaries may exist between:

```text
Browser ↔ API

API ↔ Database

Application ↔ Payment Provider

Application ↔ Identity Provider

Application ↔ Internal Service

User ↔ Administrator

Organisation A ↔ Organisation B
```

---

# Identify State

Business applications frequently operate as state machines.

Example:

```text
Order
 ↓
CREATED
 ↓
PAYMENT_PENDING
 ↓
PAID
 ↓
SHIPPED
 ↓
DELIVERED
```

Alternative transitions:

```text
PAYMENT_PENDING → CANCELLED

PAID → REFUNDED
```

Now ask:

```text
Can CREATED become SHIPPED?

Can CANCELLED become DELIVERED?

Can REFUNDED become SHIPPED?

Can SHIPPED return to PAYMENT_PENDING?

Can the client directly choose the state?
```

---

# State Transition Testing

For every workflow:

```text
List States
    ↓
List Allowed Transitions
    ↓
List Forbidden Transitions
    ↓
Test Forbidden Transitions
```

For example:

| Current State | Requested State | Expected |
|---|---|---|
| Draft | Submitted | Allowed |
| Submitted | Approved | Role dependent |
| Approved | Processed | Allowed |
| Draft | Processed | Denied |
| Rejected | Processed | Denied |
| Cancelled | Completed | Denied |

This simple exercise can reveal significant logic vulnerabilities.

---

# Sequence Testing

If the normal sequence is:

```text
A
↓
B
↓
C
↓
D
```

test:

```text
A → C

A → D

B → D

A → B → B → C

A → B → A → C

A → B → C → B

D → C
```

The objective is to determine whether the server enforces the workflow rather than relying on the user interface.

---

# Repeat Actions

Ask whether actions intended to occur once can occur multiple times.

Examples:

```text
Redeem voucher
Claim reward
Use invitation
Activate trial
Receive refund
Apply credit
Accept bonus
Confirm email
Use recovery token
Approve transaction
```

Generic test:

```text
Action
  ↓
Success
  ↓
Repeat Same Request
  ↓
What Happens?
```

---

# Replay Testing

Burp Repeater is particularly useful here.

Workflow:

```text
Perform Valid Action
      ↓
Capture Request
      ↓
Send to Repeater
      ↓
Repeat Request
      ↓
Observe State
```

Look for:

```text
Duplicate refund
Duplicate credit
Repeated discount
Repeated reward
Duplicate order
Repeated approval
Repeated state transition
```

---

# Client-Side Restrictions

Never assume a business rule is secure because the interface prevents the action.

Examples:

```text
Disabled button
Hidden field
JavaScript validation
Dropdown restriction
Read-only field
Hidden menu
Client-side price calculation
```

The real question is:

```text
Does the server enforce the rule?
```

---

# Hidden Parameters

Inspect requests for values such as:

```text
price
amount
discount
role
status
approved
paid
currency
quantity
accountId
userId
organisationId
plan
subscription
credit
balance
```

These values are especially interesting when they represent business decisions.

---

# Server-Generated Values

Ask whether values that should be server controlled are being supplied by the client.

Examples:

```text
Price
Tax
Discount percentage
Account balance
Payment status
Approval status
User role
Subscription level
Order state
Refund amount
```

Preferred architecture:

```text
Client Provides Intent
        ↓
Server Determines Business Outcome
```

For example:

```text
Client:
Buy product 123
Quantity 2
```

Server:

```text
Product 123
      ↓
Lookup Price
      ↓
Check Stock
      ↓
Calculate Tax
      ↓
Calculate Total
```

---

# Trust the Intent, Not the Outcome

A useful design principle is:

```text
Client Requests Action
```

rather than:

```text
Client Declares Result
```

Good:

```json
{
    "productId": 123,
    "quantity": 2
}
```

Suspicious:

```json
{
    "productId": 123,
    "quantity": 2,
    "price": 1.00,
    "discount": 99,
    "paid": true,
    "status": "completed"
}
```

The latter exposes multiple business decisions to client control.

---

# Burp Suite Workflow

A practical business logic workflow is:

```text
Use Application Normally
        ↓
Burp Proxy
        ↓
Map Complete Workflow
        ↓
Send Important Requests to Repeater
        ↓
Identify Business Parameters
        ↓
Create Baseline
        ↓
Modify One Assumption
        ↓
Replay
        ↓
Observe State
        ↓
Repeat With Another Rule
```

Business logic testing benefits greatly from understanding the normal workflow before modifying it.

---

# Burp Repeater

Use Repeater for:

```text
Parameter modification
Request replay
Step skipping
Sequence changes
State manipulation
Role testing
Identifier changes
Boundary testing
```

A useful Repeater naming scheme is:

```text
BL-PRICE-001
BL-DISCOUNT-001
BL-RECOVERY-001
BL-APPROVAL-001
BL-BOOKING-001
```

This keeps testing organised.

---

# Burp Comparer

Comparer can help identify subtle differences between:

```text
Normal Workflow
       vs
Modified Workflow
```

Compare:

```text
Status codes
Response bodies
JSON properties
Headers
Cookies
Identifiers
State values
```

---

# Burp Sequencer

Sequencer may be relevant when business logic depends on security tokens such as:

```text
Recovery tokens
Invitation tokens
Transaction identifiers
Coupon identifiers
One-time codes
```

Token predictability is a different vulnerability class, but it may affect the security of the overall business workflow.

---

# Race Conditions

Business logic rules sometimes work correctly when requests occur sequentially but fail when requests occur simultaneously.

Example:

```text
Balance = €100
```

Two requests:

```text
Withdraw €80
Withdraw €80
```

If both check:

```text
Balance >= €80
```

before either updates the balance:

```text
Request A → Approved
Request B → Approved
```

Result:

```text
€160 withdrawn from €100 balance
```

This is a race condition affecting business logic.

---

# Race Condition Candidates

High-value operations include:

```text
Payments
Withdrawals
Discount redemption
Voucher redemption
Reward claiming
Inventory
Bookings
Reservations
Account creation limits
Invitation usage
Password reset
MFA operations
Credit consumption
API quota enforcement
```

---

# Limit Testing

Whenever a business rule contains:

```text
once
maximum
minimum
per day
per user
per account
per organisation
per transaction
only one
up to
```

there is a test opportunity.

Examples:

```text
Maximum 5 tickets

One voucher per user

Maximum withdrawal €1,000

One free trial

10 API requests per minute

Maximum refund equal to original payment
```

Test boundaries:

```text
limit - 1
limit
limit + 1
```

and where authorised:

```text
Repeated
Concurrent
Alternative workflow
Different session
Different endpoint
```

---

# Refund Logic

Refund systems deserve their own mini threat model.

Expected:

```text
Payment €100
     ↓
Maximum Refund €100
```

Ask:

```text
Can refund exceed payment?

Can the same payment be refunded twice?

Can partial refunds exceed the original amount cumulatively?

Can cancelled payments be refunded?

Can another order identifier be supplied?

Can refund destination be modified?

Can the refund be repeated concurrently?
```

---

# Credit and Loyalty Logic

Applications may use:

```text
Store credit
Points
Tokens
Rewards
Gift balances
Promotional balances
```

Threat model:

```text
Earn
 ↓
Store
 ↓
Redeem
 ↓
Balance Updated
```

Ask:

```text
Can credit be redeemed twice?

Can negative values increase balance?

Can points be transferred repeatedly?

Can expired credit be revived?

Can another user's balance identifier be supplied?

Can earn and redeem operations race?
```

---

# File and Document Workflows

Business logic also applies to non-financial applications.

Example:

```text
Create Document
      ↓
Submit
      ↓
Review
      ↓
Approve
      ↓
Publish
```

Questions:

```text
Can draft documents be published?

Can rejected documents be approved?

Can the document change after approval?

Can a user approve their own document?

Can review be skipped?

Can an old approval apply to a new document version?
```

This demonstrates that business logic testing is much broader than e-commerce.

---

# Logic Threat Modelling Template

For each important feature, create:

```text
FEATURE:
Pricing

ASSET:
Financial integrity

ACTORS:
Customer
Application
Payment provider

EXPECTED WORKFLOW:
Product → Basket → Checkout → Payment → Order

BUSINESS RULES:
Server determines price
Quantity must be positive
Voucher can be used once
Payment amount must equal order amount

TRUST BOUNDARIES:
Browser → API
API → Payment provider

ABUSE CASES:
Price modification
Negative quantity
Voucher replay
Payment mismatch

TESTS:
Modify price
Test quantity boundaries
Replay voucher
Compare order amount with payment amount
```

---

# Another Logic Threat Model

```text
FEATURE:
Password Recovery

ASSET:
User account

ACTORS:
Anonymous user
Account owner
Application

EXPECTED WORKFLOW:
Request → Token → Verify → Reset

BUSINESS RULES:
Token belongs to one user
Token expires
Token can only be used once
Verification must occur before reset

ABUSE CASES:
Skip verification
Reuse token
Switch account
Use expired token

TESTS:
Request final endpoint directly
Replay token
Change account identifier
Test token after expiration
```

---

# Business Logic Checklist

## Understand

```text
[ ] Identify important business functions
[ ] Identify actors
[ ] Identify assets
[ ] Identify business rules
[ ] Identify trust boundaries
[ ] Identify workflow states
[ ] Identify allowed transitions
[ ] Identify forbidden transitions
```

## Client Control

```text
[ ] Identify client-controlled prices
[ ] Identify client-controlled quantities
[ ] Identify client-controlled roles
[ ] Identify client-controlled status
[ ] Identify client-controlled account IDs
[ ] Identify client-controlled approval values
[ ] Identify client-controlled payment values
```

## Workflow

```text
[ ] Skip steps
[ ] Repeat steps
[ ] Reverse steps
[ ] Perform steps out of order
[ ] Replay completed actions
[ ] Modify values between steps
[ ] Test stale workflow state
```

## Limits

```text
[ ] Test minimum
[ ] Test maximum
[ ] Test zero
[ ] Test negative values
[ ] Test limit + 1
[ ] Test repeated actions
[ ] Consider concurrency
```

## State

```text
[ ] Map states
[ ] Test forbidden transitions
[ ] Modify object after approval
[ ] Modify object after payment
[ ] Test cancelled state
[ ] Test expired state
[ ] Test completed state
```

---

# Evidence Collection

Business logic findings require clear evidence because the requests themselves may appear completely legitimate.

Record:

```text
Business function
Expected rule
Normal workflow
Modified workflow
Affected endpoint
Affected parameter
Original value
Modified value
Application response
Resulting application state
Business impact
Affected actor
Required privileges
```

---

# Example Evidence

```text
Finding:
Product Price Manipulation

Business Rule:
Product prices must be determined by the server.

Normal Request:
productId=123
price=99.95

Modified Request:
productId=123
price=1.00

Observed Result:
Application accepted €1.00 as the order price.

Expected Result:
Server should ignore client-provided price and retrieve the current
price for product 123.

Impact:
A customer can manipulate the amount associated with an order.
```

In a real assessment, stop before completing a financially damaging transaction unless the agreed test procedure explicitly allows it.

---

# Reporting Business Logic Vulnerabilities

Avoid vague titles such as:

```text
Business Logic Issue
```

Describe the violated rule.

Better titles include:

```text
Product Price Can Be Manipulated During Checkout

Single-Use Discount Code Can Be Redeemed Multiple Times

Password Reset Verification Can Be Skipped

Requester Can Approve Their Own Transaction

Approved Transaction Amount Can Be Modified Before Processing

Expired Reservation Can Be Confirmed

Free Trial Can Be Activated Repeatedly

Refund Amount Can Exceed Original Payment
```

The title should immediately explain the business impact.

---

# Description

A good description explains:

```text
What the application is designed to do

What business rule should apply

How the workflow can be manipulated

Why server-side controls fail

What outcome becomes possible
```

Business context is especially important here.

---

# Impact

Describe impact in terms of the affected business.

Examples:

```text
Financial loss
Unauthorised discounts
Unauthorised refunds
Account takeover
Approval bypass
Subscription bypass
Inventory exhaustion
Reservation abuse
Unauthorised access to premium functionality
Violation of separation of duties
Workflow integrity failure
```

Avoid overstating impact.

---

# Remediation

Business logic vulnerabilities usually cannot be fixed with a generic security header or WAF rule.

The underlying business rule must be enforced.

---

# Enforce Rules Server-Side

All security-relevant business decisions should be validated server-side.

For example:

```text
Client:
productId = 123
quantity = 2
```

Server:

```text
Lookup Product
      ↓
Retrieve Price
      ↓
Validate Quantity
      ↓
Check Stock
      ↓
Apply Valid Discount
      ↓
Calculate Tax
      ↓
Calculate Total
```

---

# Validate Every State Transition

Do not only check whether the user is authenticated.

Check whether the requested transition is valid.

For example:

```text
Current State = Pending Approval

Requested State = Processed
```

Server should ask:

```text
Is Pending Approval → Processed allowed?
```

If not:

```text
Reject
```

---

# Revalidate After Changes

If an important object changes after approval, validation should occur again.

Example:

```text
Transaction
    ↓
Approved
    ↓
Amount Changes
    ↓
Approval Invalidated
    ↓
Reapproval Required
```

This applies to:

```text
Amount
Beneficiary
Product
Quantity
Account
Document
Permissions
Scope
```

---

# Enforce Idempotency Where Required

Operations intended to happen once should not produce additional effects when replayed.

Examples:

```text
Payment
Refund
Voucher redemption
Reward claim
Order creation
Approval
```

Where appropriate, use unique transaction identifiers and idempotency controls.

---

# Use Atomic Operations

For concurrency-sensitive business rules:

```text
Check
  +
Update
```

should occur atomically where required.

This helps prevent:

```text
Check Balance
      ↓
Concurrent Request
      ↓
Both Requests Succeed
```

---

# Business Logic Quick Reference

```text
Understand Function
       ↓
What Is the Asset?
       ↓
Who Are the Actors?
       ↓
What Are the Rules?
       ↓
What Are the States?
       ↓
What Transitions Are Allowed?
       ↓
What Does the Client Control?
       ↓
What Does the Server Trust?
       ↓
What Happens If I:

Change a value?
Skip a step?
Repeat a step?
Reverse the sequence?
Replay a request?
Exceed a limit?
Use zero?
Use a negative value?
Change state after approval?
Send requests simultaneously?
```

---

# Five Useful Logic Threat Models

```text
PRICING

Protect:
Money

Test:
Price
Quantity
Discount
Currency
Tax
Shipping
Payment amount
```

```text
ACCOUNT RECOVERY

Protect:
Account

Test:
Token lifecycle
Step skipping
Account binding
Token reuse
State transitions
```

```text
APPROVAL

Protect:
Business decision

Test:
Self-approval
Approval levels
Step skipping
Post-approval modification
Separation of duties
```

```text
BOOKING

Protect:
Limited resource

Test:
Availability
Capacity
Reservation expiration
Payment
Concurrency
State transitions
```

```text
SUBSCRIPTION

Protect:
Entitlements

Test:
Plan restrictions
Trials
Usage limits
Cancellation
Upgrade/downgrade
Feature access
```

---

# Tools

Business logic testing usually requires fewer specialised tools than injection testing.

Useful tools include:

```text
Burp Suite
Burp Proxy
Burp Repeater
Burp Comparer
Burp Sequencer
Turbo Intruder
Browser Developer Tools
API documentation
Application documentation
```

The most important tool remains:

```text
Understanding the business process
```

---

# References

## PortSwigger Web Security Academy

Business logic vulnerabilities:

https://portswigger.net/web-security/logic-flaws

PortSwigger provides practical examples covering flawed assumptions, excessive trust in client-side controls, inconsistent input handling, workflow bypasses and other application logic vulnerabilities.

---

## PortSwigger Race Conditions

https://portswigger.net/web-security/race-conditions

Useful when business rules fail because multiple operations can occur concurrently.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

The OWASP Web Security Testing Guide contains testing guidance covering business logic and application workflows.

---

## OWASP Business Logic Testing

https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/README

Useful reference for structured testing of application-specific business rules.

---

# Final Business Logic Workflow

```text
Read Scope
    ↓
Understand Application
    ↓
Identify Business Functions
    ↓
Choose High-Value Functions
    ↓
For Each Function:
    ↓
Identify Actors
    ↓
Identify Assets
    ↓
Identify Business Rules
    ↓
Identify Trust Boundaries
    ↓
Map States
    ↓
Map Allowed Transitions
    ↓
Identify Forbidden Transitions
    ↓
Create Abuse Cases
    ↓
Convert Abuse Cases Into Tests
    ↓
Capture Normal Workflow in Burp
    ↓
Establish Baseline
    ↓
Change One Business Assumption
    ↓
Test Server-Side Enforcement
    ↓
Test Sequence
    ↓
Test Replay
    ↓
Test Boundaries
    ↓
Consider Concurrency
    ↓
Validate Business Impact
    ↓
Collect Minimum Necessary Evidence
    ↓
Report the Violated Business Rule
```

The key principle is:

> Business logic testing should follow the business. If the application handles pricing, threat model pricing. If it handles account recovery, threat model recovery. If it handles approvals, threat model the approval process. If it manages bookings, threat model the lifecycle of the reserved resource. Understand the intended rules first, then systematically test whether those rules can be violated.
