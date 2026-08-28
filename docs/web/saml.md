# SAML Security

Security Assertion Markup Language, or SAML, is an XML-based standard used to exchange authentication and authorisation information between security domains.

SAML is commonly used for enterprise Single Sign-On:

```text
User
  ↓
Service Provider
  ↓
Identity Provider
  ↓
Authentication
  ↓
SAML Assertion
  ↓
Service Provider
  ↓
Authenticated Session
```

Common environments include:

```text
Enterprise SSO
Microsoft Entra ID
AD FS
Okta
Ping Identity
Shibboleth
Keycloak
Google Workspace
Salesforce
SaaS applications
Internal corporate applications
```

A vulnerability in a SAML implementation can potentially result in:

```text
Authentication bypass
Account takeover
Identity impersonation
Privilege escalation
Cross-tenant access
Replay attacks
Session confusion
Information disclosure
XML-based attacks
```

SAML security depends heavily on:

```text
Cryptographic signature validation
Assertion validation
Issuer validation
Audience validation
Recipient validation
Destination validation
Time validation
Replay protection
Identity mapping
Secure XML processing
Trust configuration
```

!!! warning "Authorised Security Testing"
    Perform SAML testing only against applications and identity providers explicitly authorised for assessment. Use dedicated test accounts and test tenants wherever possible. Avoid impersonating real users, modifying production identity-provider configuration, extracting private signing keys, disrupting SSO infrastructure, or testing assertions against accounts outside the approved scope.

---

# SAML Terminology

The three most important parties are:

```text
Principal
Identity Provider
Service Provider
```

---

# Principal

The principal is usually:

```text
The User
```

who wants to access an application.

---

# Identity Provider

The Identity Provider is commonly abbreviated:

```text
IdP
```

The IdP authenticates the user.

Examples include:

```text
Microsoft Entra ID
AD FS
Okta
Keycloak
Ping Identity
Shibboleth
```

Conceptually:

```text
User
 ↓
IdP
 ↓
Authentication
```

---

# Service Provider

The Service Provider is commonly abbreviated:

```text
SP
```

The SP is the application the user wants to access.

Example:

```text
https://app.example.com
```

The SP trusts assertions issued by an authorised IdP.

---

# Basic SAML SSO Flow

A simplified SAML flow:

```text
User
 ↓
Service Provider
 ↓
Authentication Required
 ↓
SAML AuthnRequest
 ↓
Identity Provider
 ↓
User Authentication
 ↓
SAML Response
 ↓
Service Provider ACS
 ↓
Assertion Validation
 ↓
Session Created
```

---

# SAML Roles

Conceptually:

```text
┌─────────────┐
│    User     │
└──────┬──────┘
       ↓
┌─────────────┐
│     SP      │
│ Application │
└──────┬──────┘
       ↓
┌─────────────┐
│     IdP     │
│   Identity  │
└─────────────┘
```

The SP normally does not directly authenticate the user's password.

Instead:

```text
IdP
 ↓
Authenticates User
 ↓
Issues Assertion
 ↓
SP Trusts Assertion
```

This makes the trust relationship critical.

---

# SAML Components

Important SAML components include:

```text
SAMLRequest
SAMLResponse
Assertion
Issuer
Subject
NameID
Conditions
AudienceRestriction
SubjectConfirmation
AuthnStatement
AttributeStatement
Signature
RelayState
```

---

# SAMLRequest

A Service Provider may send:

```text
SAMLRequest
```

to the Identity Provider.

The request can contain information such as:

```text
Request ID
Issuer
Destination
Assertion Consumer Service URL
Requested authentication context
```

---

# SAMLResponse

After authentication, the IdP returns:

```text
SAMLResponse
```

to the Service Provider.

A common HTTP POST looks conceptually like:

```http
POST /saml/acs HTTP/1.1
Host: app.example.com
Content-Type: application/x-www-form-urlencoded

SAMLResponse=BASE64_ENCODED_XML&RelayState=...
```

---

# Assertion Consumer Service

The endpoint receiving the SAML response is usually called:

```text
Assertion Consumer Service
```

or:

```text
ACS
```

Examples:

```text
/saml/acs
/sso/saml
/auth/saml/callback
/login/saml2/sso/provider
```

The ACS is one of the most important endpoints during SAML testing.

---

# SAML Assertion

The assertion contains claims made by the IdP.

Conceptual example:

```xml
<saml:Assertion>

    <saml:Issuer>
        https://idp.example.com
    </saml:Issuer>

    <saml:Subject>

        <saml:NameID>
            test-user@example.com
        </saml:NameID>

    </saml:Subject>

    <saml:Conditions>

        <saml:AudienceRestriction>

            <saml:Audience>
                https://app.example.com
            </saml:Audience>

        </saml:AudienceRestriction>

    </saml:Conditions>

</saml:Assertion>
```

Real assertions normally contain additional:

```text
Namespaces
IDs
Timestamps
Signatures
SubjectConfirmation
Authentication statements
Attributes
```

---

# NameID

`NameID` often represents the authenticated identity.

Example:

```xml
<saml:NameID>
    alice@example.com
</saml:NameID>
```

Possible formats include:

```text
Email address
Persistent identifier
Transient identifier
Unspecified identifier
```

Do not assume NameID always contains an email address.

---

# Attributes

Assertions may contain additional user information.

Example:

```xml
<saml:Attribute
    Name="role">

    <saml:AttributeValue>
        user
    </saml:AttributeValue>

</saml:Attribute>
```

Other attributes may include:

```text
email
username
firstName
lastName
role
groups
department
tenant
organisation
employeeID
entitlements
```

---

# Authentication vs Authorisation

SAML can transport information used for both.

Authentication:

```text
Who is the user?
```

Authorisation:

```text
What is the user allowed to do?
```

For example:

```text
NameID
→ Authentication Identity

groups
→ Authorisation Input

role
→ Authorisation Input
```

A dangerous application may trust authorisation attributes without sufficient control.

---

# RelayState

`RelayState` commonly preserves application state across the SSO flow.

Example:

```text
User requests:

/admin/reports

↓

Redirect to IdP

↓

Authenticate

↓

Return to:

/admin/reports
```

RelayState may carry this destination.

It should not automatically be trusted as:

```text
Authorisation
```

---

# RelayState Security

Potential issues include:

```text
Open redirect
State confusion
Cross-flow substitution
Untrusted destination handling
Session mix-up
```

Refer to:

```text
docs/web/open-redirect.md
```

---

# SAML Bindings

Common SAML bindings include:

```text
HTTP Redirect Binding
HTTP POST Binding
SOAP Binding
Artifact Binding
```

The Web Browser SSO profile commonly uses:

```text
Redirect
+
POST
```

---

# HTTP Redirect Binding

An AuthnRequest may be sent in a URL:

```text
https://idp.example.com/sso?
SAMLRequest=...
&RelayState=...
&SigAlg=...
&Signature=...
```

The SAMLRequest may be:

```text
DEFLATE compressed
Base64 encoded
URL encoded
```

---

# HTTP POST Binding

The IdP commonly returns a SAMLResponse through an automatically submitted HTML form.

Conceptually:

```html
<form
    method="POST"
    action="https://app.example.com/saml/acs">

    <input
        type="hidden"
        name="SAMLResponse"
        value="BASE64_DATA">

    <input
        type="hidden"
        name="RelayState"
        value="...">

</form>
```

---

# SAML Metadata

SAML environments often publish metadata.

Potential paths include:

```text
/saml/metadata
/saml2/metadata
/metadata
/federationmetadata/2007-06/federationmetadata.xml
```

Metadata can contain:

```text
Entity ID
SSO endpoints
ACS endpoints
Bindings
Signing certificates
Encryption certificates
Logout endpoints
```

---

# Metadata Example

Conceptually:

```xml
<EntityDescriptor
    entityID="https://idp.example.com">

    <IDPSSODescriptor>

        <KeyDescriptor use="signing">
            ...
        </KeyDescriptor>

        <SingleSignOnService
            Binding="..."
            Location="https://idp.example.com/sso"/>

    </IDPSSODescriptor>

</EntityDescriptor>
```

---

# Public Certificates

SAML metadata commonly contains:

```text
Public X.509 Certificates
```

This is normally expected.

Do not report:

```text
SAML signing certificate exposed
```

merely because the public certificate appears in metadata.

The private signing key is the secret.

---

# SAML Reconnaissance

Useful strings to search for:

```text
SAML
SAMLRequest
SAMLResponse
RelayState
AssertionConsumerService
SingleSignOnService
NameID
EntityDescriptor
IDPSSODescriptor
SPSSODescriptor
```

---

# Application Reconnaissance

Look for endpoints such as:

```text
/login/saml
/saml/login
/saml/acs
/saml2
/sso
/sso/login
/auth/saml
/auth/sso
/federation
```

---

# JavaScript Analysis

Search JavaScript for:

```text
saml
sso
identityProvider
relayState
acs
metadata
```

Refer to:

```text
docs/web/reconnaissance/javascript-analysis.md
```

---

# SAML Testing Methodology

A comprehensive workflow:

```text
Identify SAML SSO
       ↓
Map SP and IdP
       ↓
Capture Complete Login Flow
       ↓
Identify SAMLRequest
       ↓
Identify SAMLResponse
       ↓
Decode Assertion
       ↓
Map Signed Elements
       ↓
Identify Identity Attributes
       ↓
Test Signature Enforcement
       ↓
Test Assertion Integrity
       ↓
Test Audience
       ↓
Test Recipient
       ↓
Test Destination
       ↓
Test Issuer
       ↓
Test InResponseTo
       ↓
Test Time Conditions
       ↓
Test Replay
       ↓
Test Identity Mapping
       ↓
Test XML Parser Behaviour
       ↓
Test RelayState
       ↓
Test Session Creation
       ↓
Test Logout
       ↓
Assess Impact
```

---

# Test Accounts

Ideally use at least two controlled accounts:

```text
Account A
Account B
```

If role testing is authorised:

```text
Account A
→ Standard User

Account B
→ Different Controlled Role
```

This makes identity substitution testing much safer.

---

# Capture the Full SAML Flow

Use Burp Proxy while performing a normal SSO login.

Record:

```text
Initial SP request

SP → IdP redirect

SAMLRequest

IdP authentication

SAMLResponse

ACS POST

SP session cookie

Post-login redirect
```

Do not begin mutation before understanding the normal flow.

---

# Establish a Baseline

Record:

```text
IdP hostname
SP hostname
ACS endpoint
Entity IDs
NameID
Audience
Issuer
Destination
Recipient
NotBefore
NotOnOrAfter
SessionIndex
InResponseTo
RelayState
Signature location
```

---

# Decode SAMLResponse

A POST-bound SAML response is often Base64 encoded.

Using Python:

```bash
python3 - <<'PY'
import base64

value = input("SAMLResponse: ").strip()

decoded = base64.b64decode(value)

print(
    decoded.decode(
        "utf-8",
        errors="replace"
    )
)
PY
```

---

# Pretty Print XML

If `xmllint` is installed:

```bash
echo 'BASE64_VALUE' |
base64 -d |
xmllint --format -
```

---

# URL-Decoded SAML

If copied directly from HTTP traffic, URL encoding may also need handling.

Example Python helper:

```python
#!/usr/bin/env python3

import sys
import base64
import urllib.parse


value = sys.stdin.read().strip()

value = urllib.parse.unquote_plus(
    value
)

decoded = base64.b64decode(
    value
)

print(
    decoded.decode(
        "utf-8",
        errors="replace"
    )
)
```

Usage:

```bash
cat saml.txt |
python3 decode_saml.py
```

---

# Burp SAML Raider

SAML Raider is one of the most useful Burp extensions for SAML assessments.

It provides:

```text
SAML message decoding
SAML message editing
Certificate management
Signature manipulation
XML Signature Wrapping helpers
XXE testing helpers
XSLT testing helpers
```

Official BApp Store:

```text
https://portswigger.net/bappstore/c61cfa893bb14db4b01775554f7b802e
```

Install from:

```text
Burp Suite
    ↓
Extensions
    ↓
BApp Store
    ↓
SAML Raider
```

---

# SAML Raider Workflow

Recommended flow:

```text
Capture SAMLResponse
       ↓
Send to Repeater
       ↓
SAML Raider Tab
       ↓
Inspect XML
       ↓
Inspect Signature
       ↓
Inspect Certificate
       ↓
Modify Controlled Attribute
       ↓
Send
       ↓
Observe Validation
```

---

# SAML Raider Certificate Management

SAML Raider can help inspect and manage:

```text
X.509 certificates
Certificate chains
Public keys
Private keys used for controlled testing
```

It can also generate controlled certificates for signature validation testing.

Never treat:

```text
Ability to create a certificate
```

as evidence that the SP trusts it.

The vulnerability exists only if:

```text
SP Accepts Untrusted Signature
```

---

# SAML Editor

The BApp Store also contains:

```text
SAML Editor
```

which provides SAML decoding and encoding functionality.

SAML Raider is generally more useful for a full SAML security assessment because it additionally supports:

```text
Signature testing
Certificate handling
XSW testing
```

---

# SAMLReQuest

Another BApp Store extension is:

```text
SAMLReQuest
```

which assists with viewing, decoding, and modifying SAML requests and responses.

Use the tool that best fits your workflow.

Avoid installing several extensions that perform identical transformations unless needed.

---

# Burp Repeater

Repeater remains essential even with SAML Raider.

Use it to:

```text
Replay assertions
Modify attributes
Modify NameID
Remove signatures
Change conditions
Change audience
Change issuer
Change recipient
Change destination
Modify RelayState
```

Make one controlled change at a time.

---

# Burp Comparer

Comparer is useful for:

```text
Account A assertion
vs
Account B assertion
```

Compare:

```text
NameID
Attributes
Audience
Issuer
SessionIndex
Conditions
Signature structure
```

This helps identify which fields actually control application identity.

---

# Burp Decoder

Decoder can assist with:

```text
Base64
URL encoding
XML
```

SAML Raider is normally more convenient for SAML-specific transformations.

---

# Signature Validation

One of the most important SAML security questions is:

```text
What exactly is signed?
```

Possible structures include:

```text
Signed Response

Signed Assertion

Signed Response + Signed Assertion
```

The application must validate the signature appropriate to its trust model.

---

# XML Signature

A SAML signature may contain:

```xml
<ds:Signature>

    <ds:SignedInfo>

        <ds:Reference
            URI="#ASSERTION_ID">

            ...

        </ds:Reference>

    </ds:SignedInfo>

    <ds:SignatureValue>
        ...
    </ds:SignatureValue>

    <ds:KeyInfo>
        ...
    </ds:KeyInfo>

</ds:Signature>
```

The important relationship is:

```text
Signature
   ↓
Reference URI
   ↓
Specific XML Element ID
```

---

# Signature Enforcement Test

A safe initial test with your own account:

```text
Valid Signed Assertion
        ↓
Accepted

Remove Signature
        ↓
Send Again
```

Expected secure behaviour:

```text
Rejected
```

If accepted:

```text
Signature Enforcement Failure
```

may exist.

---

# Modified Assertion Test

Using your own controlled account:

```text
Capture Valid Assertion
        ↓
Modify Non-Sensitive Controlled Attribute
        ↓
Leave Existing Signature
        ↓
Send
```

Expected:

```text
Signature Validation Fails
```

If the modified assertion is accepted, investigate whether the modified element is actually covered by the signature.

---

# Do Not Begin With Administrator

Do not immediately change:

```text
role=user
```

to:

```text
role=admin
```

against a production system.

Start with:

```text
Controlled identity attributes
```

and determine whether integrity validation exists.

Privilege testing should follow only where authorised.

---

# Signature Exclusion

A vulnerable implementation may accept:

```text
Unsigned Assertion
```

or:

```text
Unsigned Response
```

when a signature should be mandatory.

Testing flow:

```text
Valid Signed Message
       ↓
Remove Signature
       ↓
Replay
       ↓
Accepted?
   ↓         ↓
  NO        YES
   ↓         ↓
Secure    Investigate
```

---

# Signature Wrapping

XML Signature Wrapping is commonly abbreviated:

```text
XSW
```

The core problem is a mismatch between:

```text
Element Verified by Signature
```

and:

```text
Element Used by Application
```

Conceptually:

```text
XML Document
   ↓
Signature Validator
   ↓
Validates Assertion A

Application Logic
   ↓
Processes Assertion B
```

If:

```text
Assertion A
≠
Assertion B
```

authentication may be compromised.

---

# XSW Concept

Example concept:

```xml
<Response>

    <Assertion ID="SIGNED">
        Signed legitimate identity
    </Assertion>

    <Assertion>
        Attacker-controlled identity
    </Assertion>

</Response>
```

A secure parser and SAML library must ensure the application consumes the exact assertion that was cryptographically validated.

---

# SAML Raider XSW Testing

SAML Raider supports multiple common XML Signature Wrapping transformations.

Workflow:

```text
Controlled Valid Assertion
        ↓
SAML Raider
        ↓
Apply XSW Variant
        ↓
Send to SP
        ↓
Observe
```

Only perform this using:

```text
Controlled identities
```

until the validation weakness is established.

---

# Duplicate Assertions

Test whether the SP handles:

```text
Multiple Assertions
```

securely.

Potential parser disagreement:

```text
Validator
→ First Assertion

Application
→ Second Assertion
```

or the reverse.

---

# Duplicate IDs

XML signature validation relies on element identifiers.

Duplicate IDs should be rejected.

Conceptually:

```xml
<Assertion ID="abc">
```

appearing multiple times can create ambiguity.

Modern SAML libraries should defend against this.

---

# Signature Reference Validation

The application should verify:

```text
Signature reference
```

points to:

```text
The exact expected SAML element
```

and not merely accept:

```text
Any valid signed element somewhere in XML
```

---

# Certificate Trust

A critical question:

```text
Which certificate is trusted?
```

Secure model:

```text
SP Configuration
      ↓
Known IdP Certificate
      ↓
Signature Verified
```

Dangerous model:

```text
SAML Message
      ↓
Embedded Certificate
      ↓
Automatically Trusted
```

The application must not blindly trust arbitrary signing certificates supplied by the assertion itself.

---

# Self-Signed Certificate Test

Conceptually:

```text
Create Test Certificate
       ↓
Sign Modified Assertion
       ↓
Send
```

Expected:

```text
Rejected
```

because:

```text
Certificate
≠
Trusted IdP Certificate
```

If accepted:

```text
Broken Certificate Trust
```

may permit assertion forgery.

SAML Raider can assist with this controlled test.

---

# KeyInfo

XML signatures may contain:

```xml
<ds:KeyInfo>
```

The application should not automatically trust attacker-supplied key information.

Trust should be anchored in:

```text
SP-side trusted configuration
```

---

# Algorithm Validation

Inspect:

```text
SignatureMethod
DigestMethod
CanonicalizationMethod
```

Example:

```xml
<ds:SignatureMethod
    Algorithm="..."/>
```

The implementation should use supported secure algorithms and reject unsafe or unexpected algorithm combinations.

---

# Assertion Conditions

Important assertion conditions include:

```text
NotBefore
NotOnOrAfter
AudienceRestriction
```

Example:

```xml
<saml:Conditions
    NotBefore="2026-08-28T10:00:00Z"
    NotOnOrAfter="2026-08-28T10:05:00Z">
```

---

# NotBefore

The assertion should not be accepted before:

```text
NotBefore
```

subject to a small configured allowance for legitimate clock skew.

---

# NotOnOrAfter

The assertion should not be accepted after:

```text
NotOnOrAfter
```

Test:

```text
Valid Assertion
     ↓
Wait Until Expired
     ↓
Replay
```

Expected:

```text
Rejected
```

---

# Clock Skew

Small clock-skew allowances are normal.

Example concept:

```text
1 to several minutes
```

depending on architecture.

Do not report a small legitimate tolerance as a vulnerability without security impact.

---

# Excessive Assertion Lifetime

An assertion valid for:

```text
Hours
```

or:

```text
Days
```

may increase the impact of token theft.

Prefer:

```text
Short-lived assertions
```

appropriate to the SSO flow.

---

# Audience Validation

The assertion may specify:

```xml
<saml:Audience>
    https://app.example.com
</saml:Audience>
```

This identifies the intended relying party.

The SP should verify:

```text
Audience
=
Expected SP
```

---

# Audience Confusion

Consider:

```text
IdP
 ├── App A
 ├── App B
 └── App C
```

An assertion issued for:

```text
App A
```

should not automatically be accepted by:

```text
App B
```

---

# Audience Test

If you have two authorised test applications using the same IdP:

```text
Authenticate to App A
        ↓
Capture Assertion
        ↓
Submit to App B ACS
```

Expected:

```text
Rejected
```

If accepted:

```text
Audience Validation Failure
```

may exist.

---

# Recipient Validation

SubjectConfirmationData may contain:

```xml
Recipient="https://app.example.com/saml/acs"
```

The SP should verify the assertion is intended for the current recipient.

---

# Destination Validation

The SAML Response may contain:

```xml
Destination="https://app.example.com/saml/acs"
```

The SP should validate this according to the protocol and implementation requirements.

---

# Issuer Validation

Example:

```xml
<saml:Issuer>
    https://idp.example.com
</saml:Issuer>
```

The SP must verify that the assertion was issued by:

```text
A Trusted IdP
```

not merely:

```text
Any syntactically valid issuer
```

---

# Multi-IdP Environments

Some applications support:

```text
Customer A IdP
Customer B IdP
Customer C IdP
```

This creates additional trust-boundary complexity.

Test:

```text
Tenant A Assertion
       ↓
Tenant B Login Endpoint
```

Expected:

```text
Rejected
```

---

# Cross-Tenant SAML Confusion

A severe vulnerability may occur if:

```text
Tenant A
controls its own IdP
```

and the application incorrectly allows:

```text
Tenant A assertion
```

to authenticate:

```text
Tenant B identity
```

This can create:

```text
Cross-Tenant Account Takeover
```

---

# Identity Mapping

The SP must map SAML identities safely.

Possible identifiers:

```text
NameID
email
username
employeeID
persistent ID
external ID
```

Ask:

```text
Which attribute uniquely identifies the account?
```

---

# Email-Based Identity Mapping

A common pattern:

```text
SAML email
    ↓
Find Local Account By Email
    ↓
Login
```

Potential problems include:

```text
Unverified email claims
Case normalisation
Unicode normalisation
Aliases
Domain confusion
Duplicate identities
Tenant confusion
```

---

# Case Sensitivity

Test controlled variations such as:

```text
Test.User@example.com
test.user@example.com
```

depending on how the application treats identity values.

The IdP and SP should agree on canonical identity mapping.

---

# Unicode and Normalisation

Identity comparison should be consistent.

Potential edge cases include:

```text
Unicode characters
Whitespace
Trailing spaces
Normalisation differences
```

Do not perform large identity mutation sets against real accounts.

Use controlled identities.

---

# NameID vs Attribute Identity

Some applications may receive:

```text
NameID = account-A
```

but:

```text
email = account-B@example.com
```

Determine:

```text
Which value controls authentication?
```

A mismatch between:

```text
Signed / validated identity
```

and:

```text
Application lookup identity
```

can create security issues.

---

# Duplicate Attributes

An assertion might contain:

```text
email=A
email=B
```

or multiple attribute elements with the same name.

Different components may interpret duplicates differently.

Conceptually:

```text
SAML Library
→ First Value

Application
→ Last Value
```

Parser disagreement can create identity confusion.

---

# Attribute-Based Roles

Example:

```xml
<saml:Attribute
    Name="role">

    <saml:AttributeValue>
        user
    </saml:AttributeValue>

</saml:Attribute>
```

If roles are taken directly from SAML:

```text
IdP
 ↓
role=admin
 ↓
SP
 ↓
Administrator
```

then the IdP becomes part of the application's authorisation trust boundary.

---

# Role Manipulation

Using a controlled role account:

```text
role=user
```

change:

```text
role
```

while invalidating the existing signature.

Expected:

```text
Assertion Rejected
```

If accepted:

```text
Assertion Integrity Failure
```

may exist.

---

# Group Mapping

SAML may transport:

```text
groups
```

Example:

```text
Administrators
Finance
Developers
Security
```

Test whether:

```text
Unknown groups
Duplicate groups
Case changes
Unexpected group values
```

affect authorisation.

Refer to:

```text
docs/web/authorisation.md
```

---

# Privilege Escalation

Potential SAML privilege escalation paths:

```text
Unsigned role attributes
Weak signature validation
XSW
Duplicate attributes
Cross-tenant identity mapping
Improper group mapping
Trusting user-controlled IdP claims
```

---

# InResponseTo

A SAML response may contain:

```text
InResponseTo
```

linking it to the original authentication request.

Conceptually:

```text
AuthnRequest ID=ABC
       ↓
SAMLResponse
InResponseTo=ABC
```

This helps bind:

```text
Request
```

to:

```text
Response
```

---

# InResponseTo Testing

Capture two controlled authentication flows:

```text
Flow A
Flow B
```

Attempt to cross-use responses where appropriate.

Expected:

```text
Response A
should correspond to
Request A
```

The exact requirements depend on:

```text
SP-initiated
vs
IdP-initiated
```

SSO.

---

# SP-Initiated SSO

Flow:

```text
User
 ↓
SP
 ↓
AuthnRequest
 ↓
IdP
 ↓
SAMLResponse
 ↓
SP
```

Here:

```text
InResponseTo
```

normally has clear relevance.

---

# IdP-Initiated SSO

Flow:

```text
User
 ↓
IdP
 ↓
Select Application
 ↓
SAMLResponse
 ↓
SP
```

There may be no preceding SP AuthnRequest.

IdP-initiated SSO changes some request-correlation assumptions.

---

# Unsolicited Responses

Determine whether the SP accepts:

```text
Unsolicited SAML Responses
```

If not required:

```text
Rejecting them
```

can reduce attack surface.

---

# Replay Attacks

A valid SAML assertion should not necessarily be reusable indefinitely.

Test:

```text
Authenticate
 ↓
Capture SAMLResponse
 ↓
Complete Login
 ↓
Replay Same SAMLResponse
```

Observe whether:

```text
New Session Created
```

---

# Replay Context

Replay severity depends on:

```text
Assertion lifetime
One-time enforcement
Session state
Exposure likelihood
Authentication sensitivity
```

---

# OneTimeUse

SAML supports:

```xml
<saml:OneTimeUse/>
```

as a condition indicating the assertion should not be reused.

Not every implementation uses it.

Regardless, replay risk should be assessed according to the application's SSO design.

---

# Replay Cache

A Service Provider can maintain a cache of consumed:

```text
Assertion IDs
Response IDs
```

for the relevant validity period.

Conceptually:

```text
Assertion ID
    ↓
Seen Before?
 ↓        ↓
NO       YES
 ↓        ↓
Accept   Reject
```

---

# Session Creation

After successful SAML validation:

```text
SAML Assertion
      ↓
SP
      ↓
Local Session
```

Inspect:

```text
Session cookie
Session rotation
Session lifetime
Authentication level
User identity
```

Refer to:

```text
docs/web/session-management.md
```

---

# Session Fixation

The SP should establish a fresh authenticated session after SSO.

Test whether:

```text
Pre-auth session ID
```

remains unchanged after:

```text
SAML authentication
```

where the session architecture makes this relevant.

---

# Logout

SAML environments may implement:

```text
Local logout
Single Logout
```

commonly abbreviated:

```text
SLO
```

---

# Local Logout

Local logout may terminate:

```text
SP Session
```

while leaving:

```text
IdP Session
```

active.

The user may immediately SSO back in.

This is not automatically a vulnerability.

---

# Single Logout

SAML Single Logout can coordinate logout between:

```text
SP
IdP
Other SPs
```

It introduces additional:

```text
SAMLRequest
SAMLResponse
Signature validation
Redirect handling
```

attack surface.

---

# Logout Testing

Verify:

```text
SP session invalidated
Session cookie unusable
Back button behaviour
IdP session behaviour understood
Other applications unaffected unless expected
```

---

# RelayState Testing

Capture:

```text
RelayState
```

and determine whether it contains:

```text
Path
URL
Opaque identifier
State token
```

---

# Open Redirect via RelayState

Example:

```text
RelayState=https://example.org/
```

If the SP redirects to arbitrary external locations after SSO:

```text
Open Redirect
```

may exist.

Refer to:

```text
docs/web/open-redirect.md
```

---

# RelayState Integrity

If RelayState carries security-sensitive state:

```text
Account
Tenant
Destination
Transaction
```

determine whether modification changes server-side behaviour.

RelayState should not become an unsigned authorisation mechanism.

---

# SAML and CSRF

SSO endpoints can interact with:

```text
Login CSRF
Session swapping
Unsolicited assertions
```

The application should correctly bind authentication responses to intended flows where appropriate.

Refer to:

```text
docs/web/csrf.md
```

---

# Login CSRF

Conceptually:

```text
Attacker Authenticates
       ↓
Attacker SAML Response
       ↓
Victim Browser
       ↓
Victim Becomes Logged In
As Attacker
```

This can cause:

```text
Data entered into attacker account
Account confusion
Sensitive activity associated with wrong identity
```

The practical feasibility depends on the SAML flow and SP protections.

---

# XML Parsing

SAML is XML.

Therefore the SAML processing stack may potentially expose XML-related attack surface.

Examples:

```text
XXE
XSLT processing
XML Signature Wrapping
Parser differentials
Namespace confusion
```

---

# XXE

If the SAML XML parser allows unsafe external entity resolution:

```text
XXE
```

may become possible.

Refer to:

```text
docs/web/xxe.md
```

---

# SAML Raider XXE Support

SAML Raider provides functionality to insert XXE test structures.

Use:

```text
Controlled external interaction
```

or:

```text
Non-sensitive local proof
```

according to the authorised scope.

Do not attempt sensitive file extraction merely to prove parser behaviour.

---

# SAML and XSLT

XML signatures can involve transformations.

Unsafe XSLT processing in vulnerable implementations can create additional risk.

SAML Raider includes functionality to assist with XSLT-related testing.

Use these tests only when:

```text
Relevant
Authorised
Controlled
```

---

# XML Comments

XML parsing and identity extraction can sometimes behave unexpectedly around:

```xml
<!-- comments -->
```

Testing parser consistency may be useful when assessing older or custom SAML implementations.

The important security question remains:

```text
Does the identity consumed by the application
match the identity protected by the signature?
```

---

# Namespace Handling

SAML relies heavily on XML namespaces.

Examples:

```text
saml:
samlp:
ds:
```

Custom or inconsistent XML parsing may introduce:

```text
Namespace confusion
Element confusion
Parser differentials
```

Prefer mature SAML libraries rather than custom XML processing.

---

# XML Canonicalisation

XML signatures rely on canonicalisation.

Conceptually:

```text
XML
 ↓
Canonical Representation
 ↓
Digest
 ↓
Signature
```

Do not implement SAML signature validation manually.

Use established libraries.

---

# SAML and XXE Relationship

Do not report:

```text
SAML uses XML
```

as:

```text
XXE vulnerability
```

You must demonstrate unsafe XML parser behaviour.

---

# SAML and Host Header Attacks

SSO implementations may construct:

```text
ACS URLs
Redirect URLs
Metadata URLs
Entity IDs
```

using request-derived host information.

If untrusted headers influence these values:

```text
Host Header Attack
```

may become relevant.

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# Dynamic ACS URLs

Look for SAML requests where:

```text
AssertionConsumerServiceURL
```

changes according to:

```text
Host
X-Forwarded-Host
Forwarded
```

A manipulated callback location can have serious consequences if the IdP accepts attacker-controlled destinations.

---

# ACS Allow-Listing

Identity Providers should restrict ACS destinations to:

```text
Pre-registered trusted endpoints
```

rather than trusting arbitrary URLs supplied in authentication requests.

---

# SAML and Open Redirects

Redirect handling appears in several places:

```text
RelayState
Login endpoint
Logout endpoint
IdP discovery
Post-authentication redirect
```

Open redirects can support:

```text
Phishing
SSO flow manipulation
Token leakage in badly designed implementations
```

---

# SAML and Information Disclosure

Potentially exposed information includes:

```text
User email
Name
Groups
Roles
Department
Employee ID
Tenant ID
Internal domain names
IdP identifiers
Internal URLs
```

Some assertion attributes may be unnecessarily exposed to the SP or browser.

Apply:

```text
Data Minimisation
```

---

# Browser Exposure

With HTTP POST binding, the SAMLResponse passes through the browser.

Therefore:

```text
Browser history
Extensions
Logs
Debugging tools
Analytics
Proxy logs
```

may become relevant to token exposure.

Sensitive assertions should have:

```text
Short lifetimes
Secure transport
Replay protection
```

---

# Caching

Authentication responses should not be unnecessarily cached.

Review:

```text
Cache-Control
Pragma
```

on SAML endpoints where relevant.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# HTTPS

SAML endpoints should use:

```text
HTTPS
```

including:

```text
IdP SSO
SP ACS
Metadata retrieval where appropriate
Logout endpoints
```

Transport security protects SAML messages while in transit.

---

# SAML Certificate Expiration

Inspect signing certificate:

```text
Subject
Issuer
Serial
Not Before
Not After
Fingerprint
Key algorithm
```

Expired or soon-to-expire certificates may create:

```text
Availability risk
```

rather than direct exploitation.

---

# Certificate Rotation

A secure operational design should support:

```text
Certificate rollover
```

without disabling signature validation.

Dangerous workaround:

```text
Certificate expired
      ↓
Disable signature verification
```

Never recommend this.

---

# SAML and MFA

The IdP may enforce:

```text
MFA
```

before issuing the assertion.

The SP may receive information about:

```text
Authentication context
```

or assurance level.

Refer to:

```text
docs/web/mfa.md
```

---

# AuthnContext

SAML can include:

```text
AuthnContextClassRef
```

representing the authentication context.

An SP may require stronger authentication for:

```text
Administrative functions
Financial actions
Sensitive operations
```

---

# Step-Up Authentication

Potential flow:

```text
Normal SSO
   ↓
Standard Assurance
   ↓
Sensitive Action
   ↓
Require Stronger AuthnContext
   ↓
IdP MFA
```

Test whether sensitive operations genuinely require the intended authentication level.

---

# MFA Bypass Through SAML

A flawed application might:

```text
Trust any valid SAML assertion
```

without checking:

```text
Required authentication context
```

This could bypass intended step-up authentication.

The actual requirement must be confirmed before reporting.

---

# SAML and Password Reset

Password reset may bypass federated identity controls.

For example:

```text
SAML-only account
     ↓
Local Password Reset
     ↓
Local Password Login
```

If local authentication was intended to be disabled, this can create an alternate authentication path.

Refer to:

```text
docs/web/password-reset.md
```

---

# Alternate Authentication Paths

For SAML-enabled accounts test:

```text
Normal password login
Password reset
Magic link
Mobile API
Legacy login
Basic authentication
OAuth login
Recovery flow
```

The strongest SAML configuration is irrelevant if:

```text
A weaker alternative login path
```

bypasses it.

---

# SAML and OAuth

Applications sometimes support both:

```text
SAML
OAuth / OIDC
```

Do not confuse the protocols.

SAML:

```text
XML Assertions
Enterprise Federation
```

OIDC:

```text
OAuth 2.0 Based
JWT / JSON
Identity Layer
```

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# SAML vs OIDC

| SAML | OIDC |
|---|---|
| XML | JSON/JWT |
| Assertions | ID Tokens |
| IdP | OpenID Provider |
| SP | Relying Party |
| ACS | Redirect URI |
| Entity ID | Client ID |
| SAML metadata | OIDC discovery |

Both require strict:

```text
Issuer
Audience
Destination
Token integrity
State
```

validation.

---

# SAML and JWT

Some architectures:

```text
SAML
 ↓
Gateway
 ↓
JWT
 ↓
Application
```

A vulnerability may occur during:

```text
SAML-to-JWT claim mapping
```

Review:

```text
Identity
Role
Groups
Tenant
Audience
```

Refer to:

```text
docs/web/jwt.md
```

---

# SAML and IDOR / BOLA

SAML establishes identity.

IDOR/BOLA concerns:

```text
What objects that identity can access
```

A secure SAML login does not guarantee secure object authorisation.

Refer to:

```text
docs/web/idor-bola.md
```

---

# SAML and Mass Assignment

SAML attributes should not automatically become arbitrary writable application properties.

Dangerous conceptual flow:

```text
SAML Attributes
      ↓
Generic Object Mapper
      ↓
Local User Object
```

Potential sensitive fields:

```text
role
admin
tenant
permissions
accountType
```

Refer to:

```text
docs/web/mass-assignment.md
```

---

# SAML and Business Logic

SAML may affect:

```text
Account provisioning
Tenant assignment
Role assignment
Licence assignment
Organisation membership
Account linking
```

These are business logic boundaries.

Refer to:

```text
docs/web/business-logic.md
```

---

# Just-In-Time Provisioning

Many SAML applications use:

```text
JIT Provisioning
```

Flow:

```text
Valid SAML Identity
       ↓
No Local Account
       ↓
Automatically Create Account
```

Test:

```text
Which attributes control account creation?
```

---

# JIT Provisioning Risks

Potential issues:

```text
Untrusted role assignment
Wrong tenant assignment
Duplicate account creation
Email collision
Domain confusion
Unexpected administrative privileges
```

---

# Account Linking

An application may link:

```text
Existing local account
```

to:

```text
SAML identity
```

using:

```text
Email
Username
External ID
```

Incorrect account linking can result in account takeover.

---

# Domain-Based Trust

Dangerous pattern:

```text
email ends with @example.com
      ↓
Automatically trusted
```

The application must ensure the SAML assertion originates from the correct trusted IdP and tenant.

An email suffix alone is not a secure trust boundary.

---

# IdP Discovery

Applications supporting many IdPs may ask:

```text
Enter email
```

then determine:

```text
Which IdP?
```

Potential issues:

```text
Tenant enumeration
Open redirect
Incorrect IdP selection
Cross-tenant confusion
Domain takeover implications
```

---

# Tenant Enumeration

Responses such as:

```text
SSO configured
```

versus:

```text
No organisation found
```

may reveal customer organisations.

Assess whether this information is sensitive.

---

# SAML Fuzzing Strategy

Avoid random large XML fuzzing initially.

Use structured changes:

```text
Baseline
   ↓
One Field Changed
   ↓
Observe
```

Suggested order:

```text
NameID
Issuer
Audience
Recipient
Destination
NotBefore
NotOnOrAfter
InResponseTo
RelayState
Attributes
Signature
```

---

# SAML Test Matrix

| Test | Expected Secure Result |
|---|---|
| Remove signature | Reject |
| Modify signed NameID | Reject |
| Modify signed role | Reject |
| Untrusted signing certificate | Reject |
| Wrong audience | Reject |
| Wrong recipient | Reject |
| Wrong issuer | Reject |
| Expired assertion | Reject |
| Future assertion | Reject |
| Invalid InResponseTo | Reject where required |
| Replay | Reject where one-time semantics apply |
| XSW | Reject |
| Duplicate ambiguous assertions | Reject |
| Untrusted tenant assertion | Reject |

Exact expectations depend on the intended SAML profile and architecture.

---

# Controlled SAML Mutation Script

For basic analysis, the following script decodes a SAML response and prints important values.

```python
#!/usr/bin/env python3

import argparse
import base64
import urllib.parse
import xml.etree.ElementTree as ET


NS = {
    "saml": (
        "urn:oasis:names:tc:"
        "SAML:2.0:assertion"
    ),
    "samlp": (
        "urn:oasis:names:tc:"
        "SAML:2.0:protocol"
    ),
}


def text(element):

    if element is None:
        return None

    return element.text


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Decode and inspect a SAMLResponse "
            "for authorised security testing."
        )
    )

    parser.add_argument(
        "file",
        help=(
            "File containing the encoded "
            "SAMLResponse value."
        )
    )

    args = parser.parse_args()

    with open(
        args.file,
        "r",
        encoding="utf-8"
    ) as handle:

        encoded = handle.read().strip()

    encoded = urllib.parse.unquote_plus(
        encoded
    )

    xml_data = base64.b64decode(
        encoded
    )

    root = ET.fromstring(
        xml_data
    )

    print(
        ET.tostring(
            root,
            encoding="unicode"
        )
    )

    print()
    print("=" * 70)
    print("SAML SUMMARY")
    print("=" * 70)

    issuer = root.find(
        ".//saml:Issuer",
        NS
    )

    name_id = root.find(
        ".//saml:NameID",
        NS
    )

    audience = root.find(
        ".//saml:Audience",
        NS
    )

    conditions = root.find(
        ".//saml:Conditions",
        NS
    )

    confirmation = root.find(
        ".//saml:SubjectConfirmationData",
        NS
    )

    print(
        "Issuer:",
        text(issuer)
    )

    print(
        "NameID:",
        text(name_id)
    )

    print(
        "Audience:",
        text(audience)
    )

    if conditions is not None:

        print(
            "NotBefore:",
            conditions.get(
                "NotBefore"
            )
        )

        print(
            "NotOnOrAfter:",
            conditions.get(
                "NotOnOrAfter"
            )
        )

    if confirmation is not None:

        print(
            "Recipient:",
            confirmation.get(
                "Recipient"
            )
        )

        print(
            "InResponseTo:",
            confirmation.get(
                "InResponseTo"
            )
        )

    print()
    print("Attributes")
    print("-" * 70)

    for attribute in root.findall(
        ".//saml:Attribute",
        NS
    ):

        name = attribute.get(
            "Name"
        )

        values = []

        for value in attribute.findall(
            "./saml:AttributeValue",
            NS
        ):

            values.append(
                value.text
            )

        print(
            f"{name}: {values}"
        )


if __name__ == "__main__":
    main()
```

---

# Script Usage

Save the Base64 SAMLResponse:

```text
response.txt
```

Then:

```bash
python3 saml_inspect.py \
  response.txt
```

The script is intended for:

```text
Inspection
```

not:

```text
Signature validation
```

Never write your own XML signature validation logic for production security decisions.

---

# SAML Response Comparison Script

A small helper can compare two controlled assertions.

```python
#!/usr/bin/env python3

import argparse
import base64
import urllib.parse
import xml.etree.ElementTree as ET


NS = {
    "saml": (
        "urn:oasis:names:tc:"
        "SAML:2.0:assertion"
    ),
}


def load(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as handle:

        value = handle.read().strip()

    value = urllib.parse.unquote_plus(
        value
    )

    xml_data = base64.b64decode(
        value
    )

    return ET.fromstring(
        xml_data
    )


def extract(root):

    result = {}

    issuer = root.find(
        ".//saml:Issuer",
        NS
    )

    name_id = root.find(
        ".//saml:NameID",
        NS
    )

    audience = root.find(
        ".//saml:Audience",
        NS
    )

    result["Issuer"] = (
        issuer.text
        if issuer is not None
        else None
    )

    result["NameID"] = (
        name_id.text
        if name_id is not None
        else None
    )

    result["Audience"] = (
        audience.text
        if audience is not None
        else None
    )

    for attribute in root.findall(
        ".//saml:Attribute",
        NS
    ):

        name = attribute.get(
            "Name"
        )

        values = [
            value.text
            for value in attribute.findall(
                "./saml:AttributeValue",
                NS
            )
        ]

        result[
            f"Attribute:{name}"
        ] = values

    return result


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "first"
    )

    parser.add_argument(
        "second"
    )

    args = parser.parse_args()

    first = extract(
        load(args.first)
    )

    second = extract(
        load(args.second)
    )

    keys = sorted(
        set(first)
        |
        set(second)
    )

    for key in keys:

        left = first.get(
            key
        )

        right = second.get(
            key
        )

        if left != right:

            print(
                f"[DIFF] {key}"
            )

            print(
                f"  A: {left}"
            )

            print(
                f"  B: {right}"
            )


if __name__ == "__main__":
    main()
```

---

# Comparison Usage

Capture assertions for:

```text
Controlled Account A
Controlled Account B
```

Then:

```bash
python3 saml_compare.py \
  account-a.txt \
  account-b.txt
```

This can reveal:

```text
Identity attribute
Role attribute
Group attribute
Tenant attribute
Session differences
```

---

# OpenSSL Certificate Inspection

If a signing certificate has been extracted:

```bash
openssl x509 \
  -in saml-signing.pem \
  -text \
  -noout
```

Inspect:

```text
Subject
Issuer
Validity
Public key
Signature algorithm
Extensions
```

---

# Certificate Fingerprint

```bash
openssl x509 \
  -in saml-signing.pem \
  -noout \
  -fingerprint \
  -sha256
```

Compare this with:

```text
Trusted IdP metadata
```

where appropriate.

---

# Metadata Retrieval

Example:

```bash
curl -s \
  https://idp.example.com/metadata |
xmllint --format -
```

Do not assume a generic `/metadata` endpoint exists.

Use discovered or documented endpoints.

---

# Metadata Checklist

Inspect:

```text
[ ] entityID
[ ] IdP SSO endpoints
[ ] SP ACS endpoints
[ ] Signing certificate
[ ] Encryption certificate
[ ] Supported bindings
[ ] Logout endpoints
[ ] NameID formats
```

---

# Common False Positives

## Public Certificate Disclosure

Not automatically vulnerable:

```text
Signing certificate visible
```

because public keys are intended to be distributed.

---

## Unsigned AuthnRequest

Some SAML deployments intentionally permit:

```text
Unsigned AuthnRequest
```

This is not automatically an authentication bypass.

Assess whether request manipulation creates security impact.

---

## Missing Assertion Encryption

SAML assertions do not always require XML encryption.

If:

```text
HTTPS
```

protects the transport and the architecture does not require encrypted assertions, lack of XML encryption is not automatically a vulnerability.

---

## IdP-Initiated SSO

Missing:

```text
InResponseTo
```

may be expected for IdP-initiated SSO.

Understand the flow before reporting.

---

## Long-Lived SP Session

A long application session is:

```text
Session Management
```

rather than necessarily a SAML flaw.

---

## Self-Signed IdP Certificate

A self-signed SAML signing certificate is not automatically insecure.

SAML trust can be established through:

```text
Explicit certificate pinning / metadata
```

rather than a public CA hierarchy.

---

# Evidence Collection

Capture:

```text
Normal authentication flow
Original SAMLResponse
Decoded assertion
Signature structure
Controlled modified assertion
SP response
Resulting session
Authenticated identity
```

---

# Minimal Evidence Principle

If modifying:

```text
Your own display-name attribute
```

proves that unsigned assertion content is trusted:

```text
Stop
```

Do not immediately impersonate:

```text
Administrator
CEO
Another customer
```

unless stronger impact demonstration is explicitly required and authorised.

---

# Authentication Bypass Evidence

Strong evidence includes:

```text
Original valid assertion
Controlled modified assertion
Signature invalid / removed
SP accepts assertion
New authenticated session
Server-side identity changed
```

---

# Cross-Tenant Evidence

Use:

```text
Tenant A controlled account
Tenant B controlled account
```

where possible.

Demonstrate:

```text
Tenant boundary violation
```

without accessing unrelated customer data.

---

# Example Finding: SAML Signature Not Validated

```text
Finding:
SAML Assertions Are Accepted Without Valid Signature Verification

Observed:
The Service Provider accepts SAML assertions after the cryptographic signature has been removed or invalidated.

Testing was performed using a controlled account. A valid assertion was captured, a controlled identity attribute was modified, and the original signature was removed or rendered invalid.

The Service Provider nevertheless accepted the assertion and established an authenticated session based on the modified assertion data.

Impact:
An attacker able to submit a crafted SAML response may be able to forge authentication assertions and impersonate application users.

Depending on the application's identity and role mapping, this may result in complete account takeover or privilege escalation.

Recommendation:
Require cryptographic signature validation for every SAML message or assertion relied upon for authentication. Validate the signature using the explicitly configured trusted Identity Provider certificate and ensure the exact XML element consumed by application logic is the element protected by the validated signature.
```

---

# Example Finding: XML Signature Wrapping

```text
Finding:
SAML Authentication Is Vulnerable to XML Signature Wrapping

Observed:
The Service Provider validates the cryptographic signature of one SAML assertion but processes identity information from a different assertion within the same XML document.

Using a controlled account, a modified SAML response containing both the valid signed assertion and a separate controlled assertion was accepted.

The resulting session reflected identity information from the unsigned assertion.

Impact:
An attacker possessing a valid SAML assertion may be able to alter the identity or attributes processed by the Service Provider without invalidating the cryptographic signature.

This may permit user impersonation or privilege escalation.

Recommendation:
Use a mature SAML implementation that securely binds XML signature verification to assertion processing. Reject ambiguous XML documents, duplicate IDs, unexpected assertions and unsupported structures. Application logic must consume the exact assertion element whose signature has been successfully validated.
```

---

# Example Finding: Assertion Replay

```text
Finding:
SAML Assertions Can Be Replayed to Create New Authenticated Sessions

Observed:
A previously consumed SAML response could be submitted again to the Assertion Consumer Service and resulted in the creation of another authenticated session.

The assertion remained reusable during its validity period and no effective replay detection was observed.

Impact:
An attacker who obtains a valid SAML assertion may be able to reuse it to create authenticated sessions for the affected account.

The practical risk depends on how assertions may be exposed and the duration of their validity.

Recommendation:
Use short assertion validity periods and implement replay protection appropriate to the SAML profile. Track consumed assertion or response identifiers for the relevant validity period and reject unexpected reuse. Consider OneTimeUse where appropriate.
```

---

# Example Finding: Audience Validation Missing

```text
Finding:
SAML Assertions Issued for Another Service Provider Are Accepted

Observed:
The application accepts a valid SAML assertion whose Audience value identifies a different Service Provider.

Testing was performed between authorised test applications using the same Identity Provider.

The assertion intended for the first application was accepted by the second application and resulted in an authenticated session.

Impact:
An attacker who obtains a valid assertion for another Service Provider may be able to reuse that assertion to authenticate to the affected application.

This breaks the intended separation between SAML relying parties.

Recommendation:
Strictly validate AudienceRestriction and require the assertion audience to match the expected Service Provider identifier.
```

---

# Example Finding: Cross-Tenant Identity Confusion

```text
Finding:
SAML Identity Mapping Allows Cross-Tenant Account Impersonation

Observed:
The application maps SAML users to local accounts using an identity attribute without correctly binding the assertion to the originating tenant or trusted Identity Provider.

Using two controlled tenants, an assertion originating from one tenant could be modified or configured to resolve to an account belonging to the second tenant.

Impact:
A malicious tenant administrator may be able to impersonate users belonging to another organisation.

This could result in cross-tenant account takeover and unauthorised access to customer information.

Recommendation:
Bind every federated identity to the trusted Identity Provider, tenant and immutable external subject identifier. Do not perform global account lookup solely by mutable attributes such as email address.
```

---

# Example Finding: SAML Role Manipulation

```text
Finding:
Unsigned SAML Attributes Control Application Privileges

Observed:
The application derives local privileges from SAML role attributes that are not effectively protected by the validated XML signature.

Using a controlled user, the role attribute was modified and the Service Provider accepted the modified value.

Impact:
An authenticated attacker may be able to modify SAML attributes to obtain privileges that were not granted by the trusted Identity Provider.

Recommendation:
Ensure every identity and authorisation attribute consumed by the application is contained within the cryptographically validated assertion. Apply server-side allow-listing and mapping for security-sensitive roles and groups.
```

---

# Example Finding: Expired Assertion Accepted

```text
Finding:
Expired SAML Assertions Remain Valid

Observed:
The Service Provider accepted a SAML assertion after the assertion's NotOnOrAfter validity condition had expired.

The replayed assertion resulted in a new authenticated session.

Impact:
The effective lifetime of stolen SAML assertions is increased, allowing authentication tokens to remain useful beyond the period intended by the Identity Provider.

Recommendation:
Validate all SAML temporal conditions, including NotBefore and NotOnOrAfter, using a small and explicitly configured clock-skew allowance. Reject assertions outside their permitted validity period.
```

---

# Reporting Titles

Useful titles include:

```text
SAML Signature Validation Can Be Bypassed

Unsigned SAML Assertions Are Accepted

SAML Authentication Vulnerable to XML Signature Wrapping

SAML Assertions Can Be Replayed

Expired SAML Assertions Are Accepted

SAML Audience Restriction Is Not Validated

SAML Recipient Is Not Validated

SAML Issuer Validation Is Missing

SAML Assertion Signed by Untrusted Certificate Is Accepted

SAML Role Attribute Manipulation Allows Privilege Escalation

SAML Identity Mapping Allows Account Takeover

Cross-Tenant SAML Identity Confusion

SAML RelayState Allows Open Redirect

SAML Login Flow Vulnerable to Session Confusion

SAML Authentication Does Not Enforce Required MFA Context
```

---

# Severity

Severity should be based on demonstrated impact.

Examples:

```text
Metadata disclosure
→ Informational

Weak hardening
→ Low

Assertion replay with limited exposure
→ Medium

Role manipulation
→ High

Authentication bypass
→ High / Critical

Arbitrary user impersonation
→ Critical

Administrator impersonation
→ Critical

Cross-tenant account takeover
→ Critical
```

Do not rate based only on:

```text
SAML Misconfiguration
```

Determine:

```text
What security boundary can actually be crossed?
```

---

# Remediation

A secure SAML implementation should enforce:

```text
Trusted IdP
     +
Valid Signature
     +
Expected Issuer
     +
Expected Audience
     +
Expected Recipient
     +
Expected Destination
     +
Valid Time Window
     +
Request Correlation
     +
Replay Protection
     +
Safe Identity Mapping
```

---

# Use Mature Libraries

Do not implement:

```text
XML Signature Validation
SAML Parsing
Canonicalisation
Trust Processing
```

from scratch.

Use:

```text
Mature
Maintained
Well-tested
```

SAML libraries.

---

# Validate Signatures

Require signatures according to the SAML trust model.

Validate using:

```text
Explicitly trusted IdP certificate
```

rather than arbitrary certificate information contained in the message.

---

# Validate the Correct Element

After signature verification:

```text
Application
```

must consume:

```text
The exact signed assertion
```

not another similarly named or positioned XML element.

---

# Reject Ambiguous XML

Reject:

```text
Duplicate IDs
Unexpected assertions
Duplicate security-sensitive attributes
Unsupported structures
Unexpected namespaces
```

where they create ambiguity.

---

# Validate Issuer

Require:

```text
Issuer
=
Configured Trusted IdP
```

---

# Validate Audience

Require:

```text
Audience
=
Expected Service Provider
```

---

# Validate Recipient

Require:

```text
Recipient
=
Expected ACS
```

where applicable.

---

# Validate Destination

Require the response destination to match:

```text
Expected ACS endpoint
```

according to the SAML profile being used.

---

# Validate Time

Check:

```text
NotBefore
NotOnOrAfter
SubjectConfirmationData expiry
```

with only the necessary clock-skew allowance.

---

# Short Assertion Lifetime

Prefer:

```text
Minutes
```

rather than unnecessarily long assertion validity.

Exact lifetime depends on architecture.

---

# Replay Protection

Where appropriate:

```text
Assertion ID
Response ID
      ↓
Replay Cache
      ↓
Previously Seen?
```

Reject reused assertions according to the intended protocol semantics.

---

# Request Correlation

For SP-initiated flows:

```text
AuthnRequest ID
       ↓
InResponseTo
```

should be validated appropriately.

---

# Secure Identity Mapping

Prefer an immutable mapping:

```text
Trusted IdP
+
Tenant
+
Stable Subject Identifier
```

rather than relying only on:

```text
Email address
```

---

# Secure Role Mapping

Do not blindly map arbitrary IdP strings to internal administrative roles.

Use:

```text
Explicit role mappings
Allow-listed groups
Tenant-specific configuration
```

---

# Protect ACS Configuration

ACS URLs should be:

```text
Preconfigured
Allow-listed
HTTPS
```

Do not construct them from untrusted Host headers.

---

# Protect Metadata

Retrieve metadata from:

```text
Trusted locations
```

and validate configuration changes.

Do not dynamically trust arbitrary metadata URLs supplied by users.

---

# Certificate Rotation

Implement controlled:

```text
Signing certificate rollover
```

without disabling validation.

---

# Logging

Useful SAML security events include:

```text
Invalid signature
Unknown issuer
Wrong audience
Expired assertion
Replay detected
Invalid recipient
Invalid destination
Unknown certificate
Failed identity mapping
Duplicate assertion ID
Unexpected role mapping
```

---

# Do Not Log Sensitive Assertions Unnecessarily

SAML assertions may contain:

```text
Identity data
Email
Groups
Roles
Employee information
Authentication information
```

Avoid storing full assertions in insecure application logs.

---

# SAML Security Checklist

## Discovery

```text
[ ] SAML SSO identified
[ ] IdP identified
[ ] SP identified
[ ] ACS identified
[ ] Metadata located
[ ] Entity IDs identified
[ ] Bindings identified
[ ] Logout flow identified
```

## Flow Mapping

```text
[ ] SP-initiated flow captured
[ ] IdP-initiated flow considered
[ ] SAMLRequest captured
[ ] SAMLResponse captured
[ ] RelayState captured
[ ] Session creation observed
```

## Assertion

```text
[ ] Issuer
[ ] NameID
[ ] Attributes
[ ] Audience
[ ] Recipient
[ ] Destination
[ ] InResponseTo
[ ] NotBefore
[ ] NotOnOrAfter
[ ] SessionIndex
```

## Signature

```text
[ ] Signature present
[ ] Signed element identified
[ ] Signature removal tested
[ ] Signed data modification tested
[ ] Trusted certificate verified
[ ] Arbitrary certificate rejected
[ ] Reference URI reviewed
[ ] Duplicate IDs tested where appropriate
```

## XSW

```text
[ ] Multiple assertions considered
[ ] XML Signature Wrapping tested
[ ] Duplicate element handling reviewed
[ ] Signed element equals consumed element
```

## Conditions

```text
[ ] Audience validated
[ ] Recipient validated
[ ] Destination validated
[ ] Issuer validated
[ ] NotBefore validated
[ ] NotOnOrAfter validated
[ ] Clock skew reasonable
```

## Replay

```text
[ ] Immediate replay tested
[ ] Post-use replay tested
[ ] Expired replay tested
[ ] Assertion ID handling reviewed
[ ] Response ID handling reviewed
[ ] OneTimeUse considered
```

## Request Binding

```text
[ ] InResponseTo validated
[ ] SP-initiated correlation tested
[ ] Unsolicited response behaviour reviewed
```

## Identity

```text
[ ] Identity attribute identified
[ ] NameID mapping reviewed
[ ] Email mapping reviewed
[ ] Case handling reviewed
[ ] Normalisation reviewed
[ ] Duplicate attributes reviewed
[ ] Account linking reviewed
```

## Authorisation

```text
[ ] Role attributes reviewed
[ ] Group attributes reviewed
[ ] Tenant attributes reviewed
[ ] JIT provisioning reviewed
[ ] Administrative mapping reviewed
```

## Multi-Tenant

```text
[ ] IdP bound to tenant
[ ] Cross-tenant assertion rejected
[ ] Global email lookup reviewed
[ ] Tenant-controlled IdP threat considered
```

## XML

```text
[ ] XXE considered
[ ] XSLT considered
[ ] Namespace handling reviewed
[ ] Duplicate IDs reviewed
[ ] Parser ambiguity reviewed
```

## RelayState

```text
[ ] RelayState purpose understood
[ ] Open redirect tested
[ ] State integrity reviewed
[ ] Sensitive values absent
```

## Sessions

```text
[ ] New session after SSO
[ ] Session fixation reviewed
[ ] Logout tested
[ ] Session invalidation tested
[ ] SLO reviewed where applicable
```

## Alternate Authentication

```text
[ ] Password login
[ ] Password reset
[ ] MFA
[ ] OAuth/OIDC
[ ] Legacy endpoints
[ ] Mobile/API authentication
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Comparer
[ ] Decoder
[ ] Logger
[ ] SAML Raider
[ ] SAML Editor where useful
[ ] SAMLReQuest where useful
```

## Evidence

```text
[ ] Original assertion retained
[ ] Modified assertion retained
[ ] Decoded XML retained
[ ] Responses retained
[ ] Session evidence retained
[ ] Controlled accounts used
[ ] Minimal impact demonstrated
```

---

# Quick Reference

```text
SAML

User
 ↓
SP
 ↓
IdP
 ↓
SAML Assertion
 ↓
SP
 ↓
Session
```

Primary fields:

```text
Issuer
NameID
Audience
Recipient
Destination
InResponseTo
NotBefore
NotOnOrAfter
Attributes
Signature
RelayState
```

Primary attacks:

```text
Signature bypass
XML Signature Wrapping
Assertion replay
Audience confusion
Issuer confusion
Recipient bypass
Expired assertion acceptance
Identity mapping flaws
Role manipulation
Cross-tenant confusion
RelayState abuse
XXE
```

Primary Burp extension:

```text
SAML Raider
```

Official BApp:

```text
https://portswigger.net/bappstore/c61cfa893bb14db4b01775554f7b802e
```

---

# Pentester Quick Workflow

```text
Capture SSO
   ↓
Find SAMLResponse
   ↓
Decode XML
   ↓
Find NameID
   ↓
Find Attributes
   ↓
Find Signature
   ↓
What Is Signed?
   ↓
Remove Signature
   ↓
Modify Controlled Attribute
   ↓
Test XSW
   ↓
Test Certificate Trust
   ↓
Test Issuer
   ↓
Test Audience
   ↓
Test Recipient
   ↓
Test Destination
   ↓
Test Time Conditions
   ↓
Test InResponseTo
   ↓
Replay Assertion
   ↓
Test Identity Mapping
   ↓
Test Roles / Groups
   ↓
Test Tenant Boundary
   ↓
Test RelayState
   ↓
Test XML Parser
   ↓
Verify Session
   ↓
Report
```

---

# References

## OWASP SAML Security Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html
```

Primary OWASP guidance for securing SAML implementations.

---

## OWASP Authentication Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
```

Useful for the wider authentication controls surrounding SAML.

---

## OWASP XML Security Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/XML_Security_Cheat_Sheet.html
```

Useful when evaluating the XML processing layer behind SAML.

---

## OASIS SAML 2.0

```text
https://www.oasis-open.org/standard/saml/
```

Official SAML standard resources.

---

## SAML 2.0 Technical Overview

```text
https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html
```

Useful for understanding SAML profiles and message flows.

---

## SAML 2.0 Core

```text
https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf
```

Defines assertions, protocols and core SAML structures.

---

## SAML 2.0 Bindings

```text
https://docs.oasis-open.org/security/saml/v2.0/saml-bindings-2.0-os.pdf
```

Defines HTTP POST, Redirect and other SAML bindings.

---

## SAML 2.0 Profiles

```text
https://docs.oasis-open.org/security/saml/v2.0/saml-profiles-2.0-os.pdf
```

Defines SAML profiles including Web Browser SSO.

---

## SAML 2.0 Security Considerations

```text
https://docs.oasis-open.org/security/saml/v2.0/saml-sec-consider-2.0-os.pdf
```

Security and privacy considerations for SAML deployments.

---

## SAML Raider

```text
https://portswigger.net/bappstore/c61cfa893bb14db4b01775554f7b802e
```

Burp Suite extension for:

```text
SAML message manipulation
Certificate management
Signature testing
XML Signature Wrapping
XXE testing
XSLT testing
```

---

## PortSwigger BApp Store

```text
https://portswigger.net/bappstore
```

Useful for checking current SAML-related Burp extensions.

---

## PortSwigger Authentication Security

```text
https://portswigger.net/web-security/authentication
```

Useful background for authentication testing surrounding federated login.

---

# Final SAML Testing Model

```text
                            SAML SSO
                               ↓
                       IDENTIFY TRUST MODEL
                               ↓
                 ┌─────────────┼─────────────┐
                 ↓             ↓             ↓
                USER           SP            IdP
                               ↓
                         CAPTURE FLOW
                               ↓
                   ┌───────────┼───────────┐
                   ↓           ↓           ↓
              SAMLRequest  SAMLResponse  RelayState
                               ↓
                        DECODE ASSERTION
                               ↓
          ┌────────────────────┼────────────────────┐
          ↓                    ↓                    ↓
       IDENTITY             CONDITIONS           SIGNATURE
          ↓                    ↓                    ↓
       NameID              Audience            Signed What?
       Email               Recipient               ↓
       Groups              Destination        Trusted Key?
       Roles               Time                    ↓
       Tenant              InResponseTo         VALID?
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ↓
                        MUTATION TESTING
                               ↓
           ┌───────────────────┼───────────────────┐
           ↓                   ↓                   ↓
       SIGNATURE              XSW               TRUST
           ↓                   ↓                   ↓
       Remove Sig       Wrapped Assertion     New Certificate
       Modify Data      Duplicate IDs         Wrong Issuer
           ↓                   ↓                   ↓
       ACCEPTED?            ACCEPTED?            ACCEPTED?
        ↓     ↓              ↓     ↓              ↓     ↓
       NO    YES            NO    YES            NO    YES
       ↓      ↓             ↓      ↓             ↓      ↓
     GOOD   VULN          GOOD   VULN          GOOD   VULN
                \             |             /
                 \            |            /
                  └───────────┼───────────┘
                              ↓
                     CONDITION TESTING
                              ↓
          ┌──────────┬────────┼────────┬──────────┐
          ↓          ↓        ↓        ↓          ↓
       ISSUER     AUDIENCE RECIPIENT  TIME   InResponseTo
          ↓          ↓        ↓        ↓          ↓
                         STRICT?
                      ↓          ↓
                     YES         NO
                      ↓          ↓
                    GOOD      INVESTIGATE
                                  ↓
                         REPLAY TESTING
                                  ↓
                        SAME ASSERTION AGAIN
                           ↓            ↓
                        REJECT        ACCEPT
                           ↓            ↓
                         GOOD         REPLAY
                                        ↓
                             IDENTITY MAPPING
                                        ↓
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
                  NameID              EMAIL               ROLE
                    ↓                   ↓                   ↓
              STABLE SUBJECT?     TENANT BOUND?      ALLOW-LISTED?
                    └───────────────────┼───────────────────┘
                                        ↓
                               MULTI-TENANT TEST
                                        ↓
                              CROSS-TENANT ACCEPTED?
                                  ↓           ↓
                                 NO          YES
                                  ↓           ↓
                                GOOD       CRITICAL
                                       
                                        ↓
                                 XML PROCESSING
                                        ↓
                           ┌────────────┼────────────┐
                           ↓            ↓            ↓
                          XXE          XSLT       PARSER DIFF
                           └────────────┼────────────┘
                                        ↓
                                  SESSION TEST
                                        ↓
                         ┌──────────────┼──────────────┐
                         ↓              ↓              ↓
                     ROTATION        LOGOUT        FIXATION
                         └──────────────┼──────────────┘
                                        ↓
                                ALTERNATE AUTH
                                        ↓
                       ┌────────────────┼────────────────┐
                       ↓                ↓                ↓
                    PASSWORD           MFA           OAUTH/OIDC
                       └────────────────┼────────────────┘
                                        ↓
                                  MINIMAL PROOF
                                        ↓
                                      REPORT
                                        ↓
                                  REMEDIATION
                                        ↓
             ┌──────────────────────────┼──────────────────────────┐
             ↓                          ↓                          ↓
       SIGNATURE TRUST           PROTOCOL VALIDATION        IDENTITY BINDING
             ↓                          ↓                          ↓
       Trusted IdP Key           Issuer/Audience/etc.       IdP + Tenant + ID
             └──────────────────────────┼──────────────────────────┘
                                        ↓
                                      RETEST
```

The central principle is:

> A SAML assertion should only create an authenticated session when its cryptographic integrity, trusted issuer, intended audience, recipient, destination, validity period, request relationship and identity mapping have all been validated. Testing therefore needs to go beyond decoding `SAMLResponse`: determine exactly which XML element is signed, which element the application consumes, which certificate establishes trust, and whether an assertion can be substituted, wrapped, replayed or mapped to an identity that the trusted IdP did not actually authenticate.
