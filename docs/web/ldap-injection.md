# LDAP Injection

LDAP injection occurs when attacker-controlled input is incorporated into an LDAP query without correct context-specific escaping or validation.

LDAP stands for:

```text
Lightweight Directory Access Protocol
```

LDAP is commonly used to access directory services containing information such as:

```text
Users
Groups
Email addresses
Departments
Roles
Devices
Service accounts
Organisational units
Authentication information
```

A typical architecture may look like:

```text
User
  ↓
Web Application
  ↓
LDAP Query
  ↓
Directory Service
  ↓
Active Directory / LDAP Directory
```

If user-controlled input reaches the LDAP query interpreter:

```text
User Input
    ↓
LDAP Query Construction
    ↓
LDAP Interpreter
```

the attacker may be able to modify the intended query.

Possible consequences include:

```text
Authentication bypass
User enumeration
Directory information disclosure
Group enumeration
Attribute disclosure
Access-control bypass
Query manipulation
Blind information extraction
Directory modification
```

The exact impact depends heavily on:

```text
LDAP query context
Directory permissions
Application logic
LDAP bind account privileges
Whether queries are read-only
Whether modification operations are exposed
```

!!! warning "Authorised Security Testing"
    Perform LDAP injection testing only against systems explicitly authorised for assessment. Directory services frequently contain sensitive identity information and may support authentication for many applications. Prefer controlled accounts, low-impact boolean tests, and minimal query manipulation. Avoid high-volume enumeration, directory modification, account lockouts, or authentication disruption unless specifically authorised.

---

# LDAP Injection Concept

Consider an application that searches for a user.

Conceptually:

```text
User Input
   ↓
username=alice
   ↓
LDAP Filter
   ↓
(uid=alice)
   ↓
LDAP Search
```

If the application constructs the filter using string concatenation:

```text
"(uid=" + username + ")"
```

then special LDAP filter characters may alter the query structure.

Conceptually:

```text
Expected

(uid=alice)
```

becomes:

```text
User-Controlled LDAP Expression
```

if the input is not safely escaped.

This is analogous to:

```text
SQL Injection
```

but the interpreter is:

```text
LDAP
```

rather than:

```text
SQL
```

---

# LDAP Directory Structure

LDAP directories are hierarchical.

Example:

```text
dc=example,dc=com
│
├── ou=People
│   ├── uid=alice
│   ├── uid=bob
│   └── uid=charlie
│
├── ou=Groups
│   ├── cn=admins
│   ├── cn=developers
│   └── cn=finance
│
└── ou=Services
    ├── cn=mail
    └── cn=vpn
```

Objects contain attributes.

Example user:

```text
dn: uid=alice,ou=People,dc=example,dc=com

uid: alice
cn: Alice Example
mail: alice@example.com
department: Security
memberOf: cn=developers,ou=Groups,dc=example,dc=com
```

---

# Distinguished Names

LDAP objects are identified using Distinguished Names.

Example:

```text
uid=alice,ou=People,dc=example,dc=com
```

Another example:

```text
cn=Alice Example,ou=Security,dc=example,dc=com
```

A DN represents the object's location in the directory hierarchy.

---

# LDAP Search Filters

LDAP searches commonly use filters.

Example:

```text
(uid=alice)
```

Multiple conditions can be combined.

AND:

```text
(&(uid=alice)(department=Security))
```

OR:

```text
(|(uid=alice)(uid=bob))
```

NOT:

```text
(!(uid=alice))
```

---

# LDAP Filter Operators

Common LDAP filter constructs include:

```text
&
|
!
=
>=
<=
~=
*
```

Examples:

```text
(uid=alice)
```

```text
(uid=*)
```

```text
(&(uid=alice)(department=Security))
```

```text
(|(uid=alice)(uid=bob))
```

---

# Wildcards

The asterisk:

```text
*
```

acts as a wildcard in LDAP search filters.

Example:

```text
(uid=*)
```

means conceptually:

```text
Objects where uid exists
```

Example:

```text
(mail=*@example.com)
```

may match email addresses in a domain depending on the directory and query.

---

# LDAP Filter Special Characters

Important characters in LDAP search filters include:

```text
*
(
)
\
NUL
```

These characters have special meaning and must be escaped correctly when they originate from untrusted input.

---

# LDAP Filter Escaping

LDAP search-filter escaping and Distinguished Name escaping are different operations.

This distinction is extremely important.

```text
LDAP Search Filter
        ↓
RFC 4515-style escaping
```

versus:

```text
LDAP Distinguished Name
        ↓
DN-specific escaping
```

Using the wrong escaping function may still leave an application vulnerable.

---

# Core Testing Model

Think of LDAP injection as:

```text
SOURCE
   ↓
User-Controlled Input
   ↓
PROPAGATION
   ↓
Application Code
   ↓
SINK
   ↓
LDAP Query Construction
   ↓
LDAP Interpreter
```

The testing objective is to determine:

```text
Can attacker-controlled input
change the meaning of the LDAP query?
```

---

# Common LDAP Injection Sources

Potential sources include:

```text
Username
Password
Email
Search field
Employee number
Group name
Department
Role
User ID
Account name
Organisation
Domain
API parameters
JSON properties
HTTP headers
Cookies
GraphQL arguments
```

---

# Common Vulnerable Functionality

LDAP-backed functionality frequently includes:

```text
Login
Employee search
User lookup
Address book
Group search
Role lookup
Password reset
Account recovery
Directory browser
Admin portals
SSO integration
VPN portals
Internal applications
Corporate intranets
```

---

# LDAP Authentication

Applications sometimes authenticate users by searching LDAP first.

Conceptually:

```text
Username + Password
        ↓
LDAP Search
        ↓
Find User DN
        ↓
LDAP Bind
        ↓
Authentication
```

Example search:

```text
(&(uid=alice)(objectClass=person))
```

The returned DN may then be used for authentication.

---

# Dangerous Authentication Pattern

A vulnerable application may build a filter like:

```text
(&(uid=USER_INPUT)(password=PASSWORD_INPUT))
```

Conceptually:

```text
User Input
    ↓
Direct String Concatenation
    ↓
LDAP Authentication Filter
```

If input changes the filter logic:

```text
Authentication Bypass
```

may become possible.

---

# Bind Authentication vs Filter Authentication

These are important to distinguish.

## Filter-Based Authentication

Conceptually:

```text
(&(uid=alice)(password=secret))
```

The application searches for an object matching both values.

This pattern can be especially dangerous if credentials are incorporated directly into an LDAP filter.

---

## LDAP Bind Authentication

Another model:

```text
Search Username
      ↓
Obtain User DN
      ↓
Bind to LDAP Using
User DN + Password
      ↓
Success / Failure
```

This reduces certain forms of filter-based password injection, although the username search itself still requires safe handling.

The exact security depends on implementation.

---

# LDAP Injection Categories

LDAP injection can broadly appear as:

```text
Authentication LDAP Injection

Search Filter Injection

Blind LDAP Injection

Distinguished Name Injection

Attribute Manipulation

Directory Modification Injection
```

---

# Search Filter Injection

Suppose the application performs:

```text
Search Employee
```

with:

```text
username=alice
```

and constructs:

```text
(uid=alice)
```

If LDAP metacharacters alter the query:

```text
Search Filter Injection
```

may exist.

---

# Authentication LDAP Injection

The most security-sensitive scenario is often:

```text
Login
```

because query manipulation may affect authentication logic.

Conceptually:

```text
Username
Password
   ↓
LDAP Filter
   ↓
True / False
   ↓
Authenticated?
```

If an attacker can alter:

```text
LDAP Filter
```

they may influence:

```text
True / False
```

and potentially bypass authentication.

---

# Blind LDAP Injection

Sometimes the application does not return directory data.

Instead:

```text
Input A
   ↓
LDAP Query
   ↓
True Condition
   ↓
Response A
```

and:

```text
Input B
   ↓
LDAP Query
   ↓
False Condition
   ↓
Response B
```

The tester may infer information from:

```text
Response content
Response length
Status code
Redirect
Timing
Application behaviour
```

This is:

```text
Blind LDAP Injection
```

---

# LDAP Injection Testing Methodology

Use:

```text
Identify LDAP-Backed Functionality
        ↓
Establish Baseline
        ↓
Identify Input Parameters
        ↓
Test LDAP Metacharacters
        ↓
Observe Errors / Behaviour
        ↓
Test Boolean Conditions
        ↓
Test Wildcard Behaviour
        ↓
Determine Filter Context
        ↓
Test Authentication Logic
        ↓
Test Blind Behaviour
        ↓
Assess Directory Exposure
        ↓
Assess Privilege of LDAP Account
        ↓
Verify Minimal Impact
        ↓
Report
```

---

# Step 1: Identify LDAP-Backed Functionality

Indicators include:

```text
Corporate login
Active Directory authentication
Employee directory
Username lookup
Group membership
LDAP error messages
Distinguished Names
OU names
AD attributes
```

Technology clues may include:

```text
LDAP
Active Directory
OpenLDAP
JNDI
System.DirectoryServices
DirectorySearcher
LdapConnection
Spring LDAP
python-ldap
ldap3
```

---

# Error Messages

LDAP-related errors may expose implementation details.

Examples include references to:

```text
LDAP
LDAPException
InvalidSearchFilter
DirectorySearcher
SearchRequest
NamingException
InvalidNameException
javax.naming
System.DirectoryServices
```

Do not rely on errors alone.

Many production applications suppress them.

---

# Establish a Baseline

Send a normal request first.

Example:

```http
POST /search HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=alice
```

Record:

```text
Status code
Response length
Response body
Headers
Redirects
Timing
Number of results
```

---

# Baseline Matrix

Useful baseline inputs:

```text
Known valid value
Known invalid value
Empty value
Random value
```

Example:

| Input | Expected |
|---|---|
| alice | User returned |
| nonexistent-test-user | No result |
| empty | Validation error |
| random123xyz | No result |

---

# LDAP Metacharacter Testing

Start with individual LDAP-relevant characters.

Examples:

```text
*
(
)
\
```

The objective is:

```text
Does application behaviour change
when LDAP syntax characters are introduced?
```

Do not begin with large or destructive payload sets.

---

# Wildcard Test

A simple wildcard is often a useful first test:

```text
*
```

Suppose:

```text
alice
```

returns:

```text
1 result
```

while:

```text
*
```

returns:

```text
Many results
```

This strongly suggests the input may be reaching an LDAP search filter without correct escaping.

---

# Prefix Wildcards

Controlled examples:

```text
a*
```

```text
al*
```

```text
ali*
```

If:

```text
a*
```

matches multiple accounts and:

```text
alice
```

matches one account, wildcard interpretation may be occurring.

---

# Suffix Wildcards

Example:

```text
*ice
```

may match:

```text
alice
```

depending on the filter.

Again, use controlled test accounts where possible.

---

# Presence Filter Behaviour

LDAP supports presence-style filters conceptually similar to:

```text
(attribute=*)
```

If user input is inserted directly into the value portion:

```text
(uid=USER_INPUT)
```

then supplying:

```text
*
```

could transform the effective query into:

```text
(uid=*)
```

This can reveal unescaped wildcard handling.

---

# Parenthesis Testing

Parentheses define LDAP filter structure.

Testing:

```text
(
```

or:

```text
)
```

may cause:

```text
LDAP syntax error
Different response
500 error
Validation error
```

A syntax error can be a useful signal.

It is not by itself proof of exploitable LDAP injection.

---

# Backslash Testing

The backslash is used for escaping in LDAP filter syntax.

Testing:

```text
\
```

may reveal:

```text
Encoding behaviour
Parser errors
Application sanitisation
```

---

# Boolean LDAP Testing

Once LDAP filter injection is strongly suspected, compare controlled true and false conditions.

The objective is:

```text
TRUE condition
        ↓
Response A

FALSE condition
        ↓
Response B
```

A consistent difference can demonstrate query manipulation.

---

# Safe Boolean Testing

Prefer conditions based on:

```text
Your own controlled account
Known non-sensitive attributes
```

rather than extracting unrelated directory information.

For example, if a test account is known to begin with:

```text
test-
```

you can compare behaviour against a prefix you already know.

---

# Authentication Testing

Authentication endpoints require additional care.

Start with:

```text
Controlled account
Controlled password
```

Record:

```text
Correct username + correct password

Correct username + incorrect password

Incorrect username + incorrect password
```

Then introduce minimal LDAP metacharacters.

---

# Authentication Baseline

Example:

| Username | Password | Expected |
|---|---|---|
| controlled-user | correct | Success |
| controlled-user | wrong | Failure |
| nonexistent-user | wrong | Failure |

Then test whether LDAP syntax changes:

```text
Failure
```

into:

```text
Success
```

without a valid password.

That is the important security boundary.

---

# Do Not Confuse Search Expansion with Authentication Bypass

Suppose:

```text
username=*
```

changes the response.

That does not automatically mean:

```text
Authentication Bypass
```

It may only mean:

```text
LDAP wildcard interpreted
```

Authentication impact must be demonstrated separately.

---

# Search Endpoint Testing

Search functionality is often safer for initial validation than authentication.

Example:

```http
GET /employees?name=alice HTTP/1.1
Host: target.example
```

Test:

```text
alice
a*
*
(
\
```

Compare:

```text
Number of results
Response length
Status
Errors
```

---

# JSON APIs

LDAP-backed APIs may receive JSON.

Example:

```http
POST /api/users/search HTTP/1.1
Host: target.example
Content-Type: application/json

{
    "username": "alice"
}
```

Test each relevant property independently.

---

# Nested JSON

Example:

```json
{
    "filter": {
        "username": "alice",
        "department": "Security"
    }
}
```

Both values may reach LDAP filters.

---

# GraphQL

GraphQL resolvers may perform LDAP searches.

Example:

```graphql
query {
    users(name: "alice") {
        username
        email
    }
}
```

The GraphQL layer does not inherently protect the backend LDAP query.

Flow:

```text
GraphQL Argument
      ↓
Resolver
      ↓
LDAP Search
```

Refer to:

```text
docs/web/graphql.md
```

---

# HTTP Headers

LDAP-backed applications may derive identity information from headers such as:

```text
X-User
X-Username
X-Employee-ID
X-Group
```

This is less common but can occur behind:

```text
Reverse proxies
SSO gateways
Internal applications
```

Do not ignore non-body inputs.

---

# Cookies

Directory-related values may also appear in:

```text
Cookies
```

particularly in legacy applications.

---

# Parameter Discovery

Useful names include:

```text
user
username
uid
cn
name
email
mail
group
role
department
employee
employeeId
account
domain
search
filter
query
```

Refer to:

```text
docs/web/reconnaissance/parameter-discovery.md
```

---

# LDAP Attribute Names

Common attributes may include:

```text
uid
cn
sn
givenName
mail
member
memberOf
department
employeeNumber
userPrincipalName
sAMAccountName
objectClass
```

The exact schema depends on:

```text
Active Directory
OpenLDAP
Custom LDAP schema
```

---

# Active Directory LDAP

Microsoft Active Directory exposes LDAP interfaces.

Common attributes include:

```text
sAMAccountName
userPrincipalName
displayName
mail
memberOf
objectSid
objectGUID
distinguishedName
```

A web application connected to Active Directory may therefore introduce LDAP injection even though the application itself is not running on a domain controller.

---

# LDAP vs Active Directory

Do not treat:

```text
LDAP
```

and:

```text
Active Directory
```

as synonyms.

LDAP is a protocol.

Active Directory is Microsoft's directory service and supports LDAP among other protocols.

---

# Distinguished Name Injection

Not all LDAP injection occurs inside search filters.

Input may be used to construct a DN.

Example concept:

```text
"uid=" + username + ",ou=People,dc=example,dc=com"
```

The security rules for:

```text
DN values
```

are different from:

```text
Search filter values
```

This is why context-specific escaping matters.

---

# DN Example

Expected:

```text
uid=alice,ou=People,dc=example,dc=com
```

If attacker input can alter:

```text
uid=...
```

or inject additional DN components, the resulting object reference may change.

---

# Search Filter vs DN

Always determine the context:

```text
Input
 ↓
LDAP Search Filter?
```

or:

```text
Input
 ↓
Distinguished Name?
```

because remediation differs.

---

# Blind LDAP Injection

Blind LDAP injection becomes relevant when:

```text
No directory values are returned
```

but the application behaves differently for:

```text
True
False
```

conditions.

---

# Boolean Oracle

A blind vulnerability needs an observable oracle.

Examples:

```text
Login success / failure
Result / no result
200 / 404
Different response length
Different error
Different redirect
```

---

# Blind Prefix Testing

Conceptually, if an attribute value is already known to the tester's controlled account:

```text
test-user
```

you can test:

```text
Starts with t?
Starts with te?
Starts with tes?
```

The purpose is to confirm:

```text
LDAP query manipulation
```

without extracting another user's data.

---

# Response Length Analysis

Suppose:

```text
True Condition
Length: 4218
```

and:

```text
False Condition
Length: 317
```

Repeated consistent differences can form a useful oracle.

Use:

```text
Burp Comparer
```

to investigate.

---

# Status Code Oracle

Example:

```text
True
→ 200

False
→ 404
```

This can support blind testing.

---

# Redirect Oracle

Example:

```text
True
→ /account

False
→ /login?error=1
```

Again, verify consistency.

---

# Timing

Timing-based LDAP injection is generally less straightforward than classic SQL injection.

Do not assume that:

```text
Slow response
```

means:

```text
LDAP injection
```

Network conditions, directory load, and application logic can all influence timing.

Prefer stronger behavioural evidence.

---

# Error-Based Detection

Potential error indicators:

```text
Bad search filter
Invalid search filter
LDAPException
NamingException
InvalidNameException
Filter error
Protocol error
```

Example:

```text
javax.naming.directory.InvalidSearchFilterException
```

This can strongly suggest LDAP-backed processing.

---

# Error Handling

A secure application should not expose:

```text
Directory hostname
Base DN
Bind username
LDAP URL
Stack traces
Internal query
```

through error messages.

---

# LDAP URLs

Information disclosure may reveal:

```text
ldap://directory.internal:389
```

or:

```text
ldaps://directory.internal:636
```

This may expose internal infrastructure information.

Refer to:

```text
docs/web/information-disclosure.md
```

---

# Authentication Bypass Analysis

Authentication bypass requires demonstrating:

```text
No valid second credential
        ↓
Authentication succeeds
```

A change in error text is insufficient.

Strong evidence includes:

```text
Authenticated session cookie
Authenticated access token
Protected account page
Protected API access
```

---

# Session Verification

If an LDAP manipulation appears to authenticate successfully:

```text
Capture resulting session
        ↓
Request /account
        ↓
Verify server-side identity
```

Do not rely only on:

```text
302 /dashboard
```

---

# Identity Confusion

If a wildcard matches multiple directory entries, determine which identity the application selects.

Potentially:

```text
First LDAP Result
```

could become the authenticated identity in badly designed applications.

Do not test against arbitrary privileged users unless explicitly authorised.

---

# LDAP Query Construction

A vulnerable pattern may look conceptually like:

```java
String filter =
    "(uid=" + username + ")";
```

The problem is:

```text
Untrusted Input
+
LDAP Syntax
```

without context-specific escaping.

---

# Java LDAP

Common Java APIs include:

```text
JNDI
javax.naming.directory
DirContext
SearchControls
Spring LDAP
```

Search source code for:

```text
DirContext
InitialDirContext
search(
SearchControls
LdapTemplate
```

---

# Java Source Review

Useful command:

```bash
grep -RniE \
'DirContext|InitialDirContext|SearchControls|LdapTemplate|javax\.naming|ldap://' \
.
```

Then inspect whether user-controlled values are concatenated into:

```text
LDAP filters
DNs
```

---

# .NET LDAP

Common .NET APIs include:

```text
System.DirectoryServices
DirectorySearcher
DirectoryEntry
System.DirectoryServices.Protocols
LdapConnection
SearchRequest
```

Useful source search:

```bash
grep -RniE \
'DirectorySearcher|DirectoryEntry|LdapConnection|SearchRequest|System\.DirectoryServices' \
.
```

---

# Python LDAP

Common Python libraries include:

```text
ldap3
python-ldap
```

Search:

```bash
grep -RniE \
'import ldap|from ldap|ldap3|python-ldap|search_s|search_ext' \
.
```

---

# PHP LDAP

Common functions include:

```text
ldap_connect
ldap_bind
ldap_search
ldap_list
ldap_read
```

Search:

```bash
grep -RniE \
'ldap_connect|ldap_bind|ldap_search|ldap_list|ldap_read' \
.
```

---

# Node.js LDAP

Potential libraries include:

```text
ldapjs
ldapts
```

Search:

```bash
grep -RniE \
'ldapjs|ldapts|createClient|client\.search|client\.bind' \
.
```

---

# Source-to-Sink Analysis

During code review:

```text
HTTP Parameter
      ↓
Controller
      ↓
Service
      ↓
LDAP Helper
      ↓
Filter Construction
      ↓
LDAP Search
```

Trace whether:

```text
Untrusted value
```

reaches:

```text
Filter
```

without safe encoding.

---

# Dangerous String Concatenation

Look for patterns similar to:

```text
"(uid=" + username + ")"
```

```text
"(&(uid=" + username + ")(department=" + department + "))"
```

```text
"cn=" + group + ",ou=Groups,..."
```

These deserve review.

---

# Validation Is Not the Same as Escaping

Suppose input is checked for:

```text
Length <= 50
```

This does not protect against LDAP syntax characters.

Likewise:

```text
HTML encoding
```

does not protect an LDAP context.

Security must match the interpreter:

```text
LDAP Filter
→ LDAP Filter Escaping

LDAP DN
→ LDAP DN Escaping
```

---

# Context Matters

Do not use:

```text
SQL escaping
HTML escaping
URL encoding
JavaScript encoding
```

as substitutes for:

```text
LDAP escaping
```

Each interpreter has different syntax.

---

# Canonicalisation

Validation should occur against a canonical representation where appropriate.

Potential inconsistencies can arise from:

```text
Encoding
Unicode
Escaping
Normalization
```

Do not invent custom canonicalisation logic unless necessary.

Use established libraries.

---

# LDAP Bind Account Privileges

The impact of LDAP injection depends heavily on the permissions of the account used by the application.

Conceptually:

```text
Web Application
      ↓
LDAP Bind Account
      ↓
Directory Permissions
```

If the bind account can only:

```text
Read a small subset
```

impact is reduced.

If it can:

```text
Read all directory attributes
Modify users
Modify groups
Reset passwords
```

impact may be substantially greater.

---

# Least Privilege

During an assessment, determine where possible whether the application LDAP identity has:

```text
Read-only access
Restricted search base
Attribute restrictions
Write permissions
Administrative permissions
```

Do not attempt directory modifications merely to determine permissions unless explicitly authorised.

---

# Search Base

LDAP searches usually have a base.

Example:

```text
ou=People,dc=example,dc=com
```

A restricted search base can limit exposure.

Conceptually:

```text
Directory
   ↓
Only ou=People searchable
```

is preferable to unnecessary access across:

```text
Entire Directory
```

---

# Returned Attributes

Applications should request only necessary attributes.

Example:

```text
uid
displayName
mail
```

rather than:

```text
All Attributes
```

where possible.

This reduces impact if a query is manipulated.

---

# Sensitive LDAP Attributes

Potentially sensitive directory information includes:

```text
Email addresses
Telephone numbers
Group memberships
Job titles
Department
Employee IDs
Internal usernames
Service accounts
Distinguished names
Directory structure
Authentication metadata
```

Actual sensitivity depends on the environment.

---

# Directory Enumeration

A vulnerable search may allow:

```text
User enumeration
Group enumeration
Attribute enumeration
```

Do not perform large-scale directory extraction during normal testing.

Demonstrate:

```text
Minimal controlled evidence
```

instead.

---

# Safe Proof of Concept

Prefer:

```text
Normal query
→ 1 controlled result

Modified query
→ 2 controlled results
```

over:

```text
Dump entire corporate directory
```

The first is normally sufficient to demonstrate the flaw.

---

# LDAP Injection and User Enumeration

An LDAP injection vulnerability may amplify user enumeration.

Example:

```text
Search prefix
      ↓
Different results
      ↓
Valid usernames inferred
```

This can support:

```text
Credential attacks
Phishing
Password spraying
```

but do not perform those follow-on attacks unless separately authorised.

---

# LDAP Injection and Password Reset

Password reset functionality may use LDAP to locate accounts.

Example:

```text
Email
  ↓
LDAP Search
  ↓
Account
  ↓
Reset Process
```

LDAP injection here could cause:

```text
Account confusion
Enumeration
Wrong-account selection
```

Refer to:

```text
docs/web/password-reset.md
```

---

# LDAP Injection and MFA

Applications may use LDAP attributes to determine:

```text
MFA requirement
Group membership
Authentication policy
```

Manipulating directory lookup logic could potentially influence downstream authentication decisions.

Refer to:

```text
docs/web/mfa.md
```

---

# LDAP Injection and Authorisation

Applications may query LDAP groups:

```text
Is user member of admins?
```

Conceptually:

```text
User
 ↓
LDAP Group Query
 ↓
memberOf
 ↓
Role Decision
```

If the query can be manipulated:

```text
Authorisation Bypass
```

may become possible.

Refer to:

```text
docs/web/authorisation.md
```

---

# Group Membership Queries

Example conceptual filter:

```text
(&(objectClass=group)(member=USER_DN))
```

Any user-controlled component must be safely handled.

---

# LDAP Injection and IDOR / BOLA

These vulnerabilities are different.

```text
LDAP Injection
→ Manipulates directory query syntax
```

```text
IDOR / BOLA
→ Manipulates object identifiers without proper authorisation
```

They can coexist.

Refer to:

```text
docs/web/idor-bola.md
```

---

# LDAP Injection and Business Logic

LDAP data may influence:

```text
Authentication
Role assignment
Organisation membership
Access decisions
Password recovery
Account provisioning
```

A technically small LDAP injection may therefore create significant business-logic impact.

Refer to:

```text
docs/web/business-logic.md
```

---

# LDAP Injection and Information Disclosure

LDAP errors may reveal:

```text
Directory host
Base DN
Schema
Attributes
Bind account
Internal domains
Organisational structure
```

Refer to:

```text
docs/web/information-disclosure.md
```

---

# LDAP Injection vs SQL Injection

Both involve:

```text
Untrusted Input
      ↓
Query Interpreter
```

but their syntax differs.

| SQL Injection | LDAP Injection |
|---|---|
| SQL database | Directory service |
| SQL query | LDAP filter / DN |
| Quotes/operators | LDAP filter metacharacters |
| Tables/rows | Directory objects/attributes |
| SQL escaping | LDAP-specific escaping |

Do not reuse SQL injection payloads blindly against LDAP.

---

# LDAP Injection vs XPath Injection

LDAP and XPath both support structured query expressions.

However:

```text
LDAP Filter Syntax
```

and:

```text
XPath Syntax
```

are completely different.

Fingerprint the backend before selecting test inputs.

---

# Burp Suite Workflow

A practical LDAP injection workflow:

```text
Burp Proxy
    ↓
Identify Search / Login Request
    ↓
Send to Repeater
    ↓
Establish Baseline
    ↓
Test *
    ↓
Test (
    ↓
Test )
    ↓
Test \
    ↓
Compare Behaviour
    ↓
Determine LDAP Context
    ↓
Build Minimal Boolean Test
    ↓
Verify With Controlled Data
    ↓
Intruder for Small Test Matrix
    ↓
Comparer
    ↓
Scanner Where Appropriate
    ↓
Manual Verification
    ↓
Report
```

---

# Burp Proxy

Use Proxy to identify:

```text
Login requests
Directory searches
Employee lookups
Password reset
Group lookup
Role lookup
```

Search HTTP history for parameters such as:

```text
username
uid
user
email
group
department
search
filter
```

---

# Burp Repeater

Repeater is the most important Burp tool for LDAP injection testing.

Create a baseline:

```http
GET /api/users?name=alice HTTP/1.1
Host: target.example
```

Then test one change at a time:

```text
alice
*
a*
(
)
\
```

Record:

```text
Status
Length
Response
Result count
Timing
Errors
```

---

# Why Repeater Is Important

LDAP behaviour can be subtle.

Automated scanners may miss:

```text
Custom filters
Blind differences
Application-specific response behaviour
Authentication logic
```

Manual comparison is often necessary.

---

# Burp Comparer

Comparer is useful when:

```text
True response
```

and:

```text
False response
```

look nearly identical.

Compare:

```text
Response body
Headers
JSON
HTML
```

---

# Burp Intruder

Intruder is useful for controlled testing across a small payload set.

Example:

```http
GET /api/users?name=§alice§ HTTP/1.1
Host: target.example
```

Payloads:

```text
alice
nonexistent-test-value
*
a*
(
)
\
```

Analyse:

```text
Status
Length
Words
Lines
Redirect
```

---

# Intruder Grep Match

Useful response terms:

```text
LDAP
invalid
filter
error
user
results
found
not found
```

---

# Intruder for Multiple Parameters

Suppose:

```http
POST /api/search HTTP/1.1
Content-Type: application/json

{
    "name": "alice",
    "department": "Security"
}
```

Test:

```text
name
```

and:

```text
department
```

independently before combining changes.

---

# Burp Scanner

Burp Scanner may detect some injection-related behaviour.

However:

```text
No scanner finding
```

does not prove:

```text
No LDAP Injection
```

Manual testing remains important.

---

# Burp Logger

Use Logger to review:

```text
Search requests
Authentication requests
Repeated parameter names
Background API calls
```

This is especially useful in SPAs where directory lookups may occur asynchronously.

---

# Burp Decoder

Decoder can help when parameters are:

```text
URL encoded
Base64 encoded
Nested
```

For example:

```text
%2A
```

represents:

```text
*
```

after URL decoding.

Always understand which decoding occurs before LDAP processing.

---

# Double Encoding

Avoid assuming:

```text
%252A
```

will reach LDAP as:

```text
*
```

The result depends on how many decoding layers exist.

Determine:

```text
Browser
Proxy
Web server
Framework
Application
LDAP library
```

processing.

---

# Burp Extensions

There is no requirement to install a dedicated LDAP extension to test LDAP injection effectively.

The most useful Burp capabilities are:

```text
Repeater
Intruder
Comparer
Scanner
Logger
Decoder
```

LDAP injection often requires understanding application-specific query behaviour rather than simply running a generic payload list.

---

# PyBurp

For custom automation inside Burp, PyBurp can be useful for creating Python-based request processing and fuzzing logic.

Potential LDAP uses:

```text
Custom LDAP payload generation
Response classification
Parameter mutation
Automated true/false comparison
Custom scan logic
```

This is useful if you want to turn repeated LDAP testing workflows into Burp-integrated scripts.

Review third-party extensions before installing them.

---

# Custom Burp Extension Idea

A dedicated LDAP helper could eventually perform:

```text
Identify candidate parameters
        ↓
Send Baseline
        ↓
Test LDAP Metacharacters
        ↓
Compare Responses
        ↓
Flag Wildcard Expansion
        ↓
Flag LDAP Errors
        ↓
Generate Minimal Report Evidence
```

This would fit well as a future Montoya API project.

---

# LDAP Payload File

Create:

```text
ldap-basic.txt
```

with a small initial test set:

```text
*
a*
(
)
\
test*
nonexistent-test-value
```

Keep the initial payload set small.

The purpose is:

```text
Detection
```

not:

```text
Directory dumping
```

---

# ffuf Parameter Testing

For an explicitly authorised search endpoint, a small wordlist can be used with ffuf.

Example concept:

```bash
ffuf \
  -w ldap-basic.txt \
  -u 'https://target.example/api/users?name=FUZZ'
```

Analyse:

```text
Status
Size
Words
Lines
```

Burp is usually better for understanding authentication state and application logic.

---

# curl Baseline Testing

A simple controlled comparison:

```bash
curl -i \
  'https://target.example/api/users?name=alice'
```

Then:

```bash
curl -i \
  'https://target.example/api/users?name=%2A'
```

Compare the responses.

---

# Python LDAP Response Comparator

The following helper performs a small controlled set of HTTP requests and compares response characteristics.

It does not attempt directory extraction.

```python
#!/usr/bin/env python3

import argparse
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


DEFAULT_PAYLOADS = [
    "normal-test-value",
    "nonexistent-test-value",
    "*",
    "a*",
    "(",
    ")",
    "\\",
]


def replace_parameter(url, parameter, value):

    parsed = urlparse(url)

    query = parse_qsl(
        parsed.query,
        keep_blank_values=True
    )

    updated = []

    found = False

    for key, current_value in query:

        if key == parameter:

            updated.append(
                (key, value)
            )

            found = True

        else:

            updated.append(
                (key, current_value)
            )

    if not found:

        updated.append(
            (parameter, value)
        )

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(updated),
            parsed.fragment,
        )
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Small LDAP injection response "
            "comparison helper for authorised testing."
        )
    )

    parser.add_argument(
        "--url",
        required=True,
        help=(
            "Target URL, for example "
            "'https://target.example/search?name=alice'"
        ),
    )

    parser.add_argument(
        "--parameter",
        required=True,
        help="Query-string parameter to test.",
    )

    parser.add_argument(
        "--cookie",
        help="Optional Cookie header.",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=10,
    )

    parser.add_argument(
        "--proxy",
        help=(
            "Optional proxy, for example "
            "http://127.0.0.1:8080"
        ),
    )

    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS verification.",
    )

    args = parser.parse_args()

    headers = {
        "User-Agent": (
            "LDAP-Response-Comparator/1.0"
        )
    }

    if args.cookie:

        headers["Cookie"] = args.cookie

    proxies = None

    if args.proxy:

        proxies = {
            "http": args.proxy,
            "https": args.proxy,
        }

    print(
        f"{'PAYLOAD':<30}"
        f"{'STATUS':<10}"
        f"{'LENGTH':<12}"
        f"{'WORDS':<10}"
        f"TIME"
    )

    print(
        "-" * 80
    )

    for payload in DEFAULT_PAYLOADS:

        test_url = replace_parameter(
            args.url,
            args.parameter,
            payload,
        )

        try:

            response = requests.get(
                test_url,
                headers=headers,
                timeout=args.timeout,
                proxies=proxies,
                verify=not args.insecure,
                allow_redirects=False,
            )

            words = len(
                response.text.split()
            )

            elapsed = (
                response.elapsed.total_seconds()
            )

            print(
                f"{payload!r:<30}"
                f"{response.status_code:<10}"
                f"{len(response.content):<12}"
                f"{words:<10}"
                f"{elapsed:.3f}"
            )

        except requests.RequestException as exc:

            print(
                f"{payload!r:<30}"
                f"ERROR: {exc}"
            )


if __name__ == "__main__":
    main()
```

---

# Comparator Usage

Example:

```bash
python3 ldap_response_compare.py \
  --url 'https://target.example/search?name=alice' \
  --parameter name
```

Through Burp:

```bash
python3 ldap_response_compare.py \
  --url 'https://target.example/search?name=alice' \
  --parameter name \
  --proxy http://127.0.0.1:8080 \
  --insecure
```

This allows:

```text
Python Script
     ↓
Burp
     ↓
Target
```

so every request remains visible in Burp.

---

# What to Look For

Example output:

```text
PAYLOAD                       STATUS    LENGTH      WORDS     TIME
----------------------------------------------------------------
'normal-test-value'           200       311         28        0.121
'nonexistent-test-value'      200       311         28        0.118
'*'                           200       4812        402       0.136
'a*'                          200       1221        104       0.127
'('                           500       712         51        0.120
')'                           500       712         51        0.119
'\\'                          500       712         51        0.121
```

This pattern would strongly justify manual investigation because:

```text
*
→ substantially different response

(
→ server error
```

But it is still necessary to verify:

```text
Actual LDAP query manipulation
```

rather than reporting purely from automated output.

---

# POST Request Testing Script

For JSON-based endpoints:

```python
#!/usr/bin/env python3

import argparse
import copy
import requests


PAYLOADS = [
    "normal-test-value",
    "nonexistent-test-value",
    "*",
    "a*",
    "(",
    ")",
    "\\",
]


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        required=True
    )

    parser.add_argument(
        "--field",
        required=True
    )

    parser.add_argument(
        "--proxy"
    )

    parser.add_argument(
        "--insecure",
        action="store_true"
    )

    args = parser.parse_args()

    proxies = None

    if args.proxy:

        proxies = {
            "http": args.proxy,
            "https": args.proxy,
        }

    base = {
        args.field: ""
    }

    print(
        f"{'PAYLOAD':<30}"
        f"{'STATUS':<10}"
        f"{'LENGTH':<12}"
        f"TIME"
    )

    print(
        "-" * 70
    )

    for payload in PAYLOADS:

        body = copy.deepcopy(
            base
        )

        body[args.field] = payload

        try:

            response = requests.post(
                args.url,
                json=body,
                proxies=proxies,
                verify=not args.insecure,
                timeout=10,
                allow_redirects=False,
            )

            elapsed = (
                response.elapsed.total_seconds()
            )

            print(
                f"{payload!r:<30}"
                f"{response.status_code:<10}"
                f"{len(response.content):<12}"
                f"{elapsed:.3f}"
            )

        except requests.RequestException as exc:

            print(
                f"{payload!r:<30}"
                f"ERROR: {exc}"
            )


if __name__ == "__main__":
    main()
```

---

# POST Script Usage

```bash
python3 ldap_json_compare.py \
  --url 'https://target.example/api/users/search' \
  --field username
```

Through Burp:

```bash
python3 ldap_json_compare.py \
  --url 'https://target.example/api/users/search' \
  --field username \
  --proxy http://127.0.0.1:8080 \
  --insecure
```

---

# Why Keep Scripts Small

A useful pentesting helper should initially answer:

```text
Is this parameter interesting?
```

rather than:

```text
Can I dump the entire directory?
```

This keeps testing:

```text
Controlled
Repeatable
Low impact
Easy to verify
```

---

# Automated Scanner Findings

If a scanner reports:

```text
LDAP Injection
```

always reproduce manually.

Verify:

```text
Baseline
Metacharacter behaviour
True condition
False condition
Actual impact
```

---

# False Positive: Wildcard Search Feature

Some applications intentionally support:

```text
*
```

as a wildcard.

For example:

```text
Employee Search
```

may deliberately allow:

```text
ali*
```

This is not necessarily LDAP injection.

The important question is:

```text
Can input alter query structure
beyond intended search functionality?
```

---

# False Positive: Generic 500 Error

A:

```text
500 Internal Server Error
```

after:

```text
(
```

does not prove LDAP injection.

The character may break:

```text
Application validation
JSON parsing
Template rendering
Another backend
```

Correlate multiple indicators.

---

# False Positive: Search Returns More Results

If:

```text
*
```

returns all results because wildcard searching is explicitly intended:

```text
Not necessarily vulnerable
```

Test whether structural LDAP syntax can escape the intended value context.

---

# False Positive: LDAP Error Message

An LDAP error confirms:

```text
LDAP technology
```

but not necessarily:

```text
LDAP Injection
```

Input may have reached a safe LDAP library that rejected malformed data.

---

# False Positive: Authentication Error Difference

Different messages for:

```text
Invalid user
Invalid password
```

may indicate:

```text
User enumeration
```

but not necessarily LDAP injection.

---

# Evidence Collection

Strong LDAP injection evidence includes:

```text
Original request
Original response
Modified request
Modified response
Controlled true condition
Controlled false condition
Result-count difference
LDAP-specific error
Authenticated session if bypass demonstrated
Directory data limited to authorised test information
```

---

# Evidence Table

| Test | Input | Result |
|---|---|---|
| Baseline | alice | 1 result |
| Invalid | nonexistent | 0 results |
| Wildcard | * | Multiple results |
| Prefix | a* | Matching results |
| Invalid syntax | ( | LDAP-related error |

This creates a clear, reproducible narrative.

---

# Minimal Evidence Principle

Do not collect:

```text
1000 directory records
```

when:

```text
2 controlled records
```

prove the vulnerability.

---

# Authentication Bypass Evidence

If authentication bypass exists, collect:

```text
Login request
Invalid or absent valid password
Modified LDAP input
Authentication response
Session cookie
Protected endpoint
Authenticated identity
```

Stop once the security impact is demonstrated.

---

# Example Finding: LDAP Injection

```text
Finding:
LDAP Injection in User Search Functionality

Observed:
The application's user search functionality incorporates the supplied username value into an LDAP search filter without correctly escaping LDAP filter metacharacters.

A normal search for a controlled username returned a single directory entry.

When the username parameter was replaced with an LDAP wildcard, the application returned multiple directory entries.

Additional controlled tests produced behaviour consistent with the supplied input altering the LDAP search filter.

Impact:
An attacker may be able to manipulate LDAP directory queries performed by the application.

Depending on the privileges of the application's LDAP account and the exposed functionality, this may allow unauthorised directory enumeration and disclosure of user or organisational information.

Recommendation:
Do not construct LDAP filters using untrusted input without context-specific encoding. Escape all untrusted values using a well-tested LDAP filter encoding function appropriate to the framework or library in use. Apply allow-list validation where appropriate and restrict the application's LDAP account and search base according to least privilege.
```

---

# Example Finding: LDAP Authentication Bypass

```text
Finding:
LDAP Injection Allows Authentication Bypass

Observed:
The login functionality uses attacker-controlled input when constructing an LDAP authentication query.

Using a controlled account, it was possible to modify the LDAP query so that authentication succeeded without supplying the valid account password.

The resulting session was accepted by protected application functionality.

Impact:
An unauthenticated attacker may be able to bypass the application's authentication mechanism and obtain access to user accounts.

Depending on which LDAP object is selected by the manipulated query, additional account compromise may be possible.

Recommendation:
Do not authenticate users by concatenating credentials into LDAP search filters. Safely locate the intended user using correctly escaped LDAP filter values and perform authentication using a secure LDAP bind or another framework-supported authentication mechanism. Ensure every untrusted value is encoded for its exact LDAP context.
```

---

# Example Finding: Blind LDAP Injection

```text
Finding:
Blind LDAP Injection in Directory Lookup Endpoint

Observed:
The directory lookup endpoint produced consistently different responses depending on whether a supplied LDAP condition evaluated to true or false.

Testing was performed using attributes belonging to a controlled account.

This demonstrated that attacker-controlled input can modify the LDAP search condition and that the application's response can be used as a boolean oracle.

Impact:
An attacker may be able to infer directory information through repeated LDAP queries even when the application does not directly return directory attributes.

The practical impact depends on accessible attributes, rate limiting, and the privileges of the application's LDAP identity.

Recommendation:
Use context-specific LDAP filter encoding for all untrusted values before they are included in LDAP search filters. Apply strict allow-list validation where appropriate, restrict searchable attributes, and configure the LDAP account according to least privilege.
```

---

# Example Finding: LDAP Information Disclosure

```text
Finding:
LDAP Query Manipulation Exposes Directory Information

Observed:
A search parameter was incorporated into an LDAP filter without correctly escaping wildcard characters.

Supplying a wildcard caused the application to return directory records outside the intended single-user search.

Testing was stopped after a minimal number of controlled records had been observed.

Impact:
An attacker may be able to enumerate directory users and associated attributes.

Exposed information may assist further attacks such as username enumeration, phishing, credential attacks, or organisational reconnaissance.

Recommendation:
Escape all LDAP filter values using the appropriate LDAP encoding routine and restrict both the search base and returned attributes to the minimum required by the application.
```

---

# Reporting Titles

Useful titles include:

```text
LDAP Injection Allows Authentication Bypass

LDAP Injection in User Search Functionality

Blind LDAP Injection Allows Directory Attribute Enumeration

LDAP Wildcard Injection Exposes Directory Users

LDAP Filter Injection Allows Unauthorised Directory Queries

LDAP Injection Exposes Active Directory Information

LDAP Search Filter Uses Unescaped User Input

LDAP Distinguished Name Constructed from Untrusted Input
```

---

# Severity

Severity depends on demonstrated impact.

Examples:

```text
LDAP error disclosure
→ Informational / Low

Limited user enumeration
→ Low / Medium

Directory attribute disclosure
→ Medium

Large-scale directory exposure
→ Medium / High

Authorisation bypass
→ High

Authentication bypass
→ High / Critical

Privileged account compromise
→ Critical

Directory modification
→ High / Critical
```

Do not assign severity based solely on:

```text
"LDAP Injection"
```

Assess:

```text
What can actually be achieved?
```

---

# Remediation

LDAP injection prevention should combine:

```text
Correct Context-Specific Escaping
            +
Allow-List Validation
            +
Least Privilege
            +
Restricted Search Scope
            +
Minimal Returned Attributes
```

---

# Escape LDAP Filter Values

When user input appears inside:

```text
LDAP Search Filter
```

use a trusted library implementing correct LDAP filter escaping.

Do not create custom escaping functions unless absolutely necessary.

---

# Escape Distinguished Names Separately

When user input is used inside:

```text
Distinguished Name
```

use:

```text
DN-specific escaping
```

not:

```text
LDAP filter escaping
```

These are different contexts.

---

# Allow-List Validation

Where business requirements allow, constrain values.

Example username policy:

```text
Letters
Numbers
Hyphen
Period
Underscore
```

depending on the actual identifier format.

Example conceptual rule:

```text
^[A-Za-z0-9._-]{1,64}$
```

Do not use this exact pattern blindly.

Match the application's legitimate username format.

---

# Validate Attribute Names

If users can choose fields such as:

```text
name
email
department
```

map them server-side.

Example:

```text
name
→ cn

email
→ mail

username
→ uid
```

Do not accept arbitrary LDAP attribute names from the client.

---

# Avoid Client-Controlled Filters

Do not expose an API such as:

```json
{
    "ldapFilter": "(uid=alice)"
}
```

unless the application explicitly requires raw LDAP functionality and applies very strong authorisation controls.

Prefer structured inputs:

```json
{
    "username": "alice"
}
```

with the server constructing the query safely.

---

# Least Privilege LDAP Account

The application should not bind using:

```text
Domain Administrator
Directory Administrator
Highly privileged service account
```

unless absolutely necessary.

Prefer:

```text
Dedicated service identity
Read-only access
Restricted OU
Required attributes only
```

---

# Restrict Search Base

Instead of:

```text
dc=example,dc=com
```

use a narrower base where possible:

```text
ou=ApplicationUsers,dc=example,dc=com
```

---

# Restrict Returned Attributes

Request:

```text
uid
displayName
mail
```

if those are all that are required.

Avoid unnecessarily returning:

```text
All directory attributes
```

---

# Secure Authentication Design

Prefer:

```text
Username
   ↓
Safely Escaped User Lookup
   ↓
Exact User DN
   ↓
LDAP Bind With Password
   ↓
Success / Failure
```

rather than building a filter containing both username and password.

---

# Error Handling

Return generic application errors.

Do not expose:

```text
LDAP filter
LDAP hostname
Base DN
Bind DN
Stack trace
Directory schema
```

to users.

---

# Logging

Log:

```text
LDAP query failures
Unexpected filter syntax
Repeated wildcard searches
Authentication failures
Directory errors
```

but do not log:

```text
Passwords
Sensitive bind credentials
Unnecessary directory attributes
```

---

# Monitoring

Potential indicators include:

```text
Repeated *
Repeated (
Repeated )
Malformed filters
High-volume prefix searches
Unexpected broad result sets
```

Be careful:

```text
*
```

may be legitimate in some directory applications.

Detection should consider application context.

---

# Secure Development Review

During code review, search for:

```text
LDAP libraries
String concatenation
Search filter construction
DN construction
User-controlled attributes
```

Then trace:

```text
SOURCE
 ↓
TRANSFORMATION
 ↓
LDAP SINK
```

---

# LDAP Injection Checklist

## Discovery

```text
[ ] LDAP-backed functionality identified
[ ] Authentication reviewed
[ ] Search functionality reviewed
[ ] Password reset reviewed
[ ] Group lookup reviewed
[ ] API endpoints reviewed
[ ] GraphQL reviewed where relevant
```

## Baseline

```text
[ ] Known valid input
[ ] Known invalid input
[ ] Empty input
[ ] Random input
[ ] Response status recorded
[ ] Response length recorded
[ ] Result count recorded
```

## Metacharacters

```text
[ ] *
[ ] (
[ ] )
[ ] \
[ ] Prefix wildcard
[ ] Controlled malformed syntax
```

## Query Behaviour

```text
[ ] Wildcard interpretation
[ ] Boolean behaviour
[ ] Error behaviour
[ ] Search expansion
[ ] Authentication impact
[ ] Blind oracle
```

## Context

```text
[ ] Search filter context identified
[ ] DN context identified
[ ] Attribute context identified
[ ] Correct encoding context understood
```

## Authentication

```text
[ ] Correct credentials baseline
[ ] Incorrect password baseline
[ ] Invalid username baseline
[ ] Query manipulation tested safely
[ ] Authenticated session verified
```

## Blind LDAP

```text
[ ] True condition
[ ] False condition
[ ] Response difference
[ ] Status difference
[ ] Length difference
[ ] Redirect difference
[ ] Controlled attribute only
```

## Directory Exposure

```text
[ ] Search base considered
[ ] Returned attributes reviewed
[ ] User enumeration assessed
[ ] Group enumeration assessed
[ ] Minimal evidence collected
```

## Privileges

```text
[ ] LDAP bind account considered
[ ] Read/write permissions considered
[ ] Search scope considered
[ ] Least privilege assessed
```

## Source Review

```text
[ ] Java LDAP APIs
[ ] .NET DirectoryServices
[ ] Python LDAP libraries
[ ] PHP LDAP functions
[ ] Node LDAP libraries
[ ] String concatenation
[ ] Filter escaping
[ ] DN escaping
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Intruder
[ ] Comparer
[ ] Decoder
[ ] Logger
[ ] Scanner
[ ] Custom helper script where useful
```

## Related Vulnerabilities

```text
[ ] Authentication
[ ] Authorisation
[ ] Password Reset
[ ] MFA
[ ] Information Disclosure
[ ] Business Logic
[ ] IDOR / BOLA
```

## Safety

```text
[ ] Controlled accounts used
[ ] Minimal directory data retrieved
[ ] No bulk directory dump
[ ] No directory modification
[ ] No account lockouts
[ ] No uncontrolled authentication attempts
```

---

# Quick Reference

```text
LDAP INJECTION

Input
  ↓
LDAP Query
  ↓
Can Syntax Change?
  ↓
Yes
  ↓
Injection Candidate
```

Useful initial characters:

```text
*
(
)
\
```

Useful first test:

```text
Known user
vs
Nonexistent user
vs
*
```

Look for:

```text
Result count
Response length
Errors
Status
Authentication state
```

Primary Burp tools:

```text
Proxy
Repeater
Comparer
Intruder
Decoder
Logger
Scanner
```

Primary remediation:

```text
LDAP Filter Escaping
DN Escaping
Allow-List Validation
Least Privilege
Restricted Search Base
```

---

# Recommended Testing Workflow

```text
Identify LDAP Functionality
          ↓
Capture in Burp
          ↓
Send to Repeater
          ↓
Normal Baseline
          ↓
Invalid Baseline
          ↓
Test *
          ↓
Test Parentheses
          ↓
Test Backslash
          ↓
Behaviour Changed?
       ↓          ↓
      NO         YES
       ↓          ↓
Other Tests   LDAP Candidate
                  ↓
          Determine Context
            ↓           ↓
         FILTER         DN
            ↓           ↓
      Filter Tests    DN Tests
            └─────┬─────┘
                  ↓
          Boolean Behaviour
                  ↓
           Controlled Proof
                  ↓
        Authentication Impact?
             ↓          ↓
            YES         NO
             ↓          ↓
       Verify Session   Search Impact
             └─────┬─────┘
                   ↓
            Directory Exposure
                   ↓
             Minimal Evidence
                   ↓
                Report
```

---

# References

## OWASP LDAP Injection Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html

Primary OWASP guidance for preventing LDAP injection.

---

## OWASP Injection Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html

General injection-prevention guidance covering safe APIs, validation, and context-specific escaping.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

The OWASP testing guide contains methodology applicable to injection testing and application assessment.

---

## RFC 4515

https://datatracker.ietf.org/doc/html/rfc4515

Defines LDAP search filter string representation and escaping rules.

---

## RFC 4514

https://datatracker.ietf.org/doc/html/rfc4514

Defines the string representation of LDAP Distinguished Names.

---

## RFC 4511

https://datatracker.ietf.org/doc/html/rfc4511

LDAP protocol specification.

---

## PortSwigger BApp Store

https://portswigger.net/bappstore

Useful when checking for Burp extensions that can support specialised testing workflows.

---

## PortSwigger Burp Repeater

https://portswigger.net/burp/documentation/desktop/tools/repeater

Repeater is particularly useful for manually testing LDAP-backed parameters and comparing controlled query behaviour.

---

## PortSwigger Burp Intruder

https://portswigger.net/burp/documentation/desktop/tools/intruder

Useful for applying small controlled LDAP test sets to selected parameters.

---

## PortSwigger Burp Comparer

https://portswigger.net/burp/documentation/desktop/tools/comparer

Useful for comparing true and false responses during blind LDAP injection testing.

---

## PortSwigger Burp Decoder

https://portswigger.net/burp/documentation/desktop/tools/decoder

Useful for understanding URL encoding and other transformations applied to LDAP metacharacters.

---

## PyBurp

https://portswigger.net/bappstore/d8969aceb89d4dc38e996f3c3579880d

A Burp extension that enables Python-based traffic processing and custom testing logic inside Burp.

It may be useful for building custom LDAP testing automation.

---

# Final LDAP Injection Testing Model

```text
                          LDAP INJECTION
                                ↓
                        IDENTIFY FUNCTION
                                ↓
                ┌───────────────┼────────────────┐
                ↓               ↓                ↓
              LOGIN           SEARCH          DIRECTORY
                ↓               ↓                ↓
             INPUT           INPUT            INPUT
                └───────────────┼────────────────┘
                                ↓
                         BURP REPEATER
                                ↓
                           BASELINE
                                ↓
              ┌─────────────────┼──────────────────┐
              ↓                 ↓                  ↓
              *                 (                  \
              ↓                 ↓                  ↓
          WILDCARD          STRUCTURE          ESCAPING
              └─────────────────┼──────────────────┘
                                ↓
                     BEHAVIOUR DIFFERENCE?
                         ↓              ↓
                        NO             YES
                         ↓              ↓
                  INVESTIGATE       LDAP CANDIDATE
                  OTHER SINKS            ↓
                                  DETERMINE CONTEXT
                                    ↓          ↓
                                  FILTER       DN
                                    ↓          ↓
                             FILTER ESCAPE   DN ESCAPE
                                    └────┬─────┘
                                         ↓
                                  BOOLEAN TEST
                                         ↓
                              TRUE            FALSE
                                ↓               ↓
                           RESPONSE A       RESPONSE B
                                └───────┬───────┘
                                        ↓
                              CONSISTENT ORACLE?
                                  ↓           ↓
                                 NO          YES
                                  ↓           ↓
                            INVESTIGATE    INJECTION
                                             ↓
                           ┌─────────────────┼──────────────────┐
                           ↓                 ↓                  ↓
                       AUTH BYPASS       DATA EXPOSURE      AUTHZ IMPACT
                           ↓                 ↓                  ↓
                     VERIFY SESSION     MINIMAL DATA      VERIFY CONTROL
                           └─────────────────┼──────────────────┘
                                             ↓
                                      LDAP PRIVILEGES
                                             ↓
                                ┌────────────┼────────────┐
                                ↓            ↓            ↓
                            SEARCH BASE    ATTRIBUTES    BIND RIGHTS
                                └────────────┼────────────┘
                                             ↓
                                      MINIMAL EVIDENCE
                                             ↓
                                           REPORT
                                             ↓
                                        REMEDIATION
                                             ↓
                         ┌───────────────────┼───────────────────┐
                         ↓                   ↓                   ↓
                   FILTER ESCAPING      DN ESCAPING       LEAST PRIVILEGE
                         └───────────────────┼───────────────────┘
                                             ↓
                                      VALIDATE FIX
```

The central principle is:

> LDAP injection occurs when untrusted data is allowed to influence LDAP query syntax. Testing should first establish whether LDAP metacharacters change query behaviour, then determine whether the input is used in a search filter, Distinguished Name, or another LDAP context. Demonstrate the smallest possible security impact using controlled accounts and minimal directory data. Remediation must use the correct LDAP escaping mechanism for the exact context, supported by allow-list validation and a least-privileged directory account.
