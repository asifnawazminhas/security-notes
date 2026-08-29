# WebSocket Security

WebSockets provide persistent, bidirectional communication between a client and server.

Unlike traditional HTTP communication:

```text
Client
  ↓
HTTP Request
  ↓
Server
  ↓
HTTP Response
```

WebSockets establish a long-lived connection:

```text
Client
   ↕
WebSocket Connection
   ↕
Server
```

Once established, both the client and server can send messages independently.

WebSockets are commonly used for:

```text
Chat applications
Notifications
Trading platforms
Dashboards
Games
Collaboration platforms
Real-time monitoring
Support systems
Administrative interfaces
Live feeds
IoT applications
```

From a security testing perspective, WebSockets should be treated as another application interface.

The important questions are:

```text
How is the connection established?

How is the user authenticated?

How is authorisation enforced?

What messages exist?

What objects can messages access?

What business actions can messages perform?

Is input validated?

Can messages be replayed?

Can messages be modified?

Can another origin establish the connection?
```

!!! warning "Authorised Security Testing"
    Test WebSocket functionality only where explicitly included in the authorised assessment scope. Real-time applications may perform immediate actions when messages are submitted, so understand each message before modifying or replaying it.

---

# WebSocket Architecture

A typical application may look like:

```text
Browser
   ↓
HTTPS
   ↓
Web Application
   ↓
WebSocket Upgrade
   ↓
Persistent Connection
   ↕
Application Server
```

Once established:

```text
Browser                         Server

   │                              │
   │──── WebSocket Message ──────>│
   │                              │
   │<──── WebSocket Message ──────│
   │                              │
   │──── WebSocket Message ──────>│
   │                              │
```

This differs from the traditional:

```text
Request
   ↓
Response
   ↓
Request
   ↓
Response
```

model.

---

# ws and wss

WebSocket URLs commonly use:

```text
ws://
```

or:

```text
wss://
```

For example:

```text
ws://example.com/socket
```

or:

```text
wss://example.com/socket
```

`wss://` represents WebSockets over TLS and should generally be used for sensitive communications.

Conceptually:

```text
ws://
 ↓
WebSocket over plaintext transport
```

```text
wss://
 ↓
WebSocket over TLS
```

---

# The WebSocket Handshake

A WebSocket connection normally begins as an HTTP request.

Example:

```http
GET /chat HTTP/1.1
Host: target.example
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://target.example
Cookie: session=...
```

The important headers include:

```text
Upgrade
Connection
Sec-WebSocket-Key
Sec-WebSocket-Version
Origin
Cookie
Authorization
```

The server may respond:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: ...
```

The HTTP connection has now been upgraded.

Conceptually:

```text
HTTP Request
     ↓
Upgrade: websocket
     ↓
Server Accepts
     ↓
101 Switching Protocols
     ↓
WebSocket Connection
```

---

# Why the Handshake Matters

The handshake may contain security-sensitive information such as:

```text
Session cookies
Bearer tokens
Origin
Query parameters
Custom authentication headers
WebSocket protocol information
```

Testing therefore begins before the first WebSocket message is sent.

Questions include:

```text
Does the handshake require authentication?

Is the Origin validated?

Can authentication parameters be removed?

Can another user's session be used?

Are sensitive tokens placed in the URL?

Does the server accept unexpected subprotocols?
```

---

# WebSocket Discovery

WebSocket endpoints can be discovered through:

```text
Burp Suite
Browser Developer Tools
JavaScript
HTML source
Network traffic
Application documentation
API documentation
```

Search for:

```text
ws://
wss://
WebSocket(
socket
/socket
/ws
/websocket
```

---

# JavaScript Discovery

Applications frequently create WebSocket connections in JavaScript.

Example:

```javascript
const socket = new WebSocket("wss://target.example/chat");
```

Search JavaScript files:

```bash
rg -i 'WebSocket|wss://|ws://' .
```

or:

```bash
grep -RniE 'WebSocket|wss://|ws://' .
```

Look for:

```text
WebSocket URLs
Message types
JSON structures
Event names
Authentication tokens
Object identifiers
Administrative actions
```

---

# Browser Developer Tools

Modern browsers provide WebSocket visibility through Developer Tools.

Open:

```text
Developer Tools
    ↓
Network
    ↓
WS
```

Select the WebSocket connection.

You can normally inspect:

```text
Handshake
Messages
Frames
Direction
Payload
Timing
```

This is useful for understanding the protocol before modifying anything.

---

# Burp Suite

Burp Suite provides excellent WebSocket support.

A practical workflow is:

```text
Browser
   ↓
Burp Proxy
   ↓
WebSocket Handshake
   ↓
Connection Established
   ↓
WebSocket Messages
   ↓
Burp WebSockets History
```

Burp can intercept and modify WebSocket messages in a similar way to HTTP traffic.

---

# Burp WebSockets History

In Burp Suite, look for the WebSockets history.

Depending on the Burp version, WebSocket traffic is available through Proxy and related message views.

You should be able to inspect:

```text
Client → Server

Server → Client
```

messages.

For example:

```json
{
    "type": "message",
    "text": "Hello"
}
```

Response:

```json
{
    "type": "message",
    "username": "alice",
    "text": "Hello"
}
```

---

# Map the WebSocket Protocol

Before testing, document the messages used by the application.

For example:

```text
AUTH
JOIN
MESSAGE
EDIT
DELETE
LEAVE
PING
```

Or JSON:

```json
{
    "action": "join",
    "roomId": 100
}
```

```json
{
    "action": "message",
    "roomId": 100,
    "message": "Hello"
}
```

```json
{
    "action": "delete",
    "messageId": 500
}
```

This creates a protocol map.

---

# WebSocket Message Inventory

Create a table such as:

| Message | Direction | Authentication | Object | Action |
|---|---|---|---|---|
| `join` | Client → Server | User | Room | Join |
| `message` | Client → Server | User | Room | Create |
| `edit` | Client → Server | User | Message | Modify |
| `delete` | Client → Server | User | Message | Delete |
| `users` | Client → Server | User | Room | Read |
| `admin-ban` | Client → Server | Admin | User | Ban |

Now the WebSocket becomes much easier to threat model.

---

# WebSocket Threat Modelling

Use the same principle as API testing.

Identify:

```text
Actors
Objects
Actions
Properties
Business Rules
States
Trust Boundaries
```

Example:

```text
ACTORS

Anonymous
User
Moderator
Administrator
```

```text
OBJECTS

Room
Message
User
Notification
Channel
```

```text
ACTIONS

Join
Read
Send
Edit
Delete
Ban
Invite
```

Then ask:

```text
Which actor may perform which action against which object?
```

---

# Authentication

WebSocket authentication may occur:

```text
During HTTP handshake
```

or:

```text
After connection establishment
```

or both.

Handshake authentication may use:

```text
Cookie
Authorization header
Query token
Custom header
```

Message-level authentication might use:

```json
{
    "type": "authenticate",
    "token": "..."
}
```

---

# Cookie-Based Authentication

Example:

```http
GET /socket HTTP/1.1
Host: target.example
Upgrade: websocket
Connection: Upgrade
Cookie: session=abc123
```

The server associates the WebSocket connection with the authenticated session.

Test whether the connection still succeeds when:

```text
Cookie removed
Cookie invalid
Cookie expired
User logged out
Session changed
```

Expected behaviour depends on the application.

---

# Authentication After Connection

Some applications establish a connection first:

```text
Connect
  ↓
Unauthenticated WebSocket
  ↓
Authentication Message
  ↓
Authenticated WebSocket
```

Example:

```json
{
    "action": "authenticate",
    "token": "TOKEN"
}
```

Ask:

```text
What can be done before authentication?

Can authentication be skipped?

Can protected messages be sent first?

Does the server enforce authentication for every sensitive action?
```

---

# Session Invalidation

A useful test is:

```text
Login
  ↓
Establish WebSocket
  ↓
Logout
  ↓
Existing WebSocket Connection
  ↓
Still Authorised?
```

The expected behaviour depends on the application's security requirements.

For sensitive applications, logout may need to invalidate existing WebSocket access.

---

# Authorisation

Authentication answers:

```text
Who are you?
```

Authorisation answers:

```text
What are you allowed to do?
```

A WebSocket connection being authenticated does not mean every message should automatically be trusted.

---

# Object-Level Authorisation

Suppose:

```json
{
    "action": "readConversation",
    "conversationId": 100
}
```

The security question is:

```text
Does the authenticated user belong to conversation 100?
```

Test using two controlled accounts.

For example:

```text
Account A
    ↓
Conversation A

Account B
    ↓
Conversation B
```

Then:

```text
Account A
    ↓
Request Conversation B
```

Expected:

```text
Denied
```

---

# Object Identifiers

WebSocket messages may contain identifiers such as:

```text
userId
roomId
conversationId
messageId
documentId
accountId
channelId
organisationId
```

Example:

```json
{
    "action": "deleteMessage",
    "messageId": 9876
}
```

Ask:

```text
Who owns message 9876?

Can this user delete it?
```

This is essentially BOLA or IDOR occurring through WebSockets.

---

# Function-Level Authorisation

Consider:

```json
{
    "action": "banUser",
    "userId": 123
}
```

The server should verify:

```text
Authenticated?
        ↓
Moderator/Admin?
        ↓
Allowed to manage this user?
        ↓
Action permitted?
```

Do not rely on:

```text
The normal UI does not show the Ban button.
```

The server must enforce the permission.

---

# Role Testing

Use controlled accounts where possible:

```text
User
Moderator
Administrator
```

Capture a privileged message.

Example:

```json
{
    "action": "deleteRoom",
    "roomId": 100
}
```

Then determine whether a lower-privileged account can send the same message.

Expected:

```text
Server-side denial
```

---

# Message Modification

Burp allows WebSocket messages to be intercepted and modified.

Normal message:

```json
{
    "action": "sendMessage",
    "roomId": 10,
    "text": "Hello"
}
```

Potential testing areas include:

```text
roomId
text
action
userId
messageId
role
status
```

Modify one meaningful value at a time.

This makes the resulting behaviour easier to understand.

---

# Message Replay

WebSocket messages may sometimes represent one-time actions.

For example:

```json
{
    "action": "claimReward",
    "rewardId": 123
}
```

Capture the message and replay it.

Ask:

```text
Is the action processed twice?

Does state prevent replay?

Is an idempotency mechanism used?
```

Potentially sensitive replay targets include:

```text
Payments
Rewards
Invitations
Approvals
Reservations
Credits
State changes
```

Avoid repeating destructive or financially meaningful actions against production systems without explicit approval.

---

# Business Logic

WebSocket applications frequently contain important business logic.

Examples:

```text
Trading
Auctions
Reservations
Games
Collaboration
Messaging
Support
Real-time approvals
```

The same business logic methodology applies.

Start with:

```text
What business function does this message represent?
```

Then:

```text
What rule should apply?
```

Then:

```text
Can the rule be violated?
```

---

# Example: Auction

Suppose:

```json
{
    "action": "bid",
    "auctionId": 500,
    "amount": 100
}
```

Business rules may include:

```text
Bid must exceed current bid
Auction must still be active
User must be eligible
Bid must use supported increments
User cannot bid after auction closes
```

Convert these rules into tests.

```text
Can bid amount be zero?

Can it be negative?

Can it be below current bid?

Can a bid be submitted after closing?

Can multiple simultaneous bids violate state?

Can the auction identifier be changed?
```

---

# Example: Chat

Suppose:

```json
{
    "action": "message",
    "roomId": 123,
    "text": "Hello"
}
```

Threat model:

```text
Message content
Room membership
Message ownership
Message editing
Message deletion
User identity
Moderation
```

Questions:

```text
Can users send messages to rooms they have not joined?

Can another user's messages be edited?

Can another user's messages be deleted?

Can the sender identity be supplied by the client?

Can moderation actions be invoked directly?
```

---

# Example: Trading Platform

Suppose:

```json
{
    "action": "order",
    "asset": "EXAMPLE",
    "quantity": 10,
    "price": 50
}
```

Business logic questions include:

```text
Who calculates price?

Are quantities validated?

Can negative quantities be submitted?

Can stale prices be used?

Can an order be submitted after the market state changes?

Can the same order be replayed?

Are limits enforced atomically?
```

Testing should use designated test environments for financial functionality.

---

# State Machines

Real-time applications frequently maintain state.

Example:

```text
Disconnected
    ↓
Connected
    ↓
Authenticated
    ↓
Joined Room
    ↓
Messaging
```

Forbidden transitions may include:

```text
Connected
    ↓
Messaging
```

without:

```text
Authenticated
```

or:

```text
Authenticated
    ↓
Send Room Message
```

without:

```text
Joined Room
```

---

# State Transition Testing

Map:

```text
Current State
      ↓
Allowed Messages
```

Example:

| State | Message | Expected |
|---|---|---|
| Connected | Authenticate | Allowed |
| Connected | Send Message | Denied |
| Authenticated | Join Room | Allowed |
| Authenticated | Admin Action | Denied |
| Joined | Send Message | Allowed |
| Logged Out | Send Message | Denied |

Then test forbidden transitions.

---

# Sequence Testing

If the expected sequence is:

```text
CONNECT
   ↓
AUTH
   ↓
JOIN
   ↓
MESSAGE
```

test:

```text
CONNECT → MESSAGE

CONNECT → JOIN

CONNECT → JOIN → MESSAGE

CONNECT → AUTH → MESSAGE

CONNECT → AUTH → JOIN → JOIN

CONNECT → AUTH → JOIN → LEAVE → MESSAGE
```

The server should validate state rather than trusting the client workflow.

---

# Input Validation

WebSocket messages may contain the same kinds of user input as HTTP requests.

Example:

```json
{
    "message": "Hello"
}
```

The input may later reach:

```text
HTML
SQL
Command
Template
Log
File
Another API
```

Therefore WebSocket messages can potentially expose familiar vulnerability classes.

---

# WebSocket XSS

Consider a chat application.

Input:

```json
{
    "message": "USER_CONTROLLED_INPUT"
}
```

Server:

```text
Receive Message
      ↓
Store Message
      ↓
Send to Other Users
      ↓
Browser Renders Message
```

If output encoding is missing, stored XSS may occur.

Testing should follow the dedicated XSS methodology.

Refer to:

[Cross-Site Scripting](xss.md)

---

# WebSocket SQL Injection

A WebSocket message may eventually reach a database.

Example:

```json
{
    "action": "search",
    "query": "example"
}
```

Conceptually:

```text
WebSocket Message
       ↓
Application
       ↓
Database Query
```

If input is used unsafely, SQL injection may still be possible.

The transport protocol does not change the underlying injection principle.

Refer to:

[SQL Injection](sql-injection.md)

---

# WebSocket Command Injection

A WebSocket message may trigger server-side operating system functionality.

Example:

```json
{
    "action": "diagnostic",
    "host": "example"
}
```

Conceptually:

```text
WebSocket
   ↓
Application
   ↓
OS Command
```

If the input reaches a command interpreter unsafely, command injection may exist.

Refer to:

[OS Command Injection](command-injection.md)

---

# WebSocket SSRF

A WebSocket message may contain a URL:

```json
{
    "action": "preview",
    "url": "https://example.com"
}
```

If the server retrieves the URL:

```text
WebSocket Message
       ↓
Application
       ↓
HTTP Client
       ↓
Remote Resource
```

this should trigger SSRF testing.

Refer to:

[Server Side Request Forgery](ssrf.md)

---

# Cross-Site WebSocket Hijacking

Cross-Site WebSocket Hijacking, commonly abbreviated as:

```text
CSWSH
```

occurs when a WebSocket handshake relies on automatically supplied credentials such as cookies but does not sufficiently validate where the connection originated.

Conceptually:

```text
Victim Logged Into target.example
           ↓
Victim Visits attacker.example
           ↓
Attacker Page Opens WebSocket
           ↓
Browser Includes target.example Cookies
           ↓
Target Accepts Connection
```

If the server does not verify the origin appropriately, the attacker's page may interact with the victim's authenticated WebSocket session.

---

# CSWSH Requirements

A typical CSWSH scenario may involve:

```text
Cookie-based authentication
+
Browser automatically includes cookie
+
Weak or missing Origin validation
+
WebSocket performs sensitive actions
```

Conceptually:

```text
Authentication Cookie
       +
Missing Origin Validation
       ↓
Cross-Origin WebSocket Connection
```

---

# Origin Header

The WebSocket handshake may contain:

```http
Origin: https://target.example
```

The server can use this to verify that the connection originated from an expected web origin.

Testing questions:

```text
Is Origin required?

Is Origin validated?

Is validation exact?

Are arbitrary origins accepted?

Is a missing Origin accepted?

Are subdomains trusted unnecessarily?
```

---

# Testing Origin Validation

Start with the legitimate handshake:

```http
Origin: https://target.example
```

Establish baseline behaviour.

Then, where appropriate, test controlled changes such as:

```http
Origin: https://example.com
```

Expected:

```text
Connection rejected
```

if the WebSocket is intended only for the application's own origin.

Do not assume every cross-origin WebSocket is vulnerable.

Some APIs intentionally allow connections from multiple origins.

---

# Missing Origin

Test whether removing:

```http
Origin:
```

changes behaviour.

The security significance depends on:

```text
Authentication mechanism
Application design
Browser behaviour
Expected clients
```

A non-browser WebSocket API may legitimately allow connections without an Origin header.

---

# Weak Origin Validation

Avoid simplistic validation such as:

```text
Origin contains "target.example"
```

because a malicious origin could potentially resemble the trusted value.

Validation should compare against explicitly trusted origins.

Conceptually:

```text
Origin
  ↓
Exact Allowlist
  ↓
Allow / Deny
```

---

# CSWSH Threat Model

Ask:

```text
Does WebSocket authentication rely on cookies?

Does the browser automatically send them?

Does the server validate Origin?

Can another website create the connection?

Can messages be sent?

Can messages be read?

What actions can be performed?
```

The impact depends on the functionality available through the socket.

---

# Burp Testing for CSWSH

Workflow:

```text
Capture WebSocket Handshake
        ↓
Send Handshake to Repeater
        ↓
Establish Baseline
        ↓
Modify Origin
        ↓
Reconnect
        ↓
Observe Result
```

Compare:

```text
Valid Origin
Invalid Origin
Missing Origin
```

Record whether:

```text
Connection established
Authentication preserved
Messages accepted
Responses returned
```

---

# WebSocket Handshake Manipulation

The initial handshake should also be tested for:

```text
Authentication removal
Origin changes
Query parameter manipulation
Host handling
Token modification
Protocol selection
```

Example:

```text
wss://target.example/socket?token=...
```

Ask:

```text
Does the token expire?

Is it reusable?

Is it exposed in logs?

Is it bound to a user?

Is it transmitted only over TLS?
```

---

# Sensitive Tokens in URLs

Avoid placing long-lived secrets in WebSocket URLs when possible.

Example:

```text
wss://target.example/socket?access_token=SECRET
```

URLs may appear in:

```text
Logs
Monitoring
Proxy logs
Application telemetry
Debug output
```

Short-lived connection tokens can reduce exposure where query-based authentication is necessary.

---

# Message-Level Trust

A common mistake is trusting identity fields supplied by the client.

For example:

```json
{
    "action": "message",
    "userId": 123,
    "message": "Hello"
}
```

The server should normally determine the user from the authenticated connection.

Preferred:

```text
Authenticated WebSocket
       ↓
Server Knows User = 123
       ↓
Client Sends Message
       ↓
Server Associates User 123
```

Rather than:

```text
Client Says:
userId = 123
```

---

# Identity Manipulation

If messages contain:

```text
userId
username
accountId
role
organisationId
```

ask why the client needs to supply those values.

Example:

```json
{
    "action": "message",
    "userId": 500,
    "text": "Hello"
}
```

Try changing the identifier between two controlled accounts.

The server should not trust identity claims that can already be derived from the authenticated session.

---

# Property-Level Authorisation

Consider:

```json
{
    "action": "updateProfile",
    "displayName": "Alice"
}
```

Potential internal properties may include:

```text
displayName
role
status
verified
subscription
```

As with REST APIs, test whether security-sensitive properties can be added to WebSocket messages.

Expected:

```text
Allowlisted writable properties only
```

---

# Message Type Manipulation

Suppose normal users send:

```json
{
    "type": "message"
}
```

while administrators send:

```json
{
    "type": "adminMessage"
}
```

The server must enforce authorisation based on the authenticated user.

It should not assume:

```text
Only the administrator UI knows the admin message type.
```

Anything sent by the client should be considered attacker controllable.

---

# WebSocket Race Conditions

Persistent connections make concurrency particularly relevant.

Suppose:

```json
{
    "action": "reserve",
    "itemId": 100
}
```

Two messages may be sent nearly simultaneously:

```text
Message A ─┐
           ├── Reserve Item 100
Message B ─┘
```

Expected:

```text
One succeeds
One fails
```

Potential vulnerability:

```text
Both succeed
```

Race conditions are particularly interesting for:

```text
Reservations
Inventory
Credits
Rewards
Financial operations
Auctions
Voting
Limited-use actions
```

---

# Rate Limiting

Persistent WebSocket connections may bypass HTTP-focused rate limiting.

For example:

```text
HTTP API
  ↓
Rate Limited
```

while:

```text
WebSocket
  ↓
Unlimited Messages
```

Assess whether sensitive WebSocket operations have appropriate controls.

---

# Rate-Limit Candidates

Examples include:

```text
Chat messages
Search
Notifications
Invitations
OTP requests
Expensive calculations
API proxying
File processing
AI operations
Trading actions
```

Testing should remain controlled.

Do not intentionally degrade the service.

---

# Message Size

Applications should impose sensible message size limits.

Consider:

```text
Small Message
Medium Message
Maximum Expected Message
Slightly Above Maximum
```

Avoid sending extremely large messages to production systems simply to demonstrate that a limit is absent.

The objective is to verify validation safely.

---

# Binary WebSocket Messages

WebSockets may transmit:

```text
Text frames
Binary frames
```

Binary messages may contain:

```text
Protocol buffers
Images
Files
Compressed data
Custom protocols
```

Do not assume binary traffic is opaque.

Identify the protocol where possible.

---

# Compression

WebSocket connections may negotiate extensions such as:

```text
permessage-deflate
```

Compression changes how messages are transported but does not remove the need for:

```text
Authentication
Authorisation
Input validation
Resource limits
```

---

# WebSocket Subprotocols

The handshake may contain:

```http
Sec-WebSocket-Protocol: chat
```

or:

```http
Sec-WebSocket-Protocol: graphql-ws
```

Applications may support multiple subprotocols.

Ask:

```text
Which protocols are supported?

Does authentication differ?

Can unexpected protocols be selected?

Are old protocols still enabled?
```

---

# GraphQL Over WebSockets

GraphQL applications may use WebSockets for:

```text
Subscriptions
Real-time events
Notifications
```

Common protocol concepts include:

```text
Connection initialization
Subscription start
Data
Error
Complete
```

The same GraphQL security principles still apply.

Test:

```text
Authentication
Subscription authorisation
Object access
Field access
Resource consumption
```

---

# GraphQL Subscription Authorisation

Consider:

```graphql
subscription {
  orderUpdated(orderId: "1001") {
    id
    status
  }
}
```

The server should verify:

```text
Is this user authorised to observe order 1001?
```

not merely:

```text
Is the WebSocket authenticated?
```

Subscriptions can otherwise become a real-time information disclosure channel.

---

# Reauthentication

Long-lived connections create another question:

```text
What happens when permissions change?
```

Example:

```text
User Connects as Administrator
        ↓
Administrator Role Removed
        ↓
Existing WebSocket Remains Open
```

Ask:

```text
Does the connection retain old privileges?

Are permissions checked per message?

Does the server force reconnection?

Are long-lived authorisation decisions cached?
```

Sensitive actions should generally verify current permissions rather than indefinitely trusting stale connection state.

---

# Token Expiration

Suppose:

```text
JWT expires after 15 minutes
```

but:

```text
WebSocket remains connected for 8 hours
```

Ask:

```text
Does token expiration affect the connection?

Does the application reauthenticate?

Are sensitive actions still accepted?
```

The correct behaviour depends on application requirements, but it should be deliberately designed.

---

# Connection State and Account Changes

Test scenarios such as:

```text
Account disabled
Password changed
Role changed
Session revoked
MFA status changed
User logged out
```

Then determine what happens to existing WebSocket connections.

This is particularly important for administrative and financial applications.

---

# Error Handling

WebSocket errors may reveal:

```text
Stack traces
Internal class names
Database errors
Object identifiers
Server paths
Framework versions
Business state
```

Example:

```json
{
    "error": "NullReferenceException at ChatService.cs:187"
}
```

Production systems should return controlled error messages.

---

# Information Disclosure

Server messages may contain more information than the client actually requires.

Example:

```json
{
    "username": "alice",
    "message": "Hello",
    "internalUserId": 5001,
    "email": "alice@example.com",
    "role": "user",
    "internalNotes": "..."
}
```

Ask:

```text
Which fields are required by the client?
```

This is equivalent to excessive data exposure in APIs.

---

# WebSocket Logging

WebSocket events should be logged appropriately.

Useful security events include:

```text
Connection
Authentication
Authentication failure
Authorisation failure
Sensitive action
Administrative action
Connection termination
Protocol errors
```

Avoid logging unnecessary secrets.

---

# Burp Workflow

A practical WebSocket assessment can follow:

```text
Use Application Normally
        ↓
Identify WebSocket Connection
        ↓
Inspect Handshake
        ↓
Inspect WebSocket History
        ↓
Map Message Types
        ↓
Identify Actors
        ↓
Identify Objects
        ↓
Identify Actions
        ↓
Identify Business Rules
        ↓
Send Messages to Repeater
        ↓
Modify One Value
        ↓
Observe Behaviour
```

---

# Burp Repeater and WebSockets

Burp Repeater can be used to work with WebSocket connections and messages.

Useful tests include:

```text
Handshake modification
Origin modification
Authentication testing
Message modification
Message replay
Object ID changes
Role comparison
State testing
```

Start with a normal message and establish a baseline.

---

# Example Burp Workflow

Suppose the application sends:

```json
{
    "action": "getMessages",
    "roomId": 100
}
```

Workflow:

```text
1. Capture the WebSocket connection.

2. Confirm the endpoint is in scope.

3. Identify the authenticated account.

4. Establish the normal response for room 100.

5. Create room 200 using another controlled account.

6. Modify roomId from 100 to 200.

7. Send the message.

8. Observe whether the server checks room membership.

9. Record the response.

10. Stop once authorisation behaviour is established.
```

This provides a controlled object-level authorisation test.

---

# Two-Account Testing

Two controlled accounts are extremely useful.

Create:

```text
Account A
Account B
```

Then create objects:

```text
Room A
Message A
Document A
```

and:

```text
Room B
Message B
Document B
```

Now test:

```text
Account A → Object B
Account B → Object A
```

This is safer and produces clearer evidence than enumerating unrelated user data.

---

# WebSocket Testing Matrix

| Test | Question |
|---|---|
| Authentication | Can connection be established without credentials? |
| Session | Does logout invalidate the connection? |
| Origin | Are unexpected origins rejected? |
| Object access | Can User A access User B's object? |
| Function access | Can normal users invoke privileged messages? |
| Properties | Can protected properties be supplied? |
| Replay | Can one-time messages be repeated? |
| State | Can workflow steps be skipped? |
| Input | Is message content safely processed? |
| Rate | Are sensitive actions appropriately limited? |

---

# WebSocket Checklist

## Discovery

```text
[ ] Inspect browser Network → WS
[ ] Inspect Burp WebSocket history
[ ] Search JavaScript for WebSocket
[ ] Search for ws://
[ ] Search for wss://
[ ] Identify endpoints
[ ] Identify subprotocols
```

## Handshake

```text
[ ] Review authentication
[ ] Review cookies
[ ] Review Authorization
[ ] Review query tokens
[ ] Review Origin
[ ] Review subprotocol
[ ] Test missing credentials
[ ] Test invalid credentials
```

## Authentication

```text
[ ] Test unauthenticated connection
[ ] Test pre-authentication messages
[ ] Test logout
[ ] Test token expiration
[ ] Test session revocation
[ ] Test account disablement where safe
```

## Authorisation

```text
[ ] Identify object IDs
[ ] Use two controlled accounts
[ ] Test object access
[ ] Test object modification
[ ] Test privileged functions
[ ] Test role boundaries
[ ] Test property-level authorisation
```

## Business Logic

```text
[ ] Identify message workflows
[ ] Map states
[ ] Test forbidden transitions
[ ] Test replay
[ ] Test repeated actions
[ ] Test sequence changes
[ ] Consider race conditions
```

## Input Validation

```text
[ ] Identify user-controlled fields
[ ] Determine processing context
[ ] Test relevant injection classes
[ ] Review message size limits
[ ] Review binary messages
```

## Cross-Origin

```text
[ ] Review Origin validation
[ ] Test controlled alternate origin
[ ] Test missing Origin where appropriate
[ ] Determine cookie behaviour
[ ] Assess CSWSH conditions
```

## Information Exposure

```text
[ ] Review server messages
[ ] Identify unnecessary properties
[ ] Review error messages
[ ] Review internal identifiers
[ ] Review sensitive metadata
```

---

# Evidence Collection

For each finding record:

```text
WebSocket endpoint
Handshake request
Authentication method
Origin
Account / role
Message direction
Original message
Modified message
Original response
Modified response
Object ownership
Expected behaviour
Observed behaviour
Business impact
```

---

# Example Authorisation Evidence

```text
Finding:
WebSocket Object-Level Authorisation Bypass

Endpoint:
wss://target.example/chat

Account A:
User A

Account B:
User B

Message:

{
    "action": "getMessages",
    "roomId": 200
}

Room 200 Owner:
User B

Expected:
Access denied

Observed:
Server returned the message history for room 200.

Impact:
Authenticated users can access conversations belonging to other users.
```

---

# Example CSWSH Evidence

```text
Finding:
Cross-Site WebSocket Hijacking

Authentication:
Session cookie

Expected Origin:
https://target.example

Test Origin:
https://example.com

Observed:
WebSocket handshake accepted.

Authentication:
Victim session cookie automatically included.

Result:
Authenticated WebSocket functionality accessible from another origin.
```

The actual report should describe only functionality demonstrated during controlled testing.

---

# Reporting

Avoid vague titles such as:

```text
WebSocket Vulnerability
```

Prefer:

```text
WebSocket Messages Lack Object-Level Authorisation

Standard Users Can Invoke Administrative WebSocket Actions

WebSocket Connection Remains Authorised After Logout

WebSocket Handshake Does Not Validate Origin

Cross-Site WebSocket Hijacking Allows Authenticated Actions

WebSocket Message Allows Modification of Restricted Properties
```

---

# Impact

Possible impacts include:

```text
Unauthorised data access
Unauthorised modification
Account compromise
Cross-user message access
Administrative action bypass
Business logic abuse
Sensitive information disclosure
Cross-Site WebSocket Hijacking
```

Describe the demonstrated impact rather than listing every theoretical consequence.

---

# Remediation

WebSocket security controls should be enforced server-side.

A persistent connection must not become:

```text
Authenticated once
      ↓
Trust everything forever
```

Instead:

```text
Connection
    ↓
Authenticate
    ↓
Message
    ↓
Validate
    ↓
Authorise
    ↓
Process
```

---

# Validate Origin

For browser-based cookie-authenticated WebSockets:

```text
Origin
  ↓
Explicit Trusted Origin Allowlist
  ↓
Accept / Reject
```

Do not rely on substring matching.

---

# Authenticate Connections

Require appropriate authentication before exposing sensitive WebSocket functionality.

Authentication may occur:

```text
During handshake
```

or:

```text
Immediately after connection
```

but sensitive messages should not be processed before authentication is complete.

---

# Authorise Every Sensitive Action

For every message:

```text
Authenticated User
       ↓
Requested Action
       ↓
Requested Object
       ↓
Current Permissions
       ↓
Business State
       ↓
Allow / Deny
```

Do not trust the fact that the UI only exposes certain actions.

---

# Derive Identity Server-Side

Prefer:

```text
Connection
   ↓
Authenticated User
   ↓
Server Derives Identity
```

instead of:

```text
Client
   ↓
userId = 123
```

when the identity is already known from the authenticated connection.

---

# Validate Message Schemas

Messages should be validated against expected structures.

Example:

```text
Message
   ↓
Known Message Type?
   ↓
Expected Properties?
   ↓
Correct Types?
   ↓
Valid Values?
   ↓
Authorised?
   ↓
Process
```

Reject unexpected properties where appropriate.

---

# Enforce Message Size Limits

Configure appropriate limits for:

```text
Frame size
Message size
Connection lifetime
Message frequency
Resource-intensive actions
```

The values should reflect legitimate application requirements.

---

# Handle Session Changes

Consider how active connections should behave when:

```text
User logs out
Password changes
Account disabled
Role removed
Token expires
Session revoked
```

Sensitive applications should have a deliberate policy for invalidating or reauthorising persistent connections.

---

# Use TLS

Sensitive WebSocket communication should use:

```text
wss://
```

rather than:

```text
ws://
```

to protect traffic in transit.

---

# WebSocket Quick Reference

```text
DISCOVERY

ws://
wss://
WebSocket(
Browser DevTools → Network → WS
Burp WebSockets history
JavaScript
```

```text
HANDSHAKE

Upgrade
Connection
Origin
Cookie
Authorization
Sec-WebSocket-Key
Sec-WebSocket-Protocol
```

```text
AUTHENTICATION

Can I connect without credentials?
Can I send messages before authentication?
What happens after logout?
What happens after token expiration?
```

```text
AUTHORISATION

Can User A access User B's object?
Can normal users invoke admin messages?
Can object IDs be changed?
Can protected properties be modified?
```

```text
BUSINESS LOGIC

Can messages be replayed?
Can steps be skipped?
Can state be manipulated?
Can limits be bypassed?
Can concurrent messages violate rules?
```

```text
CROSS-ORIGIN

Is Origin validated?
Are cookies automatically included?
Can another origin establish the connection?
Can authenticated messages be sent or read?
```

---

# Five Questions for Every WebSocket Message

For every interesting message ask:

```text
1. Who is sending this?

2. What action does this message perform?

3. What object does it affect?

4. Is this user authorised to perform this action on this object?

5. Which properties can the client control?
```

Then:

```text
6. Can the message be replayed?

7. Does the message depend on application state?

8. Can the expected sequence be bypassed?

9. What server-side system processes the data?

10. What happens if the connection's authentication state changes?
```

---

# WebSocket Threat Model Template

```text
FEATURE:
Chat

ENDPOINT:
wss://target.example/chat

ACTORS:
User
Moderator
Administrator

OBJECTS:
Room
Message
User

ACTIONS:
Join
Send
Edit
Delete
Ban

AUTHENTICATION:
Session cookie

AUTHORISATION:
Users may access joined rooms only
Users may edit their own messages
Moderators may delete messages
Administrators may ban users

BUSINESS RULES:
User must join room before messaging
Deleted messages cannot be edited

TRUST BOUNDARIES:
Browser → WebSocket Server
WebSocket Server → Database

ABUSE CASES:
Read another room
Edit another user's message
Delete another user's message
Invoke moderator action
Send message without joining
Replay sensitive action

TESTS:
Modify roomId
Modify messageId
Replay messages
Change action type
Test state sequence
Test Origin
```

---

# Tools

Useful tools include:

```text
Burp Suite
Burp Proxy
Burp Repeater
Burp WebSockets history
Browser Developer Tools
wscat
websocat
JavaScript analysis tools
```

Manual analysis is particularly important because WebSocket protocols are often application-specific.

---

# wscat

`wscat` is a command-line WebSocket client.

Example connection:

```bash
wscat -c wss://target.example/socket
```

It can be useful for:

```text
Manual connections
Sending messages
Protocol analysis
Testing non-browser behaviour
```

Authentication requirements may require additional configuration.

---

# websocat

`websocat` is another command-line WebSocket client.

Example:

```bash
websocat wss://target.example/socket
```

It can be useful when investigating WebSocket protocols outside the browser.

---

# References

## PortSwigger Web Security Academy

WebSockets:

https://portswigger.net/web-security/websockets

PortSwigger provides practical material covering:

```text
WebSocket interception
Message manipulation
Handshake manipulation
Cross-Site WebSocket Hijacking
```

---

## PortSwigger Cross-Site WebSocket Hijacking

https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking

Useful for understanding the relationship between:

```text
Cookie authentication
Origin validation
Cross-origin connections
```

---

## OWASP WebSocket Security Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html

Useful defensive guidance covering:

```text
Origin validation
Authentication
Authorization
Input validation
Session management
Resource limits
Logging
```

---

## MDN WebSocket API

https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

Useful for understanding how browsers interact with WebSocket endpoints.

---

# Final WebSocket Testing Workflow

```text
                    APPLICATION
                         ↓
                  Discover WebSocket
                         ↓
              Browser DevTools / Burp
                         ↓
                 Inspect Handshake
                         ↓
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
    Authentication     Origin       Subprotocol
          ↓              ↓              ↓
          └──────────────┼──────────────┘
                         ↓
                 Connection Established
                         ↓
                   Map Messages
                         ↓
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
       Actors          Objects        Actions
          ↓              ↓              ↓
          └──────────────┼──────────────┘
                         ↓
                  Threat Model
                         ↓
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
 Authentication    Authorisation   Business Logic
          ↓              ↓              ↓
          └──────────────┼──────────────┘
                         ↓
                  Modify Messages
                         ↓
                   Replay Messages
                         ↓
                  Test Object IDs
                         ↓
                  Test Role Boundaries
                         ↓
                  Test State Machine
                         ↓
                    Test Origin
                         ↓
                      CSWSH?
                         ↓
                 Review Input Sinks
                         ↓
              XSS / SQLi / SSRF / etc.
                         ↓
                 Review Rate Limits
                         ↓
               Review Session Changes
                         ↓
                 Collect Evidence
                         ↓
                      Report
```

The key principle is:

> Do not treat a WebSocket as a trusted connection simply because the initial handshake succeeded. Treat every message as an application request. Authenticate the connection, authorise every sensitive action against the requested object, validate message content, enforce business state, and consider whether another website could establish an authenticated connection through the victim's browser.
