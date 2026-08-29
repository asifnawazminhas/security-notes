# Race Conditions

Race conditions occur when an application processes multiple operations concurrently and the final result depends on the timing or order in which those operations execute.

In web applications, race conditions are closely related to business logic vulnerabilities.

A typical application may perform several operations when processing a single request:

```text
Receive Request
      ↓
Check Current State
      ↓
Perform Action
      ↓
Update State
```

The problem occurs when multiple requests interact with the same state at approximately the same time.

For example:

```text
Request A                         Request B
    ↓                                 ↓
Check coupon unused              Check coupon unused
    ↓                                 ↓
Returns TRUE                     Returns TRUE
    ↓                                 ↓
Apply discount                   Apply discount
    ↓                                 ↓
Mark coupon used                 Mark coupon used
```

Both requests passed the validation before either request updated the state.

The intended logic:

```text
Check
 ↓
Act
 ↓
Update
```

effectively became:

```text
Check A
Check B
   ↓
Act A
Act B
   ↓
Update A
Update B
```

This can result in behaviour that should normally be impossible.

Potential impacts include:

```text
Multiple coupon redemption
Multiple gift-card redemption
Duplicate transactions
Exceeding account balances
Rate-limit bypass
Multiple password reset operations
MFA bypass
Account takeover
Email verification bypass
Duplicate voting
Inventory manipulation
Privilege escalation
Workflow bypass
Business logic abuse
```

!!! warning "Authorised Security Testing"
    Race-condition testing can generate multiple state-changing requests in a very short period. Perform testing only against authorised systems and preferably with dedicated test accounts and disposable data. Start with a very small number of parallel requests and avoid high-volume concurrency against production systems unless this has been explicitly approved.

---

# The Core Concept

A race condition usually exists because an application assumes that operations happen sequentially:

```text
Request
   ↓
Validate
   ↓
Perform Action
   ↓
Update State
```

But modern applications commonly process requests concurrently:

```text
                  ┌── Request A
Client ───────────┼── Request B
                  └── Request C
                         ↓
                  Application
                         ↓
                     Database
```

Multiple application threads or processes may therefore interact with the same:

```text
Database record
Session
Account
Order
Coupon
Balance
Token
File
Queue
Cache entry
```

at approximately the same time.

---

# Race Window

The period during which another request can interfere with an operation is called the:

```text
Race Window
```

For example:

```text
Check Coupon
     ↓
     ├──────── RACE WINDOW ────────┐
     ↓                             │
Apply Discount                     │
     ↓                             │
Mark Coupon Used ←─────────────────┘
```

Another request reaching the application during this window may also see:

```text
Coupon = unused
```

before the first request changes it.

Race windows may exist for only:

```text
Milliseconds
Microseconds
```

which makes precise request timing important.

---

# TOCTOU

Many race conditions are examples of:

```text
Time Of Check
     ↓
Time Of Use
```

commonly abbreviated:

```text
TOCTOU
```

The application checks something:

```text
Is coupon unused?
```

and later acts on that result:

```text
Apply coupon
```

The state may change between those operations.

Conceptually:

```text
CHECK
  ↓
Race Window
  ↓
USE
```

---

# Classic Example: Coupon Redemption

Suppose an application implements:

```text
1. Check whether coupon has been used
2. Apply discount
3. Mark coupon as used
```

Sequentially:

```text
Request 1
   ↓
Coupon unused?
   ↓
YES
   ↓
Apply discount
   ↓
Mark used
```

A second request should then fail:

```text
Request 2
   ↓
Coupon unused?
   ↓
NO
   ↓
Reject
```

But parallel requests may produce:

```text
Request A                 Request B
    ↓                         ↓
Coupon unused?            Coupon unused?
    ↓                         ↓
YES                       YES
    ↓                         ↓
Apply                     Apply
    ↓                         ↓
Mark used                 Mark used
```

Result:

```text
Single-use coupon
        ↓
Applied twice
```

---

# Limit-Overrun Race Conditions

One of the most common race-condition patterns is a:

```text
Limit Overrun
```

The application attempts to enforce a limit such as:

```text
Use once
Maximum 3 attempts
One vote
One transfer
One claim
One redemption
One registration
One reward
```

but concurrent requests exceed that limit.

Examples include:

```text
Redeeming one coupon multiple times
Redeeming one gift card multiple times
Submitting multiple votes
Exceeding withdrawal limits
Exceeding transfer limits
Bypassing login attempt limits
Using one CAPTCHA solution multiple times
Claiming one promotion multiple times
```

---

# Limit-Overrun Testing Model

```text
Identify Limit
      ↓
Understand Normal Behaviour
      ↓
Send Request Sequentially
      ↓
Confirm Limit Works Normally
      ↓
Send Small Parallel Group
      ↓
Compare Result
      ↓
Limit Exceeded?
      ↓
YES
      ↓
Race Condition
```

---

# Race Conditions vs Business Logic

Race conditions are often best understood as:

```text
Concurrency-dependent business logic flaws
```

A normal business logic vulnerability might be:

```text
Add cheap item
     ↓
Checkout
     ↓
Add expensive item
     ↓
Order confirmed without correct payment
```

A race variation might involve:

```text
Validate Payment ─────────────── Confirm Order
                         ↑
                    Race Window
                         ↑
                  Modify Basket
```

The application logic may be secure when requests are sequential but insecure when requests execute concurrently.

Refer to:

[Business Logic Vulnerabilities](business-logic.md)

---

# Why Race Conditions Are Difficult to Find

Race conditions can be difficult to identify because:

```text
Requests may need precise timing
Network jitter changes arrival times
Backend processing times differ
Multiple servers may be involved
Session locking may serialise requests
Database locking may change behaviour
The vulnerable state may exist briefly
The effect may be second-order
```

A vulnerability may therefore appear:

```text
Intermittent
Random
Unreliable
```

even when the underlying race condition is real.

---

# Network Jitter

Consider two requests sent at approximately the same time:

```text
Client
 ├── Request A ────────────────→ Server
 │
 └── Request B ─────────────────────→ Server
```

Network conditions may cause:

```text
Request A arrives at 10.001
Request B arrives at 10.016
```

A difference of:

```text
15 milliseconds
```

may be enough to miss the race window.

This is why specialised request synchronisation techniques are useful.

---

# Hidden Multi-Step Sequences

One of the most important concepts in modern race-condition testing is that a single HTTP request may trigger multiple internal operations.

For example:

```text
POST /login
      ↓
Validate Password
      ↓
Set User Session
      ↓
Check MFA Requirement
      ↓
Set MFA Enforcement
      ↓
Send MFA Code
      ↓
Return Response
```

From the browser's perspective:

```text
One Request
```

But internally:

```text
Many State Transitions
```

Each intermediate state can potentially create a race window.

---

# Sub-States

These temporary internal states are often referred to as:

```text
Sub-States
```

Example:

```text
Unauthenticated
      ↓
Password Validated
      ↓
Session Authenticated
      ↓
MFA Enforcement Enabled
      ↓
Fully Authenticated
```

The dangerous temporary state could be:

```text
Session Authenticated
      +
MFA Not Yet Enforced
```

If another request reaches a protected endpoint during that window:

```text
Login Request
      ↓
Temporary Authenticated State
      ↓
             Sensitive Request
                    ↓
              Access Granted?
```

a security control might be bypassed.

---

# State Machine Thinking

Race-condition testing becomes significantly easier when application functionality is viewed as a state machine.

For example:

```text
NEW ORDER
    ↓
PENDING PAYMENT
    ↓
PAYMENT VALIDATED
    ↓
ORDER CONFIRMED
    ↓
FULFILLED
```

Ask:

> What temporary states exist between these visible states?

Potential hidden states:

```text
Payment checked but order not locked

Balance checked but balance not updated

User created but email verification not applied

Session created but MFA flag not set

Password reset user selected but token not committed
```

These temporary states can become race-condition attack surfaces.

---

# PortSwigger Methodology

A useful methodology for advanced race-condition testing is:

```text
PREDICT
   ↓
PROBE
   ↓
PROVE
```

This provides a structured way to investigate concurrency issues without blindly racing every endpoint.

---

# Step 1: Predict Potential Collisions

First ask:

```text
Is the endpoint security-sensitive?
```

Then ask:

```text
Can multiple requests interact with the same data?
```

Potential shared resources include:

```text
Account balance
Coupon
Gift card
Session
Password reset state
Email address
Order
Basket
Invitation
Token
Username
Verification status
Rate-limit counter
```

---

# Collision Potential

Consider:

```text
Request A
      ↓
Record X

Request B
      ↓
Record Y
```

If the requests operate on completely different records:

```text
Collision Potential = Low
```

But:

```text
Request A
      ↓
Shared Record X
      ↑
Request B
```

has greater collision potential.

---

# High-Value Collision Targets

Prioritise functionality involving:

```text
Single-use resources
Balances
Counters
Tokens
State transitions
Authentication
Verification
Authorisation
Orders
Payments
Privileges
Inventory
```

---

# Step 2: Probe for Clues

First establish normal behaviour.

Send requests:

```text
Sequentially
```

and record:

```text
Status code
Response length
Response body
Headers
Application state
Email messages
Account state
Database-visible effects
```

Then send the same requests:

```text
In parallel
```

and compare the results.

---

# Benchmarking

Before attempting the race:

```text
Request 1
      ↓
Response

Request 2
      ↓
Response

Request 3
      ↓
Response
```

This establishes the baseline.

Then:

```text
Request 1 ─┐
Request 2 ─┼──→ Parallel
Request 3 ─┘
```

Compare:

```text
Sequential Behaviour
        vs
Parallel Behaviour
```

---

# Look Beyond HTTP Responses

Race-condition effects may not appear directly in the response.

Check:

```text
Account balance
Order status
Profile state
Email
Notification
Database-visible data
Application dashboard
Audit history
Token state
Coupon state
```

For example:

```text
Both responses:
200 OK
```

does not necessarily mean nothing happened.

The resulting account state may show:

```text
Coupon applied twice
```

---

# Step 3: Prove the Concept

Once unusual behaviour appears:

```text
Reduce Requests
      ↓
Identify Required Requests
      ↓
Repeat
      ↓
Understand State Transition
      ↓
Demonstrate Minimal Impact
```

The goal is to understand:

```text
What collided?
Where is the race window?
Which state became inconsistent?
What security boundary was crossed?
```

---

# Do Not Stop at "It Worked Once"

Race conditions can produce unusual one-off behaviour.

Try to establish:

```text
Repeatability
Cause
Required timing
Required session
Required endpoint combination
Resulting impact
```

A strong finding explains the underlying logic rather than merely showing that two requests produced an unexpected result.

---

# Single-Endpoint Race Conditions

A single endpoint may be vulnerable when multiple requests use different values.

Example:

```text
POST /password-reset
username=alice
```

and:

```text
POST /password-reset
username=bob
```

sent concurrently.

Internally, the application might store:

```text
session.resetUser
session.resetToken
```

If the operations interleave incorrectly:

```text
Request A                     Request B
   ↓                             ↓
Set user = Alice
                              Set user = Bob
   ↓
Generate token A
                              Generate token B
   ↓
Set token A
                              Set token B
```

unexpected combinations may occur.

---

# Shared Session State

Single-endpoint races frequently involve:

```text
Session variables
Temporary user state
Password reset state
Email verification state
Authentication state
```

Look for workflows where multiple requests modify:

```text
The same session
```

or:

```text
The same user object
```

---

# Email-Based Operations

Email workflows are particularly interesting because email delivery is often asynchronous.

Examples:

```text
Password reset
Email verification
Email change
Account invitation
Magic login links
```

Conceptually:

```text
HTTP Request
      ↓
Update State
      ↓
Queue Email
      ↓
HTTP Response
      ↓
Background Worker
      ↓
Send Email
```

This creates additional state transitions worth investigating.

---

# Multi-Endpoint Race Conditions

A multi-endpoint race occurs when different endpoints interact with the same underlying state.

Example:

```text
POST /checkout
```

and:

```text
POST /cart/add
```

The checkout process may:

```text
Calculate total
      ↓
Validate payment
      ↓
Confirm order
```

A concurrent cart modification may occur during the race window:

```text
Checkout
   ↓
Payment validated
   ↓
   ├──────── RACE WINDOW ────────┐
   ↓                             │
Confirm order                    │
                                 │
                         Add item to cart
```

Potential result:

```text
Order contains item
      ↓
Item was not included in payment
```

---

# Multi-Endpoint Testing Model

```text
Endpoint A
     ↓
Security-Sensitive Operation
     ↓
Shared State
     ↑
Endpoint B
     ↓
State Modification
```

Ask:

> Can Endpoint B modify data after Endpoint A validates it but before Endpoint A completes?

---

# Interesting Endpoint Combinations

Examples include:

```text
Checkout + Add Item

Checkout + Remove Item

Transfer + Transfer

Password Reset + Password Reset

Login + Protected Resource

Change Email + Verify Email

Create Account + Access Account

Redeem Coupon + Redeem Coupon

Approve + Modify

Delete + Update
```

---

# Aligning Race Windows

Different endpoints may require different amounts of processing.

Example:

```text
Endpoint A:
Request → DB → Response
          20 ms

Endpoint B:
Request → Validation → API → DB → Response
                    120 ms
```

Sending both requests at exactly the same time may not align the vulnerable operations.

You may need to understand:

```text
Network delay
Application processing delay
Database operations
External API calls
Connection establishment
```

---

# Connection Warming

The first request on a connection may incur additional setup cost.

For example:

```text
TLS
Connection establishment
Backend connection
Database connection
Cache population
```

A harmless preliminary request can sometimes reduce this variability.

Conceptually:

```text
Warm-Up Request
      ↓
Connection Established
      ↓
Race Requests
```

This can make timing more consistent.

---

# Session-Based Locking

Some frameworks serialise requests associated with the same session.

Instead of:

```text
Request A ─┐
Request B ─┼──→ Concurrent
Request C ─┘
```

the application may process:

```text
Request A
    ↓
Request B
    ↓
Request C
```

This can hide otherwise exploitable race conditions.

---

# Detecting Session Locking

Send several requests using the same session.

If response timing appears:

```text
Request 1 = 1 second
Request 2 = 2 seconds
Request 3 = 3 seconds
```

the requests may be queued.

Compare with requests using:

```text
Different sessions
```

if your authorised testing scenario permits it.

---

# PHP Session Locking

Some PHP applications use session mechanisms that can serialise requests sharing the same session identifier.

Therefore:

```text
Same Session
     ↓
Requests Serialised
```

may occur.

Testing with separate controlled sessions can help determine whether session locking is masking concurrency behaviour.

---

# Partial Construction Race Conditions

Applications frequently create objects in multiple stages.

Example user registration:

```text
Create User
     ↓
Generate API Key
     ↓
Set Default Permissions
     ↓
Require Email Verification
```

Temporary state:

```text
User Exists
     ↓
Security Attributes Not Fully Initialised
```

This is known as a:

```text
Partial Construction Race Condition
```

---

# Partial Object Example

Suppose:

```text
1. INSERT user
2. Generate verification state
3. Set role
4. Generate API key
```

Between steps:

```text
1
↓
User exists
↓
2
```

another request might interact with the partially created object.

Ask:

```text
Can it log in?
Can it access resources?
Can it modify itself?
Can it retrieve an uninitialised field?
```

---

# Partial Construction Testing

Look for workflows involving:

```text
Registration
Account provisioning
Organisation creation
API key generation
Invitation acceptance
Payment creation
File processing
Role assignment
```

Ask:

> Does the object become accessible before all security-sensitive attributes have been initialised?

---

# Deferred Operations

Some application operations occur after the HTTP response.

Example:

```text
HTTP Request
      ↓
Create Object
      ↓
Return 200 OK
      ↓
Background Job
      ↓
Complete Security Setup
```

This creates a potentially much larger race window.

Look for:

```text
Background workers
Queues
Email workers
Async jobs
Event handlers
Webhooks
```

---

# Rate-Limit Race Conditions

Suppose login attempts are tracked as:

```text
Read failedAttempts
      ↓
Check failedAttempts < 5
      ↓
Validate password
      ↓
Increment failedAttempts
```

Concurrent requests may all observe:

```text
failedAttempts = 0
```

before the counter is updated.

Conceptually:

```text
Request A → counter = 0
Request B → counter = 0
Request C → counter = 0
Request D → counter = 0
```

Then all attempts may proceed.

---

# Safe Rate-Limit Testing

Do not immediately send hundreds of requests.

Start with:

```text
2
```

then perhaps:

```text
3
```

controlled parallel attempts.

Determine whether the control counts:

```text
Requests received
Authentication attempts
Completed operations
Failed operations
```

---

# CAPTCHA Race Conditions

A single-use CAPTCHA may be processed as:

```text
Validate CAPTCHA
      ↓
Perform Action
      ↓
Invalidate CAPTCHA
```

Parallel requests may potentially reuse the same validation state.

Conceptually:

```text
Request A → CAPTCHA valid
Request B → CAPTCHA valid
                ↓
         Both continue
```

This is another example of a limit-overrun race.

---

# OTP and MFA

Potentially interesting operations include:

```text
OTP validation
MFA verification
MFA activation
MFA deactivation
Backup code usage
Recovery code usage
```

The question is not simply:

```text
Can the code be reused?
```

but also:

```text
What state exists between verification and invalidation?
```

---

# Password Reset

Password-reset workflows contain several potential shared states:

```text
Username
Reset token
Session
Email address
Token expiry
Token usage state
```

Map the entire process:

```text
Request Reset
      ↓
Identify User
      ↓
Generate Token
      ↓
Store Token
      ↓
Send Email
      ↓
Submit Token
      ↓
Change Password
      ↓
Invalidate Token
```

Each transition deserves analysis.

---

# Email Change

An email change might involve:

```text
Submit New Email
      ↓
Store Pending Email
      ↓
Generate Token
      ↓
Send Verification
      ↓
Verify Token
      ↓
Replace Current Email
```

Race testing should consider:

```text
Multiple email changes
Multiple verification requests
Verification while changing email again
Concurrent confirmation
```

using controlled addresses.

---

# Invitation Workflows

Invitation systems often involve:

```text
Create Invitation
      ↓
Generate Token
      ↓
Assign Role
      ↓
Send Email
      ↓
Accept Invitation
```

Potential collision targets:

```text
Role
Email
Organisation
Token
Invitation status
```

---

# Financial Operations

Financial workflows require extreme care.

Potential race-sensitive functionality includes:

```text
Balance checks
Transfers
Refunds
Credits
Withdrawals
Gift cards
Coupons
Payments
```

Conceptually:

```text
Check Balance = €100
        ↓
Transfer €80
        ↓
Update Balance
```

Two parallel transfers could theoretically both pass the original balance check.

In production assessments, use:

```text
Test accounts
Minimal values
Explicit approval
```

and stop as soon as sufficient evidence exists.

---

# Inventory and Reservations

Applications may implement:

```text
Check stock
      ↓
Reserve item
      ↓
Decrease stock
```

or:

```text
Check seat available
      ↓
Create reservation
      ↓
Mark seat unavailable
```

Parallel requests may expose race windows.

This can apply to:

```text
Tickets
Hotel rooms
Seats
Appointments
Products
Limited releases
```

---

# Voting and Ratings

Potential logic:

```text
Check user has not voted
      ↓
Record vote
      ↓
Mark user as voted
```

Parallel requests may cause:

```text
One user
   ↓
Multiple votes
```

The same concept applies to:

```text
Ratings
Likes
Reactions
Polls
Rewards
```

---

# File Processing

Race conditions can also affect files.

Potential patterns:

```text
Upload
 ↓
Validation
 ↓
Processing
 ↓
Move to Final Location
```

or:

```text
Check File
 ↓
Use File
```

If another operation can modify the file between:

```text
CHECK
```

and:

```text
USE
```

a TOCTOU issue may occur.

Refer to:

[File Upload Security](file-upload.md)

---

# Burp Suite

Burp Suite provides excellent functionality for race-condition testing.

Useful components include:

```text
Proxy
Repeater
Turbo Intruder
Comparer
Logger
```

For most manual testing, start with:

```text
Repeater
```

---

# Burp Repeater Request Groups

Modern Burp Repeater allows multiple requests to be grouped.

Conceptually:

```text
Repeater

Group:
 ├── Request 1
 ├── Request 2
 ├── Request 3
 └── Request 4
```

This is extremely useful for race-condition testing.

---

# Creating a Request Group

A practical workflow:

```text
Proxy
  ↓
Find Request
  ↓
Send to Repeater
  ↓
Duplicate Request
  ↓
Create Group
  ↓
Add Requests
```

For example:

```text
Race Test
 ├── Coupon Request 1
 ├── Coupon Request 2
 └── Coupon Request 3
```

---

# Sequential Requests

First benchmark the requests sequentially.

Use:

```text
Send group in sequence
```

Conceptually:

```text
Request A
   ↓
Response A
   ↓
Request B
   ↓
Response B
```

Record the expected application behaviour.

---

# Parallel Requests

Next send the group:

```text
In parallel
```

Conceptually:

```text
Request A ─┐
Request B ─┼──→ Server
Request C ─┘
```

Compare the results against the sequential baseline.

---

# Burp Single-Packet Attack

For HTTP/2 targets, Burp can use the:

```text
Single-Packet Attack
```

to significantly improve request synchronisation.

The goal is to reduce:

```text
Network Jitter
```

between requests.

Conceptually:

```text
HTTP/2 Connection
      ↓
Request A ── hold final fragment
Request B ── hold final fragment
Request C ── hold final fragment
      ↓
Release together
      ↓
Server receives requests
with extremely close timing
```

---

# Why Single-Packet Attacks Matter

Traditional parallel requests may arrive like:

```text
A ─────────→

B ─────────────→

C ─────────────────→
```

The single-packet technique aims for:

```text
A ───────────────┐
B ───────────────┼──→
C ───────────────┘
```

This can make very small race windows much easier to reach.

---

# HTTP/2

HTTP/2 is particularly useful because multiple request streams can share:

```text
One TCP connection
```

This allows request fragments to be synchronised more precisely than requests sent over independent connections.

Check the target protocol in Burp.

---

# Last-Byte Synchronisation

Where HTTP/2 single-packet techniques are not available, another concept is:

```text
Last-Byte Synchronisation
```

The general idea is:

```text
Send almost entire Request A
Send almost entire Request B
Send almost entire Request C
        ↓
Hold final bytes
        ↓
Release final bytes together
```

This attempts to reduce timing differences.

Modern Burp functionality handles much of this complexity for common scenarios.

---

# Turbo Intruder

Turbo Intruder is a Burp Suite extension designed for high-speed and highly configurable HTTP request execution.

It is particularly useful for:

```text
Race conditions
Precise request timing
Large request sets
Custom request sequencing
Complex attack logic
```

Install through:

```text
Burp Suite
   ↓
Extensions
   ↓
BApp Store
   ↓
Turbo Intruder
```

---

# Sending a Request to Turbo Intruder

In Burp:

```text
Proxy / Repeater
      ↓
Right-click Request
      ↓
Extensions
      ↓
Turbo Intruder
      ↓
Send to Turbo Intruder
```

Turbo Intruder opens an attack configuration window.

---

# Turbo Intruder and Race Conditions

Turbo Intruder is useful when:

```text
Repeater request groups are insufficient
Custom sequencing is required
Many synchronised requests are required
Timing needs precise control
Complex multi-step races are being investigated
```

For normal manual testing, Burp Repeater should often be the first choice.

---

# Safe Turbo Intruder Testing

Do not immediately configure:

```text
Thousands of requests
```

Start with:

```text
2 requests
```

then:

```text
3 requests
```

and increase only when necessary and explicitly permitted.

The objective is:

```text
Demonstrate concurrency flaw
```

not:

```text
Generate maximum traffic
```

---

# Turbo Intruder Workflow

```text
Capture Request
      ↓
Send to Turbo Intruder
      ↓
Select Race Template
      ↓
Configure Small Request Count
      ↓
Launch
      ↓
Compare Responses
      ↓
Check Application State
```

---

# Repeater vs Turbo Intruder

Use:

```text
Burp Repeater
```

when:

```text
Small request groups
Manual analysis
Single-packet testing
Simple races
Multi-endpoint races
```

Use:

```text
Turbo Intruder
```

when:

```text
Complex synchronisation
Custom logic
More advanced timing
Large controlled request sets
Special request sequencing
```

---

# Burp Comparer

Race-condition responses may differ only slightly.

Comparer can help analyse:

```text
Normal Response
       vs
Race Response
```

Look for differences in:

```text
Status
JSON
Headers
Tokens
Object IDs
State
Messages
```

---

# Burp Logger

Logger can help reconstruct the exact order in which requests were sent and responses received.

This is particularly useful for:

```text
Multi-endpoint races
Intermittent results
Long workflows
```

---

# Browser Verification

Always verify the final application state.

After the race attempt:

```text
Refresh account
Check balance
Check order
Check coupon
Check email
Check profile
Check verification status
```

The HTTP responses may not reveal the vulnerability directly.

---

# Time-Sensitive Attacks

Precise request synchronisation can reveal security issues even where there is not a conventional state collision.

For example:

```text
Request A
      ↓
Generate Token Based on Time

Request B
      ↓
Generate Token Based on Time
```

If token generation depends improperly on:

```text
High-resolution timestamp
```

closely timed requests might produce related or identical values.

Secure tokens should use:

```text
Cryptographically secure randomness
```

rather than predictable timestamps.

---

# Race Conditions and APIs

API endpoints are particularly important because they often expose clean state-changing operations.

Examples:

```text
POST /api/coupon
POST /api/order
POST /api/transfer
POST /api/invite
POST /api/password-reset
POST /api/verify
```

Map:

```text
Endpoint
 ↓
Resource
 ↓
State Read
 ↓
State Write
```

Refer to:

[API Security](api-security.md)

---

# Race Conditions and GraphQL

GraphQL mutations may also expose race conditions.

Example:

```graphql
mutation {
    redeemCoupon(code: "TEST") {
        success
    }
}
```

Parallel execution of the same mutation may interact with the same underlying record.

Conceptually:

```text
Mutation A ─┐
Mutation B ─┼──→ Coupon Resolver
Mutation C ─┘
                    ↓
               Shared Record
```

GraphQL aliases and batching can create additional concurrency and rate-limit considerations.

Refer to:

[GraphQL API Security](graphql.md)

---

# Race Conditions and WebSockets

WebSocket applications may also process messages concurrently or asynchronously.

Potential state-changing messages:

```text
purchase
transfer
redeem
update
accept
approve
```

If WebSocket functionality is in scope, examine whether multiple messages can interact with shared state.

Refer to:

[WebSocket Security](websockets.md)

---

# Race Conditions and Authentication

Authentication workflows deserve particular attention.

Potential targets:

```text
Login
MFA
Password reset
Email verification
Magic links
Account activation
Recovery codes
Session creation
```

Think in states:

```text
Unauthenticated
      ↓
Password Valid
      ↓
MFA Pending
      ↓
Authenticated
```

Then ask:

> Are any intermediate states externally usable?

Refer to:

[Authentication Testing](authentication.md)

---

# Race Conditions and Authorisation

Privilege changes may involve:

```text
Check Permission
      ↓
Perform Operation
      ↓
Update Permission / Object
```

Potentially interesting workflows include:

```text
Role changes
Ownership changes
Organisation membership
Invitation acceptance
Administrative approval
```

Refer to:

[Authorisation Testing](authorisation.md)

---

# Race Conditions and Session Management

Session state can be especially important.

Potential variables:

```text
userid
authenticated
mfa_verified
reset_user
reset_token
role
organisation
```

Concurrent requests modifying the same session may produce unexpected combinations.

Refer to:

[Session Management](session-management.md)

---

# Race Conditions and Caching

Caches can introduce additional asynchronous state.

Potential components:

```text
Application cache
Redis
CDN
Database cache
Session cache
```

A value may be:

```text
Updated in database
```

while:

```text
Old value remains in cache
```

This is not automatically a race-condition vulnerability, but inconsistent state across storage layers deserves investigation.

---

# Race Conditions and Microservices

Modern applications may perform:

```text
API Gateway
     ↓
Service A
     ↓
Message Queue
     ↓
Service B
     ↓
Database
```

Concurrency problems become more complex because state may exist across:

```text
Databases
Caches
Queues
Services
Workers
```

Ask:

```text
Where is validation performed?

Where is state updated?

Are these operations atomic?

Can another service modify the state in between?
```

---

# Race Conditions and Webhooks

Webhook workflows may create delayed state transitions.

Example:

```text
Create Payment
      ↓
Pending
      ↓
Payment Provider
      ↓
Webhook
      ↓
Paid
```

Potential race-sensitive operations:

```text
Cancel order while payment completes

Modify order while webhook processes

Submit duplicate webhook

Trigger refund while settlement occurs
```

Only test webhook behaviour within the authorised assessment scope.

---

# Identifying Candidate Endpoints

During application mapping, mark endpoints containing operations such as:

```text
apply
redeem
claim
use
verify
confirm
approve
transfer
withdraw
purchase
checkout
reset
change
register
invite
accept
activate
cancel
refund
vote
```

These verbs often indicate state transitions.

---

# Build a State Table

For important functionality:

| Operation | Before | Action | After |
|---|---|---|---|
| Redeem coupon | unused | redeem | used |
| Verify email | pending | verify | verified |
| Transfer | balance 100 | transfer 50 | balance 50 |
| Accept invite | pending | accept | member |
| Password reset | valid token | change password | token invalid |

Then ask:

```text
What happens if the same transition occurs twice simultaneously?
```

---

# Build a Collision Matrix

For advanced testing:

| Endpoint A | Endpoint B | Shared State | Potential Collision |
|---|---|---|---|
| Redeem | Redeem | Coupon | Multiple redemption |
| Checkout | Add item | Basket | Price mismatch |
| Reset | Reset | Session | Token/user mismatch |
| Register | Login | User | Partial account |
| Verify | Change email | Email state | Verification confusion |

This makes multi-endpoint testing systematic.

---

# Testing Decision Tree

```text
STATE-CHANGING ENDPOINT?
          ↓
         YES
          ↓
SINGLE-USE / LIMITED / SECURITY-SENSITIVE?
          ↓
         YES
          ↓
SHARED STATE?
          ↓
         YES
          ↓
BENCHMARK SEQUENTIALLY
          ↓
SEND SMALL PARALLEL GROUP
          ↓
BEHAVIOUR DIFFERENT?
      ↓          ↓
     NO         YES
      ↓          ↓
OTHER        INVESTIGATE
ENDPOINTS        ↓
           IDENTIFY WINDOW
                ↓
           REDUCE REQUESTS
                ↓
           REPRODUCE SAFELY
                ↓
              REPORT
```

---

# Predict, Probe, Prove

Quick reference:

```text
PREDICT
   ↓
Which requests could collide?

PROBE
   ↓
Does parallel behaviour differ from sequential behaviour?

PROVE
   ↓
Can the unexpected state be reproduced and explained?
```

This is one of the most useful mental models for race-condition testing.

---

# Testing Checklist

## Reconnaissance

```text
[ ] Map state-changing endpoints
[ ] Identify single-use actions
[ ] Identify rate-limited actions
[ ] Identify financial actions
[ ] Identify verification workflows
[ ] Identify authentication workflows
[ ] Identify invitation workflows
[ ] Identify state transitions
```

## State Analysis

```text
[ ] Identify shared resources
[ ] Identify read operations
[ ] Identify write operations
[ ] Identify temporary states
[ ] Identify background operations
[ ] Identify multiple storage layers
[ ] Build state diagram
```

## Baseline

```text
[ ] Send requests sequentially
[ ] Record status codes
[ ] Record response bodies
[ ] Record application state
[ ] Record email / notification effects
[ ] Confirm normal limits
```

## Parallel Testing

```text
[ ] Create Repeater group
[ ] Start with two requests
[ ] Send in parallel
[ ] Compare responses
[ ] Verify final state
[ ] Repeat if required
```

## Advanced Testing

```text
[ ] Test single endpoint
[ ] Test multiple endpoints
[ ] Test different values
[ ] Check session locking
[ ] Check separate sessions
[ ] Warm connections where appropriate
[ ] Use single-packet attack
[ ] Use Turbo Intruder where required
```

## Impact

```text
[ ] Limit overrun
[ ] Duplicate operation
[ ] Rate-limit bypass
[ ] Verification bypass
[ ] Authentication impact
[ ] Authorisation impact
[ ] Financial impact
[ ] Workflow bypass
[ ] Partial object access
```

---

# Quick Burp Workflow

```text
PROXY
  ↓
Find State-Changing Request
  ↓
REPEATER
  ↓
Duplicate Request
  ↓
Create Group
  ↓
SEND SEQUENTIALLY
  ↓
Record Baseline
  ↓
Reset Application State
  ↓
SEND IN PARALLEL
  ↓
Compare Responses
  ↓
Check Final Application State
  ↓
Unexpected Difference?
  ↓
YES
  ↓
Reduce + Reproduce
  ↓
Document
```

---

# Evidence Collection

For a confirmed race condition, collect:

```text
Affected endpoint
HTTP method
Required authentication
Initial application state
Expected state transition
Parallel requests
Request count
Timing method
Burp configuration
Sequential baseline
Parallel result
Final application state
Repeatability
Security impact
Screenshots
Request / response evidence
```

---

# Strong Evidence

Strong evidence shows:

```text
Sequential Requests
       ↓
Correct Security Control

Parallel Requests
       ↓
Security Control Bypassed
```

For example:

```text
Sequential:
Coupon request 1 → accepted
Coupon request 2 → rejected

Parallel:
Coupon request 1 → accepted
Coupon request 2 → accepted

Final state:
Discount applied twice
```

This clearly demonstrates the concurrency issue.

---

# Example Finding: Coupon Race Condition

```text
Finding:
Race Condition Allows Reuse of Single-Use Discount Code

Affected Endpoint:
POST /api/coupon/apply

Observed:
The application correctly prevented sequential reuse of the same single-use discount code.

However, when two identical redemption requests were submitted concurrently, both requests were processed before the coupon was marked as used.

Both requests therefore passed the application's validation logic.

Impact:
An authenticated user may redeem a single-use discount multiple times, resulting in unintended price reductions.

Recommendation:
Perform coupon validation and redemption as a single atomic operation and enforce the single-use constraint at the database level.
```

---

# Example Finding: Rate-Limit Race

```text
Finding:
Race Condition Allows Authentication Rate-Limit Bypass

Affected Endpoint:
POST /login

Observed:
Sequential failed authentication attempts were correctly counted and eventually blocked.

When a small group of authentication attempts was submitted concurrently, multiple attempts were processed before the failed-attempt counter was updated.

Impact:
An attacker may perform more authentication attempts than intended by the application's rate-limiting control.

Recommendation:
Update and evaluate authentication attempt counters atomically before allowing additional authentication processing.
```

---

# Example Finding: Partial Construction

```text
Finding:
Race Condition Allows Access to Partially Initialised User Accounts

Observed:
During account creation, the application created the user record before applying all required security attributes.

A concurrent request could interact with the account during this temporary state.

Impact:
An attacker may access account functionality before the expected account security controls have been fully applied.

Recommendation:
Create the account and all required security attributes within an atomic transaction or keep the account inaccessible until initialisation has completed successfully.
```

---

# Example Finding: Multi-Endpoint Race

```text
Finding:
Race Condition Allows Basket Modification After Payment Validation

Observed:
The checkout process validated the basket total before finalising the order.

A concurrent basket modification request could update the basket after payment validation but before order confirmation.

Impact:
An authenticated user may cause an order to contain items that were not included in the validated payment amount.

Recommendation:
Lock the order contents before payment validation and ensure that payment validation and order finalisation operate against the same immutable order state.
```

---

# Example Finding: Verification Race

```text
Finding:
Race Condition Allows Email Verification Workflow Bypass

Observed:
The account verification workflow temporarily exposed an account state in which the account existed and could be accessed before all email verification controls had been applied.

A concurrent request could interact with the account during this state.

Impact:
An attacker may be able to use account functionality without completing the required email verification process.

Recommendation:
Keep newly created accounts inaccessible until verification-related state has been fully initialised and enforce the transition atomically.
```

---

# Reporting Titles

Use precise titles such as:

```text
Race Condition Allows Reuse of Single-Use Discount Code

Race Condition Allows Authentication Rate-Limit Bypass

Race Condition Allows Duplicate Gift Card Redemption

Race Condition Allows Multiple Account Credits

Race Condition Allows Access to Partially Initialised Account

Race Condition Allows Basket Modification After Payment Validation

Race Condition in Password Reset Workflow Causes State Confusion

Race Condition Allows Email Verification Bypass

Race Condition Allows Duplicate Business Operation
```

Avoid vague titles such as:

```text
Race Condition Found
```

Describe what the race actually enables.

---

# Severity

Severity depends entirely on impact.

For example:

```text
Duplicate non-sensitive action
```

may have relatively low impact.

While:

```text
Race Condition
      ↓
Rate-Limit Bypass
      ↓
Account Compromise
```

may have high impact.

Or:

```text
Race Condition
      ↓
Payment Logic Bypass
      ↓
Financial Loss
```

may be severe.

Report:

```text
Demonstrated impact
```

rather than assigning severity based solely on the vulnerability class.

---

# Remediation

The fundamental goal is to ensure that security-sensitive state transitions are:

```text
Atomic
```

Conceptually:

```text
CHECK
  +
ACTION
  +
UPDATE
```

should behave as:

```text
ONE INDIVISIBLE OPERATION
```

rather than separate operations that concurrent requests can interleave.

---

# Database Transactions

Use database transactions where appropriate.

Instead of:

```text
SELECT coupon
      ↓
Application checks coupon
      ↓
UPDATE coupon
```

perform the security-sensitive transition transactionally.

Conceptually:

```text
BEGIN
  ↓
Lock / Validate
  ↓
Update
  ↓
COMMIT
```

---

# Database Constraints

Enforce critical invariants at the database level where possible.

Examples:

```text
Unique constraints
Single-use constraints
Foreign keys
Atomic counters
Conditional updates
```

Do not rely exclusively on application-layer checks.

---

# Atomic Updates

Instead of:

```text
Read value
   ↓
Check value
   ↓
Write new value
```

prefer atomic database operations where supported.

Conceptually:

```text
UPDATE resource
SET state = new_state
WHERE state = expected_state
```

Then verify:

```text
Rows affected = 1
```

---

# Row Locking

Appropriate locking mechanisms may include:

```text
Row-level locks
Transactions
Optimistic locking
Pessimistic locking
```

The correct choice depends on:

```text
Database
Performance
Application architecture
Business requirements
```

---

# Optimistic Locking

An object may contain:

```text
version = 5
```

An update requires:

```text
WHERE version = 5
```

and increments:

```text
version = 6
```

If another request has already modified the object:

```text
version != 5
```

the second operation fails.

---

# Idempotency

Sensitive operations should support idempotency where appropriate.

For example:

```text
Payment request
      ↓
Idempotency Key
      ↓
Already Processed?
   ↓           ↓
 YES          NO
 ↓             ↓
Return       Process
Existing     Once
Result
```

This helps prevent duplicate operations.

---

# Immutable Snapshots

For workflows such as checkout:

```text
Basket
   ↓
Create Immutable Order Snapshot
   ↓
Calculate Price
   ↓
Process Payment
   ↓
Confirm Same Snapshot
```

Do not validate one version of an object and later operate on a mutable version.

---

# Avoid Security-Relevant Sub-States

Where possible, do not expose partially completed security states.

Instead of:

```text
Create User
   ↓
User Accessible
   ↓
Configure Security
```

use:

```text
Create User
   ↓
Configure Security
   ↓
Activate User
   ↓
User Accessible
```

---

# Secure Registration

A safer conceptual model:

```text
Begin Transaction
      ↓
Create User
      ↓
Set Role
      ↓
Set Verification State
      ↓
Generate Required Security Data
      ↓
Commit
      ↓
Account Becomes Accessible
```

---

# Rate Limiting

Rate-limit counters should be updated atomically.

Avoid:

```text
Read Counter
    ↓
Check Counter
    ↓
Process Attempt
    ↓
Increment Counter
```

where multiple requests can observe the same original counter.

---

# Distributed Systems

In distributed applications, concurrency controls must work across:

```text
Multiple application servers
Containers
Workers
Regions
Processes
```

A process-local lock may not protect:

```text
Server A
```

from:

```text
Server B
```

Shared-state locking or transactional controls may therefore be necessary.

---

# Test After Remediation

After fixes:

```text
Establish Baseline
      ↓
Repeat Sequential Test
      ↓
Repeat Parallel Test
      ↓
Use Same Timing Technique
      ↓
Verify Final State
```

Confirm:

```text
Only one operation succeeds
```

where only one operation should be permitted.

---

# Tools

Useful tools include:

```text
Burp Suite
Burp Repeater
Turbo Intruder
Burp Comparer
Burp Logger
Browser DevTools
curl
Custom test scripts
```

For most web application race testing:

```text
Burp Repeater
      +
Request Groups
      +
Parallel Sending
      +
Single-Packet Attack
```

should be the starting point.

For more complex cases:

```text
Turbo Intruder
```

can provide greater control.

---

# References

## PortSwigger Web Security Academy: Race Conditions

https://portswigger.net/web-security/race-conditions

Covers:

```text
Limit-overrun race conditions
Hidden multi-step sequences
Predict, Probe, Prove methodology
Multi-endpoint races
Single-endpoint races
Session locking
Partial construction
Time-sensitive attacks
Remediation
```

---

## PortSwigger Race Condition Labs

https://portswigger.net/web-security/all-labs#race-conditions

Practical labs covering multiple race-condition techniques.

---

## PortSwigger Research: Smashing the State Machine

https://portswigger.net/research/smashing-the-state-machine

James Kettle's research on advanced web race conditions.

Important concepts include:

```text
Hidden sub-states
Single-endpoint races
Multi-endpoint races
Partial construction
State-machine analysis
Single-packet attacks
```

---

## PortSwigger Research: The Single-Packet Attack

https://portswigger.net/research/the-single-packet-attack-making-remote-race-conditions-local

Detailed research into reducing network jitter when exploiting remote race conditions.

---

## Turbo Intruder

https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988

Burp Suite extension by James Kettle for high-speed and highly configurable HTTP request execution.

Useful for:

```text
Race conditions
Custom timing
Complex request sequences
High-performance request handling
```

---

## Turbo Intruder GitHub

https://github.com/PortSwigger/turbo-intruder

Source code and additional information for Turbo Intruder.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

Useful general methodology for testing web application business logic and concurrency-related issues.

---

# Final Race Condition Testing Model

```text
                         APPLICATION
                              ↓
                    MAP BUSINESS LOGIC
                              ↓
                   IDENTIFY STATE CHANGES
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
          SINGLE-USE       SECURITY         BUSINESS
          RESOURCE          STATE            STATE
              ↓               ↓               ↓
              └───────────────┼───────────────┘
                              ↓
                       SHARED STATE?
                              ↓
                             YES
                              ↓
                          PREDICT
                              ↓
                    POTENTIAL COLLISION
                              ↓
                         BENCHMARK
                              ↓
                    SEQUENTIAL REQUESTS
                              ↓
                         BASELINE
                              ↓
                           PROBE
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
           REPEATER       SINGLE PACKET    TURBO INTRUDER
              ↓               ↓               ↓
              └───────────────┼───────────────┘
                              ↓
                    PARALLEL REQUESTS
                              ↓
                    BEHAVIOUR DIFFERENT?
                              ↓
                             YES
                              ↓
                           PROVE
                              ↓
                     IDENTIFY SUB-STATE
                              ↓
                    IDENTIFY RACE WINDOW
                              ↓
                     REDUCE REQUEST SET
                              ↓
                    REPRODUCE MINIMALLY
                              ↓
                     VERIFY FINAL STATE
                              ↓
                    SECURITY IMPACT?
                              ↓
                             YES
                              ↓
                         DOCUMENT
                              ↓
                           REPORT
```

The key principle is:

> Do not think of race-condition testing as simply sending the same request many times very quickly. Model the application's state transitions, identify operations that interact with the same data, establish normal sequential behaviour, then deliberately test whether concurrency exposes temporary sub-states that should never be externally accessible. Use Burp Repeater's parallel request groups and single-packet technique for precise manual testing, and move to Turbo Intruder when more advanced synchronisation or request sequencing is required.
